"""Round-07 cards: 3-value notan (wall light / body dark / maw black / mask white) + shaded massing diptych."""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R='teams/cad/composition_r07/renders'; OUT='review/staging/round-07/images'
WALL=(200,195,186); BODY=(58,44,34); MAW=(8,6,5); MASK=(250,246,236)
def notan(front, mask):
    f=np.asarray(Image.open(front).convert('L'),float)/255
    m=np.asarray(Image.open(mask).convert('L'))>127
    out=np.zeros(f.shape+(3,),np.uint8); out[:]=WALL
    out[m]=BODY
    head=m&(f>0.62); maw=m&(f<0.10)
    # keep only the largest bright blob as the mask/head
    from scipy import ndimage as ndi
    lab,n=ndi.label(head)
    if n: head=lab==(1+np.argmax(ndi.sum(head,lab,range(1,n+1))))
    lab,n=ndi.label(maw)
    if n: maw=lab==(1+np.argmax(ndi.sum(maw,lab,range(1,n+1))))
    out[maw]=MAW; out[head]=MASK
    return Image.fromarray(out)
def card(sid, label):
    n=notan(f'{R}/study_{sid}_front.png', f'{R}/study_{sid}_mask.png')
    s=Image.open(f'{R}/study_{sid}_front.png').convert('RGB')
    W,H=n.size; sw,sh=W//2,H//2
    c=Image.new('RGB',(W+sw+30,H+60),(16,14,12)); c.paste(n,(0,60)); c.paste(s.resize((sw,sh)),(W+30,60+H//4))
    d=ImageDraw.Draw(c)
    try: font=ImageFont.truetype('DejaVuSans.ttf',30); small=ImageFont.truetype('DejaVuSans.ttf',22)
    except: font=small=ImageFont.load_default()
    d.text((16,14),label,fill=(235,230,220),font=font)
    d.text((W+30,60+H//4-34),'massing (no surface yet)',fill=(170,165,155),font=small)
    c.thumbnail((1400,1000)); c.save(f'{OUT}/{sid}.jpg',quality=88)
if __name__=='__main__':
    for sid,lab in [('G1a','G1a  c01-style: tall trunk, shelves high-left / mid-right / low-left'),
                    ('G1b','G1b  same, head offset + leaning trunk'),
                    ('G2a','G2a  diagonal emergence, head upper right'),
                    ('G3a','G3a  low crouch, horns, VERTICAL maw'),
                    ('G3b','G3b  low crouch, horns, HORIZONTAL maw'),
                    ('G4a','G4a  sinuous ribbon (closest to your sketch)')]:
        card(sid,lab)
    # c01 reference: original + traced silhouette
    o=Image.open('review/rounds/round-04/images/c01_baseline-velvet-salon.jpg').convert('RGB')
    ov=Image.open('teams/aesthetics/analysis/composition_gate/c01_overlay.png').convert('RGB')
    h=900; o=o.resize((int(o.width*h/o.height),h)); ov=ov.resize((int(ov.width*h/ov.height),h))
    c=Image.new('RGB',(o.width+ov.width+30,h),(16,14,12)); c.paste(o,(0,0)); c.paste(ov,(o.width+30,0))
    c.thumbnail((1400,1000)); c.save(f'{OUT}/c01_ref.jpg',quality=88)
    print('ok')
