"""Score every teams/cad/composition_r07/renders/study_<id>_front.png + study_<id>_mask.png. Run from repo root:
python3 -I teams/aesthetics/analysis/composition_gate/score_r07.py  -> r07_scores.json + r07_scores.md"""
import glob, os, subprocess, json, sys
R = 'teams/cad/composition_r07/renders/'; D = 'teams/aesthetics/analysis/composition_gate/'
rows = []
for f in sorted(glob.glob(R + 'study_*_front.png')):
    i = os.path.basename(f)[6:-10]; m = R + f'study_{i}_mask.png'
    if not os.path.exists(m): rows.append(dict(id=i, error='no mask')); continue
    p = subprocess.run([sys.executable, '-I', 'tools/composition_gate.py', f, m, '--no-diag'], capture_output=True, text=True)
    d = json.loads(p.stdout); rows.append(dict(id=i, verdict=d['verdict'], verdict_excl_iou=d['verdict_excl_iou'], n_pass=d['n_pass'],
        failed=d['failed'], values={k: v['value'] for k, v in d['metrics'].items()}, warnings=d.get('warnings')))
json.dump(rows, open(D + 'r07_scores.json', 'w'), indent=1)
ks = ['fill_ratio', 'wedge_count', 'torso_width_frac', 'limb_reach_ratio', 'limb_count', 'head_vs_flesh', 'iou_vs_c01']
L = ['| id | pass | excl-IoU | ' + ' | '.join(ks) + ' | failed |', '|' + '---|' * (len(ks) + 4)]
for r in rows:
    if 'error' in r: L.append(f"| {r['id']} | {r['error']} |"); continue
    L.append(f"| {r['id']} | {r['n_pass']}/7 | {r['verdict_excl_iou']} | " + ' | '.join(f"{r['values'][k]:.3g}" for k in ks) + f" | {', '.join(r['failed']) or '-'} |")
open(D + 'r07_scores.md', 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
