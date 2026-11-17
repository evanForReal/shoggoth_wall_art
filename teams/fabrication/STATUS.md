# Fabrication Team — STATUS.md

**Status:** ACTIVE (enabling) — estimates only; final segmentation blocked on CAD geometry.

## Exec Summary (newest first)

- 2026-11-16: RP-2 item 3. Blind-pocket relaxation (< 6 mm mouth): CONDITIONAL counter-sign. Printable if pocket opens within 45 deg of print-up, no undercut, mouth >= 2.0 mm, depth <= 3x width (wash-only to 6x), floor >= 2.6 mm; flank pockets <= 6 mm with arched roof. Evidence is size-only; depth, axis and wall angle are unmeasured by CAD. Own heightfield of gate1c/gate2 preview STLs: 84-86% of narrow-depression area <= 6 mm deep (source: analysis/heightfield/heightfield_check.json), 4-6% > 24 mm (breaks the depth rule). v2 fab-risk list: eyelids, tooth tips, maw undercuts, tentacle undersides/suckers. Vote on RP-2: FOR. Segment/mass refresh deferred to the v2 mesh. See `analysis/rp2-blind-pockets.md`.
- 2026-11-15: Enabling pass (RP-1 item 3). 3x3 ft on 256 mm bed: plan 16 segments (range 12-20; 3x2: ~12). Print time ~17 printer-days nominal (range 5-45) at ~30 g/h, ~12.6 kg incl. supports. PETG baseline, ASA if hot/sunny wall. Top risks: supports in lattice, strands below printable floor, seams/tolerance stack. See `enabling-v1.md`.
- 2026-11-13: Stub created. No fabrication work started.

## Current State

ACTIVE enabling work; CAD has produced Gate 1-2 patches and a composition-grade fullpiece (not print-res); fullpiece-v2 in build.

- `analysis/rp2-blind-pockets.md`: blind-pocket verdict (conditional, C1-C6), evidence from gate2/validation_sculpt.json, coupon plan, v2 feature fab-risk table, RP-2 vote (FOR).
- Segment/mass/print-time numbers in `enabling-v1.md` are stale against a 914 mm, 22 kg-solid proxy; refresh DEFERRED until the v2 mesh lands.

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
| 2026-11-16 | fabrication-lead | RP-2 item 3: added analysis/rp2-blind-pockets.md; exec line + Current State | docs-reviewer (resolved, was FLAG OPEN: "own heightfield" numbers (STATUS exec line "~85-90% <= 6 mm deep, 4-6% > 24 mm"; analysis s.3 cross-check table) trace to no committed script or JSON, violating AGENTS.md rule 5; mark "unsourced" or commit the script and output. Also "85-90%" overstates the table (61+25 = 86% gate1c, 64+20 = 84% gate2). Verified OK vs gate2/validation_sculpt.json: 22 incl voids, bins 9/6/7, void share <6 mm 22.2% to 33.0%, ridge P5 2.75 / 0.75, interior 208 voids 195/0/13, thin fraction 7.5% to 13.6%, thin components 135 to 85, 9 of 22 = 41%. Body [PROVISIONAL] tags kept; resolved by the two rows below it (orchestrator sourcing row, then fabrication-lead owner confirmation), re-verified at HEAD: analysis/heightfield/heightfield_check.py and heightfield_check.json are committed; re-ran build (gate1c_patch.stl, gate2_patch.stl on disk) + stats from a scratch dir with `python3 -I`: output byte-identical to heightfield_check.json (diff clean). JSON values vs s.3 table: narrow area 85.2 / 97.2 cm2 = 85 (29%) / 97 (33%); depth P50/P90/P99 2.0/8.6/121.5 and 1.8/9.4/105.1 (table shows 121, 105); band shares 61.2/24.8/6.8/1.6/5.6 and 64.4/19.7/8.3/3.3/4.4 = 61/25/7/2/6 and 64/20/8/3/4; share <= 6 mm deep 0.86 / 0.84 = '84-86%' (replaces the overstated 85-90%); '4-6% > 24 mm' = 0.056 / 0.044. Cosmetic, signed through: P99 121.5 shown as 121 (truncated, not rounded)) |
| 2026-11-17 | orchestrator | Resolves FLAG OPEN above: heightfield numbers now sourced (analysis/heightfield/heightfield_check.py + .json, re-run on the retained gate1c/gate2 heightfields, reproduces every table value); "85-90%" corrected to 84-86% | docs-reviewer (verified: script + JSON exist and reproduce byte-identically (re-run above); '84-86%' matches JSON share_le_6mm_deep 0.86 / 0.84; every s.3 cross-check table value traces to heightfield_check.json; no new numbers beyond the JSON) |
| 2026-11-17 | fabrication-lead | Owner confirmation: re-ran heightfield_check.py (build+stats) on the on-disk gate1c/gate2 preview STLs (gitignored, dated 2026-11-16, not regenerated; build is seeded) -> new JSON byte-identical to heightfield_check.json; numbers match (no change to s.3 table); script adopted as Fabrication's | docs-reviewer (verified: owner re-run claim reproduced independently (byte-identical JSON from the same on-disk gate1c/gate2 STLs, dated 2026-11-16, gitignored); script header names Fabrication as owner; satisfies the cross-team rule (owner re-runs and adopts, AGENTS Cross-team edits). Not assessed: whether the STLs equal the originals used on 2026-11-16 (not regenerated; build is deterministic per the owner)) |
