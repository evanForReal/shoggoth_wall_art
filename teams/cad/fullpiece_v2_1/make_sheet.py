#!/usr/bin/env python3
"""variants_sheet.png: c01 reference + v1 hero_front (before) + v2 hero + 5 variants (all front). Also shrinks any render > 1 MB (palette quantise)."""
import os, glob
from PIL import Image, ImageDraw
D = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(D, 'renders')
TW, TH = 480, 360
tiles = [('c01 reference (r04)', os.path.join(D, '../../../review/rounds/round-04/images/c01_baseline-velvet-salon.jpg')),
         ('v1 hero (BEFORE, fullpiece/)', os.path.join(D, '../fullpiece/renders/hero_front.png')),
         ('v2 hero', os.path.join(R, 'hero_front.png')),
         ('a: v1_liftedge (masquerade A: lifted edge)', os.path.join(R, 'v1_liftedge_front.png')),
         ('b: v2_eyes_heavy (40 eyes)', os.path.join(R, 'v2_eyes_heavy_front.png')),
         ('c: v3_maw_big (1.28x maw, fangs)', os.path.join(R, 'v3_maw_big_front.png')),
         ('d: v4_weathered (smiley weathering 1.0)', os.path.join(R, 'v4_weathered_front.png')),
         ('e: v5_tentacles5 (5 major whips)', os.path.join(R, 'v5_tentacles5_front.png'))]
sheet = Image.new('RGB', (3 * TW, 3 * TH), (14, 12, 11)); dr = ImageDraw.Draw(sheet)
for i, (lab, p) in enumerate(tiles):
    if not os.path.exists(p): continue
    im = Image.open(p).convert('RGB'); im.thumbnail((TW, TH)); x, y = (i % 3) * TW + (TW - im.width) // 2, (i // 3) * TH + (TH - im.height) // 2
    sheet.paste(im, (x, y)); dr.rectangle([(i % 3) * TW, (i // 3) * TH, (i % 3) * TW + TW, (i // 3) * TH + 16], fill=(0, 0, 0)); dr.text(((i % 3) * TW + 4, (i // 3) * TH + 2), lab, fill=(235, 220, 190))
q = sheet.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG); q.save(os.path.join(R, 'variants_sheet.png'), optimize=True)
for p in glob.glob(os.path.join(R, '*.png')):
    if os.path.getsize(p) > 1_000_000:
        Image.open(p).convert('RGB').quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(p, optimize=True)
    print(os.path.basename(p), os.path.getsize(p))
