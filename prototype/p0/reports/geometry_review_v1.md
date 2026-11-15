# geometry_review_v1: independent re-review of Geometry v1 fixes (P0)

Reviewer: independent-v1-reviewer, 2026-11-15 (not the v0 author, not the v0 reviewer). No author code edited. Own scripts (scratchpad, ray_cast via manifold3d; rtree/networkx absent): `r1_comp.py`, `r1_wall.py`, `r1_vent.py`, `r1_vent2.py`, `r1_shelf.py`, `r1_sec.py`, `r1_sec2.py`. Files reviewed: `out/` (underlay sha256 22257f8f9cebb89b, assembly 646a2ca1b54ee4ed), `params.json`, `GEOMETRY_NOTES.md`.

## Verdict table

| # | Item | Result | Evidence |
|---|------|--------|----------|
| 1a | Wall >= 2.4, non-edge samples | PASS (tolerance) | 8732 outer samples (30k surface draws, inward-normal ray, first two hits). Edge-filtered (>3 mm from >35 deg dihedral): min 2.358, 0.0 % < 2.3, 0.10 % < 2.4 (7 samples, all >= 2.358) |
| 1b | Wall, tip hemispherical cap vs 2.4 | **WAIVER-NEEDED** | cap min 2.309 (3.8 % under 2.4 spec), 0.9 % of s 430-451 samples < 2.4. Chord sag of the loft. Functionally fine (5 perimeters + gap fill); formally violates "2.4 mm". Either waive to 2.3 or raise WALL_BOOST ~1.05 |
| 1c | Wall, raw incl. edges | WAIVER-NEEDED (dome rim only) | raw min 0.19 mm, 0.16 % < 2.3 (14 samples). By region: s 0-100 min 0.19 (dome bore exits, x 50-68, 8 samples 0.19-2.26 within 2 mm of rim); s 100-200 2.468; s 200-300 2.143 (vent rim at s~216, 1.1 mm from edge; filtered 2.358); s 300-450 >= 2.309 |
| 1d | Edge-wedge exclusion judgement | ACCEPT for vent rims; EXCEPTION for bore wedges | Vent rims: inward-normal thickness is ill-defined at a cylinder rim, exclusion is legitimate. Dome bore wedges (4 x d14 oblique exits through 3.0 mm dome shell): real knife-edges (<0.5 mm), unprintable, ~2 mm wide. They sit at x 50-68 on the anchor load path, are covered by plug/skin, but stress concentration is untested. Needs an explicit waiver line or a chamfer/counterbore |
| 2 | Single component, watertight, no stray | PASS | underlay, skin, assembly, seg_00..02 (+ `_print`), all 9 variants: 1 component each, watertight and winding-consistent after default merge, 0 degenerate faces, 0 duplicate faces. v0 had 6 (underlay). Note: raw STL vertices are unmerged (349788 raw vs 58270 merged); printcheck must merge (already noted in author notes) |
| 3a | 6 vents d4 open through wall | PASS | For each of 6 holes: 17 rays (axis + 2 rings r=0.9, 1.8) from chamber centre along -U: 0 blocked in underlay and in assembly (so skin and deck ribs do not block). Control: rays at r=2.1 mm hit the wall (2 hits), r=1.9 open. Wall above p0 is the opposite wall; no hit below |
| 3b | Chambers connected to outside | PASS | No enclosed void shells (component count 1 for every mesh; v0 had two sealed chambers). Vents at s=72/216/368 cover the 3 bulkhead-separated chambers. Caveat: connectivity is inferred from component count, plus one vent per chamber confirmed open; no flood-fill of the interior |
| 4 | Skin swap: underlay hash identical | PASS | Ran generate myself: bone_crust seed 1, rust_blister seed 5, default. Underlay sha256 all = 22257f8f... = `out/underlay.stl`. Skin and assembly hashes all differ (5 distinct claimed; 3 verified by me) |
| 5a | Shelf flat | PASS | 31x31 raycast over 120x120: z 83.978..84.000 (0.022 mm), slope 5e-5 deg (fit) on underlay and assembly; plane z=84 |
| 5b | Keepout 40 mm, nothing above plane | PASS | Underlay: 0 vertices above plane in T +-120 x N +-84 and in any R <= 140 of centre. Assembly: skin first rises above plane at |T| = 99.98 (T = -100 = 60 + 40 margin, ramp side only), max 5.0 mm there, 0 verts above plane within |T| < 99.9 over |N| < 84. Boundary exact to 0.02 mm. Note: only a plant footprint <= 200 mm along T clears the skin on the ramp-up side |
| 6 | Load path s=0..60 vs v0 | PASS (no regression) | Slice by planes normal to the centerline, v0 (archived) vs v1: area and second moments ratio v1/v0 = 0.97-1.03 for s=0..90 (Ivert s=0 4.80e6 -> 4.76e6; s=15 2.27e6 -> 2.21e6; s=24+ +3 % from thicker normal wall). Section is one island-connected body at s=-5..16 (cross ribs fill 1850-2800 mm2). Rails removed at s<20 had no measurable area contribution there (cross ribs already cover). Same step as v0 remains: area 1262 mm2 at s=20 -> 778 mm2 at s=24 (Ivert 1.40e6 -> 0.90e6, -36 % in 4 mm): abrupt stiffness drop where cross ribs end and rails begin; FEA to check peak stress at s~18-24 |
| 7 | Determinism | PASS | Fresh default run: all 12 non-variant files in out/ (STLs, JSONs) byte-identical to committed out/. Fresh `--variants` run: all 9 variant STLs byte-identical |
| 8 | Author `geometry_selfcheck.py` claim of 0.0 % < 2.3 | CONSISTENT | Mine (edge-filtered) 0.0 %, min 2.358 vs author 2.38; raw min differs (mine 0.19 vs author 2.30) because my sampling lands closer to bore rims. Author's "raw min 2.30" label is therefore not truly raw; it is over its own seeded samples |

## New defects / residual issues

1. N1 (minor): GEOMETRY_NOTES "raw min 2.30" can mislead: true raw min is rim-limited (0.19 mm at dome bore exits). Restate as "edge-filtered min 2.36-2.38".
2. N2 (minor): tiny rings (1-3 mm2) in the s=20.0 section near the bottom (N~1, U~-46): rail-start plane vs cross-rib end, probably coplanar leftovers; mesh is still watertight, single component. Not a functional defect; UNVERIFIED as sliver void vs island (<= 3 mm2).
3. N3: stiffness step at s=20-24 (above) is the likely FEA hotspot; no fillet at dome/tube junction (author open item (a)).
4. N4: anchor-load restatement in `analytic_geometry_prelim.md` not re-derived by me in this pass (UNVERIFIED); v0 review already established the My-only/Mx-in-shear method.
5. Unchanged from v0: bolt access / nut pockets unmodelled; print orientation is a bed-fit heuristic (UNVERIFIED overhang).

## Sign-off

Confirmed with exceptions: 1b (cap 2.31 < 2.4 needs waiver), 1d (dome bore wedges need waiver or chamfer). All other v1 fixes verified.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-15 | independent-v1-reviewer | v1 review | author:geometry-fix |
