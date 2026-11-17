# Full-piece V2.1 (texture, eyes, palette, root-grip pass on v2)

**Status:** [PROVISIONAL] CAD Lead, 2026-11-17. Copy of `../fullpiece_v2/` (untouched) with the coordinator's seven fixes. 2.0 mm voxel, SEED = 7, same Gate-2 helpers and 1C shader family, dark-wall lighting. Every number below has a key in `engineering_checks.json`. KEPT from v2: maw (asymmetric broken teeth), canonical carved smiley with gripping-finger masquerade, headroom >= 300 mm, structural numbers (22 mm solid core, 84 x 66 mm pad, seat 28 mm, arm roots), hard envelope clip, sourced checks.

## 1. Variants (each differs from hero by one axis)

| Variant | Differs from hero | Axis |
|---|---|---|
| `hero` | fingers masquerade, 8 whips, maw 1.0x, mixed teeth | baseline |
| `v1_liftedge` | lower-right face edge lifted, dark slot behind, 3 fibres in the slot; no fingers | (a) masquerade device |
| `v2_tentacles5` | 5 major whips (root radius x1.5, length x1.1) instead of 8 (4 membranes vs 7) | (b) tentacle count |
| `v3_maw_big` | maw 1.45x (shifted 22 mm down), 17 fang-style teeth | (c) maw size / teeth |

Dropped: `eyes_heavy` and `weathered` (indistinguishable on the sheet at board scale, per coordinator). Renders (`renders/`, PIL-validated, all <= 1 MB, 256-colour palette re-encode where needed): hero `front|tq|rake|side|maw`; variants `front|tq`; `variants_sheet.png` = c01 + v2 hero (before) + v2.1 hero + 3 variants.

## 2. What changed vs v2 (the seven fixes)

1. **Eyes:** almond/slit lids (lens footprint, raised lid rim around a recessed slit aperture holding a shallow eyeball dome; lengths 20-40 mm; half-closed, drooping and skewed lids; random orientation, clustered with Gaussian clusters + singles), placed only on the body mass near the centre (within 340 mm of the body centre, outside mask and maw, not on shelf/seat/arm zones, surface slope <= 45 deg), not strung along tentacles. Eyeball band pale, iris dark, pupil black are shader tags (paint). Hero 20 eyes.
2. **Texture/webbing:** helical sinew strands (two rope sets) wrap every D-section limb and the buttress; flow-aligned strand ridges + pitting on the muscle bellies (Hm raised by streamline ribs); web gate loosened (suppressed only in belly cores); 150 streamline seeds (was 70); grain pass at full amplitude on flesh (-25 % on calm cores only), reduced only on eyes (x0.3), teeth, mask face; thin scalloped membrane skirts with 2 fenestrations each between adjacent whip roots (7 in hero, 4 in `v2_tentacles5`).
3. **Sprawl:** whips lengthened (request 520-820 mm), fitted to the envelope and to the three shelf keep-out boxes; mask moved up (y 200) and maw down (y -100) so flesh and eyes sit between them. Realised whip lengths 310-433 mm only (see s.4).
4. **Palette:** desaturated ochre / bone / umber / rust zones; maw lip ring darkened to flesh-rust; teeth stay ivory; mask face the one pale element (shader).
5. **Shelves + buttress:** arms extend under the plates and fuse with the seat/underside; plates taper to 4.5 mm at the rim (up to 11 mm toward the wall, organic noise); 5 root-grip tendrils per plate (3 on the front rim, 2 on the outer rim) curl over the edge, <= 62 mm above the flat; a soft low skirt around each seat block; buttress = a branch limb from the S3 arm end running under the plate to the tip, then the straight-core limb down to the foot, same sinew texture, fused at the tip with an 11 mm fillet.
6. **Smile:** half-width 12.4 mm (mouth ~25 mm), depth 12.4 mm = 90 deg V (fab rule), plus shader shadow in grooves and eye pits.
7. **Mass:** 26.4 kg hero (see s.3, s.4).

## 3. Engineering checks (`engineering_checks.json`)

| Check | hero | v1_liftedge | v2_tentacles5 | v3_maw_big |
|---|---|---|---|---|
| Bbox (limit 914 x 914 x 300) | 910.6 x 910.9 x 300.0 | 910.6 x 911.2 x 300.0 | 910.4 x 898.6 x 300.0 | 910.6 x 911.1 x 300.0 |
| Within envelope (hard clip) | yes | yes | yes | yes |
| Headroom: verts above the 62 mm tendril allowance, S1 / S2 / S3 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| Headroom: root-grip tendril band verts (12-62 mm), S1 / S2 / S3 | 1477 / 2327 / 2318 | same | same | 1477 / 2327 / 2309 |
| Relief mean / P10 / P50 / P90 / std / max (mm) | 53.6 / 17.7 / 47.7 / 84.7 / 39.1 / 300.0 | 51.7 / 16.9 / 46.5 / 81.5 / 38.6 / 300.0 | 59.2 / 19.1 / 57.2 / 88.9 / 39.6 / 300.0 | 54.3 / 15.3 / 47.8 / 91.8 / 40.4 / 300.0 |
| Solid mass proxy, PETG 1.27 (kg) | 26.4 | 25.6 | 27.2 | 26.7 |
| Eyes: count / length range (mm) / half-closed | 20 / 20.1-39.6 / 11 | 15 / 20.1-42.8 / 6 | **11** / 20.1-40.8 / 3 | **8** / 20.3-27.6 / 6 |
| Teeth: count / broken | 29 / 11 | 24 / 9 | 27 / 12 | 17 / 7 |
| Buttress: drop / limb min dia / core / foot pad | 300 mm / 38.5 mm / 22 mm solid / 84 x 66 mm | same | same | same |
| Seat embed (mm) | 28 | 28 | 28 | 28 |
| Shelf flats S1 / S2 / S3 (cm2) | 476.1 / 371.0 / 538.2 | 476.1 / 371.1 / 538.4 | 476.1 / 371.3 / 538.3 | 476.1 / 371.0 / 536.5 |
| Back plane z range (mm) | 0.0-3.0 | same | same | same |

Headroom method: verts inside the footprint x range (2.5 mm inset), z < p, from 12 mm above the flat to 300 mm; the 12-62 mm band is the root-grip tendrils (spec allows <= 60 mm; ours reach 62 incl. voxel tolerance); anything above 62 mm counts as intrusion (none). The keep-out is carved to 304 mm in the field. Shelf heights as v2 (S1 344.5, S2 170.5, S3 -109.5). Flat areas lose a few cm2 to the grips (hero S1 476.1 equals v2). Buttress min diameter is the measured limb envelope; the structural core is the embedded straight 22 mm cylinder.

## 4. Not honored / partly honored

1. **Mass 26.4 kg, target <= 25** (v2 28.6). Only `v1_liftedge` (25.6) is near; field breakdown at 4 mm: mask zone ~6.8 kg solid, maw zone ~4 kg, shelf x-bands ~6.5 kg, rest ~8.5 kg. Not a valid number until hollowed.
2. **Sprawl is not c01.** Realised whip lengths 310-433 mm (requested 520-820): the radial starts sit 100-190 mm from centre and the 440 mm clip plus the shelf keep-out boxes cut the paths. Silhouette still reads compact next to c01; upper-left is bare. Membranes are small (7 skirts, 90-230 mm).
3. **Eye counts below 15 in two variants** (`v2_tentacles5` 11, `v3_maw_big` 8): the placement area shrinks when whips thicken or the maw grows. Hero 20, liftedge 15.
4. **Seat blocks still read as dark rectangles** under S1 and S2 (cleat seat is a mandatory 160 x 150 solid zone; only a soft skirt added).
5. **Root-grip tendrils read as short pegs/fingers** standing on the plate rims; they also touch the top face near the rim (a few cm2 off the flat).
6. Eyes are small at wall distance (20-40 mm long) and mostly in one lower-right cluster; the iris is painted (shader), not geometry.
7. Smile groove is the 90 deg fab limit; at hero scale it reads, but it is a dark thick arc: the face still has some cartoon read in `hero_rake`. Weathering 0.8 helps (slump, pits, crack).
8. Not validated: min-wall, 6 mm void, overhang, segmentation; fingers and grips are overhangs; sinew ridges are 2-3 mm tall (print-res only).
9. Structural zones: no eyes in seat +100 mm, plate, arm roots; foot pad / strut / tip-foot nodes have no eyes or pockets by construction (eyes only within 340 mm of centre).

## 5. Self-assessment

vs the seven fixes (A = done to brief, F = missed):
1. Eyes read as eyes: **B-**. Slit lids, pale ball, dark iris, half-closed/sagging, clustered on the body; but small and in one cluster; two variants under count.
2. Texture/webbing: **B-**. Sinew wraps limbs and bellies, web remains in non-calm zones, membranes between roots; flesh no longer plastic. Still far from c02's fibre mat; membranes small.
3. Sprawl: **C**. Longer, thicker whips than v2 but silhouette still compact, whips under 60 % of requested length.
4. Palette: **B+**. Desaturated ochre/bone/umber; maw lip dark, teeth ivory, mask the only pale clean element. Fingers and eyeballs are the next pale items.
5. Shelves + buttress: **B-**. Thin organic plates, grips, arms run under the plates, buttress limb continues the arm with the same sinew. Seat rectangles and peg-like grips remain.
6. Smile: **B**. Deeper shadow within the 90 deg rule, wider mouth.
7. Mass: **C+** (26.4 vs 25).

**vs c01 (honest):** same family of ideas (face high, gaping maw below, eyes between, radial limbs, plants on shelves) but v2.1 is a dense lumpy mass, not c01's open webbed sprawl; limbs are thick and short, there are no fibre mats, and the figure fills about 60 % of the box width in the body (shelves reach the full 880 mm). c01's silhouette, translucency and fibre depth are not reached. Variant (b) is the weakest visible difference on the sheet; (a) and (c) are clear.

## 6. Regenerate

`./run_all.sh OUT` (per variant: field ~3 min, mesh+grain ~30 s, views ~2.5 min each), then `python3 build_checks.py OUT && python3 make_sheet.py`. `measure.py` re-measures headroom/relief from any mesh. Scratch output lives outside the repo.

## 7. Print-res needs (additions to v2 s.7)

Hollowing to 9-14 kg; shell the 6.8 kg mask zone; soften or hide seat rectangles inside the web; grip tendrils as printable curls (base >= 4 mm, no overhang > 45 deg); lid chamfers <= 45 deg and eye crease >= 90 deg verified; sinew ridges at 0.4 mm voxel; maw as a separate piece with a flat parting plane; membrane skirts need min-wall checks (7-9 mm thick edges now).

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-17 | cad-lead | Initial creation (v2.1 package) | [PROVISIONAL] |
