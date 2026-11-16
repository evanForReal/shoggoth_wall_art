# Gate 1: SDF webbing test patch

**Status:** peer-signed via teams/cad/STATUS.md edit log (README carries no edit log) CAD Lead, 2026-11-16. Question: can procedural SDF webbing look like c01/c02? Answer in Section 5: partially.

## 1. What was built

One limb, one shelf stub, one perforated web field, flat back at z = 0 (wall datum). Units mm; +y up; +z leaves the wall.

- Web: 2D Voronoi network (anisotropic Poisson seeds, hole-spacing gradient 13 to 24 mm across the patch, flow direction field, 3D-noise warp that leans walls with height). Strands are wall-extrusions from the back plane, 2.1-3.0 mm wide (modulated along length), up to ~4.8 mm near limb and shelf root. Some cells are open holes (probability 4% to 34% along the density gradient); the rest are membrane cells (3-14 mm skin) with elongated oval perforations sized per cell. 35% of open-open edges are deleted so holes merge. A low secondary net fills part of the field. Ragged noise silhouette.
- Limb: 26 mm OD, 2.0 mm wall, hollow, open to the back, S-curve ~330 mm long, ridged surface relief (+-2.2 mm). Cut flat at the domain edge (segment seam) at the top right.
- Shelf stub: 150 x 150 mm flat top plane at y = -34.75 (4 mm plate, outline noise 0-9 mm outward), underside web hanging 14-55 mm, solid 10 mm root block at the wall. Underside web is a 2D Voronoi in the (x, z) plane.
- Material look: vertex colour (ochre, bone, rust patches, darker toward the back). Cycles CPU renders, AgX, warm area key, dim cool fill.

## 2. Validation (full-resolution mesh, 0.5 mm voxel, 58.4 M-voxel grid)

| Check | Result |
|---|---|
| Voxel size | 0.5 mm (marching cubes, scikit-image) |
| Watertight / winding | True / consistent, 1 shell (558 floating specks, 602 mm3 total, removed) |
| manifold3d import | `Error.NoError`; volume 476.7 cm3 |
| Bounding box | X -110.25..110.25, Y -100.25..100.25, Z 0..162.0 mm (220.5 x 200.5 x 162.0) |
| Triangles | 2,687,838 full (over the 2.5 M/segment budget; a real segment would be smaller); 379,694 decimated |
| Mass, solid PETG (material not yet confirmed by Fabrication) 1.27 g/cm3 | 605 g upper bound (solid plate and root block; real print less) |
| Back plane | z = 0.0 to 0.6 on back-face vertices; flat by construction |
| Shelf top flat | ~177 cm2 up-facing at y = -34.75; vertex spread 0.10 mm (bulk +-0.0005 mm) |
| Min-strand sample | medial-ridge EDT: median 4.0 mm; P1/P5 1.0 mm (voxel floor); 11.5% of medial samples < 2.0 mm |
| 2.0 mm opening test | 97.1% of volume survives opening with a 1.0 mm radius ball; 2.9% sits in features < 2.0 mm |
| STL | `gate1_patch.stl`, binary, 19.0 MB, 379,694 tris, manifold3d round-trip, trimesh watertight, volume change -0.01% |

**Min-strand finding: FAIL as built.** Generator widths are >= 2.0 mm by construction, but the sample shows ~11% of medial points under 2 mm. Likely sources (not isolated): rounded rib tops, flare/skin transition necks, warp-gradient thinning, silhouette-cut stubs. The check is voxel-quantised (+-0.5 mm), so the figure is indicative. Fix before any print: erode-test inside the field and clamp (min-wall pass), then re-measure with a proper skeleton thickness. Hole-size rule (>= 6 mm smallest dimension) was not measured; membrane holes are designed >= 6 mm but strand-merging makes irregular voids.

Known script gap: `validate_patch.py` reported 0 shelf-top faces (normal test run after winding inversion); flatness above was computed in a one-off follow-up on `patch_clean.npz`. Fix the script before reuse.

## 3. Files

- `gen_patch.py`: field + marching cubes (`--vox 0.5 --out DIR`; ~3 min, ~6 GB RAM peak, 4 cores). All knobs are named constants at the top.
- `validate_patch.py`: cleanup, manifold3d, mass, strand/opening check, STL decimation (needs `fast-simplification`).
- `render_views.py`: bpy Cycles CPU renders (4 views, ~2.5 min each at 80 samples, 1200x900).
- `renders/1_front.png`, `2_three-quarter.png`, `3_raking-closeup.png`, `4_side-profile.png` (all < 1 MB; raking is 1100 px wide).
- `validation.json`, `gate1_patch.stl`.

Regenerate: `python3 gen_patch.py --vox 0.5 --out OUT && python3 validate_patch.py OUT/raw_mesh.npz OUT --stl && python3 render_views.py OUT/patch_clean.npz renders`. Seed `SEED = 7` is fixed; output is deterministic.

## 4. Parameter knobs that matter

`OPEN_P` (open-hole vs membrane share and its gradient; biggest look change), `HOLE_R_MIN/MAX` (cell size gradient), `FLOW_ANISO`, `HOLE_STRETCH` (elongation), `WARP_BIG` / `WARP_SMALL` (flow and lean), `EDGE_REMOVE_OO` (hole merging), `STRAND_W_MIN/MAX`, `STRAND_VAR`, `H_MIN/H_MAX` and `SKIN_T` (relief depth), `LOAD_BOOST` (thick strands near load path), `SEED`.

## 5. Self-assessment vs c01 / c02

Honest verdict: **not yet c01/c02-family; a credible start, and the method is not ruled out.**

What works:
- Asymmetric hole density and size gradient; no lattice symmetry (c03 failure avoided).
- Membrane sheets with oval perforations bounded by thicker ribs read in the direction of c02's perforated "skin".
- Limb relief and the flat-topped shelf with hanging underside read as c01's arm-into-shelf idea.
- Pipeline is deterministic, watertight, flat-backed, regenerates in minutes.

What does not:
- Overall read is root/vein branching, not calcified mat. c02 is a dense fibrous sheet with hundreds of small holes and strands of every width; this patch is sparser and the strands are too uniform and too rounded (smoothie-like), with no crisp torn edges.
- No fine secondary fibres crossing the big holes (the secondary net is too low and sparse to read).
- Shelf underside reads as stalactites/melted wax, not web.
- Colour is a flat cream/ochre; c01/c02 have strong rust-to-bone contrast and dark crevices. The shader is cheap; geometry matters more here.
- 0.5 mm voxels soften strands; 2 mm features are 4 voxels across.

## 6. What the full sculpt needs

1. A second strand vocabulary: many thin (2 mm) fibres and sheets torn between thicker ribs; a hole-size distribution with a heavy tail of 6-10 mm holes. Candidate: curvilinear-flow tubes along a traced streamline field (hand-placed curves from c01/c02) plus noise, instead of Voronoi-only.
2. Control curves traced from c01/c02 for limbs, mask and maw; mask carved by boolean (blocked on round-05 mask direction).
3. Tiled meshing (230 mm cells at 0.4 mm) and per-segment cuts with solid knuckles; seam-aware min-wall pass; the min-strand fix above.
4. Hollow, cleat-pocket shelf root and the buttress strut (not in this patch); relief depth ~60 mm mean (patch mean is ~15 mm).
5. A decimation/triangle budget per segment (< 2.5 M) and a validation script that implements the full mesh-spec Section 1.

NB: gate1_patch.stl is not committed (19 MB); regenerate deterministically with gen_patch.py (SEED=7).
