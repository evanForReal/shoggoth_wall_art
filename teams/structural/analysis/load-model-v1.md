# Load Model v1 — Structural Engineering Pass

**Status:** [PROVISIONAL] first pass. Hand calcs, no FEA. Geometry basis: r04 c01 (velvet-salon baseline) and c02 (stone-smile), ~3x2 to 3x3 ft. Inputs from liaison v2 (STATUS.md). SI units throughout; g = 9.81 m/s^2.

## 0. Exec summary

1. Shelf cantilevers dominate. Worst per-anchor tension is ~295 N (factored, p = 30 cm, s = 8 cm, load at tip). Sculpture self-weight is a minor shear load (<= 64 N per anchor at N = 6, before peaking).
2. Nails (sketch baseline) fail. Single drywall toggles fail at p = 30 cm. Screws into studs through an aluminum or PETG cleat pass with margin (D/C 0.3-0.7). Drywall-only wall needs paired upper toggles plus a brace.
3. Under-shelf compression strut (buttress tentacle) beats a cable assist: cuts worst upper-anchor tension from 295 N to ~92 N (about 3x), and does not intrude on plant headroom. The strut still pushes the shelf outward with 74 N horizontal thrust, which the shelf-root anchors must resist in tension; the strut foot needs its own wall anchorage (Section 6).

Needs from others: CAD mass model (real mesh), Evan wall-construction answer (Section 8).

## 1. Assumptions

| Item | Value | Basis |
|---|---|---|
| Plant+pot+wet soil per span | 5 kg | Liaison v2 upper bound (2-5 kg) |
| Safety factor, plant load | 1.5 | Mission brief |
| Factored plant load W | 5 x 9.81 x 1.5 = **73.6 N** | |
| Shelf protrusion p | 0.10, 0.20, 0.30 m | Liaison v2 / brief |
| Nominal load centroid | x_c = 0.5 p | Pot spans 0 to p, or sits centered on a deeper shelf |
| Bounding load centroid | x_c = p (load at tip) | Conservative envelope; physically unreachable at p = 10 cm for a 5 kg pot (base ~15 cm), reachable at 20-30 cm |
| Shelf tentacle self-mass | 1.0 kg each, centroid at p/2, SF 1.0 | Part of the sculpture mass in 1b; assumption until CAD mass model |
| Anchor pair | upper = tension T, lower = bearing C, vertical spacing s = 0.08-0.12 m | Brief |
| Load path | each shelf carried by its own anchor pair; body stiffness redistribution NOT credited | Conservative |
| Dynamic / impact | not covered by SF 1.5 beyond watering overshoot; bumps, leaning, children not modelled | Flag |

Wall-bearing contact: moment is resolved as a couple. Upper anchor pulls out (T), lower contact edge pushes in (C), T = C = M / s. Vertical load V is shared by the anchors in shear/friction.

## 2. Load case (b): sculpture self-weight

Method (no mesh yet):

- Projected area A_p ~ 1.0 m^2 (3x3 ft = 0.84 m^2, rounded up; 3x2 = 0.56 m^2).
- Printed surface area A_s = 2-3 x A_p. Relief has a front skin, side walls, fenestrated lattice and internal ribs; c01/c02 are heavily fenestrated.
- Shell: 2-3 perimeters x 0.45 mm = 0.9-1.35 mm. PETG/PLA density 1240-1270 kg/m^3, x0.95 for printed void fraction.
- Infill 10-15% in the solid fraction only: enclosed solid volume V_s = 0.02-0.04 m^3 (mean depth 5-8 cm over 0.4-0.5 m^2 of solid mass).
- Finish coat + hardware + mask: 0.5-1.5 kg.

| | Low | High |
|---|---|---|
| Shell: A_s x t x rho | 2 m^2 x 0.9 mm x 1180 = 2.1 kg | 3 m^2 x 1.35 mm x 1270 = 5.1 kg |
| Infill: V_s x fill x rho | 0.02 x 0.10 x 1200 = 2.4 kg | 0.04 x 0.15 x 1270 = 7.6 kg |
| Finish + hardware | 0.5 kg | 1.5 kg |
| **Total** | **5.0 kg** | **14.2 kg** |

**Sculpture mass: 5-14 kg, nominal ~9 kg.** Weight 49-139 N (nominal 88 N). Segment joints, inserts and bonding add ~5-10%; not included.

Total installed (unfactored) = 9 kg + 3 x 5 kg = ~24 kg nominal, up to 29 kg.

Distribution over the anchor set. Dead-load factor 1.2 on sculpture; shelves at factored 73.6 N each (220.8 N). Total vertical demand V_tot:

| Sculpture mass | 1.2 x weight | V_tot (incl. 220.8 N shelves) | N = 6 | N = 8 | N = 10 |
|---|---|---|---|---|---|
| 5 kg | 59 N | 280 N | 47 N | 35 N | 28 N |
| 9 kg | 106 N | 327 N | 54 N | 41 N | 33 N |
| 14 kg | 165 N | 386 N | 64 N | 48 N | 39 N |

Per-anchor shear, even split. Apply 2x peaking for stiffness mismatch and hole tolerance: worst ~130 N (N = 6, 14 kg).

Body overturning: body centroid offset from wall d ~ 0.05 m. M = 137 N x 0.05 = 6.9 N.m (14 kg, unfactored). Anchor rows ~0.6 m apart: T = 6.9 / 0.6 = **11 N** total. Negligible next to shelves.

## 3. Load case (a): plant-shelf cantilever

Per shelf: M = W x x_c + W_self x (p/2), W = 73.6 N, W_self = 1.0 x 9.81 = 9.81 N.

| p (m) | M nominal (x_c = p/2) | M bound (x_c = p) |
|---|---|---|
| 0.10 | 73.6 x 0.05 + 9.81 x 0.05 = 4.17 N.m | 73.6 x 0.10 + 0.49 = 7.85 N.m |
| 0.20 | 73.6 x 0.10 + 9.81 x 0.10 = 8.34 N.m | 73.6 x 0.20 + 0.98 = 15.7 N.m |
| 0.30 | 73.6 x 0.15 + 9.81 x 0.15 = 12.5 N.m | 73.6 x 0.30 + 1.47 = 23.6 N.m |

Anchor demand T = C = M / s (N):

| p (m) | s = 0.08 nom / bound | s = 0.10 nom / bound | s = 0.12 nom / bound |
|---|---|---|---|
| 0.10 | 52 / 98 | 42 / 79 | 35 / 65 |
| 0.20 | 104 / 196 | 83 / 157 | 70 / 131 |
| 0.30 | 156 / **295** | 125 / 236 | 104 / 196 |

Worked example (worst): M = 73.6 x 0.30 + 9.81 x 0.15 = 22.1 + 1.47 = 23.6 N.m; T = 23.6 / 0.08 = 295 N. (Unrounded: 23.55 / 0.08 = 294.4 N; 295 N used throughout.)

Shear per shelf: V = 73.6 + 9.81 = 83.4 N; 42 N per anchor. Resultant at worst upper anchor sqrt(295^2 + 42^2) = 298 N, ~T.

Lower bearing check (drywall, edge contact 150 mm x 10 mm = 1500 mm^2): 295 N / 1500 mm^2 = 0.20 MPa vs gypsum compressive ~2-5 MPa. OK. Needs a bearing pad; knife edge into paper face crushes first.

### Shelf root section (printed beam)

Thin-wall box, 80 x 60 mm outer, t = 1.2 mm: I = [80 x 60^3 - 77.6 x 57.6^3] / 12 = 2.04e5 mm^4, c = 30 mm.
sigma = M c / I = (23.6e3 N.mm x 30) / 2.04e5 = **3.5 MPa**.
- Short-term OK (PETG XY tensile ~40 MPa, interlayer ~15-20 MPa).
- Sustained: PLA allowable under creep ~5 MPa or less (Tg ~55-60 C); marginal. PETG/ASA ~ 7-10 MPa. Real roots are lattice, not box. Root needs equivalent section or internal spine.
- Tip deflection, P = 49 N unfactored, L = 0.30 m, E ~1800 MPa: delta = P L^3 / (3 E I) = 49 x 2.7e7 / (3 x 1800 x 2.04e5) = **1.2 mm**. Creep x2-3 over service life: ~3 mm. Acceptable.

Layer orientation: bending tension runs along tentacle axis. Print with tentacle axis in the XY plane. Never let layer interfaces sit across the root tension face.

## 4. Anchor options

Capacities are working values from typical published data and NDS-style formulas, rounded; not verified against a manufacturer sheet. Drywall: ultimate / 4. Demand = factored, worst case (T = 295 N, V per anchor 42 N; nominal case in parentheses).

| Option | Working capacity per anchor | D/C, worst (nominal) | Verdict | Failure mode to watch |
|---|---|---|---|---|
| Nail (8d, 1.5 in in stud), sketch baseline | Tension ~140 N (withdrawal, NDS 1380 G^2.5 D x 1.5 in); shear ~300 N | 2.1 (0.9) | **FAIL** | Withdrawal under sustained tension and wall vibration; no positive lock |
| Drywall toggle (snap/strap class, 12.7 mm gypsum) | Tension ~150 N (ult 450-900 N / 4); shear ~250 N | 1.96 (0.83); paired uppers 0.98 | **Marginal.** Pass only p <= 20 cm with paired upper toggles, or with strut | Gypsum pull-through, paper-face crush, hole enlargement from cyclic loading |
| Stud screw (#10 x 2.5 in, >= 38 mm into SPF stud) | Tension ~530 N used (NDS W = 2850 G^2 D x 1.5 in: G = 0.42 gives 143 lbf = 636 N; 530 N corresponds to G ~0.38, conservative for softer SPF); shear ~350 N | 0.56 (0.24); with shear, linear-sum bound 0.68 | **PASS** | Missing the stud; stripped thread in splintered wood; stud pitch 406 mm limits freeform placement |
| French cleat, aluminum 6061 (6 x 50 mm bar, 450 mm long spans 2 studs) | Governed by fasteners (above); bar bending/shear not critical | Upper pair of screws: 0.28-0.34 | **PASS, preferred** | Fastener pull-out; cleat hook disengagement if piece lifts (add retaining screw); thermal/galvanic nil indoors |
| French cleat, printed PETG/ASA (8-10 mm, metal washers) | Fastener-governed; pull-through 295 N / (181 mm^2 head annulus) = 1.6 MPa; layer shear 295 N / (pi x 16 mm x 8 mm = 402 mm^2) = 0.73 MPa vs ~15 MPa | Strength < 0.1; creep governs | **PASS with PETG/ASA/nylon.** PLA not recommended | Print-layer shear along tongue (print cleat on edge so layers run along the tongue); creep and heat; PLA loses stiffness near 50 C (sunlit wall, lamp) |
| Masonry sleeve/wedge, 6 mm | Tension ~800 N | 0.37 | PASS | Edge distance, spalling; only if wall is masonry |

Fabrication intel check: DECISIONS.md and review/rounds/round-03/manifest.json contain NO material-selection intel for load-bearing parts (only a "hand-painted PLA finish" aesthetics note). The PETG/ASA/nylon call above is this team's engineering judgment on creep and glass-transition; Fabrication to confirm. PLA acceptable for non-load-bearing skin.

Cleat geometry note: 45 degree cleat lip resists pull-out on the piece but does not resist moment alone. Moment is resolved by upper fastener tension and lower edge bearing, so the cleat must be fastened at both rows. Seat the lower edge against the wall on a bearing pad.

## 5. Multi-anchor freeform spread (6-10 points)

- Spreading reduces **shear and body share** per anchor (Section 2 table: 28-64 N at N = 6-10). It does NOT reduce shelf tension; that stays local to each shelf root pair.
- To cut shelf tension, add anchors at the shelf root: 2 upper + 2 lower per shelf halves T (295 N to ~148 N per upper anchor). More effective than adding remote hold-downs.
- Body hold-downs (2 shown in diagram) carry self-weight shear and anti-rotation. They also give a second load path for shelf moment through body stiffness. That is the upside not credited here; shelf root stiffness is unknown until the mesh exists.
- Wall-contacting tentacle terminations: use as locator/bearing pads (compression only, adhesive or one screw). They stop the piece rocking out of plane and kill vibration. Do not rely on them in tension.
- Stud pitch 406 mm OC: anchor x-positions snap to studs. Shelves A and C (left side) can share one vertical stud line. Aluminum cleat >= 450 mm spans two studs and decouples art layout from stud layout.
- Anchor count: recommended **8** (6 shelf + 2 hold-down). Raise to 10 if shelf roots get 2 + 2.

### Whip tentacles (decorative, no load path)

Example 20 mm OD, 1.2 mm wall, L = 0.40 m, mass ~40 g: I = pi/64 (20^4 - 17.6^4) = 3144 mm^4.
- Self-weight tip deflection: w L^4 / (8 E I), w = 0.001 N/mm: 0.001 x 400^4 / (8 x 1800 x 3144) = 2.56e7 / 4.53e7 = 0.6 mm. Fine.
- 10 N hand load at tip: delta = 10 x 0.4^3 / (3 E I) = 38 mm; sigma = 10 x 400 x 10 / 3144 = **12.7 MPa**. Interlayer failure risk.
- Rule: whips are never hooks, handles or shelves. Add a keep-off note to the build sheet. Core with 3 mm carbon or steel rod only if the whip reaches a high-traffic zone.

## 6. Tensegrity / cable assist (r03 f11 liked)

Cable from shelf tip up and back to a wall anchor at angle theta above horizontal.

- Cable tension Tc = P / sin(theta). P = 73.6 N, theta = 45 degrees: Tc = 104 N. Wall anchor sees 73.6 N out-of-wall (tension) + 73.6 N down.
- Shelf-root couple vanishes when the cable carries the full tip load. Residual: self-weight only, 1.47 N.m / 0.08 m = 18 N. Total demand shifts to cable anchor, 74 N (D/C 0.5 on a toggle).
- 1.5 mm 7x7 stainless: stretch = 104 N x 0.42 m / (88 kN) = 0.5 mm. Break ~1.7 kN; ratio ~16. Needs turnbuckle pretension or it shares load poorly with the cantilever.
- **When worthwhile:** drywall-only wall; p >= 25 cm; s <= 8 cm; or any case where stud placement cannot be reached. Not needed with studs + cleat.
- **Conflict:** the cable rises through the plant's headroom above the tip. Liaison v2 requires protrusion clear of vertical obstruction. A steep cable (theta = 70 degrees, Tc = 78 N, 27 N horizontal pull) hugs the outer pot edge but still intrudes.
- **Alternative: compression strut under the shelf** (a buttress tentacle; foot on the wall 0.30 m below the shelf, tip end under the shelf at p = 0.30 m, L = 0.42 m, 45 degrees). Statics: axial 104 N; vertical component 73.6 N carries the tip load, horizontal component 73.6 N. At the tip the strut pushes the shelf outward 73.6 N, so the shelf-root anchors must pull inward with 73.6 N. Plus the residual self-weight couple 18 N: worst upper-anchor demand ~74 + 18 = **92 N** (conservatively all on the upper anchor), versus 295 N cantilever-only. That is ~3x lower, not elimination. D/C: stud screw 92/530 = 0.17, drywall toggle 92/150 = 0.61.
- **Strut-foot anchorage:** foot is pushed into the wall with 73.6 N horizontal (bearing, no pull-out) plus 73.6 N vertical shear down. Needs a bearing pad plus a shear-capable fastener (one stud screw or toggle, D/C < 0.3) so the foot cannot slip. Prefer foot on a stud line or on the cleat.
- **Strut member:** tube 20 mm OD x 1.2 mm, pinned ends: P_cr = pi^2 E I / L^2 = 9.87 x 1800 x 3144 / 424^2 = 311 N, factor 3.0 on the already-factored 104 N. Aesthetically native (reads as another tentacle). Upsize the tube for margin.
- Cable stays an option for the "webbing" look (f11): thread through lattice voids, keep as secondary.

## 7. Conclusions

1. Shelf moment sets anchor design: T = 295 N worst. Self-weight is secondary (<= 64 N per anchor shear, 11 N total overturning tension).
2. Use stud-fastened French cleat (aluminum preferred, PETG/ASA printed acceptable) per shelf; nails and single toggles do not pass.
3. Add an under-shelf strut for p >= 25 cm or any drywall-only mount. It cuts worst upper-anchor demand about 3x (295 N to ~92 N: 74 N strut thrust + 18 N self-weight couple) but does not remove pull-out; the shelf-root anchors still resist the strut's horizontal thrust.

## 8. Open questions

**For CAD (mass model from real mesh):**
- Mass, COM and per-shelf-tentacle mass from the mesh (replaces 5-14 kg and 1.0 kg guesses).
- Shelf-root cross-section at the wall; can it hold the 3.5 MPa box equivalent or a spine?
- Hard-point flats at each shelf root: cleat seat, two rows at s = 8-12 cm, 150 mm wide min, with bearing pad zone.
- Segment joints kept off shelf roots; through-spine (rod or bar) path from shelf root into body.
- Shelf top: flat footprint >= 150 mm x 150 mm and a drip lip/tray option.
- Underside route for the buttress tentacle.
- Mean and max relief depth to refine body overturning.

**For Evan:**
- Wall construction: drywall on stud, plaster/lath, or masonry/concrete? Biggest lever on anchor choice.
- Is drilling into studs acceptable (rental or finish constraints)? The sketch said nails; they fail here.
- Install location: stud positions known, or free placement?
- Plant weight: confirm 5 kg ceiling; any heavier planter (ceramic, 30 cm+)?
- Room environment: sun or heater near the wall (PLA creep)?
- Is an under-shelf buttress tentacle acceptable aesthetically in place of a cable?

## 9. Diagrams

- `side-profile-cantilever.svg`: side profile, protrusion variance, loaded shelf cantilever with W, T, C, dimensions.
- `front-anchor-map.svg`: front view anchor map over the c01 silhouette; load-bearing vs decorative tentacles.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-15 | structural-lead | Initial creation (engineering pass v1) | [PROVISIONAL] |
| 2026-11-15 | structural-lead | Rev after peer review: strut thrust statics (92 N not 18 N), strut-foot anchorage, NDS conversion (143 lbf = 636 N; 530 N used), 295 N rounding, D/C 0.56/0.68 with linear-sum rule, layer-shear area, SVG label | [PROVISIONAL] |
