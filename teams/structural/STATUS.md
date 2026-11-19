# Structural Team — STATUS.md

**Status:** ACTIVE — engineering pass v1 delivered, peer-signed. Design case locked (DECISIONS 2026-11-15). Awaiting CAD mass model. RP-2 item 3 numbers issued 2026-11-16.

## Exec Summary (newest first)

- 2026-11-19: Mask arm round-12 spot-check (`analysis/mask-arm-v1.md` s.10, [PROVISIONAL]): C1 C3 C4 C8 PASS; C2 C6 C9 C10 CONDITIONAL (rod meets mask back 32-50 deg off normal, pad truncated: full-cylinder 100% infill modifier; C6 eye hole 16 mm from pad). Rod D/C 0.31-0.45 (limit 0.7), edge droop <= 0.55 mm, wall screw D/C <= 0.28. Eye-hole thread and coil are cosmetic. Print flags: C2 arm z 266 mm, C6 z 250 / 283 mm along rod, C9 266 mm along rod.
- 2026-11-18: Mask arm Phase 2 review of round-11 build (`analysis/mask-arm-v1.md` s.9, [PROVISIONAL]): H and V3 PASS P1-P12 (re-measured from voxels: lever 123.6 / 187.1 mm, rod D/C 0.38 / 0.46, 10-yr droop 0.2 / 0.5 mm vs 3 mm). P12 H 6.3 mm accepted (sag at that station < 0.1 mm). S10 decision: dedicated 4-screw stud row at the arm plate (153 / 199 N upper tension, D/C 0.22 / 0.28), CONDITIONAL on a stud under the plate. Conditions: rod Fy >= 300 on BOM, 100% infill zones, epoxy both interfaces. CAD findings: combined review STL not watertight, V3 part STLs inverted, V3 arm part z 270 > 256.
- 2026-11-18: Mask arm v1 SPEC issued (`analysis/mask-arm-v1.md`, Phase 1, [PROVISIONAL]). Mask 0.23-0.84 kg (design 0.8 kg), bump 40 N at edge, lever cap 250 mm. CAD placeholder 22 mm PETG core FAILS 10-yr droop (6.7 mm at 23 C, 10.8 mm at 40 C vs 3 mm). Requires 10 mm steel rod (sag 0.5 mm, D/C 0.56; 8 mm fails stress), >= 80 mm embed in solid root block, >= 40 mm into mask pad, separate bonded mask. All-PETG fallback d >= 32 mm solid, axis XY. Phase 2 review pending CAD composition_r11 build.
- 2026-11-16: RP-2 item 3 delivered (`analysis/rp2-strut-limb-voids.md`). (a) 6 mm rule for blind pockets: CONDITIONAL SIGN (floor >= 2.0 mm, exclusion zones). (b) ONE strut spec: embedded core I >= 11,000 mm^4 (24 x 3.0 tube or 22 mm solid, L_eff 500 mm, chord <= 470 mm); fullpiece v1 solid r15 FAILS creep buckling (87 N < 104 N); mesh-spec 6,300 rejected. (c) shelf arm root I >= 1.2e5 mm^4, solid core d >= 40 mm (creep sag governs). (d) 22 kg is a solid proxy; realistic ~11 kg (7-15); mount D/C 0.42-0.46 at 14-22 kg. Hand calcs, E/creep unmeasured.
- 2026-11-15: Engineering pass v1 (peer-signed): shelf moment governs (worst 295 N tension per upper anchor); stud-fastened cleat passes, nails and single toggles fail; sculpture est. 5-14 kg. See `analysis/load-model-v1.md`.
- 2026-11-14: Liaison from Aesthetics: mount design to assume multiple wall-contacting tentacle terminations, freeform spread (not a contained silhouette).
- 2026-11-13: Stub created. Functional constraints captured. No structural work started.

## Functional Constraints

- **Tentacles:** 3 load-bearing tentacles (baseline). Alt counts (2, 4, 5) must be generated for Evan review.
- **Wall mounts:** Each load-bearing tentacle requires a wall mount. Mounts must carry full cantilever load of tentacle + body fraction.
- **Structural goal:** Sturdy but light. Minimize mass; do not compromise rigidity at mount attachment points.
- **Final scale:** ~3×2–3×3 ft. Early iterations are small/exploratory.
- **Segmentation:** Model segmented into printable pieces for generic FDM printer (~256 mm bed). Joints must be structural-grade where load paths pass through them. Printer-flexibility preserved — no printer-specific features until Fabrication locks a machine.

## Current State

Engineering pass v1 delivered and peer-signed. Hand calcs, no FEA, no mesh yet. Design case locked: drywall on wood studs, drilling approved, French cleat + stud screws primary, buttress tentacle approved >=25 cm shelves, 5 kg/shelf ceiling (DECISIONS 2026-11-15).

- `analysis/load-model-v1.md`: plant-shelf cantilever (5 kg x 1.5 SF = 73.6 N, p = 10-30 cm, s = 8-12 cm), sculpture self-weight (5-14 kg, nominal ~9 kg), anchor options table with D/C verdicts, multi-anchor spread (6-10), whip stiffness, cable vs strut assist, open questions.
- `analysis/side-profile-cantilever.svg`: protrusion variance + loaded shelf free body.
- `analysis/front-anchor-map.svg`: 8-anchor map over c01 silhouette (6 shelf + 2 hold-down).
- `analysis/rp2-strut-limb-voids.md`: blind-pocket verdict + conditions, strut core spec (Euler + creep, beam-column, foot pad/fastener), shelf-arm min I, mass/mount check, assumptions table. Supersedes load-model-v1 Section 6 strut member and mesh-spec-v1 Section 5 member row.
- Open: coupon test for E and creep (all [GENERAL]); fullpiece_v2 review (mass, hard-points); Evan stud map and room temperature.
- Blocked on: CAD mass model from real mesh. (Wall-construction answer received: drywall on wood studs.)

## Liaison

*(Exchange active constraints with Aesthetics here. Both leads must sign off.)*

- 2026-11-14, aesthetics→structural: Format converging on wall-concentrated piece — flat-back relief or trophy-proud body with freeform tentacle spread across wall plane (round-01: 06/07/08 loved, 05 note). Mount design should assume multiple tentacle terminations contacting the wall, not a single contained silhouette. Signed: aesthetics-lead (orchestrator), structural-lead (docs-reviewer).
- 2026-11-14, liaison v2 (r03 verdicts + vision sketch IMG_0073): (a) trophy-plaque format dead; body is bas-to-mid relief, tentacles spread freeform with multiple wall anchors (f02+f04 loved). (b) NEW LOAD CASE: the 3 load-bearing tentacle spans are plant shelves — flat tops, protrusion clear of vertical obstruction, must carry potted-plant load (soil+water weight, est. 2-5 kg per span) plus sculpture self-weight; anchor spec (e.g. nails per sketch — recommend upgrading to screw/cleat) to be engineered. (c) Strong horizontal protrusion variance wanted across the piece. (d) Tension-cable assist acceptable aesthetically (f11 liked). Signed: aesthetics-lead (orchestrator), structural-lead (docs-reviewer/haiku).

- 2026-11-16, structural→cad: build to three numbers (calcs in `analysis/rp2-strut-limb-voids.md`). (1) Strut core: I >= 11,000 mm^4 at every section, min OD 24 mm hollow (wall >= 3.0 mm) or 22 mm solid, chord <= 470 mm (else I >= 0.0498 c^2), axis within 10 mm of tip/foot node centroids, 8 mm steel rod through any splice (core too long for the 256 mm bed); wrap uncredited. Replaces load-model 20 x 1.2, mesh-spec 26 mm / 6,300, fullpiece solid r15. (2) Shelf arm root: I >= 1.2e5 mm^4, Z >= 3,400 mm^3, solid core d >= 40 mm (or hollow equivalent, wall >= 3.0 mm), held to 0.5 p, axis in XY at print. (3) Strut foot: pad >= 75 x 60 mm at datum, stand-off <= 30 mm, two #10 x 2.5 in stud screws 40 mm apart, on a stud line or the cleat extension, never bare drywall. Also: seat embed 25 mm (v1 has 16); blind pockets < 6 mm allowed only floor >= 2.0 mm and outside seat/pad/strut/arm-root/joint-land zones; mesh-spec Section 0 buttress rule becomes "p > 250 mm or drywall-only"; report real hollowed mass (nominal ~11 kg, cap 14).

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
| 2026-11-15 | structural-lead | Engineering pass v1: load model, anchor options, diagrams | docs-reviewer |
| 2026-11-15 | structural-lead | Rev after peer review: strut statics corrected (295 to ~92 N, not ~18 N), stud-screw conversion, rounding, labels | docs-reviewer |
| 2026-11-16 | structural-lead | RP-2 item 3: added analysis/rp2-strut-limb-voids.md; exec line, Current State, Liaison to CAD (strut core, arm root, foot), blind-pocket verdict | docs-reviewer (verified: I of 22 mm solid = pi d^4/64 = 11,499 and 24x3 tube = 11,133 mm^4; Euler P_cr = pi^2 x 640 x 11,133 / 500^2 = 281 N creep (v1 r15 solid I 2,485 gives 87 N at 424 mm); I_min 0.0498 c^2 gives 11,000 at c = 470; beam-column sigma 3.3 MPa; foot D/C 0.11 + 0.08 = 0.19 with inputs stated (74 N H and V, h 30 mm, 50 mm lever, 350/530 N screw caps); arm I_req 1.24e5 mm^4; mass 22.16 kg from fullpiece/engineering_checks.json. E 1,600/640 MPa and creep factors are [GENERAL], stated as unmeasured. Body [PROVISIONAL] tags cleared: status line, exec line, analysis bullet, Liaison-to-CAD line. Note: CAD counter-sign of that liaison line is not logged) |
| 2026-11-18 | structural-lead | Added analysis/mask-arm-v1.md (Phase 1 mask-arm spec); exec line [PROVISIONAL] | |
| 2026-11-18 | structural-lead | mask-arm-v1.md s.9 Phase 2 review (round-11 build, H and V3), S10 anchor-row decision; exec line [PROVISIONAL] | |
| 2026-11-19 | structural-lead | mask-arm-v1.md s.10 round-12 spot-check; exec line [PROVISIONAL] | [PROVISIONAL] |
