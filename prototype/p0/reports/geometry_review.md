# geometry_review — independent review of Geometry region (P0)

Reviewer: independent-geometry-reviewer, 2026-11-15. Scope: model/, params.json, generate.py, geometry_selfcheck.py, analytic_geometry_prelim.py. No author code edited. Own script: scratchpad `rev.py` (trimesh + manifold ray_cast; rtree absent so trimesh ray/proximity unusable).

## Verdict table

| # | Item | Result | Evidence |
|---|------|--------|----------|
| 1a | `generate.py --no-previews` reproduces | PASS | 30 s, STL md5 identical to pre-existing out/ |
| 1b | `geometry_selfcheck.py` | PASS (rc 0, ALL PASS) | but 2 checks are weak, see Bugs |
| 2a | watertight, winding, vol>0: underlay/skin/assembly | PASS | vol 1.211e6 / 0.495e6 / 1.605e6 mm3 |
| 2b | segments watertight, vol>0 | PASS | 3 segs; sum 1.6013e6 vs assembly 1.6046e6 (0.2 % = holes+clearance) |
| 2c | bed fit <=240 in some orientation | PASS | OBB seg0 209x210x221, seg1 90x160x168, seg2 70x160x172; AABB in assembly frame also all <=240 |
| 2d | shelf flat 120x120, slope <=2 deg | PASS | own 25x25 raycast, z range 83.978..84.000 (0.022 mm), plane z=84 |
| 2e | nothing above shelf plane over footprint(+margin) | PASS | 0 verts above plane inside 124x120 footprint; max 0.0 within R=70 of centre |
| 2e' | clearance beyond the 20 mm keepout margin | NOTE | skin rises to +5.4 mm above plane starting exactly at keepout edge (t=-80 mm, ramp side). Spec silent on margin; OK if plant footprint <=160 mm along T |
| 2f | skin <=6 mm proud | PASS (by construction) | offset d<=max_proud=6.0 along normal; sampled 6.08 mm is sampling error, not a violation. Strictly UNVERIFIED to <0.1 mm |
| 2g | skin never removes underlay | PASS | vol(U-A) = -5.7 mm3 (noise from sliver bodies, ~0) |
| 2h | shell wall >=2.4 mm over underlay | **FAIL** | 1501 outer-surface rays along inward normal: s<225 min 2.39 (PASS); s 225-300 min 1.68, 37 % <2.3; s 400-450 min 0.81, 51 % <2.3; overall 12 % <2.3. Cause: wall is in-plane section offset; oblique on shelf ramps/tip cap (author known-issue c). Normal-direction thickness is what slicer sees |
| 3 | params.json vs PROTOTYPE_SPEC defaults | PASS | span 450, root 100, tip 40, shell 2.4, plate 160x110x8, 4xd6 120x70, stub 200x80, PETG, shelf 66.7-93.3 % (centre 80 %), flat 124 wide x 120 long (exactly at 120 min, zero margin along T), centerline rise 52<=60, tip x 300.8. Extras not in spec (stub wall 3.0, bosses, access bores) are fine. 3D arc 455.4 vs 450 (plan arc = 450) |
| 4 | root-section hand calc | PASS | below |
| 5 | code bugs | see list | no try/except anywhere, no abs paths, deterministic |
| 5b | determinism | PASS | two runs (default out and a scratch out) byte-identical STLs |
| 6 | anchor tension 148 N / 393 N | **FAIL (method error)** | below |

## (4) Root section
Root s=0: circle r=50, t=2.4, I = pi/4(50^4-47.6^4) = 8.77e5 mm4 (matches). Load (259,270,84), root (60,0,0), frame T=+X, N=+Y: plant-only M_N = 199*49.05 = 9.76 N.m, M_T = 270*49.05 = 13.2 N.m; Am=7481, tau = 13.2e3/(2*7481*2.4)=0.37 MPa, sigma=0.56, vm 0.85 MPa. Adding author's self-weight moment (M_N 11.6, M_T 15.5 N.m) gives sigma 0.66, tau 0.43, vm 1.00 = author 1.00 (LC1). LC2 same method gives ~2.7 = author 2.68. Agreement <1 %. Caveats: shell-only, no stress concentration at tube/dome junction (no fillet), LC3 (30 N at tip, ~9 N.m) not in prelim table, dome/plate load path (3 mm dome wall, ring flange) not covered.

## (6) Anchor screws
Author adds a term Mx*y/sum(y^2) to tension. Mx is torque about X = wall normal = in-plane torque on plate (from plant at y=270). Screws cannot resist it in axial tension; it goes into shear. Remove it:
- Tension from My only (plate 4 screws at y=+-60, z=+-35): pivot at bottom plate edge (z=-55, author's own assumption): LC1 83 N, LC2 217 N. Pivot at bottom screw row (z=-35, softer wall): LC1 112 N, LC2 293 N.
- Author 148/393 N overstated by 1.35-1.8x. Reproduced his numbers only by including the Mx term (83+65=148).
- Shear is understated: author V/4 = 17/42 N; with in-plane torque (r=69.5 mm) LC1 73 N, LC2 193 N worst screw.
- Consequence: LC2 vs 245 N drywall rating is marginal (217 PASS / 293 FAIL depending on pivot), not a clear fail. GEOMETRY_NOTES "governing item is ANCHOR ... 393 N" should be restated. Stud-spacing remark (120 mm cannot land in one stud) is correct. Also: spec LC5 says 25 kg anchors; shear 193 N per screw also needs checking.

## Bugs / weaknesses (code)
1. `geometry_selfcheck`: swap check is tautological (`underlay_bytes_equal` compares rebuilt underlay to itself); the skin-overlap bound is circular and has a dead `*0.0` term; `ratio` unused; swap uses seed 7 not params seed. Self-check has no shell-wall or manifold-slivers check, so "ALL PASS" misses the wall FAIL.
2. Underlay STL has 6 connected components: outer, 2 big sealed internal chambers (-0.56e6, -0.91e6 mm3 between bulkhead plugs; no vent/drain ports), two ~-0.2 mm3 sliver voids (1x1x46 mm at s~151 and s~302, i.e. at cut-plane/plug coplanarity), and a 6-triangle zero-volume stray at (50,2,47). Coplanar workarounds (NEG_PAD 0.6 overlap, XB=-5 then trim, cut stations must avoid the 3 mm loft grid, spine_flange_h=4.0) are fragile; slivers are the residue.
3. `mtools.clean_mesh` silently snaps to 2 um and fan-fills boundary loops <=64 verts with no count/log; `loft_mesh` silently flips winding. Repairs can mask real holes.
4. `generate.py` docstring lists `--skin-only-swap`, not implemented. `geometry_selfcheck` ignores `--params` (always repo params.json). `analytic_geometry_prelim.py` hard-codes E=2000/PETG, ignores `material`, has dead code (unused RHO, the empty `sw` loop, `vu0,cu0`); its .md edit log is regenerated on every run, discarding sign-offs.
5. Dead code `_smooth_normals` first lines (`if len(adj) < 0`) in skin.py.
6. `to_manifold` first line is a no-op; no try/except found (good); non-manifold raises (good). No absolute paths. Skin RNG seeded via SeedSequence: deterministic (verified).
7. `print_orientation` OBB rotation is bed-fit only; overhang/support unverified (UNVERIFIED).

## Recommended fixes
- Add ray-cast normal-thickness check to selfcheck; fix shell wall on ramp/tip (offset along surface normal or raise in-plane inset on oblique sections; or accept and set spec min to 1.2 mm for pad skirt).
- Recompute anchor loads with Mx in shear; report both pivot assumptions; restate LC5 verdict.
- Eliminate sliver voids (shift cut-station plugs off coplanar faces); vent sealed chambers (>=3 mm drain holes) or note.
- Replace tautological swap check with hash of underlay STL across styles.
- Log counts from clean_mesh; fix doc/flag mismatch; make analytic read E/rho from params.
