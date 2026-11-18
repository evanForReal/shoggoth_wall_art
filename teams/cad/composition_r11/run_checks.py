#!/usr/bin/env python3
"""checks.py items #1-13 + tools/composition_gate.py + shelf headroom/flat-top + diff vs A0, for all 13 studies -> checks.json."""
import json, subprocess, sys, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..')); sys.path.insert(0, HERE)
IDS = 'H V1 V2 V3 V4'.split(); out = {'note': 'headroom = measure_extra.py (volume test over the largest free flat rectangle on each plate top, clear height capped 300 mm; the envelope itself ends 172-307 mm above the tops, so the cap is read as "nothing solid above the plate plane over the patch"); gate verdict_excl_iou is for information only', 'studies': {}}
for s in IDS:
    subprocess.run([sys.executable, '-I', os.path.join(HERE, 'checks.py'), s], check=True, capture_output=True)
    c = json.load(open(f'{HERE}/checks/{s}.json'))
    p = subprocess.run([sys.executable, '-I', f'{ROOT}/tools/composition_gate.py', f'{HERE}/renders/study_{s}_front.png', f'{HERE}/renders/study_{s}_mask.png'], capture_output=True, text=True)
    g = json.loads(p.stdout)
    out['studies'][s] = dict(checklist_score=c['score'], checklist_failed=c['failed'], gate_n_pass=g['n_pass'], gate_failed=g['failed'], gate_verdict=g['verdict'], verdict_excl_iou=g['verdict_excl_iou'],
                             gate_values={k: v['value'] for k, v in g['metrics'].items()}, wall_lum=c['wall_luminance_pct'], flesh_lum=c['flesh_luminance_pct'], mask_lum=c['mask_luminance_pct'], maw_lum=c['maw_luminance_pct'])
import measure_extra
me = json.load(open(f'{HERE}/measure_extra.json'))
for s in IDS: out['studies'][s]['shelves'] = me[s]['shelves']; out['studies'][s]['diff_vs_H'] = me[s].get('diff_vs_H')
json.dump(out, open(f'{HERE}/checks.json', 'w'), indent=1); print(json.dumps({k: (v['checklist_score'], v['gate_n_pass'], v['verdict_excl_iou'], {n: (q['flat_top_x_mm'], q['flat_top_z_mm'], q['clear_above_flat_mm']) for n, q in v['shelves'].items()}) for k, v in out['studies'].items()}, indent=1))
