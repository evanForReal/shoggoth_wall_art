# composition_r08: round-08 studies (composition round 2 + first character pass)

CAD Lead, 2026-11-17. [PROVISIONAL] Macro-form only: strand bundles, lace webs, ribs, cords at >= 8 mm; grain is shader/bump only (no geometry grain). No hands, teeth, eyes. r07 untouched. Numbers are in `checks.json`; per-study checks in `checks/<id>.json`.

## 1. What changed vs r07 (engine reused, vocabulary replaced)
- **Body** still ONE variable-radius sweep from a spine, z-flattened, but the head is an **ogive hood** (pointed apex, no bulbous top) merging into the trunk without a neck. The spine now carries the radius at each control point and ends in a **hanging taper**, not a hub.
- **Limbs = bundles**: 5 twisted strands (strand radius 0.40 R, helical offset, strands merge toward the tip, floor r 4.5 mm = 9 mm diameter) instead of smooth tubes. Hanging strands taper by the feature-ref law.
- **Lace webs**: perforated membranes (Worley lace, cell 34-46 mm, strand width 9 mm, 8 mm thick, 9 mm solid rim) under the shelf arms (flying-buttress triangles with a pointed-arch free edge) and between hanging strands.
- **Gothic ribs**: pointed-arch ribs framing the maw, sinew cords running along the trunk (broken around mask and maw, smoothed so they do not read as knuckles; the first cut looked like fingers around the maw and was removed).
- **Mask**: carved smiley per feature-references s.1.1 (Harvey Ball proportions: eyes 0.095/0.100 D x 0.215/0.228 D, smile arc through three points, stroke 0.070 D = 14 mm, flat-floor recesses 11 mm deep, 5.5 mm bezel). D = 200 mm (spec wants >= 230 for a 15 mm stroke; 230 would be 4.97% of the envelope, over the #3 limit of 4%). Recess floors render near-black.
- **Maw**: vertical almond 200 x 300, carved, dark (6-9% luminance), locked per r07.
- **Shelves**: flat top 200 x 164 mm; 300 mm clear above holds on 13 of 15 tops (G4 S2_LL 246 mm, G4 S3_R 290 mm; everything else 300), bowed belly, claw strands cradle the front rim from below. Plate silhouettes are still slabs from the front.
- **Lower body**: nothing paired or mirrored; all hang, taper and trail (details per study).
- **Render**: wall 13.2-13.4% luminance, warm soft downlight from upper left, one pale value (mask). Flesh 34-36%, maw 6-9%.

## 2. Studies
| id | lower body ends in | notes |
|---|---|---|
| G1a_i | pendant taper: the trunk narrows into one long tail with 4 root-strands peeling off at different heights, 2 webs between strands | most literal "pendant"; tail reads as a pencil point; H3/H4 strands trail wide at the bottom (400 mm extent in the lowest 60 mm), the weakest on the base rule |
| G1a_ii | trunk dissolves into 7 thin hanging strands of unequal length/thickness/drift, lace curtains between 5 pairs | closest to c01's cascade; lowest-60 mm extent 76 mm, 3 tips touch the bottom band; best on base and two-legs |
| G1a_iii | off-centre root-knot, one heavy S-rope sweeping lower right + hanging veil of 4 strands and 2 webs | most c01-like right limb; most asymmetric |
| G2a_dev | diagonal G2: ogive head upper right, trunk on the diagonal curling into a hanging tail left; 3 hanging strands, no whip over head | big right-hand wedge of wall; S2 plate lowered to -262 for headroom |
| G4a_dev | S ribbon, head upper left, hanging tail lower right, 3 hangers | trunk reads as a wide fish body; S2_LL plate at -300 is intruded by the trunk (246 mm clear, not 300) |
G1 shelf arrangement (A): UL 285, UR 150, LL -190. G2: UL 330, ML -60, LR -262. G4: UR 330, R -40, LL -300.

## 3. Checks
Checklist #1-13 on the front silhouette/render (`checks.py`) and `tools/composition_gate.py` (c01 bands; the G1 IoU band in the tool is 0.70, the brief and DESIGN_PRINCIPLES s.4.1 start is 0.60):

| id | COMP | failed | body % | fill % | wedges >= 4% | mask margin (p99.5) | maw:mask | min clear mm | gate | gate fails | IoU vs c01 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G1a_i | 8/13 | #2, #7, #8, #10, #11 | 27.15 | 39.5 | 3 | 60.0 | 1.35 | 300 | 6/7 | iou_vs_c01 | 0.616 |
| G1a_ii | 6/13 | #2, #6, #7, #8, #10, #11, #13 | 26.0 | 38.0 | 2 | 62.0 | 1.37 | 300 | 5/7 | limb_count, iou_vs_c01 | 0.605 |
| G1a_iii | 8/13 | #2, #7, #8, #11, #13 | 26.44 | 39.5 | 3 | 66.0 | 1.36 | 300 | 5/7 | limb_count, iou_vs_c01 | 0.602 |
| G2a_dev | 7/13 | #1, #2, #6, #7, #8, #11 | 25.4 | 40.8 | 3 | 51.0 | 1.35 | 300 | 4/7 | fill_ratio, limb_count, iou_vs_c01 | 0.374 |
| G4a_dev | 7/13 | #2, #6, #7, #8, #11, #12 | 27.56 | 41.1 | 5 | 74.0 | 1.33 | 246 | 5/7 | torso_width_frac, iou_vs_c01 | 0.376 |

- **IoU:** G1a_i 0.614, G1a_ii 0.602, G1a_iii 0.600 (CAD `iou_c01.py`, same recipe as the gate; gate values above). All three clear 0.60 by a hair, bought by widening the trunk (head hood 292 mm, shoulders 380 mm) and by the web wings. The gate's own band is 0.70: FAIL against that.
- **Deliberate or structural fails:** #2 body 25-28% (c01 trunk, orchestrator rule; band 12-20%). #7 hanging strands have taper < 5:1 because strands start at R0 16-40 and the tip floor is 12 mm (design choice for thin trailing strands). #6 fails where hanging strands do not "rise or extend outward" (the no-stance directive contradicts #6 for the lowest limbs). #8 equal rivals fails in all five (arm and strand areas cluster). #11 the 200 mm flat shelf top is a straight run by spec (listed apart); other straight runs 144-230 mm are web free edges and arm undersides (not curved enough).
- **#10 (G1a_i):** hanging pairs H1/H4, H2/H3 closer than 60 mm over 180-228 mm; G1a_ii has only 2 wedges >= 4% (12.4, 6.0).
- **#12 G4a_dev:** S2_LL clear 246 mm (trunk intrudes 54 mm), S3_R 290 mm. Not fixed: the only free left-lower position is at y -300 or below, which starts to read as a foot.
- **Gate misses beyond IoU:** limb_count 5/4 in ii/iii/G2 (skeleton merges strands through webs), fill 0.370 (just under the 0.371 band) in G2, torso width 0.652 in G4 (band <= 0.598).
- **Base metric (lowest 60 mm of silhouette):** G1a_ii 76 mm, G2 94, G4 94, G1a_iii 158, G1a_i 400.

## 4. Evan's r07 notes, answered bluntly
- **"a bit squid like":** reduced, not gone. Arms are twisted-rope bundles with lace buttresses (not smooth tubes) and the head is an ogive hood. But the trunk is still a smooth body with sparse cords, so the figure now reads "hooded bullet / candle figure" more than lace-web creature. c01's tree-root surface across the whole mass is not here; that is the next pass.
- **"gothic and beksinski":** vertical/elongated trunk (apex at 428 mm), pointed-arch ribs around the maw, flying-buttress webs; decay/bone surface is only shader grain and a bone tone on ribs/webs. Reads gothic, not Beksinski.
- **"base that would not sit flat":** G1a_ii best (hangs, 3 thin tips, nothing horizontal), G1a_iii good (one diagonal rope plus drops), G1a_i weakest (two thin strands trail horizontally along the bottom).
- **"two-legged":** no pair of lower limbs from a hip in any study; lower limbs differ in thickness (R0 12-58), length, angle and bend direction; counts 4-7 + tail. The shelf arm at lower left (G1) is a shelf, not a leg, but together with the cascade could still read as a stance from far away; judgment, not measured.
- **Vertical maw:** kept, 1.33-1.37x mask area, flanked by pointed-arch ribs.
- **Iconic smiley:** reads at 128 px and in the front render; strokes 14 mm (spec 15 at D 230).
- **c01 comparison:** silhouette-level IoU 0.60-0.61. c01 has lace everywhere, wide web wings and a mass of roots; mine has a smooth trunk with webs only under the arms and between strands, so it is still much cleaner and heavier. The bottom cascade (G1a_ii) is the closest passage.

## 5. Weak points to fix next
Plates are still slabs from the front; trunk surface is bare between cords; cords can look like segmented bone (no continuous sinew); the mask rim is slightly serrated where the bezel meets the hood; the pendant tail of G1a_i and the fish-like wedge tails of G2/G4 are bulky; webs have straight free edges.

## 6. Reproduce
`python3 build.py G1a_ii` (25 s) -> `python3 render_comp.py G1a_ii --views front,tq --mask --samples 24` (4 min) -> `python3 run_checks.py` -> `python3 make_sheets.py`. Files: `renders/study_<id>_{front,tq,mask}.png`, `contact_sheet.png`, `silhouette_sheet_128.png`, `checks.json`. `build/` holds large meshes (gitignored).

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-17 | cad-lead | Initial creation: round-08 composition + character pass | [PROVISIONAL] |
