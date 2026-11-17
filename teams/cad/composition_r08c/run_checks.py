#!/usr/bin/env python3
"""checks.py items #1-13 + tools/composition_gate.py for every study -> checks.json (merged)."""
import json, subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
IDS = 'G1a_b G1a_c'.split(); out = {'spec': 'DESIGN_PRINCIPLES s.4 #1-13 (checks.py) + tools/composition_gate.py; see README', 'studies': {}, 'gate': {}}
for s in IDS:
    subprocess.run([sys.executable, '-I', os.path.join(HERE, 'checks.py'), s], check=True, capture_output=True)
    out['studies'][s] = json.load(open(f'{HERE}/checks/{s}.json'))
    p = subprocess.run([sys.executable, '-I', f'{ROOT}/tools/composition_gate.py', f'{HERE}/renders/study_{s}_front.png', f'{HERE}/renders/study_{s}_mask.png'], capture_output=True, text=True)
    g = json.loads(p.stdout); out['gate'][s] = dict(n_pass=g['n_pass'], failed=g['failed'], verdict=g['verdict'], verdict_excl_iou=g['verdict_excl_iou'], values={k: v['value'] for k, v in g['metrics'].items()})
import iou_r07
for s_ in IDS: out['gate'][s_]['iou_vs_r07_G1a'] = round(iou_r07.iou_png(f'{HERE}/renders/study_{s_}_mask.png')[0], 4)
out['summary'] = {s: dict(score=out['studies'][s]['score'], failed=out['studies'][s]['failed'], gate=f"{out['gate'][s]['n_pass']}/7", gate_failed=out['gate'][s]['failed'], iou_r07=out['gate'][s]['iou_vs_r07_G1a']) for s in IDS}
json.dump(out, open(f'{HERE}/checks.json', 'w'), indent=1); print(json.dumps(out['summary'], indent=1))
