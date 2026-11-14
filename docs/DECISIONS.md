# DECISIONS.md — Human Verdict Log

**Append-only.** Never delete or modify existing entries.

## Schema

| Field | Description |
|-------|-------------|
| `date` | ISO date of verdict |
| `round/topic` | Review round ID or decision topic |
| `verdict` | Evan's decision |
| `notes` | Supporting detail, constraints, follow-ups |

---

## Log

| Date | Round/Topic | Verdict | Notes |
|------|-------------|---------|-------|
| 2026-11-13 | Seed / Project kickoff | See notes | Aesthetic pole = sculptural horror (Giger + Beksiński surface language, Lovecraft conceptual). Format = undecided, explore in mood board (relief vs full-sculpture). Size ~3×2–3×3 ft. Review UX = phone swipe board (GitHub Pages) + email ping; verdicts via GitHub issue JSON. Hierarchy = 3 levels (Evan → Orchestrator → Leads → Workers). Batch 1 = 12 images across 3 axes: (1) Giger-vs-Beksiński surface language, (2) wall-format relief vs full-sculpture, (3) mask treatment. |
| 2026-11-14 | round-01 | 4 love / 3 like / 5 dislike (issue #1) | Surface: Beksiński decay palette wins (03 like, 04 love); Giger biomech skin + gothic vertebral rejected (01, 02) except where sculpture merges with wall architecture (08 love). New constraint: must blend with interior decor + carry mild-cutesy element (01 notes). Format: all wall-relief/trophy formats loved (06, 07, 08); 05 liked with note "much more freeform and concentrated on the wall". Mask: all literal mask refs rejected (09, 10, 11); 12 (shoggoth body context) liked. Round-02 axes set: cutesy-horror balance, wall-integration/relief depth, surface-finish. |

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-13 | docs-lead | Initial creation + seed entry | docs-reviewer |
| 2026-11-14 | orchestrator | Appended round-01 verdict entry | [PROVISIONAL] |
