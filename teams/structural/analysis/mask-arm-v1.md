# Mask Arm v1: tentacle-held mask, first-principles structural spec

**Status:** structural-lead, 2026-11-18. Phase 1 (spec before CAD geometry). Hand calcs, no FEA, no coupon test. [PROVISIONAL] until peer sign-off. Directive: DECISIONS 2026-11-18 round-10 O3 ("the tentacle should be structurally sound and have gone through the review process"; mask held "in a similar way to how the platforms are held"). Method, E and creep derates carried from `rp2-strut-limb-voids.md` Sections 2.1 and 3 (E 1,600 MPa short-term, 640 MPa at 10 yr 23 C, 400 MPa at 40 C; all [GENERAL], unmeasured). Printability not assessed here (Fabrication).

## 0. Verdict and SPEC

The CAD placeholder (22 mm printed core, no rod) **FAILS** long-term droop: 6.7 mm at 23 C, 10.8 mm at 40 C, vs 3 mm limit. Stress is not the issue; stiffness is. **A straight steel rod in the arm is required.** An all-PETG arm passes only at d >= 32 mm solid with the axis in XY (fallback, Section 5).

### SPEC (CAD builds to this)

| # | Item | Value |
|---|---|---|
| S1 | Reinforcement | **Straight 10 mm steel rod, Fy >= 300 MPa** (cold-drawn 1018/12L14, or smooth 8.8 shank; NOT annealed 304, NOT threaded rod in the span). Pultruded carbon 10 mm rod is an accepted equal (EI 6.4e7 N.mm^2 vs steel 9.8e7). PETG wrap is not credited. |
| S2 | Printed core around rod | Solid, d >= 22 mm (CAD placeholder OK), bore 10.4 mm; radial PETG cover over the rod >= 5 mm at every station (>= 3.0 mm absolute floor where a sculpted tentacle thins). Rod axis within 15 mm of the tentacle centreline along the rod span; curls beyond the rod tip are decorative. |
| S3 | Root | Root dia >= 60 mm (placeholder OK). Solid root block (100% infill, no shell/void) >= 60 mm dia x >= 80 mm deep, rod embedded >= 80 mm (8 d) in it. Block merges into the segment solid back plate / through-spine (solid pad >= 100 x 100 mm, >= 6 mm thick), not into a hollow shell. |
| S4 | Root seam (if arm is a separate print) | Rod crosses the seam, epoxy-bonded both sides (structural 2-part epoxy), bore 10.4 mm, seam land >= 1,500 mm^2 solid ring, spigot-and-socket >= 15 mm deep to keep alignment. Seam is not the load path (rod is). Do not put a seam within 40 mm of the root face other than at the face itself. |
| S5 | Mask end | Rod continues >= 40 mm (4 d) into a blind bore in the mask, epoxy-bonded. Solid pad (100% infill) >= 70 mm dia x >= 30 mm deep around the bore and spigot socket, fillet >= 15 mm to the shell. Anti-rotation: D-flat or 2 keys on the 40 mm boss (torque 4 N.m, Section 3). |
| S6 | Fingers | >= 4 root fingers are load-spreading / aesthetic. **Zero structural credit.** They may not be the only mask retention. |
| S7 | Mask construction | **Separate print, bonded to the arm** (Section 4). Mask mass <= 0.8 kg (CAD reports volume and shell/infill basis). |
| S8 | Reach / tilt | Horizontal lever from root axis at the trunk surface to mask CoM **<= 250 mm** (hard cap, covers the 60-100 mm and the 150 mm variants). Centreline length < 250 mm stands. Tilt <= 25 deg as designed (<= 35 deg allowed without re-review); CoM offset from rod axis <= 50 mm. Any growth in reach, tilt, or mask mass re-opens review. |
| S9 | Print orientation | Rod makes orientation non-critical. If any all-PETG section carries bending (no rod there), its axis must be within 30 deg of the XY plane. No layer interface across the root face tension side (fallback only). |
| S10 | Wall load | Extra anchor tension from a 40 N bump, Section 6: <= 80 N per screw (2-screw row). Combined with a shelf on the same cleat: D/C <= 0.5. CAD to name the nearest anchor row to the root. |

## 1. Loads

### 1.1 Mask self-weight (200 mm disc, carved, 2 mm walls, PETG 1.27 g/cm^3)

Surface = front relief (1.35 x pi R^2) + back (1.05 x pi R^2) + rim (pi D t). Volume = surface x wall + interior x carve fraction x infill.

| Case | D x t (mm) | wall | infill | carve fill | Volume (cm^3) | Mass (g) |
|---|---|---|---|---|---|---|
| Low | 180 x 25 | 2.0 | 10% | 0.5 | 182 | 230 |
| Nominal | 200 x 40 | 2.0 | 15% | 0.6 | 314 | 400 |
| High | 200 x 50 | 2.4 | 20% | 0.7 | 476 | 605 |
| Bound (220 mm, 25% infill) | 220 x 50 | 2.4 | 25% | 0.75 | 658 | 836 |

Range 0.23-0.84 kg, nominal 0.4. **Design W_m = 0.8 kg = 7.85 N** (covers the bound; includes paint/finish ~5%). Arm self-weight incl. 10 mm x ~330 mm steel rod (0.20 kg) + 22 mm core (0.12 kg) + wrap (~0.1 kg) = 0.45 kg = 4.4 N, w = 4.4/250 = 0.0176 N/mm.

### 1.2 Bump / grab (choice and basis)

**40 N at the mask edge, any direction.** Basis: a hand brushing or shoving a protruding object in a hallway/living space (typical incidental contact 10-30 N; a firm push to steady oneself 40-50 N). 40 N sits in the upper band; it is a service load, applied with no further factor, checked against yield (D/C on steel yield, not ultimate). Deliberate pull-down or hanging (> 100 N) is abuse: the mask-to-rod bond and the arm may fail but the wall anchors must not (Section 6 shows they have > 2x margin at 40 N). Lever: arm reach 250 + mask radius 100 = 350 mm. M_bump = 40 x 350 = 14.0 N.m. Torsion from an edge push offset from the arm axis: T = 40 x 100 mm = 4.0 N.m.

### 1.3 Dusting

5 N at the edge, repeated: M = 1.75 N.m. Rod stress 36 MPa, far below any fatigue limit for steel. Not governing.

### 1.4 Sustained

M_sus = W_m L + W_a L/2 = 7.85 x 250 + 4.4 x 125 = 2,513 N.mm = 2.51 N.m (bounding lever L = 250, arm horizontal).
Governing combination: M = M_bump + M_sus = 16.5 N.m (conservative: bump and full sustained at the same instant, same direction).

### 1.5 Allowables [GENERAL]

| Material | Sustained | Transient (bump) |
|---|---|---|
| PETG/ASA along layers | 7 MPa (rp2) | 22 MPa |
| PETG/ASA across layers | 3 MPa | 8 MPa |
| Steel rod | n/a | Fy >= 300; D/C <= 0.7 on yield |

## 2. Arm as cantilever

Tip sag (mask CoM) delta = W_m L^3/(3EI) + w L^4/(8EI), L = 250 mm. Numerator N = 7.85 x 250^3/3 + 0.0176 x 250^4/8 = 4.09e7 + 8.6e6 = **4.95e7 N.mm^3** (arm 4.4 N, w = 0.0176 N/mm).

### (a) Stress (solid round, sigma = 32 M / (pi d^3), M = 16.5 N.m)

| Section | sigma (MPa) | Allowable | D/C |
|---|---|---|---|
| 10 mm steel rod | 168 | Fy 300 | 0.56 (PASS) |
| 8 mm steel rod | 329 | Fy 300 | 1.10 (FAIL) |
| 22 mm PETG, along layers | 15.8 | 22 | 0.72 |
| 22 mm PETG, across layers (Z-axis print) | 15.8 | 8 | 1.97 (FAIL) |
| 32 mm PETG, across layers | 5.1 | 8 | 0.64 |
| 60 mm root block, PETG | 0.78 | 8 | 0.10 |

Minimum solid d for stress alone (M = 16.5 N.m): along layers 19.6 mm; across layers 27.5 mm; steel (Fy 300 x 0.7 = 210 MPa) 9.3 mm. So 10 mm is the practical rod minimum (8 mm FAILS).

### (b) Long-term droop <= 3 mm at 10 yr

I_req = N / (E_lt x 3 mm): 23 C (640 MPa) **25,800 mm^4 = 26.9 mm solid PETG**; 40 C (400 MPa) 41,200 mm^4 = 30.3 mm.

| Section | EI (N.mm^2) | Sag, mm | Verdict |
|---|---|---|---|
| 22 mm PETG, 23 C | 640 x 11,499 = 7.4e6 | 6.7 | FAIL |
| 22 mm PETG, 40 C | 400 x 11,499 = 4.6e6 | 10.8 | FAIL |
| 32 mm PETG, 23 C / 40 C | 3.3e7 / 2.1e7 | 1.5 / 2.4 | PASS |
| 30 mm PETG, 40 C | 1.6e7 | 3.1 | marginal FAIL |
| **10 mm steel (rod only)** | 2e5 x 491 = 9.8e7 | **0.50** | PASS (6x margin; no creep) |
| 8 mm steel | 4.0e7 | 1.23 | PASS (stress fails) |

Bump elastic deflection at the edge (40 N, lever 350, 10 mm steel): 5.8 mm transient, recovers (steel stays elastic). Natural frequency k = 3EI/L^3 = 18.9 N/mm, m 0.9 kg gives f ~ 23 Hz: no rattle concern.

### (c) 150 mm out, 25 deg tilt variant

Governing lever is geometric. If the arm is <= 250 mm and the mask CoM is <= 250 mm horizontally from the root axis, the calcs above bound it. Tilt moves the CoM, not the weight; with CoM offset <= 50 mm off the rod axis, static torque = 7.85 x 50 = 0.4 N.m (vs 4.0 N.m bump torsion). 10 mm rod in torsion at 4 N.m: tau = 16 T / (pi d^3) = 20 MPa (shear yield ~ 170): D/C 0.12. Mask boss keyed (S5). If the arm rises above horizontal, the horizontal lever shrinks and the case improves; arm drooping below horizontal does not change the horizontal lever. Passes at the same spec. CAD must still report the as-built lever.

## 3. Connections

- **Root.** Rod is the cantilever; the PETG root block is a bearing seat. Bearing couple at M = 16.5 N.m, embed 80 mm, reaction arm ~ 0.67 x 80 = 53 mm: F = 16,500/53 = 310 N; bearing area ~ d x le/2 = 10 x 40 = 400 mm^2: 0.78 MPa vs 8 MPa transient. Large margin; the real risk is the **block not being solid** (2 mm shell + 15% infill would crush/crack). Hence S3 solid block, merged into the segment plate/spine. Seam, if any: plain-bending stress at a solid 60 mm section 0.78 MPa, so seam bond is secondary; the rod crosses it anyway.
- **Mask end.** Moment at boss from an edge push: 40 x 100 = 4.0 N.m; couple on a 40 mm rod embed: F = 4,000/27 = 150 N on 10 x 20 = 200 mm^2: 0.75 MPa. Axial pull-off of the mask: epoxy shear area pi x 10 x 40 = 1,257 mm^2; 100 N pull gives 0.08 MPa. Both large margin. Weak point is the mask shell around the socket, hence the solid pad (S5). Torsion 4 N.m on the 40 mm keyed boss: tau 0.3 MPa.
- **Wall.** Section 6.

## 4. Separate mask vs integral: separate, bonded (recommended)

1. Print: carved mask prints back-down on the bed, relief up; a blind socket in the back opens onto the bed (a plain hole in the first layers, no support). An integral arm+boss on the back would have to print back-up or the boss goes through the bed. The arm prints along XY separately (<= 250 mm, bed OK).
2. Finish: mask can be painted, weathered, eyes/fangs detailed off the wall; the arm and trunk stay in the wall segment kit.
3. Risk: mask is the highest-touch, most-damageable part; a separate part can be replaced or re-bonded without reprinting the arm.
4. Structure: load goes into steel, not a printed boss; boss only locates and prevents rotation.
5. Shipping: mask can travel unmounted; the rod end is the only protrusion.

Bond: structural 2-part epoxy (not CA); 10.4 mm bores, rough-sand the rod, degrease. Optional: two M4 cross-pins through boss + rod to make the bond non-critical (not required by the numbers).

## 5. Print orientation and the all-PETG fallback

Layer lines are across the bending stress only when the arm axis runs along Z. Arm axis in XY: bending stress is along layers (good); interlayer shear max tau = 4V/(3A) = 0.1 MPa at 40 N (negligible). Tentacle sculpts that curl up in Z put stress across layers in those sections. With the steel rod this does not matter (rod carries everything). Fallback if CAD cannot fit a rod: all-PETG core **d >= 32 mm solid, axis within 30 deg of XY, no seam in the first 150 mm, 100% infill core**. 40 C sag 2.4 mm, bump + sustained stress 5.1 MPa (across layers D/C 0.64). Not preferred: unmeasured E and creep, no margin if the room is hot.

## 6. Wall effect

40 N bump at 0.40 m from the wall plane, anchor row spacing s = 100 mm: T = 40 x 0.40 / 0.10 = 160 N per row, 80 N per upper screw (2 per row). Screw caps 350 / 530 N (rp2): D/C 0.15-0.23. With a shelf on the same row (98 N/screw, rp2 Section 3.3): 178 N/screw, D/C 0.34-0.51. Sustained mask weight at 0.2-0.3 m: negligible (7.85 N x 0.3 / 0.1 = 24 N per row). Mask arm is not an anchor-governing case.

## 7. Phase 2 pass / fail criteria

CAD supplies (README "mask-arm geometry" and/or `mask_arm_for_review.stl`): rod dia/length/embed, root block size, core dia, lever to mask CoM, mask mass basis, tilt, seam locations, print orientation. Structural scores:

| # | Criterion | PASS |
|---|---|---|
| P1 | Rod | Steel/carbon, 10 mm min, Fy >= 300 MPa, in the model as a bore (10.4 mm) with >= 5 mm cover (3.0 mm floor) |
| P2 | Rod embed | >= 80 mm in solid root block, >= 40 mm in mask pad |
| P3 | Root block | Solid >= 60 mm dia x 80 mm deep, merged to solid plate/spine >= 100 x 100 x 6 mm |
| P4 | Mask pad | Solid >= 70 mm dia x 30 mm deep, fillet >= 15 mm |
| P5 | Lever | Horizontal root axis to mask CoM <= 250 mm; tilt <= 25 deg (<= 35 allowed) |
| P6 | Mask mass | <= 0.8 kg from CAD volume x 1.27 |
| P7 | Core | >= 22 mm solid continuous along the rod span; any section thinner than 22 mm only beyond the rod tip |
| P8 | Rod straight | Rod axis within 15 mm of centreline; no bend |
| P9 | Seam | If separate arm: rod crosses seam; land >= 1,500 mm^2; no seam within 40 mm of root face except the face |
| P10 | Orientation | Arm axis in XY, or rod present (then waived) |
| P11 | Fingers | Not counted as retention; boss anti-rotation key present |
| P12 | Clearance | Arm and mask do not touch the wall plane, trunk, or other limbs under 6 mm sag |

Any miss on P1-P6 = FAIL (rework). P7-P12 miss = FAIL with a named fix. Not verified until built and bench loaded: a 10 N (1.0 kg) mask-dummy hang test for 7 days and a 40 N edge push test on the first print.

## 8. Assumptions

E, creep, interlayer strength, allowables: [GENERAL] and unmeasured. The bounding lever (250 mm horizontal) ignores the benefit of any upward angle. The bump and the sustained loads are summed (conservative). No FEA of the root block or the mask pad.

## 9. Phase 2 review, round-11 build

**Status:** structural-lead, 2026-11-18 [PROVISIONAL]. Sources: `teams/cad/composition_r11/README.md` s.3-4, `arm_report.json`, `build/{H,V3}_{armpart,maskpart,rod}.{npy,stl}`, `build/{H,V3}_meta.json`, `mask_arm_for_review.stl`. I re-measured from the 2 mm voxel arrays (`*_armpart.npy`, `*_maskpart.npy`, `*_rest.npy`) and the STLs, not from CAD's numbers. Voxel resolution is +-2 mm. No FEA, no bench test.

**Verdict (board-note line):** Structural PASS for H and V3 mask arm: 10 mm steel rod in a 50-70 mm solid sheath, rod D/C 0.38 (H) / 0.46 (V3) under a 40 N edge bump, 10-yr droop < 0.5 mm vs 3 mm; conditions: rod Fy >= 300 MPa on the BOM, root block + plate sliced 100% solid, dedicated stud-screw row under the arm plate (needs a stud there), epoxy fills the bore annulus.

### 9.1 Independent measurements (H / V3)

| Quantity | CAD | My check | Note |
|---|---|---|---|
| Mask CoM (x, y, z) | (-30.4, 241.7, 211.8) / (-29.3, 242.1, 276.8) | same (voxel centroid of mask part) | match |
| Horizontal lever exit axis to CoM | 123.6 / 187.1 | 123.6 / 187.1 | match; cap 250 |
| Farthest mask voxel from exit | n/a | 228.2 / 271.3 | used for bump moment |
| CoM offset from rod axis | 21.7 / 24.9 | 21.7 / 24.9 | match; cap 50 |
| Rod (`H_rod.stl`) | dia 10, axis (-0.191, 0.380, 0.905) | dia 10.38 (volume/length), PCA axis (-0.191, 0.380, 0.905) | match; V3 has no rod STL |
| Root block 60 dia x 82 deep, 100% solid (bore filled) | 1.00 / 1.00 | 1.00 / 1.00 (29,000 cells) | match |
| Solid thickness under the 100 x 100 plate, from z 2 | "plate 100% solid z 2-6" | min 10 mm, median 90 mm, over all 2,601 columns | stronger than claimed; >= 6 |
| Sheath surface distance from rod axis, free span | cover 12.8 / 8.8 (min over A..pad) | >= 21.4 / 23.2 mm to surface along the whole span (cover >= 16); lowest at the ends: rod end A to wall face 10.8 / 6.8 mm (cover), D-flat region 10.8 mm | CAD's minima are the wall-side rod end; consistent within +-2 mm |
| Arm free-span min clearance to rest of piece (CAD rule: 3D > 45 mm from exit, s > exit + 20) | 6.3 / 9.2 | 6.3 / 9.2 | reproduced; position (-26, 198, 116) H; value grows with distance from exit (11.8 at s > exit + 45, 24.4 at + 60) |
| Mask mass | 0.566 kg (pad + fingers 100% solid) | 0.42 kg (whole part shell 2 mm + 15%, +5% finish); 0.566 as CAD | both < 0.8 |
| Review STL | "two watertight bodies" | combined file is NOT watertight; `H_armpart.stl`, `H_maskpart.stl` individually watertight; `V3_*part.stl` have inverted normals (negative volume) and are not watertight | flag to CAD, not structural |

### 9.2 Loads on the as-built geometry (design mask 0.8 kg = 7.85 N, arm free span 3.9 / 5.3 N)

| | H | V3 |
|---|---|---|
| M_sustained at exit (mask 7.85 x lever + arm) | 7.85 x 123.6 + 3.9 x 42 = 1.13 N.m | 7.85 x 187.1 + 5.3 x 70 = 1.84 N.m |
| M_bump = 40 N x farthest mask point | 40 x 228.2 = 9.13 N.m | 40 x 271.3 = 10.85 N.m |
| M total | 10.27 N.m | 12.69 N.m |
| Rod bending stress 32M/(pi 10^3) | 104.6 MPa | 129.3 MPa |
| Torsion T = 40 N x 125 mm = 5.0 N.m, tau = 16T/(pi d^3) | 25.5 MPa | 25.5 MPa |
| Von Mises sqrt(sigma^2 + 3 tau^2) | 114 MPa | 137 MPa |
| D/C on Fy 300 (limit 0.7) | **0.38** | **0.46** |
| 10-yr droop at mask edge, rod only, cantilever from block face + 20 mm fixity allowance (EI 9.82e7 N.mm^2, perpendicular gravity fraction 0.93 / 0.97) | tip 0.11 + rotation 0.10 = **0.2 mm** | tip 0.28 + rotation 0.19 = **0.5 mm** |
| Limit | 3 mm | 3 mm |

Sheath: PETG sheath at 69 mm dia (I 1.15e6 mm^4, E_lt 640) is stiffer than the rod (EI 7.3e8 vs 9.8e7); if bonded it carries ~88% of the moment at < 0.3 MPa outer-fibre stress. Not credited. Result: orientation and interlayer strength do not matter at these loads, and the rod is a backup, not the sole path. Mask end: edge push 40 N x 110 mm = 4.4 N.m; spigot-socket reaction 0.37 MPa, rod-epoxy shear at a 100 N pull 0.10 MPa, D-flat key 0.4 MPa (5 N.m / 18 mm = 280 N on 24 x 30 mm). All < 0.1 of capacity.

### 9.3 P1-P12, H and V3

| # | Criterion | H | V3 | Basis |
|---|---|---|---|---|
| P1 | 10 mm rod, bore 10.4, cover >= 5 (3 floor) | **PASS** | **PASS** | Rod STL dia 10.4/10.38, axis matches. Cover >= 16 on the span; at the wall-side rod end 10.8 / 6.8 mm (>= 5, V3 tight at +-2 mm). Condition: BOM must state steel Fy >= 300 MPa (README says only "10 mm steel") |
| P2 | Embed >= 80 root / >= 40 mask | **PASS** (82 / 44) | **PASS** (82 / 44) | Root: 82 in a solid block. Mask end, read strictly: 14 mm in the mask's own bore plus 30 mm through the arm-tip spigot (dia 40, 15 mm wall, solid, keyed, epoxied into the socket). I accept the assembly as equivalent (two bond interfaces, 980 and 3,770 mm^2, both < 0.4 MPa). Waiver is conditional on epoxy at BOTH interfaces |
| P3 | Root block solid >= 60 x 80; plate >= 100 x 100 x 6 | **PASS** | **PASS** | Measured above. Condition: slicer 100% infill modifier over the block (60 dia x 82 along axis), the column, and the 100 x 100 plate zone; a voxel-solid model does not make a solid print |
| P4 | Pad >= 70 x 30, fillet >= 15 | **PASS** (70 x 38, k 28 ~17 mm est.) | **PASS** | Pad dims from CAD; r33.5 ring 100% solid (re-measured by CAD, not by me); fillet radius is a design value, not measured on the mesh. Re-check on the final-CAD mesh |
| P5 | Lever <= 250; tilt <= 25 (35 max); CoM offset <= 50 | **PASS** (123.6; 15 deg; 21.7) | **PASS** (187.1; 25 deg; 24.9) | Re-measured. V3 mask roll is at the 25 deg limit; rod 16 deg off wall normal; centreline A to tip 238 mm of the 250 cap |
| P6 | Mask mass <= 0.8 kg | **PASS** (0.42-0.57) | **PASS** | |
| P7 | Core >= 22 mm along rod span | **PASS** (>= 42) | **PASS** (>= 46) | Distance from axis to the surface, my EDT, not at the wall-side end (>= 32 / 26 there) |
| P8 | Rod axis within 15 mm of centreline, straight | **PASS** (3.5) | **PASS** (3.5) | Rod PCA axis straight; sheath surface distance >= 21 mm everywhere on the span, so the rod sits well inside the sheath |
| P9 | Rod crosses seam; land >= 1,500 mm^2; no seam within 40 mm of root face | **PASS** (no root seam; land 1,785) | **PASS** (1,837) | Arm is integral with the trunk segment. See F2 for the V3 print-height issue |
| P10 | Arm axis in XY or rod present | **WAIVED** (rod) | **WAIVED** (rod) | Axis is 65 / 74 deg out of XY; sheath stress < 0.3 MPa so interlayer strength is irrelevant |
| P11 | Fingers not retention; key present | **PASS** | **PASS** | 6 fingers, D-flat 16 mm from axis. Fingers hook 6.6 mm over the front lip (0.6 mm over the 6 mm plate-finger rule): a Fabrication call |
| P12 | Clear of wall, trunk, limbs under 6 mm sag | **PASS** (6.3 mm marginal on paper, adequate on analysis) | **PASS** (9.2) | See 9.4 |

All of P1-P12 pass for H and V3. Mask-to-rest (eyes) 38.2 / 93.8 mm; arm min z 84 / 88 (wall).

### 9.4 CAD flag 1: P12, H free-span clearance 6.3 mm

PASS. 6.3 mm reproduced (voxel +-2 mm, so >= 4.3 mm worst case). The 6 mm number in P12 was a sag allowance for the arm; real sag at the closest station is far smaller. Station is ~38 mm along the axis from the exit (x = 38 mm from the block face): delta = W x^2 (3L - x) / (6EI) = 7.85 x 38^2 x (3 x 164 - 38) / (6 x 9.82e7) = 0.009 mm. Tip sag 0.2 mm (9.2). Even a 40 N bump at the edge moves that station < 0.1 mm. Contact with the patch swelling would not load anything structurally. Closer to the exit the arm merges into flesh by design. Nothing to change.

### 9.5 CAD flag 2: S10 anchor row (decision)

No anchor layout exists. **Decision: the arm gets its own dedicated stud-screw row, at the arm plate (centre y ~ 137), not a share of S1_UL.** Reasons: S1_UL is 107 mm away, so sharing routes 11-15 N.m through a 2.6 mm membrane or a new web; the dedicated row is the short load path and leaves the shelf row at its current D/C.

Spec for the row: 4 x #10 x 2.5 in stud screws through the 100 x 100 plate, 2 upper at y ~ 175, 2 lower at y ~ 100 (vertical spacing >= 75 mm), upper pair >= 20 mm apart in the same stud (1.5 in face); counterbored seats in the plate (head pull-through is not governing: ~4 kN vs < 0.1 kN).

Load (wall moment = sustained + 40 N bump at the farthest z of the mask, any direction):

| | H | V3 |
|---|---|---|
| M_wall sustained (mask at z 211.8 / 276.8 + arm) | 2.2 N.m | 3.0 N.m |
| M_wall bump (40 N x mask max z 233 / 298) | 9.3 N.m | 11.9 N.m |
| Upper-row tension at s = 75 mm | 153 N | 199 N |
| Per upper screw (2) | 77 N | 99 N |
| D/C vs 350 N (lower pull-out cap, rp2) | 0.22 | 0.28 |
| Fallback: shared S1_UL row, s = 100 mm (adds 58 / 75 N per screw to the shelf's 98 N) | 156 N, D/C 0.45 | 173 N, D/C 0.49 |

Open conditions: (i) a stud must lie under the plate; Evan's stud map is still open, so S10 stays CONDITIONAL until CAD's anchor layout lands and shows it. (ii) If no stud is available, use the shared fallback only with a >= 6 mm solid web from the plate to the S1_UL cleat zone (D/C 0.45-0.49 passes, but not by a wide margin: 0.5 limit). (iii) CAD names the row in its anchor map. Not checked: wall deflection, stud split near the plate.

### 9.6 Findings for CAD / Fabrication (non-structural, not blocking)

- F1. `mask_arm_for_review.stl` is not watertight as a combined file (README says two watertight bodies); the part STLs `H_armpart/H_maskpart` are. `V3_armpart/V3_maskpart` STLs have inverted normals (negative volume, not watertight). Repair before any slicing.
- F2. V3 arm part spans z 0-270 mm: if the arm is integral with its trunk segment and the segment prints upright, it exceeds a 256 mm build height. H arm part is z 0-209: OK. Fabrication/CAD decide (split the arm at the wall with a rod-crossing seam, or print V3 tilted).
- F3. Bore 10.4 vs rod 10.0: the 0.2 mm radial annulus must be fully filled with epoxy (syringe/vacuum). An unfilled annulus allows +-0.4 mm / 82 mm = 0.005 rad tilt, ~0.7 mm at the mask CoM; still inside the 3 mm limit but loose.
- F4. Rod grade on the BOM (Fy >= 300; smooth shank 8.8 or cold-drawn 1018). Not annealed 304. Carbon equal is accepted.
- F5. P3/P4 solid zones need slicer modifiers (100% infill: block, column, plate, pad, spigot). The model being voxel-solid does not set this.
- F6. P4 fillet radius (k 28, ~17 mm) is a design estimate; re-measure on final-CAD mesh. Bond clearances 0.15 mm and the D-flat are nominal in the voxel model; recut in final CAD.

### 9.7 Not verified

No bench test. First print: 1 kg dummy-mask hang test for 7 days and a 40 N edge push test (spec Section 7). E, creep, epoxy shear properties [GENERAL]. Anchor layout not designed. Final CAD mesh not reviewed.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-18 | structural-lead | Initial creation, Phase 1 spec (mask arm v1) [PROVISIONAL] | |
| 2026-11-18 | structural-lead | Added section 9, Phase 2 review of the round-11 build (H, V3): P1-P12 PASS, S10 decision, findings F1-F6 [PROVISIONAL] | |
