# GEOMETRY_NOTES.md — Geometry region (P0)

Exec summary, newest first. Owner: Geometry regional manager. Units mm.

## 2026-11-15 v0.1 final for this run

**Checks:** `geometry_selfcheck.py` ALL PASS (watertight/winding after STL round-trip for underlay, skin, assembly, 3 segments;
shelf flat 0.02 mm over 120x120, slope 0.01 deg, nothing above plane z=84 over footprint+12 mm; skin max proud 6.08 mm
within 0.5 mm sampling tol; skin never removes underlay; bed fit). Matrix test: all 3 architectures x 3 joint types generate,
reload watertight, fit bed. `--skins-all` writes `out/skins/skin_<style>.stl` + `skins.json` (added mass per style) for the swap test.
Note: geometry-side "swap" check only proves the underlay is independent of skin; FEA-side 2 % test is Verification's.
**Hand calcs** (`reports/analytic_geometry_prelim.md`, shell-only, interlayer 18 MPa): worst section SF 16 (LC1), 6.0 (LC2) near
s~80-120; shelf deflection 0.8 mm; f1 ~18 Hz with 5 kg; design is stress-plausible, over-strong in the span (mass 1.5 kg underlay,
stub = 0.5 kg of it). Governing item is the ANCHOR: peak screw tension 148 N (LC1), 393 N (LC2) vs 245 N drywall-anchor rating;
120 mm screw spacing cannot land in one stud. No params change made (no FEA feedback arrived; no unjustified edits).
**Iterations:** v0 only. No VERIFICATION_NOTES.md existed when this run ended; 2 feedback-driven iterations NOT done.
Verification-side observation: printcheck initially crashed on numpy `ndarray.ptp` (numpy 2) - appears fixed since.
**Tuning knobs for next iteration:** `ribs.pitch`, `ribs.flange`, `joint.cut_stations`, `anchor_plate.*`, `body_stub.*`, `shelf.*`.
Tolerances learned: cut stations off the 3 mm loft grid (151, 302), spine_flange_h 4.0 and spine_web_t 4.0 avoid coplanar slivers.

## 2026-11-15 v0 published (generator runs end-to-end)

**Command:** `python prototype/p0/generate.py` (reads `params.json`, writes `out/`, previews to `reports/previews/`). ~15 s.
Flags: `--architecture rib_ladder|lattice|spine_beam`, `--joint dovetail_bolt|tongue_pin|socket_through_bolt`,
`--style <skin>`, `--seed N`, `--variants` (underlay-only 3x3 matrix to `out/variants/`), `--no-previews`.
Sanity: `python prototype/p0/geometry_selfcheck.py` -> `reports/geometry_selfcheck.{md,json}`.

**Artifacts (`prototype/p0/out/`):** `underlay.stl` (FEA load-bearing monolith), `skin.stl`, `assembly.stl`,
`segments/seg_NN.stl` (assembly frame), `segments/seg_NN_print.stl` (min-volume-box orientation, heuristic only),
`segments.json`, `joints.json` (bolt/pin axes, diameters, key dims), `geometry_manifest.json` (centerline samples with
T/N/U frames and outer/inner section params, shelf plane + LC1 load point, anchor holes, cut stations, masses, hashes).
All STLs watertight + winding-consistent after STL round-trip (cleanup snaps to 2 um grid; see `model/mtools.clean_mesh`).

**Geometry as built (defaults):** root (60,0,0); centerline tip x=300.8 (centerline protrusion 300 per spec); max
geometry x ~357 because the shelf pad (148 mm wide) is oblique to X. Plan heading 0->76->62 deg (S in plan), z rises 52.
Plan arc = 450; 3D arc 455. Shelf: flat 124 mm wide top, plateau s=300..420 (120 long), top plane z=84, measured
flatness 0.02 mm over 120x120 (assembly, incl. skin keepout). Section family: rounded rect (A,B,R); circle r 50->20
taper; pad A=74, B=32, R=12. Shell 2.4. Stub: half-ellipsoid 200 dia x 80 deep, wall 3.0, open back (plate + ring
flange x 0..8, cross ribs in y=0 and z=0 planes). Plate 160x110x8, 4x d6 at 120x70, bosses d20x6 (hole axis +X), 4x d14
screw-access bores through dome shell (heads/driver reach from front; plugs/skin cover). 3 segments, cuts at s=151, 302.
Bed fit (oriented extents): seg0 221x210x209, seg1 167x160x90, seg2 172x160x70 (all <=240).

**Architectures (param `architecture`):** `rib_ladder` (top/bottom rails + ring ribs @36), `lattice` (2x4 helical
struts, 160 mm turn, s<~233, + rings), `spine_beam` (center vertical web + top/bottom flanges + rings @72). All three share
shelf deck webs (n=0, +-32, rings @30) and dome cross-ribs. Solid-density underlay mass (PETG) ~1.5-1.7 kg.
**Joints (param `joint.type`):** dovetail_bolt (key slides along N, 2x M4 axial), tongue_pin (rect tongue 20 long + d6.4
center pin), socket_through_bolt (d~1.3B spigot 24 long, bonded, M5 transverse). Underlay monolith carries only the
bulkhead plug (A 8 mm, B key_len+4); keys/sockets/holes appear in segments. Clearance 0.2.

**Requests to Verification:**
1. FEA on `underlay.stl`; skin = added mass only (`geometry_manifest.json: mass.skin_g_solid` is solid density;
   actual added mass = assembly - underlay volume, ~390 cm3 because of 0.6 mm bond overlap; apply infill factor).
2. Joint stress reports separately per joint type; hardware list in `joints.json`.
3. Peak-moment section is expected at the root (s=0) / dome neck; cuts are outboard.

**Known issues (v0):** (a) nut pockets / bolt access for dovetail+tongue joints not modelled (axial bolts are inside
hollow shell; Fabrication to decide access ports). (b) skin is full density solid 0.8-6 mm; heavy (~490 cm3 raw). (c) shell
wall 2.4 on pad ramp-down is steep (~1.8 mm/mm), expect overhang flags. (d) segments in assembly frame, print
orientation is a heuristic. (e) no fillet at tube/dome junction yet. (f) reviewer sign-off pending, see edit log.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-15 | geometry-manager | v0 notes | [PROVISIONAL] (no second agent available in this run) |
| 2026-11-15 | geometry-manager | v0.1 status, checks, hand-calc summary | [PROVISIONAL] |
