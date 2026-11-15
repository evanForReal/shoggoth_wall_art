# VALIDATION - sim/ (voxel-hex FEA + analytic frame) (2026-11-15)

**Solver choice:** voxel-hex Q1 (cubic cells, 2x2x2 Gauss) built from a signed-winding raster of the STL; solved by CG preconditioned with an in-repo smoothed-aggregation AMG (sim/amg.py). Reason: no mesher (gmsh) and no direct sparse solver beyond SuperLU (SuperLU needed >2 min for a 146k-dof shell, so unusable); a cavity-correct raster is robust for any closed mesh. Cost: O(h) staircase error on curved boundaries, so thin walls need >= 2 cells through the wall (h <= wall/2).

**Verdict: NOT VALIDATED** (tolerance 5 % on tip deflection and first frequency vs closed form, at the finest tested h with h/wall <= 0.5 for hollow cases). Total runtime 689 s.

Closed forms: Timoshenko cantilever (Euler-Bernoulli + shear with Cowper kappa), f1 = 1.8751^2/(2 pi L^2) sqrt(EI/(rho A)) (Euler-Bernoulli, no shear/rotary correction; adds a few % for L/D~6), tapered case by quadrature of exact I(x).

Load = tip force 100 N spread over tip-face nodes; clamp = all dofs on the first node layer at the root face (3-D clamp includes Poisson/warping restraint, expected +1..3 % stiffness vs beam theory). Stress column: axial stress of outermost element at mid-span vs M*z/I evaluated at that element's centroid height.

## Summary
| case | h used | tip delta err % | f1 err % | mid-span stress err % | pass |
|---|---|---|---|---|---|
| hollow_tube_OD40_t2.4_L240 | 0.8 | -0.86 | -4.83 (h=1.2) | +0.01 | True |
| tapered_hollow_noplate_L300_D60-30 | 0.9 | +0.33 | n/a | n/a | True |
| solid_square_20x20_L100 | 0.8 | -1.95 | -1.71 (h=1.25) | -0.14 | True |
| solid_round_D24_L150 | 0.75 | -3.36 | +1.42 (h=1.5) | -1.60 | True |
| hollow_tube_OD40_t2.4_L400 | 1.2 | -1.26 | n/a | -0.80 | False |

## Mesh-convergence study (error vs closed form)

### hollow_tube_OD40_t2.4_L240
closed form: tip delta = 4.7926 mm (bending 4.5802), f1_EB = 162.40 Hz

| h mm | cells | dof | CG its | delta FE mm | err % | f1 FE Hz | f1 err % | sigma err % |
|---|---|---|---|---|---|---|---|---|
| 2.4 | 5000 | 34542 | 1387 | 4.7929 | +0.01 | 112.28 | -30.86 | -0.37 |
| 1.6 | 17250 | 94677 | 246 | 4.6260 | -3.48 | 154.66 | -4.76 | -3.21 |
| 1.2 | 39800 | 194769 | 201 | 4.7555 | -0.77 | 154.55 | -4.83 | -0.21 |
| 0.8 | 133500 | 571599 | 343 | 4.7511 | -0.86 | n/a | n/a | +0.01 |

### tapered_hollow_noplate_L300_D60-30
closed form: tip delta = 4.4628 mm (bending 4.2173)

| h mm | cells | dof | CG its | delta FE mm | err % | f1 FE Hz | f1 err % | sigma err % |
|---|---|---|---|---|---|---|---|---|
| 2.4 | 6990 | 49098 | 98 | 4.7128 | +5.60 | n/a | n/a | n/a |
| 1.6 | 23600 | 133938 | 100 | 4.6254 | +3.64 | n/a | n/a | n/a |
| 1.2 | 55980 | 280230 | 89 | 4.5591 | +2.16 | n/a | n/a | n/a |
| 0.9 | 132504 | 596676 | 92 | 4.4775 | +0.33 | n/a | n/a | n/a |

### solid_square_20x20_L100
closed form: tip delta = 1.2896 mm (bending 1.2500), f1_EB = 405.44 Hz

| h mm | cells | dof | CG its | delta FE mm | err % | f1 FE Hz | f1 err % | sigma err % |
|---|---|---|---|---|---|---|---|---|
| 5.0 | 320 | 1575 | 0 | 1.2063 | -6.46 | 407.47 | +0.50 | +0.79 |
| 2.5 | 2560 | 9963 | 0 | 1.2490 | -3.15 | 400.59 | -1.20 | +1.39 |
| 1.25 | 20480 | 70227 | 26 | 1.2616 | -2.17 | 398.52 | -1.71 | +0.95 |
| 0.8 | 78125 | 255528 | 24 | 1.2645 | -1.95 | n/a | n/a | -0.14 |

### solid_round_D24_L150
closed form: tip delta = 3.5042 mm (bending 3.4539), f1_EB = 187.26 Hz

| h mm | cells | dof | CG its | delta FE mm | err % | f1 FE Hz | f1 err % | sigma err % |
|---|---|---|---|---|---|---|---|---|
| 3.0 | 2600 | 10557 | 0 | 3.1517 | -10.06 | 191.67 | +2.36 | -6.89 |
| 1.5 | 20800 | 73023 | 50 | 3.2095 | -8.41 | 189.92 | +1.42 | -6.24 |
| 1.0 | 67650 | 226500 | 59 | 3.4411 | -1.80 | n/a | n/a | -0.58 |
| 0.75 | 162400 | 528831 | 48 | 3.3864 | -3.36 | n/a | n/a | -1.60 |

### hollow_tube_OD40_t2.4_L400
closed form: tip delta = 21.5585 mm (bending 21.2045), f1_EB = 58.46 Hz

| h mm | cells | dof | CG its | delta FE mm | err % | f1 FE Hz | f1 err % | sigma err % |
|---|---|---|---|---|---|---|---|---|
| 2.4 | 8350 | 57456 | 2000 | 21.3964 | -0.75 | 54.65 | -6.52 | -1.39 |
| 1.6 | 28750 | 157377 | 381 | 20.7353 | -3.82 | 57.21 | -2.15 | -3.48 |
| 1.2 | 66267 | 323646 | 331 | 21.2879 | -1.26 | n/a | n/a | -0.80 |

## Not validated (honest scope)
- Stress concentrations at plate/stub/rib junctions and at joints (voxel stair-step peaks are mesh-dependent; use as indicators, check convergence per model with `--pitch`).
- Orthotropic FDM behaviour: FEA is isotropic with E_xy; layer-direction awareness is applied only to the allowable (failure index), not to stiffness.
- Anchor/screw loads from the FEA screws-only support are a no-contact upper bound; compared to hand calc in the cross-check.
- Frame (analytic) module validated against the same closed forms in sim/analytic/validate_frame (see below).

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-15 | verif-fea (generated) | validation run | [PROVISIONAL] |
