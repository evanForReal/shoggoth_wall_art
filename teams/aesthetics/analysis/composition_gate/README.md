# Composition gate (RP-3 item 3)

Objective, repeatable composition numbers computed from a (front render, binary mask) pair and compared to bands derived from a trace of c01 (the loved target). Author: aesthetics-analyst (non-CAD). Tool: `tools/composition_gate.py`. Status: signed off (edit log).

```
python3 -I tools/composition_gate.py <render.png> <mask.png> [--ref teams/aesthetics/analysis/composition_gate/c01_metrics.json] [--no-diag]
```
Render and mask must be pixel-aligned (mask resized nearest if not). Mask: white = creature only. Exit 0 = PASS (all 7), 1 = FAIL. Output also carries `verdict_excl_iou` (see Limitations) and a warning if wall luminance > 15%.

## 1. c01 trace (manual steps, all of them)

Source: `review/rounds/round-04/images/c01_baseline-velvet-salon.jpg` (904x1200). Script: `trace_c01.py`.

1. **Automatic segmentation was tried and rejected.** HSV value > 0.27, green-hue removal: failed. The spotlight pools on the wall (V 0.2-0.4) and dark limb undersides (V 0.13, same as wall) overlap the creature's value range. Not usable even with morphology.
2. **Outline = manual polygon (~190 vertices)**, read off 3x zoomed, gridded crops (`/tmp` helper, not kept) in four quadrants. Estimated accuracy +-6 px on a 700 px creature (+-1%). Rules applied: creature body, hair/hood halo, mask, three shelf slabs (they are limb flares, per DESIGN_PRINCIPLES 2.1), root fringe to y 748 as one smoothed blob (hair-thin rootlets omitted).
3. **Excluded by hand:** both pots + plants, hanging string-of-pearls (x 130-175, y 210-350), ferns, lamp, sofa, side table, candle, floor, wall panelling, spotlight pools, the dripping strand tips beyond ~y 425 on the right arm.
4. **Maw filled** (it is an inset cavity in the chest, not wall; silhouette-level read).
5. **Interior see-through holes** (wall visible through the limb loops): 5 manual ellipses, kept as holes only where pixel V < 0.22: UL arm loops (293,258) and (257,330); UR arm loops (673,347), (633,372); ML arm loop (227,567). Small lace perforations (<~15 px) are left filled: silhouette, not texture.
6. **Envelope:** mask bbox 700 x 682 px at (103,82)-(803,764); padded to a centred 700 px square, resampled to 512 x 512 (`c01_mask_envelope.png`). `c01_mask.png` is the same mask at full frame (pixel-aligned with the JPEG) so the tool can take (jpg, mask) as a pair.
7. **Centreline:** skeleton of the hole-filled mask opened with a disk r = 1.5% of envelope (drops fringe/drips), spurs < 5% pruned iteratively. `c01_centreline.png` (512 px) and `c01_overlay.png` (cyan edge, magenta centreline, yellow limb tips, orange torso blob).

Trace risk: this is a hand trace of AI concept art. The sensitivity sweep below shows which metrics move with trace error.

## 2. Metrics (all on the 512 x 512 envelope unless noted)

| # | Metric | Definition | Maps to |
|---|---|---|---|
| 1 | `fill_ratio` | mask area (holes empty) / envelope area | s.4 #10 fill |
| 2 | `wedge_count` | connected background regions inside the mask's convex hull with area >= 2% of envelope [GENERAL] | s.4 #10 wedges |
| 3 | `torso_width_frac` | bbox width of the largest blob of the hole-filled mask after opening with a disk r = 12% of envelope [GENERAL], / envelope width | s.4 #2, RP-3 "torso width fraction" |
| 4 | `limb_reach_ratio` | mean over limbs of (distance from limb tip to torso blob) / torso width | RP-3 "limb reach / torso" |
| 5 | `limb_count` | pruned-skeleton endpoints with branch length >= 8% of envelope to first junction AND tip >= 5% outside the torso blob [GENERAL] | s.4 #6 |
| 6 | `head_vs_flesh` | median luma of head blob / median luma of flesh ring. Head = connected region >= 85% of max inside-mask luma after Gaussian blur sigma 1.5% (s.8 recipe); ring = mask pixels within 8% of the head blob, minus a 1% buffer | s.4 #4, #14 |
| 7 | `iou_vs_c01` | IoU of envelope masks (bbox-aligned, centred in square) vs `c01_mask_envelope.png` | RP-3 item 1 |

Diagnostics (not gating, in `--` output): `empty_hull_ratio`, `wedge_areas_frac`, `torso_height_frac`, `limb_reach_max_ratio`, `head_vs_wall`, `wall_luma`, head centre / area, per-limb tips.

**Deviation from the brief: opening radius.** Brief said ~6% of envelope. At 6% the c01 "torso" blob is 0.87 of envelope width (arms are 14-16% thick lace slabs and survive). 8%: 0.85. 10%: 0.62. 12%: 0.48, a clean head + chest + root column. Used 12%. The number is only comparable between renders using the same 12%.

**Wedge count at 2%** gives 7 for c01 (areas 8.5, 5.5, 5.0, 4.9, 4.7, 3.1, 3.1% of envelope). At the s.4 #10 threshold of 4% it is 5.

## 3. c01 values and pass bands

Tolerances are all [GENERAL]: chosen from trace sensitivity and the s.4 numbers, not fitted to any hero/study. Sensitivity sweep on c01's own mask (edge erode/dilate 4/8 px disk, rotate +-4 deg, mirror), produced by `sensitivity_sweep.py` (run `python3 -I teams/aesthetics/analysis/composition_gate/sensitivity_sweep.py` from repo root; output `sensitivity_sweep.{md,json}`). Source px on the 904x1200 frame; rotation about the mask bbox centre; render and mask transformed together.

| perturbation | fill | wedges | torso w | reach | limbs | head/flesh | IoU |
|---|---|---|---|---|---|---|---|
| base | 0.464 | 7 | 0.479 | 0.532 | 6 | 1.74 | 1.00 |
| erode 8 px | 0.409 | 7 | 0.463 | 0.422 | 6 | 1.67 | 0.88 |
| erode 4 px | 0.437 | 7 | 0.469 | 0.447 | 6 | 1.70 | 0.94 |
| dilate 4 px | 0.490 | 7 | 0.488 | 0.536 | 6 | 1.78 | 0.95 |
| dilate 8 px | 0.516 | 7 | 0.621 | 0.372 | 6 | 1.80 | 0.90 |
| rot -4 deg | 0.444 | 7 | 0.463 | 0.539 | 6 | 1.76 | 0.74 |
| rot +4 deg | 0.433 | 7 | 0.461 | 0.534 | 6 | 1.76 | 0.75 |
| mirror L-R | 0.464 | 7 | 0.479 | 0.533 | 6 | 1.74 | 0.52 |

| Metric | c01 | Band (pass) | Rule |
|---|---|---|---|
| fill_ratio | 0.464 | 0.371 - 0.557 | x0.80..x1.20; trace sweep spans 0.88x-1.11x |
| wedge_count | 7 | 5 - 9 | +-2; s.4 #10 wants >= 3 at 4% |
| torso_width_frac | 0.479 | 0.359 - 0.598 | x0.75..x1.25 |
| limb_reach_ratio | 0.532 | 0.372 - 0.692 | x0.70..x1.30; sweep spans 0.70x-1.02x (most trace-sensitive metric) |
| limb_count | 6 (3 shelf arms, 2 lower tentacles, 1 curl) | 6 - 8 | lo = s.4 #6 (>= 6); hi = c01 + 2 |
| head_vs_flesh | 1.74 (head luma 0.62, ring 0.35; wall 0.12, head/wall 5.0) | 1.22 - 3.48 | x0.70..x2.0 |
| iou_vs_c01 | 1.00 | 0.70 - 1.00 | c01 rotated 4 deg = 0.74; mirrored = 0.52. Below a ~5 deg rotation of c01 = a different figure. No upper bound |

Note c01 fill is 0.46, above the 35-40% eyeballed earlier: this trace fills lace perforations. DESIGN_PRINCIPLES s.1.6/#10 now use the gate band (0.371-0.557); the by-eye numbers are retired.
c01 has 6 skeleton limbs (DESIGN_PRINCIPLES s.2.1 now states this: 3 shelf arms + 2 lower tentacles + 1 curl; the by-eye 4 lower tentacles resolve to 2 lower + 1 curl in the skeleton; root tendrils are pruned).

## 4. Self-test

Hero masks: `make_hero_masks.py` (wall = per-channel quadratic fit to outer 5% frame; creature = luma > wall + 0.07 or saturation > wall + 0.12; close 3 px; drop specks; fill holes < 0.02% of frame). Shadow on the wall keeps wall hue/saturation, so it is rejected. Visual check: edge follows the geometry; shelf undersides and posts are included (real geometry).

| Render | Result | Pass | Failed | Values |
|---|---|---|---|---|
| c01 (jpg + c01_mask.png) | **PASS** | 7/7 | - | (the base row above) |
| r06 hero (`teams/cad/fullpiece_v2_1/renders/hero_front.png`) | **FAIL** | 4/7 | limb_reach_ratio 0.303 (< 0.372), limb_count 11 (> 8), iou 0.584 (< 0.70) | fill 0.472, wedges 5, torso 0.547, head/flesh 1.45 |
| r05 hero (`teams/cad/fullpiece/renders/hero_front.png`) | **FAIL** | 4/7 | torso_width_frac 0.758 (> 0.598), limb_reach_ratio 0.152 (< 0.372), iou 0.609 (< 0.70) | fill 0.446, wedges 5, limbs 6, head/flesh 1.39 |

Both heroes carry the wall-luminance warning (0.26 and 0.25 vs <= 0.15 required).

Reading: r06 = spiky clutter (11 skeleton limbs: fingers, posts, spines; limbs short relative to body). r05 = body is a single mass 0.76 of envelope wide, limbs hardly reach out of it (reach 0.15 vs 0.53). Matches Evan's verdicts ("blob", "clunky/cluttered"). Fill, wedge count and head contrast do NOT separate them from c01.

## 5. Round-07 studies (`teams/cad/composition_r07/renders/`)

Scored with `score_r07.py` (reads `study_<id>_front.png` + `study_<id>_mask.png`; writes `r07_scores.json`, `r07_scores.md`). Table below is `r07_scores.md`, re-run 2026-11-17 (identical output). Bands: s.3.

| id | pass | excl-IoU | fill_ratio | wedge_count | torso_width_frac | limb_reach_ratio | limb_count | head_vs_flesh | iou_vs_c01 | failed |
|---|---|---|---|---|---|---|---|---|---|---|
| G1a | 6/7 | PASS | 0.433 | 6 | 0.449 | 0.668 | 6 | 2.64 | 0.598 | iou_vs_c01 |
| G1b | 6/7 | PASS | 0.409 | 7 | 0.465 | 0.616 | 6 | 1.94 | 0.447 | iou_vs_c01 |
| G2a | 5/7 | FAIL | 0.44 | 7 | 0.619 | 0.444 | 6 | 2.35 | 0.495 | torso_width_frac, iou_vs_c01 |
| G2b | 6/7 | PASS | 0.42 | 7 | 0.584 | 0.518 | 6 | 2.35 | 0.466 | iou_vs_c01 |
| G3a | 6/7 | PASS | 0.416 | 6 | 0.469 | 0.495 | 7 | 2.33 | 0.532 | iou_vs_c01 |
| G3b | 6/7 | PASS | 0.416 | 6 | 0.467 | 0.524 | 8 | 2.34 | 0.518 | iou_vs_c01 |
| G4a | 4/7 | FAIL | 0.472 | 6 | 0.678 | 0.4 | 5 | 2.05 | 0.444 | torso_width_frac, limb_count, iou_vs_c01 |
| G4b | 4/7 | FAIL | 0.449 | 6 | 0.66 | 0.403 | 5 | 2.22 | 0.455 | torso_width_frac, limb_count, iou_vs_c01 |

Reading: all 8 fail IoU (0.44-0.60; c01-chiral, s.6). G2a, G4a, G4b also fail torso width (0.62-0.68 > 0.598: body not separated from limbs); G4a/G4b have 5 limbs (< 6). Fill, wedges, head/flesh pass in all 8 (weak discriminators, s.6). G1a is the closest study to c01 (IoU 0.598). Re-run `score_r07.py` when studies change.

## 6. Limitations

- **Single reference, hand-traced.** Bands are c01 +- tolerance, not a population. One trace, +-1% edge error. Reach is the most sensitive (0.70x under 8 px erosion).
- **Weak discriminators.** fill, wedge count and head/flesh pass both failed heroes. They are necessary-not-sufficient. The discriminating ones are torso width, reach, limb count, IoU.
- **IoU is chiral and gesture-specific.** c01 mirrored scores 0.52. A study that deliberately explores another gesture (DESIGN s.5 options) will fail IoU legitimately. For those, read `verdict_excl_iou`. IoU is the right check for a study claiming to be the c01 figure; the RP-3 item 1 build gate is a separate use of the same function; start value 0.60, ratchet to 0.85 (DESIGN_PRINCIPLES s.4.1 Build-gate).
- **Silhouette only.** No gesture-line, tentacle taper, straight-run, furniture-geometry or shelf-triangle checks (DESIGN s.4 #7, #9, #11, #12). No check that the mask is the single brightest region (#4 beyond head/flesh). Limb count cannot tell a limb from a shelf post or finger; bands cap it at 8.
- **Head = brightest blurred blob in the mask.** Wrong if a spec highlight, tooth ring or pale limb outshines the mask; check `head_centre_xy` in diagnostics (c01: 0.53, 0.12).
- **Wall luminance.** Head contrast vs wall is diagnostic only because renders use 25-26% walls versus c01 12%. Render at <= 15% (s.0).
- **Mask provenance.** For CAD renders the mask should come from the renderer (study masks do) not from thresholding; thresholded hero masks are approximate.
- **Maw/holes.** c01 trace fills the maw; study masks must too (G1a does) or the maw is counted as a wedge.
- Parameters marked [GENERAL] are judgment calls; changing one changes every value. Lead may reset (record in edit log).

## Files

`trace_c01.py` (c01 trace), `build_ref.py` (values, bands, overlay), `make_hero_masks.py`, `score_r07.py`, `sensitivity_sweep.py` (+ `sensitivity_sweep.{md,json}`), `c01_mask.png`, `c01_mask_envelope.png`, `c01_centreline.png`, `c01_overlay.png`, `c01_metrics.json`, `c01_trace_meta.json`, `hero_r05_mask.png`, `hero_r06_mask.png`, `r07_scores.{json,md}`.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-17 | aesthetics-analyst | Initial creation: c01 trace, gate metrics/bands, tool, self-test | docs-reviewer (resolved, was FLAG OPEN: (1) s.5 is stale: it says only G1a existed and lists G1a fill 0.392 / wedges 8 / torso 0.463 / reach 0.592 / head 1.48 / IoU 0.594, but `python3 -I score_r07.py` now scores all 8 studies and G1a is 0.433 / 6 / 0.449 / 0.668 / 2.64 / 0.598 (r07_scores.md, identical to the re-run); replace s.5 with the 8-row table or point to r07_scores.md. (2) The s.3 sensitivity sweep and s.2 opening-radius numbers have no committed script or JSON (build_ref.py writes only base values; c01_metrics.json has no sweep). Re-computed here: opening radius 6/8/10/12% = 0.867/0.846/0.619/0.479 reproduces; rot -4 deg (fill 0.443, torso 0.465, reach 0.533, IoU 0.74) and mirror IoU 0.52 reproduce; erode/dilate 8 px do not reproduce with a plain 17 px min/max filter (fill 0.401/0.536, IoU 0.845/0.865 vs table 0.412/0.511, 0.89/0.91; perturbation not recorded); head/flesh for rot/mirror differs (1.68/1.62 vs 1.76/1.74). Commit the sweep script or mark the table "unsourced". Verified OK: the c01 command exits PASS 7/7 and values equal c01_metrics.json and the bands table; self-test r06 hero FAIL 4/7 (reach 0.303, limbs 11, IoU 0.584; fill 0.472, wedges 5, torso 0.547, head 1.45) and r05 hero FAIL 4/7 (torso 0.758, reach 0.152, IoU 0.609) reproduce exactly; s.6 limitations consistent with r07 results. Body [PROVISIONAL] status line stays; resolved by the next row (aesthetics-lead, 'Resolves FLAG OPEN above'), re-verified at HEAD: (1) s.5 is the 8-study table and equals row for row the stdout of `python3 -I teams/aesthetics/analysis/composition_gate/score_r07.py` run from repo root (G1a 0.433 / 6 / 0.449 / 0.668 / 6 / 2.64 / 0.598; G4b 4/7; outputs r07_scores.{json,md} unchanged, git status clean); (2) s.3 sweep table equals row for row the stdout of `python3 -I teams/aesthetics/analysis/composition_gate/sensitivity_sweep.py` (8 rows: erode 8 px 0.88, dilate 8 px 0.90, rot -4 deg 0.74, rot +4 deg 0.75, mirror 0.52); sweep script and sweep .md/.json are tracked (git ls-files); s.3 band table equals c01_metrics.json bands; stated sweep spans recompute (fill 0.409/0.464 = 0.88x to 0.516/0.464 = 1.11x; reach 0.372/0.532 = 0.70x). Non-blocking, signed through: the tool's iou_vs_c01 band stays 0.70 while DESIGN s.4.1 sets the build gate at 0.60; README s.6 describes the build gate as a separate use, so G1a (0.598) FAILs the tool and passes the build gate; aesthetics lead to confirm)) |
| 2026-11-17 | aesthetics-lead | Resolves FLAG OPEN above: s.5 replaced with the 8-study table from r07_scores.md (re-run, identical); s.3 sweep now produced by committed-ready `sensitivity_sweep.py` and table regenerated from it (all 8 rows reproduce; erode/dilate 8 px = disk radius 8 px: fill 0.409/0.516, IoU 0.88/0.90; the earlier hand table's 0.412/0.511 is superseded); stale c01 notes and IoU-gate sentence updated | docs-reviewer (verified: both script outputs reproduce as above; 'identical to r07_scores.md' claim holds; s.6 IoU sentence matches DESIGN s.4.1 (0.60 start, ratchet 0.85); body [PROVISIONAL] status (L3) cleared with this sign-off. Same non-blocking IoU-band note as the row above) |
