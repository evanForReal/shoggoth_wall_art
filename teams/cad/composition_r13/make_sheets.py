#!/usr/bin/env python3
"""contact sheet: r11 H (as loved) | r12s H+ball S2 | H13 | E1 (fronts, 2x2) + PIL validation of every PNG (<= 1 MB)."""
import os, glob
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, 'renders')
tiles = [('r11 H (as loved, old palette)', f'{HERE}/../composition_r11/renders/study_H_front.png'), ('r12s H + ball S2 (old palette)', f'{HERE}/../composition_r12s/renders/study_S2_front.png'), ('H13 (scale 0.84, K1 finish)', f'{R}/study_H13_front.png'), ('E1 (width ~1200, K1 finish)', f'{R}/study_E1_front.png')]
CW, CH = 600, 450; sh = Image.new('RGB', (CW * 2, CH * 2), (8, 8, 8)); d = ImageDraw.Draw(sh)
for i, (lab, p) in enumerate(tiles):
    im = Image.open(p).convert('RGB').resize((CW, CH), Image.LANCZOS); x, y = (i % 2) * CW, (i // 2) * CH; sh.paste(im, (x, y)); d.rectangle([x, y, x + 10 + 6 * len(lab), y + 14], fill=(0, 0, 0)); d.text((x + 4, y + 2), lab, fill=(240, 240, 240))
sh.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(f'{R}/contact_sheet_r13.png', optimize=True)
bad = []
for f in sorted(glob.glob(f'{R}/*.png')):
    try:
        Image.open(f).verify(); Image.open(f).load()
        if os.path.getsize(f) > 1_000_000: bad.append((os.path.basename(f), os.path.getsize(f)))
    except Exception as ex: bad.append((f, str(ex)))
print('PNG validation:', 'OK' if not bad else bad, len(glob.glob(f'{R}/*.png')), 'files')
