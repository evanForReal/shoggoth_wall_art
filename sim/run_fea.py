"""FEA driver: voxel-hex linear-elastic analysis of underlay (+ skin as added mass) for LC1-LC5.

python -m sim.run_fea --underlay X.stl [--skin Y.stl] --params params.json --loadcases loadcases.json --out reports/ [--pitch 1.2]
Writes <out>/fea.json, <out>/fea.md, <out>/fea_fields.npz
"""
from __future__ import annotations
import argparse, json, time
from pathlib import Path
import numpy as np
from scipy import ndimage
from scipy.spatial import cKDTree

from .common import *
from .voxel import load_mesh, occupancy, Grid, winding_raster
from .hexfea import HexModel, G

GN = 9.81


def build_model(mesh, skin, params, lc, mat, pitch):
    wall = params["shell_wall"]
    occ, bad, grid = occupancy(mesh, pitch)
    depth = ndimage.distance_transform_edt(occ, sampling=pitch)
    inf = lc["infill"]
    interior = depth > (wall + 0.25 * pitch)
    efac = np.where(interior, inf["E_factor"], 1.0)
    rfac = np.where(interior, inf["fraction"], 1.0)
    M = HexModel(occ, grid, mat["E"], mat["nu"], rho=mat["rho_t_mm3"], efac=efac, rhofac=rfac)
    info = {"anomalous_cells": bad, "n_solid_cells": int(occ.sum()), "interior_cells": int((interior & occ).sum())}
    # skin as lumped added mass
    skin_mass_nodes = None; skin_mass_kg = 0.0
    if skin is not None:
        w = winding_raster(skin, grid)
        so = (w == 1) & ~occ
        idx = np.argwhere(so)
        if len(idx):
            cen = grid.origin + (idx + 0.5) * pitch
            _, nn = cKDTree(M.xyz).query(cen)
            mcell = mat["rho_t_mm3"] * pitch ** 3 * lc["skin"]["mass_factor"]
            skin_mass_nodes = (nn, np.full(len(nn), mcell))
            skin_mass_kg = mcell * len(nn) * 1000.0
    return M, occ, grid, depth, skin_mass_nodes, skin_mass_kg, info


def shelf_point(params, M, occ, grid, cl, manifest=None):
    if manifest and manifest.get("shelf", {}).get("load_point_LC1"):
        p = np.array(manifest["shelf"]["load_point_LC1"], float)
        sel = (np.hypot(M.xyz[:, 0] - p[0], M.xyz[:, 1] - p[1]) < 12.0)
        if sel.any():
            p[2] = M.xyz[sel, 2].max()
        return p
    sz = params.get("shelf_zone", {}) or {}
    if "center" in sz and len(sz["center"]) == 3:
        return np.asarray(sz["center"], float)
    if "center_frac" in sz:
        fr = sz["center_frac"]
    elif "span_frac" in sz:
        fr = float(np.mean(sz["span_frac"]))
    elif "s_range" in sz:
        fr = float(np.mean(sz["s_range"]))
    else:
        fr = 0.8
    if cl is not None:
        p, _ = cl.at(fr); x, y = float(p[0, 0]), float(p[0, 1])
    else:
        lo = M.xyz[:, 0].min(); hi = M.xyz[:, 0].max(); x = lo + fr * (hi - lo); y = 0.0
    sel = (np.hypot(M.xyz[:, 0] - x, M.xyz[:, 1] - y) < 12.0)
    ztop = M.xyz[sel, 2].max()
    return np.array([x, y, ztop])


def tip_point(params, M, cl, manifest=None):
    if manifest and manifest.get("tip_xyz"):
        return np.array(manifest["tip_xyz"], float)
    if cl is not None:
        p, _ = cl.at(1.0); return p[0]
    n = M.xyz[:, 0] > M.xyz[:, 0].max() - 1e-6
    return M.xyz[n].mean(0)


class Runner:
    def __init__(self, M, params, lc, mat, grid, skin_nodes, cl, manifest=None):
        self.M = M; self.params = params; self.lc = lc; self.mat = mat; self.cl = cl
        self.h = M.h
        self.skin_nodes = skin_nodes
        xmin = M.xyz[:, 0].min()
        self.xmin = xmin
        self.shelf = shelf_point(params, M, None, grid, cl, manifest)
        self.tip = tip_point(params, M, cl, manifest)
        self.manifest = manifest
        r_tip = params["tip_diameter"] / 2 + M.h
        zt = self.shelf[2]
        self.shelf_nodes = M.nodes_where(lambda X: (np.hypot(X[:, 0] - self.shelf[0], X[:, 1] - self.shelf[1]) < 40.0) & (X[:, 2] > zt - 3 * M.h))
        if len(self.shelf_nodes) < 4:
            self.shelf_nodes = M.nodes_near(self.shelf, 40.0)
        self.tip_nodes = M.nodes_near(self.tip, r_tip)
        self.cache = {}
        self.solve_log = []

    def set_support_backface(self):
        M = self.M
        M.set_fixed(M.nodes_where(lambda X: X[:, 0] < self.xmin + 1e-6)); M.factor()
        self.support = "back_face_fixed"; self.cache.clear()

    def unit_load(self, key):
        M = self.M
        if key == "sw":
            return M.gravity_load(self.skin_nodes)
        where, axis = key
        nodes = self.shelf_nodes if where == "shelf" else self.tip_nodes
        f = np.zeros(M.ndof); f[nodes * 3 + axis] += 1.0 / len(nodes)
        return f

    def solution(self, key):
        if key in self.cache:
            return self.cache[key]
        M = self.M
        f = self.unit_load(key)
        t0 = time.time(); u, info = M.solve(f); dt = time.time() - t0
        R = M.reactions(u, f)
        fx = M.xyz[M.fixed.reshape(-1, 3).any(1)] if False else None
        fnodes = np.nonzero(M.fixed.reshape(-1, 3).any(1))[0]
        Rn = R.reshape(-1, 3) if False else None
        # reaction per fixed dof -> per node
        rr = np.zeros((M.nn, 3)); rr_f = (M.K @ u - f).reshape(-1, 3)
        rr[fnodes] = rr_f[fnodes]
        F = rr[fnodes].sum(0)
        pos = M.xyz[fnodes]
        Mo = np.cross(pos, rr[fnodes]).sum(0)
        sig = M.stress(u).astype(np.float32)
        out = {"u": u, "sig": sig, "F": F, "M": Mo, "info": info, "applied": f.reshape(-1, 3).sum(0), "node_react": (fnodes, rr[fnodes])}
        self.solve_log.append({"key": str(key), "time_s": round(dt, 1), **info})
        print(f"  solve {key}: {dt:.1f}s {info}", flush=True)
        self.cache[key] = out
        return out

    def combo(self, coeffs):
        """coeffs: dict key->scalar."""
        M = self.M
        u = np.zeros(M.ndof); sig = np.zeros((M.ne, 6)); F = np.zeros(3); Mo = np.zeros(3); app = np.zeros(3)
        for k, c in coeffs.items():
            s = self.solution(k)
            u += c * s["u"]; sig += c * s["sig"]; F += c * s["F"]; Mo += c * s["M"]; app += c * s["applied"]
        return u, sig, F, Mo, app

    def lc_coeffs(self, case):
        c = {}
        if case.get("self_weight"):
            c["sw"] = 1.0
        for ld in case.get("loads", []):
            d = np.asarray(ld["direction"], float); d = d / np.linalg.norm(d)
            mag = ld["mass_kg"] * GN if "mass_kg" in ld else ld["force_N"]
            where = "shelf" if ld["where"] == "shelf_center" else "tip"
            for ax in range(3):
                if abs(d[ax]) > 1e-12:
                    c[(where, ax)] = c.get((where, ax), 0.0) + mag * d[ax]
        return c


def evaluate_static(R, case, params, mat, lc, bdir, excl_nodes_xyz):
    M = R.M
    coeffs = R.lc_coeffs(case)
    u, sig, F, Mo, app = R.combo(coeffs)
    vm = HexModel.von_mises(sig)
    sn, tau = HexModel.normal_shear(sig, bdir)
    fi1 = vm / mat["allow_xy"]
    fi2 = np.sqrt((np.maximum(sn, 0) / mat["allow_z"]) ** 2 + (tau / (lc["interlayer_shear_ratio"] * mat["allow_z"])) ** 2)
    fi = np.maximum(fi1, fi2)
    cen = M.elem_centers()
    excl = np.zeros(M.ne, bool)
    if len(excl_nodes_xyz):
        d, _ = cKDTree(excl_nodes_xyz).query(cen)
        excl = d < 3.0 * M.h
    fi_ex = np.where(excl, 0.0, fi)
    e = int(np.argmax(fi_ex)); e_raw = int(np.argmax(fi))
    sfreq = case.get("sf_min")
    sf = 1.0 / max(fi_ex[e], 1e-12)
    ut = u.reshape(-1, 3)
    out = {
        "id": case["id"], "title": case["title"],
        "vm_max_MPa_raw": float(vm.max()), "vm_max_MPa": float(vm[e]),
        "vm_p999_MPa": float(np.percentile(vm, 99.9)),
        "fi_max": float(fi_ex[e]), "governing": "inplane_vm/allow_xy" if fi1[e] >= fi2[e] else "interlayer(allow_z)",
        "sf": float(sf), "sf_raw_incl_load_patch": float(1.0 / max(fi.max(), 1e-12)),
        "sf_required": sfreq if isinstance(sfreq, (int, float)) else None,
        "hotspot_xyz": cen[e].round(1).tolist(), "hotspot_raw_xyz": cen[e_raw].round(1).tolist(),
        "tip_disp_mm": ut[R.tip_nodes].mean(0).round(4).tolist(),
        "tip_disp_mag_mm": float(np.linalg.norm(ut[R.tip_nodes].mean(0))),
        "shelf_uz_mm": float(ut[R.shelf_nodes, 2].mean()),
        "max_disp_mm": float(np.linalg.norm(ut, axis=1).max()),
        "reaction_F_N": F.round(3).tolist(), "reaction_M_Nmm_about_origin": Mo.round(1).tolist(),
        "equilibrium_err_N": float(np.linalg.norm(F + app)),
        "applied_F_N": app.round(3).tolist(),
    }
    return out, fi * (sfreq if isinstance(sfreq, (int, float)) else 1.0), cen


def anchor_fea(R, lc, params, mat):
    """screws-only support (no contact: upper bound on tension). Returns per-option per-screw loads for LC1, LC2."""
    M = R.M
    sp_ = screw_positions(params, R.manifest)
    opts = lc["anchor"]["options"]
    res = {}
    # configs: which screws are active
    cfgs = {"stud_2": [i for i, (y, z) in enumerate(sp_) if y > 0], "all4": list(range(len(sp_)))}
        rw = 0.9 * lc["anchor"].get("screw_head_dia_mm", 9.0) / 2 + M.h
    keep_cache = (R.cache, R.support)
    out = {}
    for name, act in cfgs.items():
        nodes = []; owner = []
        for i in act:
            y, z = sp_[i]
            sel = M.nodes_where(lambda X, y=y, z=z: (np.abs(X[:, 0] - R.xmin) < 1e-6) & (np.hypot(X[:, 1] - y, X[:, 2] - z) <= rw))
            nodes.append(sel); owner.append(np.full(len(sel), i))
        allnodes = np.concatenate(nodes); own = np.concatenate(owner)
        M.set_fixed(allnodes); M.factor(); R.cache = {}
        per = {}
        for case_id, mass in (("LC1", 5.0), ("LC2", 15.0)):
            case = {"self_weight": True, "loads": [{"where": "shelf_center", "mass_kg": mass, "direction": [0, 0, -1]}]}
            coeffs = R.lc_coeffs(case)
            tot = {}
            for k, c in coeffs.items():
                s = R.solution(k)
                fn, rn = s["node_react"]
                for j, i in enumerate(act):
                    msk = np.isin(fn, nodes[j])
                    tot[i] = tot.get(i, np.zeros(3)) + c * rn[msk].sum(0)
            per[case_id] = {int(i): v.round(2).tolist() for i, v in tot.items()}
        out[name] = per
    R.cache, R.support = keep_cache
    R.set_support_backface()
    return out, sp_


def run(args):
    t_all = time.time()
    params = load_params(args.params); lc = load_loadcases(args.loadcases); mat = material(lc, params)
    mesh = load_mesh(args.underlay)
    skin = load_mesh(args.skin) if args.skin and Path(args.skin).exists() else None
    manifest = load_manifest(args.params, args.underlay)
    cl = get_centerline(params, manifest)
    pitch = args.pitch or params["shell_wall"] / 2.0
    M, occ, grid, depth, skin_nodes, skin_kg, minfo = build_model(mesh, skin, params, lc, mat, pitch)
    print(f'model: {M.ne} elems {M.ndof} dof build {M.t_build:.1f}s', flush=True)
    R = Runner(M, params, lc, mat, grid, skin_nodes, cl, manifest)
    R.set_support_backface()
    bdir = layer_dir(params)
    val = {}
    vp = Path(__file__).parent / "validation.json"
    if vp.exists():
        val = json.loads(vp.read_text())
    validated = bool(val.get("validated")) and pitch / params["shell_wall"] <= val.get("max_h_over_wall", 0.0) + 1e-9
    mass_under = float((M.elem_mass()).sum() * 1000)
    # loaded node coords for exclusion
    excl_xyz = np.vstack([M.xyz[R.tip_nodes]])
    results = []; U_all = None; cen = None
    for case in lc["load_cases"]:
        if case["kind"] != "static":
            continue
        r, U, cen = evaluate_static(R, case, params, mat, lc, bdir, excl_xyz)
        sfreq = r["sf_required"]
        ok = (r["sf"] >= sfreq) if sfreq else None
        if case["id"] == "LC1":
            r["tip_defl_limit_mm"] = lc["criteria"]["tip_deflection_max_mm"]
            r["defl_metric_mm"] = max(abs(r["shelf_uz_mm"]), abs(r["tip_disp_mag_mm"]))
            r["defl_ok"] = r["defl_metric_mm"] <= r["tip_defl_limit_mm"]
            ok = bool(ok and r["defl_ok"])
        r["pass_numeric"] = None if ok is None else bool(ok)
        r["status"] = ("UNVERIFIED" if not validated else ("PASS" if ok else "FAIL")) if ok is not None else "INFO"
        results.append(r)
        U_all = U if U_all is None else np.maximum(U_all, U)
    # modal
    modal = {}
    try:
        guesses = np.stack([R.solution("sw")["u"], R.solution(("tip", 1))["u"], R.solution(("tip", 0))["u"], R.solution(("shelf", 2))["u"]], 1)
        m_bare = M.lumped_mass(skin_nodes)
        f0, how = M.modes(m_bare, k=4, guess=guesses)
        mp = 5.0 / 1000.0
        extra = (R.shelf_nodes, np.full(len(R.shelf_nodes), mp / len(R.shelf_nodes)))
        m_pl = m_bare.copy(); np.add.at(m_pl, extra[0], extra[1])
        f1, _ = M.modes(m_pl, k=4, guess=guesses)
        modal = {"freq_bare_Hz": f0.round(3).tolist(), "freq_with_5kg_plant_Hz": f1.round(3).tolist(), "method": how,
                 "limit_Hz": lc["criteria"]["freq_min_hz"],
                 "pass_numeric": bool(f1[0] >= lc["criteria"]["freq_min_hz"]),
                 "status": ("UNVERIFIED" if not validated else ("PASS" if f1[0] >= lc["criteria"]["freq_min_hz"] else "FAIL"))}
    except Exception as ex:  # report honestly
        modal = {"status": "ERROR", "error": repr(ex)}
    # anchor
    anchor = {}
    try:
        if args.anchor_fea:
            per, sp_ = anchor_fea(R, lc, params, mat)
            anchor = {"method": "FEA screws-only support (washer patch fixed, no bearing contact => tension upper bound)",
                      "screw_positions_yz": sp_.tolist(), "per_config": per}
    except Exception as ex:
        anchor = {"status": "ERROR", "error": repr(ex)}
    # station utilization
    stations = []
    if cl is not None and U_all is not None:
        fr, _ = cl.project(cen)
        bins = np.linspace(0, 1, 11)
        for a, b in zip(bins[:-1], bins[1:]):
            m = (fr >= a) & (fr < b + (1e-9 if b == 1 else 0))
            if m.any():
                stations.append({"s0": round(a, 2), "s1": round(b, 2), "util_max": float(U_all[m].max()), "util_p95": float(np.percentile(U_all[m], 95)), "n": int(m.sum())})
    mass = {"underlay_kg": round(mass_under, 4), "skin_kg": round(skin_kg, 4)}
    stat = [r["status"] for r in results if r["status"] != "INFO"] + [modal.get("status", "ERROR")]
    overall = "FAIL" if "FAIL" in stat else ("UNVERIFIED" if ("UNVERIFIED" in stat or "ERROR" in stat or minfo["anomalous_cells"]) else "PASS")
    rep = {"tool": "sim.run_fea", "date": TODAY, "inputs": {"underlay": str(args.underlay), "skin": str(args.skin) if skin is not None else None, "params": str(args.params), "loadcases": str(args.loadcases)},
           "material": mat["name"],
           "model": {"pitch_mm": pitch, "h_over_wall": pitch / params["shell_wall"], "n_elem": M.ne, "n_dof": M.ndof, "solver": M.method, "mass": mass, **minfo,
                     "support": R.support, "shelf_point": R.shelf.round(2).tolist(), "tip_point": R.tip.round(2).tolist(),
                     "layer_dir": bdir.tolist(), "wall_s": round(time.time() - t_all, 1)},
           "solver_validation": {"validated": validated, **{k: val.get(k) for k in ("max_h_over_wall", "date", "summary")}},
           "solves": R.solve_log, "load_cases": results, "modal": modal, "anchor_fea": anchor, "station_utilization": stations,
           "summary": {"status": overall, "min_sf_lc1_lc3": min([r["sf"] for r in results if r["id"].startswith(("LC1", "LC3"))] or [None]),
                       "notes": ["SF uses elements farther than 3h from tip-load nodes; raw SF incl. load patch also reported",
                                 "Pass numbers are UNVERIFIED unless solver validated (sim/validation.json) at this h/wall"]}}
    outd = Path(args.out); outd.mkdir(parents=True, exist_ok=True)
    name = args.name
    (outd / f"{name}.json").write_text(json.dumps(rep, indent=1, default=float))
    write_md(rep, outd / f"{name}.md")
    if not args.no_fields:
        np.savez_compressed(outd / f"{name}_fields.npz", centers=cen.astype(np.float32),
                            sig_sw=R.solution("sw")["sig"], sig_plant=R.solution(("shelf", 2))["sig"],
                            sig_tipy=R.solution(("tip", 1))["sig"], sig_tipx=R.solution(("tip", 0))["sig"])
    return rep


def write_md(rep, path):
    m = rep["model"]; L = []
    L.append(f"# FEA report ({rep['date']})\n")
    L.append(f"**Status: {rep['summary']['status']}**  solver validated: {rep['solver_validation']['validated']}\n")
    L.append(f"- model: {m['n_elem']} hex cells, {m['n_dof']} dof, pitch {m['pitch_mm']} mm (h/wall {m['h_over_wall']:.2f}), solver {m['solver']}, underlay {m['mass']['underlay_kg']} kg, skin {m['mass']['skin_kg']} kg, wall time {m['wall_s']} s")
    L.append(f"- inputs: {rep['inputs']}; material {rep['material']}; layer dir {m['layer_dir']}; shelf pt {m['shelf_point']}; tip pt {m['tip_point']}")
    if m["anomalous_cells"]:
        L.append(f"- WARNING: {m['anomalous_cells']} voxel cells with winding not in {{0,1}} (self-overlap / inverted shell)")
    L.append("\n| LC | SF | SF req | vM max MPa (excl.patch) | raw | governing | hotspot xyz | tip disp mm | status |\n|---|---|---|---|---|---|---|---|---|")
    for r in rep["load_cases"]:
        L.append(f"| {r['id']} | {r['sf']:.2f} | {r['sf_required']} | {r['vm_max_MPa']:.2f} | {r['vm_max_MPa_raw']:.2f} | {r['governing']} | {r['hotspot_xyz']} | {r['tip_disp_mag_mm']:.2f} | {r['status']} |")
    lc1 = [r for r in rep["load_cases"] if r["id"] == "LC1"]
    if lc1:
        r = lc1[0]
        L.append(f"\nLC1 deflection metric (max of shelf uz, tip |u|): {r['defl_metric_mm']:.2f} mm vs limit {r['tip_defl_limit_mm']} -> {'ok' if r['defl_ok'] else 'EXCEEDS'}; shelf uz {r['shelf_uz_mm']:.2f}, tip {r['tip_disp_mm']}")
        L.append(f"LC1 reaction F {r['reaction_F_N']} N, M(about origin) {r['reaction_M_Nmm_about_origin']} N*mm, equilibrium err {r['equilibrium_err_N']:.3f} N")
    md = rep["modal"]
    L.append(f"\n## Modal ({md.get('method')})\nbare {md.get('freq_bare_Hz')} Hz; with 5 kg plant {md.get('freq_with_5kg_plant_Hz')} Hz; limit {md.get('limit_Hz')} -> {md.get('status')}")
    if rep["anchor_fea"].get("per_config"):
        L.append("\n## Anchor (FEA screws-only support; screw index = order in screw_positions_yz; per-screw [Fx,Fy,Fz] N, +X = pull-out from wall)")
        L.append(f"positions (y,z): {rep['anchor_fea']['screw_positions_yz']}")
        for cfg, per in rep["anchor_fea"]["per_config"].items():
            for lcid, v in per.items():
                L.append(f"- {cfg} {lcid}: {v}")
    if rep["station_utilization"]:
        L.append("\n## Utilization along span (U = FI*SF_req; U<1 passes; U<<1 = mass can be cut)\n| s0-s1 | U max | U p95 |\n|---|---|---|")
        for s in rep["station_utilization"]:
            L.append(f"| {s['s0']}-{s['s1']} | {s['util_max']:.2f} | {s['util_p95']:.2f} |")
    L.append("\n" + "\n".join("- " + n for n in rep["summary"]["notes"]))
    L.append("\n---\n*Edit log*\n\n| Date | Agent | Change | Signed-off-by |\n|------|-------|--------|---------------|\n| " + rep["date"] + " | verif-fea (generated) | auto-generated by sim.run_fea | [PROVISIONAL] |")
    Path(path).write_text("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--underlay", required=True); ap.add_argument("--skin"); ap.add_argument("--params", required=True)
    ap.add_argument("--loadcases", default=str(P0 / "loadcases.json")); ap.add_argument("--out", required=True)
    ap.add_argument("--pitch", type=float); ap.add_argument("--name", default="fea")
    ap.add_argument("--no-anchor-fea", dest="anchor_fea", action="store_false"); ap.add_argument("--no-fields", action="store_true")
    a = ap.parse_args(); rep = run(a)
    print(rep["summary"]["status"], [(r["id"], round(r["sf"], 2), r["status"]) for r in rep["load_cases"]], rep["modal"].get("freq_with_5kg_plant_Hz"))


if __name__ == "__main__":
    main()
