#!/usr/bin/env python3
"""contact_sheet.png (13 fronts + original A = r08c G1a_b), PIL validation (<= 1 MB each, all PNGs)."""
import os, glob
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, 'renders')
IDS = 'A0 T1 T2 T3 E1 E2 M1 M2 D1 D2 O1 O2 O3'.split()
LAB = {'A0': 'A0 control (A, no crown)', 'T1': 'T1 three distinct tentacles', 'T2': 'T2 long curling whip', 'T3': 'T3 sucker row on arms', 'E1': 'E1 one big hooded eye', 'E2': 'E2 cluster of small eyes',
       'M1': 'M1 long fangs', 'M2': 'M2 lamprey rings', 'D1': 'D1 sparser', 'D2': 'D2 denser', 'O1': 'O1 diagonal (G2a)', 'O2': 'O2 sinuous ribbon (G4a)', 'O3': 'O3 slipping mask'}
CW, CH = 400, 300; cols = 5; rows = 3
sheet = Image.new('RGB', (CW * cols, CH * rows), (8, 8, 8)); d = ImageDraw.Draw(sheet)
tiles = [('A (r08c G1a_b, original)', os.path.join(HERE, '..', 'composition_r08c', 'renders', 'study_G1a_b_front.png'))] + [(LAB[s], f'{R}/study_{s}_front.png') for s in IDS]
for i, (lab, p) in enumerate(tiles):
    im = Image.open(p).convert('RGB').resize((CW, CH), Image.LANCZOS); x, y = (i % cols) * CW, (i // cols) * CH; sheet.paste(im, (x, y)); d.rectangle([x, y, x + 8 + 6 * len(lab), y + 14], fill=(0, 0, 0)); d.text((x + 4, y + 2), lab, fill=(240, 240, 240))
sheet.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(f'{R}/contact_sheet.png', optimize=True)
bad = []
for f in sorted(glob.glob(f'{R}/*.png')):
    try:
        Image.open(f).verify(); Image.open(f).load()
        if os.path.getsize(f) > 1_000_000: bad.append((f, os.path.getsize(f)))
    except Exception as ex: bad.append((f, str(ex)))
print('PNG validation:', 'OK' if not bad else bad, len(glob.glob(f'{R}/*.png')), 'files')
