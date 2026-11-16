# Audit Cycle 2 — Exec Summary (2026-11-16)

Auditor: Audit Lead. Scope: 15 commits since cycle 1 (42b4ae4..ae60df5) plus the uncommitted r05 backprop (DECISIONS.md, teams/aesthetics/STATUS.md). Rubric: docs/AUDIT.md v1, recenter threshold as recalibrated (any RED, or 2+ YELLOW on R1/R4 in one area).

## TL;DR

**RP-1 held. The pipeline now moves: geometry has an owner, a method, five gated builds, and a full-piece composition that Evan voted on. Numbers I could check are mostly honest. The weak points are (1) the CAD team's constraint disclosure and number provenance, (2) Structural and Fabrication going dark while CAD runs ahead, and (3) a sign-off process that is real in form and thin in substance. 0 RED. Recenter fires on CAD only (R1 Y + R4 Y). RP-2 filed.**

- RP-1 outcomes: geometry owner assigned and method executed (DECISIONS 2026-11-15 rows; teams/cad/gate1..gate2, fullpiece). Structural pass committed and signed (29271ce, 4d4bb96). Board renders manifest `notes` (e252b5a: `m.notes` into `#notes-banner`). Round-05 exists (13 cards, review/rounds/round-05/manifest.json). Hygiene mostly durable; two residuals below.
- r05 backprop is accurate. I pulled issue #5 and recounted: h4 love; h1, h2 like; h3, v1a, v1b, v2a, v2b, v3a, v3b, v4a, v4b, s1 dislike = **1 / 2 / 10 of 13**. Matches the DECISIONS row. Card ids match manifest 1:1.
- Worst finding: the hero violates a locked plant-shelf constraint (300 mm headroom; DECISIONS 2026-11-14 sketch row, mesh-spec-v1 s.4) and the board does not say so. Evan then praised "great shelves and placement" (issue #5, h1) and the backprop locks "shelf arrangement A + placement". CAD's own README s.4 item 2 says S3 has ~160 mm effective clearance. Round-05 manifest notes and card rationales never mention headroom.
- Second: the strut. Three incompatible specs: load-model-v1 20 mm OD x 1.2 mm tube (I = 3,144 mm^4); mesh-spec-v1 26 mm OD, I >= 6,300 mm^4 [PROPOSED, unsigned]; fullpiece v1 r15 solid (I ~ 39,800 mm^4, my arithmetic). Structural has not touched the repo since 2026-11-15 18:45 (3e58215). Evan already said the leg "sticks out unrelated to the prior sculpture" (h2).
- Third: sign-offs. Batch-flipped in ae60df5 (four CAD rows unsigned for up to 14.5 h, then signed in the commit that also added the next deliverable). Real flags exist on 3 of 7 burst rows; the other 4 passed clean, including one with a defect I found (Gate 2 "no net thinning"). See Process.

## Scorecard

G / Y / R. Evidence per cell below.

| Area | R1 Vision | R2 Readable | R3 Modular | R4 Evidence | R5 Process |
|---|---|---|---|---|---|
| Aesthetics | G | Y | G | G | G |
| Structural | Y | Y | G | G | Y |
| CAD | Y | Y | G | Y | Y |
| Fabrication | G | Y | n/a | G | Y |
| Orchestration / process | G | Y | G | Y | Y |

Cycle 1 for comparison: 9 Y, 0 R. Cycle 2: 11 Y, 0 R (Aesthetics R4 and Structural R4 improved; CAD and Fabrication now scorable and mostly Y on freshness and sign-off).

### Aesthetics

- **R1 G.** r05 recount exact (above). Locks trace to named notes: h4 depth, h1 shelves/maw, h2 buttress/organic form, h3/v1a face. Caveat, not drift: "radial layout STANDS" (DECISIONS r05 row) is inferred from v3 dislike; Evan said nothing about layout. With 10 of 13 cards disliked, dislike of an alternative is weak evidence of endorsement of the hero. Smiley re-center row cites "Evan, direct chat": not auditable.
- **R2 Y.** teams/aesthetics/STATUS.md is 99 lines against its own header cap of 60. Exec Summary (newest-first) has no r05 verdict line; the verdicts live only in Current State. A "Superseded round-05 charter" paragraph sits in Current State. Takeaways section not updated with r05 lessons (rejected list was).
- **R3 G.** r05 ran on the unchanged manifest-driven app plus the e252b5a notes edit. Images are committed in-repo (13 PNGs), not hotlinked.
- **R4 G.** Board exists with images and manifest; issue #5 ids match; cycle-1 R4 gap (r05 "in progress", no artifact) closed. Residual: tools/verify_tallies.py still counts manifest cards only; its docstring says it does not check verdicts. The recount script I asked for was not built.
- **R5 G.** Backprop in the same session as the verdict. Rows are [PROVISIONAL] pending sign-off: declared in-flight, not scored.

### Structural

- **R1 Y.** init_vision asks for 2/4/5-tentacle alternates; still no card in rounds 1-5 and no structural alternate in repo. Fullpiece v1 hero is a 3-shelf layout only.
- **R2 Y.** STATUS header: "Awaiting CAD mass model." CAD delivered a 22 kg solid proxy and strut geometry (fullpiece/engineering_checks.json); STATUS silent. Takeaways are good (3 items) but nothing since 2026-11-15.
- **R3 G.** Functional Constraints still separate from implementation; load-model-v1.md is parametric in p, s.
- **R4 G.** load-model-v1 committed and signed (4d4bb96). Spot-checks hold: 5 x 9.81 x 1.5 = 73.6 N; strut P_cr = pi^2 x 1800 x 3144 / 424^2 = 311 N, matches. Cycle-1 uncommitted SVGs now committed (analysis/side-profile-cantilever.svg, front-anchor-map.svg).
- **R5 Y.** Liaison item "relax 6 mm through-void rule for blind relief" (CAD STATUS Liaison, 2026-11-16) is unsigned by Structural and Fabrication. Gate 1C and Gate 2 progress claims lean on it (160 / 157 voids converted to blind pockets; "72% to 0%" under 6 mm). CAD->structural mesh-spec request (2026-11-15) also still [PROVISIONAL]. Structural has not responded in ~22 h.

### CAD

- **R1 Y.** Hero violates the 300 mm plant headroom (fullpiece/README s.4 item 2; mesh-spec-v1 line 81). Not disclosed on the board (round-05 manifest notes list starburst/mask-focal only). Mask is the focal element despite r04 c05 "not a centerpiece" (self-disclosed, README s.5). Partial credit: CAD self-flags both in the README and in STATUS "NOT honored", and the geometry method choice traces to DECISIONS rows.
- **R2 Y.** STATUS exec lines 7-10 and four README headers still read [PROVISIONAL] after the edit-log rows were signed (ae60df5): two sources of truth. "Next (superseded, done as Gate 1)" is a dead line. Takeaways: "None yet" after five gates that each produced lessons (e.g. fibre grain only reads at close range; pure SDF resists c02).
- **R3 G.** Five variants from one param set (`VARIANTS` in gen_fullpiece.py), seeded (SEED=7), `run_all.sh` per gate, helpers reused from gate2. 10.7 M-tri sculpt not stored but regenerable (README says so).
- **R4 Y.** Verified OK: Gate 1 (validation.json: 11.5% medial samples < 2 mm, 605 g), Gate 1B (17 vs 25 through-voids, 99.0% opening retention, 0 thin components: gate1b/minwall_after.json), Gate 1C (72.3% to 0.0% void area < 6 mm, 160 voids filled, 10 remain, 99.1%, 597 g: gate1c/minwall_*.json), fullpiece bbox/mass/shelf flats vs engineering_checks.json (v3 918.4 x 919.4, hero 22.2 kg, v4 291 mm). Not OK: (a) fullpiece README s.4 item 2 headroom counts (S2 884, S3 62,315) and s.2 relief stats (mean 50 mm, P10/P50/P90) appear in no JSON or generator output; the reviewer flagged the first and signed anyway. (b) Gate 2 STATUS says "no net min-wall thinning". gate2/validation_sculpt.json: surface-inclusive skeleton fraction below thin 2.9% to 8.8%, ridge fraction below thin 0.19% to 1.2%; interior-only ridge fraction 7.5% to 13.6%, ridge P5 1.16 to 0.75 mm; void-area share under 6 mm 22% to 33% (inclusive). The README picks the component-count and opening-retention metrics that improved and discloses the void regression only in prose; the exec line omits it.
- **R5 Y.** Gates 1B, 1C, 2 and fullpiece built on unsigned predecessors; liaison unsigned (above); one reviewer flag left open at sign-off (fullpiece headroom counts).

### Fabrication

- **R1 G.** enabling-v1.md remains consistent with r04/DECISIONS; nothing new claimed.
- **R2 Y.** STATUS "no CAD mesh yet / waiting for CAD geometry" is stale (five meshes exist; fab-relevant numbers: 22 kg solid proxy vs the 12.6 kg plan, v3 over bed-envelope). Takeaways: none.
- **R3 n/a.**
- **R4 G.** No new claims; enabling-v1.md present and cited. Segment plan (16) never re-estimated against the fullpiece.
- **R5 Y.** fabrication->cad liaison [PROVISIONAL] since 2026-11-15; no counter-signature; not consulted on the blind-pocket rule that directly redefines its 6 mm void floor.

### Orchestration / process

- **R1 G.** Board, issue verdicts, escalation path intact; deviations in DECISIONS are Evan-approved or Evan-direct.
- **R2 Y.** CLAUDE.md repo map still omits tools/ (flagged by the cycle-1 reviewer, unfixed) and teams/cad subdirs. AGENTS.md says every agent is Sonnet; the 2026-11-16 commits I sampled (dfa441d, b861dd1, ae60df5) trail "Claude Fable 5"; deviation log covers only the Haiku episode. Aesthetics STATUS over its line cap.
- **R3 G.** Notes banner (e252b5a) renders via textContent (safe). Caveat: banner is capped at 5.6 em with scroll, and the r05 notes are ~900 chars, so the CAD self-assessment sits mostly below the fold on a phone.
- **R4 Y.** Pages deploy is now indirectly evidenced (issue #5 opened 16:07Z, 11 min after ae60df5, with ids matching the manifest). Email ping still unevidenced; no .github dir. Orchestrator and workers still indistinguishable in git: all 30 non-Evan commits are author "Claude".
- **R5 Y.** See Sign-off integrity and Append-only integrity below.

## Sign-off integrity (2026-11-16 burst)

Straight answer: **honored in form, only partly in substance, and retroactive by design. Not a pure rubber stamp. Not independent verification.**

Evidence:
- 7 burst rows went [PROVISIONAL] then signed: CAD Gate 1B/1C/2 (created 01:26Z, 02:09Z, 04:44Z; signed ae60df5 15:56Z, 14.5 h / 13.8 h / 11.2 h later), DECISIONS hybrid row (02:10Z to 15:56Z), vocabulary row (09:41Z to 15:56Z), plus the fullpiece row and aesthetics row signed in the same commit. One commit, one session (Fable 5 trailer), one reviewer persona.
- Substance present: the reviewer produced real flags on Gate 1 (xref error, gitignored STL vs STATUS), the vocabulary row (chronology inverted), and fullpiece (unverifiable counts). Those are defects a skim would not find.
- Substance missing: Gate 1B, 1C, 2, hybrid row: signed clean. Gate 2's "no net thinning" line is contradicted by its own validation_sculpt.json (R4 above) and was not flagged. The fullpiece row was signed with its own flag unresolved. The 3e58215 in-place edit of a DECISIONS row (below) was signed under an edit-log row that does not mention it.
- Dependent work proceeded on unsigned work: fullpiece (b861dd1, 15:53Z) built on three unsigned gates; the r05 board (ae60df5) shipped to Evan with every CAD source line still [PROVISIONAL] in its body.
- Mechanical drift: edit-log cell updated to signed; [PROVISIONAL] tags in README headers and STATUS exec lines left in place (CAD STATUS lines 7-10; gate1b/1c/2/fullpiece README line 3). A cold reader cannot tell which is true.
- AGENTS.md says both agents append edit-log lines in the same commit and no self-sign-off. Practice is overwrite-in-place of an "unsigned [PROVISIONAL]" cell. Cycle 1 flagged the same; AGENTS.md not amended.
- Independence is unverifiable: git cannot distinguish author from reviewer.

## DECISIONS append-only integrity

`git log -p docs/DECISIONS.md`: all `-|` lines are edit-log sign-off cells, **except one**: commit 3e58215 (2026-11-15 18:45Z) rewrote the existing "Step-2 geometry ownership" row's notes ("Method ... to be selected ... selection will be logged here" became "Method selected same day -- see the Step-2 geometry method row"). Content-benign, same-day, but a modification of a prior row, not an append, and not disclosed in the edit log. Header says "Never delete or modify".
- Row order: new rows are inserted above older ones in no consistent order (r05 rows at top; vocabulary above hybrid; r04 above correction above r01). Reviewer flagged once; no rule fixed. Not a content violation.
- r05 backprop rows are uncommitted working-tree edits: no integrity issue yet, noted.

## STATUS staleness

| File | Last touched | Staleness |
|---|---|---|
| teams/structural/STATUS.md | 2026-11-15 18:45Z | "Awaiting CAD mass model" is stale; ~22 h, five CAD builds, no structural touch |
| teams/fabrication/STATUS.md | 2026-11-15 18:45Z | "no CAD mesh yet" stale |
| teams/cad/STATUS.md | 2026-11-16 15:56Z | current except [PROVISIONAL] tags, dead "Next" line, no takeaways |
| teams/aesthetics/STATUS.md | working tree | current on r05; exec line missing, over line cap |
| teams/audit/STATUS.md | this cycle | |

## Lagging areas

- **CAD: ahead and loose.** Fast, honest self-assessment, but disclosure to Evan is incomplete (headroom) and several README numbers have no committed source. Gate 2 void regression (22% to 33% under 6 mm) is unresolved and hidden behind the unsigned blind-pocket relaxation.
- **Structural: lag.** Owns the strut, hard-point, headroom and mass questions; has not reviewed any CAD output. No 2/4/5-tentacle alternates.
- **Fabrication: lag.** Same. 16 segments / 12.6 kg plan has not been reconciled with a 914 mm, 22 kg-solid piece.
- **Process: sign-off ritual.** See above.
- **Not lagging:** Aesthetics (verdict log accurate, board healthy).

## Cross-checks

| Check | Result |
|---|---|
| Issue #5 verdict JSON vs DECISIONS r05 row | 1 love / 2 like / 10 dislike of 13; exact |
| Issue #5 ids vs manifest | 13 / 13 match |
| Card cites in DECISIONS r05 row (h1-h4, v1, v2, v3, v4, s1) | all correct |
| Gate 1/1B/1C validation numbers vs STATUS | match |
| Gate 2 STATUS vs validation_sculpt.json | topology/mass/bbox match; "no net thinning" selective (see CAD R4) |
| Fullpiece README s.3 vs engineering_checks.json | match (bbox, mass, shelf flats); s.2 relief stats and s.4 headroom counts: no source |
| Strut: load-model vs mesh-spec vs fullpiece | 20x1.2 tube / 26 OD [PROPOSED] / r15 solid; unreconciled. Auditor hand check, not signed: solid r15, L ~ 389 mm (tip/foot coordinates in engineering_checks.json), P_cr ~ 4.7 kN vs 104 N axial: ample. Spec question is mass and look, not strength |
| Cycle-1 follow-ups | owner, method, structural commit, notes rendering, round-05: closed. tools/ in CLAUDE.md map, tally script for verdicts, Haiku/Fable deviation docs: open |

## Recenter

Threshold fires: **CAD R1 Y + R4 Y**. RP-2 filed in teams/audit/STATUS.md. No item touches the vision. 0 RED.

## Not verifiable

- Evan's direct-chat verdicts (hybrid method, vocabulary approval, RP-1 adoption, structural design case, smiley re-center): chat not auditable.
- Provenance of the Gate-1 "reviewer verdict: cooked dough, not calcified fibre" (gate1b README line 3): no board, issue, or DECISIONS row; assumed Evan chat or self-review.
- Visual self-assessments vs c01/c02 in gate READMEs: I did not independently judge renders. Evan's r05 dislike of s1 (gap to c01) corroborates the fullpiece one.
- Full-piece headroom counts and relief stats (no source).
- Email pings. Whether anyone other than one orchestrator session and one reviewer persona acted (ephemeral).
- Whether Evan saw the headroom violation outside the board.
- Fullpiece_v2 and round-06 (in flight, per instruction).
