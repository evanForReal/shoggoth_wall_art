"""Headless preview renderer: surface-sample z-buffer splat + lambert shading (numpy + matplotlib only)."""
import numpy as np
import trimesh

PALETTES = {
    "underlay": (0.62, 0.64, 0.68),
    "calcified_webbing": (0.80, 0.76, 0.66),
    "bone_crust": (0.86, 0.82, 0.72),
    "flowstone": (0.72, 0.60, 0.45),
    "rust_blister": (0.62, 0.30, 0.15),
    "mummified_ochre": (0.74, 0.55, 0.22),
    "assembly": (0.75, 0.72, 0.65),
}

VIEWS = {  # name: (view direction pointing from camera into scene, up)
    "iso": (np.array([-1.0, 0.8, -0.9]), np.array([0, 0, 1.0])),
    "top": (np.array([0, 0, -1.0]), np.array([1.0, 0, 0])),
    "side": (np.array([0, 1.0, 0]), np.array([0, 0, 1.0])),
    "front": (np.array([-1.0, 0, 0]), np.array([0, 0, 1.0])),
}


def _basis(vdir, up):
    f = vdir / np.linalg.norm(vdir)
    r = np.cross(f, up); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return r, u, f


def render(mesh, view="iso", color=(0.7, 0.7, 0.7), px=900, n_samples=1_200_000, seed=0, bounds=None):
    pts, fi = trimesh.sample.sample_surface(mesh, n_samples, seed=seed)
    nrm = mesh.face_normals[fi]
    r, u, f = _basis(*VIEWS[view])
    x = pts @ r; y = pts @ u; z = pts @ f
    b = bounds if bounds is not None else (np.array([x.min(), y.min()]), np.array([x.max(), y.max()]))
    lo, hi = b
    scale = (px - 20) / max(hi[0] - lo[0], hi[1] - lo[1])
    ix = ((x - lo[0]) * scale + 10).astype(int); iy = ((y - lo[1]) * scale + 10).astype(int)
    W = int((hi[0] - lo[0]) * scale + 20); H = int((hi[1] - lo[1]) * scale + 20)
    ok = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
    ix, iy, z, nrm = ix[ok], iy[ok], z[ok], nrm[ok]
    nrm = np.where(((nrm * f).sum(1) > 0)[:, None], -nrm, nrm)  # face camera
    order = np.argsort(-z)            # far first so near overwrites
    ix, iy, z, nrm = ix[order], iy[order], z[order], nrm[order]
    key = iy * W + ix
    zbuf = np.full(W * H, np.inf); np.minimum.at(zbuf, key, z)
    vis = z <= zbuf[key] + 0.6 * (1 / scale) * 3
    L1 = -(0.5 * f + 0.6 * u - 0.5 * r); L1 /= np.linalg.norm(L1)
    L2 = -f
    sh = 0.25 + 0.6 * np.clip((nrm * L1).sum(1), 0, 1) + 0.25 * np.clip((nrm * -f).sum(1) * -1, 0, 1)
    bg = np.array([0.08, 0.08, 0.09])
    img = np.ones((H * W, 3)) * bg
    col = np.clip(sh[:, None] * np.array(color), 0, 1)
    img[key[vis]] = col[vis]
    mask = np.zeros(H * W); mask[key[vis]] = 1
    img = img.reshape(H, W, 3); mask = mask.reshape(H, W)
    from scipy.ndimage import uniform_filter
    for _ in range(2):  # fill sampling gaps
        num = np.stack([uniform_filter(img[..., c] * mask, 3) for c in range(3)], -1)
        den = uniform_filter(mask, 3)[..., None]
        fill = (mask == 0) & (den[..., 0] > 0.34)
        img = np.where(fill[..., None], num / np.maximum(den, 1e-9), img)
        mask = np.where(fill, 1.0, mask)
    return img[::-1]


def sheet(meshes_colors, path, views=("iso", "top", "side"), title=None, px=700):
    """meshes_colors: list of (mesh, color). Renders each view with shared bounds, saves one PNG."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    allv = np.vstack([m.vertices for m, _ in meshes_colors])
    imgs = []
    for v in views:
        r, u, f = _basis(*VIEWS[v])
        lo = np.array([(allv @ r).min(), (allv @ u).min()]); hi = np.array([(allv @ r).max(), (allv @ u).max()])
        layer = None
        for (m, c) in meshes_colors:
            imgs_v = render(m, v, c, px=px, bounds=(lo, hi), n_samples=2_500_000)
            layer = imgs_v if layer is None else np.where((imgs_v.sum(-1, keepdims=True) > 0.26), imgs_v, layer)
        imgs.append(layer)
    fig, axs = plt.subplots(1, len(views), figsize=(5.2 * len(views), 5.2), dpi=110)
    for ax, im, v in zip(np.atleast_1d(axs), imgs, views):
        ax.imshow(im); ax.set_title(v, fontsize=9, color="w"); ax.axis("off")
    fig.patch.set_facecolor("#111111")
    if title:
        fig.suptitle(title, color="w", fontsize=10)
    fig.tight_layout(); fig.savefig(path, facecolor=fig.get_facecolor()); plt.close(fig)
