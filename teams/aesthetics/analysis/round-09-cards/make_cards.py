"""Round-09 cards: front (large) + three-quarter (small) diptych."""
from PIL import Image, ImageDraw, ImageFont
OUT='review/staging/round-09/images'
def card(front, tq, label, out):
    f=Image.open(front).convert('RGB'); t=Image.open(tq).convert('RGB')
    W,H=f.size; tw,th=W//2,H//2
    c=Image.new('RGB',(W+tw+30,H+60),(16,14,12)); c.paste(f,(0,60)); c.paste(t.resize((tw,th)),(W+30,60+H//4))
    d=ImageDraw.Draw(c)
    try: font=ImageFont.truetype('DejaVuSans.ttf',30); small=ImageFont.truetype('DejaVuSans.ttf',22)
    except: font=small=ImageFont.load_default()
    d.text((16,14),label,fill=(235,230,220),font=font); d.text((W+30,60+H//4-34),'three-quarter',fill=(170,165,155),font=small)
    c.thumbnail((1400,1000)); c.save(f'{OUT}/{out}.jpg',quality=88)
R='teams/cad/composition_r09/renders'
card(f'{R}/study_S6_front.png',f'{R}/study_S6_tq.png','S6  A without crown + distinct tentacles, fangs, big eyes','S6')
card(f'{R}/study_S5_front.png',f'{R}/study_S5_tq.png','S5  same as S6, quieter eyes','S5')
card(f'{R}/study_S1_front.png',f'{R}/study_S1_tq.png','S1  fan: body left, three limbs fan to shelves','S1')
card(f'{R}/study_S2_front.png',f'{R}/study_S2_tq.png','S2  reach: body low, limbs climb a diagonal','S2')
card('teams/cad/composition_r08c/renders/study_G1a_b_front.png','teams/cad/composition_r08c/renders/study_G1a_b_tq.png','A  round-08 (your "extreme improvement"), for comparison','A')
print('ok')
