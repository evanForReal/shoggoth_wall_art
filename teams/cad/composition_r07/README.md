# composition_r07: figure-first composition studies (round-07)

CAD Lead, 2026-11-17. NO surface detail: no grain, eyes, teeth, fingers. Massing, value, depth only.
Every number below is in `checks.json` (per study, per item) or comes from the generator inputs in `studies.py`.

## 1. Method and why

Pipeline: gesture spline -> variable-radius sphere-sweep body -> limbs as tapered sweeps rooted inside the body -> mask dome -> maw carve -> flat-top shelf plates -> hard clip. Code: `engine.py` (SDF sweeps, smooth-min), `build.py` (assembly, marching cubes, per-part silhouettes), `studies.py` (the 8 figures as data), `render_comp.py` (bpy Cycles), `checks.py`, `make_sheets.py`.

- **Body** = ONE sweep along the spine spline (head hood, trunk, root column), radius profile r(t), z-flattened x2 so the trunk sits at bas-to-mid relief (60-100 mm). Head hood merges into the trunk: no neck pinch (orchestrator read of G1a).
- **Limbs** = one sweep each along its own 3D curve with a lateral S-wave, radius law `w = w0 (1-s)^0.75` to s = 0.88 then linear to a 12 mm tip (feature-ref s.4), root start buried inside the trunk, smooth-min blend k = 26 mm. Roots stagger in height along the trunk sides; weights differ (r0 36-70).
- **Mask** = flattened ellipsoid dome (D = 200 mm) seated on the head hood, one pale value. **Maw** = vertical almond (w 200, h 300, 1:1.5, 1.0 D wide) carved into the trunk with a swollen chest around it, sloped walls, floor 12 mm above the wall plane, darkness falls off over 38 mm onto the rim.
- **Shelves** = superellipse plate (flat top >= 180 x 148 mm, R26 edges, belly bowed 14 mm below), top carved to an exact plane; the limb passes under it, is level at the plate's inner edge, and its tail lifts at the rim as a cradle. Arms are never above the plate plane inside its footprint.
- **Why SDF sweeps, not metaballs or the bpy skin modifier:** exact control of radius per arclength (taper law, root:tip), 3D z profile per curve, exact flat planes and hard clips by min/max, watertight marching cubes, 5 s per study. Metaballs cannot hold a 5:1 taper with a 12 mm tip. Skin modifier gives topology-driven bulges and no analytic flat plane. Not a union of features: the body is one field grown from the spine, limbs are continuations of it.
- Render: Cycles, orthographic front (1.175 mm/px, mask png shares the framing exactly), one raking warm key from upper left + faint fill, identical for all studies. Wall 12% luminance (limit 15), flesh 36-38%, mask 90-98%, maw 6-8%.

## 2. Studies (pairs differ in ONE axis)

| id | gesture | axis | description |
|---|---|---|---|
| G1a | G1 Descending Figure | baseline | c01-faithful: tall trunk, mask set into the trunk top, maw inside with flesh below, 3 arms staggered (UL high 285, UR 150, LL -190; r05 arrangement A kept), 3 tentacles (heavy right one hooks down, left one long, thin centre one). 6 limbs. |
| G1b | G1 | mask offset left (-62 mm) + S-leaning trunk | Shelves re-staggered (UR high 310, UL 135, LR -190). Differs from A by design: composition first. |
| G2a | G2 Diagonal Emergence | heavy trunk | Head upper right, trunk on a diagonal to lower left, rising whip over the head, shelves UL 330 / ML -60 / LR -290. |
| G2b | G2 | lean trunk (r 150 vs 186) | Same limbs. |
| G3a | G3 Low Crouch | vertical almond maw | Wide hunched trunk, two horns rising each side of the head, 8 limbs. Mask at 0.30 H (checklist #3 limit): the "low" head is as low as #3 allows. |
| G3b | G3 | horizontal almond maw | Rules on maw orientation (feature-ref asks for this question). |
| G4a | G4 Sinuous Spiral | heavy ribbon | Head upper left, S ribbon down to lower right, shelves UR 330 / R -115 / LL -365. |
| G4b | G4 | lean ribbon | Same limbs; ribbon weight cut. |

Files: `renders/study_<id>_front.png` (1200x900, <= 0.73 MB, PIL-verified), `study_<id>_mask.png` (binary, wall excluded, same framing), `study_G1a_tq.png` and `study_G2a_tq.png` (three-quarter, the two I judge strongest compositions), `contact_sheet.png` (8 fronts + c01), `silhouette_sheet_128.png` (128 px black-on-white + c01 trace).

## 3. Checklist #1-13 (front silhouette + render)

| id | score | failed | body % env | fill % | wedges >= 4% | mask margin (p99.5 / max, 8-bit) | maw:mask area | min headroom mm | L/R weight / mirror IoU |
|---|---|---|---|---|---|---|---|---|---|
| G1a | 9/13 | #2,#8,#10,#11 | 25.01 | 45.7 | 4 | 46.0 / 37.0 | 1.35 | 300 | 1.25 / 0.529 |
| G1b | 10/13 | #2,#8,#13 | 23.61 | 43.6 | 4 | 54.0 / 45.0 | 1.37 | 300 | 1.84 / 0.416 |
| G2a | 8/13 | #2,#7,#8,#11,#13 | 25.15 | 43.8 | 4 | 25.0 / 16.0 | 1.36 | 300 | 1.01 / 0.468 |
| G2b | 7/13 | #1,#2,#7,#8,#10,#11 | 21.1 | 41.8 | 4 | 24.0 / 16.0 | 1.36 | 300 | 1.1 / 0.495 |
| G3a | 7/13 | #2,#7,#8,#10,#11,#13 | 21.88 | 41.5 | 5 | 45.0 / 37.0 | 1.35 | 300 | 1.55 / 0.453 |
| G3b | 8/13 | #2,#7,#8,#10,#13 | 21.91 | 41.5 | 5 | 45.0 / 37.0 | 1.35 | 300 | 1.54 / 0.482 |
| G4a | 8/13 | #2,#7,#8,#10,#11 | 25.56 | 47.0 | 2 | 89.0 / 78.0 | 1.33 | 300 | 1.43 / 0.442 |
| G4b | 7/13 | #1,#2,#7,#8,#10,#11 | 22.28 | 44.6 | 2 | 89.0 / 78.0 | 1.33 | 300 | 1.3 / 0.407 |

Limb taper (root:tip, measured at t = 0.97) / length over W (target 5:1 and 0.40-0.65 W):

| id | limbs |
|---|---|
| G1a | S1_UL 6.1:1/0.44W, S2_UR 5.9:1/0.44W, S3_LL 5.5:1/0.54W, T1 7.5:1/0.5W, T2 7.1:1/0.61W, T3 5.1:1/0.54W |
| G1b | S1_UR 7.7:1/0.45W, S2_UL 5.1:1/0.42W, S3_LR 5.6:1/0.51W, T1 8.3:1/0.54W, T2 5.3:1/0.58W, T3 5.8:1/0.41W |
| G2a | S1_UL 7.2:1/0.52W, S2_LR 8.3:1/0.57W, S3_ML 4.2:1/0.5W, T1 6.9:1/0.44W, T2 6.1:1/0.41W, T3 5.0:1/0.44W |
| G2b | S1_UL 7.5:1/0.52W, S2_LR 8.3:1/0.57W, S3_ML 4.7:1/0.5W, T1 7.1:1/0.44W, T2 6.2:1/0.41W, T3 5.6:1/0.44W |
| G3a | S1_UL 5.8:1/0.51W, S2_UR 6.0:1/0.44W, S3_LR 6.2:1/0.58W, H1 5.3:1/0.51W, H2 3.9:1/0.46W, T1 7.8:1/0.5W, T2 5.2:1/0.46W, T3 4.8:1/0.53W |
| G3b | S1_UL 6.0:1/0.51W, S2_UR 6.0:1/0.44W, S3_LR 6.1:1/0.58W, H1 5.1:1/0.51W, H2 3.8:1/0.46W, T1 7.8:1/0.5W, T2 5.3:1/0.46W, T3 4.9:1/0.53W |
| G4a | S1_UR 7.7:1/0.6W, S2_LL 8.0:1/0.65W, S3_R 4.5:1/0.45W, F2 6.2:1/0.41W, W1 4.4:1/0.42W, F1 7.2:1/0.52W |
| G4b | S1_UR 8.0:1/0.6W, S2_LL 8.0:1/0.65W, S3_R 4.7:1/0.45W, F2 6.3:1/0.41W, W1 4.6:1/0.42W, F1 7.4:1/0.52W |

Headroom: all 24 shelf tops hold 300 mm clear (flat patch footprint, voxel test). Flat tops 184 x 148 mm. Triangles non-collinear, height gaps >= 135 mm, one top above y = 152 in every study.
c01 silhouette IoU (gate recipe, own computation `iou_c01.py`): G1a 0.60 (G1a neck version 0.59). The independent gate scores the pngs separately.

### Failures, by cause (blunt)
- **#2 fails in all 8 by design.** Body is 21.1-25.6% of the envelope vs the 12-20% band. The orchestrator rule (bulky trunk, no neck, c01 torso 0.46-0.48 W) and the checklist ceiling contradict; I followed the orchestrator. The neck-step test was rewritten to "shoulders >= 1.15 x head width" (passes everywhere); the pinched neck is gone on purpose. Body : largest limb is 4.03-6.16 (>= 1.8 passes).
- **#8 (no equal rivals) fails in 8 of 8.** Limb areas cluster. I tried area-targeting r0 per rank; it forced r0 to 128 and produced bulbous arms that swallowed the head, so I reverted to hand-set weights (shelf r0 70/58/48, tentacles 36-64). Not solved. G1b passes #1,#3-#7,#9-#12; only #2, #8, #13 fail.
- **#11:** the shelf flat top is a 184 mm straight run by spec (>= 150), so the 120 mm rule can never pass with a flat top; those runs are listed apart in checks.json (`shelf_top_runs_mm`). Non-shelf runs in the #11-failing studies: 126-235 mm (G3a 235, G4a 187) (limb undersides): too straight, waves are only 5-7% of length.
- **#10:** fill 45.7% / 47.0% in G1a / G4a (over 45) because the trunk is big; close limb pairs (> 150 mm under 60 mm) fail it in G2b, G3a, G3b, G4b.
- **#13:** G1b/G3 left-heavy (centroid -43 to -45 mm, L/R 1.5-1.8); G2a mirror-balanced (1.01, needs >= 1.1).
- **#7:** one or two thin limbs per study have taper < 5 (W1, H2, T3, S3_ML): r0 36 with a 12 mm tip floor.
- **#1 (judgment):** reads as a tentacled figure in all 8 at 128 px (silhouette sheet). It fails in G2b/G4b only through the automatic proxy (shoulder/head step on lean trunks). My judgment: G2b and G4b read as creatures; the lean trunk is the weakest of each pair.
- Every study fails 3-6 items (G1a 4, G1b 3, G2a 5, G2b 6, G3a 6, G3b 5, G4a 5, G4b 6); #2 is deliberate in all. I fixed what a re-tune could fix (headroom, taper, orientation, plate seams, balance partly); the rest needs a decision (see s.5), not another parameter pass. Not "replaced" because the alternative (the earlier neck/thin-limb passes) fails the orchestrator's visual rules.

## 4. Coordinator inputs folded in
1. Mask D = 200 mm (spec 200-240). D = 230 gives 4.97% of the envelope and fails #3 (2-4%); D 200 = 3.76%. Smiley strokes not carved here (no detail). Head hood ~275 mm wide, so the body scales to the head (trunk 370-396 mm wide).
2. Maw vertical almond 1:1.5, 1.0 D wide, in the torso, dark (6-8%), rim darker than body mean. Orientation is the one-way difference of pair G3a/G3b.
3. Tentacle law, S-wave, tips taper to 12 mm, >= 3 lower limbs; gaps >= 60 mm hold in G1a, G1b, G2a; close limb pairs (> 150 mm of length under 60 mm) remain in G2b, G3a/b, G4a/b. Root angles >= 25 deg not scripted (judgment: met in G1a/G1b/G2a/G3a). Length 6-10x root width is not reachable inside 0.65 W (lengths are 3.8-6.5x root width); I used the checklist length range.
4. Shelf arms: tapered limbs under the plate with a lifting tail. The plate is still a slab in the front view; the belly and tail are subtle. This is the weakest design element. Flat top and headroom specs hold.
5. Orchestrator read of G1a (no neck, trunk, staggered roots, weights, <= 2 curls, asymmetry): applied to all. Curls: 1-2 hooks per study.
6. RP-3: `study_<id>_mask.png` saved for every study. G1a is the c01-derived kernel test: IoU 0.60.

## 5. Board recommendation (3-4 cards)
1. **G1a**: most c01-faithful; trunk, maw with flesh below, staggered arms. The "can our relief kernel reach c01" card.
2. **G2a**: strongest composition by gesture (diagonal, head high right, large wall wedges, S-curved whip). Fails #2, #7 (1 limb), #8, #11, #13.
3. **G3a + G3b** as one card pair: asks the maw orientation question; strongest menace (horns), best silhouette read at 128 px.
Keep G1b as spare. Drop G4a/b (heavy bean-shaped body, crowded lower half), G2b (lean trunk looks knotted).
Where I differ from arrangement A: all but G1a. G1b mirrors it, G2 puts the low shelf at lower right, G3 has UL/UR/LR, G4 has UR/R/LL. Composition wins; the headroom spec holds in all.

## 6. Self-assessment vs c01 (blunt)
- Silhouette: reads as one creature with a head, trunk, 6-8 tapered limbs and wall wedges. IoU vs c01 0.60 (c01 has web-sheet arms; mine are tubes).
- Still reads as a smooth clay octopus/mascot. Limbs are rubbery equal-ish tubes, plates are floating slabs, the maw is a clean almond. c01's lace, perforations and lost edges are absent by brief; they must come back as texture and perforation, not as geometry added to this massing.
- Shelf plates are the worst element (flat slabs at tube ends; arm-plate seam visible in G2 lower right).
- G2/G4 lower-right arms have a knotted loop where the root descends; G4 bodies read as a bean.
- No lost edges, no perforations (hierarchy of rest holes comes from the wall wedges only).

## 7. Reproduce
`python3 build.py G1a` (5 s) -> `python3 render_comp.py G1a --views front,tq --mask --samples 28` (about 1.5 min) -> `python3 -I checks.py G1a` -> `python3 make_sheets.py`. `studies_v0_neck.py` is the superseded neck-version data (the first G1a pass, kept for comparison; its render is deleted).

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-17 | cad-lead | Initial creation: round-07 composition studies | docs-reviewer (resolved, was FLAG OPEN: same defects as the CAD STATUS row. s.3 Failures: "#2 ... 21-27% of the envelope" is 21.1-25.6% in checks.json; "#8 fails in 7 of 8" is 8 of 8 (the G1b line in the same section lists #8 as failing); "Body : largest limb 4.0-6.3" is 4.03-6.16. Verified OK: s.3 table scores, failed lists, body %, fill %, wedges >= 4%, maw:mask area and L/R weight / mirror IoU for all 8 rows equal checks.json; headroom 300 mm on all 24 tops, flat tops 184 x 148 mm, height gaps >= 135 mm, tops above y 152 in every study; #13 left-heavy G1b/G3 (centroid -43 to -45 mm, L/R 1.5-1.8); mask D 200 = 3.76%; header claim that numbers are in checks.json or studies.py holds for those checked (D 230 = 4.97% not re-derived). Minor, non-blocking: #10 bullet omits G3a/G3b, which also fail #10 (close limb pair S3_LR/T3). Body [PROVISIONAL] header tag stays; resolved by the next row (cad-lead, 'Fixed reviewer flags'), re-verified at HEAD against checks.json: s.3 Failures now read '#2 ... 21.1-25.6%' (body_pct min 21.1, max 25.56), 'Body : largest limb is 4.03-6.16' (min 4.03, max 6.16), '#8 ... fails in 8 of 8' (8/8 failed lists), non-shelf runs '126-235 mm' (longest_nonshelf_run_mm over the 6 #11-failing studies: 126, 139, 132, 235, 187, 147), 'G3a 235, G4a 187' correct, per-study fail counts 4,3,5,6,6,5,5,6, G2a fails #2,#7,#8,#11,#13, G1b fails #2,#8,#13, flesh luminance 35.6-38.4 = '36-38%', fill 45.7/47.0 in G1a/G4a, G3a/G3b close pair S3_LR/T3 (336 mm) listed. Non-blocking, signed through: the #10 bullet lists the close-pair failures as G2b, G3a, G3b, G4b but G4a also has two close pairs (S1_UR/W1 156 mm, S2_LL/F2 228 mm); G4a is already named for fill and s.4 item 3 lists G4a/b, so no number is wrong; CAD lead to add G4a at next spawn)) |
| 2026-11-17 | cad-lead | Fixed reviewer flags: #8 8/8, #2 body 21.1-25.6%, limb ratio 4.03-6.16, non-shelf runs 126-235, #10 bullet adds G3a/G3b, flesh 36-38% | docs-reviewer (verified: every number named in the row is correct vs checks.json (see row above); header claim 'every number is in checks.json or studies.py' holds for the numbers checked (mask D 230 = 4.97% not re-derived); body [PROVISIONAL] header tag (L3) cleared with this sign-off) |
