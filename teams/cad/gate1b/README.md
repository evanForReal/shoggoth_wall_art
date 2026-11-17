# Gate 1B: fibre vocabulary, denser web, min-wall measured and clamped

**Status:** CAD Lead, 2026-11-16. Builds on `../gate1/` (reviewer verdict: "cooked dough, not calcified fibre"; sparser than c02). Same patch scope, same camera and lighting as Gate 1 for comparability.

## 1. What changed vs Gate 1

| Target | Change | Knob |
|---|---|---|
| Second strand vocabulary | 28 flow-traced, catenary-sagged fibres (2.2-2.6 mm dia) cross voids >= 90 mm2; chords biased to the flow field, lateral wiggle, sag toward -y, low in z (4-8 mm at ends, down to 1.3 mm at mid, so they bridge close to the build plate) | `FIB_*` |
| Torn-sheet edges | Square-blended rib section (crisp, not round), HF edge noise, rough membrane hole outline, flow-aligned grain on skin, blind pores (non-through, 1.3 mm deep) | `CRISP`, `RIB_HF`, `TORN_AMP`, `GRAIN_AMP`, `PIT_*` |
| Width distribution | Heavy-tail half-width (`WIDTH_TAIL`), cap 4.5 mm half-width, load boost kept: strand widths span ~2-9 mm (hist in `minwall_after.json`) | `WIDTH_TAIL`, `W_HALF_CAP` |
| Density | Seed spacing 8.5-16 mm (was 13-24), anisotropy 1.3 (was 1.7): 280 cells vs 109 (2.6x). Gradient kept | `HOLE_R_*`, `FLOW_ANISO`, `OPEN_P` |
| Shelf underside | Voronoi stalactites removed. 36 fibres fan from the plate rim back to the wall body (2.1-6 mm, thicker at the body) plus 26 cross-links, p07-style root grip. Plate top stays flat | `SH_FIBRES`, `SH_LINKS` |
| Colour | Rust-to-bone contrast raised, darker crevices, rougher shader (render script only) | `render_views.py` |
| Measurement | Field-based skeleton + EDT + medial-ridge min-wall check, clamp pass, 6 mm void rule (`minwall.py`) | |

Pipeline: `./run_all.sh OUT` (field 3.5 min, min-wall 3 min, validate 3 min, renders ~12 min; ~6 GB RAM peak). Seed fixed (`SEED = 7`); deterministic. `gen_patch.py --set NAME=value` overrides constants; `--window X0 X1 Y0 Y1 ZMAX` evaluates a sub-window with identical seeds for resolution studies.

## 2. Validation (final mesh = clamped field, 0.5 mm voxel, 58.4 M voxels)

| Check | Result |
|---|---|
| Watertight / winding | True / consistent, 1 shell (609 floating specks, 1,072 mm3, removed) |
| manifold3d | `Error.NoError`, volume 465.8 cm3 |
| Bounding box | 220.5 x 200.5 x 159.0 mm (X +-110.25, Y +-100.25, Z 0-159; shelf tip at ~159 incl. outline noise) |
| Triangles | 2,866,566 full (over 2.5 M/segment); 378,988 decimated |
| Mass, solid PETG 1.27 | 592 g upper bound (solid plate/root; was 605 g) |
| Back plane | z = 0.0-0.6 on back-face vertices; flat by construction |
| Shelf top | ~230 cm2 up-facing at y = -34.75, vertex spread 0.044 mm |
| STL | `gate1b_patch.stl` 18.9 MB, 378,988 tris, manifold3d round trip, trimesh watertight, volume -0.08%. Gitignored. |

### Min-wall: the skeleton measurement (field, pre-meshing)

Method: `occ = F > 0`; EDT to nearest empty voxel centre; thickness estimate `t = 2*EDT - vox/2` (true value within [2*EDT - vox, 2*EDT]); thin means t < 1.75 mm (2.0 minus half-voxel slack). Three views of the same field: a curve skeleton (`skimage.skeletonize`), the medial ridge (EDT local maxima, catches sheets that the curve skeleton collapses), and a 2.0 mm ball opening.

| | Gate 1 field | Gate 1B before clamp | Gate 1B after clamp |
|---|---|---|---|
| Skeleton voxels thin (<1.75 mm) | 20.7% | 22.7% | 10.7% |
| Ridge voxels thin | 11.5% | 14.8% | 2.0% |
| Thin ridge components >= 25 voxels | 224 | 230 | **0** |
| Volume retained by 2.0 mm opening | 97.7% | 97.0% | 99.0% |

**Findings.**
1. The Gate 1 fail was real, not mesh quantisation. Resolution study on one 60 x 60 mm window (same seeds, 0.5 mm vs 0.25 mm voxel): skeleton-thin 27.9% -> 33.8%, opening-retained 95.4% -> 94.0%. Finer sampling finds more thin features, not fewer.
2. Causes (inferred from the generator, not isolated per feature): feathered membrane lips (Gate 1B lip raised to 2.0 mm), rib necks where the warp gradient thins a strand, 1.0-1.1 mm half-width floor sitting on the 2.0 mm limit with no slack, noise-bitten edges, strand-end tips.
3. The curve-skeleton percentage stays high after clamp (10.7%) because skeleton spurs run out to tips and corners where thickness tends to 0 by definition. The ridge test and the opening test are the better gates: after the clamp no thin ridge component >= 25 voxels remains and 99.0% of volume sits in features >= 2.0 mm.
4. Clamp = stamp a 1.1 mm-radius ball on every thin skeleton/ridge voxel (union with F). Cost: +18.9 cm3 (+4.1% volume). Residual < 2 mm volume 1.0%: tips, junction shoulders, fibre ends.
5. Not measured: overhang/bridge limits (fibres sit low in z by design but were not checked against the 20 mm PETG bridge rule), strand width in z.

### 6 mm through-void rule (z-projection)

Voids = gaps in the projection along z that do not touch the grid border; inscribed diameter via EDT. Ragged-silhouette notches that open to the exterior are excluded.

| | Gate 1 | Gate 1B final |
|---|---|---|
| Interior voids, total | 101 | 202 |
| Inscribed diameter < 2 mm (slivers) / 2-6 / 6-10 / 10-20 / 20-40 mm | n/a (bins differ) | 139 / 46 / 14 / 3 / 0 |
| Voids >= 6 mm | 25 | **17** |
| Voids < 6 mm (rule violations if counted as holes) | 76 | 185 (area fraction 42%) |

**Honest reading: the 6 mm rule is not met as a through-hole rule.** Most sub-6 mm voids are slivers between overlapping tilted ribs and fibre-split sub-voids. The fix is geometric (merge or close slivers < 6 mm, drop fibres that split a void below 6 mm), not done here. A fibres-off variant at 0.8 mm gives the same count of voids >= 6 mm (21 vs 21), so the fibres are not the cause; the lean of tall ribs in projection is. Sub-6 mm "pores" in the membrane are blind pits, not through-holes, on purpose.

## 3. Hole-scale statistics from c02 (by eye, then parameterised)

Crop of c02 at 3x: a few large smooth ovals (~65-130 mm at the 1.3 mm/px scale implied by a 3 ft piece), ~10 mid voids of 17-26 mm, and 50+ pores of 2-6 mm lining the oval rims and the membrane, with fibrous grain running along the flow everywhere. Gate 1B reproduces the mid voids (6-20 mm), pores as blind pits, and grain; it does not produce the large smooth ovals.

Counts: seeds (cells) 109 -> 280 (2.6x, short of the 3-5x ask). The 6 mm void floor plus ~2.5 mm strands caps cell pitch near 9-10 mm; through-void count did not rise (25 -> 17).

## 4. Self-assessment vs c02 (blunt)

Better than Gate 1, still not c02.
- It now reads as a dense coral / root-mat. Gate 1 read as sparse twigs. That is real progress and the fibre crossing, torn lips and denser pitch help.
- It is not calcified fibre. c02 is mostly continuous tissue with a hierarchy: large smooth oval voids, each ringed by perforated membrane, ringed in turn by strand grain. Mine is an even tangle of ribs of similar scale; no big voids, no nesting, no sense that holes grew in one sheet.
- Strand ends and nodes carry bead-like knobs (edge-noise artefacts), and rib surfaces are still smooth and soft. The close-up shows dough nodules, not fibre. Raking light does not rescue it.
- Flow direction is weak. c02's grain sweeps across the whole piece; mine is locally elongated cells in a mostly isotropic tangle.
- Through-void count went down, not up; the visible density is relief and pores, not holes.
- Limb is visually lost in the web (it has the same ochre and similar relief).
- Shelf plate top is a flat cream slab with big rust blotches; the fibre fan underneath is the best new element and reads as root grip.
- Colour is better (rust vs bone) but still blotchy-calico, not c02's brown-black crevices and orange-rust fields.

Verdict: method not ruled out; this is a plausible second-tier match, not Evan-board ready as "c02 family".

## 5. Files

`gen_patch.py` (field), `minwall.py` (measure, clamp, void rule), `validate_patch.py`, `render_views.py`, `run_all.sh`, `validation.json`, `minwall_before.json`, `minwall_after.json`, `gate1b_patch.stl` (gitignored), `renders/1_front.png` ... `4_side-profile.png`, `renders/5_knob-sheet.png` (c02 crop, Gate 1, Gate 1B, and three knob variants at 0.8 mm voxel: sparser cells, more open holes, fibres off).

## 6. Next

1. Hierarchy: carve a handful of large smooth oval voids (distance-to-ellipse fields aligned to the flow) and ring each with membrane + pores; derive the cell field from those instead of from uniform Poisson seeds.
2. Flow: advect rib centrelines along a global streamline field so the grain sweeps across the patch.
3. Remove bead knobs (lower `RIB_HF`, or filter noise along the strand axis); roughen rib surfaces at fibre scale (0.3-0.5 mm needs a finer voxel or a displacement pass in bpy).
4. Sliver and void clean-up to meet the 6 mm rule; overhang and bridge check on fibres.
5. Limb contrast: darker or different material and lower web relief near it.
