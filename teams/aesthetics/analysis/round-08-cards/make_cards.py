"""Round-08 cards: front render (large) + three-quarter (small) diptych."""
from PIL import Image, ImageDraw, ImageFont
OUT='review/staging/round-08/images'
def card(front, tq, label, out):
    f=Image.open(front).convert('RGB'); t=Image.open(tq).convert('RGB')
    W,H=f.size; tw,th=W//2,H//2
    c=Image.new('RGB',(W+tw+30,H+60),(16,14,12)); c.paste(f,(0,60)); c.paste(t.resize((tw,th)),(W+30,60+H//4))
    d=ImageDraw.Draw(c)
    try: font=ImageFont.truetype('DejaVuSans.ttf',30); small=ImageFont.truetype('DejaVuSans.ttf',22)
    except: font=small=ImageFont.load_default()
    d.text((16,14),label,fill=(235,230,220),font=font); d.text((W+30,60+H//4-34),'three-quarter',fill=(170,165,155),font=small)
    c.thumbnail((1400,1000)); c.save(f'{OUT}/{out}.jpg',quality=88)
R='teams/cad'
card(f'{R}/composition_r08c/renders/study_G1a_b_front.png',f'{R}/composition_r08c/renders/study_G1a_b_tq.png','A  horn-spire crown, ribbed trunk, jagged maw (medium)','A')
card(f'{R}/composition_r08c/renders/study_G1a_c_front.png',f'{R}/composition_r08c/renders/study_G1a_c_tq.png','B  same, denser roots + webs','B')
card(f'{R}/composition_r08b/renders/study_G1a_b_front.png',f'{R}/composition_r08b/renders/study_G1a_b_tq.png','C  root-curl crown, smooth trunk, lipped maw (earlier pass)','C')
o=Image.open('review/rounds/round-04/images/c01_baseline-velvet-salon.jpg').convert('RGB'); o.thumbnail((1000,1000)); o.save(f'{OUT}/c01_ref.jpg',quality=88)
print('ok')
