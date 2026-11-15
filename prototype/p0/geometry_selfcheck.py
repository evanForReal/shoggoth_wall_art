#!/usr/bin/env python3
"""Geometry-side sanity checks (not FEA / not the printability report).
Writes <report-dir>/geometry_selfcheck.{json,md}; exit code 1 on any FAIL.

    python prototype/p0/geometry_selfcheck.py [--out prototype/p0/out] [--params prototype/p0/params.json]
                                              [--report-dir prototype/p0/reports] [--skip-swap] [--determinism]

Checks: watertight/winding/single-component (no sealed voids, no strays) for underlay/skin/assembly/segments; skin additive
and <= max_proud; shelf flat + clearance column; ray-cast NORMAL-direction min wall (can fail); repair/flip counters from
the generator manifest (can fail); skin swap = underlay STL hash identical across all styles (re-runs generate.py per style);
optional determinism (generate twice, hash all STLs).
"""
import argparse, glob, hashlib, json, os, subprocess, sys, tempfile
import numpy as np
import trimesh
from scipy.spatial import cKDTree
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from model.mtools import to_manifold, to_trimesh, shell_components   # noqa: E402
from model.structural.underlay import build_underlay                 # noqa: E402
from model.aesthetic.skin import STYLES                              # noqa: E402

WALL_FAIL = 2.3          # mm: normal-direction thickness below this is a failure (nominal 2.4, mesh chord tolerance)
WALL_PCT_MAX = 0.1       # % of (edge-filtered) samples allowed under WALL_FAIL
EDGE_EXCL = 3.0          # mm: ignore samples this close to a sharp edge (acute wedges are thin by construction)
REPAIR_LIMITS = dict(loft_winding_flips=0, boundary_loops_filled=2, boundary_loops_left_open=0,
                     degenerate_faces_dropped=50, vertices_merged=50)


def sha_file(fn):
    return hashlib.sha256(open(fn, "rb").read()).hexdigest()


def run_generate(params, out, style=None):
    cmd = [sys.executable, os.path.join(ROOT, "prototype/p0/generate.py"), "--params", params, "--out", out, "--no-previews"]
    if style:
        cmd += ["--style", style]
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def wall_check(under_mesh, n_samples=50000, seed=1):
    """Ray-cast normal-direction thickness. Samples the underlay surface (area weighted); from each point a segment is cast
    along the inward normal and the first exit hit with normal within ~45 deg of the ray is the local thickness
    (grazing hits at edges are skipped). Edge-proximate samples (<EDGE_EXCL mm from a >35 deg dihedral edge) are
    excluded from the pass/fail set but counted in the raw statistics."""
    import manifold3d as m3d
    mm = to_manifold(under_mesh)
    pts, fi = trimesh.sample.sample_surface(under_mesh, n_samples, seed=seed)
    nr = under_mesh.face_normals[fi]
    th = np.full(len(pts), np.nan)
    for i, (p, n) in enumerate(zip(pts, nr)):
        o = p - n * 1e-3
        for h in mm.ray_cast(tuple(o), tuple(o - n * 40.0)):
            if float(np.dot(np.asarray(h.normal), -n)) > 0.7:
                th[i] = float(np.linalg.norm(np.asarray(h.position) - o)) + 1e-3
                break
    ok = ~np.isnan(th)
    ang = under_mesh.face_adjacency_angles
    sharp = ang > np.radians(35.0)
    e = under_mesh.face_adjacency_edges[sharp]
    ev = under_mesh.vertices
    seg_pts = np.vstack([ev[e[:, 0]], ev[e[:, 1]], 0.5 * (ev[e[:, 0]] + ev[e[:, 1]])])
    d_edge = cKDTree(seg_pts).query(pts)[0]
    flt = ok & (d_edge > EDGE_EXCL)
    # shelf/ramp/tip regions reported separately via world position is Verification's job; report raw + filtered.
    bad = flt & (th < WALL_FAIL)
    worst = np.argsort(np.where(flt, th, 1e9))[:5]
    return dict(n_samples=int(n_samples), n_valid=int(ok.sum()), n_filtered=int(flt.sum()),
                raw_min_mm=float(np.nanmin(th)), raw_pct_lt_2p3=float(100 * np.mean(th[ok] < WALL_FAIL)),
                min_mm=float(th[flt].min()), p0p1_mm=float(np.percentile(th[flt], 0.1)),
                pct_lt_2p3=float(100 * bad.sum() / max(flt.sum(), 1)), pct_lt_2p4=float(100 * np.mean(th[flt] < 2.35)),
                worst_xyz_th=[[*pts[i].round(1).tolist(), round(float(th[i]), 2)] for i in worst],
                note=f"edge-excluded: dihedral>35deg within {EDGE_EXCL} mm; ribs are 2.4 nominal by design")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "prototype/p0/out"))
    ap.add_argument("--params", default=os.path.join(ROOT, "prototype/p0/params.json"))
    ap.add_argument("--report-dir", default=os.path.join(ROOT, "prototype/p0/reports"))
    ap.add_argument("--skip-swap", action="store_true")
    ap.add_argument("--determinism", action="store_true", help="generate twice into temp dirs, compare sha256 of every STL")
    ap.add_argument("--wall-samples", type=int, default=50000)
    a = ap.parse_args()
    p = json.load(open(a.params))
    man = json.load(open(os.path.join(a.out, "geometry_manifest.json")))
    segj = json.load(open(os.path.join(a.out, "segments.json")))
    R = {}
    ok = True

    def rec(k, v, passed):
        nonlocal ok
        R[k] = dict(value=v, pass_=bool(passed)); ok &= bool(passed)

    M = {n: trimesh.load(os.path.join(a.out, f"{n}.stl")) for n in ("underlay", "skin", "assembly")}
    for n, m in M.items():
        comps = shell_components(m)
        rec(f"{n}.watertight_winding_volume>0_single_component", dict(
            wt=bool(m.is_watertight), wind=bool(m.is_winding_consistent), vol=float(m.volume),
            components=[(c["faces"], round(c["volume"], 2)) for c in comps]),
            m.is_watertight and m.is_winding_consistent and m.volume > 0 and len(comps) == 1 and comps[0]["volume"] > 0)
    U = to_manifold(M["underlay"]); S = to_manifold(M["skin"]); A = to_manifold(M["assembly"])
    rem = (U - A).volume()
    rec("skin_never_removes_underlay (vol U-A mm3)", float(rem), rem < 1.0)
    # skin overlap with underlay is the bond inset only: bounded by inset * (total underlay surface area) (independent of the
    # skin generator; looser than inset*envelope-area since the underlay area includes internal surfaces)
    ov = (U ^ S).volume()
    bound = 1.05 * p["skin"]["inset"] * float(M["underlay"].area)
    rec("skin_overlap_with_underlay mm3 (<= 1.05*inset*underlay_surface_area)", dict(overlap=float(ov), bound=float(bound),
        ratio=float(ov / bound)), 0 < ov <= bound)
    # skin proud height <= max_proud: distance of skin verts from the underlay outer envelope (rebuilt from params)
    res_env = build_underlay(p, architecture=man["architecture"], joint_type=man["joint_type"])
    env = to_trimesh(res_env["envelope"])
    pts, _ = trimesh.sample.sample_surface(env, 1_500_000, seed=1)   # ~0.4 mm spacing -> +0.5 tol
    dist, _ = cKDTree(pts).query(M["skin"].vertices)
    rec("skin_max_proud_mm (skin verts to underlay envelope, +0.5 sampling tol)", float(dist.max()),
        dist.max() <= p["skin"]["max_proud"] + 0.5)
    # shelf flat 120x120
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
    # clearance: nothing above the plane over the keepout column (flat +/- margin along T, +/- 80 across N)
    mg = float(p["shelf"]["keepout_margin"])
    tmax = 60 + mg - 5.0                         # 5 mm inside the keepout edge (frame skew)
    cols = []
    for tt in np.linspace(-tmax, tmax, 41):
        for nn in np.linspace(-80, 80, 17):
            q = o + nn * N + tt * T
            hits = A.ray_cast((q[0], q[1], 800.0), (q[0], q[1], -100.0))
            cols.append(max(h.position[2] for h in hits) if hits else -1e9)
    over = float(np.max(cols) - man["shelf"]["plane_z"])
    rec(f"max_geometry_above_shelf_plane_over_T+-{tmax:.0f}xN+-80_mm (>=40 mm keepout margin: 160 mm pot clears)", over, over < 0.05 and mg >= 40)
    bb = A.bounding_box()
    rec("protrusion_x_max_mm (assembly aabb, incl skin)", float(bb[3]), True)
    rec("tip_centerline_x", man["tip_xyz"][0], abs(man["tip_xyz"][0] - 300) < 5)
    zc = [c["xyz"][2] for c in man["centerline"]]
    rec("centerline_rise_mm", float(max(zc) - min(zc)), max(zc) - min(zc) <= 60)
    rec("span_arc3d_mm (plan arc = span_length)", man["span_arc3d"], abs(man["span_arc3d"] - p["span_length"]) < 15)
    # segments
    for s in segj["segments"]:
        sm = trimesh.load(os.path.join(a.out, s["file"]))
        comps = shell_components(sm)
        rec(f"seg{s['index']}_fits_{segj['bed_usable']}mm_bed_single_component", dict(ext=s["print_extents"], components=len(comps)),
            s["fits_bed"] and s["watertight"] and len(comps) == 1)
    rec("segment_count>=2", len(segj["segments"]), len(segj["segments"]) >= 2)
    sm = [to_manifold(trimesh.load(os.path.join(a.out, s["file"]))) for s in segj["segments"]]
    import manifold3d as m3d
    uni = m3d.Manifold.batch_boolean(sm, m3d.OpType.Add)
    deficit = A.volume() - uni.volume()
    rec("segments_union_volume_deficit_mm3 (holes+clearance)", float(deficit), 0 <= deficit < 0.01 * A.volume())
    # vents
    vents = man.get("vents", [])
    rec("vent_holes (d>=3 mm, >=2 per sealed chamber, listed in manifest)", dict(n=len(vents), d=sorted({v["d"] for v in vents}),
        stations=sorted({v["s"] for v in vents})), len(vents) >= 6 and all(v["d"] >= 3.0 for v in vents))
    # wall thickness (ray-cast, normal direction)
    w = wall_check(M["underlay"], a.wall_samples)
    rec(f"min_wall_normal_dir_mm (ray-cast, underlay; fail < {WALL_FAIL}; edge-filtered)", w,
        w["min_mm"] >= WALL_FAIL and w["pct_lt_2p3"] <= WALL_PCT_MAX)
    # repair counters from generator
    rp = man.get("repairs")
    if rp is None:
        rec("repair_counters_present", None, False)
    else:
        worst = {k: 0 for k in REPAIR_LIMITS}
        for c in rp["clean_calls"]:
            for k in ("boundary_loops_filled", "boundary_loops_left_open", "degenerate_faces_dropped", "vertices_merged"):
                worst[k] = max(worst[k], c[k])
        worst["loft_winding_flips"] = rp["loft_winding_flips"]
        rec("repairs (clean_mesh per-mesh max / loft winding flips) vs limits", dict(worst=worst, limits=REPAIR_LIMITS,
            loft_calls=rp["loft_calls"]), all(worst[k] <= REPAIR_LIMITS[k] for k in REPAIR_LIMITS))
    # skin swap: underlay STL byte-hash identical across all styles (full generate.py run per style)
    if not a.skip_swap:
        with tempfile.TemporaryDirectory() as td:
            procs = {}
            for st in STYLES:
                procs[st] = (run_generate(a.params, os.path.join(td, st), st), os.path.join(td, st))
            hs, sk = {}, {}
            for st, (pr, d) in procs.items():
                err = pr.communicate()[1]
                if pr.returncode != 0:
                    hs[st] = "GENERATE FAILED: " + err.decode()[-200:]; continue
                hs[st] = sha_file(os.path.join(d, "underlay.stl")); sk[st] = sha_file(os.path.join(d, "skin.stl"))
        base = sha_file(os.path.join(a.out, "underlay.stl"))
        rec("skin_swap: underlay.stl sha256 identical across all 5 styles and equal to out/underlay.stl (skin hashes must differ)",
            dict(out_underlay=base[:16], styles={k: (v[:16] if len(v) == 64 else v) for k, v in hs.items()},
                 distinct_skins=len(set(sk.values()))),
            all(v == base for v in hs.values()) and len(set(sk.values())) == len(STYLES))
    if a.determinism:
        with tempfile.TemporaryDirectory() as td:
            ps = [run_generate(a.params, os.path.join(td, f"r{i}")) for i in range(2)]
            for pr in ps:
                pr.communicate()
            fl = sorted(os.path.relpath(f, os.path.join(td, "r0")) for f in glob.glob(os.path.join(td, "r0", "**", "*.stl"), recursive=True))
            diff = [f for f in fl if sha_file(os.path.join(td, "r0", f)) != sha_file(os.path.join(td, "r1", f))]
            rec("determinism: two generate runs, sha256 of every STL", dict(n_files=len(fl), differing=diff), len(fl) > 0 and not diff)
    os.makedirs(a.report_dir, exist_ok=True)
    json.dump(dict(all_pass=ok, params=os.path.relpath(a.params, ROOT) if a.params.startswith(ROOT) else a.params,
                   out=os.path.relpath(a.out, ROOT) if a.out.startswith(ROOT) else a.out, checks=R),
              open(os.path.join(a.report_dir, "geometry_selfcheck.json"), "w"), indent=1)
    lines = ["# geometry_selfcheck", "", f"ALL PASS: **{ok}**", "", "| check | value | pass |", "|---|---|---|"]
    for k, v in R.items():
        val = json.dumps(v["value"]) if not isinstance(v["value"], float) else f"{v['value']:.4g}"
        lines.append(f"| {k} | {val[:260]} | {'PASS' if v['pass_'] else 'FAIL'} |")
    open(os.path.join(a.report_dir, "geometry_selfcheck.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
