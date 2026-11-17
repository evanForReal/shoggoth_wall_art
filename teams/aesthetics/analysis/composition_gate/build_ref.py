"""Build c01_metrics.json: c01 values from tools/composition_gate.py + pass bands (value x tolerance). Run from repo root."""
import sys, json, numpy as np
sys.path.insert(0, 'tools')
import composition_gate as cg
from PIL import Image
D = 'teams/aesthetics/analysis/composition_gate/'
env = np.asarray(Image.open(D + 'c01_mask_envelope.png').convert('L').resize((cg.N, cg.N), Image.NEAREST)) > 127
m, diag, sq, g = cg.compute('review/rounds/round-04/images/c01_baseline-velvet-salon.jpg', D + 'c01_mask.png', env)
v = m
# [GENERAL] tolerances; justification in README
bands = {
 'fill_ratio':       (v['fill_ratio'] * 0.80, v['fill_ratio'] * 1.20, 'x0.80..x1.20 [GENERAL]; trace sensitivity (+-8px edge shift) spans x0.89..x1.10'),
 'wedge_count':      (v['wedge_count'] - 2, v['wedge_count'] + 2, '+-2 [GENERAL]; DESIGN s.4 #10 needs >=3 at 4%'),
 'torso_width_frac': (v['torso_width_frac'] * 0.75, v['torso_width_frac'] * 1.25, 'x0.75..x1.25 [GENERAL]'),
 'limb_reach_ratio': (v['limb_reach_ratio'] * 0.70, v['limb_reach_ratio'] * 1.30, 'x0.70..x1.30 [GENERAL]; sensitivity x0.70..x1.02'),
 'limb_count':       (6, v['limb_count'] + 2, 'lo = DESIGN s.4 #6 (>=6); hi = c01+2 [GENERAL]'),
 'head_vs_flesh':    (v['head_vs_flesh'] * 0.70, v['head_vs_flesh'] * 2.0, 'x0.70..x2.0 [GENERAL] (one-sided in spirit: brighter head is fine)'),
 'iou_vs_c01':       (0.70, 1.0, 'lo 0.70 [GENERAL]: c01 rotated +-4deg = 0.74, edge shift +-8px = 0.89, c01 mirrored = 0.52; below a ~5deg rotation of c01 = different figure. No upper bound'),
}
ref = dict(source='review/rounds/round-04/images/c01_baseline-velvet-salon.jpg', ref_mask_envelope='c01_mask_envelope.png',
           params=cg.P, N=cg.N, c01_values={k: (round(x, 4) if isinstance(x, float) else x) for k, x in v.items()},
           bands={k: dict(lo=round(float(lo), 4), hi=round(float(hi), 4), rule=r) for k, (lo, hi, r) in bands.items()},
           c01_diagnostics={k: x for k, x in diag.items() if k != 'limbs'}, c01_limbs=diag['limbs'])
json.dump(ref, open(D + 'c01_metrics.json', 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
print(json.dumps(ref['c01_values'], indent=1))

# ---- overlay preview: mask edge (cyan), pruned skeleton (magenta), limb tips (yellow), torso blob (orange tint)
from scipy import ndimage as ndi
src = np.asarray(Image.open(ref['source']).convert('RGB')).copy()
bx, by, side = diag['envelope_box_xy_side']
def to_src(arr):
    big = np.asarray(Image.fromarray((arr * 255).astype(np.uint8)).resize((side, side), Image.NEAREST)) > 127
    out = np.zeros(src.shape[:2], bool)
    y0, x0 = max(by, 0), max(bx, 0)
    out[y0:y0 + side - (y0 - by), x0:x0 + side - (x0 - bx)] = big[y0 - by:, x0 - bx:][:out.shape[0] - y0, :out.shape[1] - x0]
    return out
full = np.asarray(Image.open(D + 'c01_mask.png')) > 127
tor = to_src(g['_torso']); src[tor & full] = (0.6 * src[tor & full] + 0.4 * np.array([255, 140, 0])).astype(np.uint8)
src[full ^ ndi.binary_erosion(full, iterations=2)] = (0, 255, 255)
src[ndi.binary_dilation(to_src(g['_skeleton']), iterations=2)] = (255, 0, 255)
for l in diag['limbs']:
    cx, cy = int(bx + l['tip'][0] * side), int(by + l['tip'][1] * side)
    src[cy - 6:cy + 7, cx - 6:cx + 7] = (255, 255, 0)
Image.fromarray(src).crop((60, 60, 850, 800)).save(D + 'c01_overlay.png')
Image.fromarray((g['_skeleton'] * 255).astype(np.uint8)).save(D + 'c01_centreline.png')
