# Coherence review A of r11 H (design-principles / gestalt lens)

[PROVISIONAL] Reviewer A, 2026-11-19. Scope: refinement of finer details of the LOCKED base model H (Evan r11 hd). No redesign. Reviewer B (Beksiński lens) worked independently.
Inputs: `teams/cad/composition_r11/renders/study_H_front.png` (1200x900 perspective render, all pixel metrics), `build/H.npz` mesh (orthographic silhouette, geometry metrics), `review/rounds/round-11/images/H*.jpg`, `study_H_{tq,close,sideL}.png`, composition_r11 README, DESIGN_PRINCIPLES.md (all), DECISIONS r05-r11, aesthetics STATUS.
Scripts + outputs live next to this file (`d0..d9_*.py`, `*.json`). Run order: `d1_mesh_sil.py` (needs gitignored `build/H.npz`; writes `mesh_sil.npy`, deleted from the commit) -> `d4`, `d7`; others run from the PNG alone. `python3 d?_*.py` from this directory (not `-I`; scripts import `common.py`).

## 0. Verdict

**MIXED, leaning cohesive.** Reads as one creature with a clear mask > maw order. Does not read as "scattered dense objects" in the silhouette, value masses, or detail distribution. It does start to read as scattered in four places: (1) the second-rank slot is contested (maw is outranked by the left-shoulder bead cluster and the upper-left shelf lip); (2) three near-identical bright shelf bars at the periphery read as attached trays, not grown limb ends; (3) the mask is held, but the hold is invisible from the front (6 tiny rings); (4) the plants have not been designed in, and the assumed foliage fills 86% of the one big rest area (left wedge). The lower root tangle (29.6% of figure area) is an even mid-tone mat. None of these needs a redesign; each is a one-axis study.

Confidence: pixel numbers are single-light, single-camera, one render; saliency is a crude centre-surround model, not eye tracking. Treat ranks as relative.

## 1. Assumptions (stated once)

- Scale: figure bbox width in render = 779 px (d0) = 914 mm envelope, so 1 px = 1.172 mm. At 3 m, 1 px = 1.34 arcmin. Render wall median lum 33.8/255 (13%), i.e. already at the DESIGN_PRINCIPLES s.0 target (<= 15%). Perspective render: sizes at depth differ slightly from mm.
- "3 m acuity blur": Gaussian sigma 3 arcmin = 2.2 px (dim room, low contrast; 4 m = 3.0 px). "Squint": sigma 1.5% of piece width = 11.7 px = 13.7 mm = 15.7 arcmin at 3 m (DESIGN s.8 recipe). G64: 64 px across the piece (~14 mm/px, ~4 m dim-room limit per s.0).
- Figure mask = pixels brighter than a quadratic wall fit by 14 levels (d0). It misses shadowed undersides: that is the *perceived* lit figure (29.9% of the 780 px square). The geometric silhouette (mesh, orthographic, 1.5 mm/px) fills 44.4% of the 914 mm envelope (d4 `fill_ratio_geometric`; composition_gate says 0.4395, torso 0.4512 matches mine 0.4513, wedges 6 matches). So roughly two thirds of the geometric mass is visible as lit form at 3 m; the rest is lost edge (good per 1.10, but it also weakens the shelf undersides and limb roots).
- Plants (not in the model): assumed pot 150 w x 130 h + foliage 260 w x 320 h upright, or vines hanging ~380 mm. Mock only.

## 2. Diagnostics (numbers trace to the JSON named)

### 2.1 Squint / 3 m blur (`d2_squint_sheet.png`, `d2_squint.json`)
- Brightest squint blob is the mask (peak 243); next non-mask peaks are 0.60 (upper-left shelf lip), 0.59 (left-shoulder bead cluster), 0.54 (left lip of the maw), 0.51 (right shelf lip). No non-mask region reaches 85% of mask lum at acuity blur (`nonmask_comp_ge_85pct_of_mask_lum` = 0). Mask median lum 222 vs lit flesh 95 (2.3x) vs wall 34 (6.6x) (d9). #1 is unambiguous.
- Cover-the-mask test (tile 6): the eye lands on the upper-left shelf lip, then the shoulder beads. Not on the maw. That is the hierarchy gap (see 2.5).
- G64 (tile 4): reads as a figure: head disc, dark vertical maw, three horizontal bars (shelves), a dense lower mat. Creature class is "tentacled figure with its arms out holding trays". Passes at 64 px.
- Squint tile 3: forms group into a spine (mask > left trunk > lower-left shelf arm) + right arm/shelf + lower mat. The maw is a clean dark vertical void. Good.

### 2.2 Value structure (`d3_value_sheet.png`, `d3_value.json`)
4 wall-relative levels (cuts: wall+10, 90, 165; Otsu cuts landed on the wall gradient and were discarded).
- Top level (>165): 75% inside the mask raw, 84% at 3 m acuity, 97% at squint (`top_level_in_mask_frac`); components of top level outside the mask >= 0.5% of envelope: 0 at acuity and squint, 0 raw. Passes DESIGN #4 on this render (CAD's own checklist marks #4 failed on its measure; mine is a different test, see 5).
- Figure area by level at acuity: shaded flesh 51%, lit flesh 36%, top 12.5%. Lit flesh (level 2) forms 6 components >= 0.5% envelope at acuity, 4 at squint; top 3 hold 88% of lit mass at squint. Value masses group into few shapes: mask / one lit "C" chain on the left (head > left shoulder > left shelf arm > lower-left shelf) / shelf lips / lower mat. Passes the notan test.
- Weak spot: the lit shelf lips (p90 lum 164 UL, 140 UR, 117 LL vs root-tangle limb median 80, d9) are the second-brightest large shapes. They make three bright bars.

### 2.3 Silhouette connectivity and rest areas (`d4_silhouette_map.png`, `d4_silhouette.json`)
- 1 connected component carrying 99.94% of area; the only island is 241 mm2 (a small fragment; README flags 8 floating fragments). No scattered islands in the silhouette.
- Holes: 16 enclosed, 1 >= 0.5% envelope; holes = 5.5% of filled area. They are the web perforations; small and numerous = rest texture, not rest area.
- Open wedges >= 2% envelope: 6 (12.8, 5.1, 5.0, 3.9, 2.8, 2.2 % of envelope); >= 4%: 3. Hull solidity 0.54, negative space in hull 46%. Passes the gate bands. The 12.8% wedge is the left one, between the upper-left and lower-left shelves. It is the single large rest area; the lower right wedge (5%) is split by the whip.
- Gate torso blob width 0.451, area 0.271 (c01 0.479/0.298).
- Balance: area centroid x = +0.2 mm (0.03% of envelope), L/R area ratio 1.02, centroid y 55.6% from top, mirror IoU 0.46. Mass is dead-centre but shapes are asymmetric: static in mass, lively in shape. DESIGN 1.9 wants 1.1-1.5; with plants it moves to 1.30 (see 2.6), which is better.
- Straight silhouette runs: S3_LL front-top edge 266 mm, S1_UL 148 mm, S2_UR 82 mm (limit 120 mm, #11). Two shelves read as ruler-straight bars. The flat tops are locked; the straightness of the edge as seen from the front is not.
- Features (opening residual, % of envelope): body 43.0; next three (the shelves, by position) 0.99 / 0.91 / 0.88. Max/min 1.125 (inside the "equal rival" 0.8-1.25 window for same-class items); they differ in length only ~15% (hand trace 290/260/304 mm).

### 2.4 Edge / detail density (`d5_detail_heatmap.png`, `d5_detail.json`)
- Peak of both relative detail density and absolute edge density is in the maw (`peak_rel`, `peak_abs` region = maw). Maw = 6.3% of figure area, 19.6% of detail energy (3.1x figure mean; abs edge 2.3x). Mask: 10.6% of area, 5.4% of detail (0.51x mean): clean, quiet. This is the Beksiński/painter ordering DESIGN 1.10/1.11 asks for. Not uniform: Gini 0.55, densest 10% of figure holds 37-39% of detail, densest 25% holds 65%. Area at >= 50% of peak density = 4.1% of figure (limit: <= 50%).
- Tertiary level has no hierarchy: eye patch 0.94x mean, shoulder eyes 0.78x, shelves 0.66-0.91x, root tangle 0.95x, whip 1.31x, neck lattice 1.00x (abs 1.2x). Everything below the maw sits at ~1x. That is where "dense objects" can creep in: many things at the same medium weight.
- Root tangle = 29.6% of figure area, 27.9% of detail energy, density 0.95x: a uniform mat.

### 2.5 Flow and hierarchy (`d6_flow_overlay.png`, `d6_flow.json`)
- Saliency order (centre-surround DoG, 3 scales, winner-take-all, 8 fixations): 1 mask, 2 mask (eye), 3 left-shoulder beads, 4 mask, 5-6 upper-left shelf lip, 7 mask, 8 right shelf lip. The maw never makes the first 8. Region peak saliency relative to mask: shoulder beads 0.89, UL shelf 0.76, UR shelf 0.66, maw 0.64, root tangle 0.61, LL shelf 0.57, eye patch 0.49. DESIGN 1.1 wants #2 = maw. The model says #2 = left-shoulder bead cluster (white pearls on the trunk, 3-4 spheres) and the UL shelf lip. Caveat: teeth are 3-8 px at 3 m; the maw reads by darkness and size, and the model undervalues dark voids. Still: nothing makes the maw win.
- Hand-traced principal curves (overlay): spine from the mask down the left rim of the maw to the root hub (464 mm, one gentle S); three shelf arms leave it like spokes (290/260/304 mm); lower-left and lower-right sweeps (476/484 mm) carry the eye down and out; whip curls back (259 mm). The spine and the lower sweeps are continuous and good. The lower-right sweep exits the composition at the bottom right corner (flow leaves the piece). The three shelf arms terminate in flat bars (end stops): the eye reaches them and stops; nothing leads from a shelf back to the head except the upper-left arm, which passes behind the mask.
- Limb tips (skeleton, 11 excluding the head spur): inward tangent within 45 deg of the bearing to the mask for 9 of 11; the limbs radiate from the body, no tangent tip-to-tip kisses found.

### 2.6 Plants (`q3_plants_mock.png`, `d7_plants.json`) MOCK
- Upright mock: plants cover 86% of the 80,082 mm2 left wedge (trailing: 68%); the upper-left plant tops out 258 mm above the envelope, upper right 123 mm; area centroid moves from y -51 to +91 mm, L/R ratio 1.02 -> 1.30 (left heavy: two plants left, one right), plants raise the figure from 44% to 73% of envelope.
- Pots and foliage will be the largest saturated colour in the piece (the creature is near-monochrome: median figure saturation 0.40 but one hue; only the veined eyes break it; 66% of saturated-pixel mass is in the head patch, d9). A dull pot and dark foliage keep the creature the subject; terracotta (as in the mock) would not.
- The straight shelf edges (2.3) are partly hidden by plants; pots add three more identical vertical masses (sized alike).

### 2.7 Palette and accents (`d9_misc.json`)
Near-monochrome tan flesh; mask cream (CV 0.077 of face luminance: flat); eye accents red/orange at head patch (66% of saturated px), lower-left arm (26%, cluster 167 px), small elsewhere. White bead cluster at the left shoulder (598 px) is the brightest non-mask small item. One material family + one accent hue = strong unity, which is the main reason H does not read as scattered.

## 3. Read against DESIGN_PRINCIPLES (H, as built)

| Principle | Read | Evidence |
|---|---|---|
| 1.8 Unity | PASS. One body, one palette, limbs grow from one trunk, shelves are limb ends in limb texture. Exception: mask is a separate object by design; its hold is not visible front-on. | d4 1 component; d9 palette |
| 1.1 Hierarchy | PARTIAL. #1 mask strong. #2 maw by detail and darkness, not by saliency; shoulder beads and UL lip contest it. #3 undefined (eye patch, shelves, whip all ~equal). | d6, d5 |
| 1.2/1.3 Value, shape | PASS. 3-4 value masses. Body 43% vs next shapes < 1%: one dominant mass. | d3, d4 |
| 1.7 Rhythm | MIXED. Tentacles differ in length/curl (good). Shelves are three same-size bowls with identical lip and 3-4 under-ribs (repeat unit). Teeth graded (good). Grip rings: 6 equal small rings in a circle on the rim (gear/rivet read, 1.7 reject rule: ring of repeated units around a focal object; small, but present). | d4 features; close render |
| 1.1/1.9 Focal | PASS for the mask; head is upper-centre-left (mask centre x -32 mm), maw under it, offset 15 deg roll keeps the totem stack from being static. | renders |
| 1.6 Rest areas | MIXED. Left wedge 12.8% is real rest, and plants will fill it. The right side has the whip; the head dome is a large smooth quiet mass (rest, good). Lower mat has none. | d4, d7 |
| 1.4 Silhouette | PASS (connected, 6 wedges). Reads as a Y-pose humanoid with trays; the arms-out symmetry is mild. Two flat 148-266 mm edges fail #11 spirit. | d4 |
| 1.10 Lost/found | PASS. Undersides dissolve (1/3 of geometric mass lost); mask crisp; teeth crisp. | d4 vs d0 |

## 4. Ranked refinements (max 8; each one axis; Evan-loved items listed under risk)

1. **Left-shoulder bead cluster: lower its pop.** Element: 3-4 white spheres + eyes at the left trunk (render x 460-545, y 370-480). Change: lid/bead value toward flesh, scale -25%, keep eyes. Why: it is saliency #3 (0.89 of mask) and out-ranks the maw (0.64). Expect: second fixation lands on the maw; head patch remains the only bright-bead site. Risk: Evan liked E2 clusters and "bulging, seething, veiny eyes"; he did not specify a count of sites. Keep eyes, change their contrast. Study: shoulder cluster contrast only. (Q1)
2. **Make the hold visible from the front.** Element: 6 grip rings on the mask rim. Change: 3 larger graded fingers + thumb (largest nearest the wrist), short visible wrist under the lower-left rim. Why: from the front the mask reads as a sticker/badge on the head dome (arm hidden at x 0, y 168 behind it); six equal rings read as stitches/rivets. Expect: "the creature is holding it to deceive" reads at 3 m, ties mask to body (unity). Risk: structural spec is the rod + pad, fingers carry no load (README s.3 Fingers), so free; do not add more than 4 nubs and keep them graded. Study: finger count/size only. (Q4)
3. **Plant plan before more geometry.** Element: three shelf plants. Change (design rules, not geometry): neutral dark pots; one trailing plant on the lower-left shelf so the left wedge stays open; upper-left plant low (it otherwise adds 258 mm above the envelope next to the head). Why: assumed upright foliage fills 86% of the left wedge and shifts the centroid up 142 mm. Expect: wedge survives; plant stays tertiary. Risk: shelf spec locked (flat top >= 150x150, >= 300 clear) and unchanged; Evan's "creature covered in plants" is dead (r04) but plants on shelves are the brief. Study: plant type per shelf (mock). (Q3)
4. **Root tangle recedes in value.** Element: lower mat (x 230-990, y 610-845). Change: value -25 to -40%, keep shapes and density (Evan loved D2 density). Why: 29.6% of area, 27.9% of detail, uniform 0.95x; at squint it is the second-largest mid-tone mass and competes with head + maw for rank. Expect: three big sweeps still read; face + maw lead; wall-to-limb lost edges increase. Risk: the lower sweeps are loved gesture (T1/T2); darken only the lace fillers/leaves, not the three principal limbs. Study: albedo of filler lace only. (Q2)
5. **Shelf lips to limb value.** Element: lit shelf lips (p90 164/140/117 vs limb median 80). Change: lip albedo/spec to <= 1.3x limb median; no geometry. Why: UL lip is saliency #5-6 and the three bars read as separate trays. Expect: shelves read as limb ends. Risk: none to geometry; locked shelf spec untouched. Study: one material parameter.
6. **Vary the three shelves.** Element: shelf bowls. Change: different rib count (3/4/5), front-edge scallop on the 266 mm S3_LL edge and the 148 mm S1_UL edge, size +/-15% (keep flat top >= 150x150, all three already differ 158x182 / 194x182 / 188x158). Why: 0.99/0.91/0.88% area, same lip = repeated unit; two straight runs > 120 mm. Expect: less "tray set", more grown. Risk: flat-top clear zone; do not scallop the top plane. Study: lip outline + rib count only.
7. **Mask value and volume.** Element: mask face (CV 0.077, 2.3x flesh, 6.6x wall; DESIGN target mask 1.7-2.0x body). Change: with Evan's volumetric directive (r11 h), let a gradient cross the face (shading from curvature) and drop mean value 10% (222 -> ~200). Why: flat cream = sticker; keeps it brightest (next item 0.60). Expect: object read, still #1. Risk: must stay the unique top-level region (currently 0 rivals). Study: value only, after the volume study exists.
8. **Neck hinge (low confidence).** Element: pale ladder strands between mask bottom and maw top (render x 505-612, y 322-398). Change: thin/darken half of the strands or let the wrist (item 2) occupy it. Why: it is the hinge between the two top focal elements and looks busy by eye; numerically only average (1.0x rel, 1.2x abs). Expect: cleaner mask-to-maw transition. Risk: may be loved texture; do after 2. Study: strand count.

## 5. Notes against other documents

- CAD checklist (composition_r11/checks.json) fails #4 (mask brightest) for H although my V4 test passes (top-level outside the mask: 0 components >= 0.5%). Different test and luminance scale (their json: mask 87.8, flesh 28.0, wall 13.2). Not reconciled here; flagging only.
- Mask is in `H.npz` (mask front z 233); the disc added in d4 coincides and is a no-op guard.

## 6. Proposed questions for Evan (swipe: love / like / dislike + optional note)

Each is paired with a mock (labelled in the image) and phrased so like = apply the change.

- **Q1** `q1_eyes_mock.png`: "Eyes are spread over the head, left shoulder and two arms (left). Gather them on the head patch only (right)? Like = gather them; dislike = keep them spread." Decision: eye-site count (item 1). Mock removes eyes by median fill; real change is lower contrast, not deletion.
- **Q2** `q2_tangle_mock.png`: "Lower root tangle 40% darker, same shapes (right), so the face and maw lead? Or keep it full-bright (left)? Like = darker." Decision: item 4 (D2 density vs value).
- **Q3** `q3_plants_mock.png`: "Plants will fill the left gap. Left: upright bushy. Right: trailing vines. Which do you want on the shelves? Like = trailing, dislike = upright. Mock plants, assumed size." Decision: item 3, the largest unknown effect on coherence.
- **Q4** `q4_grip_mock.png`: "Now the creature holds the mask with six tiny rings (left). Show a visible grip of three fat fingers and a thumb (right, rough mock)? Like = fat fingers." Decision: item 2.

Priority if only two fit a round: Q3, Q4.

## 7. Files
`d0_mask_overlay.png` (figure mask), `d1_mesh_silhouette.png`, `d2_squint_sheet.png`, `d3_value_sheet.png`, `d4_silhouette_map.png`, `d5_detail_heatmap.png`, `d6_flow_overlay.png`, `q1..q4_*_mock.png`, JSON next to each script. All PNG <= 1 MB, PIL-verified (`common.save`).

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-19 | aesthetics-reviewer-A | Initial creation: coherence review A of r11 H (diagnostics d0-d9, verdict, refinements, questions) | [PROVISIONAL] |
