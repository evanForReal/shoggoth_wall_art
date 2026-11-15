"""Deterministic procedural noise (random Fourier features) and helpers. Pure numpy."""
import numpy as np


def _rng(seed, salt):
    return np.random.default_rng(np.random.SeedSequence([int(seed) & 0xFFFFFFFF, int(salt) & 0xFFFFFFFF]))


def fourier_noise(P, seed, salt, freq, n_feat=32, aniso=(1.0, 1.0, 1.0)):
    """Approx. Gaussian field, unit variance, spatial wavelength ~ 1/freq (mm^-1). aniso scales axes (freq mult)."""
    r = _rng(seed, salt)
    k = r.normal(size=(n_feat, 3))
    k /= np.linalg.norm(k, axis=1, keepdims=True)
    k *= 2 * np.pi * freq * r.uniform(0.7, 1.3, size=(n_feat, 1))
    k *= np.asarray(aniso)[None, :]
    ph = r.uniform(0, 2 * np.pi, size=n_feat)
    out = np.zeros(len(P))
    for i in range(0, n_feat, 8):  # chunk to bound memory
        out += np.cos(P @ k[i:i + 8].T + ph[i:i + 8]).sum(axis=1)
    return out * np.sqrt(2.0 / n_feat)


def fbm(P, seed, salt, freq, octaves=3, gain=0.5, lac=2.0, aniso=(1, 1, 1)):
    tot = np.zeros(len(P)); amp = 1.0; norm = 0.0
    for o in range(octaves):
        tot += amp * fourier_noise(P, seed, salt + 17 * o, freq * lac ** o, aniso=aniso)
        norm += amp ** 2; amp *= gain
    return tot / np.sqrt(norm)


def smooth(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0, 1)
    return t * t * (3 - 2 * t)


def cells(P, seed, salt, size, jitter=0.9):
    """Jittered-grid Voronoi: returns F1, F2, cell_id_random in [0,1]."""
    from scipy.spatial import cKDTree
    r = _rng(seed, salt)
    lo = P.min(0) - 2 * size; hi = P.max(0) + 2 * size
    g = [np.arange(lo[i], hi[i], size) for i in range(3)]
    G = np.stack(np.meshgrid(*g, indexing="ij"), -1).reshape(-1, 3)
    pts = G + (r.uniform(-jitter / 2, jitter / 2, size=G.shape) * size)
    rid = r.uniform(0, 1, size=len(pts))
    d, i = cKDTree(pts).query(P, k=2)
    return d[:, 0], d[:, 1], rid[i[:, 0]]


def blobs(P, seed, salt, spacing, radius):
    """Sum-of-gaussian bumps at jittered points; returns [0,1]."""
    from scipy.spatial import cKDTree
    r = _rng(seed, salt)
    lo = P.min(0) - 2 * spacing; hi = P.max(0) + 2 * spacing
    g = [np.arange(lo[i], hi[i], spacing) for i in range(3)]
    G = np.stack(np.meshgrid(*g, indexing="ij"), -1).reshape(-1, 3)
    pts = G + r.uniform(-0.5, 0.5, size=G.shape) * spacing
    keep = r.uniform(size=len(pts)) < 0.55
    pts = pts[keep]; amp = r.uniform(0.4, 1.0, size=len(pts))
    tree = cKDTree(pts)
    d, i = tree.query(P, k=3, distance_upper_bound=3 * radius)
    out = np.zeros(len(P))
    for j in range(3):
        ok = np.isfinite(d[:, j])
        out[ok] = np.maximum(out[ok], amp[i[ok, j]] * np.exp(-(d[ok, j] / radius) ** 2))
    return out
