"""Round-10 spread cards: front (large) + three-quarter (small) diptych, labelled with the one change vs A0."""
from PIL import Image, ImageDraw, ImageFont
OUT='review/staging/round-10/images'; R='teams/cad/composition_r10/renders'
def card(front, tq, label, out):
    f=Image.open(front).convert('RGB'); t=Image.open(tq).convert('RGB')
    W,H=f.size; tw,th=W//2,H//2
    c=Image.new('RGB',(W+tw+30,H+60),(16,14,12)); c.paste(f,(0,60)); c.paste(t.resize((tw,th)),(W+30,60+H//4))
    d=ImageDraw.Draw(c)
    try: font=ImageFont.truetype('DejaVuSans.ttf',30); small=ImageFont.truetype('DejaVuSans.ttf',22)
    except: font=small=ImageFont.load_default()
    d.text((16,14),label,fill=(235,230,220),font=font); d.text((W+30,60+H//4-34),'three-quarter',fill=(170,165,155),font=small)
    c.thumbnail((1400,1000)); c.save(f'{OUT}/{out}.jpg',quality=88)
S=[('A0','A0  CONTROL: round-08 A with only the crown removed'),
   ('T1','T1  vs A0: three distinct tentacles (heavy / medium / thin)'),
   ('T2','T2  vs A0: one long whip curling past its shelf'),
   ('T3','T3  vs A0: suckers on the existing arms'),
   ('E1','E1  vs A0: one big hooded slit-pupil eye'),
   ('E2','E2  vs A0: cluster of small mismatched eyes'),
   ('M1','M1  vs A0: long inward fangs'),
   ('M2','M2  vs A0: lamprey rings of hooked teeth'),
   ('D1','D1  vs A0: sparser (fewer webs and strands)'),
   ('D2','D2  vs A0: denser'),
   ('O1','O1  outlier: A0 character on the diagonal pose'),
   ('O2','O2  outlier: A0 character on your ribbon pose'),
   ('O3','O3  outlier: mask tilted and slipping')]
for sid,lab in S: card(f'{R}/study_{sid}_front.png',f'{R}/study_{sid}_tq.png',lab,sid)
card('teams/cad/composition_r08c/renders/study_G1a_b_front.png','teams/cad/composition_r08c/renders/study_G1a_b_tq.png','A  round-08 original (you liked it twice), with crown','A')
print('ok')
