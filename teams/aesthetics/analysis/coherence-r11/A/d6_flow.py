"""Flow lines: (a) saliency-model fixation order (centre-surround DoG on luminance at 3 scales, winner-take-all with inhibition of return);
(b) hand-traced principal curves (render px) overlaid with focal points."""
from common import *
from regions import *
from scipy.ndimage import gaussian_filter
from PIL import ImageDraw
rgb = load_rgb(); g = gray(rgb); wall = wall_fit(g)
Lg = gaussian_filter(g, 2.2)               # 3 m acuity
sal = np.zeros_like(g)
for s in (6, 12, 24):
    d = np.abs(gaussian_filter(Lg, s) - gaussian_filter(Lg, 4*s)); sal += d/d.max()
sal[:100] = 0; sal[860:] = 0; sal[:, :190] = 0; sal[:, 1010:] = 0
S = sal.copy(); fix = []
for k in range(8):
    y, x = np.unravel_index(np.argmax(S), S.shape)
    nm = [n for n, r in REG.items() if r[y, x]]
    fix.append(dict(rank=k+1, x=int(x), y=int(y), sal=float(S[y, x]/sal.max()), region=nm[0] if nm else "other"))
    yy2, xx2 = np.mgrid[0:S.shape[0], 0:S.shape[1]]; S[(yy2-y)**2+(xx2-x)**2 < 70**2] = 0
CURVES = {
  "spine (mask > left trunk > hub)":   [(560,320),(520,380),(490,450),(500,540),(560,615),(610,650)],
  "lower-right sweep":                  [(610,650),(700,700),(800,720),(900,750),(955,800),(935,822)],
  "lower-left sweep":                   [(600,650),(520,700),(400,740),(300,790),(240,832)],
  "S1_UL arm":                          [(500,380),(470,330),(440,270),(420,245),(330,245)],
  "S3_LL arm":                          [(520,570),(470,630),(440,645),(330,650)],
  "S2_UR arm":                          [(640,430),(690,385),(770,365),(880,360)],
  "whip":                               [(975,390),(985,440),(950,510),(900,525),(872,497)],
}
FOCI = {"mask": (572,238), "maw": (618,465), "eye patch": (668,235), "shoulder eyes": (490,400)}
res = dict(fixations=fix)
res["region_saliency_max_rel_mean_rel"] = {k: [round(float(sal[r].max()/sal.max()), 2), round(float(sal[r].mean()/sal.max()), 2)] for k, r in REG.items()}
# curve metrics: polyline length (mm), turning (deg total), terminates within 120 px of a focal point?
def plen(p): return float(sum(np.hypot(*(np.array(p[i+1])-np.array(p[i]))) for i in range(len(p)-1)))
cm = {}
for k, p in CURVES.items():
    a = np.array(p, float); v = np.diff(a, axis=0); ang = np.degrees(np.arctan2(v[:, 1], v[:, 0])); turn = np.abs(np.diff(np.unwrap(np.radians(ang))))
    cm[k] = dict(length_mm=round(plen(p)*PX_MM), total_turn_deg=round(float(np.degrees(turn.sum()))),
                 max_kink_deg=round(float(np.degrees(turn.max())) if len(turn) else 0))
res["curves"] = cm
# shelf-top brightness vs focal: mean luminance of the lit shelf lips
for nm in ("shelf_UL", "shelf_UR", "shelf_LL"):
    r = REG[nm]; res[f"{nm}_p90_lum"] = float(np.percentile(g[r], 90))
res["mask_p50_lum"] = float(np.percentile(g[REG["mask"]], 50)); res["wall_med"] = float(np.median(wall))
dump("d6_flow.json", res)
print(json.dumps(res, indent=1))
im = Image.fromarray(np.clip(g*0.9, 0, 255).astype(np.uint8)).convert("RGB")
d = ImageDraw.Draw(im, "RGBA")
cols = [(255,200,0),(80,200,255),(80,255,140),(255,120,200),(255,120,60),(180,140,255),(255,255,120)]
for (k, p), c in zip(CURVES.items(), cols):
    d.line(p, fill=c+(230,), width=5)
    x, y = p[-1]; d.ellipse([x-7, y-7, x+7, y+7], outline=c+(255,), width=3)
for k, (x, y) in FOCI.items():
    d.ellipse([x-18, y-18, x+18, y+18], outline=(255,255,255,255), width=2); d.text((x+20, y-6), k, fill=(255,255,255,255))
pts = [(f["x"], f["y"]) for f in fix[:6]]
d.line(pts, fill=(255,0,0,160), width=2)
for f in fix[:6]:
    x, y = f["x"], f["y"]; d.ellipse([x-12, y-12, x+12, y+12], fill=(220,0,0,200)); d.text((x-3, y-6), str(f["rank"]), fill=(255,255,255,255))
legend = " | ".join(CURVES.keys())
d.rectangle([0, 0, 1200, 18], fill=(0,0,0,200)); d.text((6, 3), "red numbered = saliency fixation order 1-6 (model, not eye tracking); coloured = hand-traced principal curves; white rings = focal points", fill=(255,255,255,255))
print("kb", save(im.crop((150, 0, 1050, 880)), "d6_flow_overlay.png"))
