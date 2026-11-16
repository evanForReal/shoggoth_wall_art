#!/usr/bin/env python3
"""Per-round manifest summary + verdict tally verification.

Run from repo root: python3 tools/verify_tallies.py   (exit 1 on any FAIL)

1. Manifest summary: card count and axis distribution per review/rounds/round-NN.
2. Verdict check, per review/verdicts/round-NN.json (snapshot of the verdict JSON
   block from GitHub issue #N on evanForReal/shoggoth_wall_art; keys unchanged,
   plus a "source" field). For each round:
   - count love/like/dislike over verdict entries (also flags unknown verdict
     values and duplicate ids);
   - card ids must match review/rounds/round-NN/manifest.json 1:1 (ids missing
     from either side are listed);
   - tally must equal the docs/DECISIONS.md count. Source row: Round/Topic cell
     exactly "round-NN", Verdict cell "X love / Y like / Z dislike". If a
     "Correction (r02/r03 tallies)" row exists, counts parsed from its Notes
     ("Round-NN is X love / Y like / Z dislike") supersede the original row.
     The original row of a corrected round is not compared.
   Prints PASS/FAIL per round.

Snapshots are refreshed manually from the issues (GitHub MCP issue_read); this
script does not touch the network. Nothing here edits DECISIONS.md or rounds/.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

KINDS = ("love", "like", "dislike")
TALLY_RE = re.compile(r"(\d+)\s*love\S*\s*/\s*(\d+)\s*like\S*\s*/\s*(\d+)\s*dislike")
CORR_RE = re.compile(r"Round-(\d+)\s+is\s+(\d+)\s*love\s*/\s*(\d+)\s*like\s*/\s*(\d+)\s*dislike")


def decisions_rows():
    rows = []
    for line in Path("docs/DECISIONS.md").read_text().splitlines():
        if line.startswith("|"):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    return rows


def decisions_tallies():
    """Return ({round_name: (l, k, d)}, set of corrected rounds)."""
    rows = decisions_rows()
    orig = {}
    for r in rows:
        if len(r) >= 3 and re.fullmatch(r"round-\d+", r[1]):
            m = TALLY_RE.search(r[2])
            if m:
                orig[r[1]] = tuple(int(x) for x in m.groups())
    corrected = {}
    for r in rows:
        if len(r) >= 4 and r[1].startswith("Correction (r02/r03"):
            for m in CORR_RE.finditer(r[3]):
                corrected[f"round-{int(m.group(1)):02d}"] = tuple(int(x) for x in m.groups()[1:])
    return {**orig, **corrected}, set(corrected)


for mf in sorted(Path("review/rounds").glob("round-*/manifest.json")):
    cards = json.loads(mf.read_text())["cards"]
    axes = Counter(c.get("axis", "?") for c in cards)
    print(f"{mf.parent.name}: {len(cards)} cards")
    for a, n in sorted(axes.items()):
        print(f"  {a}: {n}")

print("\nverdict check")
expected, corrected = decisions_tallies()
fails = 0
for vf in sorted(Path("review/verdicts").glob("round-*.json")):
    rnd = vf.stem
    errs = []
    verdicts = json.loads(vf.read_text())["verdicts"]
    vids = [v["id"] for v in verdicts]
    unknown = [v["id"] for v in verdicts if v["verdict"] not in KINDS]
    if unknown:
        errs.append(f"unknown verdict values: {unknown}")
    dups = sorted(i for i, n in Counter(vids).items() if n > 1)
    if dups:
        errs.append(f"duplicate verdict ids: {dups}")
    mpath = Path("review/rounds") / rnd / "manifest.json"
    if mpath.exists():
        mids = {c["id"] for c in json.loads(mpath.read_text())["cards"]}
        miss_m = sorted(mids - set(vids))
        miss_v = sorted(set(vids) - mids)
        if miss_m:
            errs.append(f"in manifest, not in verdicts: {miss_m}")
        if miss_v:
            errs.append(f"in verdicts, not in manifest: {miss_v}")
    else:
        errs.append("manifest missing")
    cnt = Counter(v["verdict"] for v in verdicts)
    got = tuple(cnt[k] for k in KINDS)
    exp = expected.get(rnd)
    tag = " (correction row)" if rnd in corrected else ""
    if exp is None:
        errs.append("no DECISIONS.md tally row found")
    elif exp != got:
        errs.append(f"tally mismatch: issue {got[0]}/{got[1]}/{got[2]} vs DECISIONS{tag} {exp[0]}/{exp[1]}/{exp[2]}")
    status = "FAIL" if errs else "PASS"
    fails += bool(errs)
    print(f"{rnd}: {status}  issue {got[0]} love / {got[1]} like / {got[2]} dislike ({len(verdicts)} cards)"
          + (f"  DECISIONS{tag} {exp[0]}/{exp[1]}/{exp[2]}" if exp else ""))
    for e in errs:
        print(f"  - {e}")
sys.exit(1 if fails else 0)
