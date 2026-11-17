# composition_r08c: r08b + coordinator fixes (2 studies: b medium, c dense)

CAD worker, 2026-11-17. [PROVISIONAL] Not boarded; not committed. r07, r08, r08b untouched. Code = r08b + new crown tines, catenary webs, jagged maw, narrow ribbed trunk, mask collar. Ids `G1a_b`, `G1a_c` (same skeleton as r07 G1a). Data: `checks.json`, `measure_extra.json`, `checks/`. `torso_test.py` = quick gate torso metric from the build silhouette.

## 1. Results
| id | IoU vs r07 G1a (png, need >= 0.70) | IoU vs c01 (need >= 0.60) | COMP | failed | gate | gate fails | torso_width_frac (<= 0.598) | maw:mask | lum wall / flesh / mask / maw |
|---|---|---|---|---|---|---|---|---|---|
| b | 0.719 | 0.535 | 7/13 | 5,7,8,10,11,13 | 5/7 | limb_count 11, iou_vs_c01 | 0.459 | 1.09 | 13.1 / 30.1 / 100 / 7.6 |
| c | 0.723 | 0.547 | 7/13 | 5,7,8,10,11,13 | 6/7 | iou_vs_c01 | 0.484 | 1.11 | 13.0 / 31.0 / 100 / 7.8 |
Other gate values (b/c): fill 0.424 / 0.444, wedges 7 / 6, limb_reach 0.449 / 0.445, head_vs_flesh 2.17 / 2.10. Checklist: #2 now passes (body 17.0%, was 22.2); #12 passes (headroom 300 on all three tops); #5 fails by brief (maw:mask 1.0-1.2 vs checklist <= 0.7 / >= 1.3); #7/#8/#10/#11/#13 fail as in r08b. **IoU vs c01 fell (0.575-0.585 to 0.535-0.547)**: narrowing the trunk costs c01 overlap; the 0.60 start is further away. Shelf flat tops (volume): S1_UL 158 x 182, S2_UR 194 x 182, S3_LL 188 x 158 mm, 300 mm clear over each.

## 2. Per-fix, blunt
1. **Crown**: replaced the curly strands with 5 (b) / 7 (c) thick tapering tines (root dia 29-36 mm, tips 9 mm) plus 3 / 6 short side branches, asymmetric heights, rooted behind and beside the mask, arching up/outward; no curls, no twist, no veil. Result: no hair. New problem: spaced antler/horn spikes around a bright smiley read as horns or a sun; the head is a devil/sun emoji more than a root hood. Tines are not fused into a root mass (no shoulder roots joining them). Partly met.
2. **Webs**: every web edge is a strand (arm underside, a drip strand hung from the arm, a trunk-flank strand, hanging cascade strands) or a catenary sag between two attachment points (curved, parabolic); no rectangular panels; holes pointed ovals along flow (open fraction 0.21-0.33), min ligament 11 mm. Wings are now small wedges, c01 has far larger perforated sheets. The first version (arm + vertical drip) was a rectangle and was thrown away. Cascade curtains are short and dark. Met in rule, weak in effect.
3. **Maw**: jagged asymmetric outline (sawtooth teeth, stronger on the left, two bites on the right), centre offset +10 mm, tilt 3 deg, 150 x 316 mm, 1.09-1.11 x mask; no rolled lip; a continuous outer rib left, a broken one right, 7 splayed rib stubs. The shard-like wall facets make the interior read broken/shattered; still a tall slit mouth. Suggestive-anatomy read reduced, not proven gone.
4. **Trunk**: half-width 88-132 mm (was 100-184), same height; torso_width_frac 0.459 / 0.484 (gate pass, was 0.74-0.81). The failure was not the trunk: it was hole-filled loops (H4 trailing into H5's hook enclosed a wedge). H4 now stops short and H5/H4/H9 are thinner, so the lower right is lighter than r07's T2/T3 band (IoU cost). Vertical ribbing: 2 (b) / 3 (c) strands per side, 11-15 mm wide, along the trunk and around the maw. They read as a ladder/ribcage, not bark; the trunk between them is still smooth.
5. **Mask**: lens recessed (rim at z 74, trunk surface 73), bezel removed, a flesh collar (r 9-14 mm) overlaps the lower rim, tines cover the top edge on b and c. Sticker look reduced; the collar shows as a lumpy pale-edged rim and the mask is still the brightest and flattest object. Fixed a mask-centre bump (head top poked through the lens: read as a nose).
6. **S3_LL**: checks.py #12 now 300 mm in both. I did not isolate the 6 mm intruder in r08b (a direct voxel search found nothing there either); r08c removed the wings that sat left of x -215 and the over-the-top finger hooks, and the read cleared. Cause unconfirmed.

## 3. Versus Evan's r07 notes
Squid: less (no mantle, tall narrow trunk, ribs), but the tall slit maw plus tentacle cascade is still octopus-person. Gothic/Beksinski: spires and ribs read gothic; not Beksinski (smooth flesh, no erosion). Base: unchanged and good, nothing flat. Two-legged: no pair; H1 and H5 remain the two long diverging strands. vs c01: c01 is fibre lace everywhere; r08c is cleaner, thinner, and has the lowest c01 IoU yet.

## 4. Reproduce
`python3 build.py G1a_b` -> `python3 iou_r07.py G1a_b` -> `python3 torso_test.py G1a_b` -> `python3 render_comp.py G1a_b --views front,tq --mask --samples 24` -> `python3 run_checks.py` -> `python3 measure_extra.py` -> `python3 make_sheets.py`. `renders/contact_sheet.png` has b, c, r07 G1a, r08b b, c01. `build/` is large; not for commit.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-17 | cad-worker | Initial creation: round-08c studies | [PROVISIONAL] |
