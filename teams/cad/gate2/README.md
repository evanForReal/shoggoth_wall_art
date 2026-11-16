# Gate 2: hybrid pipeline (SDF skeleton + bpy-hosted flow-aligned fibre-grain pass)

**Status:** [PROVISIONAL] CAD Lead, 2026-11-16. Method per DECISIONS 2026-11-16 (Evan: hybrid approved). Builds on `../gate1c/`. Same patch scope, camera, lighting and 1C shader.

## 1. Pipeline

1. `gen_patch.py` (field, 0.5 mm voxel). In-field changes vs 1C: bays carved with strongly noise-warped boundaries (`OVAL_NOISE` 1.5 -> 4.5 plus a 2.2 mm second octave) and a rim rib that breaks up where its noisy width falls below 1.15 mm; flow-dominant infill (Voronoi ribs at 45% of relief instead of 65%, 50% open-open edge deletion, streamline spacing 15 -> 10.5 mm: 27 streamlines vs 18). Flow grid exported for the sculpt pass.
2. `minwall.py --clamp --fill`: mesh + min-wall clamp + sliver plug, as in 1C.
3. `sculpt.py` (character pass, hosted in bpy): Taubin smoothing (8 iterations, volume-preserving; extra 14 on the limb; back plane and flat shelf top pinned) -> one midpoint subdivision (mean edge 0.49 -> 0.24 mm) -> outward-only displacement along vertex normals with 3-octave RIDGED noise in flow-aligned stretched coordinates (final: along-flow wavelengths 25 / 14 / 8 mm, across-flow 2.25 / 1.1 / 0.68 mm), amplitude 1.3 mm on ribs and 0.5 mm on membranes (blend by height z 6-12 mm), limb capped at 0.45 mm, scaled to zero within narrow gaps (< 1.8 mm, from a voxel closing of the clamped field) so neighbouring surfaces cannot touch. Mesh is built in bpy (`foreach_set`, `mesh.validate()` returned "no changes"), coordinates read back from bpy.
4. `validate_sculpt.py`: edge-based topology, manifold3d, re-voxelisation of the SCULPTED mesh at 0.5 mm and the same `minwall.measure` as the field check, with a pre-sculpt calibration.
5. `render_views.py`: same lighting, 1C crevice shader, 4 views.

Run: `./run_all.sh OUT` (field ~4 min, clamp ~3 min, sculpt ~1 min, validation ~10 min, renders ~25 min at 10.7 M triangles; peak ~8 GB RAM).

## 2. Feasibility notes (numbers)

- The displacement runs on the full 2.67 M-triangle mesh after one subdivision to 5.35 M vertices / 10.70 M triangles. Sculpt step: 58 s and well under 8 GB. Cycles renders of the 10.7 M mesh take ~5 min per view (64 samples, 1200 x 900).
- Resolution limit: edges are 0.24 mm, so the finest usable across-flow wavelength is ~0.7 mm (about 3 samples). The brief's 0.3 mm grain is NOT resolved; a second subdivision would be 42.8 M triangles (~4x memory, not attempted). 0.3 mm grain is also below what a 0.4 mm nozzle prints; 0.7-1.1 mm is the realistic printable grain.
- I did not use the Blender Displace/Subdivision modifier stack. The same operation is done in numpy and handed to bpy because per-vertex flow-aligned coordinates and the gap-clearance mask have no direct modifier equivalent; Blender hosts, validates and renders the mesh. Say so plainly: bpy is the host, not the sculptor.
- STL: 10.7 M triangles cannot fit a 20 MB STL (about 380 k triangles at 19 MB), so `gate2_patch.stl` is a decimated preview with the grain smoothed away. The script plus `sculpt_strong` mesh regeneration is the artifact. STL gitignored.
- Full-resolution sculpted mesh would be ~540 MB as binary STL; per-segment export (230 mm cells) would still be ~100+ MB each. Not a printing blocker (slicers cope) but a repository/review one.

## 3. Post-sculpt validation (final = `strong`: amp 1.3 / 0.5)

| Check | Result |
|---|---|
| Topology (own edge test) | 16,046,280 edges, 0 with != 2 faces, 0 repeated directed edges: closed 2-manifold, winding consistent, 0 degenerate faces |
| manifold3d | `Error.NoError`, volume 532.7 cm3, genus 456 |
| Triangles / vertices | 10,697,520 / 5,347,850 |
| Bounding box | 223.0 x 202.7 x 160.3 mm (X +-111.5, Y -101.4..101.3, Z 0..160.3); grew ~1.3 mm per side from outward displacement |
| Mass, solid PETG 1.27 | 677 g upper bound (was 597 g pre-sculpt: +13% volume, +63 cm3, from outward-only grain; surface area 3,068 cm2 vs 2,514) |
| Back plane | z = 0.0-0.6 on back-face vertices (pinned, displacement 0) |
| Shelf top | vertex spread 0.10 mm over the pinned flat |
| Displacement | mean 0.27 mm, P99 1.04 mm, max 1.30 mm (outward only) |
| Taubin | max vertex move 0.44 mm, mean 0.10 mm |
| Self-intersection | not directly measured (no robust tool at 10.7 M faces); mitigated by gap-limited displacement and passed by manifold3d topology |
| STL (preview) | 379,444 tris, 19.0 MB, trimesh watertight, volume -0.17%, grain not preserved |

### Min-wall and voids on the re-voxelised sculpted mesh

Voxelisation (surface samples -> exterior flood fill) is biased by about +-0.5 voxel: counting surface voxels as solid inflates volume (534 cm3 vs true 470 for the pre-sculpt mesh), interior-only deflates it (395 cm3). So both bounds are reported, pre vs post with the same method. Field-truth reference (1C-style min-wall of the clamped field): thin ridge components 0, 2.0 mm opening retention 99.1%.

| Variant | Pre-sculpt | Post-sculpt |
|---|---|---|
| Surface-inclusive (optimistic): thin ridge components >= 25 voxels | 1 | **0** |
| Surface-inclusive: 2.0 mm opening retention | 99.84% | 99.49% |
| Interior-only (pessimistic): thin ridge components >= 25 voxels | 135 | **85** |
| Interior-only: 2.0 mm opening retention | 96.5% | 97.0% |
| Interior-only: ridge P5 / P50 | 1.16 / 3.75 mm | 0.75 / 3.75 mm |

Reading: no net thinning. The sculpt is outward-only and the pass added material, so the thin-component count falls and opening retention stays within +-0.5 points; the pessimistic variant's absolute counts (85 components) are largely the voxelisation bias (the same method on the field-truth clamped occupancy gives 0). Conclusion: the min-wall clamp did not need re-running. The opening-retention dip in the optimistic variant (99.84 -> 99.49%) is the fine grain itself (ridge crests thinner than 2 mm by design). **If Fabrication wants the grain crests held to 2.0 mm, they must be treated as surface texture below the min-wall rule (blind relief), same reasoning as the void proposal.**

6 mm void rule on the sculpted mesh (z-projection): interior voids >= 6 mm: 7 (inclusive) / 13 (interior-only), pre-sculpt 9 / 13. Void-area share under 6 mm: 33.0% / 7.8% post, 22.2% / 10.8% pre. The plug step ran before sculpting; outward displacement narrows some gaps, so a fraction of previously-passing voids drift under 6 mm in the optimistic variant. Not re-plugged (would need a mesh-domain plug); the rule's range is 8-33% depending on voxelisation bias. The CAD proposal to relax the rule for blind relief is logged in STATUS Liaison (unsigned).

## 4. Self-assessment vs c02 (blunt)

- **Does the fibre grain finally land? Partly.** At raking distance the ribs now carry flow-aligned striations 0.7-2 mm apart that read as wood, rope or dried tendon, and the shelf fibres look like roots. That is a real gain over 1C's smooth rubber ribs. But c02's grain is *fibrous*: a dense mat of hair-fine filaments over everything, including the membrane faces, with torn frayed ends. Mine is **one octave of ridged striation**, regular in spacing, reading as grooved clay, and weak on membranes (0.5 mm cap). At normal viewing distance (front view) the grain is invisible: the gain is only in the close-up.
- 0.3 mm filaments are not resolved (mesh limit), so the finest c02 texture layer is missing, and would not print on a 0.4 mm nozzle anyway.
- Bays: no longer drawn ellipses (the front view shows no ring-like ovals), but they are also not legible as large voids any more; the noise warp and broken rim dissolved them into the tangle. The hierarchy gain from 1C is largely gone in the front view. c02's irregular large bays are still not there.
- Flow: now readable (27 streamlines, 45% infill height). The diagonal gesture is real; the pale streamline ribs against the dark infill reads as one direction. Closer to c02 than 1C, still hair-like rather than membrane-like.
- Tonal range is the 1C win, unchanged: near-black depths, pale crests.
- Limb: smoothed (pitting gone) but now bumpy-lumpy from the residual 0.45 mm grain; it reads as a thick vine, not as a different object; colour separation holds.
- Cost: +13% mass (677 g solid upper bound), bbox 223 x 203 mm, mesh unusable as a direct STL.

Verdict: hybrid is feasible and the close-up is more plausible; at viewing distance the piece still reads as a dense dark root-tangle with a bright flow, not as c02's calcified tissue. It is closer, not there. The next gains are (1) a membrane-coverage pass: continuous sheets with irregular large voids, (2) a second, finer filament octave once the mesh supports it (adaptive subdivision on the visible faces only), (3) fray at strand ends.

## 5. Files

`gen_patch.py`, `minwall.py`, `validate_patch.py`, `sculpt.py`, `validate_sculpt.py`, `render_views.py`, `run_all.sh`, `validation.json` (pre-sculpt mesh), `validation_sculpt.json` (post-sculpt, both voxelisation variants), `minwall_before/after.json` (field), `sculpt_strong/x2/main.json` (parameters and displacement stats), `gate2_patch.stl` (decimated preview, gitignored), `renders/1_front.png` ... `4_side-profile.png`, `renders/5_knob-sheet.png` (c02 grain crop, 1C final, Gate 2 final, gentle variant 0.9/0.35, strong x2 variant 1.8/0.7 with along-scale 2.4, Gate 2 raking close-up; variants rendered, not validated).
