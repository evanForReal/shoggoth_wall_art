# Audit Team — STATUS.md

**Status:** ACTIVE — cycle 3 complete (2026-11-17). RP-2 adopted (5 of 8 items held, 3 partial). RP-3 (CAD R1 RED + Orchestration R1/R4) filed, CARRIED 4 of 7 (2026-11-17); items 1 and 4 escalate to Evan.

## Exec Summary (newest first)

- 2026-11-17: Cycle 3 done. Verdict: the method as practiced (body = union of fixed ellipses + independent features, no figure/skeleton/gesture) cannot reach c01 composition; the SDF/2.5D kernel is not the blocker. r05 1/2/10 and r06 0/1/11 are one failure (composition; side profile is the only thing that works). Orchestrator's composition-first decision (SL-39): agree, amend 4 points. 1 RED (CAD R1), 13 YELLOW. Recenter fires on CAD and on Orchestration/process (R1 Y + R4 Y). RP-3 filed. RP-2: 5 held, 3 partial (Structural/Fab did not review v2 before board; banner buries the question). Log is working; 3 unlogged choices (mass target 22 to 25 kg, lock release, v2 review skipped). Separation of duties: acceptable once, now a pattern; SL-32c crossed the line. Full report: artifacts/audit/2026-11-17-exec-summary.md.
- 2026-11-16: Cycle 2 done. Verdict: RP-1 held (owner, method, five CAD gates, fullpiece, round-05, board notes all real). r05 backprop verified exact from issue #5: 1 love / 2 like / 10 dislike of 13. 11 YELLOW, 0 RED. Recenter fires on CAD (R1 Y + R4 Y): hero violates the 300 mm plant-headroom constraint and the board did not say so; several README numbers have no committed source; Gate 2 "no net thinning" is selective. Structural and Fabrication idle ~22 h while CAD ran ahead. Sign-offs honored in form, thin in substance (batch-flipped ae60df5). RP-2 filed. Full report: artifacts/audit/2026-11-16-exec-summary.md.
- 2026-11-15: Cycle 1 done. Verdict: aesthetics record verified and accurate (issues #1-#4 recounted, tallies match). Downstream pipeline has no on-ramp (step-2 geometry unowned; structural/CAD/fab idle; round-05 does not exist yet). 9 YELLOW, 0 RED. Full report: artifacts/audit/2026-11-15-exec-summary.md.
- 2026-11-15: Team chartered (docs/AUDIT.md, Evan directive). Audit cycle 1 launched: full-project rubric pass + first exec summary.

## Current State

Audit cycle 1 scope: aesthetics (rounds 1–4 + round-05 charter), structural (liaison v1/v2 + new engineering pass), cad (stub), fabrication (stub), orchestration/process (sign-off integrity, DECISIONS hygiene, review-app/codebase readability).

## Recenter Proposals

**RP-1 (2026-11-15, Audit Lead). Trigger: 2+ YELLOW (9 across aesthetics R2/R4, structural R1/R2/R4/R5, process R2/R4/R5). No RED. Does not touch the vision; council vote applies, no Evan escalation required (item 5 asks Evan one board question).**

Drift: the aesthetic phase is converging; the rest of the pipeline is idle with no owner for geometry. Evidence: docs/AGENTS.md charters (no role produces 3D geometry); teams/structural/STATUS.md (stub header vs liaison v2, ee57a70; no committed structural output); review/rounds/round-04 c01/c02 (loved, feasibility unchecked); teams/aesthetics/STATUS.md (round-05 "in progress", no artifact).

Proposed reprioritization:
1. **Assign step-2 geometry owner** (CAD Lead or new role). Decide method: generative 3D, sculpt, or procedural. Orchestrator applies; log in DECISIONS.
2. **Structural pass: commit and sign what exists** (uncommitted teams/structural/analysis/*.svg, first cantilever/anchor pass seen mid-audit; update STATUS). Add FDM load-direction and creep limits, mass and print-time order of magnitude for ~3x3 ft, feasibility read on c01/c02 (perforated webbing). State assumptions behind 5 kg. Generate 2/4/5-tentacle alternates per init_vision.
3. **CAD/Fab enabling work**: toolchain, mesh and tolerance spec, hardware library; segment-count estimate. No geometry dependency.
4. **Hygiene (one commit, peer-signed)**: aesthetics STATUS exec summary + r02-r04 takeaways + rejected list; structural STATUS header; CLAUDE.md repo map; DECISIONS edit-log row for the ee57a70 correction; document the Haiku sign-off deviation and its cause; commit tally script and r04 generation prompts; snapshot or hash hotlinked card images.
5. **Board**: render manifest `notes` in review-app (Infra; needs Evan OK to edit). Add a seam-tolerance/material/finish probe card to round-05/06.
6. **Round-05**: relabel STATUS "chartered, blocked on credits"; name a fallback generator; log in DECISIONS whether all-generated/no-outlier format is approved by Evan.

Note to council: the "2+ YELLOW overall" threshold is met by almost any 5-criterion scorecard. Recommend recalibrating in AUDIT.md (e.g., any RED, or 2+ YELLOW on R1/R4 in one area). Charter change; Orchestrator decides.

Vote: superseded — adopted by Evan directly ("let rp1's items continue", 2026-11-15); executed same day. Item 6 fallback generator: none exists in-environment; logged in aesthetics STATUS as a single-point dependency.

**RP-2 (2026-11-16, Audit Lead). Trigger: CAD R1 Y + R4 Y (2 YELLOW on R1/R4 in one area). No RED. Does not touch the vision; council vote applies.**

Drift: CAD builds fast and self-assesses honestly in READMEs, but (a) discloses less to Evan than it knows, (b) cites numbers with no committed source, (c) leans on a rule relaxation nobody signed, and (d) Structural and Fabrication are not in the loop. Evidence:
- Headroom: fullpiece/README s.4 item 2 (S3 ~160 mm vs 300 mm; DECISIONS 2026-11-14 sketch row; mesh-spec-v1 line 81); review/rounds/round-05/manifest.json notes and card rationales do not mention it; issue #5 h1 "great shelves and placement"; DECISIONS r05 row locks "shelf arrangement A + placement".
- Unsourced numbers: fullpiece/README s.2 relief stats and s.4 headroom counts appear in no engineering_checks.json or generator output (reviewer flag in teams/cad/STATUS.md edit log, signed anyway).
- Selective claim: teams/cad/STATUS.md Gate 2 line "no net min-wall thinning" vs gate2/validation_sculpt.json (void share < 6 mm 22% to 33%; interior-only ridge P5 1.16 to 0.75 mm; ridge fraction below thin 7.5% to 13.6%).
- Unsigned dependency: 6 mm blind-pocket relaxation (CAD STATUS Liaison, 2026-11-16) underpins Gate 1C/2 void results; no Structural or Fabrication sign-off.
- Strut: load-model-v1 20 x 1.2 mm tube vs mesh-spec-v1 26 mm OD [PROPOSED] vs fullpiece r15 solid; Structural untouched since 3e58215.

Proposed reprioritization:
1. **Disclose**: round-06 manifest notes must list every NOT-honored constraint from the CAD README (headroom first), short enough to sit above the banner fold. Orchestrator.
2. **Source every README number**: fullpiece_v2 `engineering_checks.json` gains headroom intrusion counts and relief stats (mean, P10/P50/P90, max); README numbers without a JSON key get cut. CAD Lead.
3. **Structural re-engage**: sign or reject (a) blind-pocket void relaxation, (b) one strut spec (OD, wall, I) and who owns it, (c) limb min I; review fullpiece_v2 mass and hard-points before the round-06 board ships. Fabrication counter-signs (a) and refreshes the segment/mass plan against the real mesh. Both STATUS files updated.
4. **Gate 2 claim**: restate "no net thinning" with the metrics that worsened, or drop it. CAD Lead + reviewer.
5. **Sign-off protocol** (charter-adjacent; Orchestrator decides): clear [PROVISIONAL] tags in file bodies when the edit-log cell is signed; reviewer records which claim(s) it verified per row; open flags are listed as open, not signed through; no dependent build shipped to Evan on unsigned sources, or ship with the unsigned status stated on the board.
6. **DECISIONS hygiene**: disclosure row for the 3e58215 in-place edit of the Step-2 geometry ownership row; fix a row-order rule (append at one end only).
7. **Alt tentacle counts (2/4/5)**: still untested since init_vision. Put one card in round-06 or log Evan's waiver.
8. Carry-overs from cycle 1: tools/ in CLAUDE.md map; tally script that actually checks verdicts; deviation-log entry for Fable 5 trailers vs the Sonnet policy.

Vote: ADOPTED 6 of 7 — Orchestrator 3 FOR (session log SL-09); Fabrication 1 FOR (teams/fabrication/analysis/rp2-blind-pockets.md s.7); Structural 1 FOR and CAD 1 FOR (both given in the leads' hand-back reports to the Orchestrator, not written into their own files; relayed here by the Orchestrator 2026-11-17); aesthetics-lead not cast (same actor as Orchestrator, docs/AGENTS.md deviation log). Outcome row: docs/DECISIONS.md 2026-11-16 RP-2 adoption + 2026-11-17 vote-record row.

**RP-3 (2026-11-17, Audit Lead). Trigger: CAD R1 RED; Orchestration/process R1 Y + R4 Y. Items 1 and 4 touch the vision (composition target, release of inferred locks): escalate to Evan via the round-07 board. Remaining items: council vote.**

Drift: two rounds (r05 1/2/10, r06 0/1/11) failed the named target on composition. Evidence: fullpiece_v2_1/gen_fullpiece.py L25-34 (BODY, BELLIES, mass_ells) and L148-176 (whip `specs`, fixed centre): body is a union of features, no figure; review/verdicts/round-06.json h1, vb2, vc2; fullpiece_v2_1/README.md s.5 (self-grade C on sprawl, "not c01"); session log SL-34 vs SL-35 (board a hero read as nowhere near c01); 1015353 (locks dropped from aesthetics STATUS, no row).

Proposed reprioritization:
1. **Bind SL-39.** Composition stage authored as a FIGURE (head, torso, N limbs with gesture curves; shelves at limb tips), not a feature set. Evan-approved silhouette + skeleton is a hard input to the 3D generator; build check = silhouette IoU vs approved mask (start >= 0.85, [GENERAL], aesthetics lead may reset). Source of silhouettes: 2D concepts (generated or drawn) or procedural 2D; not CAD's current generator. Owner: Aesthetics lead; CAD consumes.
2. **c01-trace capability test** before any new 3D: trace c01 silhouette + limb centrelines, feed as mass input to the existing generator, render the same view. Pass = kernel fine, authoring is the issue. Fail = also change the relief/kernel (Option B/D). One worker, hours. Owner: CAD lead.
3. **Objective composition gate.** DESIGN_PRINCIPLES defines 4-5 numbers from a c01 trace (fill ratio, negative-space ratio, torso width fraction, limb reach / torso, limb count, head-vs-background value contrast). Computed by a non-CAD agent on every silhouette and hero render. Do not board a hero whose self-grade is C or worse on a verdict-named axis unless the card is that question.
4. **Lock hygiene (Evan).** DECISIONS row: shelf arrangement A placement, radial layout, local-texture-stands are released or re-conditioned; depth profile (h4 x2), smiley + maw motif, Gate-2 vocabulary, 300 mm headroom stand. Mark which locks were inferred. Put on the round-07 board.
5. **Board mechanics.** Decision-critical question first (card, or notes <= ~200 chars above the 5.6 em fold). Banner CSS change needs Evan OK.
6. **Cross-team edit rule.** Orchestrator may correct wording (no new numbers) in another team's file with an edit-log row "orchestrator on behalf of <team>", confirmed by the owner at next spawn. New analysis, scripts, votes: owner writes. Add pre-deploy carve-out sentence to CLAUDE.md for review/rounds. Sign the open [PROVISIONAL] edit-log rows (~10: session log 2, DECISIONS 2, aesthetics 2, audit 3 incl. mine, fab 1; plus RP-2 body tag in audit STATUS) within round-07.
7. **Log the three missing choices** (mass target 22 to 25 kg with Structural concurrence; lock release; skipped Structural/Fab review of v2) and a correction entry for SL-35's envelope premise. Structural review + Fabrication refresh move to the first mesh built from an approved skeleton (v3), stated as waived for v2/v2.1. Waive 2/4/5 tentacle alternates formally until a composition exists, or ask Evan once.
8. **Stop rule.** If two composition rounds do not raise the like rate, the problem is the brief: escalate to Evan for a sketch or pick-from-spread session; consider Option F (human sculpt of body).

Vote (recorded 2026-11-17): **CARRIED, 4 of 7.** Per-vote sources: Orchestrator 3 FOR all 8 items, with amendments (artifacts/session-log/2026-11-16-orchestrator.md SL-44); CAD Lead 1 FOR, with caveats (teams/cad/STATUS.md Current State, line "RP-3 vote (CAD Lead, 2026-11-17)", written by the CAD Lead). Structural and Fabrication not polled. Aesthetics lead not cast (Orchestrator acts as lead; AGENTS deviation log 2026-11-16). SL-44 amendments: item 2 (c01-trace test) is satisfied first by the gated G1 study; item 6 uses a review/staging/ folder instead of a DO-NOT-EDIT carve-out in CLAUDE.md (implemented in AGENTS.md Staging). Item 1 decision (Aesthetics Lead, docs/DESIGN_PRINCIPLES.md s.4.1): IoU build gate starts at 0.60, not 0.85 (CAD caveat adopted; ratchet 0.70, then 0.85 for the final CAD model).

## Takeaways

- Verify verdicts from the issue API, not STATUS prose; recount is cheap (script it).
- Aesthetics claims were accurate in every spot-check; stale prose, not false prose, is the failure mode.
- Edit logs show 3 actors only (docs-lead, orchestrator, docs-reviewer). Treat the lead/worker hierarchy as unevidenced until a lead leaves a trace.
- Board does not render manifest `notes`; shortfalls are invisible to Evan.
- Next audit: re-check RP-1 outcomes, round-05 existence, structural artifacts. (Done cycle 2.)
- Cycle 2: a README is a claim, not evidence. Check every number against a committed JSON; 3 of ~20 spot-checked CAD numbers had no source and one was selective.
- A constraint violated in the geometry must appear on the board. Disclosure to Evan is a CAD deliverable, not a README courtesy.
- Dislike of an alternative is not endorsement of the baseline when 10 of 13 cards are disliked. Mark inferred locks as inferred.
- The 2026-11-16 sign-off burst: real flags on 3 of 7 rows, clean on 4, one miss found by me (Gate 2). Batch sign-off after dependent work shipped is ritual; fix per RP-2 item 5.
- Silent teams are a signal: Structural and Fabrication unchanged ~22 h while the mesh they were "awaiting" appeared.
- Next audit (cycle 3, at round-06): fullpiece_v2 vs RP-2 items; Structural/Fabrication sign-offs; r06 backprop recount from issue #6; whether [PROVISIONAL] tags clear with sign-off.
- Cycle 3: when two rounds fail on the same axis the cause is the method, not the pass. Check what the code can express: v1-v2.1 had no parameter for gesture, silhouette or hierarchy, so verdicts on those could not be acted on.
- A self-grade of C on a verdict-named axis is a stop sign for boarding. SL-34 and README s.5 predicted r06 exactly.
- Evan loved the side profile in both rounds; 2.5D depth is the pipeline's strength. Keep it as the depth lock while composition is rebuilt.
- Disclosure placement matters as much as content: a 1,428-char note in a 4-line scroll banner buries the one question Evan needed to answer.
- The Orchestrator log works (tags, owned errors, reads written before CAD's). Check it against git for choices that never got an entry: mass target, lock release, skipped review.
- Orchestrator fixing other teams' flags is fine for wording, not for evidence or votes.
- Next audit (cycle 4, at round-07): silhouette board vs DESIGN_PRINCIPLES metrics; c01-trace test result; whether the approved silhouette bound the 3D build; RP-3 outcomes; lock release row; [PROVISIONAL] backlog.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-15 | orchestrator | Initial creation | docs-reviewer |
| 2026-11-15 | audit-lead | Cycle 1: exec summary, RP-1 recenter proposal, takeaways | docs-reviewer |
| 2026-11-16 | audit-lead | Cycle 2: exec line, RP-2 recenter proposal (CAD), takeaways; artifacts/audit/2026-11-16-exec-summary.md | docs-reviewer (verified, spot-check: exec line vs artifacts/audit/2026-11-16-exec-summary.md (cycle 2 = 11 Y, 0 R; Structural ~22 h idle; summary file exists); r05 1/2/10 = tools/verify_tallies.py PASS; ae60df5 exists; RP-2 Gate-2 worsened metrics match CAD STATUS (void < 6 mm 0.222 to 0.330; interior ridge P5 1.16 to 0.75 mm; ridge fraction 0.075 to 0.136); RP-2 Vote line sources match SL-09, rp2-blind-pockets.md s.7 and the DECISIONS vote-record row; RP-2 body [PROVISIONAL] tag cleared. Cosmetic, signed through: RP-2 headroom bullet quotes the fullpiece README "S3 ~160 mm" as audit-time evidence; the true v1 figure is ~12 mm (SL-29, aesthetics STATUS correction); history not rewritten) |
| 2026-11-17 | orchestrator | RP-2 Vote line: recorded 6 of 7 with a source per vote (Structural/CAD relayed from hand-backs) | docs-reviewer (verified: 6 of 7 with a source per vote; Orchestrator 3 = SL-09; Fabrication = rp2-blind-pockets.md s.7 FOR; Structural and CAD are labelled in the line as relayed by the Orchestrator from hand-back reports (disclosed, not presented as the leads' own entries); aesthetics-lead not cast matches the AGENTS deviation log; outcome rows exist (DECISIONS 2026-11-16 adoption, 2026-11-17 vote-record). Residual, disclosed: the two relayed votes have no trace in the leads' own files; review cannot resolve that) |
| 2026-11-17 | audit-lead | Cycle 3: exec line, RP-3 recenter proposal, takeaways; artifacts/audit/2026-11-17-exec-summary.md | FLAG OPEN: (1) "1 R, 12 Y" (STATUS exec line and exec summary line 29) vs the summary's own matrix (artifacts/audit/2026-11-17-exec-summary.md lines 20-26): Aesthetics 2 Y, Structural 3, CAD 2, Fabrication 2, Orchestration 4 = 13 Y plus 1 R. Fix the count or the matrix. (2) RP-3 block ends "Vote: pending" while SL-47 records RP-3 carried 4 of 7; update once the CAD vote has a durable source (see SL-47 flag). Verified OK: RP-2 5 held / 3 partial = summary table; CAD R1 RED; r05 1/2/10 and r06 0/1/11 = verify_tallies; gen_fullpiece.py L25-34 (BODY, BELLIES, mass_ells) and L148-176 (whip specs, fixed centre c0, start 95-140 mm) match the RP-3 drift text; 1015353 dropped the "Kept from r05" locks with no DECISIONS row; r06 manifest notes are 1,428 chars; fullpiece_v2_1/README s.5 grade C on sprawl and "not c01" present; SL-34/SL-35 exist; RP-3 item 6 text = AGENTS (see AGENTS flag). RP-3 body [PROVISIONAL] tag stays; resolved by the row below, re-verified at HEAD by docs-reviewer-2: (1) matrix in artifacts/audit/2026-11-17-exec-summary.md lines 20-26 counts Aesthetics 2, Structural 3, CAD 2 Y + 1 R, Fabrication 2, Orchestration 4 = 13 Y + 1 R; exec summary line 29 and STATUS exec line 7 both say 1 R, 13 Y; no "12 Y" remains in either file; (2) RP-3 Vote line now reads CARRIED 4 of 7 with a source per vote (see row below) |
| 2026-11-17 | audit-lead | Resolves FLAG OPEN above: Y count; RP-3 vote recorded with sources | docs-reviewer-2 (verified: matrix lines 20-26 = 13 Y + 1 R, exec summary line 29 and STATUS exec line 7 agree; RP-3 Vote line says CARRIED 4 of 7 = Orchestrator 3 + CAD Lead 1; Orchestrator 3 FOR all 8 items with amendments to item 2 (G1 study first) and item 6 (review/staging/ folder) = SL-44 in artifacts/session-log/2026-11-16-orchestrator.md; CAD Lead FOR with caveats = teams/cad/STATUS.md Current State L28 'RP-3 vote (CAD Lead, 2026-11-17)', in CAD's own file, caveats match (0.85 unreachable, G1a 0.60; propose 0.60); IoU start 0.60, ratchet 0.70 then 0.85 = docs/DESIGN_PRINCIPLES.md s.4.1; aesthetics-lead not cast = AGENTS deviation log 2026-11-16; `git diff 2d15de0 HEAD -- teams/audit/STATUS.md` deletes only the superseded exec-line count, status header clause and 'Vote: pending' line, no earlier content lost; RP-3 body [PROVISIONAL] tag cleared with this sign-off. Not assessed: soundness of the votes) |
