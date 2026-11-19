#!/usr/bin/env python3
"""contact sheets + PIL validation. python3 make_sheets.py p1|p2 ; p1 = r11 H flat disc + S1-S3 (front, side, rake), p2 = H-ball (pick) + 8 concepts (front, side)."""
import os, sys, glob, json
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, 'renders'); R11 = os.path.join(HERE, '..', 'composition_r11', 'renders')
CW, CH = 400, 300
def sheet(tiles, name, cols):
    rows = (len(tiles) + cols - 1) // cols; sh = Image.new('RGB', (CW * cols, CH * rows), (8, 8, 8)); d = ImageDraw.Draw(sh)
    for i, (lab, p) in enumerate(tiles):
        if not os.path.exists(p): print('missing', p); continue
        im = Image.open(p).convert('RGB').resize((CW, CH), Image.LANCZOS); x, y = (i % cols) * CW, (i // cols) * CH; sh.paste(im, (x, y)); d.rectangle([x, y, x + 8 + 6 * len(lab), y + 14], fill=(0, 0, 0)); d.text((x + 4, y + 2), lab, fill=(240, 240, 240))
    sh.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(f'{R}/{name}', optimize=True)
mode = sys.argv[1] if len(sys.argv) > 1 else 'p1'
if mode == 'p1':
    for v, nm in (('front', 'contact_sheet_p1_front.png'), ('side', 'contact_sheet_p1_side.png'), ('tq', 'contact_sheet_p1_tq.png')):
        sheet([('r11 H flat disc ' + v, f'{R11}/study_H_{v}.png')] + [(f'{s} ball ' + v, f'{R}/study_{s}_{v}.png') for s in ('S1', 'S2', 'S3')], nm, 2)
    sheet([(f'{s} raking close-up', f'{R}/study_{s}_rake.png') for s in ('S1', 'S2', 'S3')] + [('r11 H close', f'{R11}/study_H_close.png')], 'contact_sheet_p1_rake.png', 2)
else:
    pick = sys.argv[2]; ids = ['C1', 'C2', 'C3', 'C4', 'C6', 'C8', 'C9', 'C10']
    for v, nm in (('front', 'contact_sheet_p2_front.png'), ('side', 'contact_sheet_p2_side.png'), ('tq', 'contact_sheet_p2_tq.png')):
        sheet([(f'H + {pick} ' + v, f'{R}/study_{pick}_{v}.png')] + [(f'{c}+{pick} ' + v, f'{R}/study_{c}_{pick}_{v}.png') for c in ids], nm, 3)
bad = []
for f in sorted(glob.glob(f'{R}/*.png')):
    try:
        Image.open(f).verify(); Image.open(f).load()
        if os.path.getsize(f) > 1_000_000: bad.append((os.path.basename(f), os.path.getsize(f)))
    except Exception as ex: bad.append((f, str(ex)))
print('PNG validation:', 'OK' if not bad else bad, len(glob.glob(f'{R}/*.png')), 'files')
