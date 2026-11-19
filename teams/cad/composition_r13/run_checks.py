#!/usr/bin/env python3
"""r13: DESIGN_PRINCIPLES s.4 checklist (#1-13, checks.py) + tools/composition_gate.py on H13 and E1 (information only) -> checks.json. Run after run_all.sh; R13_VAR is set per id."""
import json, subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..')); out = {}
for s in ('H13', 'E1'):
    env = dict(os.environ, R13_VAR=s)
    subprocess.run([sys.executable, '-I', os.path.join(HERE, 'checks.py'), s], check=True, capture_output=True, env=env)
    c = json.load(open(f'{HERE}/checks/{s}.json'))
    p = subprocess.run([sys.executable, '-I', f'{ROOT}/tools/composition_gate.py', f'{HERE}/renders/study_{s}_front.png', f'{HERE}/renders/study_{s}_mask.png'], capture_output=True, text=True); g = json.loads(p.stdout)
    out[s] = dict(checklist_score=c['score'], checklist_failed=c['failed'], gate_n_pass=g['n_pass'], gate_failed=g['failed'], gate_verdict=g['verdict'], verdict_excl_iou=g['verdict_excl_iou'], gate_values={k: v['value'] for k, v in g['metrics'].items()},
                  wall_lum=c['wall_luminance_pct'], flesh_lum=c['flesh_luminance_pct'], mask_lum=c['mask_luminance_pct'], maw_lum=c['maw_luminance_pct'], item4=c['checks']['4'], item11=c['checks']['11'], item13=c['checks']['13'], item10=c['checks']['10'])
json.dump(out, open(f'{HERE}/checks.json', 'w'), indent=1); print(json.dumps({k: (v['checklist_score'], v['checklist_failed'], v['gate_n_pass'], v['gate_failed'], v['verdict_excl_iou']) for k, v in out.items()}, indent=1))
