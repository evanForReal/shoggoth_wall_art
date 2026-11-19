"""Named regions in render px (1200x900 study_H_front.png), hand-placed from the render. Used by d2..d6."""
import numpy as np
H, W = 900, 1200
yy, xx = np.mgrid[0:H, 0:W]
def circ(cx, cy, r): return (xx-cx)**2 + (yy-cy)**2 <= r*r
def ell(cx, cy, a, b, ang=0.0):
    t = np.deg2rad(ang); dx, dy = xx-cx, yy-cy
    u = dx*np.cos(t) + dy*np.sin(t); v = -dx*np.sin(t) + dy*np.cos(t)
    return (u/a)**2 + (v/b)**2 <= 1
def box(x0, y0, x1, y1):
    m = np.zeros((H, W), bool); m[y0:y1, x0:x1] = True; return m
MASK_C = (572, 238); MASK_R = 88
REG = {
  "mask":      circ(*MASK_C, MASK_R),
  "maw":       ell(618, 465, 68, 140, -4),
  "eye_patch": ell(668, 235, 36, 85) & ~circ(*MASK_C, MASK_R),
  "shoulder_eyes": ell(490, 400, 55, 75),
  "shelf_UL":  box(205, 200, 430, 290),
  "shelf_UR":  box(765, 320, 995, 400),
  "shelf_LL":  box(205, 605, 445, 695),
  "root_tangle": box(230, 610, 990, 845) & ~box(205, 605, 445, 695),
  "neck_lattice": box(505, 322, 612, 398) & ~circ(*MASK_C, MASK_R),
  "whip_UR":   box(850, 380, 995, 550),
}
