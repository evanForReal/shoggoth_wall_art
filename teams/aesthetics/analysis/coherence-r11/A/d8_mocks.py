"""Crude labelled MOCK image edits of H for the question cards (Q1 eyes, Q2 root tangle, Q4 visible grip). Not renders of geometry."""
from common import *
from regions import *
from scipy.ndimage import median_filter, gaussian_filter, uniform_filter
from PIL import ImageDraw, ImageFilter
rgb = load_rgb(); g = gray(rgb); wall = wall_fit(g)
fm = ndi.binary_dilation(figure_mask(g, wall, thr=8), iterations=3)
def lab(im, t):
    d = ImageDraw.Draw(im); d.rectangle([0, 0, im.size[0], 20], fill=(0, 0, 0)); d.text((6, 4), t, fill=(255, 220, 120)); return im
def pair(a, b, ta, tb, box, w=600):
    ia = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).crop(box); ib = Image.fromarray(np.clip(b, 0, 255).astype(np.uint8)).crop(box)
    h = int(ia.size[1]*w/ia.size[0]); ia = lab(ia.resize((w, h)), ta); ib = lab(ib.resize((w, h)), tb)
    s = Image.new("RGB", (2*w+10, h), (15, 15, 15)); s.paste(ia, (0, 0)); s.paste(ib, (w+10, 0)); return s
# ---- Q1: eyes only at the head patch (inpaint the shoulder cluster and the two arm eye rows with a local median)
m1 = REG["shoulder_eyes"] | ndi.binary_dilation(((xx_:=np.mgrid[0:900, 0:1200][1]) > 0) & False)  # placeholder, overwritten
yy, xx = np.mgrid[0:900, 0:1200]
def ell(cx, cy, a, b): return ((xx-cx)/a)**2 + ((yy-cy)/b)**2 <= 1
reg_eyes = ell(490, 400, 60, 80) | ell(470, 570, 45, 55) | ell(722, 372, 50, 22)
out = rgb.copy()
med = np.stack([median_filter(rgb[..., k], size=31) for k in range(3)], -1)
a = gaussian_filter(reg_eyes.astype(float), 3)[..., None]
out = rgb*(1-a) + med*a
q1 = pair(rgb, out, "H as built: eyes on head patch, shoulder, 2 arms", "MOCK: eyes only on the head patch (others removed)", (190, 100, 1010, 860))
print("q1 kb", save(q1, "q1_eyes_mock.png"))
# ---- Q2: lower root tangle recedes (darken 28% with vertical feather); mask/maw/shelves untouched
ramp = np.clip((yy-585)/90.0, 0, 1)
shelfLL = ell(325, 650, 125, 50)
fac = 1 - 0.40*ramp*(~shelfLL)
fac = gaussian_filter(fac, 4)[..., None]
out2 = rgb*fac
q2 = pair(rgb, out2, "H as built", "MOCK: root tangle 40% darker (recedes)", (190, 100, 1010, 860))
print("q2 kb", save(q2, "q2_tangle_mock.png"))
# ---- Q4: visible grip: three thick fingers over the lower-left mask rim + a wrist from below. Crude vector strokes.
im = Image.fromarray(rgb.astype(np.uint8)).convert("RGBA"); lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
C = np.array(MASK_C, float); R = MASK_R
def bez(p0, p1, p2, n=30):
    t = np.linspace(0, 1, n)[:, None]; return (1-t)**2*p0 + 2*(1-t)*t*p1 + t**2*p2
def tube(pts, r0, r1, base=(176, 140, 108)):
    n = len(pts)
    for i, (x, y) in enumerate(pts):          # shadow pass, then body, then highlight
        r = r0 + (r1-r0)*i/(n-1)
        d.ellipse([x-r-3, y-r-3, x+r+5, y+r+5], fill=(40, 28, 22, 70))
    for i, (x, y) in enumerate(pts):
        r = r0 + (r1-r0)*i/(n-1)
        d.ellipse([x-r, y-r, x+r, y+r], fill=base+(255,))
    for i, (x, y) in enumerate(pts):
        r = r0 + (r1-r0)*i/(n-1)
        d.ellipse([x-r*0.55-r*0.2, y-r*0.55-r*0.25, x+r*0.25-r*0.2, y+r*0.2-r*0.25], fill=(196, 160, 126, 255))
def finger(theta_deg, reach=70, over=22, r0=11, r1=8):
    th = np.deg2rad(theta_deg); u = np.array([np.cos(th), np.sin(th)]); tng = np.array([-u[1], u[0]])
    p0 = C + u*(R+reach) + tng*14; p1 = C + u*(R+10); p2 = C + u*(R-over) - tng*10
    tube([tuple(p) for p in bez(p0, p1, p2, 40)], r0, r1)
wr = [tuple(p) for p in bez(np.array([590, 385.]), np.array([578, 350.]), np.array([566, 322.]), 40)]
tube(wr, 24, 20, base=(150, 118, 92))
for th in (100, 128, 156): finger(th)
finger(62, reach=60, over=18, r0=10, r1=7)   # opposing thumb, lower right
im.alpha_composite(lay); out4 = np.asarray(im.convert("RGB"), float)
q4 = pair(rgb, out4, "H as built (6 small grip rings on the rim)", "MOCK: 3 fat fingers + thumb over the rim", (420, 110, 800, 420), w=600)
print("q4 kb", save(q4, "q4_grip_mock.png"))
