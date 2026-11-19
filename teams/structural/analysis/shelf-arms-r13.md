# Shelf arms, round-13 reach check (H13 and E1)

**Status:** structural-lead, 2026-11-19 [PROVISIONAL]. Hand calcs on CAD's 2 mm voxel build (`teams/cad/composition_r13/build/{H13,E1}_{meta.json,solid.npy}`, gitignored, re-run CAD `run_all.sh` first) and `gap_reach.json`. Numbers: `shelf_arms_r13.json`, script `shelf_arms_r13.py` (`python3 -I shelf_arms_r13.py`, ~15 s). No FEA, no coupon test; E, creep, allowables are [GENERAL] as in `rp2-strut-limb-voids.md` A3-A5. Voxel +-2 mm. Not boarded.

## 0. Verdict

Board line (3 sentences): **The upper-left (UL) shelf arm fails in both H13 and E1: its limb is a 30 mm tendril tapering to 20 mm (the same radii as r11 H), it would sag 65-247 mm against 7-9 mm allowed, and no straight rod fits its curve, so CAD must thicken it to a 42-49 mm solid core (or Evan drops UL as a plant shelf). The other four arms pass with conditions: H13 needs only a 100% infill limb zone on UR and nothing extra on LL, while E1's 36-38% larger root moments force a 16 mm steel rod in UR and a 100% infill zone or 16 mm rod in LL. The wall needs 2 stud screws per row per stud in both variants and a stud map either way; E1's 1206 mm width does not change the screw scheme, but it spans 3 studs (97% of stud phases, vs 25% for H13) and puts the shelf load 437-457 mm out from the cleat-bar stud.**

| Variant | Shelf | Load lever L (root to pot CG, mm) | Root M sustained / with 40 N lean (N.m) | Rim sag vs limit (mm) | Arm verdict | Condition | Wall |
|---|---|---|---|---|---|---|---|
| H13 | S1_UL | 350 | 20.1 / 34.1 | 98 (hollow) / 65 (solid) vs 7.0 | **FAIL** | limb d 30 -> 20 mm; needs >= 42 mm solid core (I >= 1.6e5), no rod fits (axis off 17 mm, cover < 3 mm) | COND |
| H13 | S2_UR | 368 | 21.9 / 36.6 | 10.4 (hollow) / 4.3 (solid) / 1.7 (16 mm rod) vs 7.35 | **CONDITIONAL** | limb zone s 0-192 mm 100% infill (0.52 kg), or 16 mm steel rod (D/C 0.31) | COND |
| H13 | S3_LL | 359 | 22.4 / 36.8 | 3.5 (hollow, 3 mm wall) vs 7.18 | **PASS** | continuous wall >= 3.0 mm in limb zone s 0-260 mm; no eye socket through it | COND |
| E1 | S1_UL | 471 | 27.4 / 46.2 | 247 (hollow) / 169 (solid) vs 9.4 | **FAIL** | limb d 30 -> 17 mm; needs >= 49 mm solid core (I >= 2.9e5); no rod fits | COND |
| E1 | S2_UR | 495 | 30.0 / 49.8 | 30.5 (hollow) / 12.9 (solid) / 4.1 (16 mm rod) vs 9.9 | **CONDITIONAL** | 16 mm steel rod mandatory (printed solid fails); 12 mm D/C 1.00 | COND |
| E1 | S3_LL | 490 | 31.1 / 50.8 | 7.5 (hollow) / 2.1 (solid) / 4.4 (16 mm rod) vs 9.8 | **CONDITIONAL** | hollow passes 23 C with margin 1.31 < 1.33 and fails at 40 C (12.0 mm): limb zone s 0-360 mm 100% infill (2.3 kg) or 16 mm rod (0.9 kg) | COND |

Wall column: COND = 1 screw per row per stud gives D/C 0.49-0.51 (H13) and 0.55-0.56 (E1) against the 0.5 limit, 2 screws per row per stud gives 0.25-0.28 (Section 6). Stud locations unknown.

**What E1 needs that H13 does not:** (1) UR: steel rod instead of a printed-solid option; (2) LL: solid zone or rod instead of a plain 3 mm-wall hollow limb; (3) rod 444 mm in the limb vs 277 mm, and solid zones 1.4-1.7x as long; (4) root block and cleat sized for 46-51 N.m (+35-38%) and 44-50 N.m in-plane (+40%); (5) a full-width stud strategy (Section 7); (6) mass: each 16 mm rod is 0.9 kg (E1) vs 0.6 kg (H13), against the 14 kg cap. Nothing new is needed on UL: it fails in both.

## 1. Method

Existing criteria reused from `rp2-strut-limb-voids.md` s.3 (shelf arm: 5 kg plant, SF 1.5 = 73.6 N factored; 49 N sustained; E_lt 640 MPa PETG at 10 yr 23 C, 400 MPa at 40 C; sustained stress 7 MPa; sag <= L/50 at the tip; I >= 1.2e5 mm^4 for p = 300 mm; no PLA in the load path; wrap not credited). Two things changed. (a) rp2 sized for p <= 300 mm; the r13 horizontal reach to the pot is 350-368 mm (H13) and 471-495 mm (E1), so I_req is recomputed per arm (uniform-section rule: 1.6-1.8e5 H13, 2.9-3.4e5 E1, vs 1.24e5). (b) rp2 had no bump allowance and no rod option for shelves; both are added (mask-arm-v1 s.1.2 and S1-S2).

Model (`shelf_arms_r13.py`): each shelf limb centreline from `meta['limbs'][..]['c','r']`, densified to 4 mm stations, a 3D polyline beam fixed at the limb root (trunk stiffness and cleat compliance not credited). Loads are vertical forces at their real xz positions: plant at the pot CG, plate self-weight lumped at the plate centroid, limb self-weight along the path. Moment at each station is the cross product of lever and force, resolved into bending (normal to the tangent) and torsion (along it). Rim sag is the unit-load integral of M.m/EI + T.t/GJ along the path to the pot CG. Printed zones use measured sections: limb zone = voxel section clipped to the nominal sweep radius (so webs and lumps earn nothing, cuts into the sweep do); plate zone = 3 mm ring of the voxel section normal to the path. Rod options: straight steel rod on the least-squares axis through the centreline from the root to the farthest station keeping 3 mm cover on the 3D EDT of the voxel solid; rod EI only inside the rod span, printed wrap not credited.

Voxel measurements used: limb radius profile r(s) from CAD meta (root 15 / 31 / 50 mm for UL / UR / LL, identical in r11 H `H_meta.json`); section area of the limb core against pi r^2 (min 1.00-1.03 for UL and UR; LL 0.84 H13, 0.93 E1: a flat cut into the LL limb around s 150-170 mm); plate volume from the contiguous solid run under the flat top (2030-2790 cm^3 solid); 3D inscribed radius along the centreline for rod cover; plate far flat-top voxel for the load lever.

## 2. Assumptions (A1-A12 in rp2; new ones below)

| ID | Assumption | Value | Status |
|---|---|---|---|
| A13 | Lean / bump at the pot, downward, service, unfactored; also 40 N horizontal normal to the arm | 40 N | judgement, same as mask-arm-v1 s.1.2; added to the 49 N sustained (89 N total), vs 73.6 N factored |
| A14 | Pot CG 50 mm inside the farthest flat-top point (bound case, pot against the rim) | 50 mm | CAD proxy pots 100-140 dia; rp2 used load at the tip, so this is 50 mm less severe |
| A15 | Printed-only options need sag <= limit / 1.33 (E_lt and creep unmeasured) | 1.33 | judgement; steel options 1.0 |
| A16 | Hollow limb credit: wall 3.0 mm, no infill credited | 3.0 mm | rp2 s.3.3 hollow floor |
| A17 | Self-weight: plate and limb solid volume x 1.27 g/cm^3 x retention 0.42 (A12 high) | 0.42 | judgement; plate 10.6-14.6 N, limb 0.6-9.4 N (JSON) |
| A18 | Rod: steel Fy >= 300, E 200 GPa, G 77 GPa, D/C <= 0.7 on yield under sustained + bump (vertical, and horizontal), bore +0.4 mm, cover 5 mm target, 3 mm floor, rod z >= 8 mm + radius (above 6 mm back plate), embed target 8 d | | mask-arm-v1 S1-S3 |
| A19 | Printed allowables: 7 MPa sustained, 22 MPa transient, along layers, von Mises with torsion | | mask-arm-v1 s.1.5 |
| A20 | Rim sag 10 yr: 640 MPa (23 C); 400 MPa (40 C) reported, not the verdict basis | | rp2 A4 |
| A21 | Wall: 2 studs at 406 mm OC, 1 upper + 1 lower stud screw per stud (n = 1) or 2 + 2 (n = 2), row spacing s 75 / 100 mm, #10 x 2.5 in: 530 N tension, 350 N shear, linear sum D/C <= 0.5, +28 N sculpture shear per near screw (14 kg cap, rp2 s.4.2); worst phase = stud at the shelf root, mid = stud 203 mm either side | | rp2 A11, mask-arm S10 |
| A22 | Plant 5 kg per shelf, one pot; all three shelves not loaded simultaneously in the arm check | | DECISIONS 2026-11-15 |

## 3. Reach and loads as built

Horizontal lever (root to pot CG) reproduces CAD's table (nominal at plate centroid: H13 271 / 288 / 290, E1 396 / 419 / 421 mm; CAD `gap_reach.json`). Bound case (A14) and loads:

| | L centroid | L bound | L far rim | z of rim (mm) | plate W (N) | limb W (N) | M root sust | M root fact | M root +lean | M +horiz lean | torsion root (lean) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H13 UL | 271 | 350 | 400 | 202 | 10.6 | 0.6 | 20.1 | 28.7 | 34.1 | 25.4 | 2.0 |
| H13 UR | 288 | 368 | 418 | 186 | 12.9 | 2.1 | 21.9 | 30.9 | 36.6 | 26.6 | -2.5 |
| H13 LL | 290 | 359 | 409 | 140 | 14.6 | 7.2 | 22.4 | 31.2 | 36.8 | 27.0 | 5.7 |
| E1 UL | 396 | 471 | 521 | 202 | 10.6 | 0.8 | 27.4 | 38.9 | 46.2 | 33.7 | -2.8 |
| E1 UR | 419 | 495 | 545 | 186 | 12.7 | 3.2 | 30.0 | 42.1 | 49.8 | 36.1 | 1.6 |
| E1 LL | 421 | 490 | 540 | 140 | 14.0 | 9.4 | 31.1 | 43.2 | 50.8 | 37.0 | 1.8 |

(mm, N, N.m; M = |bending| at the limb root, JSON `root_moment`.) Compare rp2: 23.6 N.m worst (p = 300, 73.6 N tip); H13 factored 28.7-31.2, E1 38.9-43.2, i.e. +22-32% and +65-83%. Root moment grows 35-38% from H13 to E1 for the lean case.

## 4. Arm sections and results

Limb zone = root to plate entry (CAD `entry`): s 0-216 / 192 / 260 mm (H13 UL / UR / LL), 312 / 316 / 360 mm (E1). Beyond it the plate and flare carry the load: plate-zone 3 mm ring I >= 3.5e5 mm^4 everywhere (min 3.5e5 H13 UR, 3.7e5 UL), bump stress 0.6-1.7 MPa vs 22; flat-top skin and the 5.5 mm rim are not checked (CAD gives no skin thickness).

| | d root / d at 0.5 L / d at entry (mm) | I at 0.5 L (mm^4) | I_req uniform rule (mm^4) / d solid | Spec I met? |
|---|---|---|---|---|
| H13 UL | 30 / 19 / 20 | 6.1e3 | 1.58e5 / 42 | no (26x short) |
| H13 UR | 62 / 40 / 41 | 1.30e5 | 1.78e5 / 44 | no on the uniform rule, passes on the integral (4.3 mm) |
| H13 LL | 100 / 64 / 63 | 8.4e5 | 1.77e5 / 44 | yes |
| E1 UL | 30 / 20 / 17 | 8.0e3 | 2.85e5 / 49 | no (36x short) |
| E1 UR | 62 / 40 / 34 | 1.31e5 | 3.25e5 / 51 | no |
| E1 LL | 100 / 67 / 57 | 1.0e6 | 3.37e5 / 51 | yes |

The uniform rule (rp2 s.3.3, I held to 0.5 L) is conservative where the root is fat; the verdicts below use the integral over the real r(s).

Printed options, 10-yr rim sag at 23 C against L/50 (JSON `printed`); stresses under sustained / lean:

| | hollow 3 mm | 40 C hollow | solid (100% infill limb zone) | 40 C solid | limit | stress hollow (MPa) | stress solid (MPa) |
|---|---|---|---|---|---|---|---|
| H13 UL | 98.4 | 157.5 | 65.1 | 104.1 | 7.0 | 17.5 / 30.3 | 13.4 / 23.2 |
| H13 UR | 10.4 | 16.6 | 4.3 | 6.8 | 7.35 | 3.4 / 5.8 | 1.6 / 2.7 |
| H13 LL | 3.5 | 5.6 | 1.0 | 1.6 | 7.18 | 2.0 / 3.3 | 0.6 / 0.9 |
| E1 UL | 247 | 395 | 169 | 270 | 9.4 | 25.7 / 44.4 | 21.3 / 36.8 |
| E1 UR | 30.5 | 48.8 | 12.9 | 20.6 | 9.9 | 4.9 / 8.4 | 2.6 / 4.5 |
| E1 LL | 7.5 | 12.0 | 2.1 | 3.4 | 9.8 | 1.9 / 3.1 | 0.5 / 0.9 |

Stress is fine everywhere except UL (limb d 17-30 mm); stiffness governs, as in rp2. At 40 C (sunlit wall) H13 UR solid still passes (6.8 vs 7.35); E1 UR and E1 LL hollow do not.

Steel rod options (wrap not credited; JSON `rods`). D/C = von Mises / 300 MPa, worst of factored, vertical lean, horizontal lean:

| | rod | sag (mm) vs limit | D/C | rod in limb / embed (mm) | min cover (mm) | axis off centreline (mm) | rod weight (N) | root bearing (MPa vs 8) |
|---|---|---|---|---|---|---|---|---|
| H13 UR | 12 | 5.4 vs 7.35 | 0.73 (fails 0.7) | 355 / 96 | 3.0 | 20.9 | 3.9 | 1.0 |
| H13 UR | **16** | 1.7 | **0.31** | 277 / 122 | 3.1 | 21.8 | 6.2 | 0.46 |
| E1 UR | 12 | 12.7 vs 9.9 | 1.00 (fails) | 487 / 96 | 3.2 | 16.5 | 5.1 | 1.4 |
| E1 UR | **16** | 4.1 vs 9.9 | **0.43** | 444 / 128 | 3.1 | 13.6 | 8.9 | 0.58 |
| E1 LL | 12 | 13.7 vs 9.8 | 1.01 (fails) | 458 / 96 | 3.2 | 41.1 | 4.8 | 1.4 |
| E1 LL | **16** | 4.4 vs 9.8 | **0.43** | 442 / 128 | 3.5 | 39.7 | 8.8 | 0.60 |

H13 LL: no rod above 10 mm keeps 3 mm cover on a straight axis (the sweep curves 22 mm off the best-fit line), and none is needed. UL: best-fit axis misses the centreline by 17.3 mm (H13) / 14.7 mm (E1) and the limb radius is 10-15 mm, so even a 10 mm rod has 0.4 / 1.8 mm cover against 3 mm: no straight rod fits.

### Per-shelf reading

- **UL (both) FAIL.** Not caused by airing: root radius 15 mm is unchanged from r11 H, the arm was never checked at this length (rp2 s.3 assumed a 40 mm core). Remedies, CAD to choose: (a) thicken the limb to d >= 42 mm (H13) / 49 mm (E1) solid through 0.5 L, taper after; (b) keep it thin and make UL a non-plant arm (no 5 kg load, keep-off like the whips in load-model s.5); (c) straighten the sweep and widen to d >= 22 mm along the full limb zone so a 16 mm rod fits, then re-run. Re-check required after any change.
- **UR.** H13 printed solid passes; E1 does not, only a 16 mm rod does. 12 mm passes sag but its stress D/C is 0.73 (limit 0.7) on H13 and 1.00 on E1: not accepted.
- **LL.** H13 passes as a hollow limb with a >= 3 mm continuous wall (sag 3.5 mm, 2.1x margin over the 1.33 rule). E1 hollow sag 7.5 mm is 76% of the limit (margin 1.31) and fails at 40 C; so E1 LL is conditional on a solid zone or a 16 mm rod. Rod is cheaper in mass (0.9 kg vs 2.3 kg solid zone).

### Rod conditions (apply to UR in both variants, LL in E1)

Fy >= 300 MPa cold-drawn or 8.8 smooth shank (not annealed 304, not threaded in the span), 16 mm; in the span 100% infill sheath, epoxy both interfaces; rod ends 82-114 mm short of the pot CG at the 3 mm cover floor (flare), the rest of the path is carried by the plate ring; embed 122-128 mm into a solid root block merged into the back plate (H13 UR 122 mm is 6 mm under 8 d, bearing 0.46 MPa so accepted); cover is at the 3.0 mm floor, not the 5 mm target (3.1-3.5 mm): CAD may not thin the limb anywhere along the rod; rod axis offset from the centreline is 13.6-39.7 mm (mask-arm S2 asks 15 mm), cover-checked on the voxel EDT, but the bore must be cut on the straight axis, not on the centreline. Rod 16 x ~570 mm needs a segmented print around it (the arm part is >256 mm; steel is not).

## 5. Findings for CAD (non-structural to the verdicts)

1. LL limb section is cut (core area 0.84 of the circle H13, 0.93 E1) around s 150-170 mm: a flat on the sweep. Hollow credit uses the measured core, but the rod bore and wall need to clear it.
2. Arm-eye sockets and ribs on the limb zone are in the solid and reduce wall locally: forbid any socket within 3 mm of the bore or inside the 3 mm hollow wall.
3. Plate flat top skin thickness and rim: not given, not checked.
4. Root block under each shelf: solid pad >= 100 x 100 x 6 mm at the back plate, not the 2.6 mm membrane (mask-arm s.9.5).

## 6. Wall / anchor loads

Model: one aluminum cleat bar per shelf under the root block, 2 stud screws per stud (upper and lower rows, s 75 or 100 mm), verified on the combined case sustained + 40 N lean (C_b) and factored (C_f). Out-of-plane moment M_x = sum(F z) (upper-row tension couple), in-plane moment M_z = sum(F x) resolved as stud shear/uplift on a 406 mm stud pair. Governing = C_b, stud at the shelf root, s 100:

| | V (N) | M_x / M_z (N.m) | lever x / z (mm) | T per upper screw s 75 / 100 (N) | R near / uplift (N) | D/C n = 1, s 75 / 100 | D/C n = 2, s 75 / 100 |
|---|---|---|---|---|---|---|---|
| H13 UL | 100 | 17.4 / -31.1 | 310 / 174 | 116 / 87 | 177 / 77 | 0.55 / 0.50 | 0.28 / 0.25 |
| H13 UR | 104 | 16.6 / 34.2 | 329 / 159 | 110 / 83 | 188 / 84 | 0.56 / 0.51 | 0.28 / 0.25 |
| H13 LL | 111 | 13.5 / -35.5 | 320 / 122 | 90 / 68 | 198 / 87 | 0.53 / 0.49 | 0.27 / 0.25 |
| E1 UL | 101 | 17.9 / -43.9 | 437 / 178 | 119 / 89 | 209 / 108 | 0.60 / 0.55 | 0.30 / 0.27 |
| E1 UR | 105 | 17.0 / 48.0 | 457 / 162 | 113 / 85 | 223 / 118 | 0.61 / 0.56 | 0.31 / 0.28 |
| E1 LL | 112 | 13.9 / -49.8 | 443 / 123 | 92 / 69 | 235 / 123 | 0.59 / 0.55 | 0.30 / 0.27 |

Stud at mid-bay instead of at the root: D/C 0.41-0.48 (n = 1, s 100). Factored case C_f: 0.43-0.49 (s 100). Required: a 4-screw group per stud (2 upper + 2 lower, >= 20 mm apart in the 1.5 in face) or accept D/C 0.5-0.6; S10 for the mask arm (153-199 N, D/C 0.22-0.28) is on its own plate row and is not added here. Out-of-plane moment is small (the pot is only 120-200 mm out from the wall in z); the shear/uplift from the in-plane moment dominates. Lower-row bearing and drywall are as rp2 s.4.2 (not re-run).

## 7. Does E1's 1206 mm change the wall scheme?

Screws: no new scheme, but a 2-per-row group is now needed on all six (E1 worst 0.56 vs H13 0.51 at 1 screw per row). Studs (406 mm OC, `studs_under_width` in JSON): 914 mm spans 2.25 bays: 2 studs, or 3 in 25% of phases. 1206 mm spans 2.97 bays: 3 studs in 97% of phases (2 in 3%). So H13 can sit on one stud pair under the trunk; E1 reaches a third stud but the three cleat bars are still sized for 2-stud pairs, and the plate loads act 437-457 mm from the root, so 2-stud bars see the uplift row go from 77-87 N to 108-123 N. Practical rule for E1: run the cleat bar across the root block to a stud on the load side as well (>= 3-stud span, ~850 mm) or add a hold-down screw on the outer stud under each plate; the trunk back plate must carry 44-50 N.m in-plane from the root block to the bar, not through the 2.6 mm membrane. Placement phase (stud map) decides which: it is Evan's input and still unknown. If the pair cannot sit under the root, the piece shifts up to 203 mm sideways; E1 has less room to shift.

## 8. Not verified

E, creep, allowables ([GENERAL], no coupon); trunk and root-block stiffness, so the root is modelled fixed; plate flat-top skin and rim; fatigue; epoxy shear; stud wood and drywall; all three shelves loaded together with the body and mask arm on the same cleats; 5 kg plant with a pot taller than 140 mm (CAD plant proxy only); the 14 kg mass cap (rods 0.6-0.9 kg each add to it; CAD to report the real hollowed mass).

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-19 | structural-lead | Initial creation: r13 shelf-arm reach check, H13 and E1 | [PROVISIONAL] |
