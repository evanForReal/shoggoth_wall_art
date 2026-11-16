# CAD Team — STATUS.md

**Status:** ACTIVE (enabling) — toolchain verified, mesh spec drafted; owns step-2 geometry (concept → 3D) per DECISIONS 2026-11-15. No geometry yet; method logged in DECISIONS (Step-2 geometry method, 2026-11-15).

## Exec Summary (newest first)

- 2026-11-16: FULL-PIECE composition package (`fullpiece/`): hero + 4 one-axis variants (smiley mask, no maw, diagonal sweep, shelf arrangement B), 914 mm piece at 2.0 mm voxel, Gate-2 vocabulary scaled, 1C shader on dark wall; hero also has raking close-up and side profile. Honors flat back, three >= 150 x 150 flat shelf tops (p 200-290), buttress under longest shelf, hard-point seat zones reserved, carved mask. NOT honored: v3 bbox 918 x 919 mm (limit 914), shelf headroom 300 mm violated by under-shelf fans, seat embed 16 mm (spec 25), mass 22 kg solid (proxy). Self-assessment: emblem-like starburst, variants too similar, mask is the focal point; not c01/c02 sprawl. [PROVISIONAL]
- 2026-11-16: GATE 2 built (`gate2/`), hybrid per DECISIONS: Gate-1C field (irregular bays, 27 flow streamlines) -> clamp -> bpy-hosted character pass (Taubin, 1 subdivision to 10.7 M tris, flow-aligned ridged displacement 0.7-2 mm grain, outward-only, gap-limited). Sculpted mesh re-validated: closed 2-manifold, manifold3d NoError, 223 x 203 x 160 mm, 677 g solid PETG upper bound (+13%), no net min-wall thinning on re-voxelisation (calibrated both ways). 0.3 mm grain not resolvable (0.24 mm mesh); STL is a decimated preview only. Verdict: grain lands in close-up only (regular striation, not fibre mat); bays dissolved into the tangle; not c02 yet. [PROVISIONAL]
- 2026-11-16: GATE 1C built (`gate1c/`): 4 large oval voids with rims and membrane rings, global streamline flow (18 ribs), recessed back membrane inside ovals, depth/concavity crevice shading, limb separated, bead knobs reduced, sliver voids plugged. Min-wall clamp: 0 thin ridge components, 99.1% volume in features >= 2 mm. Void rule: 72% -> 0% of void area under 6 mm, but by converting 160 voids to blind pockets; only 10 through-voids >= 6 mm remain (proposal logged to relax rule for blind relief). Mesh watertight, manifold3d NoError, 220 x 200 x 159 mm, 2.64 M tris, 597 g solid PETG upper bound. Verdict: strong tonal gain, hierarchy diagrammatic (ring-like ovals), flow only partial, no fibre surface texture; still not c02. [PROVISIONAL]
- 2026-11-16: GATE 1B built (`gate1b/`): fibre vocabulary (flow-traced sagged fibres, fibre-fan shelf underside), torn/crisp membrane edges, 2.6x cell density (280 vs 109), heavy-tail strand widths, stronger colour contrast. Field-based skeleton/ridge/opening min-wall check: the Gate 1 fail was REAL (persists at 0.25 mm voxel); clamp pass leaves 0 thin ridge components, 99.0% of volume in features >= 2 mm (+4.1% volume). Mesh watertight, manifold3d NoError, 220 x 200 x 159 mm, 2.87 M tris, 592 g solid PETG upper bound. 6 mm through-void rule NOT met (17 voids >= 6 mm vs 25 in Gate 1; slivers). Verdict: denser coral/root-mat, still not c02 (no large smooth voids, weak flow, bead knobs). [PROVISIONAL]
- 2026-11-16: GATE 1 test patch built (`gate1/`): limb + shelf stub + 200 x 200 mm perforated web, flat back, 0.5 mm voxels, procedural SDF. Mesh watertight, manifold3d NoError, 220 x 200 x 162 mm, 2.69 M tris, 605 g solid PETG upper bound; STL 19 MB. Verdict: not yet c01/c02-family (reads as root/vein network with perforated membranes, not dense calcified mat); method not ruled out. Min-strand sample FAILS (11% of medial samples < 2 mm). Needs Evan verdict on renders.
- 2026-11-15: Enabling pass (RP-1 item 3). Container has no blender/openscad but `pip` installs trimesh, manifold3d, scipy, scikit-image, sdf, pymeshlab, and bpy 5.3.0 (all smoke-tested). Recommend procedural/SDF code as primary step-2 method, headless bpy secondary, external image-to-3D reference-only. Mesh spec v1 drafted from load-model-v1. See `toolchain-assessment.md`, `mesh-spec-v1.md`.
- 2026-11-13: Stub created. No CAD work started.

## Current State

ACTIVE enabling work; no final geometry.

- `toolchain-assessment.md`: probe results, method comparison, recommendation (SDF/procedural primary; bpy secondary; external reference-only). Needs: Orchestrator to log method selection in DECISIONS; pinned requirements: teams/cad/requirements.txt (core pins done; minor libs unpinned)
- `mesh-spec-v1.md`: manifold gate, per-material min walls, 3 cleat hard-points (150 mm flats, bearing pads, joint keep-outs), shelf >= 150 x 150 flat, buttress limb min I and foot pad, relief depth targets (PROPOSED), joint clearance 0.25/0.15 mm per side. [PROPOSED] items need Aesthetics/Structural sign-off.
- `gate1/`: generator, validator, renderer, 4 renders, STL, validation.json, README (self-assessment). Awaiting board verdict; then second strand vocabulary (thin fibres, traced flow curves) and min-wall pass.
- `gate1b/`: fibres + denser web + min-wall measure/clamp + void rule; README has blunt c02 self-assessment and next steps (large oval voids with ringed membrane, streamline flow, sliver cleanup).
- `gate1c/`: hierarchy + flow + layering + crevice shading + sliver plug; README has blunt c02 assessment and next steps (irregular bays, streamline-derived cell field, fibre-scale surface, fab checks). Void-rule relaxation for blind relief proposed to Structural (unsigned).
- `gate2/`: hybrid SDF + bpy character pass; README has feasibility numbers, post-sculpt validation (both voxelisation bounds), blunt c02 assessment. Next: membrane-coverage pass with irregular bays, adaptive subdivision for a finer filament octave, strand-end fray.
- `fullpiece/`: gen_fullpiece.py (5 variants from one param set), render_full.py, 12 renders + variants_sheet, engineering_checks.json, README (variant notes, constraints not honored, print-res needs). Awaiting Evan's composition pick (round-05 in-house board).
- Next (superseded, done as Gate 1): first test patch (one limb + shelf + 200 mm web) from SDF code, rendered against c01/c02 for a board; round-05 mask direction (blocked on credits) is an input for the mask carving.
- Open: Evan's printer model/bed; coupon calibration of clearances; Cycles CPU render test.

## Liaison

- 2026-11-15, cad→structural: mesh-spec-v1 adopts load-model-v1 hard-point/shelf/strut requirements; requests structural sign-off on [PROPOSED] limb min I >= 6,300 mm^4, keep-out margins, shelf p set 150-300 mm (p = 100 mm case dropped: cannot hold 150 mm footprint). [PROVISIONAL]
- 2026-11-16, cad→structural: [PROVISIONAL] cad→structural: propose relaxing 6 mm through-void rule for blind relief pockets (floor on build plate prints normally); through-voids keep the rule. Awaiting structural sign-off.
- 2026-11-16, structural: CONDITIONAL — floor >= 2.0 mm, 0.5 mm fillets, no sub-6 mm pockets in seat/pad/strut/arm-root/joint-land zones; through-voids keep 6 mm (see teams/structural/analysis/rp2-strut-limb-voids.md) [PROVISIONAL]
- 2026-11-16, fabrication: CONDITIONAL — printable if mouth opens within 45 deg of print-up, no undercut, mouth >= 2.0 mm, depth <= 3x width, floor >= 2.6 mm; flank pockets <= 6 mm with arched roof (see teams/fabrication/analysis/rp2-blind-pockets.md)

## Takeaways

None yet.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-13 | docs-lead | Initial creation | docs-reviewer |
| 2026-11-15 | cad-lead | Status STUB→ACTIVE (enabling); exec summary, current state, liaison; added toolchain-assessment.md, mesh-spec-v1.md | docs-reviewer (flagged: stale pending-log and requirements lines) |
| 2026-11-16 | cad-lead | Gate 1 test patch: added gate1/ (scripts, renders, STL, README); exec line + Current State | docs-reviewer (flagged: README s.4/s.5 xref error; STL gitignored, STATUS lists it; README has no edit log) |
| 2026-11-16 | cad-lead | Gate 1B: added gate1b/ (fibres, density, min-wall measure/clamp, void rule, renders, README); exec line + Current State | docs-reviewer |
| 2026-11-16 | cad-lead | Gate 1C: added gate1c/ (ovals, streamlines, back membrane, crevice shading, sliver plug, renders, README); exec line + Current State | docs-reviewer |
| 2026-11-16 | cad-lead | Gate 2: added gate2/ (hybrid pipeline: field + bpy sculpt pass, re-validation, renders, README); exec line + Current State; liaison line (6 mm blind-pocket relaxation) | docs-reviewer |
| 2026-11-16 | cad-lead | Full-piece composition package: added fullpiece/ (generator, renderer, hero + 4 variants, engineering checks, README); exec line + Current State | docs-reviewer (flagged: README s.4 item 2 headroom intrusion counts (S2 884, S3 62,315) not in engineering_checks.json or generator; unverifiable) |
