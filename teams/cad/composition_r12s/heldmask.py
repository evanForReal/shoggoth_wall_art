"""r12s fork of r12 heldmask (ball mask support: shape=ball ellipsoid sdf, pad_inset). Original docstring: r12 held mask: general frame (yaw / pitch / roll), root search, rod-cored holding tentacle (Structural mask-arm-v1.md S1-S10), separate mask part, three grip types.
mm; x right, y up, z out of the wall (gravity = -y). Everything generated from one dict G."""
import numpy as np
from engine import curve, ellipsoid, smin
ROD_D, BORE_D = 10.0, 10.4
PAD_R, PAD_LEN, FIL_K = 35.0, 38.0, 28.0
EMBED, MASK_BORE = 82.0, 44.0
SPIG_R, SPIG_L, FLAT = 20.0, 30.0, 16.0
BLOCK_R = 30.0
NDMIN = 0.50

def rotmat(yaw, pitch, roll):
    cy, sy, cp, sp, cr, sr = np.cos(yaw), np.sin(yaw), np.cos(pitch), np.sin(pitch), np.cos(roll), np.sin(roll)
    Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]]); Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]); Rz = np.array([[cr, -sr, 0], [sr, cr, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx

def hback(G, q): return G['rim'] + (G['dz'] - G['rim']) * np.sqrt(np.clip(1 - q * q, 0, 1))

def loc(G, X, Y, Z):
    P = np.stack([X - G['c3'][0], Y - G['c3'][1], Z - G['c3'][2]], -1); return P @ G['eu'], P @ G['ev'], P @ G['en']
def glob(G, u, v, w): return G['c3'] + u * G['eu'] + v * G['ev'] + w * G['en']

def mask_sdf_fn(G):
    R, dz, rim = G['R'], G['dz'], G['rim']
    if G['H'].get('shape') == 'ball':      # ellipsoid, semi-axes R, R, dz (rim = 0): first-order distance
        def efn(X, Y, Z):
            u, v, w = loc(G, X, Y, Z); q = np.sqrt((u / R) ** 2 + (v / R) ** 2 + (w / dz) ** 2) + 1e-9
            gr = np.sqrt((u / R ** 2) ** 2 + (v / R ** 2) ** 2 + (w / dz ** 2) ** 2) / q + 1e-9
            return (q - 1) / gr
        return efn
    def mfn(X, Y, Z):
        u, v, w = loc(G, X, Y, Z); q = np.sqrt((u / R) ** 2 + (v / R) ** 2); h = rim + (dz - rim) * np.sqrt(np.clip(1 - q * q, 0, 1)); return np.maximum((q - 1) * R, np.abs(w) - h) * 0.9
    return mfn

def disc_back_points(G, n=24):
    th = np.linspace(0, 2 * np.pi, n, endpoint=False); pts = [glob(G, 0, 0, -G['dz'])]
    for rr in (0.5, 0.8, 1.0):
        for t in th: u, v = rr * G['R'] * np.cos(t), rr * G['R'] * np.sin(t); pts.append(glob(G, u, v, -float(hback(G, rr))))
    return np.array(pts)

def make_frame(H, c, zm=0.0):
    Rm = rotmat(np.radians(H.get('yaw', 0)), np.radians(H.get('pitch', 0)), np.radians(H.get('roll', 0)))
    return dict(c3=np.array([c[0], c[1], zm], float), eu=Rm[:, 0], ev=Rm[:, 1], en=Rm[:, 2], R=H['D'] / 2, dz=H['dz'], rim=H['rim'], H=H)

REASONS = {}
def _rej(k): REASONS[k] = REASONS.get(k, 0) + 1
CLEAR_MARGIN = 4.0
def candidate(f, S, H, Gm, rx, ry, dt=None):
    z_e = float(f.surface_z(np.array([rx]), np.array([ry]))[0])
    if z_e < 62: _rej('z'); return None
    bu, bv = H['boss']; q = np.hypot(bu, bv) / Gm['R']; B0 = glob(Gm, bu, bv, -float(hback(Gm, q)))
    Rx = np.array([rx, ry, z_e]); d = (B0 - Rx) / np.linalg.norm(B0 - Rx); A = Rx - EMBED * d
    if A[2] - BLOCK_R * np.sqrt(max(1 - d[2] ** 2, 0)) < 0.5: _rej('Az'); return None
    if A[2] < 14.0: _rej('Az'); return None
    nd = float(d @ Gm['en'])
    if H.get('shape') == 'ball':      # P13 (Structural N1): rod vs the seat (ball back) normal at the boss, <= 35 deg
        wl = -float(hback(Gm, q)); a_, c_ = Gm['R'], Gm['dz']; nl = -np.array([bu / a_ ** 2, bu * 0 + bv / a_ ** 2, wl / c_ ** 2]); nl /= np.linalg.norm(nl)
        nseat = nl[0] * Gm['eu'] + nl[1] * Gm['ev'] + nl[2] * Gm['en']; nd = float(d @ nseat)
        if nd < np.cos(np.radians(H.get('seat_max_deg', 35.0))): _rej('seat'); return None
    elif nd < NDMIN: _rej('nd'); return None
    if H.get('shape') == 'ball': pass
    # block solid test (60 dia x 70 deep), points in the cylinder
    rng = np.random.default_rng(3); a = np.array([1.0, 0, 0]) if abs(d[0]) < 0.9 else np.array([0, 1.0, 0]); e1 = np.cross(d, a); e1 /= np.linalg.norm(e1); e2 = np.cross(d, e1)
    n = 500; s = rng.uniform(0, 58, n); r = BLOCK_R * 0.93 * np.sqrt(rng.uniform(0, 1, n)); ph = rng.uniform(0, 6.28, n); P = A[None] + s[:, None] * d[None] + (r * np.cos(ph))[:, None] * e1[None] + (r * np.sin(ph))[:, None] * e2[None]
    from engine import XS, YS, ZS, NX, NY, NZ, X0
    ii = np.clip(((P[:, 0] - X0) / 2.0).round().astype(int), 0, NX - 1); jj = np.clip(((P[:, 1] - X0) / 2.0).round().astype(int), 0, NY - 1); kk = np.clip(((P[:, 2] + 8) / 2.0).round().astype(int), 0, NZ - 1)
    sol = float((f.F[ii, jj, kk] < 0).mean())
    if sol < 0.97: _rej('solid'); return None
    # core test: everything within 17 mm of the axis over the embed must be solid (10.4 bore + >= 5 cover + margin)
    s2 = np.repeat(np.linspace(0, EMBED - 26, 18), 8); r2 = np.tile(np.array([0, 8, 14, 17, 17, 17, 14, 8.0]), 18); ph2 = np.tile(np.linspace(0, 2 * np.pi, 8, endpoint=False), 18)
    P2 = A[None] + s2[:, None] * d[None] + (r2 * np.cos(ph2))[:, None] * e1[None] + (r2 * np.sin(ph2))[:, None] * e2[None]
    i2 = np.clip(((P2[:, 0] - X0) / 2.0).round().astype(int), 0, NX - 1); j2 = np.clip(((P2[:, 1] - X0) / 2.0).round().astype(int), 0, NY - 1); k2 = np.clip(((P2[:, 2] + 8) / 2.0).round().astype(int), 0, NZ - 1)
    if not (f.F[i2, j2, k2] < 0).all(): _rej('core'); return None
    # back plate 100 x 100 x 6 under A must lie in solid trunk
    gx, gy = np.meshgrid(np.arange(-48, 49, 8.0), np.arange(-48, 49, 8.0)); ip = np.clip(((A[0] + gx.ravel() - X0) / 2.0).round().astype(int), 0, NX - 1); jp = np.clip(((A[1] + gy.ravel() - X0) / 2.0).round().astype(int), 0, NY - 1)
    kp = int(round((4.0 + 8) / 2.0))
    if (f.F[ip, jp, kp] < 0).mean() < 0.97: _rej('plate'); return None
    # geometry of the free span: length, clearance to the existing solid
    bu_, bv_ = H['boss']; wb = -float(hback(Gm, q)) + H.get('pad_inset', 4.0); nA = float(Gm['en'] @ (A - Gm['c3'])); s_plane = (wb - nA) / float(Gm['en'] @ d); s_T = s_plane - PAD_LEN
    if s_T + 6 > 242.0 or s_T - EMBED < 20: _rej('len'); return None
    ss = np.arange(EMBED + H.get('clear_start', 60), s_T, 6.0)
    if len(ss):
        Pc = A[None] + ss[:, None] * d[None]; u_ = np.clip((ss - EMBED) / (s_T - EMBED), 0, 1); Rr = 34.0 - 9.0 * u_ ** 0.9
        ic = np.clip(((Pc[:, 0] - X0) / 2.0).round().astype(int), 0, NX - 1); jc = np.clip(((Pc[:, 1] - X0) / 2.0).round().astype(int), 0, NY - 1); kc = np.clip(((Pc[:, 2] + 8) / 2.0).round().astype(int), 0, NZ - 1)
        if (dt[ic, jc, kc] < Rr + H.get('clear_margin', CLEAR_MARGIN)).any(): _rej('clear'); return None
    return dict(z_e=z_e, Rx=Rx, B0=B0, d=d, A=A, nd=nd, sol=sol, e1=e1, e2=e2)

def geometry(f, S):
    H = S['held']; Gm = make_frame(H, H['c']); R = Gm['R']
    # reference surface under the mask footprint (pre-eyes): max over a disc of 0.65 R about the mask centre in xy, projected
    ii = np.arange(-1, 1.01, 0.1) * 0.65 * R; XX, YY = np.meshgrid(H['c'][0] + ii, H['c'][1] + ii); m = (XX - H['c'][0]) ** 2 + (YY - H['c'][1]) ** 2 < (0.65 * R) ** 2
    zs = f.surface_z(XX[m], YY[m]); ref = float(H['ref_z']) if H.get('ref_z') else float(zs.max()); surf_pk = ref
    bp = disc_back_points(Gm); zmin0 = float(bp[:, 2].min() - Gm['c3'][2]); zm = surf_pk + H['gap'] - zmin0; Gm['c3'][2] = zm
    from scipy import ndimage as ndi
    dt = ndi.distance_transform_edt(f.F >= 0).astype(np.float32) * 2.0      # true distance (mm) from every air voxel to the nearest solid
    best = None; px, py = H['root_pref']; rr = H.get('root_r', 60)
    for dx in np.arange(-rr, rr + 1, 8.0):
        for dy in np.arange(-rr, rr + 1, 8.0):
            if dx * dx + dy * dy > rr * rr: continue
            c = candidate(f, S, H, Gm, px + dx, py + dy, dt)
            if c is None: continue
            sc = np.hypot(dx, dy) + 0.25 * np.linalg.norm(c['B0'] - c['Rx']) + 40 * (1 - c['nd'])
            if best is None or sc < best[0]: best = (sc, c)
    if best is None: raise RuntimeError('no feasible root near %s for %s: %s' % (H['root_pref'], S['id'], REASONS))
    c = best[1]; G = dict(Gm); G.update(c); d = c['d']; A = c['A']; B0 = c['B0']
    zq = float(np.hypot(*H['boss']) / G['R']); G['z_bb'] = float(B0[2])
    # pad plane: perpendicular offset 4 mm inside the disc back (local w = -h_b + 4)
    wb = -float(hback(G, zq)) + H.get('pad_inset', 4.0); nA = float(G['en'] @ (A - G['c3'])); s_plane = (wb - nA) / float(G['en'] @ d); s_T = s_plane - PAD_LEN; T = A + s_T * d
    G.update(s_plane=float(s_plane), s_T=float(s_T), T=T, s_exit=EMBED, s_rod=float(s_T + MASK_BORE), wb=wb, zm=float(zm), z_back=float(zm + zmin0), surf_pk=float(surf_pk), mc=np.array(H['c'], float), roll=np.radians(H.get('roll', 0)), yaw=np.radians(H.get('yaw', 0)), pitch=np.radians(H.get('pitch', 0)))
    return G

def axc(G, X, Y, Z):
    P = np.stack([X - G['A'][0], Y - G['A'][1], Z - G['A'][2]], -1); s = P @ G['d']; U = P @ G['e1']; V = P @ G['e2']; return s, np.sqrt(np.maximum((P ** 2).sum(-1) - s ** 2, 0)), U, V

def sheath(G):
    L = G['s_T'] + 6.0; n = int(L / 1.5); s = np.linspace(0, L, n); t = s / L; sw = 3.5 * np.sin(np.pi * np.clip((s - G['s_exit'] + 20) / (G['s_T'] - G['s_exit'] + 20), 0, 1)) * np.sin(2.1 * np.pi * t + 0.6)
    c = G['A'][None] + s[:, None] * G['d'][None] + sw[:, None] * G['e1'][None]
    u = np.clip((s - G['s_exit']) / (G['s_T'] - G['s_exit']), 0, 1); R = np.where(s < G['s_exit'], 31.0 + 3.0 * np.clip((s - (G['s_exit'] - 25)) / 25, 0, 1), 34.0 - 9.0 * u ** 0.9)
    return c, R * (1 + 0.025 * np.sin(0.09 * s + 1.0)), sw

def add_arm(fld, G, part='main'):
    c, R, sw = sheath(G); fld.sweep('M_arm', c, R, 18.0 if part == 'main' else 1.0, kind=2)
    if part == 'arm':
        A = G['A']; lo = (A[0] - 70, A[1] - 70, 0); hi = (G['Rx'][0] + 70, G['Rx'][1] + 70, G['Rx'][2] + 40)
        def blk(X, Y, Z):
            s, r, U, V = axc(G, X, Y, Z); cyl = np.maximum(r - BLOCK_R, np.maximum(-s, s - (G['s_exit'] + 12))); col = np.maximum(np.sqrt((X - A[0]) ** 2 + (Y - A[1]) ** 2) - BLOCK_R, np.maximum(-Z, Z - A[2])); return np.minimum(cyl, col)
        fld.add_fn(lo, hi, blk, k=1.0, kind=1)
        def plate(X, Y, Z):
            q = 8.0; dx = np.abs(X - A[0]) - 50 + q; dy = np.abs(Y - A[1]) - 50 + q; dzp = np.abs(Z - 3.0) - 3.0; return np.maximum(np.sqrt(np.maximum(dx, 0) ** 2 + np.maximum(dy, 0) ** 2) - q, dzp)
        fld.add_fn((A[0] - 60, A[1] - 60, 0), (A[0] + 60, A[1] + 60, 12), plate, k=1.0, kind=1)
        def spig(X, Y, Z):
            s, r, U, V = axc(G, X, Y, Z); return np.maximum(np.maximum(r - SPIG_R, U - FLAT), np.maximum(G['s_T'] - s, s - (G['s_T'] + SPIG_L)))
        P0 = G['T']; fld.add_fn((P0[0] - 60, P0[1] - 60, P0[2] - 50), (P0[0] + 60, P0[1] + 60, P0[2] + 80), spig, k=1.0, kind=2)

def carve_bore(fld, G, send):
    def bore(X, Y, Z):
        s, r, U, V = axc(G, X, Y, Z); return np.maximum(r - BORE_D / 2, np.maximum(-s, s - send))
    A, E = G['A'], G['A'] + send * G['d']; lo = np.minimum(A, E) - 8; hi = np.maximum(A, E) + 8; fld.carve(tuple(lo), tuple(hi), bore)

def add_pad(fld, G):
    T = G['T']
    def pad(X, Y, Z):
        s, r, U, V = axc(G, X, Y, Z); u, v, w = loc(G, X, Y, Z)
        return np.maximum(np.maximum(r - PAD_R, np.maximum(G['s_T'] - s, s - G['s_plane'] - 14)), (w - G['wb']) * 6.0) * 0.95
    lo = (T[0] - 70, T[1] - 70, T[2] - 60); hi = (T[0] + 70, T[1] + 70, T[2] + 120); fld.add_fn(lo, hi, pad, k=FIL_K, kind=2)

def _tube(fld, name, pts_local, r0, r1, k=4.0, G=None, rmin=3.6):
    pts = [tuple(glob(G, *p)) for p in pts_local]; c, tt, ln = curve(pts, 1.5); rr = np.maximum(r0 + (r1 - r0) * tt, rmin); fld.sweep(name, c, rr, k, store=False, kind=2); return float(ln)

def add_fingers(fld, G, nf=6):
    R = G['R']; rim = G['rim']; bu, bv = G['H']['boss']; ca = np.degrees(np.arctan2(bv, bu)) if np.hypot(bu, bv) > 1 else 270.0; fing = []; hb = lambda r_: float(hback(G, min(r_ / R, 1.0)))
    for j, ang in enumerate(np.linspace(ca - 65, ca + 65, nf)):
        th = np.radians(ang + [0, 3, -3, 2, -2, 0][j % 6]); ux, vy = np.cos(th), np.sin(th); rho = 12.5
        pts = [(bu + 0.20 * (0.22 * R * ux - bu), bv + 0.20 * (0.22 * R * vy - bv), -hb(np.hypot(bu, bv)) - 7)]
        for rr_ in (0.22, 0.38, 0.54, 0.70, 0.84): pts.append((rr_ * R * ux, rr_ * R * vy, -hb(rr_ * R) - 5.5))
        for t_ in np.linspace(0.0, np.pi, 7): rad_ = R + rho * np.sin(t_); pts.append((rad_ * ux, rad_ * vy, -rho * np.cos(t_)))
        pts.append(((R - 3.0) * ux, (R - 3.0) * vy, 13.0))
        ln = _tube(fld, f'fing{j}', pts, 9.0, 3.6, G=G); fing.append(dict(ang=float(ang), length=ln, r0=9.0, r1=3.6))
    return fing

def add_coil(fld, G):
    """tentacle coiled round the rim: from the pad along the back, then 2.5 turns round the rim over ~150 deg of the circumference, tip resting on the front lip."""
    R = G['R']; bu, bv = G['H']['boss']; ca = np.arctan2(bv, bu) if np.hypot(bu, bv) > 1 else -np.pi / 2; hb = lambda r_: float(hback(G, min(r_ / R, 1.0)))
    pts = [(bu * 0.6, bv * 0.6, -hb(np.hypot(bu, bv)) - 8)]
    for rr_ in (0.35, 0.55, 0.75, 0.9): pts.append((rr_ * R * np.cos(ca), rr_ * R * np.sin(ca), -hb(rr_ * R) - 6.5))
    nt = 40; rho = 12.0
    for i in range(nt + 1):
        u_ = i / nt; psi = -np.pi / 2 + 2.5 * 2 * np.pi * u_; phi = ca - np.radians(75) + np.radians(150) * u_; rad_ = R + rho * np.cos(psi) * (1 - 0.15 * u_) ; pts.append((rad_ * np.cos(phi), rad_ * np.sin(phi), rho * np.sin(psi) * 1.05))
    r_end = (R - 4.0); phi = ca + np.radians(75); pts.append((r_end * np.cos(phi), r_end * np.sin(phi), 13.0))
    pts = [pts[0]] + [p for i, p in enumerate(pts[1:], 1) if np.linalg.norm(np.array(p) - np.array(pts[i - 1])) > 1.0]
    return [dict(kind='coil', length=_tube(fld, 'coil', pts, 10.0, 5.0, k=3.0, G=G, rmin=4.0))]

EYE_HOLE = dict(eu=-0.165, ev=0.160, a=0.095, b=0.215)
def eye_hole_sd(G):
    D = 2 * G['R']; cu, cv, a, b = EYE_HOLE['eu'] * D, EYE_HOLE['ev'] * D, EYE_HOLE['a'] * D / 2, EYE_HOLE['b'] * D / 2
    return lambda u, v: (np.sqrt(((u - cu) / a) ** 2 + ((v - cv) / b) ** 2) - 1) * a

def add_thread(fld, G):
    """tentacle from the pad, along the back to the left eye hole, through it, over the face and down to the left rim (visual; the rod + pad hold the mask)."""
    R = G['R']; D = 2 * R; cu, cv = EYE_HOLE['eu'] * D, EYE_HOLE['ev'] * D; bu, bv = G['H']['boss']; hb = lambda r_: float(hback(G, min(r_ / R, 1.0)))
    pts = [(bu * 0.6, bv * 0.6, -hb(np.hypot(bu, bv)) - 8), ((bu + cu) * 0.5, (bv + cv) * 0.5, -hb(np.hypot((bu + cu) / 2, (bv + cv) / 2)) - 14), (cu, cv - 6, -hb(np.hypot(cu, cv)) - 16), (cu, cv, -4.0), (cu, cv, hb(np.hypot(cu, cv)) + 10),
           (cu - 14, cv + 8, hb(0.55 * R) + 18), (cu - 38, cv + 12, hb(0.75 * R) + 14), (cu - 58, cv - 6, hb(0.9 * R) + 10), (cu - 66, cv - 30, hb(0.98 * R) + 12)]
    return [dict(kind='thread', length=_tube(fld, 'thread', pts, 8.0, 4.5, k=3.0, G=G, rmin=4.0))]

def add_mask(fld, G, fsd_local, part='main'):
    R = G['R']; c = G['c3']; mfn = mask_sdf_fn(G); ext = R + 40
    lo = (c[0] - ext, c[1] - ext, c[2] - ext); hi = (c[0] + ext, c[1] + ext, c[2] + ext)
    fld.add_fn(lo, hi, mfn, k=6, kind=6); add_pad(fld, G)
    grip = G['H'].get('grip', 'F'); fl = G['dz'] - 11.0; hole = eye_hole_sd(G) if grip == 'E' else None
    def feat(X, Y, Z):
        u, v, w = loc(G, X, Y, Z); out = np.maximum(fsd_local(u, v), fl - w)
        if hole is not None: out = np.minimum(out, np.maximum(hole(u, v), np.abs(w) - (G['dz'] + 2.0)))      # eye hole cut through the full thickness (the tentacle passes through it)
        return out
    fld.carve((c[0] - ext, c[1] - ext, c[2] - ext), (c[0] + ext, c[1] + ext, c[2] + ext), feat)
    fing = add_fingers(fld, G) if grip == 'F' else (add_coil(fld, G) if grip == 'C' else add_thread(fld, G))
    if part == 'mask':
        def sock(X, Y, Z):
            s, r, U, V = axc(G, X, Y, Z); a = np.maximum(np.maximum(r - SPIG_R, U - FLAT), np.maximum(G['s_T'] - s, s - (G['s_T'] + SPIG_L))); b = np.maximum(r - BORE_D / 2, np.maximum(G['s_T'] - s, s - (G['s_T'] + MASK_BORE))); return np.minimum(a, b)
        T = G['T']; fld.carve((T[0] - 60, T[1] - 60, T[2] - 40), (T[0] + 60, T[1] + 60, T[2] + 90), sock)
    return fing
