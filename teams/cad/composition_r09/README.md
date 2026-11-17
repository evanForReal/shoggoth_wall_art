# composition_r09: round-09 studies (3 distinct tentacles, uncrowded, octopus wanted)

CAD worker, 2026-11-17. [PROVISIONAL] Not boarded; not committed. r08b, r08c untouched. Body = r08c G1a_b trunk (ribbed, narrow, jagged maw, hanging lower body), mask D 200. Data: `checks.json`, `measure_extra.json`, `checks/`. Engine = r08c engine + new `build.py` (smooth tentacles, suckers, eyes, teeth, planform-limited shelf carve).

## 1. Built (all four studies)
- **No crown.** No tine, spire or anything above the head; a flesh ring (r 10-17 mm, heaviest over the upper rim) closes over the mask edge, mask recessed. The trunk top is a quiet dome.
- **Three shelf tentacles, one smooth sweep each, root to tip:** massive (root dia 104 mm / 100 in S4), medium 62, whip 30; sucker rows on the inner face of the two larger (11 and 8; S3: 16 on the dominant limb), varied size 13-30 mm; shelf grip = tube passes under the plate and 5-6 root fingers hug the rim (flush with the top lip). Other limbs: 2-3 thin hanging strands (S3: two stubs). Webs: 0.
- **Maw:** vertical jagged almond 150 x 316, 1.09-1.10 x mask area, dark throat (maw luminance 10.2-11.6%), no strands. 39 teeth: 26 front row on the rim (base 9-16 mm, length <= 3x base, tip r 0.75 mm), 13 second row deeper and shorter (base 7-13), one long fang (base 15, length 44), ~14% broken (flat top). Fab caveat: teeth project horizontally 20-45 mm over the cavity (cantilever, not print-up within 45 deg); needs a support/rotation decision before CAD.
- **Eyes (5 per study):** off-axis cluster on a flesh swelling beside the mask (side opposite the tentacles) with globes 64 (hooded lid, carved slit pupil), 40 (clouded: pale, no iris), 26 (turret, blown round pupil), 22 (ring lid); plus one 36 mm eye (hooded, slit) on the root of the massive tentacle. Sizes 22-64, tilts differ, lids differ, pupils differ. Globes protrude ~1.0 r in a flesh socket. Pupils < 45 mm globes are painted only.
- **Shelves (volume-measured largest free flat rectangle, clear 300 mm above all):** S1 154x192 / 196x182 / 178x170; S2 178x172 / 180x194 / 176x176; S3 184x184 / 196x160 / 172x180; S4 176x176 / 202x162 / 200x180. Shelves stacked at one x keep >= 396 mm between tops (plate underside is 94 mm deep, fingers add 12); S3 and S4 limbs are routed around every shelf's clear zone. Rendering: wall 13.2-13.6%, flesh 31-33%, mask 100%.

## 2. Studies
| id | idea | flow | weight / eye path |
|---|---|---|---|
| S1 | brainstorm 4+6 | body left, three limbs fan right: massive low, medium mid, whip rises to a top shelf; shelves 330/340/70 x, tops -330/68/446 | big dark limb first, medium second, whip last |
| S2 | 4+9 | body low-left, limbs climb a rising diagonal: massive to low shelf, medium to mid-right, whip up to the top shelf | eye climbs |
| S3 | 1 | ONE dominant limb: right shelf, around the bottom, low-left shelf, up the left edge, top-left shelf; two stubs | one long loop |
| S4 | 7 | body high, limbs droop down and hook up under shelves on both sides | gravity leads to the hooks |

## 3. Checks (c01 is no longer the reference)
| id | COMP | failed | gate (7) | verdict_excl_iou | gate values | IoU vs c01 (info) | torso_width_frac | wedges >= 4% (#10) |
|---|---|---|---|---|---|---|---|---|
| S1 | 5/13 | 1,2,4,5,6,7,11,13 | 2/7 | FAIL | fill 0.351, wedges 3, reach 1.10, limb_count 3 | 0.301 | 0.371 | 3 |
| S2 | 3/13 | 1,2,3,4,5,6,7,10,11,13 | 2/7 | FAIL | fill 0.342, wedges 4, reach 0.92, limb_count 3 | 0.343 | 0.397 | 2 |
| S3 | 3/13 | 1,2,4,5,6,7,8,10,11,13 | 3/7 | FAIL | fill 0.404, wedges 2, reach 0.21, limb_count 3 | 0.421 | 0.367 | 2 |
| S4 | 5/13 | 1,2,4,5,6,7,11,12 | 2/7 | FAIL | fill 0.348, wedges 4, reach 0.97, limb_count 2 | 0.420 | 0.383 | 4 |
Gate bands (fill 0.371-0.557, wedges 5-9, reach, limb_count 4-?) were fit to c01's webbed, many-limbed figure; the new brief (3 limbs, bare wall) fails them by construction. Torso width passes everywhere. The checklist's #6/#7/#8/#10 assume 6+ limbs and 12-25 mm tips; #2 (body %), #5 (maw:mask 1.0-1.2 vs <= 0.7 / >= 1.3) fail by brief; #13 balance fails in S1-S3 (weight right or low: centroid x -81 / -112 / -26 mm, L/R ratio 2.6 / 3.0 / 1.0), passes in S4. S2 and S3 have only 2 bare wedges >= 4% (brief asks 3); S3's big loop wedge is 28.6%. #3 fails in S2 (mask centre lower than 0.30 H from top).

## 4. Self-assessment vs Evan's verbatim notes (blunt)
- **"do not do a crown. it looks comical."** Met: nothing above the head. The remaining cartoon risk is the bright smiley on a pale-ringed round dome with a small eye cluster: it reads as a cute pet (a seal/pet-monster) more than horror at thumbnail size; the maw and teeth carry the menace.
- **"the flow towards the platforms is underwhelming ... distinct tentacles."** Largely met. Weights 104 / 62 / 30 mm are readable at 64 px; each limb is continuous, one curve, ends gripping its shelf. S1 and S2 best; S4 hooks read as legs-like loops (two long drooping limbs flank the body, an inverted-V: possible "stance" read); S3 reads as a pipe or frame around the wall, not an animal (the exact risk flagged in the brainstorm). Limbs are smooth tubes: no muscular detail, suckers are small pits.
- **"too crowded ... a thing for the eyes to linger upon."** Met in count (body, 3 tentacles, 2-3 thin hangers, 0 webs, 3 or more bare wedges in S1/S4). Weak spots: the lower trunk is a blunt capsule in S2-S4 with a couple of strands; the shaft mid-spans are plain and some will read as empty.
- **"tentacled, horrific, octopus-like with a distinct, vicious mouth and disturbing eyes (no contract to be symmetrical or healthy)."** Octopus-like: yes (suckers, long smooth arms). Mouth: vicious at 1 m (39 pale blades in a jagged slot), but teeth are small and sparse relative to the 316 mm slot and hard to see at 3 m. Eyes: asymmetric cluster, one clouded, slit/blown pupils, one on a tentacle; at full view they are small beside the smiley and the hooded 64 mm eye is the only one that registers as disturbing. The cluster hosts on a swelling, which reads as a goiter/growth, intended.
- **Other:** the trunk is still a bottle shape with parallel ribs (ribcage read); the tentacles lack any gothic/Beksinski surface; webs absent so the Beksinski lace is gone entirely. Teeth fab (cantilever) unresolved.

## 5. Reproduce
`python3 build.py S1` (45 s) -> `python3 render_comp.py S1 --views front,tq --mask --samples 24` (2.5 min) -> `python3 run_checks.py` -> `python3 measure_extra.py` -> `python3 make_sheets.py`. Contact sheet `renders/contact_sheet.png` (S1-S4 + r08c A). `build/` is large; not for commit.


## 6. Addendum: S5 and S6 (A's body, edited per Evan's notes)
S1-S4 untouched. S5 = r08c G1a_b body: ribbed narrow trunk (3 ribs per side + 2 maw ribs), mask D 200 at (8, 262), crown removed (flesh ring closes over the mask), hanging root cascade thinned from 7 to 5 strands (H1 3-strand bundle with hooked tip, H2 2-strand, H3 spiral tip, H4, H6; root dia 48-88 mm), 2 catenary-edged webs (one under the UR tentacle, one under the LL tentacle, each with a drip strand). A's three arms replaced by three single-sweep tentacles at A's shelf positions: massive (root dia 104) to LL (-335, -190), medium (62) to UR (335, 150), whip (30) to UL (-335, 285); suckers 11 and 8; rim-gripping fingers. Teeth: 52 (34 front + 18 back), 5 long fangs 40-46 mm (base 13-15.5), the rest 12-35 mm, tips drop ~0.5 L into the throat (about 27 deg below the wall plane, not horizontal), ~15% broken. S6 = S5 with eyes pushed: 66 mm hooded slit-pupil eye high on the trunk right of the mask, clouded 46 mm eye low-left off-axis, three small eyes (26 blown, 22 slit turret, 20) displaced on a right-flank swelling, plus a 36 mm slit eye on the massive tentacle root. S5 keeps the r09 cluster (64 hood-slit, 40 clouded, 26, 22, 36 on tentacle).

| id | COMP | failed | gate (7) | verdict_excl_iou | gate fails | gate values | IoU vs c01 (info) | torso | maw:mask | maw lum % | wedges >= 4% |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S5 | 5/13 | 1,2,4,5,7,8,10,11 | 4/7 | FAIL | fill, limb_count, iou_vs_c01 | fill 0.338, wedges 6, reach 0.45, limbs 5 | 0.533 | 0.449 | 1.09 | 17.3 | 2 |
| S6 | 5/13 | 1,2,4,5,7,8,10,11 | 4/7 | FAIL | fill, limb_count, iou_vs_c01 | fill 0.347, wedges 6, reach 0.42, limbs 5 | 0.538 | 0.469 | 1.09 | 19.3 | 2 |
Shelf flat tops (volume): 178x172 / 180x194 / 174x174 mm, 300 mm clear above each (checks.py #12 also 300). Wall 13.1-13.2%, mask 100%. #4 (mask the single brightest) margin falls to 13 (S5) and 6 (S6) at p99.5 because pale teeth and the clouded eye approach the mask value; still passes the top-level test only barely in S6. Gate failures are now fill 0.34 (band >= 0.371), the limb_count band, and c01 IoU. Torso 0.45-0.47 and wedges 6 pass (S1-S4 had 2-4 wedges).

Self-assessment vs Evan's notes:
- **A, "extreme improvement":** the body is A's. Ribbed trunk, narrow shoulders, root cascade, jagged maw and web texture are back, so it is no longer a bowling pin; the cascade and root skirts do the gothic work. Less rotten than A: webs are 2 small catenary wedges, the trunk surface between ribs is still smooth and the arms (now tentacles) are smooth tubes. A's lace is gone.
- **"do not do a crown":** met. Head is a quiet dome plus the flesh ring. At thumbnail size the bright smiley on a round pale-ringed head still reads cute; the teeth and eye are what fight that.
- **"flow towards the platforms ... distinct tentacles":** met in weight (104 / 62 / 30) and continuity. But with A's shelf positions the arms are short (150-250 mm visible) so they read as stubs with shelves, not long tentacles; the massive one at LL is hidden behind the cascade root, and the whip UL is a thin stalk. The flow is better than A, weaker than S1/S2 where the limbs are long.
- **"too crowded":** denser than S1-S4 by design (cascade 5 strands + ribs + 2 webs + eyes), clearly lighter than A. Detail is concentrated at mask, mouth, eyes and cascade; the lower body is busy.
- **"tentacled, horrific, octopus-like, vicious mouth, disturbing eyes":** the mouth now reads vicious at full view: 52 pale blades with 5 long fangs in a dark slot (maw luminance 17-19%, was 10-12%). Fab caveat remains: teeth angled 27 deg below the wall plane are overhangs on a face-up print (needs rotation or supports, CAD decision). Eyes: S6 reads better than S5; the 66 mm hooded slit eye registers at full view as a face feature; the clouded eye reads as a white ball (low contrast, looks like a bead, not clouded flesh); the small displaced eyes read as bumps. S5's cluster sits on a swelling beside the tentacle root and is crowded by it.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-17 | cad-worker | Initial creation: round-09 studies | [PROVISIONAL] |
| 2026-11-17 | cad-worker | Added S5, S6 (A body + tentacles + bigger teeth + pushed eyes), contact sheet to 7 images, section 6 | [PROVISIONAL] |
