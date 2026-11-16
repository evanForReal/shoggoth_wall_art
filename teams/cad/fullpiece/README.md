# Full-piece composition sculpt (round-05 in-house renders)

**Status:** [PROVISIONAL] CAD Lead, 2026-11-16. For Evan's eyes, not the printer: 2.0 mm voxel, Gate-2 vocabulary scaled ~4-5x, grain via a coarse flow-aligned displacement (1.1-3.0 mm, outward only), 1C crevice shader, dark-wall context lighting (warm key, two downlight washes). Full min-wall / void validation waits for the print-res pass after Evan picks a composition.

## 1. Variants (one param set each, `VARIANTS` in `gen_fullpiece.py`; each differs from the hero by one axis)

| Variant | Changes vs hero | Axis |
|---|---|---|
| `hero` | Carved-serene mask (closed eyes, nose ridge, soft smile line; pale bone, recessed inside a raised bezel) + maw with fibre teeth, c01-like radial sprawl (8 whips + 3 shelf arms, spiral flow), shelf arrangement A (upper-left, right, lower-left) | baseline |
| `v1_smiley` | Flat-graphic smiley mask: flat disc, two oval eye recesses, upward-curving smile groove | (a) mask treatment |
| `v2_nomaw` | Mask only, maw removed (its bay and teeth gone) | (b) maw |
| `v3_diagonal` | Strong diagonal sweep: body mass rotated to 38 deg and elongated, whips trail up-right and down-left, uniform-diagonal flow field | (c) tentacle layout |
| `v4_shelvesB` | Arrangement B: left mid (y 120), right upper (y 290), right lower (y -130, longest, carries the buttress); p = 210 / 240 / 280 | (d) shelf layout |

Renders (`renders/`, all <= 1 MB): hero `hero_front|tq|rake|side.png`; each variant `<name>_front.png`, `<name>_tq.png`; `variants_sheet.png` (all five fronts plus the c01 reference).

## 2. What is in the piece

Asymmetric off-centre body mass (two blobs, centre pulled left of the wall midline) at bas-to-mid relief (mean 50 mm, P10/P50/P90 19/44/92 mm, std 27 mm, max 132 mm incl. bezel and whips); the mask sits in the upper-left of the mass, carved (recessed face inside a raised bezel, no applied object); three flat-topped plate shelves (190 mm wide, p 200-290 mm, flat to 0.5 mm) each rooted in a thick webbed arm and carried by a fan of 20 rim-to-body fibres plus 14 cross-links (root grip); a buttress strut (r 15 mm) from under the longest shelf tip to a 64 mm flat foot pad on the wall; 7-8 decorative whips tapering 29 -> 7 mm radius; irregular bays with broken rims; membranes, ribs, streamline ribs and sagged fibres per Gate 2.

## 3. Engineering checks (`engineering_checks.json`, mesh at 2.0 mm voxel, ~1.4 M tris each)

| Check | hero | v1 | v2 | v3 | v4 |
|---|---|---|---|---|---|
| Bbox X x Y x Z (mm; limit 914 x 914 x 300) | 911 x 875 x 300 | same | 911 x 875 x 300 | **918 x 919 x 300** | 911 x 875 x 291 |
| Within limit | yes | yes | yes | **NO (4-5 mm over)** | yes |
| Back plane z range | 0-3 mm (grain pinned at 0) | same | same | same | same |
| Shelf flat tops (area, nominal 190 x p) | 476 / 361 / 522 cm2 | same | 476 / 365 / 517 | 476 / 363 / 502 | 383 / 443 / 518 |
| Shelf flat spread (mm) | 0.52-0.83 | | | | |
| Buttress drop below longest shelf | 300 mm | 300 | 300 | 300 | 299.5 |
| Solid mass upper bound (PETG 1.27) | 22.2 kg | 22.2 | 23.3 | 22.5 | 22.3 |

Back plane: vertices with z < 3 mm span 0.0-3.0 mm because strand cross-sections at the datum round at 2 mm voxels; the pinned back-face vertices are at z = 0. Not a print-res flatness claim.

Cleat hard-points: three seat zones reserved and filled solid (160 mm wide x 150 mm tall under each plate, on the body side, z 0-16 mm); coordinates in `engineering_checks.json` (`shelves[].seat_zone`). Shear-fastener boss on the foot pad is not modelled.

## 4. Constraints NOT honored (or only partly)

1. **v3 bbox 918 x 919 mm** exceeds 914 x 914. Whip centrelines were clipped at +-425 mm but skirts and tube radius push past. Needs a hard clip in the print-res pass; hero, v1, v2, v4 are inside.
2. **Shelf headroom (300 mm clear above each flat) is violated.** The fibre fan under an upper shelf hangs 70-175 mm into the headroom of the shelf below it (stacked left shelves S1/S3 at the same x). Vertices intruding above each shelf (hero): S1 0, S2 884, S3 62,315 (S3 is the worst; ~160 mm effective clearance). Tendrils at the rim (p07 root-grip, <= 60 mm tall) are not modelled; the fans are underside only.
3. **Seat embed depth is 16 mm, spec >= 25 mm.** Reserved footprint is right (>= 150 x 150), depth is not.
4. **Mass: 22 kg solid** vs a 14 kg cap. Composition proxy: fully solid mask, arms, whips and seats. The print-res pass hollows to shell + ribs; mass is not a valid number until then.
5. **Not validated at all at this stage:** min-wall (2 mm voxels cannot resolve 2-3 mm strands; strands here are 9-30 mm), 6 mm void rule, overhang, segmentation, bridge limits on fibres.
6. Strut: radius 15 mm solid (spec 26 mm OD hollow tube, I >= 6,300 mm^4) and not checked against the 104 N load case.
7. Relief: body mean 50 mm is under the 60 mm (50-80) target; max 132 mm (mask bezel and whips) is slightly over the 120 mm body cap.

## 5. Self-assessment (blunt)

- **Gate-2 vocabulary:** survives only at close range. The raking hero view (mask and bezel) reads well: grain, crevice shading, recessed serene face. At wall distance the piece reads as a dark rust-and-bone tangle with pale whips; the c01/c02 character (thick webbed limbs reading as flesh, large smooth bays, fibre mat) is largely absent. Web ribs here are 9-30 mm and look coarse and "barky".
- **Silhouette:** compact starburst with two wing-like shelf fans. It is closer to an emblem or heraldic eagle than to c01's sprawling octopus or c02's sheet. The five variants are **not different enough**: they share body, mask position and tone; only the mask, maw presence and shelf heights read clearly in the sheet. V3 changes the silhouette most (diagonal), but whips still look like pale scribbles.
- **Locked constraints:** horrific asymmetry yes (off-centre mass, unequal shelves, whips by hand-set angles), but the wing-like left-right shelf pairing in arrangement A trends toward symmetry; B is better. Not-a-centerpiece restraint: the mask is the brightest element and sits near the visual centre, so it is the focal point; tone it down or move it. Carved mask never worn: yes (recessed, bezel, no seam; clean surface). >= 150 x 150 flat tops: yes (all five). Buttress under the longest shelf: yes, but it is a thin stick that does not read as "another tentacle". Flat back: yes. Cleat hard-points: reserved, not detailed.
- **Smiley (v1):** reads clearly but is the weakest fit; the face is small and fussy beside the serene mask (it looks like a cartoon sticker on the mass).
- **Maw (hero):** reads as a dark void with fibre teeth; at this scale it competes with the mask less than expected; v2 without it looks cleaner and calmer.

## 6. Regenerate

`./run_all.sh OUT` (per variant: field ~2 min, mesh + grain ~20 s, renders ~1.5 min/view at 1200 x 900, 48 samples; ~6 GB RAM). Single variant: `python3 gen_fullpiece.py --variant hero --vox 2.0 --out OUT && python3 render_full.py OUT hero renders --views front,tq,rake,side`. Imports the locked helpers from `../gate2/gen_patch.py`. Seeds fixed.

## 7. Print-res pass will need

1. Hard bbox clip; fix v3; per-segment cuts (<= 230 x 230 mm) with seam lands off the hard-points.
2. 0.4-0.5 mm voxel per segment (tiled), real strand widths 2-8 mm, min-wall clamp, sliver plug and the Gate-2 sculpt pass at 0.24 mm edges.
3. Shelf rework: stagger fans so every footprint has 300 mm headroom, add rim tendrils <= 60 mm, 25 mm+ seat embed, 80-120 mm two-row fastener geometry, bearing pads at the datum.
4. Buttress as a 26 mm OD hollow tube with a #10 shear boss; mass hollowing to hit 9-14 kg; segment mass table.
5. Whips at spec (OD >= 16 mm), body relief re-balanced to 60 mm mean.
