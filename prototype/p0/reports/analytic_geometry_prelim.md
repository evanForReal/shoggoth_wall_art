# analytic_geometry_prelim — Geometry region hand calcs (PRELIMINARY, shell-only)

Scope: plausibility of default params before FEA. Shell-only section (ribs/plugs neglected = conservative), thin-wall Bredt torsion, unit-load deflection, E/rho/allowables from params.json materials. Skin counted at 80 % solid. NOT the Verification analytic report. Owner: geometry-manager. [PROVISIONAL: unsigned]

Weights: underlay 15.4 N (1.57 kg), skin 4.9 N (0.50 kg eff.). LC1 plant 49.1 N at shelf center (259,270,84).

## Section stress along span (LC1 5 kg, LC2 15 kg), von Mises = sqrt(sigma^2+3 tau^2), MPa

| s | I_N mm4 | M_N (LC1) N.m | M_T (LC1) N.m | vm LC1 | vm LC2 | allow LC1 (18/3) | allow LC2 (18/1.5) | min SF LC1 | min SF LC2 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 9.58e+05 | 11.6 | -15.5 | 0.97 | 2.59 | 6.0 | 12.0 | 18.7 | 6.9 |
| 40 | 7.63e+05 | 13.6 | -11.3 | 1.04 | 2.80 | 6.0 | 12.0 | 17.3 | 6.4 |
| 80 | 6.38e+05 | 13.9 | -7.5 | 1.08 | 2.90 | 6.0 | 12.0 | 16.7 | 6.2 |
| 120 | 5.28e+05 | 13.1 | -3.7 | 1.08 | 2.92 | 6.0 | 12.0 | 16.7 | 6.2 |
| 151 | 4.51e+05 | 11.8 | -0.8 | 1.05 | 2.85 | 6.0 | 12.0 | 17.2 | 6.3 |
| 200 | 3.46e+05 | 8.9 | 1.3 | 0.95 | 2.59 | 6.0 | 12.0 | 19.0 | 6.9 |
| 250 | 4.01e+05 | 6.1 | 0.7 | 0.50 | 1.39 | 6.0 | 12.0 | 35.8 | 12.9 |
| 302 | 7.29e+05 | 3.2 | 0.0 | 0.14 | 0.39 | 6.0 | 12.0 | 128.7 | 46.2 |
| 340 | 7.29e+05 | 1.2 | -0.0 | 0.05 | 0.14 | 6.0 | 12.0 | 352.4 | 131.2 |
| 380 | 7.29e+05 | 0.1 | -0.0 | 0.00 | 0.00 | 6.0 | 12.0 | 5451.1 | 5451.1 |
| 420 | 7.29e+05 | 0.0 | -0.0 | 0.00 | 0.00 | 6.0 | 12.0 | 26893.3 | 26893.3 |

Worst section SF (interlayer allowable 18 MPa, no stress concentration): LC1 16.7 (need >=3), LC2 6.2 (need >=1.5).

## Tip/shelf deflection and frequency (LC1, shell-only EI/GJ)

- Shelf-point deflection from plant 5 kg: 0.67 mm (bending 0.49, torsion 0.17); self-weight 0.10 mm; total 0.76 mm (limit 6).
- Stiffness at shelf k = 73.7 N/mm. f1 (Rayleigh, m_eff = plant + 0.24 m_span) = 18.4 Hz; without plant 61.4 Hz (limit 8).

## Anchor plate screws (4x d6 holes, 120x70) - UNDER REVISION, numbers only, NO verdict

Method: tension from My only (top-screw pull-out about a bottom pivot line; two pivot assumptions). Mx (torque about the wall normal) is carried in shear (V/4 + torsion share), not tension. The Verification region owns the corrected LC5 numbers and verdict; treat everything below as a hand-calc input, not a conclusion.

- LC1, pivot_plate_edge: M_y 15.8 N.m, M_x -15.7 N.m, V 69 N; peak screw tension 83 N; worst-screw shear (direct + torsion) 74 N.
- LC1, pivot_bottom_screws: M_y 15.8 N.m, M_x -15.7 N.m, V 69 N; peak screw tension 113 N; worst-screw shear (direct + torsion) 74 N.
- LC2, pivot_plate_edge: M_y 41.1 N.m, M_x -42.1 N.m, V 167 N; peak screw tension 218 N; worst-screw shear (direct + torsion) 193 N.
- LC2, pivot_bottom_screws: M_y 41.1 N.m, M_x -42.1 N.m, V 167 N; peak screw tension 294 N; worst-screw shear (direct + torsion) 193 N.
- Pattern issue (geometry fact): 120 mm horizontal screw spacing cannot land in one 38 mm stud face; at 406 mm stud spacing at most one column of two screws is in a stud. Options for Verification/Fabrication: blocking/anchors for all 4, or a wider French cleat.

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
| 2026-11-15 | geometry-fix-v1 | regenerated on v1 geometry; E/rho from params materials; anchor section rewritten (My-only tension, Mx in shear, no verdict; Verification owns LC5); edit log now preserved across runs | [PENDING] |
| 2026-11-15 | independent-v1-reviewer | confirmed/exceptions (see geometry_review_v1.md) | author:geometry-fix |
