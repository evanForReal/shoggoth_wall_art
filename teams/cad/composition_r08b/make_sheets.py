#!/usr/bin/env python3
"""contact_sheet.png (5 fronts + c01), silhouette_sheet_128.png, PIL validation (<= 1 MB each)."""
import os, glob
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, 'renders')
IDS = 'G1a_a G1a_b G1a_c'.split()
c01 = Image.open('/home/user/shoggoth_wall_art/review/rounds/round-04/images/c01_baseline-velvet-salon.jpg').convert('RGB')
CW, CH = 480, 360; sheet = Image.new('RGB', (CW * 3, CH * 2), (8, 8, 8)); d = ImageDraw.Draw(sheet)
for i, s in enumerate(IDS):
    im = Image.open(f'{R}/study_{s}_front.png').convert('RGB').resize((CW, CH), Image.LANCZOS); x, y = (i % 3) * CW, (i // 3) * CH; sheet.paste(im, (x, y)); d.text((x + 8, y + 6), s, fill=(235, 235, 235))
r7 = Image.open(os.path.join(HERE, '..', 'composition_r07', 'renders', 'study_G1a_front.png')).convert('RGB').resize((CW, CH), Image.LANCZOS); sheet.paste(r7, (0, CH)); d.text((8, CH + 6), 'r07 G1a (liked silhouette)', fill=(235, 235, 235))
w = int(CH * c01.width / c01.height); sheet.paste(c01.resize((w, CH), Image.LANCZOS), (CW + (CW - w) // 2, CH)); d.text((CW + 8, CH + 6), 'c01 (north star)', fill=(235, 235, 235))
sheet.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(f'{R}/contact_sheet.png', optimize=True)
ref = Image.open('/home/user/shoggoth_wall_art/teams/aesthetics/analysis/composition_gate/c01_mask_envelope.png').convert('L'); cells = []
for s in IDS:
    m = Image.open(f'{R}/study_{s}_mask.png').convert('L'); cells.append((s, m.crop((600 - 390, 450 - 390, 600 + 390, 450 + 390)).resize((128, 128), Image.BOX)))
cells.append(('c01', ref.resize((128, 128), Image.BOX)))
m7 = Image.open(os.path.join(HERE, '..', 'composition_r07', 'renders', 'study_G1a_mask.png')).convert('L'); cells.append(('r07 G1a', m7.crop((600 - 390, 450 - 390, 600 + 390, 450 + 390)).resize((128, 128), Image.BOX)))
sw = Image.new('L', (8 + 3 * 136, 8 + 2 * 142), 255); dd = ImageDraw.Draw(sw)
for i, (n, e) in enumerate(cells):
    x = 8 + (i % 3) * 136; y = 8 + (i // 3) * 142; sw.paste(Image.eval(e, lambda v: 255 - v), (x, y)); dd.text((x + 2, y + 128), n, fill=0)
sw.save(f'{R}/silhouette_sheet_128.png', optimize=True)
bad = []
for f in sorted(glob.glob(f'{R}/*.png')):
    try:
        Image.open(f).verify(); Image.open(f).load()
        if os.path.getsize(f) > 1_000_000: bad.append((f, os.path.getsize(f)))
    except Exception as ex: bad.append((f, str(ex)))
print('PNG validation:', 'OK' if not bad else bad, len(glob.glob(f'{R}/*.png')), 'files')
