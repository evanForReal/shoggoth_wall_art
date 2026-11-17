"""Trace-sensitivity sweep of the composition gate on c01's own mask (README s.3). Run from repo root:
   python3 -I teams/aesthetics/analysis/composition_gate/sensitivity_sweep.py
Perturbations (source-pixel units, frame 904x1200): erode/dilate by a disk of radius R px (4, 8); rotate render+mask
+-4 deg about the mask bbox centre (mask nearest, render bilinear); mirror L-R of render+mask. Writes sensitivity_sweep.md/.json.
"""
import sys, json, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import disk
sys.path.insert(0, 'tools')
import composition_gate as cg

D = 'teams/aesthetics/analysis/composition_gate/'
SRC = 'review/rounds/round-04/images/c01_baseline-velvet-salon.jpg'
rgb0, mask0 = cg.load(SRC, D + 'c01_mask.png')
ref = np.asarray(Image.open(D + 'c01_mask_envelope.png').convert('L').resize((cg.N, cg.N), Image.NEAREST)) > 127
ys, xs = np.where(mask0)
ctr = ((xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2)

def run(rgb, mask):
    sq, box = cg.envelope(mask)
    g = cg.geometry_metrics(sq)
    h = cg.head_metrics(rgb, mask, box)
    return dict(fill=g['fill_ratio'], wedges=g['wedge_count'], torso_w=g['torso_width_frac'], reach=g['limb_reach_ratio'],
                limbs=g['limb_count'], head_flesh=h['head_vs_flesh'], iou=cg.iou_vs(sq, ref))

def morph(r, grow):
    se = disk(r)
    return ndi.binary_dilation(mask0, se) if grow else ndi.binary_erosion(mask0, se)

def rot(deg):
    img = Image.fromarray((rgb0 * 255).astype(np.uint8)).rotate(deg, Image.BILINEAR, center=ctr)
    m = Image.fromarray((mask0 * 255).astype(np.uint8)).rotate(deg, Image.NEAREST, center=ctr)
    return np.asarray(img).astype(float) / 255, np.asarray(m) > 127

rows = [('base', rgb0, mask0),
        ('erode 8 px', rgb0, morph(8, False)), ('erode 4 px', rgb0, morph(4, False)),
        ('dilate 4 px', rgb0, morph(4, True)), ('dilate 8 px', rgb0, morph(8, True)),
        ('rot -4 deg', *rot(-4)), ('rot +4 deg', *rot(4)),
        ('mirror L-R', rgb0[:, ::-1], mask0[:, ::-1])]
out = {n: run(r, m) for n, r, m in rows}
json.dump(out, open(D + 'sensitivity_sweep.json', 'w'), indent=1)
L = ['| perturbation | fill | wedges | torso w | reach | limbs | head/flesh | IoU |', '|---|---|---|---|---|---|---|---|']
for n, v in out.items():
    L.append(f"| {n} | {v['fill']:.3f} | {v['wedges']} | {v['torso_w']:.3f} | {v['reach']:.3f} | {v['limbs']} | {v['head_flesh']:.2f} | {v['iou']:.2f} |")
open(D + 'sensitivity_sweep.md', 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
