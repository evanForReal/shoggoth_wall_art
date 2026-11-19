"""Plant-foliage mass: geometry metrics (mm space) + labelled MOCK render (upright vs trailing). Foliage geometry is an assumption:
pot 150 w x 130 h on each shelf top centre; upright foliage ellipse 260 w x 320 h (inside the 300 mm clear volume + pot); trailing = vines hanging 380 mm."""
from common import *
from regions import *
from PIL import ImageDraw, ImageFilter
import random
S = 1.5; N0 = 640; N = 1100; c = N/2
sil0 = np.load(os.path.join(OUT, "mesh_sil.npy"))
sil = np.zeros((N, N), bool); o = (N-N0)//2
sil[o:o+N0, o:o+N0] = sil0
yy, xx = np.mgrid[0:N, 0:N]
disc = ((xx-(c-32/S))**2 + (yy-(c-248/S))**2) <= (100/S)**2; sil |= disc
SH = {"UL": (-335, 285), "UR": (335, 150), "LL": (-335, -190)}
def ellmm(cx, cy, w, h): return ((xx-(c+cx/S))/(w/2/S))**2 + ((yy-(c-cy/S))/(h/2/S))**2 <= 1
def rectmm(cx, y0, w, h): return (abs(xx-(c+cx/S)) <= w/2/S) & (yy <= c-y0/S) & (yy >= c-(y0+h)/S)
pl_up = np.zeros_like(sil); pl_tr = np.zeros_like(sil)
for k, (x, y) in SH.items():
    pot = rectmm(x, y, 150, 130)
    pl_up |= pot | ellmm(x, y+130+140, 260, 320)
    pl_tr |= pot | ellmm(x, y+130+50, 240, 110) | rectmm(x-100, y-380, 40, 380) | rectmm(x+90, y-300, 36, 300) | rectmm(x, y-240, 30, 240)
res = {}
def metrics(m, tag):
    ys, xs = np.nonzero(m)
    L = m[:, :int(c)].sum(); R = m[:, int(c):].sum()
    # ENV = 914 mm square centred at (c, c)
    d = dict(centroid_x_mm=float((xs.mean()-c)*S), centroid_y_mm=float((c-ys.mean())*S), LR_ratio=float(max(L, R)/min(L, R)),
             heavier="L" if L > R else "R", area_pct_env=float(m.sum()/(914/S)**2*100))
    top = (c-ys.min())*S; d["top_extent_mm"] = float(top)
    return d
res["fig_only"] = metrics(sil, "fig"); res["fig+upright"] = metrics(sil | pl_up, "up"); res["fig+trailing"] = metrics(sil | pl_tr, "tr")
# left wedge (between UL shelf underside and LL shelf top, left of the trunk): x -457..-250 mm, y -190..215 mm
wedge = (xx >= c-457/S) & (xx <= c-250/S) & (yy >= c-215/S) & (yy <= c+190/S) & ~sil
res["left_wedge_area_mm2"] = float(wedge.sum()*S*S)
res["left_wedge_covered_by_upright_plants_pct"] = float((wedge & pl_up).sum()/wedge.sum()*100)
res["left_wedge_covered_by_trailing_plants_pct"] = float((wedge & pl_tr).sum()/wedge.sum()*100)
# right of UR shelf: whip-side wedge region x 250..457, y 150..457 above shelf UR: plant
res["plants_above_envelope_top_mm_upright"] = {k: max(0, y+130+300-457) for k, (x, y) in SH.items()}
# plant vs eye patch/head dome clearance: UR plant left edge x = 335-130 = 205 mm; dome right edge ~ +120 mm (mesh)
res["UR_plant_left_edge_mm"] = 335-130
dump("d7_plants.json", res); print(json.dumps(res, indent=1))
# --- mock render ---
rgb = load_rgb(); PAD = 300
pad = np.pad(rgb, ((PAD, 0), (0, 0), (0, 0)), mode="edge")
# soften padded rows to match wall gradient
base = Image.fromarray(pad.astype(np.uint8))
def pxpos(xmm, ymm):   # mm -> padded render px.  render: x_px = 600 + xmm/PX_MM ; y: top of piece (y=379.5 mm) at row 126
    return (600 + xmm/PX_MM + 0.0, PAD + 126 + (379.5-ymm)/PX_MM)
random.seed(7)
def leaf(d, cx, cy, ang, L, w, col):
    a = np.deg2rad(ang); ux, uy = np.cos(a), np.sin(a); vx, vy = -uy, ux
    pts = []
    for t in np.linspace(0, 1, 9):
        ww = w*np.sin(np.pi*t)**0.8
        pts.append((cx+ux*L*t+vx*ww, cy+uy*L*t+vy*ww))
    for t in np.linspace(1, 0, 9):
        ww = w*np.sin(np.pi*t)**0.8
        pts.append((cx+ux*L*t-vx*ww, cy+uy*L*t-vy*ww))
    d.polygon(pts, fill=col)
def draw_plants(im, mode):
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for k, (x, y) in SH.items():
        bx, by = pxpos(x, y+2)
        # pot
        pw = 150/PX_MM/2; ph = 130/PX_MM
        d.polygon([(bx-pw, by-ph), (bx+pw, by-ph), (bx+pw*0.78, by), (bx-pw*0.78, by)], fill=(120, 70, 50, 255))
        d.rectangle([bx-pw-3, by-ph-8, bx+pw+3, by-ph], fill=(140, 82, 58, 255))
        topy = by-ph-6
        if mode == "up":
            for i in range(46):
                ang = -90 + random.uniform(-62, 62); L = random.uniform(120, 300)/PX_MM; w = random.uniform(10, 20)/PX_MM*1.4
                g = random.randint(55, 105); leaf(d, bx+random.uniform(-40, 40)/PX_MM, topy, ang, L, w, (30, g, 40, 255))
        else:
            for i in range(14):
                ang = -90 + random.uniform(-80, 80); L = random.uniform(70, 150)/PX_MM; w = random.uniform(8, 14)/PX_MM*1.4
                leaf(d, bx+random.uniform(-40, 40)/PX_MM, topy, ang, L, w, (35, random.randint(70, 110), 45, 255))
            # trailing vines hanging down over shelf front, to ~380 mm
            for j, off in enumerate((-95, -30, 40, 95)):
                px0 = bx+off/PX_MM; py0 = topy+10; Lh = random.uniform(260, 400)/PX_MM
                pts = [(px0+ 14*np.sin(t*5+j), py0+t*Lh) for t in np.linspace(0, 1, 40)]
                d.line(pts, fill=(34, 92, 48, 255), width=4)
                for t in np.linspace(0.05, 1, 16):
                    xx0, yy0 = px0+14*np.sin(t*5+j*1.0), py0+t*Lh
                    leaf(d, xx0, yy0, random.choice([20, 160]) , 26/PX_MM*1.2, 9/PX_MM*1.3, (38, random.randint(85, 125), 52, 255))
    sh = lay.filter(ImageFilter.GaussianBlur(7)); shadow = Image.new("RGBA", im.size, (0, 0, 0, 0)); 
    a = np.asarray(lay)[..., 3].astype(float)*0.45; sa = Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.GaussianBlur(7))
    shadow.putalpha(sa); im = im.convert("RGBA"); im.alpha_composite(shadow, (10, 10)); im.alpha_composite(lay)
    return im.convert("RGB")
mu = draw_plants(base.copy(), "up"); mt = draw_plants(base.copy(), "tr")
box = (100, 40, 1100, 1180)
def lab(im, t):
    d = ImageDraw.Draw(im); d.rectangle([0, 0, im.size[0], 20], fill=(0, 0, 0)); d.text((6, 4), t, fill=(255, 220, 120)); return im
ims = [lab(x.crop((box[0], 0, box[2], base.size[1])).resize((600, int(base.size[1]*600/1000))), t) for x, t in ((mu, "MOCK A: upright plants (assumed 260x320 mm foliage)"), (mt, "MOCK B: trailing plants over shelf fronts"))]
sheet = Image.new("RGB", (1210, ims[0].size[1]), (15, 15, 15)); sheet.paste(ims[0], (0, 0)); sheet.paste(ims[1], (610, 0))
print("kb", save(sheet, "q3_plants_mock.png"))

