# AUDIT.md — Audit Team Charter

**Mission:** Independently verify, with evidence, that every team's work converges on Evan's vision. Produce human-readable proof of project state. Trigger recentering when work drifts.

## Rubric (v1)

Score each team per criterion: **GREEN / YELLOW / RED**, each with one line of evidence (file path, commit hash, board card id, or verdict row). No unevidenced scores.

| # | Criterion | What it measures |
|---|-----------|------------------|
| R1 | Vision compliance | Work traces to DECISIONS.md verdicts + vision constraints. No unvetted drift. |
| R2 | Readability | STATUS/docs/logs are terse, current, and sufficient for a cold agent to onboard from the repo alone. |
| R3 | Modularity / flexibility | Design + codebase structured so redesigns are modular and cheap: manifest-driven boards, decoupled rounds, geometry that can be re-segmented, constraints separated from implementations. |
| R4 | Evidence of work | Claims of progress are backed by commits, files, or boards — not assertions in STATUS prose. |
| R5 | Process integrity | Peer sign-offs present; DECISIONS.md append-only respected; verdicts backpropped within one round. |

## Method

1. Read: CLAUDE.md, docs/, every teams/*/STATUS.md (incl. edit logs), review/rounds/*, git log, open issues as summarized in DECISIONS.md.
2. Cross-check claims against artifacts (R4): a STATUS claim with no corresponding commit/file is flagged.
3. Interview live agents via messages where they exist; ephemeral agents are audited through their durable traces.
4. Score the rubric per team. Flag lagging/off-track areas with specific evidence.

## Recentering protocol

When the audit flags any RED, or 2+ YELLOWs on R1/R4 within a single area (recalibrated from "2+ YELLOW overall" per cycle-1 finding — the old threshold fired on nearly any scorecard):
1. Auditor files a **recenter proposal** in teams/audit/STATUS.md: what drifted, evidence, proposed reprioritization (task list, context, or management changes).
2. Weighted council vote: Orchestrator 3 votes, each active Team Lead 1 vote, Auditor chairs without voting. Majority carries.
3. Evan may veto or override any outcome at any time (chat or review round). Proposals touching the vision itself always escalate to Evan.
4. Approved proposals: Orchestrator applies the STATUS/task edits; outcome appended to DECISIONS.md.

## Deliverable

Per audit cycle: `artifacts/audit/<date>-exec-summary.md` — executive summary for Evan. Structure: verdict-first TL;DR; rubric scorecard with evidence links; lagging areas + proposals; what was NOT verifiable. Terse, technical, blunt. Every claim cites its evidence.

## Cadence

One audit per review-round cycle, plus on Evan's request.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-15 | orchestrator | Initial charter (Evan directive) | docs-reviewer |
| 2026-11-15 | orchestrator | Recenter threshold recalibrated (RP-1 council note; charter change) | docs-reviewer |
