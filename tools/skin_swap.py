"""Layering-contract + skin-swap test (spec Exit criterion 5).
Checks: (a) skin proud <= max_proud of underlay outer surface, (b) skin removes no underlay material, (c) shelf flat untouched (needs manifest),
(d) response sensitivity to skin mass (analytic frame; skin mass-only per spec): delta tip deflection / max stress / f1 for skin = none, given, 2x.
Spec requires underlay stress/deflection within 2 % for any valid skin. This is evaluated honestly: mass-only coupling can violate 2 % if skin is heavy.
"""
import argparse, json, sys
from pathlib import Path
import numpy as np
import trimesh
import manifold3d as m3d
from scipy.spatial import cKDTree

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sim.voxel import load_mesh
from sim.common import *
from sim.analytic import run_analytic as RA

DATE = TODAY


def man(m):
    return m3d.Manifold(m3d.Mesh(np.asarray(m.vertices, np.float32), np.asarray(m.faces, np.uint32)))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--underlay", required=True); ap.add_argument("--skin", required=True); ap.add_argument("--params", required=True)
    ap.add_argument("--loadcases", default=str(P0 / "loadcases.json")); ap.add_argument("--out", required=True); ap.add_argument("--assembly"); a = ap.parse_args()
    params = load_params(a.params); lc = load_loadcases(a.loadcases); manifest = load_manifest(a.params, a.underlay)
    U = load_mesh(a.underlay); S = load_mesh(a.skin)
    maxp = (params.get("skin") or {}).get("max_proud", 6.0)
    checks = []
    # (a) proud distance
    pts, _ = trimesh.sample.sample_surface(U, int(min(U.area / 1.0, 2_000_000)), seed=0)
    d, _ = cKDTree(pts).query(S.vertices)
    tol = 0.8  # sampling spacing ~1 mm => distance overestimate up to ~0.7
    checks.append({"check": f"skin max distance from underlay surface <= {maxp} mm", "value_mm": float(d.max()), "p99_mm": float(np.percentile(d, 99)),
                   "status": "PASS" if d.max() <= maxp + tol else "FAIL", "note": f"surface samples ~1 mm; tolerance +{tol} mm. Distance is to nearest underlay SAMPLE, not exact."})
    # (b) skin removes no underlay material
    try:
        A_ = man(load_mesh(a.assembly)) if a.assembly and Path(a.assembly).exists() else man(U) + man(S)
        lost = float((man(U) - A_).volume())
        checks.append({"check": "underlay volume not removed by skin/assembly (U - A)", "value_mm3": lost, "status": "PASS" if lost < 1e-4 * U.volume else "FAIL"})
    except Exception as ex:
        checks.append({"check": "underlay volume not removed", "status": "UNVERIFIED", "note": repr(ex)})
    # (c) shelf flat free of skin
    sh = (manifest or {}).get("shelf")
    if sh:
        fr = sh["frame"]; o = np.array(fr["origin"]); Tn = np.array(fr["T"]); Nn = np.array(fr["N"])
        rel = S.vertices - o
        t = rel @ Tn; n = rel @ Nn; z = S.vertices[:, 2]
        inside = (np.abs(t) <= fr["t_range"][1]) & (np.abs(n) <= fr["n_half"])
        above = inside & (z >= sh["plane_z"] - 0.05 - 0.0)
        # skin below plane within rect is ok (keepout is the plane surface and above). Count vertices at/above the plane within rect
        checks.append({"check": "no skin vertices on/above shelf plane within flat rectangle", "n_violating_vertices": int(above.sum()), "status": "PASS" if above.sum() == 0 else "FAIL"})
        # also underlay flatness: z spread of underlay top surface in rect
    else:
        checks.append({"check": "shelf flat free of skin", "status": "UNVERIFIED", "note": "no geometry_manifest.json shelf frame"})
    # (d) mass-coupling sensitivity via analytic frame
    class NS: pass
    res = {}
    for name, fac in (("none", 0.0), ("given", 1.0), ("double", 2.0)):
        lc2 = json.loads(json.dumps(lc)); lc2["skin"]["mass_factor"] = lc["skin"]["mass_factor"] * fac
        tmp = Path(a.out) / f"_lc_{name}.json"; tmp.write_text(json.dumps(lc2))
        ns = NS(); ns.underlay = a.underlay; ns.skin = a.skin if fac > 0 else None; ns.params = a.params; ns.loadcases = str(tmp); ns.out = str(Path(a.out) / "_swap_tmp")
        ns.name = f"an_{name}"; ns.stations = 0; ns.spacing = 6.0; ns.joints = None
        o = RA.run(ns); tmp.unlink()
        l1 = next(c for c in o["load_cases"] if c["id"] == "LC1")
        res[name] = {"mass_kg": o["mass_kg"], "tip_u": l1["tip_disp_mag_mm"], "sigma": l1["sigma_max_MPa"], "f1_plant": o["modal"]["freq_with_5kg_plant_Hz"][0]}
    base = res["none"]
    sw = {}
    for k in ("given", "double"):
        sw[k] = {m: 100 * (res[k][m] / base[m] - 1) for m in ("tip_u", "sigma", "f1_plant")}
    worst = max(abs(v) for v in sw["given"].values())
    ratio = worst / 2.0
    skin_mass_g = (res["given"]["mass_kg"] - res["none"]["mass_kg"]) * 1000
    checks.append({"check": "skin-mass coupling: underlay response change <= 2 % (given skin vs none, analytic frame)", "deltas_pct": sw["given"], "doubled_skin_deltas_pct": sw["double"],
                   "skin_mass_g_effective": skin_mass_g, "status": "PASS" if worst <= 2.0 else "FAIL",
                   "note": f"skin is mass-only per spec; sensitivity ~ {worst/max(skin_mass_g,1e-9)*100:.2f} % per 100 g; 2 % budget ~ {2.0/max(worst/max(skin_mass_g,1e-9),1e-12):.0f} g effective skin mass (analytic, LC1)"})
    checks.append({"check": "alternate skin styles (true swap): UNVERIFIED", "status": "UNVERIFIED", "note": "only one skin mesh available; Geometry's generator overwrites out/ so styles were not re-run; mass-sensitivity above bounds any style by mass (not by stiffness; skin stiffness ignored by contract)"})
    stat = "FAIL" if any(c["status"] == "FAIL" for c in checks) else ("UNVERIFIED" if any(c["status"] == "UNVERIFIED" for c in checks) else "PASS")
    out = {"tool": "tools/skin_swap.py", "date": DATE, "checks": checks, "responses": res, "summary": {"status": stat}}
    d = Path(a.out); d.mkdir(parents=True, exist_ok=True)
    (d / "skin_swap.json").write_text(json.dumps(out, indent=1, default=float))
    L = [f"# Layering contract / skin-swap ({DATE})\n", f"Status: **{stat}**\n", "| check | status | detail |\n|---|---|---|"]
    for c in checks:
        det = {k: v for k, v in c.items() if k not in ("check", "status")}
        L.append(f"| {c['check']} | {c['status']} | {json.dumps(det, default=float)[:400]} |")
    L.append("\n---\n*Edit log*\n\n| Date | Agent | Change | Signed-off-by |\n|------|-------|--------|---------------|\n| " + DATE + " | verif-print (generated) | tools/skin_swap.py | [PROVISIONAL] |")
    (d / "skin_swap.md").write_text("\n".join(L) + "\n")
    import shutil; shutil.rmtree(d / "_swap_tmp", ignore_errors=True)
    print(stat)

if __name__ == "__main__":
    main()
