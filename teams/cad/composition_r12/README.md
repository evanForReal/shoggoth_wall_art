# composition_r12: round-12 concept set C1-C10 (substantial variation, all essentials kept)

CAD worker, 2026-11-19. [PROVISIONAL] Not boarded; not committed. r11 untouched. Brief: orchestrator SL-83 (ESSENTIALS + 9 variation axes), Structural `mask-arm-v1.md` s.9 (r11 passed). Code = r11 (`engine.py`, `render_comp.py`, `checks.py`) plus a general `heldmask.py` (mask frame yaw / pitch / roll, automatic root search, three grips) and `studies.py` (one `compose()` driven by the variation table). `variation_table.csv` was written before any build; it was re-written twice during the build when C5 and C7 changed (final table here; the first version had C5 lean R, C7 lean L and massive UR, see s.5).

## 1. Variation table (axis values; names in `variation_table.csv`)

Axes: 1 holder (B below / L left / R right / O over the head), 2 pose (F facing / T turned 33 deg / S tilted 32 deg / W low beside the maw / P partly lowered), 3 grip (F rim fingers / C coil / E threaded through the eye hole), 4 patch (M behind mask / T trail down the trunk / A also on the holding tentacle), 5 mouth (F fangs / L lamprey / B both / X larger maw 1.3x + fangs), 6 whip (R right curling down / L left rising / U curling under the shelf / E to the envelope edge), 7 massive limb (LL lower-left / UR upper-right / ML mid-left), 8 cascade (T long trailing / S short dense / A asymmetric), 9 lean (U / L / R, top of the trunk shifted 60 mm, ~10 deg at the head).

| id | 1 holder | 2 pose | 3 grip | 4 patch | 5 mouth | 6 whip | 7 massive | 8 cascade | 9 lean |
|---|---|---|---|---|---|---|---|---|---|
| C1 | B | F | F | M | B | L | LL | S | U |
| C2 | L | T | C | T | F | R | UR | T | R |
| C3 | R | S | E | A | L | U | ML | A | L |
| C4 | O | P | F | M | X | E | LL | T | U |
| C5 | L | W | C | A | B | U | LL | S | R |
| C6 | B | T | E | T | L | R | ML | A | R |
| C7 | R | W | F | T | X | L | UR | T | L |
| C8 | O | F | C | A | F | E | ML | S | R |
| C9 | B | S | F | A | B | R | LL | A | L |
| C10 | R | P | E | M | L | U | UR | T | R |

Coverage (count over the 10): holder B3 L2 R3 O2; pose F2 T2 S2 W2 P2; grip F4 C3 E3; patch M3 T3 A4; mouth F2 L3 B3 X2; whip R3 L2 U3 E2; massive LL4 UR2 ML4; cascade T4 S3 A3; lean U4 L2 R4 (the first table had lean U2/L3/R5 and C7 on UR; C5 and C7 were set to upright and C7 to ML because a leaning head and the UR arm made the side-W roots infeasible, see s.5). Every value appears >= 2 times; max axis values shared by any two concepts = 4 (checked by script). H (r11) = B F F M F R LL T U.

## 2. One line per concept

- **C1** (B F F M B L LL S U): Conservative: H's face-on pose but short dense cascade, a long whip rising on the left past the UL plate, lamprey rings + fangs. The closest to H; the 'safe' card.
- **C2** (L T C T F R UR T R): Left arm from the head flank coils once round the rim of a mask turned 33 deg away on its right; right shelf massive and high (top 300), the whip curls down the right edge below it; trunk leans right, eye trail down the right flank.
- **C3** (R S E A L U ML A L): Right arm threads a tentacle through the smiley's left eye hole, mask tilted 32 deg (roll 22 / pitch 24); mid-left massive shelf, whip curling under the right shelf, cascade swept right, body leaning left, eyes on the holding arm, lamprey mouth.
- **C4** (O P F M X E LL T U): Arm arches over the head to lower the mask over the maw top (patch half-revealed above it), 1.3x maw with fangs, whip down the right edge and along the bottom to the envelope, long cascade; the most dramatic read, weakest silhouette in the gate.
- **C5** (L W C A B U LL S U): Left arm holds the mask low at the left of the maw, coiled; eyes on the holding arm; both fangs and rings; short dense cascade; head left a bare dome (patch sits behind the mask on the flank).
- **C6** (B T E T L R ML A R): Held from below, mask turned 33 deg away, threaded through the eye hole, eye trail down the left flank; lamprey; mid-left massive shelf; cascade swept left; leaning right.
- **C7** (R W F T X L ML T U): Right arm holds the mask low at the right of the 1.3x maw (face on, rim fingers); eye trail down the left flank; left whip rising; mid-left massive shelf; upright.
- **C8** (O F C A F E ML S R): Arm arches over the head, mask face-on with a coil grip, eyes on the holding arm, mid-left massive shelf, whip to the envelope edge, short cascade, leaning right.
- **C9** (B S F A B R LL A L): From below, mask tilted 33 deg on rim fingers, eyes on the holding arm, fangs + rings, lower-left massive shelf, cascade swept right, leaning left. Closest to H after C1; strongest side view.
- **C10** (R P E M L U UR T R): Right arm lowers the mask half off the patch (pitch 14), threaded through the eye hole; upper-right massive shelf at 300, whip under it, lamprey, leaning right.

## 3. Constraint report (measured: `checks.json`, `measure_extra.json`, `arm_report.json`)

Shelf tops measured as before (volume, flat rectangle in mm, clear above the flat patch = 300 in all 30): all >= 150 x 150. Relief max z <= 300 in all. Gate is information only.

| id | shelf tops UL / UR / LL (top y: flat x x z) | max z | gate (verdict excl. IoU) | checklist |
|---|---|---|---|---|
| C1 | 285: 152x188 / 150: 194x182 / -190: 188x158 | 254 | 6/7 PASS | 4/13 |
| C2 | 245: 158x182 / 300: 194x182 / -190: 172x172 | 298 | 6/7 PASS | 6/13 |
| C3 | 362: 158x182 / 170: 194x182 / -50: 182x164 | 298 | 6/7 PASS | 7/13 |
| C4 | 285: 158x182 / 150: 194x182 / -190: 188x158 | 268 | 3/7 FAIL (fails torso_width_frac, limb_reach_ratio, limb_count) | 3/13 |
| C5 | 285: 158x182 / 150: 194x182 / -190: 172x172 | 254 | 6/7 PASS | 2/13 |
| C6 | 362: 158x182 / 170: 194x182 / -50: 182x164 | 298 | 6/7 PASS | 6/13 |
| C7 | 362: 158x182 / 170: 194x182 / -50: 182x164 | 254 | 6/7 PASS | 3/13 |
| C8 | 362: 158x182 / 170: 194x182 / -50: 182x164 | 254 | 5/7 FAIL (fails limb_count) | 4/13 |
| C9 | 285: 158x182 / 150: 194x182 / -190: 188x158 | 294 | 6/7 PASS | 7/13 |
| C10 | 245: 158x182 / 300: 194x182 / -190: 172x172 | 274 | 6/7 PASS | 3/13 |

## 4. Mask arm per concept (Structural spec; limits in the header row)

| id | lever to CoM (cap 250) | CoM off axis (cap 50) | tilt deg (<= 35) | mass kg (<= 0.8) | rod A->tip mm | core dia / cover over rod (>= 22 / >= 5) | min free-span clearance, > 45 mm along axis / r11 definition (mm) | rod angle off wall normal | arm part z range | pad / block / plate |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 | 123 | 21.3 | 8.0 | 0.570 | 175 | 36 / 12.8 | 18.1 / 12.2 | 27 | 0-204 | 70x38 / 100% / 100% |
| C2 | 166 | 38.1 | 33.0 | 0.533 | 227 | 28 / 8.8 | 22.0 / 10.2 | 7 | 0-266 | 70x38 / 100% / 99% |
| C3 | 147 | 32.6 | 32.6 | 0.559 | 184 | 36 / 12.8 | 29.5 / 22.0 | 3 | 0-226 | 70x38 / 100% / 99% |
| C4 | 122 | 29.6 | 16.1 | 0.583 | 178 | 51 / 20.2 | 29.2 / 21.4 | 20 | 0-224 | 70x38 / 100% / 98% |
| C5 | 159 | 21.2 | 10.0 | 0.595 | 218 | 44 / 16.8 | 15.7 / 8.2 | 38 | 0-224 | 70x38 / 100% / 100% |
| C6 | 163 | 31.7 | 33.0 | 0.507 | 221 | 28 / 8.8 | 19.8 / 13.1 | 20 | 0-250 | 70x38 / 100% / 100% |
| C7 | 126 | 25.5 | 10.0 | 0.563 | 172 | 51 / 20.2 | 23.5 / 13.1 | 22 | 0-220 | 70x38 / 100% / 100% |
| C8 | 102 | 30.2 | 8.0 | 0.596 | 145 | 51 / 20.4 | 32.1 / 24.2 | 8 | 0-198 | 70x38 / 100% / 100% |
| C9 | 153 | 9.5 | 32.6 | 0.580 | 199 | 32 / 10.8 | 19.8 / 13.4 | 26 | 0-224 | 70x38 / 100% / 100% |
| C10 | 137 | 32.1 | 16.1 | 0.567 | 185 | 28 / 8.8 | 20.4 / 12.2 | 23 | 0-214 | 70x38 / 100% / 99% |

## 5. Blunt notes (read before the cards)

**Fixed during the build (all concepts now meet the numeric spec; see s.4)**
- The first W (low beside the maw) roots were infeasible: a flank root has z ~ 70, too thin for an 82 mm embed. W masks now hang from a head-side root (boss on the mask's upper back, centre (+-112, 125), gap 100 mm) and C5, C7 were moved to upright (table lean U). Their free-span clearance first came out 0-4 mm; the root search now enforces >= 5-8 mm (C5 8.2 / 15.7, C7 13.1 / 23.5).
- Shelf stacks: the UR and ML height patterns first put the UL plate belly (which hangs ~107 mm under its top) inside the 300 mm clear zone over the LL / ML plate, and flat tops collapsed to 20 x 34 / 56 x 118 mm. UL tops are now 245 (UR pattern) and 362 (ML pattern); every flat top is >= 150 x 150 and clear 300 (s.3).
- The root search also rejects roots whose 100 x 100 x 6 plate or 34 mm-radius block would leave the trunk, so plate coverage is 98-100% (not exactly 100: a 2 mm voxel edge).

**Weak or risky**
- **C4 and C8 fail the composition gate** (C4 3/7: torso width, limb reach, limb count; C8 5/7: limb count). Information only; the gate bands were fit to c01. C4's 1.3x maw widens the trunk, C8 has the fewest limbs (short cascade + whip E replacing H5/H9).
- **C5 and C7 (mask low beside the maw) read worst in the checklist (2/13, 3/13).** The head is a bare plain dome; the eye patch sits behind the mask on the trunk flank (C5 12 eyes; C7 8 eyes + a 6-eye trail). The mask half-covers the maw edge at 100 mm hover. If Evan wants the head patch visible, W is the concept to drop.
- **Tilted masks reach z 298 (C2, C3, C6) and 294 (C9)**: 2 / 6 mm under the 300 cap. Any more tilt or gap needs a thinner mask.
- **C2 arm part spans z 0-266 mm** (rod nearly vertical, 7 deg off the wall normal): above a 256 mm build height if printed integral with its segment and upright (Structural F2). C6 250, C9/C3 224-226, rest <= 224.
- **Clearance definitions.** Min free-span clearance is given two ways: > 45 mm along the axis from the exit (the search criterion) and the r11 definition (> 45 mm Euclidean from the exit, > 20 mm along the axis, which includes the near-exit blend); every concept is >= 8.2 mm on the r11 definition and >= 15.7 mm along the axis. H (r11) was 6.3 mm.
- **Eye-hole grip (C3, C6, C10):** the left eye of the smiley is cut through the full thickness (19 x 43 mm hole); the threaded tentacle (r 8 -> 4.5 mm) rises from the pad, passes through it and lies over the left half of the face. At 2 mm voxels there is about 3 mm clearance round the tentacle in the hole; it is not proven non-touching at print resolution, and the mask + tentacle are one printed part, so the hole must be test-printed. The carved right eye and smile are as before. The rod and pad hold the mask regardless.
- **Coil grip (C2, C5, C8):** 2.5 turns round the rim over 150 deg; 526 mm of tentacle per coil. At 6-10 mm radius it is a visual grip, no structural role.
- **Lean (C2, C3, C6, C8, C9, C10):** the trunk is bent (top 60 mm to one side, ~10 deg at the head, ~7 deg at the maw), roots and maw rotated with it; the trunk ribs use the spine-following generator (r10 O1 style), so rib flow differs from A0's vertical meridians. Shelf plates stay fixed on the wall.
- **Whips:** L (C1, C7) leaves the UL arm and rises along x >= -205 to y <= 436 so nothing sits over the UL or LL plates; R (H path, y-shifted for the right shelf height); U is a spiral under the right plate (C3, C5, C10); E (C4, C8) runs down the right edge and along the bottom edge to x 120, replacing H5 and H9, so those two concepts lose a cascade strand.
- **Larger maw (C4, C7)** 195 x 400 (1.3 x 1.27); shelf arm roots shifted 28 mm outward so the maw does not eat them; C4's maw top (y 205) is covered by the lowered mask.
- **Cascade A** is swept to the side opposite the lean (S curve); S = every strand scaled 0.62 + 3 stubby strands.
- **Unchanged from r11 and still open:** voxel 2 mm (bore 10.4 mm = 5 voxels, bond clearances nominal); veins median 2.0 mm raised on a 2 mm z grid; floating tooth / web fragments (> 0.1 cm3 components: C1 66, C3 82, C5 69, C6 74, C9 61, C10 76 from the lamprey rows; C2 8, C4 6, C7 13, C8 4 from webs / tooth fragments); no FEA, no bench test; anchor-row layout not designed (each arm root plate is at its own centre, listed in `arm_report.json`, `rod_axis.A`).
- **STLs.** `build/<id>_armpart.stl` and `_maskpart.stl` are written for all ten (build/ is gitignored, 800+ MB); they were not repaired and some are not watertight as built (mask: C2, C3, C6; arm parts carry a stray 2nd body in the file), and no `mask_arm_for_review.stl` was written for r12. Ask for one for the concept Evan picks.

**Not verified:** the 9 axis differences are checked by script and by eye on 1200 x 900 renders; a pair like C1 / C9 still shares the mask-below arrangement and the lamprey rows, so verdicts will regress cleanly only on the axes that differ in an odd number of cards.

## 6. Files
`variation_table.csv`; `renders/study_C<n>_front.png`, `_tq.png`, `_side.png`, `_mask.png` for C1-C10 (1200 x 900, <= 1 MB, PIL verified; 42 PNGs incl. sheets); `renders/contact_sheet.png` (H + 10 fronts), `renders/contact_sheet_side.png`; `checks.json` (shelves, max z, gate, checklist); `measure_extra.json`; `arm_report.json` (P1-P12 values per concept, eye counts, mass calc inputs, rod axes). Reproduce: `python3 studies.py` (table), `./run_all.sh build` (builds + renders, ~60 min), `python3 measure_arm.py`, `python3 measure_extra.py`, `python3 run_checks.py`, `python3 make_sheets.py`.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-19 | cad-worker | Initial creation: round-12 concept set C1-C10 | [PROVISIONAL] |
