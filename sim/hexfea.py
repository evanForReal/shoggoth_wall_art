"""Voxel-hex (trilinear Q1) linear-elastic FEA with numpy/scipy sparse.

Why voxel-hex and not tet: no mesher (gmsh) is installed; the winding raster in sim.voxel
gives a robust, cavity-correct occupancy for any closed mesh, and cubic hex elements are
aspect-ratio 1 so Q1 locking is limited. Cost: staircase boundary (area/I error O(h)); validated
in sim/VALIDATION.md. Units: mm, N, MPa, tonne (rho in t/mm^3), g = 9810 mm/s^2.
"""
from __future__ import annotations
import time
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.spatial import cKDTree

G = 9810.0
OFFS = np.array([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)])
XI = 2.0 * OFFS - 1.0


def _D(E, nu):
    lam = E * nu / ((1 + nu) * (1 - 2 * nu)); mu = E / (2 * (1 + nu))
    D = np.zeros((6, 6))
    D[:3, :3] = lam
    D[0, 0] = D[1, 1] = D[2, 2] = lam + 2 * mu
    D[3, 3] = D[4, 4] = D[5, 5] = mu
    return D


def _B(xi, eta, zeta, h):
    dN = np.zeros((8, 3))
    for i in range(8):
        a, b, c = XI[i]
        dN[i] = [a * (1 + eta * b) * (1 + zeta * c), b * (1 + xi * a) * (1 + zeta * c), c * (1 + xi * a) * (1 + eta * b)]
    dN = dN / 8.0 * (2.0 / h)
    B = np.zeros((6, 24))
    for i in range(8):
        dx, dy, dz = dN[i]
        B[0, 3 * i] = dx; B[1, 3 * i + 1] = dy; B[2, 3 * i + 2] = dz
        B[3, 3 * i + 1] = dz; B[3, 3 * i + 2] = dy
        B[4, 3 * i] = dz; B[4, 3 * i + 2] = dx
        B[5, 3 * i] = dy; B[5, 3 * i + 1] = dx
    return B


def ke_unit(h, nu):
    D = _D(1.0, nu); g = 1 / np.sqrt(3); K = np.zeros((24, 24))
    for a in (-g, g):
        for b in (-g, g):
            for c in (-g, g):
                B = _B(a, b, c, h); K += B.T @ D @ B * (h / 2) ** 3
    return K


class HexModel:
    def __init__(self, occ, grid, E, nu, efac=None, rho=None, rhofac=None):
        """occ bool (nx,ny,nz); efac/rhofac per-voxel scale arrays (same shape) or None; E MPa; rho t/mm^3."""
        t0 = time.time()
        self.grid = grid; self.h = grid.pitch; self.E = E; self.nu = nu; self.rho = rho
        nx, ny, nz = occ.shape
        e = np.argwhere(occ)
        self.eidx = e
        self.ne = len(e)
        self.efac = np.ones(self.ne) if efac is None else efac[occ]
        self.rhofac = np.ones(self.ne) if rhofac is None else rhofac[occ]
        sy, sz = (ny + 1) * (nz + 1), (nz + 1)
        flat = np.empty((self.ne, 8), np.int64)
        for i, o in enumerate(OFFS):
            flat[:, i] = (e[:, 0] + o[0]) * sy + (e[:, 1] + o[1]) * sz + (e[:, 2] + o[2])
        un, inv = np.unique(flat, return_inverse=True)
        self.conn = inv.reshape(self.ne, 8)
        self.nn = len(un)
        ix = un // sy; iy = (un % sy) // sz; iz = un % sz
        self.xyz = grid.origin + np.stack([ix, iy, iz], 1) * self.h
        self.edof = (self.conn[:, :, None] * 3 + np.arange(3)).reshape(self.ne, 24)
        self.ndof = 3 * self.nn
        self.Ke = ke_unit(self.h, nu) * E
        self.B0 = _B(0, 0, 0, self.h)
        self.D = _D(E, nu)
        self.K = self._assemble()
        self.vol = self.h ** 3
        self.t_build = time.time() - t0

    def _assemble(self, chunk=40000):
        K = None
        ke = self.Ke.ravel()
        for s in range(0, self.ne, chunk):
            ed = self.edof[s:s + chunk]
            rows = np.repeat(ed, 24, axis=1).ravel()
            cols = np.tile(ed, (1, 24)).ravel()
            vals = (self.efac[s:s + chunk, None] * ke[None, :]).ravel()
            Kc = sp.coo_matrix((vals, (rows, cols)), shape=(self.ndof, self.ndof)).tocsr()
            K = Kc if K is None else K + Kc
        return K.tocsr()

    # ---- supports / loads
    def nodes_where(self, fn):
        return np.nonzero(fn(self.xyz))[0]

    def set_fixed(self, nodes, dofs=(0, 1, 2)):
        fixed = np.zeros(self.ndof, bool)
        for d in dofs:
            fixed[np.asarray(nodes) * 3 + d] = True
        self.fixed = fixed
        self.free = np.nonzero(~fixed)[0]
        self._fac = None

    def factor(self, direct_limit=12_000, verbose=False):
        t0 = time.time()
        fx = self.fixed
        self.method = "splu" if len(self.free) <= direct_limit else "amg-cg"
        if self.method == "splu":
            Kff = self.K[self.free][:, self.free].tocsc()
            self.Kff = Kff
            self._fac = spla.splu(Kff, permc_spec="COLAMD")
        else:
            from .amg import SAAMG
            Dm = sp.diags((~fx).astype(float))
            Kb = (Dm @ self.K @ Dm).tocsr() + sp.diags(fx * self.K.diagonal().mean())
            self.Kb = Kb
            self.amg = SAAMG(Kb, self.xyz, fixed=fx, verbose=verbose)
            self._Mop = self.amg.operator()
        self.t_factor = time.time() - t0

    def solve(self, f, tol=1e-9, maxiter=2000):
        if getattr(self, "method", None) is None:
            self.factor()
        info = {}
        if self.method == "splu":
            uf = self._fac.solve(f[self.free])
            u = np.zeros(self.ndof); u[self.free] = uf
            res = np.linalg.norm(self.Kff @ uf - f[self.free]) / max(np.linalg.norm(f[self.free]), 1e-30)
            info["iters"] = 0
        else:
            cnt = [0]
            def cb(_): cnt[0] += 1
            ff = f.copy(); ff[self.fixed] = 0.0
            u, ec = spla.cg(self.Kb, ff, rtol=tol, maxiter=maxiter, M=self._Mop, callback=cb)
            res = np.linalg.norm(self.Kb @ u - ff) / max(np.linalg.norm(ff), 1e-30)
            info.update(iters=cnt[0], exit=int(ec))
        info["rel_res"] = float(res)
        self.last_info = info
        return u, info

    def reactions(self, u, f):
        return (self.K @ u - f)[self.fixed]

    def nodes_near(self, pt, radius, min_nodes=8):
        if not hasattr(self, "_tree"):
            self._tree = cKDTree(self.xyz)
        idx = self._tree.query_ball_point(pt, radius)
        if len(idx) < min_nodes:
            idx = self._tree.query(pt, k=min_nodes)[1]
        return np.asarray(idx)

    def point_load(self, force, pt, radius):
        f = np.zeros(self.ndof)
        nodes = self.nodes_near(pt, radius)
        for d in range(3):
            f[nodes * 3 + d] += force[d] / len(nodes)
        return f, nodes

    def elem_mass(self):
        return self.rho * self.vol * self.rhofac     # tonne

    def gravity_load(self, extra_mass_nodes=None):
        """body weight (-Z) lumped to nodes; extra_mass_nodes: (node_idx array, mass array in tonne)."""
        f = np.zeros(self.ndof)
        m8 = np.repeat((self.elem_mass() / 8.0)[:, None], 8, axis=1)
        np.add.at(f, self.conn.ravel() * 3 + 2, -(m8.ravel()) * G)
        if extra_mass_nodes is not None:
            nidx, m = extra_mass_nodes
            np.add.at(f, nidx * 3 + 2, -m * G)
        return f

    def lumped_mass(self, extra_mass_nodes=None):
        m = np.zeros(self.nn)
        np.add.at(m, self.conn.ravel(), np.repeat(self.elem_mass() / 8.0, 8))
        if extra_mass_nodes is not None:
            np.add.at(m, extra_mass_nodes[0], extra_mass_nodes[1])
        return m

    # ---- results
    def stress(self, u):
        ue = u[self.edof]                       # (ne,24)
        eps = ue @ self.B0.T
        sig = (eps @ self.D.T) * self.efac[:, None]
        return sig                              # (ne,6) xx yy zz yz zx xy

    @staticmethod
    def von_mises(s):
        sx, sy, sz, tyz, tzx, txy = s.T
        return np.sqrt(0.5 * ((sx - sy) ** 2 + (sy - sz) ** 2 + (sz - sx) ** 2) + 3 * (tyz ** 2 + tzx ** 2 + txy ** 2))

    @staticmethod
    def normal_shear(s, n):
        """traction decomposition on plane with unit normal n: (sigma_n, tau)."""
        sx, sy, sz, tyz, tzx, txy = s.T
        S = np.empty((len(s), 3, 3))
        S[:, 0, 0] = sx; S[:, 1, 1] = sy; S[:, 2, 2] = sz
        S[:, 1, 2] = S[:, 2, 1] = tyz; S[:, 0, 2] = S[:, 2, 0] = tzx; S[:, 0, 1] = S[:, 1, 0] = txy
        t = S @ n
        sn = t @ n
        tau = np.linalg.norm(t - sn[:, None] * n, axis=1)
        return sn, tau

    def elem_centers(self):
        return self.grid.origin + (self.eidx + 0.5) * self.h

    def modes(self, mass_nodes, k=4, guess=None, maxiter=300):
        """lowest k natural frequencies (Hz) of K u = w^2 M u; lumped M (tonne)."""
        if self.method == "splu":
            m = np.repeat(mass_nodes, 3)[self.free]
            fac = self._fac
            OPinv = spla.LinearOperator(self.Kff.shape, matvec=fac.solve)
            w, v = spla.eigsh(self.Kff, k=k, M=sp.diags(m), sigma=0, which="LM", OPinv=OPinv)
            return np.sort(np.sqrt(np.abs(w)) / (2 * np.pi)), "shift-invert (direct)"
        m = np.repeat(mass_nodes, 3).copy()
        m[self.fixed] = m[~self.fixed].mean() * 1e3     # push Dirichlet pseudo-modes away
        rng = np.random.default_rng(0)
        X = guess if guess is not None else rng.standard_normal((self.ndof, k))
        if X.shape[1] < k:
            X = np.hstack([X, rng.standard_normal((self.ndof, k - X.shape[1]))])
        X = X.copy(); X[self.fixed] = 0.0
        X = X + 1e-3 * rng.standard_normal(X.shape) * (~self.fixed)[:, None] * np.abs(X).max()
        X /= np.linalg.norm(X, axis=0, keepdims=True)
        w, v, hist = spla.lobpcg(self.Kb, X, B=sp.diags(m), M=self._Mop, largest=False, tol=1e-5, maxiter=maxiter, retResidualNormsHistory=True)
        w = np.sort(np.abs(w))
        conv = f"amg-lobpcg(iters={len(hist)}, last_resnorm={float(np.max(hist[-1])):.1e})"
        return np.sqrt(w) / (2 * np.pi), conv
