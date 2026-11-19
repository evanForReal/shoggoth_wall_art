"""Blur / squint at simulated 3 m and 4 m. Blob ranking on the squint image."""
from common import *
from regions import *
from scipy.ndimage import gaussian_filter, maximum_filter, label
rgb = load_rgb(); g = gray(rgb); wall = wall_fit(g)
res = {"px_mm": PX_MM}
# Assumptions: 1 px = 1.17 mm. At 3 m 1 px = 1.34 arcmin.
# ACUITY blur: dim room, low contrast: effective Gaussian sigma 3 arcmin (about 1/10 deg; 20/60-ish).
# SQUINT blur: sigma 1.5% of piece width (DESIGN_PRINCIPLES s.8 recipe) = 11.7 px = 13.7 mm.
s_ac3 = arcmin_to_px(3.0, 3.0); s_ac4 = arcmin_to_px(3.0, 4.0)
s_sq = 0.015*780
res.update(sigma_acuity_3m_px=s_ac3, sigma_acuity_4m_px=s_ac4, sigma_squint_px=s_sq,
           squint_mm=s_sq*PX_MM, squint_arcmin_at_3m=s_sq*PX_MM/3000/np.pi*180*60)
b_ac = gaussian_filter(g, s_ac3); b_sq = gaussian_filter(g, s_sq)
# G64 (64 px across the 780 px piece ~ 14 mm/px)
from PIL import Image
crop = g[100:860, 190:1010]
g64 = np.asarray(Image.fromarray(crop.astype(np.float32)).resize((64, round(64*crop.shape[0]/crop.shape[1])), Image.BOX))
# blob ranking on squint
pk = (b_sq == maximum_filter(b_sq, size=61)) & (b_sq > wall + 8)
ys, xs = np.where(pk)
rows = []
for y, x in zip(ys, xs):
    nm = [k for k, r in REG.items() if r[y, x]]
    rows.append(dict(x=int(x), y=int(y), lum=float(b_sq[y, x]), region=nm[0] if nm else "other"))
rows.sort(key=lambda r: -r["lum"])
res["squint_peaks_top8"] = rows[:8]
res["mask_peak_lum"] = rows[0]["lum"]
for r in rows[:8]: r["rel_to_mask"] = r["lum"]/rows[0]["lum"]
# unblurred brightest 'non-mask' region area >= 0.5% of piece area at >=85% of mask lum (checklist #4)
mask_lum = float(np.percentile(g[REG["mask"]], 50))
bright = (b_ac >= 0.85*mask_lum) & ~REG["mask"]
lab, n = label(bright)
big = [(int(i), int((lab == i).sum())) for i in range(1, n+1) if (lab == i).sum() >= 0.005*780*780*0.55]
res["mask_median_lum"] = mask_lum
res["nonmask_comp_ge_85pct_of_mask_lum"] = len(big)
res["nonmask_px_ge_85pct"] = int(bright.sum())
# cover-the-mask test: brightest peak outside mask
oth = [r for r in rows if r["region"] != "mask"][:4]
res["second_choice_if_mask_covered"] = oth
dump("d2_squint.json", res)
print(json.dumps(res, indent=1))
# contact sheet
def norm(a, lo=15, hi=210): return np.clip((a-lo)/(hi-lo)*255, 0, 255)
tiles = [("raw (render lum)", g), ("3 m acuity blur (sigma 3 arcmin = %.1f px)" % s_ac3, b_ac),
         ("squint (sigma 1.5%% W = %.1f px, 13.7 mm)" % s_sq, b_sq)]
crop_box = (190, 100, 1010, 860)
from PIL import ImageDraw
sheet = Image.new("L", (3*410+20, 380+36+ (380)+36), 20)
d = ImageDraw.Draw(sheet)
for i, (t, a) in enumerate(tiles):
    c = norm(a[crop_box[1]:crop_box[3], crop_box[0]:crop_box[2]])
    im = Image.fromarray(c.astype(np.uint8)).resize((410, 380))
    sheet.paste(im, (i*410+10, 18)); d.text((i*410+12, 4), t, fill=235)
g64i = Image.fromarray(norm(g64).astype(np.uint8)).resize((64*6, g64.shape[0]*6), Image.NEAREST)
sheet.paste(g64i.resize((410, 380), Image.NEAREST), (10, 380+36+16)); d.text((12, 380+36), "G64 (64 px across piece, ~14 mm/px, ~4 m)", fill=235)
# squint with peaks marked
sq = Image.fromarray(norm(b_sq[crop_box[1]:crop_box[3], crop_box[0]:crop_box[2]]).astype(np.uint8)).convert("RGB").resize((410, 380))
d2 = ImageDraw.Draw(sq)
for k, r in enumerate(rows[:6]):
    x = (r["x"]-crop_box[0])*410/820; y = (r["y"]-crop_box[1])*380/760
    d2.ellipse([x-8, y-8, x+8, y+8], outline=(255, 60, 60), width=2); d2.text((x+10, y-6), str(k+1), fill=(255, 255, 0))
sheet2 = sheet.convert("RGB"); sheet2.paste(sq, (410+10, 380+36+16)); ImageDraw.Draw(sheet2).text((422, 380+36), "squint blob ranks 1-6", fill=(235,235,235))
# inverted-cover test tile: mask painted to wall value on the squint image
cov = g.copy(); cov[circ(MASK_C[0], MASK_C[1], MASK_R+4)] = np.median(wall); cov = gaussian_filter(cov, s_sq)
ct = Image.fromarray(norm(cov[crop_box[1]:crop_box[3], crop_box[0]:crop_box[2]]).astype(np.uint8)).resize((410, 380))
sheet2.paste(ct.convert("RGB"), (2*410+10, 380+36+16)); ImageDraw.Draw(sheet2).text((2*410+12, 380+36), "squint, mask erased (cover-the-mask test)", fill=(235,235,235))
print("kb", save(sheet2, "d2_squint_sheet.png"))
