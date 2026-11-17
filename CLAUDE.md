# CLAUDE.md

**Mission:** Produce a 3D-printed Shoggoth wall-art piece (~3×2–3×3 ft) — sculptural horror aesthetic, happy-face mask — from generative concept through fabrication-ready segments.

## Pipeline

1. **Aesthetic design** — mood boards, style axes, Evan review rounds
2. **Robust 3D model** — geometry passes structural + visual bar
3. **CAD model** — engineering-grade mesh, tolerances, hardware
4. **Printer-feasible segmentation** — split for ≤256 mm FDM bed, joints designed
5. **Print / assemble** — physical build, finish

## Repo Map

```
CLAUDE.md                        ← this file
docs/
  AGENTS.md                      ← hierarchy, charters, protocols
  AUDIT.md                       ← audit charter + rubric
  DECISIONS.md                   ← append-only human-verdict log
  DESIGN_PRINCIPLES.md           ← composition principles + checklist (read before composing)
teams/
  aesthetics/STATUS.md
  structural/STATUS.md
  cad/STATUS.md
  fabrication/STATUS.md
  audit/STATUS.md
  */analysis/                    ← team working analyses (calcs, diagrams)
review/
  rounds/round-NN/               ← per-round manifests + assets (DO NOT EDIT)
review-app/                      ← GitHub Pages swipe-board (DO NOT EDIT)
aesthetics vision/               ← raw human input (DO NOT EDIT)
agent orchestration/
review/verdicts/round-NN.json    ← verdict snapshots from GitHub issues
tools/                           ← repo scripts (verify_tallies.py)
artifacts/
  audit/                         ← audit exec summaries
  session-log/                   ← orchestrator judgment-call log (non-verdict choices)
```

## Ground Rules

**Prose style:** Terse, technical, blunt. No filler, no marketing language. Exec summaries over play-by-play.

**Doc-edit peer sign-off:** Every file edit requires confirmation by a second agent. Sign-off logged in that file's edit log (`date | agent | change | signed-off-by`). Unconfirmed edits are provisional.

**Escalation / review flow:** Workers → Team Leads → Orchestrator → Evan. Evan sees only decision boards (phone-friendly swipe app, GitHub Pages). Evan is pinged by email when a round is ready. Verdicts return as a JSON block in a GitHub issue on evanForReal/shoggoth_wall_art. Agents backprop verdicts into takeaways and DECISIONS.md.

**Agent model policy:** All subagents run Sonnet. Orchestrator runs in the main session. No agent contacts Evan directly; only the Orchestrator presents, and only via review rounds.

## Key Docs

- `docs/AGENTS.md` — full hierarchy, role charters, protocols
- `docs/DECISIONS.md` — human verdict log

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-13 | docs-lead | Initial creation | docs-reviewer |
| 2026-11-15 | docs-worker | Repo map: dropped nonexistent knobs dir; added AUDIT.md, teams/audit, analysis/, artifacts/audit | docs-reviewer (flagged: tools/ missing from map) |
| 2026-11-16 | orchestrator | Repo map: added tools/ (closes flag above), review/verdicts/, artifacts/session-log/ | docs-reviewer (verified: tools/ exists with verify_tallies.py, review/verdicts/ holds round-01..05.json, artifacts/session-log/ exists; `git diff 1ebb51a HEAD` adds only these three map lines; closes the tools/ flag above. Cosmetic, signed through: review/verdicts and tools lines sit directly under "agent orchestration/" with no spacing, reads as children) |
| 2026-11-17 | orchestrator | Repo map: added docs/DESIGN_PRINCIPLES.md (Evan r06 directive) | docs-reviewer (verified: docs/DESIGN_PRINCIPLES.md exists (310 lines); CLAUDE.md map line 21 sits in the docs/ block; `git show 0a33441 -- CLAUDE.md` adds only that map line and this log row; "Evan r06 directive" matches review/verdicts/round-06.json h1 ("do some review on basic elements of design ... take notes in a log somewhere for agents to view"). No body [PROVISIONAL] tag belongs to this row. Non-blocking, signed through (outside this row; Orchestrator to add with its own row): map still omits review/staging/, and the tools/ line lists only verify_tallies.py although composition_gate.py landed in 4111ef4) |
