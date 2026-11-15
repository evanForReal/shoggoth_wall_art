# Fabrication Team — STATUS.md

**Status:** ACTIVE (enabling) — estimates only; final segmentation blocked on CAD geometry.

## Exec Summary (newest first)

- 2026-11-15: Enabling pass (RP-1 item 3). 3x3 ft on 256 mm bed: plan 16 segments (range 12-20; 3x2: ~12). Print time ~17 printer-days nominal (range 5-45) at ~30 g/h, ~12.6 kg incl. supports. PETG baseline, ASA if hot/sunny wall. Top risks: supports in lattice, strands below printable floor, seams/tolerance stack. See `enabling-v1.md`.
- 2026-11-13: Stub created. No fabrication work started.

## Current State

ACTIVE enabling work; no CAD mesh yet.

- `enabling-v1.md`: segment-count arithmetic (grid + area), joint shortlist (rear splice strap + pin/adhesive primary; dovetail + axial rod at shelf tips), material plan, print-time range with stated assumptions, feasibility read on c01/c02 webbing, Evan-board probes (seam visibility, material finish, perforation density).
- Still waiting for CAD geometry before: actual segmentation, joint detailing, assembly sequence, slicer profiles.
- Open: Evan's printer model/bed (Section 1 sensitivity: 220 mm bed means 20-26 segments); test-patch throughput calibration; Hexa-Waves precedent source unverified in repo; no repo intel on PLA creep (structural judgment only).

## Liaison

- 2026-11-15, fabrication→cad: sculpt must be 2.5D with bounded undercut, strands >= 2.0 mm (3.0 near load path), voids >= 6 mm arched, solid seam knuckles, maw as separate hero piece (enabling-v1 Section 5). [PROVISIONAL]

## Takeaways

None yet.

---
*Edit log*

| Date | Agent | Change | Signed-off-by |
|------|-------|--------|---------------|
| 2026-11-13 | docs-lead | Initial creation | docs-reviewer |
| 2026-11-15 | fabrication-lead | Status STUB→ACTIVE (enabling); exec summary, current state, liaison; added enabling-v1.md | docs-reviewer |
