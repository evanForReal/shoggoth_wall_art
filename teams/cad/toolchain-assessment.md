# CAD Toolchain Assessment v1

**Status:** ACTIVE enabling work (RP-1 item 3). Probed 2026-11-15 in the Claude Code cloud container. Findings are measured, not assumed.

## 0. Exec summary

1. No system 3D tools (no `blender`, no `openscad`). Everything needed installs from PyPI through the proxy in under a minute. Verified working: `trimesh`, `manifold3d`, `scipy`, `scikit-image`, `sdf`, `pymeshlab`, and `bpy` (Blender 5.3.0 as a headless Python module).
2. **Recommendation: (a) procedural/SDF code as the primary step-2 method, with (b) headless `bpy` as a secondary finishing/inspection tool.** (c) External image-to-3D is reference-only.
3. Evan needs to provide nothing blocking. One useful input: actual printer model(s) and count (bed size drives segment count; Fabrication is currently printer-agnostic).
4. Caveat: the container is ephemeral. Pins and an install script must be committed before the first real modeling pass (Section 5).

## 1. Probe results

| Tool | Present at start | After `pip install` | Smoke test |
|---|---|---|---|
| `blender` binary | no | n/a | not needed, see `bpy` |
| `openscad` binary | no | n/a (apt not tried; CSG is covered by `manifold3d`) | n/a |
| Python | 3.13 | n/a | n/a |
| `numpy` | 2.5.3 | n/a | ok |
| `trimesh` | no | 5.2.1 | ok |
| `manifold3d` | no | 3.5.5 | ok |
| `scipy` | no | 1.18.1 | ok |
| `scikit-image` | no | 0.26.0 | marching cubes ok |
| `sdf` (fogleman) | no | 0.3.8 | imports |
| `pymeshlab` | no | installed, imports | not exercised beyond import |
| `bpy` (Blender module) | no | 5.3.0 | voxel remesh 47k verts in 0.2 s; STL export ok |

Hardware: 4 cores, 15 GB RAM, no GPU. Rendering with Blender Eevee is unverified (no GPU); Cycles CPU is untested. Preview renders are an open item.

Smoke test (scratch, not committed): a 160^3 numpy SDF (torus with a gyroid perforation field) meshed by marching cubes in 0.8 s: 129k vertices, `trimesh.is_watertight == True`; imported into `manifold3d`, a boolean subtract returned `Status.NoError` with a valid volume. This is the exact pipeline the sculpt needs: field, mesh, boolean, validate.

## 2. Method options

### (a) Procedural / SDF code sculpting. RECOMMENDED primary.

- Approach: limb skeleton as splines with radius profiles, smooth-union into a body field, relief via heightfield displacement, webbing and perforation via thresholded cellular/gyroid/noise fields, mask carved as a subtractive/displacement field. Mesh with marching cubes at a resolution matched to the minimum feature (0.4 mm voxel is too fine for the full piece; use adaptive or per-segment meshing, see below).
- Pros: scriptable; every dimension is a named parameter ("knobs that we can tweak/" fits directly); auditable diff in git; hard-points, cleat flats, bearing pads, joint keep-outs are exact boolean operations, not hand sculpting; min-wall and overhang constraints can be enforced in the field (offset, erosion tests); segmentation is also code (plane/boolean cuts with `manifold3d`); deterministic regeneration after every Evan verdict.
- Cons: organic quality is bounded by how well noise and spline vocabulary reproduce the Beksiński webbing. Risk is "procedural look". Mitigation: two or three field layers (large limb mass, mid-scale ridges, fine web) plus hand-placed control curves traced from c01/c02.
- Scale cost: 0.91 m x 0.91 m x 0.12 m at 1 mm voxel = ~100M voxels, ~0.4 GB float32 per field. Feasible whole-piece at 1 mm for massing; fine detail (0.3-0.5 mm) must be meshed per segment (230 mm cell at 0.4 mm = 575^3 = 190M, tile into sub-blocks). Plan for tiled evaluation. Not a blocker on 15 GB.
- Output hygiene: marching cubes yields watertight meshes by construction, but staircasing and tiny holes in thin lattice need a smoothing + min-feature check. Validate with `trimesh` and `manifold3d` before export.

### (b) Blender headless sculpt (`bpy` 5.3.0). RECOMMENDED secondary.

- Available and working. Strong for: voxel/quad remesh, displacement from procedural textures, Boolean (exact solver), decimate, smoothing, shrinkwrap, UV-free texture-driven displacement, STL/OBJ export, and a possible render path.
- Weakness for the headless agent loop: true interactive sculpt brushes are not usable without a viewport. Scripted `bpy.ops.sculpt.*` is brittle. It adds a second geometry authority that is harder to diff than a Python field.
- Use for: post-processing the SDF mesh (remesh, displacement detail), preview renders if Cycles CPU works, and a human-opened .blend if Evan ever wants to hand-sculpt.

### (c) External generative tool + import (Meshy, Tripo, Hunyuan3D, etc.). Reference only.

- Image-to-3D from c01/c02 would give plausible shape fast, but: non-manifold or fused topology, arbitrary scale, no flat back plane, no hard-points, perforation fidelity unpredictable, license/credit dependency (aesthetics already carries a single-point Canva credit dependency per RP-1 item 6), and not reproducible after a verdict changes.
- Acceptable role: massing reference or a mood-check against the procedural result. Not the source of truth for engineering geometry. Anything imported would need full retopology and boolean re-cutting to carry the load-model features.

## 3. Recommendation

**Primary: (a) SDF/procedural, driven by a parameter file, tiled meshing, `manifold3d` for all booleans (hard-points, segmentation, joint pockets), `trimesh` for validation. Secondary: (b) `bpy` for remesh/detail/render. (c) as reference only.**

Why it fits this repo: the workflow is verdict-driven iteration (Evan swipes, agents backprop, geometry regenerates). A parametric script reruns in minutes after a verdict; a hand-sculpted mesh does not. The load model gives hard numeric constraints (150 mm flats, 150 x 150 mm shelves, wall thickness) that code enforces exactly and an audit can verify.

Honest risk: aesthetic quality of procedural webbing is unproven. First deliverable of the geometry pass should be a small test patch (one limb + one shelf + 200 mm of webbing) rendered against c01/c02 and put on a board, before committing the full piece.

## 4. What Evan needs to provide

| Item | Blocking? | Notes |
|---|---|---|
| Printer model(s), count, bed size | No, but changes segment count (Fabrication enabling-v1) | Fabrication currently printer-agnostic at 256 mm |
| Filament on hand / preferred (PETG vs ASA) | No | Material plan in enabling-v1 |
| Verdict on first geometry test patch | Yes, at that gate | Via a review board, not chat |
| Install wall dimensions / stud positions | No | Cleat spans two studs; layout can snap later |

No external-tool accounts or credits are required for (a) or (b).

## 5. Reproducibility actions (not yet done)

- Commit a pinned requirements file (the versions above) and an install script under `teams/cad/` before the geometry pass. Container state does not persist.
- Add a mesh validation script (watertight, manifold, min-wall, overhang histogram, flat-face check) implementing `mesh-spec-v1.md`. Not written yet; this document does not claim it exists.
- Open: Cycles CPU render test; `pymeshlab` function check; tiled marching-cubes memory profile at 0.4 mm.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-15 | cad-lead | Initial creation (container probe, method recommendation) | docs-reviewer (fixed: 100M voxels float32 = 0.4 GB, not 0.8 GB) |
