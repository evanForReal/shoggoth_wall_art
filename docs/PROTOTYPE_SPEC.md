# PROTOTYPE_SPEC.md — P0 structural prototype (interface contract)

**Owner:** Orchestrator. Changes via orchestrator only; regional managers may propose.
**Status:** [PROVISIONAL] until a manager confirms in the edit log.

## Goal

Produce **P0**: a printable, structurally verified prototype of ONE plant-shelf tentacle span plus its wall anchor and a body-root stub. P0 is the template the final 3-span sculpture is built from. Aesthetic detail is a swappable skin over a fixed structural underlay; P0 proves the underlay + pipeline, not final looks.

Exit criteria for P0:
1. Parametric generator (one command) emits all P0 artifacts from `prototype/p0/params.json`.
2. FEA + analytic check pass all load cases at the safety factors below.
3. Printability report passes: manifold, wall/feature minimums, overhang, bed fit, segment joints.
4. Independent reviewer (not the author) signs the report.
5. Skin swap test: changing the aesthetic skin module does not change structural-underlay results beyond tolerance (see Layering).

## Units / frame

mm, N, MPa, kg. Right-handed. **+X** = out from wall (protrusion), **+Y** = along wall horizontally (span direction), **+Z** = up. Wall plane is X=0, wall face normal +X. Gravity −Z. Origin = center of the anchor plate on the wall face.

## P0 geometry (initial parameters, all in `params.json`, all tunable)

| Param | Default | Note |
|-------|---------|------|
| `span_length` | 450 | root to tip, along centerline |
| `root_diameter` | 100 | where it meets body stub |
| `tip_diameter` | 40 | |
| `centerline` | gentle S-curve, rises ≤ 60 mm, protrudes 300 mm in X | spec'd as control points; must keep a **flat shelf zone** |
| `shelf_zone` | centered at 65–95 % of span, flat top ≥ 120×120 mm, slope ≤ 2° | plant sits here; **no geometry above shelf plane within 400 mm vertical** |
| `shell_wall` | 2.4 mm (6 perimeters @0.4) | hollow, ribbed |
| `anchor_plate` | 160×110×8 mm, 4× Ø6 holes, 120×70 mm pattern | screw/cleat to wall; cleat alternative evaluated |
| `body_stub` | 200 mm dia hemisphere-ish boss, depth 80 | stands in for body; load-transfer path from span to plate |
| `material` | PETG primary, PLA alt | see allowables |
| `layer_dir` | printed with span axis horizontal within each segment unless segmenter says otherwise | strength anisotropy matters |

## Load cases (all must pass)

| ID | Case | Magnitude |
|----|------|-----------|
| LC1 | Plant on shelf (vertical) | 5 kg at shelf-zone center (49 N) + self weight |
| LC2 | Plant overload / bump | 3× LC1 plant mass as quasi-static equivalent (safety is handled by SF below; this is a separate stress check at 15 kg) |
| LC3 | Side/lateral nudge | 30 N horizontal (±Y and ±X) at tip |
| LC4 | Self weight only | density from material; 20 % infill-equivalent where solid |
| LC5 | Anchor pull-out | screw shear + tension from LC1 moment; wall-side assumed: 2×  M4/#8 wood screws into stud, or drywall anchor rated ≥ 25 kg each — report which |

Safety factors: **SF ≥ 3.0** on yield (layer-direction-aware allowable) for LC1/LC3; **SF ≥ 1.5** for LC2; tip deflection under LC1 **≤ 6 mm**; first natural frequency ≥ 8 Hz.

Material allowables (conservative, FDM, **use the layer-direction value for interlayer loading**):

| Material | E (MPa) | σ_allow XY | σ_allow Z (interlayer) | ρ (g/cm³) |
|----------|---------|-----------|------------------------|-----------|
| PETG | 2000 | 35 | 18 | 1.27 |
| PLA | 3200 | 45 | 20 | 1.24 |

## Layering (the swap contract)

Three meshes, always emitted together:
- `underlay` — structural: shell + ribs + spine/core + anchor plate + joints. The only thing FEA sees as load-bearing.
- `skin` — aesthetic displacement/relief layer. **Additive, ≤ 6 mm proud of `underlay` outer surface**, never removes underlay material, never touches shelf zone flat. Contributes mass only.
- `assembly` — union of both, what gets printed.

FEA runs on `underlay` plus skin as non-structural added mass. Skin swap test: any valid skin must leave underlay stress/deflection within 2 %.

## Segmentation (P0 contract with Fabrication concerns)

P0 span (450 mm) must split into ≥ 2 segments each fitting a **256×256×256 mm** bed (design target 240 mm usable). Joints are on the structural load path: report joint stress separately. Joint types to evaluate: dovetail + bolt, interlocking tongue + steel pin/threaded rod, bonded socket with through-bolt. Pick by simulation, not taste.

## File layout (artifacts and owners)

```
prototype/p0/params.json                 geometry owner: Geometry region
prototype/p0/loadcases.json              Verification region (derived from this spec)
prototype/p0/out/{underlay,skin,assembly}.stl
prototype/p0/out/segments/seg_NN.stl
prototype/p0/reports/{fea,analytic,printability}.md  + .json machine-readable
model/aesthetic/   skin generators        (Aesthetics workers)
model/structural/  underlay generators    (Structural workers)
sim/               FEA + analytic + validation cases
printcheck/        mesh/printability checkers, segmenter tests
tools/             Makefile / run scripts / requirements / schema checks
```

Toolchain (installed in this env): numpy, scipy, trimesh, manifold3d, shapely, meshio, scikit-fem, build123d. No gmsh/CalculiX. Any new dependency must be added to `tools/requirements.txt` by Infra with a one-line justification. Voxel-hex or tet FEA via scikit-fem is acceptable; **every solver must be validated against a closed-form cantilever** (tolerance 5 %) before its numbers are trusted.

## Rules

- No agent edits `review/`, `review-app/`, `aesthetics vision/`.
- Prose style per CLAUDE.md. Every file edit needs second-agent sign-off in the file's edit log; unsigned = `[PROVISIONAL]`.
- Agents do not commit; the Orchestrator commits.
- Disagreement between regions → regional managers resolve; unresolved → Orchestrator.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-15 | orchestrator | Initial creation | [PROVISIONAL] |
