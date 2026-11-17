#!/usr/bin/env python3
"""Silhouette IoU of an r08b study vs r07 G1a (hard skeleton check, >= 0.75). python3 iou_r07.py ID [ID..]  (grid sil from build/) ; --png compares the 1200x900 mask pngs.
Writes renders/iou_<id>.png overlay (red = r07 only, cyan = r08b only, white = both)."""
import sys, os, numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); R07 = os.path.join(HERE, '..', 'composition_r07', 'renders', 'study_G1a_mask.png')
def ref_png(): return np.asarray(Image.open(R07).convert('L')) > 127
def iou_png(path):
    a = ref_png(); b = np.asarray(Image.open(path).convert('L')) > 127; return float((a & b).sum() / (a | b).sum()), a, b
def iou_grid(sid):
    from engine import XS, YS
    sil = np.load(f'{HERE}/build/{sid}_sil.npy'); a = ref_png(); X, Y = np.meshgrid(XS, YS, indexing='ij'); col = np.clip((600 + X / 1.175).round().astype(int), 0, 1199); row = np.clip((450 - Y / 1.175).round().astype(int), 0, 899)
    ra = a[row, col] & (np.abs(X) < 457) & (np.abs(Y) < 457); sb = sil & (np.abs(X) < 457) & (np.abs(Y) < 457)
    return float((ra & sb).sum() / (ra | sb).sum()), ra, sb
if __name__ == '__main__':
    png = '--png' in sys.argv
    for s in [x for x in sys.argv[1:] if not x.startswith('--')]:
        if png: v, a, b = iou_png(f'{HERE}/renders/study_{s}_mask.png')
        else: v, a, b = iou_grid(s)
        print(s, 'IoU vs r07 G1a', round(v, 3), '(png)' if png else '(grid)')
        im = np.zeros(a.shape + (3,), np.uint8); im[a & ~b] = (230, 60, 60); im[b & ~a] = (60, 200, 220); im[a & b] = (235, 235, 235)
        if not png: Image.fromarray(im.transpose(1, 0, 2)[::-1]).resize((600, 600)).save(f'/tmp/iou_{s}.png') if False else Image.fromarray(im.transpose(1, 0, 2)[::-1]).resize((600, 600)).save(os.path.join(HERE, 'build', f'iou_{s}.png'))
