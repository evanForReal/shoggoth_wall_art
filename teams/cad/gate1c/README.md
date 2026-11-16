# Gate 1C: hierarchy, global flow, depth layering, crevice shading, sliver closure

**Status:** [PROVISIONAL] CAD Lead, 2026-11-16. Builds on `../gate1b/`. Same patch scope, camera and lighting as Gates 1 and 1B.

## 1. What changed vs Gate 1B

| Target | Change | Knob |
|---|---|---|
| 1. Hierarchy | 4 large smooth ovals (long axes 68 / 54 / 44 / 36 mm) carve the front web; each has a smooth 2.2 mm half-width rim rib and a 16 mm membrane ring that swells toward the rim, with extra blind pores. The Voronoi tangle is infill between them | `OVALS`, `RING_W`, `RIM_H`, `RIM_W`, `OVAL_NOISE` |
| 2. Global flow | One flow field (28 deg at lower left sweeping to ~70 deg upper left, noise-modulated). It drives: Poisson seed anisotropy, membrane-hole orientation, fibre chords, and 18 streamline rib centrelines (5,075 samples, 2.2-9 mm wide, 20% gaps, lateral wander 2.5 mm) integrated across the whole patch. Primary Voronoi ribs lowered to 65% of relief so streamlines are the tallest ridges | `SL_*`, `flow_th` |
| 3. Depth layering | Inside each oval, a second perforated membrane (2.6 mm skin, holes >= 6 mm) plus a low rib net (8 mm) sits on the back plane, 9-14 mm below the oval rims; visible through the oval. Back plane stays flat | `BACK_T`, `BACK_H` |
| 4. Crevice shading | Vertex colour from depth below the local front surface (1 mm height map, max-filter, Gaussian smoothed) plus 4-hop concavity: deep and concave -> near-black brown, crests -> pale bone, subtle rust only in the mid tones. Calico blotches removed | `render_views.py` |
| 5. Beads and limb | `RIB_HF` 0.35 -> 0.12, `EDGE_WOBBLE` 0.45 -> 0.30, web relief near the limb capped lower; limb relief 2.2 -> 3.4 mm and its own cooler dark colour | `LIMB_RELIEF` |
| 6. 6 mm void rule | Projection voids with inscribed diameter < 6 mm are closed with a 2.6 mm plug on the back plane (blind pocket floor); see Section 3 | `FILL_MM`, `PLUG_T` (`minwall.py --fill`) |

Pipeline: `./run_all.sh OUT` (field ~4 min, min-wall + fill ~3 min, validate ~3 min, renders ~12 min; ~6 GB RAM). Seed fixed (7), deterministic. `gen_patch.py --set NAME=value` overrides constants.

## 2. Validation (final mesh = clamped + plugged field, 0.5 mm voxel, 58.4 M voxels)

| Check | Result |
|---|---|
| Watertight / winding | True / consistent, 1 shell (304 floating specks, 425 mm3, removed) |
| manifold3d | `Error.NoError`, volume 470.0 cm3 |
| Bounding box | 220.5 x 200.5 x 159.0 mm (X +-110.25, Y +-100.25, Z 0-159) |
| Triangles | 2,639,980 full (over the 2.5 M/segment budget); 379,398 decimated |
| Mass, solid PETG 1.27 | 597 g upper bound |
| Back plane | z = 0.0-0.6 on back-face vertices; flat by construction |
| Shelf top | ~228 cm2 up-facing at y = -34.75, vertex spread 0.058 mm |
| STL | `gate1c_patch.stl` 19.0 MB, 379,398 tris, manifold3d round trip, trimesh watertight, volume -0.05%. Gitignored |

### Min-wall (field-based, same method as Gate 1B)

| | Before clamp | After clamp + plug |
|---|---|---|
| Thin ridge components >= 25 voxels | 204 | **0** |
| Volume retained by 2.0 mm opening | 97.1% | 99.1% |
| Skeleton voxels thin (<1.75 mm), spur-biased | 17.8% | 10.8% |
| Ridge percentile P5 / P50 | 0.75 / 3.75 mm | 1.99 / 3.75 mm |

Clamp cost +18.3 cm3 (~3.9%, includes plugs). Width histogram of skeleton voxels (after): <1.5 mm 6.7k, 1.5-2 10.1k, 2-3 10.3k, 3-4 11.5k, 4-6 11.2k, 6-8 6.9k, >8 5.0k. Residual < 2 mm volume 0.9%: tips, junction shoulders, fibre ends. Overhang and bridge limits on fibres and the shelf fan were not checked.

## 3. 6 mm void rule: outcome

| | Gate 1B | Gate 1C before fill | Gate 1C final |
|---|---|---|---|
| Interior through-voids | 202 | 208 | 10 |
| Voids >= 6 mm | 17 | 10 | 10 |
| Voids < 6 mm | 185 | 198 | 0 |
| Void-area share < 6 mm | 41.9% | 72.3% | **0.0%** (target < 10%) |

Method: voids are gaps in the z-projection (not touching the grid border). 160 voids below 6 mm (17.8 cm2 projected) were each given a 2.6 mm plug on the back plane, so they become blind pockets, not through-holes. The rule is met by converting, not by opening.

Honest caveats:
- The through-void count is low (10 voids >= 6 mm, 7.2 cm2). The four ovals are NOT see-through in projection: by design (item 3) their back membrane and back net cover them. The piece is almost entirely blind relief with a handful of through-holes. If Evan expects light to pass, that is not delivered.
- Proposal to Structural/Fabrication: relax the 6 mm through-void rule for blind relief. A blind pocket with a 2.6 mm floor prints like any other relief (no through-hole cleaning, no bridging across the pocket floor since it sits on the build plate). Keep 6 mm only for features meant to be see-through. Not signed off by anyone; PROVISIONAL.
- Fibres and 2-6 mm "pores" are not subject to the rule in this reading.

## 4. Self-assessment vs c02 (blunt)

Better in one respect, still not c02 and arguably not more convincing overall.
- The shading is the big win. Near-black depths grading to pale crests gives real depth and drama; the calico is gone. This is the first render that reads as c02's tonal range, though c02's field is richer: rust-orange fields, cooler greys, and surface fibre texture.
- The hierarchy is present but reads as a mechanical diagram. Four evenly spaced elliptical rings are visible as rings, like links or lenses. In c02 the large voids are irregular bays with no rim rib: they open out of the tissue, and the membrane ring merges into them. Mine have a hard rim rib and a distinct ring.
- Flow is only half-there. The streamline ribs are the tallest, palest elements and sweep diagonally, so there is one gesture. But the Voronoi infill underneath is still locally isotropic tangle and hides the flow at normal viewing distance. Dense-flow variant (`SL_SPACING` 8) reads clearer but also more like hair.
- Depth layering works in the oval close-up (back net visible through the oval) but is barely legible in the front view.
- Fibre texture at 0.1-0.5 mm (c02's dominant surface character) is absent; rib surfaces are smooth. The limb has a sponge-like pitted surface which reads as a different material, not as c02.
- Bead knobs are reduced but not gone (still visible at strand ends in the raking view).
- The shelf plate top is a pale flat slab; the fibre fan underneath is good.
- Holes: the through-hole count fell (10), because depth layering and the plug close most holes. c02's density comes from holes you can see through to the wall plane; this is mostly the opposite.

Verdict: a coherent sculptural object with correct tonal range and some hierarchy; a reviewer will still say "not c02": too evenly dense and diagrammatic, no irregular bays, no fibre surface texture.

## 5. Files

`gen_patch.py`, `minwall.py` (measure, clamp, `--fill`), `validate_patch.py`, `render_views.py`, `run_all.sh`, `validation.json`, `minwall_before.json`, `minwall_after.json`, `gate1c_patch.stl` (gitignored), `renders/1_front.png` ... `4_side-profile.png`, `renders/5_knob-sheet.png` (c02 crop, 1B final, 1C final, two variants at 0.8 mm voxel, 0.8 mm base).

## 6. Next

1. Irregular bays: replace ellipses with noise-warped, flow-aligned blobs, no hard rim rib; let the membrane ring fade into the tangle.
2. Make flow dominant: derive the infill cell field from the streamline field (cells as stretched tiles between streamlines) and thin the isotropic Voronoi ribs.
3. Fibre-scale surface: 0.3-0.5 mm grain (finer voxel on a window, or a bpy displacement pass on the render mesh), plus remove the remaining bead knobs.
4. Limb: smooth the pitting; it is currently a different material.
5. Fabrication check: overhang/bridge histogram, support estimate for fibre fan, print-orientation study; Structural sign-off on the blind-relief void-rule relaxation.
