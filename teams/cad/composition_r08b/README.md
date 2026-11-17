# composition_r08b: r07 G1a skeleton, character pass (3 densities)

CAD worker, 2026-11-17. [PROVISIONAL] Not boarded; not committed. r07 and r08 untouched. Numbers: `checks.json`, `measure_extra.json`, `checks/<id>.json`. Engine = r08 engine + `add_bundle2` (split/rejoin strand bundles), `add_web2` (flow-aligned tear membranes), `carve_tears`, `add_rib2` (braided surface strands).

## 1. What is fixed (hard input) and what changed
Kept from r07 G1a: trunk spine and radii, mask centre (8, 262), maw centre (0, -20), 3 arm roots (-105,150) / (70,60) / (-70,-100), arm paths (r07 `arm()` copied verbatim), shelf positions (UL 285, UR 150, LL -190 tops, cx -335/335/-335), bottom reach (cascade outer strands follow r07's T1/T2/T3 bands).
Changed (only these six):
1. **Lower body**: spine ends early (y -245, r 46); 6 / 8 / 9 hanging strands (a/b/c) of R0 17-64, 1-4 sub-strands, lengths 330-640 mm, different curls (3 hooked/spiral tips), none paired or mirrored, no horizontal underside. The long right strand H5 and the bottom-edge strand H4 trace r07's T2/T3 bands (needed for IoU), so the right side is still a heavy sweeping rope.
2. **Head top**: no hood, no dome. Mask (D 200, carved smiley per feature-references 1.1, strokes 14 mm) seated in a trunk head of r 112; 6 / 9 / 13 root strands fan out from behind the rim (r 100 to 124-160) with a scalloped cobweb veil between their tips (a: partial). Crown edge irregular, asymmetric.
3. **Limbs**: arms = bundles of 4 / 5 / 7 twisted strands that pinch and re-split (nodes 2/3/4), lumpy radius, fused toward the tip, roots fuse into trunk; strand floor r 4.5 mm (9 mm dia).
4. **Webs**: membranes with pointed-oval tears aligned to local strand flow (tangent of the nearest anchor strands), log-normal lengths, min ligament 11 mm, scalloped free edges; under-arm wings, cascade curtains, crown veil, in-bundle membranes (b, c); trunk flank slits carved through (14-17-22%). Not Voronoi. Open fraction per web 0.17-0.38 (`measure_extra.json`).
5. **Maw**: vertical almond 166 x 290, area 1.07-1.09 x mask (r08: 1.35). Flesh: 2 braided arch ribs, 1-3 braided meridian strands per side, 2-4 chest-yoke strands from the mask's lower flanks.
6. **Shelves**: plates 248 x 244 planform, thin lip with belly, lobed outline; 6 root fingers each hug the rim from the underside and end flush with the top lip (at most 0 mm above the top plane). Measured largest free flat rectangle (volume, `measure_extra.py`): S1_UL 158 x 182, S2_UR 194 x 182, S3_LL 172 x 172 mm; 300 mm clear above all three rectangles. Caveat: checks.py #12 (a different, conservative footprint a-18 x b-18) reads S3_LL 278 mm (a) and 6 mm (b, c): something rises into that footprint at the plate's inner end where the arm joins; not isolated. Fingers are 7.6 mm dia at their root, tapering below 9 mm (claw tips).

## 2. Studies (same skeleton)
| id | arm strands | hang strands | crown | webs (open frac) | trunk slits | IoU vs r07 G1a (mask png) |
|---|---|---|---|---|---|---|
| G1a_a restrained | 4 | 6 (H1-H6) | 6, veil part | 3 small wings, 2 curtains | 12% | 0.791 |
| G1a_b medium | 5 | 8 | 9 + veil | wings, 4 curtains, arm-band membranes 0.16 | 17% | 0.770 |
| G1a_c dense | 7 | 9 | 13 + veil | wings, 7 curtains, band 0.14 | 22% | 0.767 |
Differences between a, b, c are real but modest from the front (more strands, webs and slits, same trunk and arms). The IoU budget (>= 0.75 vs r07) is what stops "c" from being c01-dense.

## 3. Checks
| id | COMP | failed | gate (7) | gate fails | IoU vs c01 | IoU vs r07 G1a | wall / flesh / mask / maw lum % | maw:mask |
|---|---|---|---|---|---|---|---|---|
| a | 4/13 | 1,2,5,6,7,8,10,12,13 | 4/7 | torso_width_frac 0.740, limb_count 4, iou_vs_c01 | 0.575 | 0.791 | 13.0 / 30.1 / 100 / 6.9 | 1.09 |
| b | 3/13 | 1,2,5,6,7,8,10,11,12,13 | 4/7 | torso 0.742, limb_reach 0.238, iou_vs_c01 | 0.584 | 0.770 | 13.0 / 30.5 / 100 / 6.9 | 1.09 |
| c | 4/13 | 1,2,5,6,7,8,10,12,13 | 3/7 | torso 0.811, limb_reach 0.240, limb_count 4, iou_vs_c01 | 0.585 | 0.767 | 13.1 / 30.8 / 100 / 6.8 | 1.07 |
Other gate values (a/b/c): fill 0.422 / 0.452 / 0.471 (band 0.371-0.557), wedges 7, head_vs_flesh 2.28 / 2.21 / 2.11. All metrics in `checks.json`.
- **IoU vs c01 is below the 0.60 start (s.4.1) in all three (0.575-0.585); r07 G1a itself was 0.598.** The two hard inputs conflict at the margin: c01's wide arm wings and lower mass would need area that costs IoU vs r07. A wider-wing build reached 0.589 for c01 but 0.738 vs r07. Failed gate item, stated.
- Torso blob 0.74-0.81 (band <= 0.598): the opened torso swallows arm roots and wings; same failure as r08.
- #2 body 22.2% (deliberate trunk), #5 fails by design: checklist wants maw:mask <= 0.7 or >= 1.3, this brief asks 1.0-1.2 (interior 17.5 < body 80, rim 68 < body: those sub-tests pass), #6/#7 hanging strands taper < 5:1 and sit < 12-25 mm tip band (H2, H3, H6, H7, H8, H9), #8 rival pairs, #10 close pairs (S3_LL/H7, H1/H7), #12 see above, #13 mirror IoU passes but L/R weight ratio 1.0-1.04 (< 1.1). #1 and #11 follow the checker's judgment fields.
- Mask is the single brightest value (margin 67-69 at p99.5). Grain is shader only; palette desaturated 38%.

## 4. Self-assessment vs Evan's r07 notes (blunt)
- **"A bit squid like"**: reduced, not removed. Head now has no dome and no hood; the cascade reads as roots, not a mantle skirt. But the figure is still: egg trunk + open vertical maw + curled tentacle strands. The trunk is the weak part: smooth between slits and braids.
- **"Gothic and Beksinski"**: marginal. Pointed-arch ribs, scalloped cobweb edges, tears along strand flow; nothing is eroded, fibrous or decayed over the whole mass. Reads "tree-root creature", not Beksinski. Webs read as torn paper strips in places (straight inner rims at the trunk).
- **Base that would not sit flat**: yes. Nothing horizontal under the figure; 6-9 strands end at different heights (y -352 to -452), 3 hooked/spiral. The right side is r07's T2 band as a heavy rope and still dominates; the bottom-edge strand H4 also trails horizontally ~150 mm.
- **No two-legged look**: no paired lower limbs from a pelvis; thickness/length/curl differ. Risk: H1 (left) and H5 (right) are the two longest and diverge about equally from the trunk base; a distant viewer can still read a splayed stance. Judgment, not measured.
- **Vertical maw**: kept, 1.07-1.09 x mask (target 1.0-1.2), flesh strands beside it. Reads as a mouth, no longer a donut.
- **vs c01**: c01 is lace everywhere (arms are wide perforated sheets, head is a rooty hood, trunk is all fibre). Mine keeps r07's solid arms/trunk; lace is in the margins. Best passages: the lower cascade, the S3_LL arm bundle. Worst: the crown (curly strands, reads like hair), wings under the arms, smooth trunk.

## 5. Reproduce
`python3 build.py G1a_b` (35 s) -> `python3 iou_r07.py G1a_b` -> `python3 render_comp.py G1a_b --views front,tq --mask --samples 24` (~2.5 min) -> `python3 run_checks.py` -> `python3 measure_extra.py` -> `python3 make_sheets.py`. Contact sheet `renders/contact_sheet.png` (3 studies + r07 G1a + c01), `renders/silhouette_sheet_128.png`. `build/` is large (134 MB), not for commit.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-17 | cad-worker | Initial creation: round-08b studies | [PROVISIONAL] |
