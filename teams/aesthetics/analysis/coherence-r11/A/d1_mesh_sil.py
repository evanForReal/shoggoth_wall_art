"""Orthographic front silhouette of the H mesh (build/H.npz), x right y up, 1.5 mm/px, 640x640 (+-480 mm)."""
from common import *
from PIL import ImageDraw
z = np.load(os.path.join(ROOT, "teams/cad/composition_r11/build/H.npz"))
v, f = z["v"], z["f"]
print("verts", v.shape, "x", v[:,0].min(), v[:,0].max(), "y", v[:,1].min(), v[:,1].max(), "z", v[:,2].min(), v[:,2].max())
S = 1.5; N = 640; c = N/2
px = (v[:,0]/S + c); py = (c - v[:,1]/S)
im = Image.new("L", (N, N), 0); d = ImageDraw.Draw(im)
for tri in f:
    d.polygon([(px[i], py[i]) for i in tri], fill=255)
m = np.asarray(im) > 127
m = ndi.binary_closing(m, iterations=1)
np.save(os.path.join(OUT, "mesh_sil.npy"), m)
print("area px", m.sum(), "mm2", m.sum()*S*S)
# depth-banded relief map: z-buffer by painter's order (sort faces by mean z ascending)
zb = np.zeros((N, N), np.float32)
order = np.argsort(v[f][:,:,2].mean(1))
im2 = Image.new("F", (N, N), 0); d2 = ImageDraw.Draw(im2)
for k in order:
    tri = f[k]; zz = float(v[tri,2].mean())
    d2.polygon([(px[i], py[i]) for i in tri], fill=zz)
zb = np.asarray(im2); np.save(os.path.join(OUT, "mesh_depth.npy"), zb)
print("depth range", zb[m].min(), zb[m].max())
save(m*255, "d1_mesh_silhouette.png")
