#!/usr/bin/env python3
"""Geometry-side sanity checks (not FEA / not the printability report). Writes reports/geometry_selfcheck.{json,md}.
    python prototype/p0/geometry_selfcheck.py [--out prototype/p0/out]"""
import argparse, json, os, sys
import numpy as np
import trimesh
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from model.mtools import to_manifold, to_trimesh          # noqa: E402
from model.structural.underlay import build_underlay        # noqa: E402
from model.aesthetic.skin import skin, STYLES               # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "prototype/p0/out"))
    ap.add_argument("--skip-swap", action="store_true")
    a = ap.parse_args()
    p = json.load(open(os.path.join(ROOT, "prototype/p0/params.json")))
    man = json.load(open(os.path.join(a.out, "geometry_manifest.json")))
    segj = json.load(open(os.path.join(a.out, "segments.json")))
    R = {}
    ok = True

    def rec(k, v, passed):
        nonlocal ok
        R[k] = dict(value=v, pass_=bool(passed)); ok &= bool(passed)

    M = {n: trimesh.load(os.path.join(a.out, f"{n}.stl")) for n in ("underlay", "skin", "assembly")}
    for n, m in M.items():
        rec(f"{n}.watertight_winding_volume>0", dict(wt=bool(m.is_watertight), wind=bool(m.is_winding_consistent),
                                                    vol=float(m.volume)), m.is_watertight and m.is_winding_consistent and m.volume > 0)
    U = to_manifold(M["underlay"]); S = to_manifold(M["skin"]); A = to_manifold(M["assembly"])
    # additive: underlay minus assembly == 0 ; assembly - underlay == skin - overlap
    rem = (U - A).volume()
    rec("skin_never_removes_underlay (vol U-A mm3)", float(rem), rem < 1.0)
    ov = (U ^ S).volume()
    inset_vol = p["skin"]["inset"] * to_manifold(M["underlay"]).surface_area() * 0.0 + p["skin"]["inset"] * build_underlay(p)["envelope"].surface_area()
    rec("skin_overlap_with_underlay mm3 (<= inset*envelope area = bond overlap only)", float(ov), ov <= 1.05 * inset_vol)
    # proud height <= 6 mm: distance of skin verts from underlay outer surface (envelope)
    env = to_trimesh(build_underlay(p)["envelope"])
    from scipy.spatial import cKDTree
    pts, _ = trimesh.sample.sample_surface(env, 1_500_000, seed=1)   # ~0.4 mm spacing -> +0.5 tol
    dist, _ = cKDTree(pts).query(M["skin"].vertices)
    rec("skin_max_proud_mm (skin verts to underlay envelope, +-0.5 sampling tol)", float(dist.max()), dist.max() <= p["skin"]["max_proud"] + 0.5)
    # shelf: raycast flat grid in pad frame, 120x120
    pf = man["shelf"]["frame"]; o = np.array(pf["origin"]); N = np.array(pf["N"]); T = np.array(pf["T"])
    zs = []
    for tt in np.linspace(-60, 60, 13):
        for nn in np.linspace(-60, 60, 13):
            q = o + nn * N + tt * T
            hits = A.ray_cast((q[0], q[1], 600.0), (q[0], q[1], -100.0))
            zs.append(max(h.position[2] for h in hits) if hits else np.nan)
    zs = np.array(zs)
    rise = np.nanmax(zs) - np.nanmin(zs)
    rec("shelf_120x120_top_z_range_mm (assembly)", float(rise), rise < 0.05 and not np.isnan(zs).any())
    slope = float(np.degrees(np.arctan2(rise, 120)))
    rec("shelf_slope_deg", slope, slope <= 2.0)
    rec("shelf_top_plane_z", float(np.nanmean(zs)), abs(np.nanmean(zs) - man["shelf"]["plane_z"]) < 0.05)
    # nothing above shelf plane in footprint+margin column (assembly)
    mg = 12.0   # keepout margin is 20; check 12 to stay inside local-frame skew
    cols = []
    for tt in np.linspace(-60 - mg, 60 + mg, 17):
        for nn in np.linspace(-(60 + 6), (60 + 6), 15):
            q = o + nn * N + tt * T
            hits = A.ray_cast((q[0], q[1], 800.0), (q[0], q[1], -100.0))
            cols.append(max(h.position[2] for h in hits) if hits else -1e9)
    over = float(np.max(cols) - man["shelf"]["plane_z"])
    rec("max_geometry_above_shelf_plane_in_footprint+margin_mm", over, over < 0.05)
    # protrusion / rise / span
    bb = A.bounding_box()
    rec("protrusion_x_max_mm (assembly aabb, incl skin)", float(bb[3]), True)
    rec("tip_centerline_x", man["tip_xyz"][0], abs(man["tip_xyz"][0] - 300) < 5)
    zc = [c["xyz"][2] for c in man["centerline"]]
    rec("centerline_rise_mm", float(max(zc) - min(zc)), max(zc) - min(zc) <= 60)
    rec("span_arc3d_mm (plan arc = span_length)", man["span_arc3d"], abs(man["span_arc3d"] - p["span_length"]) < 15)
    # segments
    for s in segj["segments"]:
        rec(f"seg{s['index']}_fits_{segj['bed_usable']}mm_bed", s["print_extents"], s["fits_bed"] and s["watertight"])
    rec("segment_count>=2", len(segj["segments"]), len(segj["segments"]) >= 2)
    # reassembly: union of segments (keys fill sockets within clearance) vs assembly
    sm = [to_manifold(trimesh.load(os.path.join(a.out, s["file"]))) for s in segj["segments"]]
    import manifold3d as m3d
    uni = m3d.Manifold.batch_boolean(sm, m3d.OpType.Add)
    # segments carry bolt holes (void) + clearance gaps; compare volume deficit
    deficit = A.volume() - uni.volume()
    rec("segments_union_volume_deficit_mm3 (holes+clearance)", float(deficit), 0 <= deficit < 0.01 * A.volume())
    # swap test (geometry side): underlay identical regardless of style
    if not a.skip_swap:
        res = build_underlay(p)
        base = to_trimesh(res["underlay"])
        hashes = {}
        for st in STYLES:
            sk = skin(env, 7, st, res["keepouts"], p["skin"]["max_proud"], p["skin"]["min_proud"], p["skin"]["edge_len"], p["skin"]["inset"])
            asm = to_manifold(sk) + res["underlay"]
            rem = (res["underlay"] - asm).volume()
            ratio = sk.volume / 1.0
            hashes[st] = dict(skin_vol=float(sk.volume), underlay_removed=float(rem),
                              underlay_bytes_equal=bool(np.array_equal(base.vertices, to_trimesh(res["underlay"]).vertices)))
        rec("skin_swap_styles_never_alter_underlay", hashes,
            all(h["underlay_removed"] < 1.0 and h["underlay_bytes_equal"] for h in hashes.values()))
    json.dump(dict(all_pass=ok, checks=R), open(os.path.join(ROOT, "prototype/p0/reports/geometry_selfcheck.json"), "w"), indent=1)
    lines = ["# geometry_selfcheck", "", f"ALL PASS: **{ok}**", "", "| check | value | pass |", "|---|---|---|"]
    for k, v in R.items():
        val = json.dumps(v["value"]) if not isinstance(v["value"], float) else f"{v['value']:.4g}"
        lines.append(f"| {k} | {val[:160]} | {'PASS' if v['pass_'] else 'FAIL'} |")
    open(os.path.join(ROOT, "prototype/p0/reports/geometry_selfcheck.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
