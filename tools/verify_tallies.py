#!/usr/bin/env python3
"""Per-round manifest summary: card count and axis distribution.

Run from repo root: python3 tools/verify_tallies.py

Verdict tallies are NOT checked here. Verdicts live in GitHub issues on
evanForReal/shoggoth_wall_art (one issue per round, JSON block in body/comment).
Audit recount (2026-11-15) method: `gh api repos/evanForReal/shoggoth_wall_art/issues/N`
(+ `/comments`) for N=1..4, parse the verdict JSON, count love/like/dislike per
card id, confirm ids match manifest card ids 1:1, sum == manifest card count,
then compare against the DECISIONS.md row for that round.
"""
import json
from collections import Counter
from pathlib import Path

for mf in sorted(Path("review/rounds").glob("round-*/manifest.json")):
    cards = json.loads(mf.read_text())["cards"]
    axes = Counter(c.get("axis", "?") for c in cards)
    print(f"{mf.parent.name}: {len(cards)} cards")
    for a, n in sorted(axes.items()):
        print(f"  {a}: {n}")
