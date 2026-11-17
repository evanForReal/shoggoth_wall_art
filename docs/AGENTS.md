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

**Sign-off substance rules (RP-2, 2026-11-16):**
- The signed-off-by cell names what was verified (e.g. `docs-reviewer (verified: tally vs issue #5, 3 notes)`), not just the reviewer.
- An open flag is not a signature: the cell reads `FLAG OPEN: <issue>` until the flag is resolved by a later row. Only cosmetic/no-action flags may be signed through, and must say so.
- Clearing a sign-off also clears the matching `[PROVISIONAL]` tags in the file body, in the same commit.
- A review board may ship cards that depend on unsigned sources only if the manifest notes name the unsigned source.
- Engineering numbers in READMEs/STATUS must trace to a committed JSON or script output; unsourced numbers are cut or marked "unsourced".

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
- **2026-11-16, orchestrator model.** The model policy ("all subagents run Sonnet") governs subagents; the Orchestrator runs in the main session on whatever model Evan selects. Commit trailers name the Orchestrator's model, which is why they differ from the subagent model. Evan switched the Orchestrator's model mid-session on 2026-11-16 and asked for an Orchestrator session log so its choices can be audited later: artifacts/session-log/. Closes audit cycle-2 carry-over (RP-2 item 8). Model policy for subagents unchanged.
- **2026-11-16, orchestrator signs as aesthetics-lead.** The Orchestrator has been acting as Aesthetics Lead (liaison signature in teams/aesthetics/STATUS.md). Consequence: in council votes the Orchestrator does not also cast an aesthetics-lead vote (would double-count one actor). Logged at RP-2 vote.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-13 | docs-lead | Initial creation | docs-reviewer |
| 2026-11-15 | orchestrator | Added Audit Lead to hierarchy + charters (Evan directive) | docs-reviewer |
| 2026-11-15 | docs-worker | Added Deviation log section | docs-reviewer |
| 2026-11-15 | orchestrator | CAD charter amended: owns step-2 geometry | docs-reviewer |
| 2026-11-16 | orchestrator | Sign-off substance rules (RP-2 item 5); deviation-log entries: orchestrator model, orchestrator-as-aesthetics-lead | docs-reviewer (verified: rules bullets 1-4 match RP-2 item 5 in teams/audit/STATUS.md and SL-11; both deviation entries vs git trailers (Fable 5 through ca9747f, Opus 5.5 from 0671872), SL-07, SL-09 and the aesthetics STATUS liaison line; no body [PROVISIONAL] tag belongs to this row. Non-blocking, signed through: bullet 5 (engineering numbers trace to committed JSON or script) is beyond item 5 text, it generalises RP-2 item 2; Orchestrator to confirm intended) |
