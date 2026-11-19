"""Shared helpers for coherence-r11 A diagnostics. Run: python3 -I <script> from this directory."""
import os, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../../../.."))
SRC = os.path.join(ROOT, "teams/cad/composition_r11/renders/study_H_front.png")  # 1200x900 clean front render
OUT = HERE

# ASSUMPTION (stated in REPORT.md): piece bbox width (shelf tip to shelf tip, 780 px measured)
# = 914 mm envelope, so 1 px = 1.17 mm. Viewing distance 3 m: 1 px = 1.17/3000 rad = 1.34 arcmin.
PX_MM = 914.0 / 780.0
def arcmin_to_px(am, dist_m=3.0):
    return am / 60.0 * np.pi / 180.0 * dist_m * 1000.0 / PX_MM

def load_rgb():
    return np.asarray(Image.open(SRC).convert("RGB"), float)

def gray(rgb):
    return rgb @ np.array([0.2126, 0.7152, 0.0722])

def wall_fit(g, fig_hint=None):
    """Quadratic surface fit to the wall luminance using pixels outside an (iteratively grown) figure mask."""
    h, w = g.shape
    yy, xx = np.mgrid[0:h, 0:w]
    X = np.stack([np.ones_like(xx), xx, yy, xx*xx, xx*yy, yy*yy], -1).reshape(-1, 6).astype(float)
    X[:, 1:] /= np.array([w, h, w*w, w*h, h*h])
    use = np.ones(h*w, bool)
    # exclude centre box initially
    box = np.zeros((h, w), bool); box[100:860, 190:1010] = True
    use &= ~box.ravel()
    for _ in range(4):
        c, *_ = np.linalg.lstsq(X[use], g.ravel()[use], rcond=None)
        wall = (X @ c).reshape(h, w)
        use = (np.abs(g - wall).ravel() < 6) | (~box.ravel() & (np.abs(g-wall).ravel() < 12))
        use &= ~box.ravel()
    return wall

def figure_mask(g, wall, thr=14):
    """Figure = brighter than the fitted wall by thr levels; closing; remove specks < 30 px."""
    m = (g - wall) > thr
    m = ndi.binary_closing(m, iterations=2)
    lab, n = ndi.label(m)
    sizes = ndi.sum(m, lab, range(1, n+1))
    keep = np.zeros(n+1, bool); keep[1:] = sizes >= 30
    return keep[lab]

def save(img, name, maxkb=1000):
    p = os.path.join(OUT, name)
    if isinstance(img, np.ndarray):
        img = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    img.save(p, optimize=True)
    Image.open(p).verify()
    kb = os.path.getsize(p) / 1024
    assert kb <= maxkb, (name, kb)
    return kb

def dump(name, d):
    with open(os.path.join(OUT, name), "w") as f:
        json.dump(d, f, indent=1)
