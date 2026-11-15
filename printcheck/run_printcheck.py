"""python -m printcheck.run_printcheck --underlay f.stl [--segments dir] [--params p.json] --out reports/ [--assembly f.stl]"""
from __future__ import annotations
import argparse, json, time
from pathlib import Path
import numpy as np
import trimesh

from sim.common import load_params, load_loadcases, material, P0, TODAY, load_manifest
from sim.voxel import load_mesh
from . import checks as C
from .joints import joint_fit
from .segments import evaluate_segments


def check_mesh(m, mat, wall, name, scan=True, thin_pitch=None, pm_path=None):
    t0 = time.time()
    r = {"name": name, "bounds": m.bounds.round(1).tolist(), "extents": m.extents.round(1).tolist()}
    r["integrity"] = C.mesh_integrity(m)
    best, allo = C.best_orientation(m)
    r["orientations"] = allo; r["best_orientation"] = best
    up = {"+z": [0, 0, 1], "-z": [0, 0, -1], "+x": [1, 0, 0], "-x": [-1, 0, 0], "+y": [0, 1, 0], "-y": [0, -1, 0]}[best["up"]]
    r["bridge"] = C.bridges(m, np.array(up, float))     # near-horizontal (<20 deg) downward patches only
    r["bridge"]["limit_mm"] = C.LIM["bridge_max_mm"]; r["bridge"]["pass"] = bool(r["bridge"]["max_minor_extent_mm"] <= C.LIM["bridge_max_mm"])
    r["overhang"] = {"fraction": best["overhang_fraction"], "limit": C.LIM["overhang_area_fraction_max"], "pass": bool(best["overhang_fraction"] <= C.LIM["overhang_area_fraction_max"]),
                     "support_volume_proxy_cm3": best["support_volume_proxy_cm3"]}
    r["bed"] = {"fits_bed_256": best["fits_bed"], "fits_target_240": best["fits_target"], "xy_extent_mm": best["xy_extent_mm"], "height_mm": best["height_mm"], "pass": bool(best["fits_bed"])}
    if scan:
        r["thickness"] = C.thin_scan(m, pitch=thin_pitch)
    r["mass_time"] = C.mass_time(m, mat["rho_g_cm3"], wall)
    pf = Path(pm_path) if pm_path else None
    if pf is not None and pf.exists():       # Geometry's own heuristic print orientation (build +Z): evaluate as-is
        pm = load_mesh(pf); st = C.orient_stats(pm, np.array([0, 0, 1.0])); st.pop("_over_mask")
        bb = C.bridges(pm, np.array([0, 0, 1.0]))
        r["geometry_print_orientation"] = {"file": pf.name, "extents": pm.extents.round(1).tolist(), "overhang_fraction": st["overhang_fraction"], "support_volume_proxy_cm3": st["support_volume_proxy_cm3"],
                                           "bridge_minor_mm": bb["max_minor_extent_mm"], "worst_bridge_center": bb.get("worst_patch_center"), "fits_bed": bool(max(pm.extents) <= C.LIM["bed_mm"])}
    r["wall_s"] = round(time.time() - t0, 1)
    return r


def run(a):
    params = load_params(a.params) if a.params else {"shell_wall": 2.4}
    lc = load_loadcases(a.loadcases); mat = material(lc, params); wall = params.get("shell_wall", 2.4)
    out = {"tool": "printcheck.run_printcheck", "date": TODAY, "limits": C.LIM, "material": mat["name"], "inputs": {"underlay": a.underlay, "segments": a.segments}}
    under = load_mesh(a.underlay)
    out["underlay"] = check_mesh(under, mat, wall, "underlay", scan=a.scan_underlay and not a.skip_thin, thin_pitch=a.thin_pitch)
    segs = {}
    if a.segments and Path(a.segments).exists():
        files = sorted(Path(a.segments).glob("seg_[0-9][0-9].stl"))
        for f in files:
            segs[f.stem] = load_mesh(f)
        out["segments"] = {k: check_mesh(v, mat, wall, k, scan=not a.skip_thin, thin_pitch=a.thin_pitch, pm_path=Path(a.segments) / f"{k}_print.stl") for k, v in segs.items()}
        names = list(segs)
        joints = []
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                jf = joint_fit(segs[names[i]], segs[names[j]])
                if jf["mating"]:
                    jf["pair"] = [names[i], names[j]]; joints.append(jf)
        out["joints"] = joints
        if a.assembly and Path(a.assembly).exists():
            asm = load_mesh(a.assembly)
            out["segment_volume_closure"] = {"sum_segment_vol_mm3": float(sum(m.volume for m in segs.values())), "assembly_vol_mm3": float(asm.volume),
                                             "note": "sum of segments exceeds assembly when joints add overlap/pins; large deficit = lost material"}
        out["segmentation_eval"] = evaluate_segments(segs, params, a.analytic, a.fea_fields, out["joints"], load_manifest(a.params, a.underlay) if a.params else None)
    # verdict
    items = []
    def add(name, ok, detail): items.append({"check": name, "status": "PASS" if ok else "FAIL", "detail": detail})
    for nm, r in [("underlay", out["underlay"])] + list(out.get("segments", {}).items()):
        add(f"{nm}: manifold/watertight/no self-overlap", r["integrity"]["pass"], {k: r["integrity"][k] for k in ("watertight", "non_manifold_edges", "open_edges", "self_intersection_proxy_cells")})
        if "thickness" in r:
            add(f"{nm}: min wall >= {C.LIM['min_wall_mm']} mm", r["thickness"]["pass_min_wall"], {"resolved_ge": r["thickness"]["min_wall_resolved_ge_mm"]})
        if nm != "underlay":     # monolith is not printed; overhang/bridge/bed apply to printable segments
            add(f"{nm}: overhang fraction <= {C.LIM['overhang_area_fraction_max']}", r["overhang"]["pass"], round(r["overhang"]["fraction"], 3))
            add(f"{nm}: bridge <= {C.LIM['bridge_max_mm']} mm", r["bridge"]["pass"], round(r["bridge"]["max_minor_extent_mm"], 1))
            add(f"{nm}: bed fit 256", r["bed"]["pass"], r["bed"]["xy_extent_mm"] + [r["bed"]["height_mm"]])
    if "segments" not in out:
        add("segments: >=2 segments each fit bed", False, "no segments provided (UNVERIFIED)")
        for it in items[-1:]:
            it["status"] = "UNVERIFIED"
    for j in out.get("joints", []):
        add(f"joint {j['pair']}: no interference, no binding/loose clearance", j["pass"], {k: j[k] for k in ("interference_mm3", "gap_median_mm", "band_fractions")})
    out["checks"] = items
    out["summary"] = {"status": "FAIL" if any(i["status"] == "FAIL" for i in items) else ("UNVERIFIED" if any(i["status"] == "UNVERIFIED" for i in items) else "PASS"),
                      "n_fail": sum(i["status"] == "FAIL" for i in items), "n_unverified": sum(i["status"] == "UNVERIFIED" for i in items)}
    outd = Path(a.out); outd.mkdir(parents=True, exist_ok=True)
    (outd / f"{a.name}.json").write_text(json.dumps(out, indent=1, default=float))
    write_md(out, outd / f"{a.name}.md")
    return out


def write_md(o, path):
    L = [f"# Printability report ({o['date']})\n", f"**Status: {o['summary']['status']}** ({o['summary']['n_fail']} fail, {o['summary']['n_unverified']} unverified); material {o['material']}\n",
         "| check | status | detail |\n|---|---|---|"]
    for i in o["checks"]:
        L.append(f"| {i['check']} | {i['status']} | {i['detail']} |")
    u = o["underlay"]
    L.append(f"\n## Underlay\nextents {u['extents']} mm; best orientation up={u['best_orientation']['up']} overhang {u['overhang']['fraction']:.3f}, support-volume proxy {u['overhang']['support_volume_proxy_cm3']:.0f} cm3 (upper bound); mass @20 % infill {u['mass_time']['mass_kg_20pct_infill']:.3f} kg (solid {u['mass_time']['mass_kg_solid']:.3f}); time proxy {u['mass_time']['print_time_proxy_h']:.1f} h")
    if "thickness" in u:
        L.append("\nThin-material scan (opening residual; volume of material thinner than t, clusters >= 30 cells):\n\n| t mm | thin vol mm3 | clusters | worst at |\n|---|---|---|---|")
        for t, v in u["thickness"]["by_threshold"].items():
            L.append(f"| {t} | {v['vol_mm3']:.1f} | {v['clusters']} | {v['worst']} |")
        L.append(f"\n{u['thickness']['note']} (pitch {u['thickness']['pitch_mm']} mm)")
    for k, s in o.get("segments", {}).items():
        L.append(f"\n## {k}\nextents {s['extents']}; best up {s['best_orientation']['up']} fits256={s['bed']['fits_bed_256']} fits240={s['bed']['fits_target_240']}; overhang {s['overhang']['fraction']:.3f}; bridge minor {s['bridge']['max_minor_extent_mm']:.1f} mm at {s['bridge'].get('worst_patch_center')}; mass {s['mass_time']['mass_kg_20pct_infill']:.3f} kg; time proxy {s['mass_time']['print_time_proxy_h']:.1f} h")
        g = s.get("geometry_print_orientation")
        if g:
            L.append(f"  - Geometry's {g['file']} (+Z build): overhang {g['overhang_fraction']:.3f}, bridge minor {g['bridge_minor_mm']:.1f} mm at {g['worst_bridge_center']}, support-volume proxy {g['support_volume_proxy_cm3']:.0f} cm3, fits bed {g['fits_bed']}")
    if o.get("joints"):
        L.append("\n## Joints\n")
        for j in o["joints"]:
            L.append(f"- {j['pair']}: interference {j['interference_mm3']:.1f} mm3, gap min/p5/median {j['gap_min_mm']:.3f}/{j['gap_p5_mm']:.3f}/{j['gap_median_mm']:.3f} mm over {j['n_mating_samples']} mating samples; bands {j['band_fractions']}; nominal {o['limits']['joint_clearance_mm']}, accept {o['limits']['joint_clearance_accept_mm']} -> {'PASS' if j['pass'] else 'FAIL'}; {j['note']}")
    if "segmentation_eval" in o:
        e = o["segmentation_eval"]
        L.append(f"\n## Segmentation score: {e['total']:.2f}/1.00\n")
        for k, v in e["components"].items():
            L.append(f"- {k}: {v['score']:.2f} - {v['detail']}")
    L.append("\n---\n*Edit log*\n\n| Date | Agent | Change | Signed-off-by |\n|------|-------|--------|---------------|\n| " + o["date"] + " | verif-print (generated) | auto-generated by printcheck.run_printcheck | [PROVISIONAL] |")
    Path(path).write_text("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--underlay", required=True); ap.add_argument("--segments"); ap.add_argument("--assembly"); ap.add_argument("--params")
    ap.add_argument("--loadcases", default=str(P0 / "loadcases.json")); ap.add_argument("--analytic"); ap.add_argument("--fea-fields", dest="fea_fields")
    ap.add_argument("--out", required=True); ap.add_argument("--name", default="printability"); ap.add_argument("--skip-thin", action="store_true"); ap.add_argument("--scan-underlay", action="store_true", help="thin-wall scan on the monolith too (slow; segments always scanned)"); ap.add_argument("--thin-pitch", type=float)
    a = ap.parse_args(); o = run(a); print(o["summary"])


if __name__ == "__main__":
    main()
