"""Value structure: 4-level posterize (multi-Otsu on the figure+wall) at raw and 3 m acuity blur and squint."""
from common import *
from regions import *
from skimage.filters import threshold_multiotsu
from scipy.ndimage import gaussian_filter, label
rgb = load_rgb(); g = gray(rgb); wall = wall_fit(g)
env_area = 780*780
res = {}
crop = (slice(100, 860), slice(190, 1010))
for tag, sig in [("raw", 0.0), ("acuity3m", arcmin_to_px(3.0)), ("squint", 11.7)]:
    b = gaussian_filter(g, sig) if sig > 0 else g
    # wall-relative fixed cuts (multi-Otsu cuts land on the wall gradient, see note in REPORT): 0 = wall/shadow/void (< wall+10),
    # 1 = shaded flesh (wall+10..90), 2 = lit flesh (90..165), 3 = mask / teeth / eye whites (> 165)
    q = 1*(b >= wall+10) + 1*(b >= 90) + 1*(b >= 165)
    th = [None, 90, 165]
    r = dict(thresholds='wall+10, 90, 165')
    tot = q[crop].size
    r["area_share_levels_in_crop"] = [float((q[crop] == k).mean()) for k in range(4)]
    comps = {}
    for k in range(4):
        lab, n = label(q == k)
        sizes = np.bincount(lab.ravel())[1:]
        comps[k] = dict(n_total=int(n), n_ge_0p1pct=int((sizes >= 0.001*env_area).sum()),
                        n_ge_0p5pct=int((sizes >= 0.005*env_area).sum()),
                        largest_pct_env=float(sizes.max()/env_area*100) if n else 0)
    r["components"] = comps
    top = q == 3
    r["top_level_px"] = int(top.sum())
    r["top_level_in_mask_frac"] = float((top & REG["mask"]).sum()/max(1, top.sum()))
    r["top_level_in_mask_or_maw_frac"] = float((top & (REG["mask"] | REG["maw"])).sum()/max(1, top.sum()))
    # top level outside mask/maw: components > 0.5% env
    lab, n = label(top & ~REG["mask"]); sizes = np.bincount(lab.ravel())[1:]
    r["top_level_outside_mask_comps_ge_0p5pct"] = int((sizes >= 0.005*env_area).sum())
    # figure-only (lit mask) value shares
    fm = figure_mask(g, wall)
    r["figure_area_pct_env"] = float(fm.sum()/env_area*100)
    r["figure_level_shares"] = [float((q[fm] == k).mean()) for k in range(4)]
    # mid-tone (level 1+2) mass grouping: share of mid-tone px in the 3 largest mid-tone components
    lit = (q >= 2); lab, n = label(lit); sizes = np.sort(np.bincount(lab.ravel())[1:])[::-1]
    r["litflesh_n_components"] = int(n)
    r["litflesh_n_ge_0p5pct_env"] = int((sizes >= 0.005*env_area).sum())
    r["litflesh_share_in_top3_components"] = float(sizes[:3].sum()/sizes.sum()) if n else 0
    r["litflesh_top5_pct_env"] = [round(float(x/env_area*100), 2) for x in sizes[:5]]
    fg = (q >= 1); lab, n = label(fg); sizes = np.sort(np.bincount(lab.ravel())[1:])[::-1]
    r["shaded_or_lit_n_ge_0p5pct_env"] = int((sizes >= 0.005*env_area).sum())
    res[tag] = r
    pal = np.array([[12, 10, 10], [80, 66, 56], [165, 135, 105], [250, 240, 215]], np.uint8)
    if tag == "raw": raw_q = q.copy()
    if tag == "acuity3m": ac_q = q.copy()
    if tag == "squint": sq_q = q.copy(); sq_pal = pal
dump("d3_value.json", res)
print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "components"} for k, v in res.items()}, indent=1))
print({k: v["components"] for k, v in res.items()})
from PIL import Image, ImageDraw
tiles = []
for t, q in [("V4 raw (4 wall-relative levels)", raw_q), ("V4 after 3 m acuity blur", ac_q), ("V4 after squint", sq_q)]:
    im = Image.fromarray(sq_pal[q][100:860, 190:1010]).resize((410, 380)); tiles.append((t, im))
sheet = Image.new("RGB", (3*410+20, 400), (20, 20, 20)); d = ImageDraw.Draw(sheet)
for i, (t, im) in enumerate(tiles):
    sheet.paste(im, (i*410+10, 18)); d.text((i*410+12, 4), t, fill=(235, 235, 235))
print("kb", save(sheet, "d3_value_sheet.png"))
