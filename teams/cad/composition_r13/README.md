# composition_r13: H13 (refined hero, body scaled to air out shelves) and E1 (wider envelope)

CAD worker, 2026-11-19. [PROVISIONAL] Not boarded. Earlier packages untouched (code copied from `composition_r12s`, `checks.py` from r11). Directives: Evan r11 H loved; r12 K1 one umber glaze (like), K2 keep eye groups, K4 grown shelves (like), K3 plants "a mix of both ... air out (expand arm length) the composition", only C1/H layout kept. H layout, pose, holder, maw, cascade, ball S2 (180 x 108, grip tendrils) kept. All numbers below trace to `report.json`, `gap_reach.json`, `checks.json`, `arm_report_{H13,E1}.json`, `measure_extra_{H13,E1}.json`, `build/*_meta.json` (2 mm voxels, +-2 mm).

## 1. What changed vs r12s H + S2
| item | change |
|---|---|
| K4 plates (B R1, A ref. 6) | new `grown_plate_fn` (`build.py`): lobed planform (superellipse n 2.3 x 3-4 lobe harmonics x front-arc scallops, different per plate), flat top kept, underside belly tapering to a 5.5 mm rim, root flare (extra 34-42 mm thickness near the limb entry, smin k 40 into the limb), 4 / 5 / 7 ribs per plate (LL / UL / UR) placed at lobe peaks, starting on the limb surface (3 of them) or the flare, fanning under the plate and round the rim; every second rib hooks <= 6 mm over the top lip. Plate half-axes 108-112 x 108-114 (r12s 124 x 122), thickness at centre 66 / 74 / 82 (+ flare) |
| whip (R4) | forks off the S2_UR limb at x = plate cx - 133 (old departure was cx - 73, i.e. 60 mm toward the trunk); head waypoints re-shaped to drop away under the plate; length 515.5 mm (old 516.2), curl unchanged |
| patch (R5) | patch smin radius 34 -> 46 (lumps 14 -> 26), one albedo (K1): no tone step, straight seam gone in the render (a first try at k 64 gave a flat vertical step on the head side and was dropped) |
| cascade (R8) | start points spread over 166 mm of trunk bottom (y -118 .. -284, `STAGGER`), lengths 0.78-1.0 x (none extended: H1/H4/H5 end at the envelope); webs rebuilt on the new strands; 3 leaf shapes untouched |
| eye groups (K2) | none removed or resized relative to the body. In H13 they scale WITH the body (x0.84, absolute size -16%); arm eye rows unscaled (arm thickness unscaled). E1: unscaled |
| finish (K1) | `render_comp.py`: one umber albedo for kinds 0-5, 10 (trunk, limbs, lace, shelves, patch, ribs, tendrils); bone only for mask and teeth; eyes keep colour; veins stay dark red; recesses dark; no height-based albedo ramp on flesh |
| arm re-root | ball arm root search re-run: H13 exit (-24, 173), E1 (-16, 192) (r12s (-24, 192)); same boss, pad, rod, bore |

## 2. Air-out: H13 (inside 914) and E1 (wider)
H13 body-group scale **s = 0.84** (spine, maw, patch + its 12 eyes, shoulder cluster, cascade, meridians, teeth, ball centre; ball NOT scaled: D 180 kept, gap 66). Plates outer edge x +-452..456 (r12s: clipped at 457). The shelf arms cannot grow much inside 914 (plates were already at the edge): the gain is trunk shrink + smaller plates. E1: s = 1.0, plates' outer edge x +-600, **overall bounding box 1206 x 842 mm (x -602..602, y -456..384)**, z 294; H13 box 914 x 732 mm (x -456..456, y -408..322), z 276.

Gap = min 2D distance (mm, front view) from the plate silhouette (planform x contiguous run below the top, flare at the limb entry included) to the body-group silhouette (trunk/head + patch disc + ball + shoulder cluster); `measure_gap.py`.
| plate | r11 H | r12s H+S2 (before) | H13 | E1 |
|---|---|---|---|---|
| S1_UL | 76.0 | 80.0 | 102.2 | 250.0 |
| S2_UR | 76.0 | 76.0 | 104.0 | 231.0 |
| S3_LL | 51.9 | 51.9 | 98.5 | 213.5 |
To trunk/head sweep only (no ball / patch / cluster): UL 101.3 / 101.3 / 143.2 / 262.4 (r11 / r12s / H13 / E1), UR and LL identical to the above. H13 vs r12s: +22 / +28 / +47 mm (+28% / +37% / +90%). Whether that reads as "less cramped" is for the render; the 0.84 body also leaves 182 mm of empty wall under the piece (height 732 of 914).

**Shelf reach** (root = limb centreline start, z 35; plate centroid from the planform; `gap_reach.json`):
| shelf | | r11 H | H13 | E1 |
|---|---|---|---|---|
| S1_UL | dx / horizontal (x,z) / 3D / limb path | 230 / 246 / 281 / 408 | 258 / 271 / 314 / 443 | 387 / 396 / 418 / 537 |
| S2_UR | | 265 / 279 / 293 / 409 | 277 / 288 / 305 / 423 | 412 / 419 / 429 / 545 |
| S3_LL | | 265 / 279 / 293 / 462 | 277 / 290 / 309 / 482 | 412 / 421 / 430 / 579 |
(mm; limb path = whole limb length incl. the run through the plate; plate masses are not computed here). Plate masses not computed (r11 plate 34-94 mm thick, now 5.5 mm rim to 66-82 mm + flare at centre); Structural must re-check shelf-arm moments with these reaches.

## 3. Limits (all measured; `report.json`)
| limit | H13 | E1 |
|---|---|---|
| relief max z <= 300 | 276 | 294 (6 mm margin; the patch blend raised the flesh peak under the ball, ball front 296) |
| shelf flat top >= 150 x 150, 300 clear | UL 164 x 162, UR 180 x 170, LL 156 x 172, clear 300 | same plates, same numbers |
| lever <= 250 / CoM off axis <= 50 / tilt <= 35 | 124.5 / 28.1 / 15 | 131.1 / 14.3 / 15 |
| mask mass <= 0.8 kg (2 mm shell, 10%, PLA, +5%) | 0.743 | 0.744 |
| core >= 22 / cover >= 5 | 52.0 / 20.8 | 50.1 / 19.9 |
| free-span clearance >= 6 | 24.4 | 22.4 |
| pad >= 70 x 30 | 70 x 52 | 70 x 52 |
| rod to seat normal <= 35 deg | 11.7 | 4.2 |
| arm part x,y,z vs 256 bed | 100 x 100 x 180 | 100 x 118 x 202 |
| ball (D x depth), ball to rest of piece | 180 x 108, 34.0 mm | 180 x 108, 28.6 mm |
| mask part extents | 194 x 188 x 128 | 194 x 186 x 136 |
All pass. Ball kept at 180 in both. Mass basis as r12s README s.1 (shell/infill is an assumption; 15% infill fails).

## 4. Plant proxy view (PROXIES, not designed plants, not measured)
`renders/study_{H13,E1}_front_plants.png`: upright foliage (17 blades, ~260 x 320 mm above the rim, grey-green) in a dark muted pot on **S2_UR** (open wall above, away from the body, whip below); trailing vines (9 strands, 360 mm) on **S1_UL**, (320 mm) on **S3_LL**, hanging over the plate fronts into the empty left wedge. Pots 100-140 dia x 90 mm. Caveats: upright pot + foliage = 410 mm above the plate (300 clear is spec; UR has open wall above it, the top reaches y 560, outside the 914 box); LL vines cross the lower-left cascade tips (H1) in projection; UL and LL stacks cover the left wedge, so the left is plant-heavy and the body stays clear. Upright on the left was rejected (coherence A: 86% of the left wedge).

## 5. Checklist and gate (information only; `checks.json`)
| | H13 | E1 | r11 H |
|---|---|---|---|
| DESIGN_PRINCIPLES #1-13 | 7/13, fails 4 5 7 8 10 11 | 8/13, fails 4 7 8 10 11 | 7/13 (4 5 7 8 10 11) |
| composition gate | 3/7, FAIL (fill 0.346, torso 0.350, limb_reach 0.755, iou_c01 0.506) | 4/7, FAIL (fill 0.272, torso 0.348, iou 0.452) | 6/7 |
H13 loses the gate on silhouette metrics because the body is smaller (torso_width_frac 0.35 < 0.36 band) and the piece fills less of the envelope; E1 fill 0.27 is below the 0.37 band because the box is wider. #4 (mask brightest): fails both (as r11 H; bright eyes / teeth). Not tuned to the gate.

## 6. Known issues
- H13 airing is modest (+22..+47 mm gap) because plates already sat at the 914 edge; the true extension is E1 (+170..+190 mm gap, width 1206). Evan's envelope call.
- H13 eye groups are 16% smaller in absolute size (uniform scale); the ball (180) is now as wide as the head (head ~178). The patch is mostly behind the ball; only the right-edge eyes show (as r12s).
- E1 relief 294 (6 mm margin); E1 ball-to-rest 28.6 mm.
- Plates: rim 5.5 mm = 3 voxels (nominal); fingers/ribs hook 4-6 mm over the top lip; `clear_above_footprint` on S3_LL is 2 mm (hook / arm eye outside the flat rectangle; flat-top clear is 300, as r12s).
- Whip fork sits 6 mm outside the plate's inner edge in H13 (x 202 vs plate x_min 210): it reads as leaving the limb at the plate root, not 60 mm clear of the plate.
- Cascade strands shortened, none lengthened (envelope); lace (D2 webs) rebuilt on the new strands; leaves untouched. Floating-fragment count not re-measured.
- No FEA; Structural must re-check shelf-arm moments (reach table), and the thin plate rim.
- Side renders: E1 uses a wider camera (render_comp.py WIDE).

## 7. Files / reproduce
`studies_r13.py` (specs), `build.py`, `engine.py` (R13_VAR=E1 widens grid and clip), `heldmask.py`, `ball.py`, `render_comp.py` (K1 finish, `--plants`), `measure_arm.py`, `measure_extra.py`, `measure_gap.py`, `report.py`, `run_checks.py`, `checks.py`, `make_sheets.py`, `run_all.sh`. Renders: `study_{H13,E1}_{front,tq,side,front_plants,mask}.png`, `contact_sheet_r13.png` (r11 H | r12s H+ball | H13 | E1). Reproduce: `./run_all.sh; python3 report.py; python3 run_checks.py; python3 make_sheets.py` (R13_VAR=E1 for any E1 script run by hand; ~45 s per build, ~1 min per render).

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-19 | cad-worker | Initial creation: H13 and E1 | [PROVISIONAL] |
