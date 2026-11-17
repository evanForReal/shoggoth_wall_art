# RP-2 Item 3: Strut Spec, Limb Min I, Blind-Pocket Relaxation, Mass Check

**Status:** structural-lead, 2026-11-16. Hand calcs, no FEA, no coupon test. Extends `load-model-v1.md`; where numbers conflict, this file supersedes load-model Section 6 strut member and mesh-spec-v1 Section 5 "Member" row. Fabrication reviews (a) independently on printability; nothing here speaks for them.

## 0. Exec summary

| Item | Verdict | Number CAD builds to |
|---|---|---|
| (a) Blind pockets < 6 mm | **CONDITIONAL SIGN** | Floor >= 2.0 mm (CAD's 2.6 mm passes); excluded from 7 load-path zones (Section 1); corner radius >= 0.5 mm; through-voids keep 6 mm |
| (b) One strut spec | **Core I >= 11,000 mm^4** (24 mm OD x 3.0 mm wall tube, or 22 mm solid), design L_eff 500 mm, chord <= 470 mm; foot pad >= 75 x 60 mm, two #10 x 2.5 in stud screws | replaces all three existing specs |
| (c) Limb (shelf arm) min I | **I >= 1.2e5 mm^4, Z >= 3,400 mm^3, solid core d >= 40 mm** at the root, held to 0.5 p | |
| (d) 22 kg proxy | Mount OK at 22 kg and at 14 kg. Realistic shelled mass **~11 kg (7-15)** | Cap stays 14 kg; high case exceeds it |

Findings that change prior documents:
1. Fullpiece v1 strut (solid r15, I = 2,485 mm^4) **fails**: P_cr = 218 N short-term (2.1x) but **87 N creep-derated, below the 104 N factored load**. It is also weaker than the load-model tube (3,144 mm^4).
2. Mesh-spec-v1 I >= 6,300 mm^4 [PROPOSED] is **rejected as too low** under creep. Replaced by 11,000.
3. A 420-500 mm strut does not fit a 256 mm bed (diagonal 362 mm). The core is spliced or metal; Section 2.6.

## 1. (a) Blind relief pockets < 6 mm

**Verdict: CONDITIONAL SIGN.** The 6 mm through-void floor in mesh-spec-v1 Section 2 is a printability rule (bridging, cleaning), not a structural one. A blind pocket keeps the back membrane continuous, so in-plane section is unchanged and nothing is cut through.

Checks:
- Net section: back plane stays a continuous 2.6 mm plate (fullpiece back plane z 0-3 mm). Pockets remove front relief only. No loss of the membrane load path.
- Local stress: worst case, a 10 N poke at the centre of a 5 mm pocket on a clamped 2.6 mm floor. sigma = 3P / (2 pi t^2) = 30 / (2 pi x 6.76) = 0.7 MPa vs 7 MPa sustained. Even with Kt = 3 at the rim: 2.1 MPa. Not governing.
- Wall behind the pocket = floor thickness. Floor >= 2.0 mm = the decorative-strand floor (mesh-spec Section 2, PETG/ASA) and above the 1.2 mm decorative skin floor.
- Not assessed (not my call): moisture, dust, cleaning, finish coat filling, printability of the pocket floor orientation.

Conditions (all must hold, else the relaxation does not apply to that pocket):
1. Floor (wall behind pocket) >= 2.0 mm everywhere. CAD's 2.6 mm plug passes with 0.6 mm margin; a voxel/sculpt pass that thins it below 2.0 mm voids the sign-off. Add to the validator.
2. Exclusion zones, no sub-6 mm pocket (and no pocket of any size cutting the core) inside:
   - cleat seat block + 100 mm margin (mesh-spec Section 3 keep-out);
   - bearing pads and hold-down pads (compression patches must be contiguous solid);
   - strut core envelope and strut tip/foot nodes + 75 mm;
   - shelf arm root, wall to 0.5 p (Section 3 of this file);
   - segment joint lands and seam bonding areas (>= 400 mm^2 solid per seam, mesh-spec Section 8);
   - splice-strap boss and heat-set insert zones (+10 mm);
   - the whole shelf top plate under the 150 x 150 footprint.
3. Re-entrant corners: fillet radius >= 0.5 mm at floor and walls. No sharp slots.
4. Pocket ligament (wall between neighbouring pockets) >= 2.0 mm.
5. Scope: blind relief only. Through-voids keep the 6 mm rule. Any through-void in an exclusion zone keeps the 6 mm rule AND needs a structural look.
6. Pocket floor stays on the back plane (plug on the build face, as in gate1c). If a segment is printed in another orientation, the floor layers must still be parallel to the load-carrying face; flag to Structural.

Residual risk: CAD cites 160 pockets converted in gate 1C and gate 2 void share < 6 mm went 22% to 33% (audit). That is a thin-feature trend, not a pocket issue, and is Fabrication's and CAD's to restate. Structural position: acceptable outside the exclusion zones.

## 2. (b) Strut core spec

### 2.1 Basis and assumptions

| Item | Value | Basis |
|---|---|---|
| Factored axial P | 104 N (73.6 N vertical + 73.6 N horizontal at 45 deg) | load-model Section 6; plant 5 kg x 1.5 at the shelf tip |
| Worst angle | 45 deg (chord = p = drop). Steeper strut lowers P: drop 350 mm, p 300 mm gives 97 N | statics |
| E, printed PETG/ASA, along layers | 1,600 MPa short-term | [GENERAL] conservative vs 2,000 neat; tube walls, not infill |
| Creep derate (10 yr, 23 C, sigma < 25% of strength) | x 0.40, E_lt = 640 MPa | [GENERAL] PETG apparent modulus; not measured. At 40 C (sun, heater) use 0.25, so 400 MPa |
| End conditions | pinned-pinned, K = 1.0, no credit for rotational fixity | conservative; tip node bonds to a flexible shelf, foot to a pad |
| Curvature of sculpted limb | L_eff = 1.1 x chord | a muscular S-curve is longer than the chord and starts imperfect |
| Imperfection | e0 = L_eff / 150 = 3.3 mm (L/300 would suit a straight tube) | sculpt allowance |
| End eccentricity | 10 mm max (strut axis vs pad / node centroid) | CAD must hold; Section 2.5 |
| Buckling factor | P_cr,lt >= 2.5 x 104 N = 260 N | ~3.5x the unfactored 75 N sustained load; 2.5 on factored covers imperfection, impacts (plant knocked, hand pressed on shelf) and unmodelled creep (40 C case) |
| Sustained stress allowable | 7 MPa | load-model Section 3 (PETG/ASA 7-10 MPa) |
| Printing | strut axis in the XY plane, never vertical | FDM layer rule; Section 2.4 |

### 2.2 Euler buckling, the three existing specs and the pick

P_cr = pi^2 E I / L_eff^2. Pinned-pinned. L_eff = 424 mm (bare chord, p = drop = 300) and 500 mm (design, chord <= 455 x 1.1).

| Spec | I (mm^4) | P_cr short, 424 | P_cr creep, 424 | P_cr short, 500 | P_cr creep, 500 | vs 260 N (creep, 500) |
|---|---|---|---|---|---|---|
| fullpiece v1 solid r15 | 2,485 | 218 N | **87 N** | 157 N | **63 N** | FAIL (below 104 N load) |
| load-model 20 x 1.2 tube | 3,144 | 276 N | 110 N | 199 N | 79 N | FAIL |
| mesh-spec 26 x 1.8 tube (I = 10,073) | 10,073 | 885 N | 354 N | 636 N | 255 N | 0.98x, marginal fail |
| mesh-spec I >= 6,300 | 6,300 | 553 N | 221 N | 398 N | 159 N | FAIL (1.5x factored) |
| **PICK 24 x 3.0 tube** | **11,133** | 978 N | 391 N | 703 N | **281 N** | **PASS 1.08x of 260; 2.7x of 104** |
| PICK alt: solid d = 22 | 11,499 | 1,010 N | 404 N | 726 N | 291 N | PASS |

Required I at L_eff = 1.1 c (c = chord): I_min = 2.5 x 104 x (1.1 c)^2 / (pi^2 x 640) = **0.0498 c^2**. c = 424: 8,950. c = 455: 10,300. c = 470: 11,000. c = 500: 12,450 (26 x 3.0 tube, I = 14,578). Rule: chord <= 470 mm for the 11,000 spec. Drop <= 350 mm at p = 300 gives c = 461.

### 2.3 Beam-column check (bending), 24 x 3.0 tube, L_eff = 500 mm

- Amplification: P_cr,lt = 281 N, P = 104 N, 1 / (1 - P / P_cr) = 1.59.
- Self-weight bending: limb mass 0.6 kg [assumption; sculpted wrap, CAD to report], normal component cos 45 = 0.707, q = 0.6 x 9.81 x 0.707 / 450 = 0.0092 N/mm; M_sw = q c^2 / 8 = 234 N.mm.
- Imperfection moment: P e0 = 104 x 3.3 = 347 N.mm. End-eccentricity moment: P x 10 mm = 1,040 N.mm (foot-pad side; the tip node is on a flexing shelf, same allowance).
- M = (347 + 1,040 + 234) x 1.59 = 2,570 N.mm.
- sigma = P/A + M c / I = 104 / 198 + 2,570 x 12 / 11,133 = 0.53 + 2.77 = **3.3 MPa** vs 7 MPa. A = 198 mm^2.
- Local tube buckling: D/t = 8, far below limits. Not governing.

The 74 N horizontal foot reaction is the horizontal component of P. It is NOT an independent lateral load on the strut; it matters (i) as the eccentricity moment above and (ii) as the thrust the shelf-root anchors must resist (load-model Section 6, 74 N inward pull at the root; D/C 0.17 on a stud screw).

### 2.4 FDM layer direction

Strut axis in the XY plane: axial compression and bending stress run along the layers (E_xy, in-plane strength 40 MPa short-term). Printed vertical: stress crosses layer interfaces, E_z ~0.8 x E_xy, interlayer tension 15-20 MPa short-term and ~5 MPa sustained; the 2.8 MPa bending tension in Section 2.3 would then run at ~55% of sustained interlayer strength. Rule: strut core printed lying down; the sculpted wrap may print in any orientation but is not credited.

### 2.5 Core definition for the sculpted limb

The sculpted tentacle wraps an embedded core. Credit the core only; the wrap gets zero (varying section, ribs, cosmetic grain; not controllable at the mesh level).

| Parameter | Requirement |
|---|---|
| Min I (any axis, every section along the full length) | **>= 11,000 mm^4** (chord <= 470 mm); 0.0498 c^2 otherwise |
| Min OD | **24 mm** (hollow) or **22 mm** (solid) |
| Wall if hollow | **>= 3.0 mm** (7 perimeters at 0.45 mm; a 1.8 mm wall fails I at 24 mm OD) |
| Equivalent stiffness (material-independent) | EI_lt >= 7.1e6 N.mm^2 |
| Metal substitute | any continuous core with EI_lt >= 7.1e6: steel rod 6 mm (EI 12.7e6) minimum, **8 mm steel rod recommended** (EI 40.2e6, P_cr 1,587 N at 500 mm); carbon pultruded 8 mm OK |
| End eccentricity | strut axis within 10 mm of tip-node and foot-pad centroids |
| Straightness | core centreline within 8 mm of the chord (S-curve allowance, covered by the 1.1 factor) |
| Tip node | solid, >= 30 x 30 mm, core embedded >= 40 mm; no segment joint within 75 mm |
| Foot node | solid, core embedded >= 40 mm |

Does not mean the limb silhouette must be 24 mm. The wrap is CAD's: thicker is free; the core must stay centred and continuous inside it.

### 2.6 Bed splice

Chord 420-470 mm exceeds the 362 mm bed diagonal. A printed core needs one splice. Structural-grade rule: continuous **8 mm steel rod** (or 8 mm carbon) through the core across the splice, >= 120 mm engaged each side, epoxy-bonded, splice >= 100 mm from tip and foot nodes. With the rod in place the rod governs (EI 40.2e6 vs 7.1e6) and the printed halves only keep the rod straight. No single printed piece of the core fits the bed (362 mm diagonal < 420 mm minimum chord), so the rod splice is the only path in the 256 mm bed. Fabrication owns the segment plan; this is the structural condition on it.

### 2.7 Foot: pad and fastener

Foot loads (factored): H = 74 N into wall (compression), V = 74 N shear down the wall. Strut axis meets the wall at stand-off h <= 30 mm above the datum.

| Check | Calc | Result |
|---|---|---|
| Pad bearing, 75 x 60 = 4,500 mm^2 | 74 / 4,500 | 0.016 MPa vs gypsum 2-5 MPa; not governing |
| Overturning couple from V at stand-off h = 30 mm | M = 74 x 30 = 2,220 N.mm over 50 mm from pad bottom edge to upper screw | 44 N tension on the upper screw |
| Shear per screw, 2 screws | 74 / 2 | 37 N vs 350 N: D/C 0.11 |
| Tension per screw | 44 N vs 530 N | D/C 0.08 |
| Linear sum | 0.11 + 0.08 | **0.19** (< 0.3 target) |
| Friction credit | mu 0.3 x 74 = 22 N | not relied on |

Spec: pad **>= 75 mm wide x 60 mm tall**, flat, at the wall datum (z = 0), stand-off <= 30 mm; **two #10 x 2.5 in stud screws** (>= 38 mm in the stud), stacked vertically 40 mm apart, 5.5 mm clearance holes with 16 mm washer seats, >= 20 mm solid depth. Pad centred on a stud line (stud 38 mm wide) or on the cleat bar extension (the bar is stud-fastened). **Not permitted** on bare drywall: toggle shear 250 N, 74/250 = 0.30 plus tension 44/150 = 0.29 gives 0.59, no margin on wet-cycle gypsum.

Placement flag for CAD: longest shelf foot sits ~300-350 mm below the shelf, centre x on a stud line at 406 mm OC. Stud positions are unknown (Evan open question). Foot x must be adjustable, or the foot bar is a cleat extension.

## 3. (c) Shelf arm (limb) min I

### 3.1 Loads

M(p) = W p + W_self p/2, W = 73.6 N at the tip (bounding case, load-model Section 3), W_self = 9.81 N (1.0 kg arm). Design as cantilever-only; strut is NOT credited (redundant load path if the strut is ever not installed or fails).

| p (mm) | M (N.m) | Z_req = M / 7 MPa (mm^3) | solid d from stress (mm) |
|---|---|---|---|
| 200 | 15.7 | 2,243 | 28.4 |
| 250 | 19.6 | 2,804 | 30.6 |
| 290 | 22.8 | 3,252 | 32.1 |
| 300 | 23.6 | 3,364 | 32.5 |

Stress is not governing. Stiffness is.

### 3.2 Creep sag governs

Unfactored tip load 49 N (5 kg) + self-weight 9.81 N distributed. E_lt = 640 MPa. Criterion: long-term tip sag <= L/50 (6 mm at 300 mm; slope ~1.7 deg, a pot tilts but does not slide). delta = P L^3 / (3 E I) + w L^4 / (8 E I).

I_req (p = 300) = (49 x 2.7e7 / 3 + 9.81 x 300^3 / 8) / (640 x 6) = **1.24e5 mm^4**. p = 250: 8.6e4. p = 200: 5.5e4.

Take the p = 300 value for all three arms (single spec, arm lengths may grow).

| Check at solid d = 40 mm (I = 125,664 mm^4, Z = 6,283 mm^3) | Value |
|---|---|
| sigma at p = 300, M = 23.6 N.m | 3.7 MPa vs 7 MPa |
| Sag, long-term (E_lt) p = 200 / 250 / 290 / 300 | 1.7 / 3.4 / 5.3 / 5.9 mm |
| Sag, short-term | 0.7 / 1.4 / 2.1 / 2.4 mm |
| Tip slope, long-term, p = 300 | 1.7 deg |

### 3.3 Spec

- **I >= 1.2e5 mm^4 about the horizontal axis (vertical load), at the wall root**, held constant to **x = 0.5 p**, then free to taper toward the shelf tip (moment falls linearly; tip fibres and plate stiffen it). Build rule: no section within 0.5 p of the root smaller than the root spec.
- **Z >= 3,400 mm^3** (stress).
- **Solid core diameter >= 40 mm** (I = 125,664). Hollow equivalent: I >= 1.2e5 and wall >= 3.0 mm (e.g., 50 mm OD x 4 mm wall, I = 154,000).
- Lateral (vertical-axis) I >= 0.3 x root I for side knocks.
- Print: arm axis in XY, shelf top face down on the bed, tension (top) face parallel to the layers (load-model Section 3). No layer interface across the root tension face.
- Wrap is not credited; core must be continuous through the root into the body spine (>= 8 mm through-spine already required by mesh-spec Section 3).
- Prior check: the load-model 80 x 60 x 1.2 mm box (I = 2.04e5) exceeds this; v1 numbers stand.

Longest arm (p = 290, buttress present): same spec; the strut only reduces the shelf-root anchor tension from 295 to ~92 N. For p = 250 (no strut in fullpiece arrangement A): cantilever-only anchor check at s = 100 mm: T = (73.6 x 0.25 + 1.2) / 0.1 = 196 N, 2 upper screws = 98 N each, D/C 0.19. Passes with 2 screws per row. DECISIONS 2026-11-15 approves a buttress at >= 25 cm but studs + cleat pass without it, so a strut on the 250 mm shelf is optional (CAD aesthetic call), not a structural need. mesh-spec Section 0 "required at p >= 250 mm" should read "required at p > 250 mm or on a drywall-only mount".

## 4. (d) Fullpiece v1 mass proxy and mount

Source: `teams/cad/fullpiece/engineering_checks.json` hero: V = 17,452 cm^3 solid, 22.16 kg at 1.27 g/cm^3. Seat embed 16 mm (spec 25 mm).

### 4.1 Realistic shelled mass

| Component | Low | Nominal | High | Assumption |
|---|---|---|---|---|
| Shell + infill of the mesh volume | 4.9 kg | 6.9 kg | 9.3 kg | retained fraction 0.22 / 0.31 / 0.42 of 22.2 kg solid. Bulk relief (T ~50 mm, surface area factor 2.5 front + 1 back, A/V ~ 70 /m) x 1.35 mm shell = 9.5% + 10% gyroid on the rest = 18.5%; thin features (ribs 9-30 mm, whips, fibres, ~40% of volume) retain ~50% |
| Seat blocks at 25 mm embed, 3 x 160 x 150 mm solid | +1.0 | +1.5 | +2.2 | net of what the retained fraction already counts |
| Strut core + arm cores (24 x 3 tube, 8 mm steel rod; 3 x 40 mm solid x 150 mm) | +0.5 | +0.8 | +1.2 | Section 2, 3 |
| Cleat bars, 3 x Al 6 x 50 x 450 mm | +0.5 (printed alt) | +1.1 | +1.1 | wall-side hardware, counted because it hangs |
| Fasteners, inserts, splice straps, adhesive, finish | +0.5 | +1.0 | +1.5 | load-model Section 2 range |
| **Total** | **7.4 kg** | **11.3 kg** | **15.3 kg** | |

Load model 5-14 kg, nominal 9 kg: consistent. The 22 kg proxy overstates the print by roughly 2x. Nominal 11 kg sits under the 14 kg cap; **the high case (15 kg) exceeds the cap**, so the cap needs enforcing from the real hollowed mesh. Mass is not a valid number until the print-res pass hollows it.

### 4.2 Mount

Anchors: 3 cleat bars x 4 stud screws (2 upper, 2 lower) + 2 hold-downs = 14 screws, sculpture shear shared over the 12 cleat screws with 2x peaking. Worst shelf anchor: p = 300 tip load, s = 80 mm, T = 295 N per row, 148 N per upper screw (2 per row). Shelf shear 83 N / 4 = 21 N per screw.

| Case | Sculpture shear per screw (1.2 x W / 12 x 2) | Combined D/C, upper screw (148 / 530 + shear / 350) |
|---|---|---|
| 14 kg cap | 28 N | 0.28 + (21 + 28) / 350 = **0.42** |
| 22 kg proxy | 43 N | 0.28 + 64 / 350 = **0.46** |
| 15.3 kg high | 30 N | 0.28 + 51 / 350 = 0.43 |

Mount passes at 14 kg and at 22 kg. The proxy is a mass-reporting problem, not a mount problem. Conditions: (i) 2 screws per row, both rows, each bar must capture at least one stud (a 450 mm bar always crosses >= 1 stud at 406 mm OC; load-model's "spans two studs" holds only when aligned), (ii) with 1 screw per upper row D/C rises to 0.56 + 0.14 = 0.70 (still passes), (iii) seat embed to 25 mm before print (16 mm does not hold the lip pocket + retaining-screw boss + 25 mm screw clearance), (iv) overturning from body COM at 50 mm: 14 kg x 9.81 x 0.05 = 6.9 N.m over 0.6 m rows = 11 N. Negligible. (v) Fullpiece headroom violation (S3 clearance ~160 mm vs 300 mm) is aesthetic/usable-plant and is CAD's, not structural; no load effect.

## 5. Open items

1. Coupon test (one 24 x 3 tube, one 40 mm arm section, PETG in Fabrication's chosen material) for E and creep. All E and creep factors here are [GENERAL] and unmeasured. This is a precondition to freezing the numbers beyond PROVISIONAL.
2. CAD reports limb wrap mass and the min core cover along the sculpt (validator: core centreline, I along length, exclusion zones for pockets).
3. Evan: stud map; room temperature near the wall (derate x 0.25 at 40 C raises strut I to ~17,500 and arm I to ~2e5).
4. Fabrication: segment plan for the 8 mm rod splice; printed vs aluminum cleat.
5. fullpiece_v2 review of mass and hard-points (RP-2 item 3 asks for v2): pending delivery of the mesh.

## 6. Assumptions table (single list)

| ID | Assumption | Value | Status |
|---|---|---|---|
| A1 | Factored plant load at tip | 73.6 N | DECISIONS 2026-11-15 |
| A2 | Strut axial / horizontal at 45 deg | 104 / 74 N | load-model-v1 |
| A3 | E_xy short, printed PETG/ASA | 1,600 MPa | [GENERAL], unmeasured |
| A4 | Creep factor 10 yr, 23 C | 0.40 (E_lt 640 MPa); 0.25 at 40 C | [GENERAL], unmeasured |
| A5 | Sustained stress allowable | 7 MPa | load-model-v1 |
| A6 | L_eff / chord | 1.1, pinned-pinned | judgement |
| A7 | Imperfection / end eccentricity | L_eff / 150 ; 10 mm | judgement, CAD must hold |
| A8 | Buckling factor, creep modulus vs factored load | 2.5 | judgement |
| A9 | Arm sag criterion | L / 50, long-term | judgement |
| A10 | Arm self-mass / strut-limb mass | 1.0 kg / 0.6 kg | assumption until CAD mass report |
| A11 | Stud screw capacities | 530 N tension, 350 N shear | load-model Section 4 |
| A12 | Mass retention fractions | 0.22 / 0.31 / 0.42 | judgement, replace with sliced mesh |

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-16 | structural-lead | Initial creation: RP-2 item 3 (blind-pocket verdict, one strut spec, limb min I, mass check) | docs-reviewer (verified: same calcs as STATUS row, sections 2.2, 2.3, 2.7, 3.2 recomputed; assumptions table A1-A12 present. Body status tag cleared. Prose in s.6 item 1 ("precondition to freezing the numbers beyond PROVISIONAL") is about coupon-test status of E/creep, left as written) |
