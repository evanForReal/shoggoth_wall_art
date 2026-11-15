# Structural Team — STATUS.md

**Status:** ACTIVE — engineering pass v1 delivered [PROVISIONAL]; awaiting CAD mass model and Evan wall-construction answer.

## Exec Summary (newest first)

- 2026-11-15: Engineering pass v1 [PROVISIONAL]: shelf moment governs (worst 295 N tension per upper anchor); stud-fastened cleat passes, nails and single toggles fail; sculpture est. 5-14 kg. See `analysis/load-model-v1.md`.
- 2026-11-14: Liaison from Aesthetics: mount design to assume multiple wall-contacting tentacle terminations, freeform spread (not a contained silhouette).
- 2026-11-13: Stub created. Functional constraints captured. No structural work started.

## Functional Constraints

- **Tentacles:** 3 load-bearing tentacles (baseline). Alt counts (2, 4, 5) must be generated for Evan review.
- **Wall mounts:** Each load-bearing tentacle requires a wall mount. Mounts must carry full cantilever load of tentacle + body fraction.
- **Structural goal:** Sturdy but light. Minimize mass; do not compromise rigidity at mount attachment points.
- **Final scale:** ~3×2–3×3 ft. Early iterations are small/exploratory.
- **Segmentation:** Model segmented into printable pieces for generic FDM printer (~256 mm bed). Joints must be structural-grade where load paths pass through them. Printer-flexibility preserved — no printer-specific features until Fabrication locks a machine.

## Current State

Engineering pass v1 delivered [PROVISIONAL, awaiting peer sign-off]. Hand calcs, no FEA, no mesh yet.

- `analysis/load-model-v1.md`: plant-shelf cantilever (5 kg x 1.5 SF = 73.6 N, p = 10-30 cm, s = 8-12 cm), sculpture self-weight (5-14 kg, nominal ~9 kg), anchor options table with D/C verdicts, multi-anchor spread (6-10), whip stiffness, cable vs strut assist, open questions.
- `analysis/side-profile-cantilever.svg`: protrusion variance + loaded shelf free body.
- `analysis/front-anchor-map.svg`: 8-anchor map over c01 silhouette (6 shelf + 2 hold-down).
- Blocked on: CAD mass model from real mesh; Evan answer on wall construction (drywall-on-stud vs masonry).

## Liaison

*(Exchange active constraints with Aesthetics here. Both leads must sign off.)*

- 2026-11-14, aesthetics→structural: Format converging on wall-concentrated piece — flat-back relief or trophy-proud body with freeform tentacle spread across wall plane (round-01: 06/07/08 loved, 05 note). Mount design should assume multiple tentacle terminations contacting the wall, not a single contained silhouette. Signed: aesthetics-lead (orchestrator), structural-lead (docs-reviewer).
- 2026-11-14, liaison v2 (r03 verdicts + vision sketch IMG_0073): (a) trophy-plaque format dead; body is bas-to-mid relief, tentacles spread freeform with multiple wall anchors (f02+f04 loved). (b) NEW LOAD CASE: the 3 load-bearing tentacle spans are plant shelves — flat tops, protrusion clear of vertical obstruction, must carry potted-plant load (soil+water weight, est. 2-5 kg per span) plus sculpture self-weight; anchor spec (e.g. nails per sketch — recommend upgrading to screw/cleat) to be engineered. (c) Strong horizontal protrusion variance wanted across the piece. (d) Tension-cable assist acceptable aesthetically (f11 liked). Signed: aesthetics-lead (orchestrator), structural-lead (docs-reviewer/haiku).

## Takeaways

1. Shelf cantilevers dominate. Worst per-anchor tension ~295 N (p = 30 cm, s = 8 cm, load at tip, factored). Self-weight adds only 28-64 N shear per anchor over 6-10 anchors (even split; allow 2x peaking, up to ~130 N) and ~11 N overturning tension.
2. Sketch nails fail (D/C ~2.1) and single drywall toggles fail at p = 30 cm (~1.96). Screws into studs via a 450 mm+ French cleat (aluminum preferred; PETG/ASA printed OK; PLA no, creep) pass at D/C 0.3-0.7.
3. For p >= 25 cm or drywall-only walls, add an under-shelf compression strut (buttress tentacle): worst upper-anchor tension 295 N to ~92 N (~3x; 74 N strut thrust reacted at shelf-root anchors + 18 N self-weight couple), no plant-headroom conflict. Strut foot needs its own bearing pad + shear fastener (74 N horizontal into wall, 74 N vertical). A tip cable works but intrudes on headroom.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-13 | docs-lead | Initial creation | docs-reviewer |
| 2026-11-14 | docs-reviewer | Mirrored liaison constraint from aesthetics | orchestrator |
| 2026-11-14 | orchestrator | Liaison v2: plant-shelf load case, relief+spread format, depth variance | docs-reviewer (haiku) |
| 2026-11-15 | structural-lead | Engineering pass v1: load model, anchor options, diagrams | [PROVISIONAL] |
| 2026-11-15 | structural-lead | Rev after peer review: strut statics corrected (295 to ~92 N, not ~18 N), stud-screw conversion, rounding, labels | [PROVISIONAL] |
