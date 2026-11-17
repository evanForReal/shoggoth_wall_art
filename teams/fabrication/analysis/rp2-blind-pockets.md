# RP-2 item 3: blind-pocket relaxation, printability read

**Status:** [PROVISIONAL] Fabrication Lead, 2026-11-16. Printability side only. Structural reviews load independently; nothing here speaks for them. Numbers marked [GENERAL] are FDM practice, not measured on Evan's printer (still unknown). Nothing here is a print test.

## 0. Verdict

**CONDITIONAL COUNTER-SIGN.** Blind relief pockets with a mouth < 6 mm are printable on 0.4 mm / 0.2 mm FDM, and are easier than through-voids of the same size (no bridge across the pocket, no through-hole cleaning, floor on the build plate). The relaxation is accepted only for pockets that meet C1-C6 below. As filed, it is evidenced for **size only**: the validators measure z-projection gaps and never record pocket depth, wall angle or axis direction. Those three decide printability, so they become gates, not assumptions.

Rule text proposed for mesh-spec-v1 Section 2 (replaces the "Min through-void" row for blind features):

> Through-void (see-through): smallest dimension >= 6 mm. Blind relief pocket (floor >= 2.6 mm, no opening on the back): permitted below 6 mm if C1-C6 of `teams/fabrication/analysis/rp2-blind-pockets.md` hold. Pockets are declared against a per-segment print orientation.

## 1. Conditions

| # | Condition | Basis |
|---|---|---|
| C1 | **Open direction.** Pocket mouth normal within 45 deg of print-up for the segment's declared orientation (design to 40 deg, ASA margin). Body segments: print-up = away from the wall (+z). Shelf segments (top-face-down): print-up = wall-space down. No pocket mouth may face the bed. | Overhang limit 45 deg PETG / 40 ASA (spec Section 2). A pocket tilted theta off print-up has one wall overhanging at theta. |
| C2 | **No net undercut.** Every pocket wall leans <= 45 deg from vertical in print; mouth width >= width at any lower level minus 0.2 mm (one layer of lateral shift per layer). No hooded or bottle-neck pockets. | Support inside a < 6 mm pocket cannot be removed. Pockets must be support-free by design, not by slicer luck. |
| C3 | **Minimum mouth 2.0 mm** (>= 4 perimeter widths of 0.45) measured on the sculpted print-res mesh, not the field. Gaps < 2.0 mm are surface texture: depth <= 2x width (<= 4 mm), not counted as pockets, expected to fill with primer. | Gaps < ~1.0 mm fuse in PETG (extrusion spread, ooze). 1.0-2.0 mm survive only as slits with string debris. 2.0 mm matches the strand floor. |
| C4 | **Depth <= 3x mouth width** by default (3 mm mouth: 9 mm deep). 3x-6x allowed only if flagged wash-only in CAD (no spray primer) and mouth >= 3 mm. > 6x forbidden: widen, shallow, or plug. | Paint access: spray cone and primer pooling; brush reach. Also keeps flanking ridges from becoming 10:1 slender walls. |
| C5 | **Floor >= 2.6 mm**, flat, on the build plate (as Gate 1C `PLUG_T`). Flanking ridges stay >= 2.0 mm (3.0 near load path) and ridge height <= 10x thickness unless cross-braced. | Floor = 13 layers, solid. Ridge slenderness [GENERAL]: tall 2 mm walls ring and get nozzle-dragged above ~10:1. |
| C6 | **Flank pockets** (mouth normal 45-90 deg from print-up, e.g. shelf side faces, tentacle flanks) are allowed only with mouth <= 6 mm AND an arched/teardrop roof (<= 45 deg). Roof is bridged (PETG bridge limit 20 mm; 6 mm is well inside). Roof surface is rough and sags 0.2-0.4 mm [GENERAL]; accept. | Below 6 mm a flank pocket bridges; above 6 mm it needs the arch anyway. |

Verification: CAD emits a per-pocket table in `engineering_checks.json` (mouth min width at print-res, depth, axis angle vs declared orientation, undercut mm). Fabrication re-checks on the first per-segment export. A coupon (Section 5) closes the numbers that are [GENERAL].

## 2. Reasoning by issue

**Trapped support.** Back-down printing of a 2.5D relief makes every pocket open upward: no support. The relaxation is safe exactly where the geometry is 2.5D. Risk sits in sculpted flanks, fan undersides and anything under an overhang (lids, lips, tentacle undersides), where the mouth faces the bed or sideways. A < 6 mm support-filled pocket is permanent debris; hence C1/C2 as design rules.

**Bridging over mouths.** Not an issue for upward pockets: the floor sits on the plate and nothing spans the mouth. Flank pockets bridge their roof (C6). A through-void of 6-20 mm bridges worse than a blind pocket of 3-6 mm, so the relaxed class is the safer one.

**Stringing.** PETG strings across open pockets on travel moves. Pockets are narrow, so strings bridge ridge to ridge and look like cobweb in dark crevices. Slicer: retraction 4-6 mm direct drive, travel avoids crossing perimeters, wipe, 235-245 C PETG with a dry spool. Clean-up with a heat gun is cheap on 2 mm-wide pockets but tedious on hundreds. Not a blocker; a coupon decides the settings.

**Paint and primer pooling.** Sprayed primer reaches ~3x mouth width; below that it pools and cracks on drying. Aesthetic intent (Gate 1C crevice shading, near-black depths, pale crests) is a dark wash plus dry-brush, which wants pooling in the depths. So: spray primer on crests only, wash the pockets. C4 encodes this. Pockets that must be fully painted (eyes, teeth bed) stay >= 6 mm or <= 3x.

**Min width / depth.** C3-C5. The nozzle, not the model, sets 2.0 mm; the 6 mm through-rule was never about printability of blind features.

## 3. Evidence from gate2/validation_sculpt.json (and the gate1c/gate2 STLs)

What the file says (sculpted mesh, re-voxelised, both bounds):

| Metric | Surface-inclusive | Interior-only |
|---|---|---|
| Interior voids (z-projection gaps) | 22 | 208 |
| Inscribed diameter bins <2 / 2-6 / 6-10 mm | 9 / 6 / 7 | 195 / 0 / 13 |
| Void-area share < 6 mm, pre to post sculpt | 22.2% to 33.0% | 10.8% to 7.8% |
| Ridge width P5 (post) | 2.75 mm | 0.75 mm |
| Ridge samples below 2.0 mm, pre to post | 0.2% to 1.2% | 7.5% to 13.6% |
| Thin ridge components (>= 25 vox), pre to post | 1 to 0 | 135 to 85 |

Read for printability:
- 41% of inclusive voids (9 of 22) are < 2 mm: below C3. They are texture, not pockets. They will print as dimples or fused slits.
- Only 6 of 22 sit in the 2-6 mm band the relaxation actually concerns; 7 are >= 6 mm and need no relaxation. Gate 1C converted 160 sub-6 mm voids to blind pockets; the post-sculpt count is the only print-res-adjacent count.
- Ridge width is unresolved between P5 0.75 mm and 2.75 mm depending on the voxelisation bound. Ridges < 1.35 mm (3 lines) print as single or gap-filled lines. The pocket walls ARE these ridges. The relaxation does not help if the ridges fail; C5 and the print-res mesh decide.
- The sculpt pass moves the wrong way for pockets: outward-only displacement up to 1.3 mm per face. On a 3 mm mouth that can remove up to 2.6 mm of width where gap-limiting does not fully zero it (mask: gaps < 1.8 mm). The post-sculpt share < 6 mm rose 22% to 33% (inclusive). C3 measures mouths on the sculpted mesh for this reason. Grain at pocket rims should ramp to 0 within ~1 mm of a rim.
- Across-flow grain wavelengths of 0.68 / 1.1 / 2.25 mm are at or below the spec emboss floor (1.0 mm) and the 0.45 mm line width: the finest octave will not print crisply (gate2 README says the same). Treat <= 1.0 mm grain as non-printed texture.

Fabrication cross-check (own measurement, indicative; script + output: `heightfield/heightfield_check.py`, `heightfield/heightfield_check.json`): z-buffer heightfield of the gate1c and gate2 preview STLs (380k-triangle decimations, 0.5 mm grid, interior 40 px margin excluded, top surface only so undercuts are invisible, grain smoothed out). Depressions narrower than 6 mm (morphological closing r = 3 mm minus surface):

| | gate1c | gate2 |
|---|---|---|
| Area of < 6 mm depressions (cm2 of ~295) | 85 (29%) | 97 (33%) |
| Depth P50 / P90 / P99 | 2.0 / 8.6 / 121 mm | 1.8 / 9.4 / 105 mm |
| Area share by depth, mm: 0.5-3 / 3-6 / 6-12 / 12-24 / > 24 | 61 / 25 / 7 / 2 / 6% | 64 / 20 / 8 / 3 / 4% |

Reading: 84-86% of narrow-depression area is <= 6 mm deep, i.e. shallow dimples that pass C4 for any mouth >= 2 mm. A tail of 4-6% of narrow-depression area is > 24 mm deep (slots between tall features such as limb and fibre fans, depth up to ~135 mm). That tail breaks C4. It is where primer will not reach and where a flank ridge exceeds 10:1. Patch relief is shallow (median 13 mm); the full piece targets 60 mm mean relief, so the deep tail grows unless CAD enforces C4 at piece scale. Caveats: decimated preview meshes; patch scale, not piece scale; closing width is an approximation of mouth width; no undercut or axis data.

## 4. Where this is not safe

- Pocket under any overhang (eyelid, lip, tentacle underside): C1/C2 fail by geometry; the relaxation does not apply. Solve in the design, not by a support rule.
- Anything below 2 mm: not a pocket.
- Pocket on the shelf side/front faces: horizontal in print, C6 only.
- Relaxation does not cover load-path walls (1.8 mm, 3.0 mm strand floors stay).

## 5. Coupon (cheap gate, run when a printer is named)

One plate, 60 x 100 mm, PETG and ASA: mouth widths 1.5 / 2 / 3 / 4 / 6 mm x depths 3 / 6 / 12 / 24 / 36 mm, axis tilts 0 / 30 / 45 / 60 / 90 deg (flank rows with teardrop roofs), one 230 mm strip for shrink. Record: pocket survival, roof sag, string count, primer coverage depth (spray vs brush). Expected ~3 h per plate. Until then C1-C6 stand on [GENERAL] limits.

## 6. What Fabrication needs from fullpiece-v2 (CAD, act now)

v2 (15-40 surface eyes, carved smiley mask, gaping toothed maw, muscular tentacles) adds almost entirely overhang-class and sub-nozzle features, which are exactly where printability fails. Segment and mass refresh is deferred until the v2 mesh lands; what CAD should do now to avoid rework is below. Orientation assumption: body segments back-down, shelves top-down, maw its own orientation.

| Feature | Fab risk | CAD action now |
|---|---|---|
| **Surface eyes (15-40)** | Upper lid is a hood over the globe: horizontal overhang at the lid, undercut crease below it. Iris/pupil detail < 1.0 mm. Eyes on tentacle flanks/undersides open sideways or down. Count multiplies pocket checks. | Eye = domed boss in a V-groove socket; lid as a chamfered rim <= 45 deg, no hooded lid, crease open angle >= 90 deg; eye diameter >= 12 mm; iris/pupil as painted or recess floor with >= 1.0 mm edges; place on faces within 45 deg of print-up, or model flat dimples <= 1.5 mm elsewhere. Tag eyes as a feature group. |
| **Teeth** | Tips below nozzle: tip radius < ~0.5-0.75 mm prints blunt or breaks. Teeth in the upper jaw point down, lower jaw up: one set overhangs in any single orientation. Teeth printed sideways delaminate on layers. | Min tip radius 0.75 mm, base >= 4 mm, height <= 3x base width, taper half-angle >= 12 deg. Model teeth as separate bodies on pin sockets (3 mm pin, 0.3 mm clearance) or split the maw into upper/lower jaw halves each printed teeth-up. No tooth axis > 30 deg off the print-up of its part. |
| **Maw (gaping)** | Throat is an enclosed or deep cavity; lips and tongue undercut; inside surface unreachable for supports, paint, cleaning. Mesh gate bans enclosed cavities. | Separate hero piece with a flat parting plane; throat as a shallow blind pocket (back wall plugged at a defined depth, C4-scale: depth <= 3x narrow dimension where the throat < 6 mm); lip walls <= 45 deg; keep the maw interior dark/painted, not detailed; no free tongue or uvula. |
| **Carved smiley mask** | Carved grooves/eye recesses are pockets (C1-C5). Smooth pale face on a gently sloped top surface shows 0.2 mm terracing (at 5 deg slope, steps ~2.3 mm wide); focal point so it will be inspected. | Smile groove V >= 90 deg open, mouth >= 2 mm and depth <= 3x width; eye recesses flat-floored; bezel inner walls <= 45 deg. Make the mask a separate insert or segment region with finish allowance (sand/fill), or accept filler + paint. |
| **Muscular tentacles** | Round tubes resting on the plate overhang below the equator. Suckers on flanks/undersides are pockets facing sideways or down. Thick volumes: mass and time (22 kg solid proxy). Fine muscle striation below 1 mm will not print. | D-section only: flat back, sides >= 45 deg from horizontal (half-round or shallower at the plate). Suckers on print-up faces only, diameter >= 6 mm, depth <= 0.5x diameter, bevelled rim; underside suckers become shallow dimples. Surface grain wavelength >= 1.0 mm, zero amplitude near pocket rims. Hollow/shell for mass at the print-res pass, with escape-free (no enclosed cavity) vents. |

General: add an overhang limiter (<= 45 deg, bounded undercut) to the field before the sculpt pass; export per-feature IDs; per-pocket table in engineering_checks.json (C1-C6); hard bbox clip (per fullpiece README); solid seam knuckles away from eyes/teeth/maw rims; declare print orientation per segment.

Not touched: segment count, mass, print time, joint detail. Those stay at enabling-v1 values (16 segments, ~12.6 kg, ~17 printer-days) and are known stale against a 22 kg-solid / 914 mm piece; refresh waits for the v2 mesh.

## 7. Vote on RP-2 (Fabrication Lead)

**FOR.** Items 1-8 are warranted; item 3 counter-signed with the conditions above; Fabrication's segment/mass refresh runs on the v2 mesh. Fabrication's ~22 h idle is accepted as a finding.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-16 | fabrication-lead | Initial creation (RP-2 item 3 verdict, conditions, v2 fab-risk list) | FLAG OPEN: same as STATUS row, s.3 "Fabrication cross-check" table (gate1c/gate2 heightfield areas, depth percentiles, depth-share bands) has no committed script or output; mark "unsourced" or commit it. s.3 first table verified against validation_sculpt.json. Body [PROVISIONAL] tag kept |
| 2026-11-17 | orchestrator | Resolves FLAG OPEN above: heightfield numbers now sourced (analysis/heightfield/heightfield_check.py + .json, re-run on the retained gate1c/gate2 heightfields, reproduces every table value); "85-90%" corrected to 84-86% | [PROVISIONAL] |
| 2026-11-17 | fabrication-lead | Owner confirmation: re-ran heightfield_check.py (build+stats) on the on-disk gate1c/gate2 preview STLs (gitignored, dated 2026-11-16, not regenerated; build is seeded) -> new JSON byte-identical to heightfield_check.json; numbers match (no change to s.3 table); script adopted as Fabrication's | [PROVISIONAL] |
