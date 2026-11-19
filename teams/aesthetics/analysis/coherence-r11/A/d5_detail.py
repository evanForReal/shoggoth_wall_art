"""Edge / detail density heatmap. Detail = local energy of the high-pass (g - gauss(g, 2 px)) combined with Sobel magnitude; smoothed at sigma 18 px (21 mm)."""
from common import *
from regions import *
from scipy.ndimage import gaussian_filter, sobel
rgb = load_rgb(); g = gray(rgb); wall = wall_fit(g)
fm = figure_mask(g, wall, thr=8)            # lenient so shaded flesh counts as figure
fm = ndi.binary_dilation(fm, iterations=3)
gs = gaussian_filter(g, 1.0)
gx, gy = sobel(gs, 1), sobel(gs, 0); mag = np.hypot(gx, gy)
# normalise by local mean luminance so dark-but-textured flesh is not hidden by the mask's absolute brightness
loc = gaussian_filter(g, 12) + 10
hp = (g - gaussian_filter(g, 2.0))
energy = gaussian_filter(np.abs(hp)/loc, 1.5)
dens = gaussian_filter(energy*fm, 18)/np.maximum(gaussian_filter(fm.astype(float), 18), 1e-3)
dens *= fm
# also raw Sobel (absolute contrast, what the eye catches) smoothed
dens_abs = gaussian_filter(mag*fm, 18)/np.maximum(gaussian_filter(fm.astype(float), 18), 1e-3)*fm
res = {}
tot_rel = energy[fm].sum(); tot_abs = mag[fm].sum(); A = fm.sum()
for nm, r in REG.items():
    rr = r & fm
    res[nm] = dict(area_share_of_figure=float(rr.sum()/A), rel_detail_share=float(energy[rr].sum()/tot_rel),
                   abs_edge_share=float(mag[rr].sum()/tot_abs),
                   rel_density_vs_figure_mean=float(energy[rr].mean()/energy[fm].mean()),
                   abs_density_vs_figure_mean=float(mag[rr].mean()/mag[fm].mean()))
# concentration: share of detail energy in the densest 10% / 25% of figure area
for key, arr in (("rel", energy), ("abs", mag)):
    v = np.sort(arr[fm])[::-1]; cs = np.cumsum(v)/v.sum()
    res[f"top10pct_area_holds_{key}_share"] = float(cs[int(0.10*len(v))])
    res[f"top25pct_area_holds_{key}_share"] = float(cs[int(0.25*len(v))])
    # Gini
    vv = np.sort(arr[fm]); n = len(vv); res[f"gini_{key}"] = float((2*np.arange(1, n+1)-n-1).dot(vv)/(n*vv.sum()))
# where is the peak of the smoothed density maps?
for key, d in (("rel", dens), ("abs", dens_abs)):
    y, x = np.unravel_index(np.argmax(d), d.shape)
    nm = [k for k, r in REG.items() if r[y, x]]
    res[f"peak_{key}"] = dict(x=int(x), y=int(y), region=nm[0] if nm else "other")
    # area of figure where density >= 50% of peak (test 1.6: detail areas <= 50% of body)
    res[f"figure_frac_ge_50pct_of_peak_{key}"] = float(((d >= 0.5*d.max()) & fm).sum()/A)
    res[f"figure_frac_ge_70pct_of_peak_{key}"] = float(((d >= 0.7*d.max()) & fm).sum()/A)
    # rank: mean smoothed density per region normalised
dump("d5_detail.json", res)
print(json.dumps(res, indent=1))
def heat(d, vmax):
    t = np.clip(d/vmax, 0, 1)
    # black -> deep red -> orange -> yellow -> white
    r = np.clip(t*2.2, 0, 1); gg = np.clip(t*2.2-0.9, 0, 1); b = np.clip(t*2.5-1.9, 0, 1)
    return np.stack([r, gg, b], -1)*255
base = np.clip(g[..., None]*0.45, 0, 255)*np.ones(3)
tiles = []
from PIL import ImageDraw
crop = (slice(100, 860), slice(190, 1010))
for nm, d in (("relative detail density (high-pass / local lum)", dens), ("absolute edge density (Sobel)", dens_abs)):
    vmax = np.percentile(d[fm], 99.5)
    h = heat(d, vmax); alpha = (d > 0)[..., None]*0.78
    out = base*(1-alpha) + h*alpha
    im = Image.fromarray(np.clip(out[crop], 0, 255).astype(np.uint8)).resize((615, 570)); ImageDraw.Draw(im).text((6, 4), nm, fill=(255, 255, 255)); tiles.append(im)
sheet = Image.new("RGB", (1240, 570), (15, 15, 15)); sheet.paste(tiles[0], (0, 0)); sheet.paste(tiles[1], (625, 0))
print("kb", save(sheet, "d5_detail_heatmap.png"))
