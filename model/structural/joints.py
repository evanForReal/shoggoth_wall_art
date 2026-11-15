"""Joint candidates at segment cut stations.

Local joint frame at station sc: origin = centerline point, x=N (horizontal normal), y=U (~up), z=T (tangent, +z = outboard).
Segment A is inboard (z<0 side, lower s), B outboard (z>0). Underlay monolith carries only the solid bulkhead
plug (A: z in [-bhA,0], B: z in [0,bhB]); the segmenter adds key/socket/holes.

Types: dovetail_bolt | tongue_pin | socket_through_bolt
"""
import numpy as np
import manifold3d as m3d
from ..mtools import union, place, prism, box, cyl
from .profile import rrect_polygon

KEY_LEN = {"dovetail_bolt": 12.0, "tongue_pin": 20.0, "socket_through_bolt": 24.0}


def _dims(span, p, sc, kind):
    t = p["shell_wall"]
    A, B, R = span.ABR(np.array([sc]), t)
    Ai, Bi, Ri = float(A[0]), float(B[0]), float(R[0])
    T, N, U = span.frame(np.array([sc]))
    o = span.point(np.array([sc]))[0]
    j = p["joint"]
    L = KEY_LEN[kind]
    bhA = j["bulkhead_A"]; bhB = L + 4.0
    n_key = min(0.6 * Ai, Ai - Ri if Ri < Ai - 5 else 0.6 * Ai)
    return dict(o=o, T=T[0], N=N[0], U=U[0], Ai=Ai, Bi=Bi, Ri=Ri, L=L, bhA=bhA, bhB=bhB,
                clr=j["clearance"], bolt_d=j["bolt_d"], pin_d=j["pin_d"], n_key=n_key, sc=sc, t=t)


def _P(d, x, y, z):
    return d["o"] + x * d["N"] + y * d["U"] + z * d["T"]


def _loc(d, man):
    return place(man, d["o"], d["N"], d["U"], d["T"])


def joint_plug(span, p, sc, kind):
    """Solid bulkhead plug: loft of the (inset t-0.6) section through stations sc-bhA .. sc+bhB, so it follows taper/curvature."""
    from ..mtools import loft_mesh, to_manifold
    from .profile import section_profiles
    d = _dims(span, p, sc, kind)
    s0, s1 = sc - d["bhA"], sc + d["bhB"]
    st = np.unique(np.concatenate([np.linspace(s0, sc, 5), np.linspace(sc, s1, int(np.ceil((s1 - sc) / 2.0)) + 1)]))
    prof = section_profiles(span, st, p["shell_wall"] - 0.6)
    T, N, U = span.frame(st)
    plug = to_manifold(loft_mesh(span.point(st), N, U, prof))
    meta = dict(type=kind, station=sc, origin=d["o"].tolist(), T=d["T"].tolist(), N=d["N"].tolist(), U=d["U"].tolist(),
                inner_half_width=d["Ai"], inner_half_height=d["Bi"], bulkhead_A=d["bhA"], bulkhead_B=d["bhB"],
                key_len=d["L"], clearance=d["clr"])
    return dict(plug=plug, meta=meta)


def _hex_prism(af, h):
    r = af / np.sqrt(3)
    ang = np.radians(np.arange(6) * 60)
    return prism(np.column_stack([r * np.cos(ang), r * np.sin(ang)]), 0, h)


def joint_features(span, p, sc, kind):
    """Returns dict(key=Manifold added to A, socket=Manifold cut from B, holes=Manifold cut from both, hardware=[...])."""
    d = _dims(span, p, sc, kind)
    L, clr = d["L"], d["clr"]
    Ai, Bi = d["Ai"], d["Bi"]
    hw = []
    if kind == "dovetail_bolt":
        hb, ht = 0.35 * Bi, 0.60 * Bi
        nk = d["n_key"]
        def shape(c):
            # trapezoid in (t,u), extruded along n; build in local (x=t->?)
            pts = np.array([[-1.0, -(hb + c)], [0.0, -(hb + c)], [L + c, -(ht + c)], [L + c, ht + c], [0.0, hb + c], [-1.0, hb + c]])
            cs = m3d.CrossSection([pts])
            return cs
        def extr(c):
            cs = shape(c)
            # extrusion axis = local z; map extrusion axis -> N, polygon x -> T, polygon y -> U
            man = m3d.Manifold.extrude(cs, 2 * (nk + c)).translate((0, 0, -(nk + c)))
            return place(man, d["o"], d["T"], -d["U"], d["N"])   # local x->T, y->-U, z->N (right-handed)
        key, socket = extr(0.0), extr(clr)
        holes = []
        for sg in (-1, 1):
            n_b = sg * 0.78 * nk
            holes.append(cyl(_P(d, n_b, 0, -d["bhA"] - 1), _P(d, n_b, 0, d["bhB"] + 1), d["bolt_d"] / 2, 24))
            hw.append(dict(kind="bolt M4", p0=_P(d, n_b, 0, -d["bhA"]).tolist(), p1=_P(d, n_b, 0, d["bhB"]).tolist(), d=4.0))
        holes = union(holes)
    elif kind == "tongue_pin":
        nt, ut = 0.6 * Ai, 0.45 * Bi
        key = _loc(d, box((0, 0, (L - 1.0) / 2), (2 * nt, 2 * ut, L + 1.0)))
        socket = _loc(d, box((0, 0, (L + clr - 1.0) / 2), (2 * (nt + clr), 2 * (ut + clr), L + clr + 1.0)))
        holes = cyl(_P(d, 0, 0, -d["bhA"] - 1), _P(d, 0, 0, d["bhB"] + 1), d["pin_d"] / 2, 24)
        hw.append(dict(kind="steel pin / M6 threaded rod", p0=_P(d, 0, 0, -d["bhA"]).tolist(),
                       p1=_P(d, 0, 0, d["bhB"]).tolist(), d=6.0))
    elif kind == "socket_through_bolt":
        dsp = min(1.3 * Bi, 1.6 * Bi)
        key = cyl(_P(d, 0, 0, -1.0), _P(d, 0, 0, L), dsp / 2, 64)
        socket = cyl(_P(d, 0, 0, -1.0), _P(d, 0, 0, L + clr), dsp / 2 + clr, 64)
        zb = L / 2
        h_ = cyl(_P(d, 0, -Bi - d["t"] - 1, zb), _P(d, 0, Bi + d["t"] + 1, zb), 5.4 / 2, 24)
        # nut trap (M5, AF 8, 4 mm) on bottom outer wall + head recess top
        holes = h_
        hw.append(dict(kind="bolt M5 transverse (bonded spigot)", p0=_P(d, 0, -Bi - d["t"], zb).tolist(),
                       p1=_P(d, 0, Bi + d["t"], zb).tolist(), d=5.0))
        # bond note: spigot is epoxy/CA bonded; bolt carries peel/shear
    else:
        raise ValueError(kind)
    return dict(key=key, socket=socket, holes=holes, hardware=hw, dims={k: (v.tolist() if hasattr(v, "tolist") else v) for k, v in d.items()})
