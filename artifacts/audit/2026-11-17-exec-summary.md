# Audit Cycle 3 — Exec Summary (2026-11-17)

Auditor: Audit Lead. Scope: 34 commits since cycle 2 (ae60df5..1015353), rounds 05-06, RP-2 outcomes, Orchestrator session log, CAD generators v1/v2/v2.1. Rubric: docs/AUDIT.md v1; threshold = any RED, or 2+ YELLOW on R1/R4 in one area. Known in-flight, not scored: docs/DESIGN_PRINCIPLES.md, teams/aesthetics/analysis/feature-references.md, round-07.

## TL;DR

**The method as practiced cannot produce c01-grade composition. The Orchestrator's composition-first decision (SL-39) is right in direction and incomplete in mechanism. 1 RED (CAD R1). Recenter fires on CAD (RED) and on Orchestration/process (R1 Y + R4 Y). RP-3 filed.**

- **Pipeline capability.** The kernel (SDF field + 2.5D relief + Gate-2 grain) is not the blocker; c01 is a wall relief and that representation can hold it. The authoring layer is. The body is not a figure. It is a union of 2 fixed ellipses + 8 hand-placed belly ellipses + tube footprints, with mask, maw, eyes, teeth and whips placed as independent features at absolute coordinates (gen_fullpiece.py L25-31, `mass_ells`, `mass_sd`). No skeleton, no gesture, no focal hierarchy, no relation between parts. Three builds (v1, v2, v2.1) improved features and left composition unchanged. None of the 4 variant axes moves composition. Details below.
- **Rounds 05/06 are one failure, not two.** r05 1/2/10, r06 0/1/11 (recounted from issue snapshots: tools/verify_tallies.py 6/6 PASS). The one love (r05 h4) and the one like (r06 h4, "LOVE THIS") are the same card type, the side profile. That is depth, which the 2.5D relief gets right. Everything he disliked is front-view composition.
- **SL-39: agree, with 4 amendments** (primitive must change, approved silhouette must bind the 3D build, objective composition gate, explicit lock release). Without them the silhouette board is a detour that the next CAD pass discards.
- **SL-35 was the expensive error.** The Orchestrator wrote "nowhere near c01's open sprawl" (SL-34), CAD graded sprawl C, and the hero was boarded anyway on the premise that the 3x3 ft envelope bounds sprawl. Round-06 cost 11 dislikes. The premise is not demonstrated (below), and the log has not retracted it.
- **RP-2: 5 of 8 held, 3 partial.** Disclosure and sourcing improved materially. Structural/Fabrication review of the v2 mesh did not happen before the board shipped. The board notes still bury the decision-critical question below the banner fold.
- **Orchestrator log: works.** Basis tags on every entry, errors owned (SL-02, SL-29, SL-32a), independent reads written before CAD's (SL-26/28/34) that matched both CAD's self-grades and Evan's verdict. Three choices visible in git are missing from it.
- **Separation of duties (SL-32, SL-36): acceptable once, now a pattern.** One part (SL-32c, authoring new evidence under Fabrication's name) crossed the line.

## Scorecard

G / Y / R. Evidence per cell in the sections below. Cycle 2 for comparison: 11 Y, 0 R.

| Area | R1 Vision | R2 Readable | R3 Modular | R4 Evidence | R5 Process |
|---|---|---|---|---|---|
| Aesthetics (Orchestrator acting as lead) | Y | G | G | G | Y |
| Structural | Y | Y | G | G | Y |
| CAD | **R** | Y | Y | G | G |
| Fabrication | G | Y | n/a | G | Y |
| Orchestration / process | Y | Y | G | Y | Y |

Cycle 3: 1 R, 13 Y (matrix: Aesthetics 2, Structural 3, CAD 2, Fabrication 2, Orchestration 4). Movement vs cycle 2: CAD R4 Y to G, CAD R5 Y to G, Aesthetics R2 Y to G, Fabrication R1 held G, CAD R1 Y to R, CAD R3 G to Y, Process R1 G to Y.

### Aesthetics

- **R1 Y.** Backprop is accurate (r06 recount exact: issue #6 0/1/11 = DECISIONS row = review/verdicts/round-06.json; all 12 ids match manifest). Directives (1)-(6) in the r06 row each trace to a quoted note. Not clean: the r05 locks "shelf arrangement A + placement" and "radial layout stands" were inferred from bare dislikes (SL-03) and conditioned on headroom (SL-10). They drove the v2/v2.1 build (shelf keep-out boxes, radial whips). Commit 1015353 deleted the "Kept from r05: shelf arrangement A layout (conditional...)" text from teams/aesthetics/STATUS.md and SL-39 plans "shelves at limb ends". No DECISIONS row or SL entry releases the locks. Release is correct; silence is the defect. Also: r05 Takeaways line sits below r06 (cosmetic).
- **R2 G.** STATUS exec lines current through r06; takeaways updated; 70 lines total including header, blanks and edit log (cap is content lines; not recounted). Cycle-2 issues closed.
- **R3 G.** r06 ran on the unchanged manifest-driven app; verdict snapshots now in review/verdicts/ (SL-13), checked by the tally script.
- **R4 G.** `python3 tools/verify_tallies.py`: 6/6 PASS (r01-r06). Cycle-2 gap (script did not check verdicts) closed (4dd6f70).
- **R5 Y.** Backprop same session (SL-38). Rows from 2026-11-17 still [PROVISIONAL]: aesthetics STATUS (2 rows), DECISIONS (2 rows).

### Structural

- **R1 Y.** Alt tentacle counts 2/4/5: still no structural alternate. The only "count" test is CAD's 5-vs-8 one-axis card, which Evan answered with a texture/blob note (vb2), not a count signal.
- **R2 Y.** STATUS header still "Awaiting CAD mass model" (teams/structural/STATUS.md L3); three meshes exist. Open item L28 "fullpiece_v2 review (mass, hard-points)" outstanding.
- **R3 G.** Constraints separate from implementation (load-model-v1 parametric in p, s).
- **R4 G.** RP-2 numbers hand-checked: 22 mm solid I = pi r^4/4 = 11,499 mm^4; 24x3 tube I = pi/64 (24^4 - 18^4) = 11,133 mm^4; both >= the 11,000 stated in DECISIONS RP-2 row and rp2-strut-limb-voids.md. Shelled-mass table (0.22/0.31/0.42 x 22.2 kg = 4.9/6.9/9.3 kg) consistent.
- **R5 Y.** RP-2 item 3 required "review fullpiece_v2 mass and hard-points before the round-06 board ships". No structural file mentions v2 or v2.1 meshes except as pending (rp2-strut-limb-voids.md L210). Board shipped. Last Structural commit 58bb675 (2026-11-16 16:29). Item not logged as waived.

### CAD

- **R1 RED.** Compliance is measured by Evan's verdicts, not by traceability. Two consecutive rounds 1/2/10 and 0/1/11 on the one named target (c01-grade organism); the team's own README concedes "not c01's open webbed sprawl; limbs thick and short; ~60% of box width" (fullpiece_v2_1/README.md s.5). Honest self-assessment is good R4 behaviour; it is not compliance. The cause is method (next section), so another pass under the same method is predicted to fail again. RED because the recenter must happen at method level, not feature level.
- **R2 Y.** STATUS body still says "No geometry yet" (L3) and "Takeaways: None yet" (L42) after 8 builds. Both flagged in cycle 2, unfixed. [PROVISIONAL] tags cleared.
- **R3 Y (was G).** v1/v2/v2.1 are three forked 486/758/884-line copies ("Copy of ../fullpiece_v2/", v2_1 README L3), not one parametric generator. Composition is hard-coded (BODY, BELLIES, whip `specs`, MASK_C, MAW_C), headroom keep-out is in code, variants are 4 knobs. A composition redesign cannot be done by changing parameters.
- **R4 G (was Y).** v2.1 README s.3 numbers match engineering_checks.json (bbox 910.6 x 910.9 x 300, mass 26,440 g, eyes 20, whip lengths 309.8-432.5 vs 520-820 requested, shelf flats, relief 53.6/17.7/47.7/84.7, pad 84 x 66). Unsourced estimates are named in README L3. v1 headroom (12 mm on S2, S3) re-measured and sourced (fullpiece/engineering_checks.json). Gate-2 "no net thinning" retracted in CAD STATUS L10.
- **R5 G (was Y).** [PROVISIONAL] tags cleared in bodies; v2/v2.1 rows signed (88b8f46) before the round-06 deploy (6ac78db): RP-2 item 5 honoured.

### Fabrication

- **R1 G.** Nothing contradicts verdicts.
- **R2 Y.** STATUS header "final segmentation blocked on CAD geometry"; "refresh DEFERRED until the v2 mesh lands" (SL-14). v2 and v2.1 landed; no refresh, no new deferral. 16-segment / 12.6 kg plan still unreconciled with a 914 mm, 26 kg-solid piece.
- **R3 n/a.**
- **R4 G.** rp2-blind-pockets.md evidence now has a script and JSON (heightfield_check.py/.json). NOT re-run by me (inputs not committed, STLs gitignored); see Not verifiable.
- **R5 Y.** The row resolving Fabrication's own FLAG OPEN (STATUS L38) was written by the Orchestrator and is [PROVISIONAL].

### Orchestration / process

- **R1 Y.** SL-35 boarded a hero the Orchestrator itself read as "nowhere near c01" (SL-34). SL-03 inferred locks from dislikes; unreleased (above).
- **R2 Y.** Session log is readable and well tagged. Log times run ~1 h ahead of git author dates (SL-35 01:55 vs commit 9390773 01:50; SL-37 02:45 vs 6ac78db 01:53; SL-38/39 ~03:00 vs 1015353 02:06) and entries are not strictly chronological (SL-33 00:55 after SL-31/32 01:30); previously noted by reviewer, unfixed. Round-06 banner: see RP-2 item 1.
- **R3 G.** Manifest-driven board unchanged; cards, images, verdict snapshots decoupled per round.
- **R4 Y.** Authors still indistinguishable in git (all "Claude", all trailers "Opus 5.5", including worker WIP snapshots committed by the Orchestrator, e.g. 1a058b5). Email ping (SL-37) not evidenced in repo. Manifest "est. ~13 kg printed vs 14 kg cap" has no committed derivation (derivable: structural ~11 kg at 22.2 kg x 26.4/22.2 = 13.1; arithmetic not written down).
- **R5 Y.** About ten edit-log rows still [PROVISIONAL] (session log SL-37 and SL-38..40; DECISIONS vote-record and r06; aesthetics 2; audit 3 incl. my own cycle-2 and cycle-3 rows; fab resolution row). Separation-of-duties pattern (below). CLAUDE.md marks review/rounds/ DO-NOT-EDIT; SL-36 edited round-06 pre-deploy. Defensible, but the rule has no pre-deploy carve-out and the reviewer explicitly did not assess it.

## Method-capability finding (R1 central question)

**Question.** Is the CAD pipeline (parametric SDF features in a fixed envelope) structurally capable of c01-grade organic composition, or is the method the problem?

**Answer.** Split it. The kernel can; the authoring method cannot. Not experimentally tested (see test below); finding rests on code, renders, and verdict notes.

### Evidence 1: how the body is defined (code)

fullpiece_v2_1/gen_fullpiece.py:
- Body mass = `min` over `BODY` (2 ellipses, semi-axes 235x275 and 175x125 mm, L25) + `BELLIES` (8 ellipses, L31-34) + limb tube footprints + root bulbs (`mass_ells`, `mass_sd`, ~L420). The two BODY ellipses alone are ~33% of envelope area before overlap (pi x 235 x 275 + pi x 175 x 125 = 272 k mm^2 vs 914^2 = 835 k). Auditor pixel estimate from c01 (904 x 1200 jpg, figure bbox ~700 x 680 px): torso + maw ring ~200 x 330 px = ~14% of figure bbox area. Eyeballed, not traced.
- Limbs = `specs` list of 8 hard-coded (angle, length, bend, root radius, z) tuples, rooted 95-140 mm out from a fixed centre `c0 = (-60, 10)` and fanned radially (build_limbs, L148-176). Radial fan from a disc is the layout. Shelves are separate rectangular plates (`SHELF_ARR`, 190 mm wide, fixed xc +-345) with arms run under them and "seat blocks"; in c01 the shelf IS the limb tip.
- Mask (`MASK_C`, `MASK_R`), maw (`MAW_C`, `MAW_AB`), eyes (rejection-sampled on any surface with slope <= 45 deg within 340 mm of centre), teeth (fibre set around the maw ellipse): independent features at absolute coordinates. Nothing relates head to torso to limb. No parameter exists for gesture, silhouette, negative-space ratio, or focal hierarchy (grep for silhouette/gesture/skeleton/torso/focal/figure in gen_fullpiece.py: 0 hits).
- Answer to "figure or union of features": **union of features**. The Orchestrator's diagnosis in SL-39 is correct.

### Evidence 2: renders

- review/rounds/round-06/images/hero_front.png and variants_sheet.png. Two concentric ring motifs (round mask bezel, round toothed maw ring) with spokes read as a gear or sun; Evan's "clockwork" is a literal description. Silhouette is a compact filled square with the three shelf boxes bolted on. c01 is an open figure: small head, narrow torso, long drooping limbs, large negative space between them, shelves at limb tips.
- The four variant axes (masquerade device, tentacle count, maw size, eye count) all live inside one composition. The v2.1 sheet shows 4 variants that differ in details Evan did not respond to (all disliked, no axis signal; DECISIONS r06 row).
- hero_side.png (h4, loved twice) shows what the method does well: stacked-depth profile, 3 shelf levels. 2.5D relief is a good fit for the product.

### Evidence 3: verdict notes (review/verdicts/round-06.json)

- h1 "weird clunky cluttered clockwork look. poor compositional skills." vc2 "actually integral body of the creature has been almost entirely lost. fully revise your design around a clearly defined organism... review the original concept art and notice how far this is." vb2 "tentacles are not obvious... a blob on the wall." r05 h2: "overall creature form has not been preserved."
- Each is a figure-level complaint. None is a surface-detail complaint. The feature-level asks (hands, smiley, bone, teeth, eyes) are real but secondary and are the ones the pipeline already improves each pass.

### Evidence 4: trajectory

v1 to v2 to v2.1: eyes, palette, smile, teeth, shelves, mass all moved; Orchestrator and CAD self-grades on sprawl stayed C (SL-34, README s.5); Evan's verdict worsened 1/2/10 to 0/1/11. Cost of a build is not the constraint (~3 min field + ~30 s mesh + ~2.5 min per view, README s.6). The loop is blind numeric authoring followed by an agent reading renders; it converges on features because features are what the code exposes.

### Is it the envelope? (challenges SL-35)

SL-35 argues sprawl is "bounded by a LOCKED parameter, not CAD effort" (whips 310-433 of 520-820 mm requested). Auditor estimate from c01 pixel coordinates, scaled so figure width = 914 mm: limb-tip distance from torso centre is ~500-570 mm (upper-left shelf tip ~540, right tip ~500, lower tips ~555-570). That is longer than the generator achieved, but the generator roots whips 95-140 mm out from a centre offset (-60, 10) and sends them nearly radially against a 440 mm clip; c01's limbs root at the torso and sweep, bending (drooping) back inside the frame. Evidence that the envelope, not geometry placement, is binding: none in repo. Evidence that placement is binding: whips terminated by the clip and keep-out boxes, per README s.4 item 2. The 3x3 vs 4 ft question may still matter later; it is not shown to be what blocks c01 composition now. Not proven either way without the c01-trace test below.

### What would settle it (not run; recommended before any new 3D)

**c01-trace test.** Trace c01's silhouette and limb centrelines to a mask and skeleton, feed them into the existing generator as the `mass` input (replace BODY/BELLIES/whip `specs`), keep Gate-2 texture, relief rule, shelf flats, 914 envelope. Render the same view. If it reads as c01 at board scale, the kernel is fine and the whole problem is authoring: go with the options below. If it does not, the kernel/relief rule is also limiting and Option B or a hybrid is needed. Cost: hours, one worker, one render.

### Method options

| # | Option | Pros | Cons |
|---|---|---|---|
| A | **Composition-first silhouette stage** (SL-39) | Cheapest place to fail; Evan rules before detail is spent; matches his stated ask (vc2, h1); keeps SDF kernel and every engineering gate | Only helps if the approved silhouette binds the 3D build; silhouettes drawn by the same feature-stacking habits repeat the failure; one more round of "regress" optics; side-profile depth (loved) must travel with it |
| B | **Figure primitive in the existing SDF code** (skeleton graph: head, torso, N limbs as curves with radius profiles, smooth-union, shelves as limb ends) | Fixes the root cause (body = figure); small refactor: `tentacle()`, `DLimb`, `lse()` already exist; keeps hard-points, validation, regeneration per verdict | Still blind numeric authoring; gesture quality depends on the curve author; webbing between limbs needs the Gate-1/2 vocabulary retargeted |
| C | **2D concept first, then derive silhouette + skeleton + height prior** (c01/c02 were 2D generations and Evan loved them) | Composition quality comes from the tool that already produced it; Evan sees finished-looking images; relief is nearly a depth map; 3D stage then adds shelves, headroom, hard-points as exact booleans | Image generator dependency (Canva credits; no in-environment fallback, aesthetics STATUS); depth-from-image plausibility not exact; non-deterministic composition stage; touches the 2026-11-15 row "image-to-3D reference-only" (depth/silhouette prior is not a mesh, but log the reading); depth tooling availability not verified |
| D | **Blender skin-modifier / metaball body** | Organic joins for free; bpy 5.3.0 headless verified (toolchain-assessment) | No viewport, scripted sculpt brittle (assessment s.(b)); a second geometry authority; same blind-authoring loop; does not fix lack of a figure unless fed a skeleton, at which point it is Option B in another tool |
| E | **Image-to-3D as geometry source** | Fast plausible shape | Non-manifold/fused, no flat back, no hard-points, non-regenerable (toolchain-assessment); remain reference-only |
| F | **Human sculpt (Evan or hired) of the body, agents do engineering** | Highest chance of c01 gestalt | Human time/cost; outside the pipeline; fallback only |

**Recommendation: A + C feeding B.** Silhouette/gesture from 2D (generated or drawn) approved by Evan, converted to skeleton + mask, consumed as hard input by an Option-B figure generator; SDF kernel and engineering stay. D and E not recommended. F is the fallback if two composition rounds fail (stop rule in RP-3).

### SL-39: agree, with four amendments

Agree: root cause diagnosis (feature stacking, no figure), the order (principles, feature references, composition board, then detail), rejection of a v3 symptom pass, depth profile on the board. The log's admission "my own briefs (SL-05, SL-30) were feature lists too" is accurate (SL-30 lists 6 feature items, 1 composition item: sprawl to ~80%).

Amend:
1. **Change the primitive, not only the order.** "Value-blocked silhouettes of a defined organism" needs an authoring unit that is a figure (head, torso, limbs with gesture curves), not another feature set rendered flat. And the approved silhouette + skeleton must be a hard input to the 3D generator with a check (silhouette IoU against the approved mask at the end of the build; auditor proposes >= 0.85 as a starting value, [GENERAL], to be set by the aesthetics lead). Without this the approval is decorative.
2. **Gate composition objectively.** Trace c01 once; define 4-5 numbers (fill ratio, negative-space ratio, torso width fraction, limb reach/torso, number of distinct limbs, head-to-background value contrast) in DESIGN_PRINCIPLES; compute on every silhouette and every later hero render by an agent that is not CAD. Board only if the numbers sit near c01. Also adopt the rule SL-35 violated: do not board a hero whose own self-grade is C or worse on a verdict-named axis unless the card asks Evan that axis question as the question.
3. **Release the inferred locks in writing.** DECISIONS row: shelf arrangement A placement, radial layout, "texture quality stands" are released or re-conditioned; stand: depth/relief profile (h4 x2), smiley + maw motif, Gate-2 surface vocabulary, headroom 300 mm. Put the release on the round-07 board (Evan may veto).
4. **Silhouette-board hygiene.** Question first: banner notes cap at 5.6 em (review-app/index.html L36, about 4 lines, ~200 chars on a phone; my estimate, not rendered). r06's question sits at char 285 of 1,428 and the headroom correction at 566. Put the decision as a card, or keep notes under ~200 chars. Editing the app needs Evan OK (CLAUDE.md DO-NOT-EDIT).

Risk to watch: if two composition rounds do not move the like rate, the signal is Evan's brief, not CAD; stop and ask Evan for a sketch or a pick-from-spread session (RP-3 item 8).

## RP-2 outcomes (8 items)

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Board disclosure in round-06 notes | **Partial.** Content: held. Placement: not. | review/rounds/round-06/manifest.json notes list headroom correction (r05 ~12 mm on 2 shelves, fixed), every known gap, 25 kg target, "nothing print-validated". Added after sign-off (c98627b): 2 missing gaps, the invented "saliva". Placement: 1,428 chars in a 5.6 em scroll banner; envelope question at char 285, correction at 566. RP-2 item 1 said "short enough to sit above the fold". Evan did not answer the envelope question. The r05 manifest cross-check (cycle 2) is the same defect, repeated. |
| 2 | Source every README number | **Held.** | v2.1 README s.3 vs engineering_checks.json: 12 of 12 spot-checked match (list under CAD R4). Estimates named in README L3. v2 README/gate READMEs "every number keyed" softened (c98627b). Residual: manifest "~13 kg printed" has no committed derivation. |
| 3 | Structural/Fab re-engage; review v2 before board | **Partial.** | Held: both delivered item-3 analyses (f1f688c, 58bb675), numbers adopted (DECISIONS RP-2 row), CAD hit them (core 22 mm, pad 84x66, seat 28, headroom 0 intrusions). Not held: Structural review of v2/v2.1 mass and hard-points; Fabrication segment/mass refresh; board shipped without either and no waiver logged. SL-14 deferred the refresh "until v2 exists"; v2 existed 2026-11-17 00:42. |
| 4 | Gate-2 claim | **Held.** | teams/cad/STATUS.md L10: "'no net min-wall thinning' claim is retracted", with the worsened metrics (0.222 to 0.330; 1.16 to 0.75 mm; 0.075 to 0.136). |
| 5 | Sign-off rules in substance | **Held, with caveats.** | Cells since 2026-11-16 name what was verified (hashes, numbers, files), separate "verified" from "judgment not assessed", and use FLAG OPEN (3 on RP-2 rows, 3 on v2/v2.1/manifest). The reviewer caught real defects: c98627b manifest gaps, invented "saliva", "every number keyed" over-claim, SL-02 numbers, RP-2 5-of-7 tally. Body [PROVISIONAL] tags cleared with sign-off (grep: none left on signed rows; 88b8f46). Caveats: reviewer independence still unevidenced (same git author); the newest ~10 rows are unsigned (batching delay is within the same day, not the 14.5 h of cycle 2); the fab heightfield "re-run reproduces every value" claim was verified for file existence and wording only, not re-run. |
| 6 | DECISIONS disclosure | **Held.** | DECISIONS 2026-11-16 disclosure row for 3e58215; row-order rule in header; `git show 3e58215` matches the quoted before/after. Append-only since: no older row bodies edited (`git diff 1ebb51a HEAD -- docs/DECISIONS.md` shows only added rows, header rule, edit-log cells; also checked the session log: only sign-off cells changed). |
| 7 | Tentacle count tested | **Held nominally, no signal.** | Round-06 vb1/vb2 (5 vs 8). vb2 note is about texture and "blob", not count. 2 and 4 untested. Structural alternates not produced. Recommend: waive formally until a composition exists, ask Evan once. |
| 8 | Carry-overs | **Held.** | tools/ in CLAUDE.md map (and review/verdicts, session-log); tally script checks verdicts, 6/6 PASS; deviation log has the model entry (AGENTS.md deviation log 2026-11-16): trailers "Opus 5.5" from 0671872 are the Orchestrator's. |

RP-2 vote record: the RP-2 adoption row and vote correction row (6 of 7) are internally consistent only through the Orchestrator's relay of the Structural and CAD votes (audit STATUS Vote line). Outcome is unaffected: Orchestrator 3 + Fabrication 1 = 4 of 7 is already a majority; the relay claims are not independently verifiable.

## Orchestrator session log (artifacts/session-log/2026-11-16-orchestrator.md)

**Is it doing its job? Yes, mostly.** 40 entries; every entry has a basis tag; backfilled entries are labelled as backfill; append-only held (diffs show only sign-off cells changed). Errors owned: SL-02 corrected by SL-29 (headroom 160 to 12 mm), SL-32a (5-of-7 tally), SL-39 (own briefs were feature lists). SL-26/28/34 independent reads, written before CAD's grades, matched CAD's grades and Evan's verdict: the Orchestrator's eye is reliable; the failure was the decision to board anyway.

**Choices visible in git or files that are NOT in the log:**
1. **Mass target 22 kg to 25 kg.** SL-23 forwarded "keep solid-mass proxy <= 22 kg" (Structural's 22.2 kg basis). SL-30 brief says "<= 25 kg"; v2.1 README and manifest use 25. No entry, no Structural concurrence. Basis: unlogged `[judgment]`.
2. **Release of r05 locks** (1015353 deleted the "kept from r05" shelf A/radial text from aesthetics STATUS; SL-39 uses "shelves at limb ends"). No entry, no DECISIONS row.
3. **Structural review of v2 skipped before board** (RP-2 item 3). SL-35 lists "no print validation" as a gap but does not record deciding to ship without Structural/Fab review.
4. Minor: card selection and framing in the round-06 manifest (5 hero views, sheet card, h1 rationale "judge overall read"); round-06 deploy email wording (SL-37 says it repeated the question and correction; email not in repo).

**Errors not (yet) owned:** SL-35's premise "sprawl bounded by locked envelope" was not revisited in SL-38 (which infers "silence = keep") or SL-39. SL-30's brief ("c01 sprawl filling ~80% of envelope") assumed the opposite one day earlier. Recommend a correction entry. Also SL-35 itself should carry `[error]` if Evan's verdict is read as refuting it; the Orchestrator should decide, not me.

**Log hygiene:** timestamps ~1 h ahead of git; not strictly chronological (SL-33). Use git commit time in the entry or drop the clock.

## Separation of duties: SL-32, SL-36

**Straight answer: acceptable once under rate-limit cost; now a pattern; one piece crossed the line.**

What was done: the Orchestrator resolved reviewer flags on files owned by Aesthetics (headroom wording), CAD (README/STATUS over-claims, whip %, render count), Fabrication (new heightfield script + JSON, corrected "85-90%" to "84-86%"), the Audit team (RP-2 vote line in teams/audit/STATUS.md), and its own manifest.

Why acceptable: edits are disclosed in the Orchestrator log and in each file's edit log as `orchestrator`; each was signed with a verification cell (not clean-passed); changes to CAD files were textual (softened claims; named unsourced estimates rather than inventing sources); the alternative (re-spawn leads under the 5 h limit for one-line fixes) was costly, and a previous deviation (r04 trawl) set the precedent of disclosing instead of forbidding.

Where it crosses:
1. **SL-32c authored new evidence in another team's name.** heightfield_check.py/.json is analysis, not wording. Reviewer verified existence and the "84-86%" wording; no one re-ran it (inputs gitignored). The row is still [PROVISIONAL]. Fabrication owns a finding it did not write.
2. **SL-32a edited the audit team's file** to record votes the leads never wrote. The "relayed" label is honest; the evidentiary value is the Orchestrator's transcript.
3. **Pattern.** The author of the manifest (SL-36), the person who resolves the flags on it, and the person who ran the sign-off pass (SL-31) are one session. Independence is only as strong as the reviewer persona's cell, and nothing in git distinguishes them.
4. CLAUDE.md "DO NOT EDIT" on review/rounds has no pre-deploy exception; SL-36 used one. Justified (undeployed; the review-app had no round-06 at that point; origin/main = 88b8f46 at deploy), but the rule should say so.

Rule proposed in RP-3 item 6: the Orchestrator may correct wording in another team's file when (a) change is textual with no new numbers, (b) the file's own edit log names "orchestrator on behalf of <team>", (c) the owner confirms at its next spawn (cell turns from [PROVISIONAL] to signed only then). New analysis, scripts, and votes come from the owner. The Orchestrator does not enter other teams' votes; leads write them.

## Lagging areas

- **CAD: method, not effort.** RED. Fast, honest, wrong abstraction. See finding.
- **Orchestration: shipped a known-C hero.** The expense was a round. Lock release unlogged.
- **Structural and Fabrication: back in the "waiting for CAD" state** after a good RP-2 burst (item 3 delivered 2026-11-16, nothing since). Not blocking now, because geometry is about to change (composition stage); cheapest to re-engage with v3.
- **Not lagging:** Aesthetics bookkeeping (verdict accuracy, tally, STATUS currency).

## Cross-checks

| Check | Result |
|---|---|
| Issue #6 verdict JSON vs DECISIONS r06 row | 0 love / 1 like / 11 dislike of 12; exact (tools/verify_tallies.py PASS) |
| Round-06 ids vs manifest | 12 / 12 match |
| tools/verify_tallies.py, all rounds | r01-r06 PASS |
| v2.1 README s.3 vs engineering_checks.json | match (bbox, mass 26,440 g, eyes 20, whips 309.8-432.5 / 520-820, headroom 0/0/0 over 62 mm, pad 84x66, relief mean 53.6) |
| v1 headroom 12 mm (SL-29) vs fullpiece/engineering_checks.json | match (S2 855 intruders, S3 60,607 intruders, clear 12.0 mm) |
| Structural I values (22 solid, 24x3 tube) | 11,499 and 11,133 mm^4 >= 11,000 |
| Orchestrator deploy claim (SL-37) vs git | origin/main = 88b8f46; local main two commits ahead (6ac78db, 1015353), unpushed |
| Gate-2 retraction (CAD STATUS L10) | present with the three worsened metrics |
| Session log append-only | 88b8f46, c98627b, b2c9dc5, 9390773: only edit-log sign-off cells altered |

## Recenter

Threshold fires: **CAD R1 RED**; **Orchestration/process R1 Y + R4 Y**. RP-3 filed in teams/audit/STATUS.md. RP-3 items 1 and 4 touch the vision (lock release, composition target) and escalate to Evan via the round-07 board; the rest go to council vote. The Orchestrator already decided the method change (SL-39); RP-3 does not reverse it, it binds it.

## Not verifiable

- Whether the c01-trace test would succeed (not run; no experiment, no new builds).
- Evan's direct-chat verdicts and the "Deploy + email ping" tap (SL-37); the email itself and its content.
- Structural and CAD votes on RP-2 (relayed by the Orchestrator).
- Fabrication heightfield numbers: script and JSON exist; inputs not committed, STLs gitignored; I did not re-run.
- Banner fold behaviour on a phone (estimate from CSS only; not rendered).
- c01 measurements: pixel estimates from the jpg (not traced; no scale ground truth); the "~14%" torso fraction and the 500-570 mm reach are order-of-magnitude.
- Whether docs-reviewer is an independent agent (git cannot tell).
- Print-readiness, min-wall, segmentation of v2.1 (CAD README s.4 item 8: not validated).
- DESIGN_PRINCIPLES.md, feature-references.md (in flight); round-07 (not built).
