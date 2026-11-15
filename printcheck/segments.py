"""Segmentation evaluator: scores a set of segment meshes (assembled pose).
Components: joint location vs peak moment, part count, build orientation vs load direction (tangent + optional FEA principal stress)."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from sim.common import get_centerline, Centerline
from . import checks as C

BUILD = {"+z": [0, 0, 1], "-z": [0, 0, -1], "+x": [1, 0, 0], "-x": [-1, 0, 0], "+y": [0, 1, 0], "-y": [0, -1, 0]}


def _centerline(params, segs, manifest=None):
    cl = get_centerline(params, manifest) if params else None
    if cl is not None:
        return cl, "centerline from params/manifest"
    V = np.vstack([m.vertices for m in segs.values()])
    c = V.mean(0); u, s, vt = np.linalg.svd(V - c, full_matrices=False)
    t = vt[0]; pr = (V - c) @ t
    return Centerline(np.array([c + pr.min() * t, c + pr.max() * t])), "PCA axis (no params centerline)"


def moment_profile(analytic_json, cl):
    if analytic_json and Path(analytic_json).exists():
        a = json.loads(Path(analytic_json).read_text())
        lc1 = next((c for c in a["load_cases"] if c["id"] == "LC1"), None)
        if lc1 and "stress_profile" in lc1:
            s = np.array([r["s"] for r in lc1["stress_profile"]]); M = np.array([r["M"] for r in lc1["stress_profile"]])
            return s, M, "analytic LC1 station moments"
    s = np.linspace(0, 1, 50); M = np.clip(0.8 - s, 0, None)
    return s, M, "FALLBACK unit-cantilever (load at s=0.8); analytic.json not provided"


def evaluate_segments(segs, params, analytic_json, fea_fields, joints, manifest=None):
    lim = C.LIM
    cl, clsrc = _centerline(params, segs, manifest)
    names = list(segs)
    sc = {}
    for n in names:
        fr, _ = cl.project(segs[n].vertices); sc[n] = (float(np.min(fr)), float(np.max(fr)), float(np.mean(fr)))
    order = sorted(names, key=lambda n: sc[n][2])
    comp = {}
    # part count
    L = cl.L
    nmin = int(np.ceil(L / lim["bed_target_mm"]))
    n = len(names)
    cs = 0.0 if n < nmin else max(0.0, 1 - 0.25 * (n - nmin))
    comp["part_count"] = {"score": cs, "detail": f"{n} segments; centerline length {L:.0f} mm; minimum {nmin} at {lim['bed_target_mm']} mm target (ideal count)"}
    # joint location
    s, M, msrc = moment_profile(analytic_json, cl)
    Mmax = float(M.max()) if M.max() > 0 else 1.0
    js = []; det = []
    for j in joints:
        fr, _ = cl.project(np.array([j["center"]])); sj = float(fr[0])
        ratio = float(np.interp(sj, s, M) / Mmax); js.append(max(0.0, 1 - ratio / 1.0))
        det.append(f"{j['pair']} at s={sj:.2f}: M/Mmax={ratio:.2f}" + (" (> limit %.2f)" % lim["joint_moment_ratio_max"] if ratio > lim["joint_moment_ratio_max"] else ""))
    comp["joint_vs_peak_moment"] = {"score": float(np.mean(js)) if js else 0.0, "detail": "; ".join(det) + f" [{msrc}; {clsrc}]" if det else "no joints detected (UNVERIFIED)", "ratios_ok": bool(js and all("limit" not in d for d in det))}
    # orientation
    osc = []; od = []
    fields = np.load(fea_fields) if fea_fields and Path(fea_fields).exists() else None
    for nme in names:
        m = segs[nme]
        best, _ = C.best_orientation(m); up = np.array(BUILD[best["up"]], float)
        p, t = cl.at(float(np.clip(sc[nme][2], 0, 1))); t = t[0]
        cos2 = float((t @ up) ** 2)
        s_t = max(0.0, 1 - cos2 / 0.5)
        extra = ""
        if fields is not None:
            cen = fields["centers"]; sig = fields["sig_sw"].astype(float) - 49.05 * fields["sig_plant"].astype(float)
            from scipy.spatial import cKDTree
            d, _ = cKDTree(m.vertices).query(cen)
            sel = d < 6.0
            if sel.sum() > 20:
                sg = sig[sel]
                S = np.zeros((len(sg), 3, 3)); S[:, 0, 0] = sg[:, 0]; S[:, 1, 1] = sg[:, 1]; S[:, 2, 2] = sg[:, 2]
                S[:, 1, 2] = S[:, 2, 1] = sg[:, 3]; S[:, 0, 2] = S[:, 2, 0] = sg[:, 4]; S[:, 0, 1] = S[:, 1, 0] = sg[:, 5]
                w, v = np.linalg.eigh(S)
                vm = np.sqrt(0.5 * ((sg[:, 0] - sg[:, 1]) ** 2 + (sg[:, 1] - sg[:, 2]) ** 2 + (sg[:, 2] - sg[:, 0]) ** 2) + 3 * (sg[:, 3] ** 2 + sg[:, 4] ** 2 + sg[:, 5] ** 2))
                top = vm >= np.percentile(vm, 90)
                pv = v[:, :, 2]                       # max principal direction
                al = ((pv @ up) ** 2 > 0.5) & (w[:, 2] > 0) & top
                frac = float(al.sum() / max(top.sum(), 1))
                s_t = 0.5 * s_t + 0.5 * (1 - min(1.0, frac / 0.25)); extra = f", FEA: {100*frac:.0f}% of top-10% stress elements have tensile principal dir within 45 deg of build axis"
        osc.append(s_t); od.append(f"{nme}: up={best['up']} tangent.build^2={cos2:.2f}{extra}")
    comp["orientation_vs_stress"] = {"score": float(np.mean(osc)), "detail": "; ".join(od)}
    w = {"part_count": 0.2, "joint_vs_peak_moment": 0.4, "orientation_vs_stress": 0.4}
    total = sum(w[k] * comp[k]["score"] for k in w)
    return {"total": float(total), "weights": w, "order_along_span": order, "components": comp, "centerline_source": clsrc}
