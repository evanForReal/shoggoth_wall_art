import sys, numpy as np
from PIL import Image
REF = np.asarray(Image.open('/home/user/shoggoth_wall_art/teams/aesthetics/analysis/composition_gate/c01_mask_envelope.png')) > 127
def env(m):
    ys, xs = np.where(m); m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]; h, w = m.shape; s = max(h, w)
    sq = np.zeros((s, s), bool); sq[(s - h) // 2:(s - h) // 2 + h, (s - w) // 2:(s - w) // 2 + w] = m
    return np.asarray(Image.fromarray(sq.astype(np.uint8) * 255).resize((512, 512), Image.NEAREST)) > 127
def iou(sil):
    a = env(sil.T[::-1]); return float((a & REF).sum() / (a | REF).sum())
if __name__ == '__main__':
    for s in sys.argv[1:]: print(s, round(iou(np.load(f'build/{s}_sil.npy')), 3))
