"""Wall-subtraction masks for the r05/r06 hero renders (flat-colour mid-brown vignetted backdrop).
Manual steps: wall model = per-channel quadratic surface fitted to the outer 5% frame; creature = pixels whose
luma is >0.07 above the wall model OR whose saturation is >0.12 above it (dark shadow on wall keeps wall hue/sat,
so it is rejected); clean = close 3px, drop specks <200 px, fill holes < 0.1% of frame; remove cast-shadow
by requiring pixel not to be darker-and-same-hue. Run: python3 -I make_hero_masks.py (from repo root)."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.color import rgb2hsv
from skimage.morphology import closing, disk, remove_small_objects
R='/home/user/shoggoth_wall_art/'
OUT=R+'teams/aesthetics/analysis/composition_gate/'
def wall_mask(path, out):
    a=np.asarray(Image.open(path).convert('RGB')).astype(float)/255; h,w,_=a.shape
    yy,xx=np.mgrid[0:h,0:w]; X=xx/w-0.5; Y=yy/h-0.5
    B=np.zeros((h,w),bool); b=int(0.05*min(h,w)); B[:b]=B[-b:]=B[:,:b]=B[:,-b:]=True
    A=np.stack([np.ones_like(X),X,Y,X*X,Y*Y,X*Y],-1)
    hsv=rgb2hsv(a); L=0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2]; S=hsv[...,1]
    def fit(ch):
        c,*_=np.linalg.lstsq(A[B],ch[B],rcond=None); return A@c
    Lw,Sw=fit(L),fit(S)
    m=((L>Lw+0.07)|(S>Sw+0.12))
    m=closing(m,disk(3)); m=remove_small_objects(m,max_size=200)
    holes=ndi.binary_fill_holes(m)&~m; lab,n=ndi.label(holes)  # fill only tiny holes (<0.02% of frame)
    for i in range(1,n+1):
        if (lab==i).sum()<0.0002*h*w: m[lab==i]=True
    Image.fromarray((m*255).astype(np.uint8)).save(out)
    print(out,m.mean())
wall_mask(R+'teams/cad/fullpiece_v2_1/renders/hero_front.png',OUT+'hero_r06_mask.png')
wall_mask(R+'teams/cad/fullpiece/renders/hero_front.png',OUT+'hero_r05_mask.png')
