# Mesh Specification v1 (engineering requirements)

**Status:** ACTIVE enabling work (RP-1 item 3). Derived from `teams/structural/analysis/load-model-v1.md` (hand calcs, no FEA) and DECISIONS rows 2026-11-14 (round-04) and 2026-11-15 (structural design case). Requires no final geometry. Values marked **[PROPOSED]** are CAD proposals with no verdict behind them; they need Aesthetics/Structural sign-off. Values marked **[GENERAL]** are standard FDM practice, not measured on Evan's printer.

Units: mm, N, kg. Wall datum: z = 0 is the finished wall plane; +z leaves the wall. Piece back plane sits at z = +6 mm (cleat bar thickness) except at bearing stand-offs (Section 3).

## 0. Exec summary

1. Every segment is a closed 2-manifold, consistent outward winding, no self-intersections, validated in code before release.
2. Wall thickness floors by material: structural load path >= 1.8 mm (PETG/ASA only); decorative skin >= 0.9-1.2 mm; lattice strands >= 2.0 mm (3.0 in or near the load path).
3. Three cleat hard-points (one per shelf): >= 150 mm wide flat seat, two fastener rows 80-120 mm apart, lower bearing pad >= 150 x 20 mm that reaches the wall datum. Segment joints kept >= 100 mm off each root.
4. Shelves: flat top >= 150 x 150 mm, protrusion 150-300 mm [PROPOSED], 300 mm of headroom clear of the footprint. Buttress limb required at p >= 250 mm (structural: >= 25 cm).
5. Relief depth targets [PROPOSED]: mean 60 mm over solid footprint (range 50-80), body max 120 mm, shelves 150-300 mm. Mass target 9 kg nominal, hard cap 14 kg.
6. Joint clearance starting value: 0.25 mm [PROPOSED] per side (slip), 0.15 mm per side (bonded). Calibrate on a coupon before any production print.

## 1. Mesh integrity (all segments, release gate)

| Requirement | Limit | Check |
|---|---|---|
| Watertight, 2-manifold (each edge shared by exactly 2 faces) | pass | `trimesh.is_watertight`, `manifold3d` import status `NoError` |
| Winding consistent, normals outward, positive volume | pass | `is_winding_consistent`, `volume > 0` |
| No self-intersection, no duplicate/zero-area faces | 0 | manifold3d round-trip + area test |
| Disconnected shells | 0 unintended | `split()`; floating islands rejected (except whip tips, listed) |
| Enclosed internal cavities | none (trapped support) | shell count of the inverse |
| Surface fidelity | chordal deviation <= 0.05 mm vs source field; no staircase > 0.1 mm | script |
| Triangle budget | <= 2.5M per segment | export gate |
| Interchange | binary STL for slicing, 3MF for assembly metadata; units mm | |
| Per-segment envelope | <= 230 x 230 mm in XY at print orientation, <= 240 mm Z | see enabling-v1 packing argument |

Each segment is validated alone AND the assembly is validated for seam closure (mating faces coincide within the joint clearance).

## 2. Minimum feature sizes (0.4 mm nozzle, 0.45 mm line width, 0.2 mm layer) [GENERAL + load-model basis]

Wall = n perimeters x 0.45 mm. Load model assumes 2-3 perimeters (0.9-1.35 mm) for shell mass and a 1.2 mm box for the shelf-root stress check (3.5 MPa).

| Feature | PLA | PETG | ASA |
|---|---|---|---|
| Min wall, decorative skin (no load) | 0.9 | 1.2 | 1.35 |
| Min wall, load path (shelf root, strut, cleat pocket, joint lands) | not permitted (creep, Tg 55-60 C) | 1.8 | 1.8 |
| Min lattice strand width, decorative | 1.5 | 2.0 | 2.0 |
| Min lattice strand width, in or near load path | not permitted | 3.0 | 3.0 |
| Min strand thickness in Z (layer-resolved) | 0.8 | 1.0 | 1.0 |
| Min through-void (webbing hole), smallest dimension | 4 | 6 | 6 |
| Min emboss/relief detail (crisp edges) | 0.8 | 1.0 | 1.0 |
| Max unsupported bridge | 30 | 20 | 15 |
| Overhang self-supporting (angle from vertical) | 50 deg | 45 deg | 40 deg |
| Whip tentacle min OD (decorative) | 14 | 16 | 16 |

Rationale: PETG strings and bridges worse than PLA; ASA warps and cracks on thin walls and long bridges, so floors rise. The 1.8 mm load-path floor (4 perimeters) is above the load model's 1.2 mm box check on purpose: thin-wall box at 1.2 mm reached 3.5 MPa vs ~7-10 MPa sustained allowable for PETG/ASA, but the real root is a lattice, not a box. Whips per load model Section 5: 12.7 MPa at 10 N hand load, so keep-off rule stands; strands below 1.5 mm will not survive handling or dusting.

Feasibility of the loved surfaces against this table: see `teams/fabrication/enabling-v1.md` Section 5. c01/c02 fine web strands (apparent 1-3 mm at 1 px ~ 1 mm scale) are at or below the floor and need thickening.

## 3. Cleat hard-points (3 shelf roots)

Basis: load model Section 4 (aluminum 6 x 50 mm French cleat, >= 450 mm long, spans two studs at 406 mm OC; PETG/ASA printed cleat acceptable) and open questions (flats, two rows s = 80-120 mm, >= 150 mm wide, bearing pad).

| Item | Requirement |
|---|---|
| Seat flat | >= 150 mm wide x 150 mm tall, planar +-0.5 mm, perpendicular to wall datum +-1 deg |
| Fastener rows | upper and lower rows, vertical spacing s = 80-120 mm (design to 100; D/C worst case at s = 80) |
| Embed depth | solid or >= 6 perimeters + 100% local infill, >= 25 mm deep behind the seat |
| Cleat interface | 45 deg lip pocket sized to a 6 x 50 mm bar [PROPOSED nominal; printed alt 8-10 mm] plus a retaining-screw boss (cleat-lift disengagement, load model Section 4); clearance per Section 7 |
| Bearing pad (lower edge) | >= 150 x 20 mm contact patch at the wall datum (z = 0) = 3000 mm^2 vs 1500 mm^2 minimum in load model (0.20 MPa on gypsum); 6 mm stand-off from the back plane so the lower edge bears on the wall while the cleat holds the back plane at +6 |
| Upper row | also a pad (compression only) to stop rocking |
| Tension face | layer interfaces never across the root tension face; tentacle axis in XY at print (load model Section 3) |
| Through-spine | root carries a path for a spine (rod/bar, >= 8 mm) running from the shelf root into the body, no segment joint on the path within 100 mm of the root |
| Section | root cross-section at the wall >= box-equivalent I = 2.04e5 mm^4 (80 x 60 outer, 1.2 mm wall) or spine-augmented equivalent |
| Alignment | root centerlines settable so seats land on a common vertical stud line pair (shelves A and C share one) |

Hold-down points (2) and wall-contacting terminations: compression-only pads >= 30 x 30 mm at the datum, flat, with an optional single-screw boss. Never tension-rated.

Segment joints: keep-out zone = root seat block + 100 mm margin all round [PROPOSED]. Also off the strut attach node (+75 mm) and the strut foot pad (+75 mm).

## 4. Shelf geometry

| Item | Requirement |
|---|---|
| Top surface | flat, planar +-1 mm, footprint >= 150 x 150 mm (pot base ~150 mm per load model) |
| Slope | 0 to 2 deg toward the wall (drain back, not out) |
| Protrusion p | 150-300 mm [PROPOSED]. The load model's p = 100 mm case cannot hold a 150 mm footprint; drop it. Baseline set e.g. 200 / 250 / 300 mm |
| Headroom | free volume >= 300 mm above the footprint, except root-grip tendrils <= 60 mm tall at the rim (p07 loved: tentacle-grips-pot) and a rim lip <= 10 mm |
| Drip | optional 5 mm perimeter lip / tray recess |
| Print orientation | top face down on the bed: flat, smooth, layers parallel to the tension face, underside web grows support-free upward |
| Single piece | shelf <= 240 mm from the root prints as one piece; longer shelves split with a tip joint at 160-240 mm from the root, pinned with an axial rod >= 8 mm. Joint demand <= 8 N.m (load at tip, 100 mm lever; conservative, ignores strut); design to 2x |

## 5. Buttress limb (approved, DECISIONS 2026-11-15)

Required at p >= 250 mm. Geometry per load model Section 6: foot ~300 mm below the shelf, ~45 deg, L ~420 mm, tip under the shelf at p.

| Item | Requirement |
|---|---|
| Axial design load | 104 N (factored), strut thrust 74 N horizontal + 74 N vertical at the foot |
| Member | min second moment of area I >= 6,300 mm^4 [PROPOSED] about the weaker axis, i.e. 2x the load model's 20 x 1.2 mm tube (3,144 mm^4, P_cr 311 N). That gives P_cr >= ~620 N, ~6x (5.98x) factored axial. Example: 26 mm OD, 1.8 mm wall tube, I ~ 10,000 mm^4. A sculpted limb is not a tube: verify min cross-section along its length, not at the thick ends |
| Wall | >= 1.8 mm, strands/webbing on the strut at >= 3.0 mm |
| Tip node | attaches to the shelf underside, solid node >= 30 x 30 mm; no segment joint within 75 mm |
| Foot | flat bearing pad >= 50 x 50 mm at the wall datum, plus a shear-fastener boss: one #10 stud screw or toggle through a >= 5.5 mm hole with a 16 mm washer seat, >= 20 mm solid depth. D/C < 0.3 on the fastener. Foot to land on a stud line or on the cleat bar extension |
| Optional | 6 mm rod channel along the strut axis for a steel/carbon core |
| Aesthetics | limb reads as another tentacle (less octopus-literal; c07 note) |

Thrust consequence: the shelf-root anchors must also resist 74 N inward pull (structural Section 6), so the root pocket and retaining screw are sized for tension, not just the cantilever couple.

## 6. Relief depth, mass, and variance targets [PROPOSED]

No verdict states numbers. Derivation: DECISIONS 2026-11-14 round-04 (Gaudi gradient v03 loved, Shlian crisp projection v08 loved; bas-relief body; "lots of horizontal protrusion variance") and the load model's assumption (mean depth 5-8 cm over 0.4-0.5 m^2 of solid mass).

| Metric (distance from the wall datum to the front surface) | Target |
|---|---|
| Mean over solid footprint | 60 mm (acceptable 50-80; matches load model mass basis) |
| Body P10 / P50 / P90 | ~20 / 55 / 110 mm |
| Body max (excl. shelves): mask brow, maw rim, limb crests | 120 mm; the mask is carved into the mass, no applied-object protrusion (r04 mask verdict) |
| Floor (thinnest skin/web skirt) | 15 mm total relief where structure exists; thinner skirt only as decorative strand |
| Shelf protrusion | 150-300 mm, at least one at 300 mm and one >= 200 mm |
| Depth standard deviation over solid footprint | >= 35 mm (shelves included) so the piece reads as strongly varied |
| Silhouette rule | gradient (Gaudi) with crisp projection edges (Shlian); no theatrical burst/niche (Bernini, Trevi dead) |

Mass gates (from load model Section 2): report mass, COM, and per-shelf-tentacle mass from the real mesh and replace the 5-14 kg / 1.0 kg guesses. Target 9 kg nominal, hard cap 14 kg; shelf tentacle mass fed back into M = W x x_c + W_self x p/2.

Reconcile in review: the relief of 60 mm mean plus 150-300 mm shelves implies overturning arm d ~ 50-60 mm for the body (load model used 50 mm). Fine unless the mean rises above ~80 mm.

## 7. Joint tolerance class (printed joints)

Starting clearance (per side, between mating printed faces):

| Joint class | Start | Range to test | Use |
|---|---|---|---|
| Slip / slide (dovetail, tongue-in-groove) | **0.25 mm** | 0.20-0.35 | assembly must go together by hand without force |
| Bonded (pin or key in socket, adhesive line) | **0.15 mm** | 0.10-0.25 | glue film (epoxy/PU, ~0.1-0.2 mm) |
| Heat-set insert hole | per insert datasheet minus 0.1-0.2 mm | | M3/M4 inserts for splice straps |
| Metal pin/rod socket (6-8 mm steel/carbon) | rod dia + 0.30 mm | +0.2-0.4 | printed holes print undersize |
| Press fit | avoid | | too variable for FDM at this size |

Justification: [GENERAL] 0.4 mm nozzle FDM holds roughly +-0.1-0.2 mm on small features; holes print 0.1-0.2 mm undersize; the first layers flare (elephant foot, 0.2-0.3 mm) so joints keep a 0.5 mm chamfer at the build plate; 0.2-0.3 mm clearance is the common working range for hand-assembled slip fits. Bonded joints take less because adhesive fills the gap.

Large-dimension shrinkage: PLA ~0.2-0.3%, PETG ~0.3-0.5%, ASA ~0.5-0.7% [GENERAL]. At 230 mm that is 0.5-1.6 mm per segment, accumulating over 4 segments across 914 mm to 2-6 mm if uncompensated. Requirement: print a calibration coupon set (one dovetail, one pin socket, one 230 mm flat strip) in the production material and printer, measure, and apply per-axis scale compensation before segments are cut for production. Nothing here is measured; Evan's actual printer and filament are unknown.

| Dimensional class | Tolerance |
|---|---|
| Segment envelope, after coupon-calibrated compensation | +-0.5 mm or 0.3%, whichever larger |
| Joint features (dovetail, sockets, pin bores) | +-0.15 mm after calibration |
| Cleat seat flatness | +-0.5 mm over 150 mm |
| Assembled back-plane coplanarity | +-1.0 mm across the piece (print the back face flat on the bed; warp risk in ASA) |
| Assembled seam | flush +-0.5 mm, gap <= 0.5 mm (cosmetic; structural seams bonded) |

## 8. Seams and segmentation hooks the geometry must provide

- Seam lands: each cut line crossing lattice must hit solid nodes: a seam face needs >= 400 mm^2 of solid bonding area and >= 3 locating features (pin/key). Sculpt must place solid "knuckles" (>= 20 mm wide, >= 3 mm wall) where seams can land, or seams follow valleys through voids.
- Flat back: all segments share a coplanar back plane (or stepped to the datum) to enable rear splice straps (M4 heat-set + bolt) across seams.
- Cut-friendly: no thin web exactly on a cell boundary; allow seam positions to float +-30 mm from the nominal grid.

## 9. Open items

- Aesthetics/Structural sign-off on [PROPOSED] numbers (depth targets, shelf p set, limb min I, keep-out margins).
- Validation script implementing Section 1 (not yet written).
- FEA or physical test of one shelf-root coupon before the structural claims go beyond hand calcs.
- Printer/material lock (Fabrication) feeds Section 7.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-15 | cad-lead | Initial creation (mesh spec from load-model-v1) | docs-reviewer (flagged: limb I, pad, embed numbers untagged PROPOSED) |
