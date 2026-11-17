# Full-piece V2 composition (round-05 verdicts implemented)

**Status:** CAD Lead, 2026-11-16/17. For Evan's eyes, not the printer: 2.0 mm voxel (SEED = 7), same Gate-2 helpers (`../gate2/gen_patch.py`), same 1C shader and dark-wall lighting as `../fullpiece/` (v1), shader extended with tone zones, maw/teeth/eye tags. Measured numbers below have a key in `engineering_checks.json` (measured values: tables in s.3 have keys in `engineering_checks.json`; design constants such as radii, groove sizes, strand widths are `gen_fullpiece.py` inputs, not measurements; anything else is marked or is an estimate); v1 comparison numbers are back-filled in `../fullpiece/engineering_checks.json` from the retained v1 meshes by `measure.py`.

LOCKED (unchanged vs v1): shelf arrangement A (L/R/L, p 250/200/290, 190 mm flat tops), radial sprawl whip angles, Gate-2 local texture, flat back, 914 x 914 x 300 envelope, cleat seat zones. Changed: shelf heights, see s.4.

## 1. Variants (one axis each vs `hero`; `VARIANTS` in `gen_fullpiece.py`)

| Variant | Differs from hero | Axis |
|---|---|---|
| `hero` | fingers masquerade (5 tendrils gripping the bezel from behind), 26 eyes, maw 1.0x with mixed teeth, weathering 0.55, 8 whips | baseline |
| `v1_liftedge` | masquerade A: lower-right face edge lifted, dark slot behind it, 3 thin fibres in the slot; no fingers | (a) masquerade device |
| `v2_eyes_heavy` | 40 eyes (dense fill pass adds 9-13 mm radius eyes) | (b) eye density |
| `v3_maw_big` | maw 1.28x, 17 teeth, thicker/longer fang-style set | (c) maw size / tooth character |
| `v4_weathered` | smiley weathering 1.0 (deeper sag, pits, crack, chipped bezel) | (d) smiley weathering |
| `v5_tentacles5` | 5 major whips (x1.3 root radius) instead of 8 | (e) tentacle count (RP-2 item 5) |

Renders (`renders/`, all PIL-validated, <= 1 MB; PNGs re-encoded to 256-colour palette where Cycles output exceeded 1 MB, so gradients show mild banding): hero `hero_front|tq|rake|side|maw.png`; variants `<name>_front|tq.png`; `variants_sheet.png` = c01 reference + v1 hero_front (before) + v2 hero + 5 variants.

## 2. What is in the piece

- **Mask:** circular face R = 92 mm on a domed disc, canonical emoticon: two vertical-oval counter-sunk eyes (bevel ring + 24 mm pit), smile = true circular arc (centre v 0.14 R, radius 0.60 R, -152 to -28 deg) as a V groove with tapered ends; heavy raised bezel (crown 106 mm) so the face is carved 40 mm into the mass. Weathering in the field: sag, pitting, gravity slump (left worse), a hairline crack from the lower-left rim, chipped bezel. Pale bone shader with stain streaks; the one clean contrasting element.
- **Maw:** (-95, -78), 118 x 82 mm semi-axes, noisy irregular lip (ridge crest 90-110 mm, heavier lower lip), void to a plugged floor at z 9-19 mm (open recess, not an enclosed cavity), 29 teeth (rooted in the lip crest, length 10-56 mm, base radius 9.7-17.7 mm, 11 broken, corner tusks, clumps and gaps, snaggled lean), 4 thin throat strands.
- **Tentacles:** 8 radial whips (root r 26-46 x 0.9, tip r 7.5, +-20 % peristaltic swells, z offsets 0-20 so crossings over/under), 3 shelf arms (r 42 to 26), all D-section (flat back, vertical flanks to 0.30 r, round front half), joined to smooth muscle bellies with 11 mm log-sum-exp root fillets and root bulbs. Buttress: limb r 23 (swells, flared top and foot), straight embedded solid core 22 mm dia, 84 x 66 mm flat foot pad (rounded rectangle, 12 mm thick, foot z 14).
- **Eyes:** lidded hemispheres (R 9-17 mm; upper lid cover 0-78 %, lower bag, iris pit dia = R), V-groove socket (half-width 0.2 R, depth 0.16 R, ~100 deg), clumped (Gaussian clusters + singles), only on faces with slope <= 1.0 (<= 45 deg off outward).
- **Form/tone:** 7 smooth muscle bellies (peak 58-80 mm x 0.74) and root bulbs are solid and calm (grain x 0.45); the Gate-2 web exists only outside them. Shader zones ochre / bone / rust from low-frequency noise.

## 3. Engineering checks (`engineering_checks.json`, 2.0 mm voxel, ~1.26 M tris hero)

| Check | hero | v1_liftedge | v2_eyes_heavy | v3_maw_big | v4_weathered | v5_tentacles5 | v1 hero (before) |
|---|---|---|---|---|---|---|---|
| Bbox X x Y x Z (limit 914 x 914 x 300) | 907.7 x 906.4 x 300.0 | 907.7 x 900.1 x 300.0 | 907.7 x 906.4 x 300.0 | 907.5 x 906.3 x 300.0 | 907.7 x 906.4 x 300.0 | 907.1 x 875.9 x 300.0 | 911.1 x 875.1 x 299.9 |
| Within limit (hard clip) | yes | yes | yes | yes | yes | yes | yes (v3 diag 918 x 919 no) |
| Headroom, min clear above flat, S1/S2/S3 (mm; intruding verts above 12 mm lip) | >= 300 / >= 300 / >= 300 (0 / 0 / 0) | same | same | same | same | same | S1 >= 300 (0); S2 12.0 (855); S3 12.0 (60,607) |
| Relief mean / P10 / P50 / P90 / std / max (mm) | 55.4 / 18.9 / 48.6 / 97.8 / 31.7 / 293.3 | 52.7 / 18.3 / 47.0 / 93.7 / 29.8 / 293.3 | 55.5 / 18.9 / 49.1 / 97.8 / 31.7 / 293.3 | 56.0 / 17.1 / 49.2 / 100.5 / 33.0 / 287.1 | 55.3 / 18.9 / 48.6 / 97.0 / 31.6 / 293.3 | 58.8 / 18.8 / 55.9 / 98.4 / 32.0 / 293.3 | 48.8 / 17.7 / 42.5 / 90.1 / 29.1 / 293.4 |
| Solid mass proxy, PETG 1.27 (kg) | 28.6 | 27.7 | 28.7 | 28.6 | 28.6 | 27.6 | 22.2 |
| Eyes: count / dia range (mm) | 26 / 18.5-34.4 | 26 / 19.1-36.1 | 40 / 18.0-34.4 | 26 / 18.8-32.3 | 26 / 18.5-34.4 | 26 / 18.4-40.6 | - |
| Teeth: count / broken / length range (mm) | 29 / 11 / 9.8-55.5 | 24 / 9 / 9.0-63.2 | 29 / 11 / 9.8-55.5 | 17 / 7 / 21.0-108.9 | 29 / 11 / 9.8-55.5 | 27 / 12 / 12.2-67.2 | - |
| Buttress drop / limb min diameter / core / foot pad | 300 mm / 38.5 mm / 22 mm solid / 84 x 66 mm | same | same | same | same | same | 300 / n.m. / n.m. / 64 mm |
| Seat embed depth (mm) | 28 | 28 | 28 | 28 | 28 | 28 | 16 |
| Shelf flat top area S1 / S2 / S3 (cm2; nominal 190 x 250 / 200 / 290) | 476.1 / 372.8 / 539.1 | 476.1 / 372.9 / 539.4 | same as hero | 476.1 / 372.9 / 539.0 | same as hero | 476.1 / 371.3 / 539.5 | 476 / 361 / 522 |
| Back plane z range (mm, z < 3 verts) | 0.0-3.0 | same | same | same | same | same | 0.0-3.0 |

Notes: headroom counts vertices inside the footprint x range (2.5 mm inset) with z < p, from 12 mm above the flat (10 mm rim lip + 2 mm voxel tolerance) to 300 mm above; the keep-out is carved in the field to 304 mm, so "none" means clear to >= 300. Relief = max z per 4 mm cell over covered cells (> 5 mm) outside the shelf bands. Back-plane spread is strand rounding at 2 mm voxels, pinned vertices sit at z = 0. Buttress min diameter is the measured limb envelope (in-plane distance to mesh vertices, stations t 0.15-0.80); the structural core is the embedded solid 22 mm cylinder, straight from foot node to tip node. Shelf-arm solid core (>= 40 mm) holds by construction (arm radius >= 26 x 0.84 swell, solid) and was not measured separately.

## 4. Constraints NOT honored or only partly

1. **Shelf heights moved** to make 300 mm headroom a hard constraint: S1 top y 250.5 -> 344.5, S3 -89.5 -> -109.5 (S2 unchanged). Cause: S1's 150 mm cleat seat block (y 194.5-344.5) hung into S3's plant volume. Arrangement A order and p are kept; Evan liked "placement", so this is a deviation to flag. Cost: S1 sits well above the mask.
2. **Side-profile distribution not identical.** Mean 55.4 vs v1 48.8 mm, P50 48.6 vs 42.5, P90 97.8 vs 90.1 (+14 %, +14 %, +9 %); P10 and std close. Solid muscle bellies added height. v2_eyes/maw/weathering variants stay within 1 mm of hero; v5 higher (58.8).
3. **Mass proxy 28.6 kg solid vs v1 22.2 kg** (target was <= v1). Muscle bellies and D-section limbs are solid. Not a valid number until hollowed; the print-res pass must shell harder.
4. **Smile groove is shallow by design.** Fabrication rule (V >= 90 deg open, depth <= 3x width): half-width 10.6 mm, depth 10.5 mm. Evan's brief was "deep, shadowed V"; at wall distance the smile reads but is weak (see hero_front). Conflict flagged for Evan/Fab: deeper grooves need a printed-in-pieces face or a different rule.
5. **Eyes smallest 18 mm across** (brief 10-45 mm; fab minimum 12 mm; iris pit >= 8 mm needs >= 18 mm). Largest 40.6 mm (v5).
6. **Applied from the fab note:** eyes >= 12 mm (18+), V-groove socket (~100 deg), eyes only where surface slope <= 1.0 (<= 45 deg off outward, tentacle flanks excluded), teeth height <= 3x base width (`L = min(L, 6 r0)`), tip radius >= 2.8 mm (broken stubs >= 5 mm), base radius >= 9.7 mm, D-section whips and arms, smile V ~91 deg. **Deferred:** lid chamfer <= 45 deg (lids are spherical shells; not measured), eye crease >= 90 deg (socket yes, lid-to-ball crease not measured), D-section on the buttress (round limb around a straight core), maw split into a separate hero piece (not modelled; throat floor is an open recess at z 9-19 mm), swell-on-front-half check (D-section is modelled, front-half swell not measured).
7. **Applied from the structural note:** buttress core 22 mm solid, straight, axis ends at the foot and tip nodes (centreline wanders <= 5 mm); foot pad 84 x 66 mm flat, stand-off 14 mm (<= 30); seat embed 28 mm; no eyes within 180 mm (x) / 250 mm below to the plate (y) of each seat centre or on the plate footprint, none within 30 mm of the arm radius (seat + 100 mm and arm roots; the foot pad and strut are empty of eyes because eyes are placed before the strut and the foot area is bare wall). Not checked: tip/foot node + 75 mm for pockets (the 4 thin lift-edge slot fibres and the maw are not in those zones); arm solid core 40 mm held by construction only.
8. **Not validated at all:** min-wall (web strands 9-30 mm here; thin teeth tips 2.8 mm), 6 mm void rule, overhang, segmentation, bridging of throat strands (3 mm radius), fingers (5.5-13 mm radius, arch 114 mm over the bezel, overhanging).
9. Fingers (hero masquerade) arch over the bezel and are overhangs; they read as claws. `v1_liftedge` is the cleaner print.

## 5. Self-assessment (blunt, graded vs the six rework points)

1. **Smiley mask: B-.** Canonical geometry, clean and readable, carved into a heavy bezel, bone vs ochre contrast holds, weathering visible in the rake view (stain, crack, slump). Weak spots: at wall distance the face is dimmer and smaller than v1's serene mask; the shallow V (item 4) loses the shadowed smile; weathering degree d vs hero is nearly invisible in the front view; not yet Bayon-head monumental, it still reads as a stone disc with a face.
2. **Maw: B+.** Gaping, dark, irregular lip, teeth of mixed length and angle, some broken, reads at wall distance and strongly in `hero_maw`. Weak: the lip ridge is as pale as the mask surround and competes with it; teeth at front view are small; v3_maw_big is the more unmistakable of the two.
3. **Muscular tentacles: C+.** Thick tapered D-section limbs with swells and crossings, rooted into bellies; flesh-reading. Weak: smooth, plasticky, no sinew or fibre; whips are short/stubby next to c01's sweep; only a handful of real overlaps; the buttress reads as a thick separate leg with a pad, only partly continuous.
4. **Eyes: B.** 26 clumped lidded eyes with iris pits and V sockets, readable in close views; heavy variant (40) is the stronger "eye-covered" read. At wall distance many read as pale warts/suckers on the whips; lid chamfers unverified.
5. **Masquerade: B-.** Fingers gripping the bezel read as claws from behind (hero); the lifted-edge slot (v1_liftedge) is subtler and arguably better. Neither says "conceals something" without explanation.
6. **Cohesive creature + tones: C+.** One organism reads better than v1 (single mass, radial limbs, tonal ochre/bone/rust zones, calm bellies against web zones). But the Gate-2 web is mostly gone from view, the piece is compact and bare at upper-left, and the gap to c01 (sinewy sprawl, fibre mat) is still large. Texture-density-by-anatomy is only a binary calm/web split.

## 6. Regenerate

`./run_all.sh OUT` then `python3 build_checks.py OUT && python3 make_sheet.py` (field 2.5-3 min, mesh+grain ~30 s, 2-3 min per 1200 x 900 x 48-sample view, ~6 GB RAM). Single: `python3 gen_fullpiece.py --variant hero --vox 2.0 --out OUT && python3 render_full.py OUT hero renders --views front,tq,rake,side,maw`. `measure.py MESH.npz META.json` re-measures headroom and relief from any mesh.

## 7. Print-res pass will need

1. Per-segment cuts (<= 230 x 230 mm) with seam lands off the seat blocks, buttress core and foot pad; 0.4-0.5 mm voxel tiles; min-wall clamp; Gate-2 sculpt pass.
2. Maw as a separate hero piece with a flat parting plane (upper/lower halves printed teeth-up); keep the throat a plugged recess.
3. Hollowing to 9-14 kg (28.6 kg solid proxy now), re-balance belly heights toward the v1 relief distribution.
4. Teeth at print scale (base >= 4 mm, height <= 3x base, tip >= 0.75 mm; current tips 2.8 mm pass); lid chamfers <= 45 deg and measured eye creases; deeper smile if Fab allows.
5. Buttress as D-section/hollow wrap around the 22 mm core, #10 shear boss, 40 mm screw spacing on the foot pad (reserve only, no holes now); shelf-arm solid core >= 40 mm verified by measurement; no pockets in the zones listed in the structural note.
6. Overhang audit of fingers and lid shells; replace 3 mm throat strands or plug them.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-17 | cad-lead | Initial creation (v2 package, README) | docs-reviewer (resolved, was FLAG OPEN: same as CAD STATUS V2 row: README header 'Every number below has a key in engineering_checks.json' overstated; tables s.3 (bbox, headroom, relief, mass, eyes, teeth, buttress, seat, flats, back plane, v1 column) all verified against JSON/v1 JSON, but s.2/s.4/s.6 constants listed in that row lack a JSON key; cite gen_fullpiece.py or mark unsourced. Resolved by the orchestrator row below (this README), re-verified in c98627b) |
| 2026-11-17 | orchestrator | Resolves FLAG OPEN above: "every number keyed" softened to measured-vs-design-constant split; unsourced estimates named (v2.1); whip % 45-65; v2.1 render count 11 + sheet; boarded-in-round-06 | docs-reviewer (verified: same checks as the CAD STATUS resolve row; header split measured/design constant present, whip % and unsourced list as described there; body [PROVISIONAL] header tag cleared) |
