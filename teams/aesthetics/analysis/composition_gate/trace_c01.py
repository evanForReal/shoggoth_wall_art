"""Trace c01 creature silhouette: manual outline polygon + manual hole ellipses
refined by a dark-pixel test. Run: python3 -I trace_c01.py  (from repo root)
All coordinates are pixels in the 904x1200 source JPEG."""
import numpy as np, json
from PIL import Image, ImageDraw
from skimage.color import rgb2hsv
from skimage.morphology import skeletonize, closing, opening, disk, remove_small_objects
from scipy import ndimage as ndi

SRC='review/rounds/round-04/images/c01_baseline-velvet-salon.jpg'
OUT='teams/aesthetics/analysis/composition_gate/'

# MANUAL STEP 1: outline polygon, clockwise from head top. Excludes plants/pots/hanging strands,
# lamp, sofa, spotlight pools. Includes the three shelf slabs (terminal flares of limbs) and the maw (filled).
POLY=[(445,85),(480,82),(510,90),(535,105),(555,130),(568,160),(576,190),(578,215),(576,250),(580,285),
 (595,298),(612,280),(628,262),(650,252),(700,250),(780,252),(802,262),(800,272),(773,283),(753,297),(750,323),
 (740,360),(733,387),(730,420),(707,417),(673,423),(640,423),(625,440),(612,455),(600,467),
 (633,470),(653,487),(670,510),(687,530),(707,533),(727,535),(750,537),(773,543),(790,563),(800,580),(800,600),
 (793,627),(780,647),(777,653),(783,630),(787,607),(783,583),(770,567),(750,560),(723,560),(700,560),(680,557),
 (660,543),(640,530),(620,520),(600,513),(580,513),(573,523),(572,550),(573,573),(580,593),(600,603),
 (627,627),(653,647),(673,660),(683,667),(697,700),(703,727),(708,760),(697,753),(687,720),(677,700),(657,677),
 (627,670),(597,663),(570,662),(562,700),(540,735),(510,745),(470,748),(430,735),(410,700),(390,670),
 (377,677),(350,697),(323,703),(297,710),(277,720),(263,737),(250,757),(237,762),(217,763),(210,753),
 (223,740),(250,720),(263,700),(277,687),(303,670),(330,657),(350,647),(377,633),(397,613),(385,590),(373,573),
 (357,573),(323,573),(300,573),(297,583),(277,603),(250,617),(223,617),(200,607),(177,593),(150,557),
 (120,525),(103,508),(110,500),(125,496),(150,493),(180,496),(215,495),(250,477),(277,475),(307,477),(323,467),
 (337,457),(350,443),(353,433),(345,415),(338,400),(333,390),(323,367),(307,357),(277,353),(247,347),(223,330),
 (200,300),(183,273),(157,257),(123,243),(108,222),(103,210),(110,207),(127,202),(167,198),(200,193),(223,192),
 (257,197),(280,203),(297,213),(297,227),(310,240),(323,257),(343,267),(367,267),(372,240),(370,200),(370,153),
 (380,135),(393,120),(410,105),(430,95)]
# MANUAL STEP 2: interior see-through holes (wall visible). ellipse (cx,cy,rx,ry); kept only where pixel is dark.
HOLES=[(293,258,17,22),(257,330,32,11),(673,347,25,29),(633,372,15,15),(227,567,26,22)]

im=Image.open(SRC).convert('RGB'); a=np.asarray(im).astype(float)
V=rgb2hsv(a/255)[...,2]
poly=Image.new('L',im.size,0); ImageDraw.Draw(poly).polygon(POLY,fill=255)
m=np.asarray(poly)>0
for cx,cy,rx,ry in HOLES:
    h=Image.new('L',im.size,0); ImageDraw.Draw(h).ellipse([cx-rx,cy-ry,cx+rx,cy+ry],fill=255)
    m&=~((np.asarray(h)>0)&(V<0.22))
Image.fromarray((m*255).astype(np.uint8)).save(OUT+'c01_mask.png')   # full frame, pixel-aligned with the JPEG (tool input)
# normalise to bounding square (envelope)
ys,xs=np.where(m); y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
print('bbox',x0,y0,x1,y1,'w',x1-x0,'h',y1-y0)
S=max(x1-x0,y1-y0)
sq=np.zeros((S,S),bool); oy=(S-(y1-y0))//2; ox=(S-(x1-x0))//2
sq[oy:oy+y1-y0,ox:ox+x1-x0]=m[y0:y1,x0:x1]
Image.fromarray((sq*255).astype(np.uint8)).resize((512,512),Image.LANCZOS).point(lambda v:255 if v>127 else 0).save(OUT+'c01_mask_envelope.png')
json.dump(dict(bbox=[int(x0),int(y0),int(x1),int(y1)],square=int(S)),open(OUT+'c01_trace_meta.json','w'))
# overlay
ov=np.asarray(im).copy(); edge=m^ndi.binary_erosion(m,iterations=2)
ov[edge]=(0,255,255)
sk=skeletonize(m); ov[ndi.binary_dilation(sk,iterations=1)]=(255,0,255)
Image.fromarray(ov).crop((60,60,850,800)).save(OUT+'c01_overlay.png')
