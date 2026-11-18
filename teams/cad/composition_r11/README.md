# composition_r11: held mask + eye patch (hero H + 4 one-change variants)

CAD worker, 2026-11-18. [PROVISIONAL] Not boarded; not committed. r08c, r09, r10 untouched. Code = r10 (`engine.py` + `add_rib` kind/sig args; `build.py`; `render_comp.py`) plus `heldmask.py` (arm / pad / mask part) and `measure_arm.py` (Structural P1-P12). Built to the Structural spec `teams/structural/analysis/mask-arm-v1.md` (S1-S10), not the placeholder (the 22 mm printed core without a rod FAILS creep; superseded).

## 1. Studies (exact differences)
H = r10 A0 (crown removed) + T1 (three smooth tentacles, 30 / 60 / 100 mm root dia) + T2 (516 mm whip) + D2 (denser: 9 strands, 12 webs) + M1 (52 teeth, 5 fangs 40-46 mm) + E2 cluster kept (8 eyes, left shoulder; does not touch the patch, no crowding seen) + the four r11 items:
1. **Held mask**: Dia 200 mm disc, carved smiley unchanged, rolled 15 deg CCW (like O3, in-plane; pitch 0), centre (-32, 248) = patch centre (8, 262) moved (-40, -14). Detached from the trunk: back 85 mm in front of the flesh peak (z 199 vs 114), 55 mm clear of the tallest eye under it. Thinner than r10 (half-thickness 17 centre / 8 rim vs 26 / 9; smile carved 11 mm deep as before). Held by one rod-cored tentacle (section 3), 6 grip fingers round the lower rim.
2. **Eye patch** behind it: swollen diseased flesh (ellipsoid r 108, +7 irregular lumps, own palette kind 10) with 12 eyes, sizes 50 / 42 / 36 / 32 / 30 / 26 / 24 / 22 / 20 / 18 / 16 / 15 mm, 5 clouded, packed to centre distance >= 0.88 (r_i + r_j) so lids crowd but globes do not fuse; bulging (globe centre 0.4-0.75 r above the socket), swollen lids (lid ring 1.25-1.7x), veins: 27 raised ridges (r 3.2 -> 2.2, dark paint, kind 9) radiating from the eyes and linking neighbours, plus bloodshot streaks painted on every globe. Eyes avoid the arm footprint. Mask displacement leaves the right-edge eyes visible from the front; the rest read from the side (renders `_side`, `_sideL`, `_prof`, `_close`).
3. **Eyes instead of suckers** on the two larger shelf tentacles: S3_LL (100 mm root) 6 eyes 15.9-24.3 mm, S2_UR (60 mm root) 7 eyes 10.4-15.3 mm, one row on the inner face, veined ridges between them. S1_UL (30 mm) plain. Suckers removed. Row stops where the arm is thinner than 28 mm or reaches the plate underside, so fewer than the 9 / 7 asked for on S3_LL. No lump larger than 50 mm anywhere.
4. E2 cluster kept as in r10.

| id | change vs H |
|---|---|
| V1 | M2 lamprey rings (4 rows, 250-ish teeth) instead of the M1 fang set |
| V2 | lamprey rings + the 5 M1 fangs rooted at inset 11 mm (inside the outer rows' pitch), ring teeth within 11 mm of a fang line deleted; the 34 + 18 M1 blades dropped (rings replace them) |
| V3 | gap 150 mm (back z 264 vs flesh 114), roll 25 deg; arm lengthened (section 3) |
| V4 | no eyes on the shelf tentacles (arms plain, no suckers); patch only |
Voxel diff vs H (measure_extra.json): V1 94 cm3 and V2 90 cm3, both confined to the maw (x -68..98, y -174..154, z 12..116); V3 2,098 cm3 confined to the head/mask zone (x -132..84, y 90..348); V4 103 cm3 (arm eyes + their veins).

## 2. Constraint report (measured, `checks.json`, `measure_extra.json`, `arm_report.json`)
- 3 shelf tops (volume-measured, mm; clear above flat patch 300 in all 5): S1_UL top 285, 158 x 182; S2_UR top 150, 194 x 182; S3_LL top -190, 188 x 158. All >= 150 x 150.
- No crown, vertical maw, no stance/two legs (H1/H5 divergence inherited), envelope hard-clipped (+-457), flat back.
- **Max z (relief): H, V1, V2, V4 = 254 mm (a shelf plate; mask front 232, finger lips 238); V3 = 296 mm (mask front, 4 mm under the 300 cap).** Mask part z range: H 160-232 (pad face to front), V3 228-296.
- Gate (`composition_gate.py`): 6/7, only `iou_vs_c01` fails, verdict_excl_iou PASS, all five. Checklist 7/13 all five (fails 4, 5, 7, 8, 10, 11; #4 is new vs r10 A0, the pale mask is again the brightest value; r10 A0 failed 5, 7, 8, 10, 11, 13).
- Validation: H front PIL verify + load OK (1200 x 900, 0.85 MB); all 25 PNGs OK, <= 1 MB.

## 3. Mask-arm geometry (H; V3 in brackets) for Structural
Frame: x right, y up, z out of the wall; gravity -y. Source: `build/H_meta.json` `held_geo`, `arm_report.json`.

| item | value |
|---|---|
| Rod (hardware) | 10 mm steel, straight; bore 10.4 mm. Axis: A (15.6, 136.8, 17.8) -> exit at trunk surface (0.0, 168.0, 92.0) -> pad face T (-17.1, 202.1, 173.2) -> rod end 44 mm beyond T. Direction (-0.191, 0.380, 0.905), 25.2 deg off the wall normal [A (7.7, 146.4, 13.3), T (-14.0, 207.6, 236.1), dir (-0.093, 0.264, 0.960), 16.2 deg] |
| Rod length / embed | 216 mm [276]; embed in root block 82 mm (measured: the 60 dia x 82 mm cylinder is 100% solid voxels); 44 mm into the mask from the pad face |
| Tentacle centreline | follows the rod axis; sheath sways <= 3.5 mm off it (P8). Exit -> pad face 89.7 mm [150.1]; exit -> tip incl. 6 mm into the pad 95.7 mm [156.1]; A -> tip 177.7 mm [238.1] (all < 250) |
| Diameters (outer) | root block 60 (A to exit); at trunk surface 69.5; mid 58.0; tip at pad face 48.8 [69.5 / 58.6 / 49.5] |
| Core / cover | solid core diameter >= 36 mm anywhere A -> pad face [28], >= 50.8 on the free span [48.8]; PETG cover over the rod >= 12.8 mm [8.8] (EDT of the voxel solid, bore filled, 2 mm voxels, +-2 mm) |
| Root block | solid cylinder 60 dia x 82 deep along the rod, vertical solid column dia 60 from A down to z 0, back plate 100 x 100 x 6 (rounded 8 mm) centred under A; exported in the arm part; in the trunk model the trunk is solid there (plate zone 100% solid at z 2-6, measured) |
| Root tendrils | 6 surface-riding root fingers (r 11 -> 4.5) round the exit, visual only |
| Mask end | separate part. Pad 70 dia, 38 mm deep along the axis (face to a plane 4 mm inside the disc back), fillet smin k 28 (est. radius 17 mm); arm-tip spigot dia 40 x 30 deep with a D-flat at 16 mm from the axis (key), socket in the pad; blind rod bore 44 mm from the pad face (about 10 mm past the disc back; about 20 mm of mask remains in front of its end at the boss). Seam land (arm tip face at the pad face) 1,785 mm2 [1,837] |
| Fingers | 6, r 9 -> 3.6 mm, 135-153 mm long, from the pad along the disc back, round the rim (wrap radius 12.5), hook ~6.6 mm over the front lip (tip centre r = R - 3, tip r 3.6; 0.6 mm over the 6 mm plate-finger rule). Printed with the mask part. No structural credit; the rod and the pad are the retention |
| Mask CoM | (-30.4, 241.7, 211.8) [(-29.3, 242.1, 276.8)]; offset from the rod axis 21.7 mm [24.9]; horizontal lever exit axis -> CoM 123.6 mm [187.1] (3D 143.9 [201.2]) |
| Print orientation | arm integral with the trunk segment (no root seam); mask prints back-down, socket open to the bed |

Mask mass (PETG 1.27 g/cm3, 2 mm walls, 15% infill; pad + fillet + fingers counted 100% solid, conservative):
- disc volume 839.0 cm3 (voxel count of the disc region of the mask part, smiley carved), disc surface area 791.5 cm2 (marching cubes of the smoothed disc volume)
- shell = area x 2 mm = 158.3 cm3; interior = 839.0 - 158.3 = 680.7 cm3; infill = 0.15 x 680.7 = 102.1 cm3
- pad + fillet + fingers solid = 163.7 cm3
- mass = 1.27 x (158.3 + 102.1 + 163.7) = 538.6 g; +5% paint/finish = **566 g** (0.566 kg, cap 0.8). V3 identical (566 g).
- Structural's 0.4 kg nominal is lower because this disc is 34 mm thick at the centre; mask part total volume 1,003 cm3 (solid), 1.005 L STL.

## 4. P1-P12 (mask-arm-v1.md s.7), H [V3 where different]; V1, V2, V4 have the same arm as H
| # | criterion | measured | result |
|---|---|---|---|
| P1 | 10 mm rod modelled as 10.4 bore, cover >= 5 (3 floor) | bore 10.4 carved A -> 44 mm into the mask; min cover 12.8 [8.8] | pass |
| P2 | embed >= 80 root / >= 40 mask | 82 / 44 | pass |
| P3 | root block solid >= 60 x 80, merged to plate >= 100 x 100 x 6 | 60 x 82, 100% solid; plate zone 100% solid | pass (model is voxel-solid; the 100% infill zone must be set in slicing) |
| P4 | pad >= 70 x 30, fillet >= 15 | 70 dia x 38; fillet k 28 -> ~17 mm (design value, not measured on the mesh) | pass |
| P5 | horizontal lever <= 250; tilt <= 25 (35 max); CoM offset <= 50 | lever 123.6 [187.1]; roll 15 deg [25] (pitch 0); rod tilt off the wall normal 25.2 [16.2]; CoM offset 21.7 [24.9] | pass |
| P6 | mask mass <= 0.8 kg | 0.566 | pass |
| P7 | core >= 22 along the rod span | >= 36 [28]; free span >= 50.8 [48.8] | pass |
| P8 | rod axis within 15 mm of the centreline, straight | max offset 3.5 | pass |
| P9 | seam: rod crosses, land >= 1,500 mm2, none within 40 mm of the root face | no root seam (arm integral); mask-end seam land 1,785 [1,837] mm2, spigot-socket 30 deep, rod crosses | pass; if Fabrication prints the arm separately, the root spigot/seam is not designed |
| P10 | arm axis in XY or rod present | axis 64.8 deg [73.8] out of the XY plane; rod present, waived | waived |
| P11 | fingers not retention; anti-rotation key | 6 fingers (visual); D-flat 16 mm on the dia-40 spigot | pass |
| P12 | arm / mask clear of wall, trunk, other limbs under 6 mm sag | mask part -> rest of piece 38.2 mm [93.8] (eyes are the nearest); arm free span (beyond 45 mm of the exit) -> trunk/patch flesh 6.3 mm [9.2]; arm min z beyond the exit 84 [88] (wall) | pass, H marginal (6.3 vs 6; the arm skims the patch swelling) |

S10: no anchor-row layout exists for the composition yet. Nearest shelf-root hard point to the arm exit (0, 168): S1_UL arm root (-105, 150), 107 mm; S2_UR root (70, 60), 129 mm. The arm root plate (centre (15.6, 137)) is a separate 100 x 100 mm pad ~107 mm from the S1_UL cleat zone: Structural decides whether it takes its own 2-screw row or shares the S1_UL row (proposal: own row at y ~ 137, screw spacing 100 mm; D/C with a shared shelf row is then the 0.5 limit).

## 5. Unintended changes and blunt notes (read before the cards)
- **Mask look is not comparable to r10.** The held mask is rendered with a darker palette (albedo 0.86 -> 0.42) because it now sits 85-150 mm closer to the lights and blew out white. The mask is thinner (34 vs 52 mm centre). Smiley and silhouette identical to r10 (same generator, rolled 15 deg).
- **The patch is mostly hidden from the front.** Mask displacement exposes only 3-4 right-edge eyes in the front view; the diseased swelling reads from the side and three-quarter. The head is taller (dome z 114 vs 98) and the head silhouette is about the same as A0. The r10 collar and upper flesh ring were removed.
- **Lid / vein quality is limited by the 2 mm voxel.** Veins are 6-4 mm wide ridges, median 2.0 mm raised (z grid steps are 2 mm, so values are 0 / 2 / 4); at least 90% of the 27 are >= 2.0, the lowest one is flush (buried in a lid mound). Eye globes' veins are paint only.
- **Roll only.** "Tilt" is the in-plane 15 deg / 25 deg like O3; the disc is parallel to the wall in the side views.
- **Arm is short and stout** (95.7 mm exit -> tip, 69 -> 49 mm dia) to satisfy cover >= 5 around a straight rod; it reads as a thick limb, not a whip. A root exit directly under the mask (0, 168) makes the rod 25 deg off the wall normal, so the pad is a tilted cylinder.
- **Resolution.** Everything is 2 mm voxels. Bore 10.4 mm is 5 voxels wide (+-2 mm); the 0.15 mm bond clearances and the exact D-flat are nominal in the STL and must be re-cut in final CAD. The STL is not repaired beyond dropping bodies < 1 cm3.
- **Floating teeth (inherited).** r10 M2 has 80 detached components > 0.1 cm3 (lamprey teeth not touching the wall at 2 mm voxels); V1 78, V2 65 (V2 fewer after the fang exclusion). H and V4: 8 > 0.1 cm3, all web / tooth fragments inherited from the A0 family (4.7, 2.2, 1.6 cm3 ...); none in the mask or arm. Fabrication must root or drop them.
- **Nearest-eye gap** 55 mm (H) / 120 mm (V3) under the mask back, so the eyes sit well clear of the mask.
- **V3 max z 296** leaves 4 mm to the cap; further tilt or gap needs a thinner mask.
- **Side views.** `_side` / `_sideL` are perspective (azimuth ~70 deg off the wall normal, like a viewer walking past). `H_prof` is orthographic from +x with the left half (x < -150) removed so the left shelf does not occlude (a render clip only; the piece is unchanged).
- **Not done:** no FEA, no bench test; arm / mask STL clearances; no pitch tilt; seam on the root not designed.

## 6. Files
`renders/study_<id>_front.png`, `_tq.png`, `_side.png`, `_mask.png` for H, V1-V4; H also `_sideL`, `_close`, `_prof`; `renders/contact_sheet.png` (r10 A0, r10 O3, H, V1-V4), `contact_sheet_side.png`. `checks.json`, `measure_extra.json`, `arm_report.json`.
`mask_arm_for_review.stl` = H arm part + mask part (two watertight bodies, bores and sockets as voids; 5.3 MB; the 10 mm rod is `build/H_rod.stl`, not in the review file). Parts: `build/H_armpart.stl` (arm sweep + root block + column + plate + spigot, 626 cm3), `build/H_maskpart.stl` (disc + pad + fingers + socket + bore, 1,005 cm3). `build/` is 750 MB and gitignored; `teams/cad/.gitignore` got `!composition_r11/mask_arm_for_review.stl` so the review STL can be tracked.
Reproduce: `./run_all.sh` (builds 5, renders ~25 min), `python3 measure_arm.py`, `python3 measure_extra.py`, `python3 run_checks.py`, `python3 make_sheets.py`.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-18 | cad-worker | Initial creation: round-11 held-mask studies, built to Structural mask-arm-v1 S1-S10 | [PROVISIONAL] |
