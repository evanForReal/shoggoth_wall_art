"""Round-11 cards: front (large) + side (small) diptych — the side view shows the held mask and the eye patch behind it."""
from PIL import Image, ImageDraw, ImageFont
OUT='review/staging/round-11/images'; R='teams/cad/composition_r11/renders'
def card(front, side, label, out, sidelabel='side view'):
    f=Image.open(front).convert('RGB'); t=Image.open(side).convert('RGB')
    W,H=f.size; tw,th=int(W*0.6),int(H*0.6)
    c=Image.new('RGB',(W+tw+30,H+60),(16,14,12)); c.paste(f,(0,60)); c.paste(t.resize((tw,th)),(W+30,60+(H-th)//2))
    d=ImageDraw.Draw(c)
    try: font=ImageFont.truetype('DejaVuSans.ttf',30); small=ImageFont.truetype('DejaVuSans.ttf',22)
    except: font=small=ImageFont.load_default()
    d.text((16,14),label,fill=(235,230,220),font=font); d.text((W+30,60+(H-th)//2-34),sidelabel,fill=(170,165,155),font=small)
    c.thumbnail((1400,1000)); c.save(f'{OUT}/{out}.jpg',quality=88)
card(f'{R}/study_H_front.png',f'{R}/study_H_side.png','H  held mask + eye patch behind it (fangs)','H')
card(f'{R}/study_H_tq.png',f'{R}/study_H_close.png','H  three-quarter + close-up','H_detail','close-up')
card(f'{R}/study_V1_front.png',f'{R}/study_V1_side.png','V1  vs H: lamprey rings instead of fangs','V1')
card(f'{R}/study_V2_front.png',f'{R}/study_V2_side.png','V2  vs H: fangs + lamprey rings','V2')
card(f'{R}/study_V3_front.png',f'{R}/study_V3_side.png','V3  vs H: mask held further out (150 mm), tilted 25°','V3')
card(f'{R}/study_V4_front.png',f'{R}/study_V4_side.png','V4  vs H: eye patch only, plain arms','V4')
print('ok')
