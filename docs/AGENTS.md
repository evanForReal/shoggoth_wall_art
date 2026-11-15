# AGENTS.md

## Hierarchy

```
Evan (human — reviews only via swipe board)
  └── Orchestrator (main session, Sonnet)
        ├── Aesthetics Lead  (Sonnet)
        │     └── Workers (Sonnet)
        ├── Structural Lead  (Sonnet)
        │     └── Workers (Sonnet)
        ├── CAD Lead         (Sonnet)
        │     └── Workers (Sonnet)
        ├── Fabrication Lead (Sonnet)
        │     └── Workers (Sonnet)
        ├── Infra Lead       (Sonnet)
        │     └── Workers (Sonnet)
        └── Audit Lead       (Sonnet) — independent; reports to Evan via Orchestrator
              └── Workers (Sonnet)
```

## Role Charters

| Role | Charter |
|------|---------|
| **Orchestrator** | Drives pipeline, assembles review rounds, presents to Evan, backprops verdicts. |
| **Aesthetics Lead** | Owns visual language, mood boards, style axes. Interfaces with Structural on tentacle count/geometry. |
| **Structural Lead** | Owns load-bearing design, mount engineering, weight/strength trade-offs. Interfaces with Aesthetics and CAD. |
| **CAD Lead** | Owns step-2 geometry: turns approved 2D concepts into 3D sculpt geometry, then into engineering-grade mesh; tolerances, hardware specs. (Geometry ownership assigned 2026-11-15, DECISIONS.) |
| **Fabrication Lead** | Segmentation strategy, joint design, printer constraints, assembly sequence. |
| **Infra Lead** | Manages review-app deployment, GitHub Pages, email ping, issue ingestion. |
| **Audit Lead** | Verifies all teams' work against the rubric in docs/AUDIT.md; produces evidence-grounded exec summaries for Evan; chairs recentering votes. Independent of delivery teams. |

## Escalation Protocol

- Issues are resolved at the lowest competent level.
- Escalate upward only when blocked or when a decision affects scope/verdicts.
- Only the Orchestrator surfaces items to Evan; always via a review round board, never raw markdown.

## Peer-Confirm Protocol

Every doc edit must be confirmed by a second agent before it is considered final. Unconfirmed edits are marked `[PROVISIONAL]`.

**Edit-log line format:**

```
date | agent | change | signed-off-by
```

Both the editing agent and the confirming agent append to the edit log in the same commit. No self-sign-off.

## Review-Round Lifecycle

1. **Trawl** — Workers generate assets per axes defined by Aesthetics Lead.
2. **Manifest** — Infra assembles `review/rounds/round-NN/` manifest with metadata.
3. **Deploy** — Infra pushes GitHub Pages swipe-board update.
4. **Email ping** — Infra sends Evan notification with round link.
5. **Issue verdicts** — Evan submits verdict as JSON block in a GitHub issue on evanForReal/shoggoth_wall_art.
6. **Backprop** — Orchestrator parses verdicts, distributes to leads.
7. **Takeaways / DECISIONS update** — Leads update STATUS.md takeaways; Orchestrator appends to docs/DECISIONS.md.

## Liaison Protocol

Aesthetics and Structural must maintain a `## Liaison` section in their respective STATUS.md files. This section holds active constraints exchanged between the two teams (tentacle count, thickness ranges, mount-load estimates). Both leads must sign off on liaison entries.

## Deviation log

Departures from policy. Append only.

- **2026-11-14, Haiku sign-offs.** Cause: account 5-hour Sonnet rate limit cut off all Sonnet subagents (reset 19:10 UTC) while Evan directed work to continue. Sign-offs ran on Haiku, labelled "(haiku)". Affected: DECISIONS edit-log rows (r02+r03 verdicts, r04 verdict) and aesthetics STATUS rows (r02/r03 backprop, r04 backprop). Cost: haiku signed wrong r02/r03 tallies; caught and superseded by the DECISIONS correction row (ee57a70). Model policy not amended.
- **2026-11-14, orchestrator trawled r04 mask group inline.** Separation-of-duties exception (orchestrator trawled, assembled, backpropped). Cause: same rate limit. Disclosed in round-04 manifest notes.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-13 | docs-lead | Initial creation | docs-reviewer |
| 2026-11-15 | orchestrator | Added Audit Lead to hierarchy + charters (Evan directive) | docs-reviewer |
| 2026-11-15 | docs-worker | Added Deviation log section | [PROVISIONAL] |
| 2026-11-15 | orchestrator | CAD charter amended: owns step-2 geometry | [PROVISIONAL] |
