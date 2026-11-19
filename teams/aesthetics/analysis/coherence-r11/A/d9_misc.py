"""Palette / accent clusters, mask flatness, shelf rivals."""
from common import *
from regions import *
import colorsys
from scipy.ndimage import label, gaussian_filter
rgb = load_rgb(); g = gray(rgb); wall = wall_fit(g)
fm = ndi.binary_dilation(figure_mask(g, wall, thr=8), iterations=2)
mx = rgb.max(-1); mn = rgb.min(-1); sat = (mx-mn)/np.maximum(mx, 1)
res = {}
res["figure_sat_median"] = float(np.median(sat[fm])); res["figure_sat_p95"] = float(np.percentile(sat[fm], 95))
acc = fm & (sat > 0.55) & (mx > 90)               # saturated red/orange/yellow accents (veined eyes, iris)
white = fm & (g > 175) & ~REG["mask"] & ~REG["maw"]      # white eye beads outside mask/maw
for nm, a in (("saturated", acc), ("white_beads", white)):
    dil = ndi.binary_dilation(a, iterations=14); lab, n = label(dil)
    cl = []
    for i in range(1, n+1):
        ys, xs = np.nonzero((lab == i) & a)
        if len(ys) < 6: continue
        cl.append(dict(cx=int(xs.mean()), cy=int(ys.mean()), px=int(len(ys))))
    cl.sort(key=lambda d: -d["px"]); res[nm+"_clusters"] = cl[:10]
res["accent_cluster_count_ge_40px"] = int(sum(1 for c in res.get("saturated_clusters", []) if c["px"] >= 40))
tot = sum(c["px"] for c in res["saturated_clusters"]) or 1
res["saturated_px_share_head_patch_region"] = float(sum(c["px"] for c in res["saturated_clusters"] if 600 < c["cx"] < 720 and c["cy"] < 330)/tot)
# mask flatness: luminance std on the mask face excluding the carved features (pixels within 18% of the median)
m = REG["mask"]; med = np.median(g[m]); face = m & (np.abs(g-med) < 0.18*med)
res["mask_face_median"] = float(med); res["mask_face_std"] = float(g[face].std()); res["mask_face_cv"] = float(g[face].std()/med)
fl = fm & ~m & (g > 70) & (g < 160)
res["flesh_lit_std"] = float(g[fl].std()); res["flesh_lit_median"] = float(np.median(g[fl]))
# mask vs flesh value ratio, and mask vs wall
res["mask_over_flesh_lum"] = float(med/np.median(g[fl])); res["mask_over_wall_lum"] = float(med/np.median(wall))
# shelf lips p90
for nm in ("shelf_UL", "shelf_UR", "shelf_LL"):
    r = REG[nm] & fm; res[nm+"_lip_p90"] = float(np.percentile(g[r], 90)); res[nm+"_median"] = float(np.median(g[r]))
res["limb_median_lum_(root_tangle)"] = float(np.median(g[REG["root_tangle"] & fm & (g > wall+12)]))
dump("d9_misc.json", res); print(json.dumps(res, indent=1))
