"""Thickness / rib / architecture sensitivity sweep (analytic frame on regenerated geometry). Tells Geometry where mass can be cut.
python -m sim.sweep --params prototype/p0/params.json --out <dir> [--quick]
Needs prototype/p0/generate.py (--params/--out). Does NOT touch prototype/p0/out (writes variants under <dir>/work).
"""
from __future__ import annotations
import argparse, copy, json, subprocess, sys, time
from pathlib import Path
import numpy as np
from .common import *
from .analytic import run_analytic as RA

ROOT_ = Path(__file__).resolve().parent.parent


def setp(d, path, v):
    ks = path.split(".")
    for k in ks[:-1]:
        d = d[k]
    d[ks[-1]] = v


class NS: pass


def run_variant(name, base, patch, work, gen, lcpath):
    p = copy.deepcopy(base)
    for k, v in patch.items():
        setp(p, k, v)
    d = work / name; (d / "out").mkdir(parents=True, exist_ok=True)
    (d / "params.json").write_text(json.dumps(p, indent=1))
    t0 = time.time()
    r = subprocess.run([sys.executable, str(gen), "--params", str(d / "params.json"), "--out", str(d / "out"), "--no-previews"], capture_output=True, text=True, cwd=str(ROOT_))
    if r.returncode != 0:
        return {"name": name, "patch": patch, "error": r.stderr[-300:]}
    ns = NS(); ns.underlay = str(d / "out/underlay.stl"); ns.skin = str(d / "out/skin.stl"); ns.params = str(d / "params.json"); ns.loadcases = lcpath
    ns.out = str(d / "rep"); ns.name = "analytic"; ns.stations = 30; ns.joints = None
    o = RA.run(ns)
    l = {c["id"]: c for c in o["load_cases"]}
    U = np.max([c["util_by_station"] for c in o["load_cases"] if c.get("util_by_station")], axis=0)
    return {"name": name, "patch": patch, "mass_beam_kg": o["mass_kg"], "min_sf_lc1_lc3": o["summary"]["min_sf_lc1_lc3"], "lc2_sf": l["LC2"]["sf"], "lc1_tip_mm": l["LC1"]["defl_metric_mm"],
            "f1_plant_Hz": o["modal"]["freq_with_5kg_plant_Hz"][0], "util_by_station": [round(float(x), 3) for x in U], "stations_s": [s["s"] for s in o["sections"]][:len(U)],
            "gen_s": round(time.time() - t0, 1), "all_pass_numeric": o["summary"]["all_pass_numeric"]}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--params", required=True); ap.add_argument("--out", required=True); ap.add_argument("--quick", action="store_true")
    ap.add_argument("--loadcases", default=str(P0 / "loadcases.json")); a = ap.parse_args()
    base = load_params(a.params); out = Path(a.out); work = out / "work"; work.mkdir(parents=True, exist_ok=True)
    gen = P0 / "generate.py"
    variants = [("base", {})]
    for w in (1.6, 2.0, 3.0):
        variants.append((f"wall{w}", {"shell_wall": w}))
    for pch in (24, 72):
        variants.append((f"ribpitch{pch}", {"ribs.pitch": pch}))
    for arch in ("lattice", "spine_beam"):
        variants.append((f"arch_{arch}", {"architecture": arch}))
    if not a.quick:
        variants += [("wall1.6_ribpitch72", {"shell_wall": 1.6, "ribs.pitch": 72}), ("wall2.0_ribpitch72", {"shell_wall": 2.0, "ribs.pitch": 72})]
    res = []
    for n, pth in variants:
        r = run_variant(n, base, pth, work, gen, a.loadcases); res.append(r)
        print(n, {k: r.get(k) for k in ("mass_beam_kg", "min_sf_lc1_lc3", "lc1_tip_mm", "f1_plant_Hz", "error")}, flush=True)
    b = next(r for r in res if r["name"] == "base" and "error" not in r)
    L = [f"# Thickness / rib / architecture sensitivity ({TODAY})\n", "Analytic beam frame on regenerated underlay meshes (analytic only, not FEA). Mass = beam-integrated underlay (infill-equivalent), root block excluded. SF per spec allowables; LC2 needs 1.5, LC1/LC3 need 3.0; tip limit 6 mm; f1 >= 8 Hz.\n",
         "| variant | mass kg | d mass % | min SF LC1/LC3 | LC2 SF | LC1 tip mm | f1 Hz | pass |\n|---|---|---|---|---|---|---|---|"]
    for r in res:
        if "error" in r:
            L.append(f"| {r['name']} | error: {r['error'][:80]} | | | | | | |"); continue
        L.append(f"| {r['name']} | {r['mass_beam_kg']:.3f} | {100*(r['mass_beam_kg']/b['mass_beam_kg']-1):+.1f} | {r['min_sf_lc1_lc3']:.2f} | {r['lc2_sf']:.2f} | {r['lc1_tip_mm']:.2f} | {r['f1_plant_Hz']:.1f} | {r['all_pass_numeric']} |")
    U = np.array(b["util_by_station"]); s = np.array(b["stations_s"])
    cut = [f"s={s[i]:.2f} (U={U[i]:.2f})" for i in range(len(U)) if U[i] < 0.35]
    L.append(f"\nBaseline utilization U = FI*SF_req (analytic, max over LCs): max {U.max():.2f} at s={s[int(U.argmax())]:.2f}; stations with U < 0.35 (mass-cut candidates): {', '.join(cut) if cut else 'none'}")
    L.append("\n---\n*Edit log*\n\n| Date | Agent | Change | Signed-off-by |\n|------|-------|--------|---------------|\n| " + TODAY + " | verif-fea (generated) | sim.sweep | [PROVISIONAL] |")
    (out / "sweep.md").write_text("\n".join(L) + "\n"); (out / "sweep.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
