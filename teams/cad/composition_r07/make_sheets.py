#!/usr/bin/env python3
"""contact_sheet.png (8 fronts + c01) and silhouette_sheet_128.png (128 px black-on-white silhouettes + c01 trace) + PIL validation of every PNG."""
import os, glob, json
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, 'renders')
IDS = 'G1a G1b G2a G2b G3a G3b G4a G4b'.split()
c01 = Image.open('/home/user/shoggoth_wall_art/review/rounds/round-04/images/c01_baseline-velvet-salon.jpg').convert('RGB')
CW, CH = 480, 360; sheet = Image.new('RGB', (CW * 3, CH * 3 + 0), (8, 8, 8)); d = ImageDraw.Draw(sheet)
for i, s in enumerate(IDS):
    im = Image.open(f'{R}/study_{s}_front.png').convert('RGB').resize((CW, CH), Image.LANCZOS); x, y = (i % 3) * CW, (i // 3) * CH
    sheet.paste(im, (x, y)); d.text((x + 8, y + 6), s, fill=(235, 235, 235))
w = int(CH * c01.width / c01.height); c = c01.resize((w, CH), Image.LANCZOS); sheet.paste(c, (2 * CW + (CW - w) // 2, 2 * CH)); d.text((2 * CW + 8, 2 * CH + 6), 'c01 (loved target)', fill=(235, 235, 235))
sheet.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(f'{R}/contact_sheet.png', optimize=True)
# silhouette sheet: crop the 780x780 px envelope (centre of the 1200x900 mask), 128 px wide
ref = Image.open('/home/user/shoggoth_wall_art/teams/aesthetics/analysis/composition_gate/c01_mask_envelope.png').convert('L')
cells = []
for s in IDS:
    m = Image.open(f'{R}/study_{s}_mask.png').convert('L'); e = m.crop((600 - 390, 450 - 390, 600 + 390, 450 + 390)).resize((128, 128), Image.BOX); cells.append((s, e))
cells.append(('c01', ref.resize((128, 128), Image.BOX)))
sw = Image.new('L', (128 * 5 + 6 * 8, 128 * 2 + 3 * 8 + 12), 255); dd = ImageDraw.Draw(sw)
for i, (n, e) in enumerate(cells):
    x = 8 + (i % 5) * (128 + 8); y = 8 + (i // 5) * (128 + 8 + 6)
    sw.paste(Image.eval(e, lambda v: 255 - v), (x, y)); dd.text((x + 2, y + 128), n, fill=0)
sw.save(f'{R}/silhouette_sheet_128.png', optimize=True)
bad = []
for f in sorted(glob.glob(f'{R}/*.png')):
    try:
        im = Image.open(f); im.verify(); im = Image.open(f); im.load(); sz = os.path.getsize(f)
        if sz > 1_000_000: bad.append((f, 'size', sz))
    except Exception as ex: bad.append((f, str(ex)))
print('PNG validation:', 'OK' if not bad else bad, len(glob.glob(f'{R}/*.png')), 'files')
