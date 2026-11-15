# Audit Cycle 1 — Exec Summary (2026-11-15)

Auditor: Audit Lead. Scope: full project, 15 commits (9126891..16a8dec), 4 review rounds, 4 GitHub issues. Rubric: docs/AUDIT.md v1.

## TL;DR

**Aesthetics record is real and accurate. Everything downstream of it has no on-ramp yet. Fix that before round 05.**

- Trust: verdict log. I re-pulled issues #1-#4 via `gh api` and recounted. Tallies match manifests and DECISIONS exactly (r01 4/3/5 of 12; r02 0/3/4 of 7; r03 15/13/20 of 48; r04 6/18/19 of 43). Card ids match 1:1. Every DECISIONS r04 card cite I spot-checked is correct.
- Trust: shortfalls (r02 7/12, r04 43/48, preview-res, inline mask trawl) are logged honestly in manifest notes with causes.
- Distrust: "team" claims. Every edit-log row names `docs-lead` (day-1 creation), `orchestrator`, or `docs-reviewer`. No lead or worker leaves a durable trace. The hierarchy is nominal: one orchestrator plus one reviewer persona, which signs as "structural-lead" on the liaison.
- Distrust: "Round-05 in progress" (aesthetics STATUS). No round-05 directory, manifest, or commit exists. It is a charter, blocked on Canva credits.
- Worst finding: pipeline step 2 (3D geometry) has no owner. AGENTS.md: CAD "converts approved geometry"; Structural engineers loads; Aesthetics makes images. Nobody turns a 2D concept into a 3D model. Four rounds in, no one has checked whether the loved concepts (c01/c02: perforated webbing, 3 ft span, 2-5 kg plant loads per span) are printable or sound at all.
- Recentering threshold (2+ YELLOW) is met. Proposal filed in teams/audit/STATUS.md. It does not touch the vision.

## Scorecard

G = green, Y = yellow, R = red. Evidence is cited per cell below the table.

| Area | R1 Vision | R2 Readable | R3 Modular | R4 Evidence | R5 Process |
|---|---|---|---|---|---|
| Aesthetics | G | Y | G | Y | G |
| Structural | Y | Y | G | Y | Y |
| CAD | G | G | n/a | G | G |
| Fabrication | G | G | n/a | G | G |
| Orchestration / process | G | Y | G | Y | Y |

Evidence:

- **Aes R1 G.** Every lock traces to DECISIONS rows (r03 s01-s06, f02/f04, d03; r04 m01, p07, v03, v08, c03/c05 notes). I re-counted the card-level claims in the r03 and r04 rows against issues #3/#4: all correct. Caveats (not drift): "mask never applied" and "tentacle-grips-pot" are orchestrator inferences from votes (m02-m06 disliked, p07 loved), not Evan statements; c01, which Evan loved, shows a disc mask. r03 had zero notes, so its locks are inferred from votes alone.
- **Aes R2 Y.** teams/aesthetics/STATUS.md Exec Summary newest entry is 2026-11-14 "Round-02 trawl initiated". Rounds 2-4 are absent from it. Takeaways hold round-01 only; r02-r04 knowledge lives in Current State and DECISIONS. Evan's requested "rejected things" component is missing; "aesthetics vision/samples for human review/takeaways.md" is 0 bytes.
- **Aes R3 G.** One manifest per round; four-group structure from the 2026-11-14 restructure row; rounds 1-4 needed one app edit (cf89445).
- **Aes R4 Y.** Boards, images, and issues verified. Gaps: "prompt on file" (r04 c01-c07 source field) is not in the repo; 84 of 91 r03/r04 cards are hotlinked (55 Wikimedia), so the record of what Evan voted on rots; round-05 "in progress" has no artifact.
- **Aes R5 G.** Backprop latency: r01 3h (01:06Z to 04:11Z), r03 29m, r04 4m. Reviewer flags are real (ee57a70 era: "outliers per group are 4-6, not 4-7"). The wrong r02/r03 tallies (signed by haiku in 6f42067) were caught and superseded by an append-only correction row 19 minutes later (ee57a70).
- **Struct R1 Y.** Evan's init_vision asks for alternate tentacle counts (2, 4, 5) "run past me"; structural STATUS repeats it; no card in rounds 1-4 tests it. "Tension-cable assist acceptable (f11 liked)" over-reads one liked generic tensegrity photo.
- **Struct R2 Y.** Header reads "STUB, awaiting Aesthetics round-01 output"; liaison v2 landed in ee57a70 and the status was never updated. Takeaways: none.
- **Struct R3 G.** Functional Constraints are separated from implementation; no printer-specific features.
- **Struct R4 Y.** Liaison v2 "est. 2-5 kg per span" had no calculation or source in any commit. Mid-audit (13:57 today) two uncommitted SVGs appeared in teams/structural/analysis/ (side-profile-cantilever.svg, front-anchor-map.svg): 5 kg shelf load, 30 cm protrusion, M = 11.0 N.m nominal / 23.6 N.m bound, 8 anchors. Arithmetic spot-check OK (5 x 9.81 x 1.5 = 73.6 N; 73.6 x 0.15 = 11.0). Not committed, not in STATUS, not signed, no assumptions doc. Counted as in-flight, not as delivered.
- **Struct R5 Y.** Liaison v2 signed "aesthetics-lead (orchestrator)" and "structural-lead (docs-reviewer/haiku)". No structural lead acted.
- **CAD/Fab.** Stubs say "no work started"; git agrees (only 9126891 and creation rows). Honest. R3 not scorable.
- **Orch R1 G.** Swipe board, issue verdicts, escalation path all match Evan's init prompt.
- **Orch R2 Y.** CLAUDE.md repo map lists `artifacts/` and `knobs that we can tweak/` (latter does not exist) and omits teams/audit and AUDIT.md. AGENTS.md lists an Infra Lead with no teams/infra/STATUS.md. AGENTS says orchestrator is Sonnet; commit trailers say Fable 5. DECISIONS rows are not in chronological order (seed, restructure, r03, r02, sketch, r04, correction, r01 last).
- **Orch R3 G (with defects).** Review-app (review-app/index.html, 539 lines) is genuinely manifest-driven: `?round=` selects the manifest, cards render from it, no per-round code. Defects: no manifest schema or doc; default round hard-coded `round-01` (line 166/182); no rounds index; manifest `notes` is never rendered (grep: only `title`, `cards`, `round`, `issue_repo` are read), so shortfall disclosures never reach the board; single file, inline CSS/JS (fine at this size); unescaped `imgUrl` in `src` (trusted input today).
- **Orch R4 Y.** Pages deploy and email pings are asserted, not evidenced: no .github dir, Pages API blocked to me, no ping record. "Resume scheduled" for Canva quota: no matching scheduled task visible to me.
- **Orch R5 Y.** See deviations below. Also: DECISIONS edit log has no row for the ee57a70 correction row. Practice (in-place `[PROVISIONAL]` overwrite, single row) differs from AGENTS.md ("both agents append in the same commit").

## Cross-checks

| Check | Result |
|---|---|
| Verdict sets in DECISIONS vs issues #1-#4 | Match. r02 and r03 rows first carried wrong counts ("1 love-equiv/3/4" sums to 8 of 7 cards; "14/21" instead of 15/20); corrected by append. |
| Tallies vs manifest card counts | 12/7/48/43, all sum correctly. |
| STATUS locks vs DECISIONS | Trace, except the inferences noted in Aes R1 and Struct R1. |
| Stale `[PROVISIONAL]` rows | None older than today. Three open, all 2026-11-15 and expected: AGENTS.md, AUDIT.md, teams/audit/STATUS.md. |
| DECISIONS append-only | Content: held (git log -p shows only edit-log sign-off cells changed). Position: new rows inserted above the r01 row. |
| Round-05 charter vs r04 verdicts | Consistent (mask arms = m01/m07/m08/m12; body = c03/c07 notes, v03/v08, p07). Two issues: "all-generated, no outliers" departs from the 2026-11-14 Evan-approved 4-group/outlier method with no DECISIONS row, and it depends on one credit-limited generator. |
| Images vs manifests (read c01, c02, c05, r02/07, r01/09) | Match titles and rationale. c01 preview (150x199) and full-res (904x1200) are the same composition. |

## Known deviations: judged

- **Haiku sign-offs.** Labelled "(haiku)" per row: honest. Reason (Sonnet rate limit) appears nowhere in the repo; policy in CLAUDE.md/AGENTS.md was not amended. Cost was real: haiku signed the wrong r02/r03 counts. Verdict: honest, under-documented, weak.
- **Orchestrator trawled r04 mask group inline.** Disclosed in r04 manifest notes. Removed from STATUS in c277006 but kept in the manifest. Output was usable (Evan loved m01, liked m07/m08/m12). Separation of duties lost: the orchestrator trawled, assembled, and backpropped.
- **r02 7/12, r04 43/48.** Disclosed with causes in manifest notes and STATUS. Honest. But Evan sees none of it on the board (notes not rendered).
- **r04 voted at 150px.** Love on c01/c02 was given on 7 KB thumbnails; images were then replaced in place in a "DO NOT EDIT" directory (427839e). Disclosed in manifest notes; old files recoverable at 5055d25. Verdict: honest. Caveat: c02's "serene stone smile" detail was barely visible at that size, and it underpins the mask lock.

## Lagging areas and proposals

- **Structural: lag, now starting.** The stub was justified before liaison v2 (ee57a70). From 2026-11-14 15:28 it had a concrete load case (3 plant-shelf spans, 2-5 kg, cantilever, wall anchors) and nothing committed for ~22 hours; an uncommitted first pass appeared during this audit (see Struct R4). Remaining geometry-independent work: cantilever and anchor calc, FDM load-direction and creep constraints (layer adhesion, PLA vs PETG), mass and print-time order of magnitude for ~3x3 ft.
- **CAD: sequencing correct for geometry, lag for enabling work.** Not blocked on: toolchain choice, mesh and tolerance spec, hardware library (inserts, cleats, screws). The unowned question is how 3D geometry gets made at all (generative 3D, sculpt, procedural).
- **Fabrication: same.** 256 mm bed and a ~3 ft piece imply on the order of 12+ segments. Nobody has asked Evan about visible-seam tolerance, material, or finish (r03 notes: printed-cleat and seam cards were bot-walled and never replaced). These feed back into aesthetics.
- **Aesthetics: on track.** Fix the STATUS hygiene; stop reporting round-05 as in progress.
- **Process.** Commit a 15-line tally script (I recounted all four rounds in that much). Render manifest `notes` in the board. Commit generation prompts. Snapshot or hash hotlinked images. Refresh CLAUDE.md map.

## Not verified, and why

- IMG_0073 sketch (HEIC; no decoder available). The plant-shelf and mask/maw constraints rest on the orchestrator's reading, relayed in DECISIONS.
- Email pings and GitHub Pages deploys (no records; Pages API blocked).
- That hotlinked images are still live (one test returned HTTP 429 from Wikimedia through the sandbox proxy; inconclusive).
- Whether Evan was told of deviations outside the board (chat not auditable).
- Existence or behavior of leads and workers: ephemeral, no durable trace.
- "Resume scheduled" for Canva credits.
