# analytic_geometry_prelim — Geometry region hand calcs (PRELIMINARY, shell-only)

Scope: plausibility of default params before FEA. Shell-only section (ribs/plugs neglected = conservative), thin-wall Bredt torsion, unit-load deflection, E=2000 MPa PETG. Skin counted at 80 % solid. NOT the Verification analytic report. Owner: geometry-manager. [PROVISIONAL: unsigned]

Weights: underlay 15.1 N (1.54 kg), skin 4.9 N (0.50 kg eff.). LC1 plant 49.1 N at shelf center (259,270,84).

## Section stress along span (LC1 5 kg, LC2 15 kg), von Mises = sqrt(sigma^2+3 tau^2), MPa

| s | I_N mm4 | M_N (LC1) N.m | M_T (LC1) N.m | vm LC1 | vm LC2 | allow LC1 (18/3) | allow LC2 (18/1.5) | min SF LC1 | min SF LC2 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 8.77e+05 | 11.6 | -15.5 | 1.00 | 2.68 | 6.0 | 12.0 | 18.1 | 6.7 |
| 40 | 7.41e+05 | 13.6 | -11.3 | 1.06 | 2.85 | 6.0 | 12.0 | 17.0 | 6.3 |
| 80 | 6.2e+05 | 13.9 | -7.5 | 1.10 | 2.97 | 6.0 | 12.0 | 16.4 | 6.1 |
| 120 | 5.12e+05 | 13.1 | -3.7 | 1.10 | 2.99 | 6.0 | 12.0 | 16.4 | 6.0 |
| 151 | 4.38e+05 | 11.7 | -0.8 | 1.07 | 2.93 | 6.0 | 12.0 | 16.8 | 6.1 |
| 200 | 3.37e+05 | 8.8 | 1.3 | 0.97 | 2.66 | 6.0 | 12.0 | 18.6 | 6.8 |
| 250 | 3.8e+05 | 6.0 | 0.7 | 0.53 | 1.46 | 6.0 | 12.0 | 34.1 | 12.3 |
| 302 | 7.1e+05 | 3.2 | 0.0 | 0.14 | 0.40 | 6.0 | 12.0 | 126.1 | 45.1 |
| 340 | 7.1e+05 | 1.2 | -0.0 | 0.05 | 0.14 | 6.0 | 12.0 | 347.0 | 128.3 |
| 380 | 7.1e+05 | 0.1 | -0.0 | 0.00 | 0.00 | 6.0 | 12.0 | 5875.9 | 5875.9 |
| 420 | 7.1e+05 | 0.0 | -0.0 | 0.00 | 0.00 | 6.0 | 12.0 | 29627.0 | 29627.0 |

Worst section SF (interlayer allowable 18 MPa, no stress concentration): LC1 16.4 (need >=3), LC2 6.0 (need >=1.5).

## Tip/shelf deflection and frequency (LC1, shell-only EI/GJ)

- Shelf-point deflection from plant 5 kg: 0.68 mm (bending 0.51, torsion 0.17); self-weight 0.10 mm; total 0.78 mm (limit 6).
- Stiffness at shelf k = 72.0 N/mm. f1 (Rayleigh, m_eff = plant + 0.24 m_span) = 18.2 Hz; without plant 61.0 Hz (limit 8).

## Anchor plate screws (4x d6 holes, 120x70; plate pivots on bottom edge, tension-only)

- LC1 (plant 5 kg + self weight): M_x -15.6 N.m, M_y 15.7 N.m, V 69 N; peak screw tension 148 N, shear 17 N each.
- LC2 (15 kg): peak screw tension 393 N, shear 42 N each.
- LC5 rating: spec drywall anchor >= 25 kg = 245 N tension each -> LC2 peak 393 N: FAIL (needs stud/lag or larger pattern). #8 wood screw into stud, ~25 mm embed in SPF: withdrawal ~ 400 N conservative -> ok vs LC2 only if screws land in stud.
- Pattern issue: 120 mm horizontal spacing cannot hit one 38 mm stud face; at 406 mm stud spacing at most one column of two screws is in a stud. Recommend Verification evaluates (a) 4 screws all in anchors/blocking, (b) a French-cleat with 300+ mm width. Flag to Evan only if blocking is not available.

## Other plausibility notes

- Shell local buckling (thin cylinder, classical 0.6 E t/r, r~40, t=2.4): ~72 MPa, knockdown 0.2 -> 14 MPa >> applied (<3 MPa). OK.
- Shelf deck: 124 mm wide top, webs at n=0,+-32, rings at 30 mm -> panel ~32x30x2.4: plate bending under 15 kg < 1 MPa. OK.
- Peak moment at the root/neck (s~0-60); joint cuts (s=151, 302) see lower M. Joint section = shell + 8/16 mm solid plug; bolt/pin/key stresses are Verification's.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-15 | geometry-manager | Initial hand calcs | [PROVISIONAL] |
| 2026-11-15 | independent-geometry-reviewer | section-stress table confirmed (<1 %, see geometry_review.md); anchor-screw section NOT confirmed (Mx wrongly added to tension) | author:geometry-manager |
