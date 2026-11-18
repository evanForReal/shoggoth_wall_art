"""r11 held mask: geometry of the rod-cored holding tentacle (Structural spec teams/structural/analysis/mask-arm-v1.md S1-S10) and the separate mask part.
Everything is generated from one dict G (geometry()) so the main field, the isolated arm part and the isolated mask part share numbers.
mm; x right, y up, z out of the wall (gravity = -y)."""
import numpy as np
from engine import curve, ellipsoid, smin
ROD_D, BORE_D = 10.0, 10.4
PAD_R, PAD_LEN, FIL_K = 35.0, 38.0, 28.0       # pad dia 70, 38 mm deep along the axis, smin k 28 -> fillet r ~ 0.6 k = 17 mm
EMBED, MASK_BORE = 82.0, 44.0                   # rod embed into the solid root block, rod depth into the mask from the pad face
SPIG_R, SPIG_L, FLAT = 20.0, 30.0, 16.0         # arm-tip spigot dia 40 x 30 deep with a D-flat at 16 mm from the axis
BLOCK_R = 30.0                                  # solid root block dia 60

def mask_sdf_fn(G):
    cx, cy, zm, R, dz, rim = G['mc'][0], G['mc'][1], G['zm'], G['R'], G['dz'], G['rim']; ct, st = np.cos(G['roll']), np.sin(G['roll'])
    def mfn(X, Y, Z):
        u = ct * (X - cx) + st * (Y - cy); v = -st * (X - cx) + ct * (Y - cy); q = np.sqrt((u / R) ** 2 + (v / R) ** 2); h = rim + (dz - rim) * np.sqrt(np.clip(1 - q * q, 0, 1))
        return np.maximum((q - 1) * R, np.abs(Z - zm) - h) * 0.9
    return mfn

def hback(G, q): return G['rim'] + (G['dz'] - G['rim']) * np.sqrt(np.clip(1 - q * q, 0, 1))

def geometry(f, S):
    H = S['held']; mc = np.array(H['c'], float); roll = np.radians(H['roll']); R = H['D'] / 2; dz = H['dz']; rim = H['rim']; pc = S['patch']['c']
    ii = np.arange(-40, 41, 4.0); XX, YY = np.meshgrid(pc[0] + ii, pc[1] + ii); m = XX ** 2 + YY ** 2 - 2 * 0 < 40 ** 2 + 0
    m = ((XX - pc[0]) ** 2 + (YY - pc[1]) ** 2) < 40 ** 2; surf_pk = float(f.surface_z(XX[m], YY[m]).max())
    z_back = surf_pk + H['gap']; zm = z_back + dz; ct, st = np.cos(roll), np.sin(roll); bv = H['boss_v']
    bx, by = mc[0] - st * bv, mc[1] + ct * bv; q = abs(bv) / R; z_bb = zm - hback(dict(rim=rim, dz=dz), q)       # back surface of the mask at the boss
    rx, ry = S['root_xy']; ww = np.arange(-6, 7, 3.0); X6, Y6 = np.meshgrid(rx + ww, ry + ww); z_e = float(f.surface_z(X6.ravel(), Y6.ravel()).max())
    Rx = np.array([rx, ry, z_e]); B0 = np.array([bx, by, z_bb]); d = (B0 - Rx) / np.linalg.norm(B0 - Rx); A = Rx - EMBED * d
    s_plane = (z_bb + 8.0 - A[2]) / d[2]; s_T = s_plane - PAD_LEN; T = A + s_T * d
    a = np.array([0, 1.0, 0]) if abs(d[1]) < 0.9 else np.array([1.0, 0, 0]); e1 = np.cross(d, a); e1 /= np.linalg.norm(e1); e2 = np.cross(d, e1)
    return dict(H=H, mc=mc, roll=roll, R=R, dz=dz, rim=rim, zm=zm, z_back=z_back, surf_pk=surf_pk, bx=bx, by=by, z_bb=z_bb, Rx=Rx, B0=B0, d=d, A=A, s_T=float(s_T), T=T, s_plane=float(s_plane), e1=e1, e2=e2,
                s_exit=EMBED, s_rod=float(s_T + MASK_BORE), z_e=z_e, ct=ct, st=st)

def axc(G, X, Y, Z):
    """axis coordinates: s along the rod from A, rad = distance from the axis, u/v = in-plane coords (e1/e2)"""
    P = np.stack([X - G['A'][0], Y - G['A'][1], Z - G['A'][2]], -1); s = P @ G['d']; U = P @ G['e1']; V = P @ G['e2']; return s, np.sqrt(np.maximum(P[..., 0] ** 2 + P[..., 1] ** 2 + P[..., 2] ** 2 - s ** 2, 0)), U, V

def sheath(G):
    """centreline + radius of the holding tentacle: rod axis A -> pad face T (+6 into the pad). offset from the rod axis <= 3.5 mm (organic sway), radius 31 in the root block, 34 at the trunk surface, tapering to 25 at the pad face."""
    L = G['s_T'] + 6.0; n = int(L / 1.5); s = np.linspace(0, L, n); t = s / L; sw = 3.5 * np.sin(np.pi * np.clip((s - G['s_exit'] + 20) / (G['s_T'] - G['s_exit'] + 20), 0, 1)) * np.sin(2.1 * np.pi * t + 0.6)
    c = G['A'][None] + s[:, None] * G['d'][None] + sw[:, None] * G['e1'][None]
    u = np.clip((s - G['s_exit']) / (G['s_T'] - G['s_exit']), 0, 1); R = np.where(s < G['s_exit'], 31.0 + 3.0 * np.clip((s - (G['s_exit'] - 25)) / 25, 0, 1), 34.0 - 9.0 * u ** 0.9)
    R = R * (1 + 0.025 * np.sin(0.09 * s + 1.0)); return c, R, sw

def add_arm(fld, G, part='main'):
    c, R, sw = sheath(G); fld.sweep('M_arm', c, R, 18.0 if part == 'main' else 1.0, kind=2)
    if part == 'arm':     # isolated arm part for review: solid root block 60 dia, vertical solid column to the back, 100 x 100 x 6 back plate, spigot
        A, d = G['A'], G['d']; lo = (A[0] - 70, A[1] - 70, 0); hi = (G['Rx'][0] + 70, G['Rx'][1] + 70, G['Rx'][2] + 40)
        def blk(X, Y, Z):
            s, r, U, V = axc(G, X, Y, Z); cyl = np.maximum(r - BLOCK_R, np.maximum(-s, s - (G['s_exit'] + 12))); col = np.maximum(np.sqrt((X - A[0]) ** 2 + (Y - A[1]) ** 2) - BLOCK_R, np.maximum(-Z, Z - A[2]))
            return np.minimum(cyl, col)
        fld.add_fn(lo, hi, blk, k=1.0, kind=1)
        def plate(X, Y, Z):
            q = 8.0; dx = np.abs(X - A[0]) - 50 + q; dy = np.abs(Y - A[1]) - 50 + q; dzp = np.abs(Z - 3.0) - 3.0
            return np.maximum(np.sqrt(np.maximum(dx, 0) ** 2 + np.maximum(dy, 0) ** 2) - q, dzp)
        fld.add_fn((A[0] - 60, A[1] - 60, 0), (A[0] + 60, A[1] + 60, 12), plate, k=1.0, kind=1)
        def spig(X, Y, Z):
            s, r, U, V = axc(G, X, Y, Z); return np.maximum(np.maximum(r - SPIG_R, U - FLAT), np.maximum(G['s_T'] - s, s - (G['s_T'] + SPIG_L)))
        P0 = G['T']; fld.add_fn((P0[0] - 60, P0[1] - 60, P0[2] - 50), (P0[0] + 60, P0[1] + 60, P0[2] + 80), spig, k=1.0, kind=2)

def carve_bore(fld, G, send):
    """rod bore (hardware envelope), 10.4 mm, from s = 0 to s = send"""
    def bore(X, Y, Z):
        s, r, U, V = axc(G, X, Y, Z); return np.maximum(r - BORE_D / 2, np.maximum(-s, s - send))
    A, E = G['A'], G['A'] + send * G['d']; lo = np.minimum(A, E) - 8; hi = np.maximum(A, E) + 8; fld.carve(tuple(lo), tuple(hi), bore)

def add_pad_and_fingers(fld, G, fsd=None, part='main'):
    d = G['d']; T = G['T']; zpl = G['z_bb'] + 4.0
    def pad(X, Y, Z):
        s, r, U, V = axc(G, X, Y, Z); return np.maximum(np.maximum(r - PAD_R, np.maximum(G['s_T'] - s, s - G['s_plane'] - 14)), (Z - zpl) * 6.0) * 0.95
    lo = (T[0] - 60, T[1] - 60, T[2] - 50); hi = (T[0] + 60, T[1] + 60, zpl + 10); fld.add_fn(lo, hi, pad, k=FIL_K, kind=2)

def add_fingers(fld, G, nf=6):
    """6 grip fingers: from the pad, along the back of the disc, round the rim, hooking <= 6 mm over the front lip (visual grip, no structural role)."""
    cx, cy = G['mc']; R = G['R']; ct, st = G['ct'], G['st']; zm = G['zm']; rim, dz = G['rim'], G['dz']; fing = []
    loc = lambda u, v: (cx + ct * u - st * v, cy + st * u + ct * v)
    for j, ang in enumerate(np.linspace(205, 335, nf)):
        th = np.radians(ang + [0, 3, -3, 2, -2, 0][j % 6]); ux, vy = np.cos(th), np.sin(th); bu, bv = 0.0, G['H']['boss_v']
        def P(rad, z): u = bu + (rad * ux - bu) * 1.0 if False else rad * ux; v = rad * vy; x, y = loc(u, v); return (x, y, z)
        hb = lambda rr: float(hback(G, min(rr / R, 1.0)))
        rho = 12.5; ra = lambda t_: (R + rho * np.sin(t_), zm + rho * -np.cos(t_))      # semicircle round the rim edge: t=0 under the rim, pi/2 outside, pi over the front lip
        pts = [(*loc(bu + 0.20 * (0.22 * R * ux - bu), bv + 0.20 * (0.22 * R * vy - bv)), zm - hb(abs(bv)) - 7)]
        for rr_ in (0.22, 0.38, 0.54, 0.70, 0.84): pts.append((*loc(rr_ * R * ux, rr_ * R * vy), zm - hb(rr_ * R) - 5.5))
        for t_ in np.linspace(0.0, np.pi, 7): rad_, zz_ = ra(t_); pts.append(P(rad_, zz_))
        pts.append(P(R - 3.0, zm + 13.0))
        c, tt, ln = curve(pts, 1.5); rr = 9.0 - 5.4 * tt; rr = np.maximum(rr, 3.6); fld.sweep(f'fing{j}', c, rr, 4.0, store=False, kind=2); fing.append(dict(ang=float(ang), length=float(ln), r0=float(rr[0]), r1=float(rr[-1])))
    return fing

def add_mask(fld, G, fsd, fl, part='main'):
    mfn = mask_sdf_fn(G); R = G['R']; cx, cy = G['mc']
    fld.add_fn((cx - R - 20, cy - R - 20, G['zm'] - 40), (cx + R + 20, cy + R + 20, G['zm'] + 40), mfn, k=6, kind=6)
    add_pad_and_fingers(fld, G); fing = add_fingers(fld, G)
    fld.carve((cx - R, cy - R, fl - 2), (cx + R, cy + R, 300), lambda X, Y, Z: np.maximum(fsd(X, Y), fl - Z))
    if part == 'mask':     # socket: D-flat spigot socket 30 deep + 44 mm rod bore, blind
        def sock(X, Y, Z):
            s, r, U, V = axc(G, X, Y, Z); a = np.maximum(np.maximum(r - SPIG_R, U - FLAT), np.maximum(G['s_T'] - s, s - (G['s_T'] + SPIG_L))); b = np.maximum(r - BORE_D / 2, np.maximum(G['s_T'] - s, s - (G['s_T'] + MASK_BORE)))
            return np.minimum(a, b)
        T = G['T']; fld.carve((T[0] - 60, T[1] - 60, T[2] - 40), (T[0] + 60, T[1] + 60, T[2] + 90), sock)
    return fing
