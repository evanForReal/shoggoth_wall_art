# Orchestrator session log — 2026-11-16

**Purpose (Evan directive, 2026-11-16):** record the Orchestrator's own design and process choices — the ones that are NOT Evan verdicts — so they can be audited later by a different model. Evan's verdicts live in docs/DECISIONS.md; this file holds the judgment calls made between them.

**Append-only.** New entries go at the bottom. Corrections are new entries that reference the old ID.

**Basis tags:** `[Evan]` = directly implements an Evan verdict/directive · `[inference]` = Orchestrator reading of Evan's votes/notes beyond what he said · `[judgment]` = Orchestrator choice with no Evan input · `[error]` = a choice later shown wrong.

**Entry format:** ID · time (UTC, approx for backfill) · choice · basis · why · alternatives rejected · reversibility.

---

## Backfill (choices made earlier today, before this log existed)

**SL-01** · ~16:00 · Boarded round-05 from fullpiece v1 as-is instead of iterating the body first. · `[judgment]`
Why: the CAD self-assessment said the body was not yet c01-grade, but the four open axes (mask, maw, layout, shelves) decide *which* body gets refined; iterating first risked compute on a rejected direction. Alternative rejected: one more CAD pass before boarding. Outcome: 10/13 disliked, but the round produced the smiley+maw re-center directive. Reversible: n/a (shipped).

**SL-02** · ~16:00 · Round-05 manifest notes summarised engineering gaps as "composition proxies" and did NOT list the shelf-headroom violation (S3 ~160 mm clear vs 300 mm locked), 16 mm seat depth, or 22 kg mass. · `[error]`
Why it happened: notes were written for the aesthetic vote and the engineering misses were judged print-res issues. Why it is wrong: Evan then praised "great shelves and placement" (h1) without knowing S3 fails headroom, and SL-04 below locked that placement on the strength of the praise. Caught by audit cycle 2 (RP-2 item 1). Correction: SL-08.

**SL-03** · ~16:15 · Backprop inferred locks from bare dislikes: "radial layout stands" (from v3 diagonal dislike), "shelves A stands" (from v4 dislike + h1 praise). · `[inference]`
Why: one-axis variants make a bare dislike of the variant a reasonable vote for the hero's value on that axis. Weakness: 10/13 cards were disliked, so a dislike may be about the shared body, not the axis. Flagged by docs-reviewer and audit. Reversible: yes — any round-06 vote overrides.

**SL-04** · ~16:15 · Interpreted "return towards the classic smiley emoticon" + h3/v1a notes as: exact canonical emoticon geometry (circle, two vertical-oval eyes, upward arc), executed monumental and eroded (r04 Bayon m01 gravity), pale bone, carved in. · `[inference]`
Why: h3 asks for the emoticon; v1a rejects the flat cartoon disc as "comical, childish, highly imperfect". Reading: the *motif* is wanted, the *execution* was wrong. Alternative rejected: a stylised/abstracted smile (would drift from "classic emoticon"). Reversible: yes, round-06 mask cards test it.

**SL-05** · ~16:15 · Fullpiece-v2 brief parameters set by Orchestrator, not Evan: 15-40 surface eyes, ≥8 mm features (2 mm voxel survival); masquerade = exactly ONE subtle device (lifting edge / gripping tendrils / glimpse through an eye); buttress rebuilt as a muscular limb with ≥26 mm structural core; texture density varies with anatomy; variant axes delegated to CAD from a suggested list (masquerade device, eye density, maw/tooth character, weathering). · `[judgment]`
Why: Evan named the motifs, not their quantities. 26 mm core taken from mesh-spec-v1, which is itself unsigned — see SL-10. Reversible: yes, all parameters in gen script.

**SL-06** · ~16:20 · Ran audit cycle 2 concurrently with the fullpiece-v2 build rather than after it. · `[judgment]`
Why: charter cadence is one audit per round; round-05 closed. Cost: audit could not see v2. Reversible: n/a.

## Live entries

**SL-07** · 16:45 · Orchestrator model switched by Evan (/model) mid-session. All entries from SL-07 on were made after the switch; SL-01..SL-06 were backfilled after the switch from the record of the earlier part of the session. · `[Evan]`

**SL-08** · 16:45 · Audit cycle-2 claims spot-verified before acting: (a) Gate 2 `validation_sculpt.json` — "incl" void area <6 mm 0.222→0.330, "interior" ridge P5 1.16→0.75 mm, interior ridge thin fraction 0.075→0.136: the "no net thinning" STATUS line is selective, CONFIRMED; (b) `git show 3e58215` rewrote the Step-2 geometry ownership row body in place, CONFIRMED; (c) headroom omission, CONFIRMED (SL-02, my manifest). · `[judgment]`

**SL-09** · 16:45 · RP-2 vote: Orchestrator casts 3 votes FOR, all 8 items. CAD, Structural, Fabrication leads asked to vote as they execute their items (majority = 4 of 7). Aesthetics-lead vote NOT cast separately: in practice the Orchestrator has been signing as aesthetics-lead (teams/aesthetics/STATUS.md liaison line), so casting it would double-count one actor. · `[judgment]`
Why for: every finding verified (SL-08); none touches the vision; items are disclosure and process fixes. Reversible: council or Evan can reverse.

**SL-10** · 16:45 · Correction to SL-03/SL-04 dependency: "shelves A + placement" is now treated as a layout lock CONDITIONAL on restoring 300 mm headroom (restagger under-shelf fans; shelf heights may shift). Round-06 manifest notes must state S3's v1 clearance and v2's measured clearance per shelf. · `[judgment]` (corrects SL-02)

**SL-11** · 16:45 · Sign-off protocol amended (RP-2 item 5, Orchestrator decision per charter): reviewer cell names what it verified; open flags stay open (cell reads "FLAG OPEN: …" not signed-through); body [PROVISIONAL] tags cleared in the same commit as the sign-off; board notes state any unsigned source a card depends on. · `[judgment]`
Alternative rejected: blocking boards on any unsigned source — too slow under the 5-hour worker rate limits; disclosure on the board gets Evan the same information.

**SL-12** · 16:45 · DECISIONS row-order rule: newest rows insert directly under the header (newest-first), matching today's insertions. Existing out-of-order rows are NOT moved (append-only). · `[judgment]`

**SL-13** · 16:45 · Verdict snapshots go to `review/verdicts/round-NN.json`, not into `review/rounds/round-NN/` (that tree is DO-NOT-EDIT after deploy). Makes recounts reproducible offline; the tally script checks them. · `[judgment]`

**SL-14** · 16:45 · Fabrication's segment/mass refresh against the real mesh is deferred until fullpiece-v2 exists (v1 body is superseded by the re-center); Fabrication's fab-side read of the 6 mm blind-pocket relaxation runs now, in parallel with Structural. · `[judgment]`

**SL-15** · 16:55 · Aesthetics STATUS trimmed 81→45 content lines to meet its own 60-line cap: r01-r04 takeaways folded to one line each (full text stays in DECISIONS rows), superseded r05 charter paragraph dropped (in git history at ca9747f), "Locked" line rewritten for r05 (removed "serene monumental" mask option, added "emoticon form"). · `[judgment]`
Risk: lossy for anyone reading STATUS alone; DECISIONS remains the full record. Reversible: `git show ca9747f:teams/aesthetics/STATUS.md`.

**SL-16** · 16:55 · Committed the RP-2 orchestrator edits (AGENTS protocol, DECISIONS disclosure + order rule, CLAUDE map, aesthetics trim, this log) as [PROVISIONAL] before sign-off, so they survive a container reclaim; sign-off batched with the Structural/Fabrication/docs-worker returns. · `[judgment]`

**SL-17** · 17:05 · Added `teams/cad/.gitignore` (stl/ply/obj/npy/npz/blend/pycache) covering every CAD package. Cause: fullpiece_v2/ had no ignore rule; per-gate ignores existed only in gate1..gate2. A 1.4 M-tri STL is ~70 MB. Per-gate ignores left in place (redundant, harmless). · `[judgment]`

**SL-18** · 17:05 · Verdict snapshots + extended tally script committed (4dd6f70) after re-running the script myself (5/5 PASS, exit 0). The worker hand-transcribed the issue JSON; counts and ids are machine-checked against manifests and DECISIONS, note text only eyeballed. · `[judgment]`

**SL-19** · ~17:20 · RP-2 CARRIES: Orchestrator 3 + Fabrication Lead 1 = 4 of 7 (majority). CAD and Structural votes still requested for the record; they cannot change the outcome. · `[judgment]`

**SL-20** · ~17:20 · Fabrication's v2 fab-risk list split by me into FORM-level (forwarded to the running CAD worker now: eyes >= 12 mm, front-facing only, chamfered lids; teeth base >= 4 mm / tip r >= 0.75 mm / height <= 3x base; throat as plugged recess; D-section tentacles; smile V-groove >= 90 deg) vs PRINT-RES (overhang limiter, per-feature IDs, orientation per segment, pocket table, coupon plate — deferred to the print-res pass). · `[judgment]`
Why now: form changes are cheap before renders and expensive after Evan votes on a shape that can't print. Cost: eyes restricted to front faces narrows the "eye-covered" look on tentacle flanks — accepted; flat dimples allowed there. Alternative rejected: wait and fold in at print res (risks Evan approving an unprintable eye/tooth language). Changed my SL-05 eye size floor 10 → 12 mm.

**SL-21** · ~17:20 · 6 mm blind-pocket relaxation: Fabrication CONDITIONAL (C1-C6: mouth faces within 45 deg of print-up, no undercut, mouth >= 2 mm, depth <= 3x mouth, floor >= 2.6 mm). Not adopted yet — waits on Structural's independent verdict. Fab's limits are [GENERAL] FDM practice, unmeasured; Evan's printer is still unknown. · `[judgment]`

**SL-22** · ~17:35 · Blind-pocket relaxation ADOPTED as the UNION of Structural's and Fabrication's conditions (stricter value wins: floor 2.6 mm from Fab over Structural's 2.0). Logged as an RP-2 outcome row in DECISIONS, explicitly marked "not an Evan verdict". · `[judgment]`
Why in DECISIONS: AUDIT.md step 4 requires adopted proposals to be appended there; RP-1 set the precedent.

**SL-23** · ~17:35 · Forwarded Structural's numbers to the running CAD worker as hard build targets: buttress core 22 solid / 24x3 tube, foot pad >= 75x60 mm, shelf-arm root solid core >= 40 mm to 0.5 p, no-pocket/no-eye load zones, keep solid-mass proxy <= 22 kg. Left the 26 mm-vs-22 mm core choice to CAD (26 solid passes). · `[judgment]`
Consequence for the look: 40 mm arm roots make the shelf limbs visibly thicker — this pushes TOWARD Evan's "muscular tentacle" ask, so no conflict expected. No-eye zones around arm roots and pads reduce eye coverage near shelves.

**SL-24** · ~17:35 · Did not act on Structural's suggested mesh-spec rewording ("buttress required only for p > 250 mm or drywall-only"). Shelf arrangement A's p=290 shelf still gets the buttress; Evan approved the buttress tentacle, and making it optional is a design change he should see, not a spec edit. · `[judgment]`

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-16 | orchestrator | Created; backfill SL-01..06; live SL-07..14 | [PROVISIONAL] |
