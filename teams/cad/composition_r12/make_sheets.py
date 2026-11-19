#!/usr/bin/env python3
"""contact_sheet.png (13 fronts + original A = r08c G1a_b), PIL validation (<= 1 MB each, all PNGs)."""
import os, glob
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, 'renders')
IDS = ['C%d' % i for i in range(1, 11)]
import studies
LAB = {k: k + ' ' + studies.TABLE[k] for k in IDS}
CW, CH = 400, 300; cols = 4; rows = 3
def sheet_of(tiles, name, cols, rows):
    sh = Image.new('RGB', (CW * cols, CH * rows), (8, 8, 8)); d = ImageDraw.Draw(sh)
    for i, (lab, p) in enumerate(tiles):
        if not os.path.exists(p): continue
        im = Image.open(p).convert('RGB').resize((CW, CH), Image.LANCZOS); x, y = (i % cols) * CW, (i // cols) * CH; sh.paste(im, (x, y)); d.rectangle([x, y, x + 8 + 6 * len(lab), y + 14], fill=(0, 0, 0)); d.text((x + 4, y + 2), lab, fill=(240, 240, 240))
    sh.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(f'{R}/{name}', optimize=True)
sheet_of([('r11 H (hero)', os.path.join(HERE, '..', 'composition_r11', 'renders', 'study_H_front.png'))] + [(LAB[s], f'{R}/study_{s}_front.png') for s in IDS], 'contact_sheet.png', cols, rows)
sheet_of([('r11 H side', os.path.join(HERE, '..', 'composition_r11', 'renders', 'study_H_side.png'))] + [(LAB[s] + ' side', f'{R}/study_{s}_side.png') for s in IDS], 'contact_sheet_side.png', cols, rows)
bad = []
for f in sorted(glob.glob(f'{R}/*.png')):
    try:
        Image.open(f).verify(); Image.open(f).load()
        if os.path.getsize(f) > 1_000_000: bad.append((f, os.path.getsize(f)))
    except Exception as ex: bad.append((f, str(ex)))
print('PNG validation:', 'OK' if not bad else bad, len(glob.glob(f'{R}/*.png')), 'files')
