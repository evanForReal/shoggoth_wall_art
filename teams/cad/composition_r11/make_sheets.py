#!/usr/bin/env python3
"""contact_sheet.png (13 fronts + original A = r08c G1a_b), PIL validation (<= 1 MB each, all PNGs)."""
import os, glob
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, 'renders')
IDS = 'H V1 V2 V3 V4'.split()
LAB = {'H': 'H hero: held mask + eye patch', 'V1': 'V1 lamprey rings (not fangs)', 'V2': 'V2 fangs + lamprey rings', 'V3': 'V3 mask 150 mm out, 25 deg', 'V4': 'V4 patch only (arms plain)'}
CW, CH = 400, 300; cols = 4; rows = 2
sheet = Image.new('RGB', (CW * cols, CH * rows), (8, 8, 8)); d = ImageDraw.Draw(sheet)
tiles = [('r10 A0 (control)', os.path.join(HERE, '..', 'composition_r10', 'renders', 'study_A0_front.png')), ('r10 O3 (slipping mask)', os.path.join(HERE, '..', 'composition_r10', 'renders', 'study_O3_front.png'))] + [(LAB[s], f'{R}/study_{s}_front.png') for s in IDS]
for i, (lab, p) in enumerate(tiles):
    im = Image.open(p).convert('RGB').resize((CW, CH), Image.LANCZOS); x, y = (i % cols) * CW, (i // cols) * CH; sheet.paste(im, (x, y)); d.rectangle([x, y, x + 8 + 6 * len(lab), y + 14], fill=(0, 0, 0)); d.text((x + 4, y + 2), lab, fill=(240, 240, 240))
sheet.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(f'{R}/contact_sheet.png', optimize=True)
sides = Image.new('RGB', (CW * 3, CH * 2), (8, 8, 8)); d = ImageDraw.Draw(sides)
for i, s in enumerate(IDS + []):
    p = f'{R}/study_{s}_side.png'
    if not os.path.exists(p): continue
    im = Image.open(p).convert('RGB').resize((CW, CH), Image.LANCZOS); x, y = (i % 3) * CW, (i // 3) * CH; sides.paste(im, (x, y)); d.text((x + 4, y + 2), LAB[s], fill=(240, 240, 240))
sides.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(f'{R}/contact_sheet_side.png', optimize=True)
bad = []
for f in sorted(glob.glob(f'{R}/*.png')):
    try:
        Image.open(f).verify(); Image.open(f).load()
        if os.path.getsize(f) > 1_000_000: bad.append((f, os.path.getsize(f)))
    except Exception as ex: bad.append((f, str(ex)))
print('PNG validation:', 'OK' if not bad else bad, len(glob.glob(f'{R}/*.png')), 'files')
