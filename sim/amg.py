"""Smoothed-aggregation AMG preconditioner (numpy/scipy only) with rigid-body-mode near-nullspace.

Needed because no direct sparse solver beyond SuperLU is available and Jacobi-PCG stalls on thin-shell voxel models.
Used as a CG preconditioner (symmetric V-cycle, damped-Jacobi smoother, dense Cholesky on the coarsest level).
Variable block sizes per coarse node are supported (rank-deficient aggregates keep rank<6 columns).
"""
from __future__ import annotations
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
import scipy.linalg as sla


def rbm(xyz):
    n = len(xyz); B = np.zeros((3 * n, 6))
    x, y, z = xyz.T
    B[0::3, 0] = 1; B[1::3, 1] = 1; B[2::3, 2] = 1
    B[1::3, 3] = -z; B[2::3, 3] = y          # rot x
    B[0::3, 4] = z; B[2::3, 4] = -x          # rot y
    B[0::3, 5] = -y; B[1::3, 5] = x          # rot z
    return B


def _strength(A, dof2node, nnode, theta):
    C = A.tocoo()
    rn = dof2node[C.row]; cn = dof2node[C.col]
    G = sp.coo_matrix((C.data ** 2, (rn, cn)), shape=(nnode, nnode)).tocsr()
    G.sum_duplicates()
    d = np.sqrt(G.diagonal())
    G = G.tocoo()
    val = np.sqrt(G.data)
    keep = val >= theta * np.sqrt(d[G.row] * d[G.col])
    keep |= (G.row == G.col)
    return sp.csr_matrix((np.ones(keep.sum()), (G.row[keep], G.col[keep])), shape=(nnode, nnode))


def _aggregate(S):
    n = S.shape[0]
    ip, ix = S.indptr, S.indices
    agg = -np.ones(n, np.int64); cnt = 0
    for i in range(n):
        if agg[i] >= 0: continue
        nb = ix[ip[i]:ip[i + 1]]
        if (agg[nb] < 0).all():
            agg[nb] = cnt; cnt += 1
    for i in range(n):
        if agg[i] >= 0: continue
        nb = ix[ip[i]:ip[i + 1]]
        a = agg[nb]; a = a[a >= 0]
        if len(a):
            agg[i] = a[0]
    for i in range(n):
        if agg[i] < 0:
            agg[i] = cnt; cnt += 1
    return agg, cnt


class SAAMG:
    def __init__(self, A, xyz, fixed=None, coarse_max=1200, theta=0.05, max_levels=10, smooth_omega=None, nsweeps=2, verbose=False):
        A = A.tocsr(); n = A.shape[0]
        self.levels = []
        B = rbm(xyz)
        if fixed is not None:
            B[fixed] = 0.0   # Dirichlet dofs carry no coarse space
        dof2node = np.arange(n) // 3
        nnode = n // 3
        th = theta
        for lev in range(max_levels):
            n = A.shape[0]
            d = A.diagonal()
            Dinv = 1.0 / d
            rho = self._rho(A, Dinv)
            om = (4.0 / 3.0) / rho
            if n <= coarse_max or lev == max_levels - 1:
                Ad = A.toarray() + 1e-12 * np.eye(n) * d.mean()
                self.levels.append({"A": A, "Dinv": Dinv, "om": om, "cho": sla.cho_factor(Ad)})
                break
            S = _strength(A, dof2node, nnode, th)
            agg, nagg = _aggregate(S)
            # local SVD per aggregate
            dagg = agg[dof2node]
            order = np.argsort(dagg, kind="stable")
            bounds = np.searchsorted(dagg[order], np.arange(nagg + 1))
            rows = []; cols = []; vals = []; Bc = []; coarse_node = []
            c0 = 0
            for a in range(nagg):
                idx = order[bounds[a]:bounds[a + 1]]
                if len(idx) == 0:
                    continue
                Bl = B[idx]
                U, Sg, Vt = np.linalg.svd(Bl, full_matrices=False)
                r = int((Sg > 1e-8 * max(Sg[0], 1e-30)).sum()) if Sg[0] > 0 else 0
                if r == 0:
                    continue
                Q = U[:, :r]
                rows.append(np.repeat(idx, r)); cols.append(np.tile(np.arange(c0, c0 + r), len(idx)))
                vals.append(Q.ravel())
                Bc.append(Sg[:r, None] * Vt[:r]); coarse_node.append(np.full(r, a))
                c0 += r
            nc = c0
            if nc >= n * 0.9:
                Ad = A.toarray() + 1e-12 * np.eye(n) * d.mean()
                self.levels.append({"A": A, "Dinv": Dinv, "om": om, "cho": sla.cho_factor(Ad)})
                break
            Pt = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, nc))
            P = Pt - sp.diags(om * Dinv) @ (A @ Pt)
            P = P.tocsr()
            self.levels.append({"A": A, "Dinv": Dinv, "om": om, "P": P})
            if verbose:
                print(f"  amg level {lev}: n={n} nnz={A.nnz} -> nc={nc} aggs={nagg}", flush=True)
            A = (P.T @ A @ P).tocsr(); A.sum_duplicates()
            B = np.vstack(Bc)
            dof2node = np.concatenate(coarse_node)
            # make dof2node contiguous node ids for coarse level (aggregate ids)
            nnode = nagg
            th = th * 0.7
        self.nsweeps = nsweeps

    @staticmethod
    def _rho(A, Dinv, it=12):
        x = np.random.default_rng(0).standard_normal(A.shape[0])
        for _ in range(it):
            x = Dinv * (A @ x); x /= np.linalg.norm(x)
        return float(np.linalg.norm(Dinv * (A @ x)) / np.linalg.norm(x)) * 1.1

    def _vcycle(self, l, b):
        L = self.levels[l]
        if "cho" in L:
            return sla.cho_solve(L["cho"], b)
        A, Dinv, om, P = L["A"], L["Dinv"], L["om"], L["P"]
        x = om * Dinv * b
        for _ in range(self.nsweeps - 1):
            x = x + om * Dinv * (b - A @ x)
        r = b - A @ x
        e = self._vcycle(l + 1, P.T @ r)
        x = x + P @ e
        for _ in range(self.nsweeps):
            x = x + om * Dinv * (b - A @ x)
        return x

    def operator(self):
        n = self.levels[0]["A"].shape[0]
        return spla.LinearOperator((n, n), matvec=lambda b: self._vcycle(0, b), dtype=float)
