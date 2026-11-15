"""Parametric P0 underlay generator (hollow S-curve shell + internal architecture + anchor + stub).

build_underlay(params, architecture=None, joint_type=None, cut_stations=None) -> dict
Architectures: rib_ladder | lattice | spine_beam.  Shared: shelf-deck webs, dome cross-ribs, plate bosses,
joint bulkhead plugs at cut stations.
"""
import numpy as np
import manifold3d as m3d
from ..mtools import (to_manifold, union, place, ring_prism, box, cyl, loft_mesh)
from .profile import Span, section_profiles, rrect_polygon, M_SEC

NEG_PAD = 0.6  # rib overlap into shell wall, mm


def _stations(span, ds, s0=None, s1=None):
    s0 = -span.neck if s0 is None else s0
    s1 = span.L if s1 is None else s1
    n = max(2, int(np.ceil((s1 - s0) / ds)) + 1)
    return np.linspace(s0, s1, n)


def _loft_tube(span, inset, ds):
    """Closed solid loft of the section family at given inset, incl. hemispherical tip cap."""
    # finer stations on the tip ramp-down (steep, strongly curved profile: chord sag of a 3 mm loft step reaches ~0.4 mm)
    s = _stations(span, ds, None, span.s_pad1 - 3.0)
    s = np.concatenate([s, np.arange(span.s_pad1, span.L + 1e-9, 1.0)])
    if s[-1] < span.L - 1e-9:
        s = np.append(s, span.L)
    prof = section_profiles(span, s, inset)
    cen = span.point(s)
    T, N, U = span.frame(s)
    L = span.L
    p_L = section_profiles(span, np.array([L]), inset)[0]
    rho = float(np.mean(np.linalg.norm(p_L, axis=1)))   # inner tip radius
    d_arr = np.arange(ds, 0.985 * rho, ds)
    T0, N0, U0 = span.frame(np.array([L]))
    cd = span.point(np.array([L])) + d_arr[:, None] * T0
    pd = np.repeat(p_L[None], len(d_arr), 0)
    k = np.sqrt(np.clip(1 - (d_arr / rho) ** 2, 0, 1))
    pd = pd * k[:, None, None]
    cen = np.vstack([cen, cd])
    N = np.vstack([N, np.repeat(N0, len(d_arr), 0)])
    U = np.vstack([U, np.repeat(U0, len(d_arr), 0)])
    prof = np.concatenate([prof, pd], axis=0)
    return loft_mesh(cen, N, U, prof)


def _ellipsoid_dome(a, b, c, x_min):
    e = m3d.Manifold.sphere(1.0, 128).scale((a, b, c))
    return e.trim_by_plane((1, 0, 0), x_min)


def sweep_rect(span, s_arr, centers_nu, half_w, half_h, rot=None):
    """Sweep a rectangle along stations. centers_nu (n,2) in (N,U); axis-aligned unless rot (n,) angles."""
    T, N, U = span.frame(s_arr)
    cen = span.point(s_arr)
    n = len(s_arr)
    rot = np.zeros(n) if rot is None else rot
    hw = np.broadcast_to(np.asarray(half_w, float), (n,))
    hh = np.broadcast_to(np.asarray(half_h, float), (n,))
    base = np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]], float)
    prof = np.zeros((n, 4, 2))
    c, sn = np.cos(rot), np.sin(rot)
    for i in range(n):
        q = base * np.array([hw[i], hh[i]])
        R = np.array([[c[i], -sn[i]], [sn[i], c[i]]])
        prof[i] = centers_nu[i] + q @ R.T
    return to_manifold(loft_mesh(cen, N, U, prof))


def _inner_pt(span, s_arr, phi, inset):
    A, B, R = span.ABR(s_arr, inset)
    out = np.zeros((len(s_arr), 2))
    for i, (a, b, r) in enumerate(zip(A, B, R)):
        poly = rrect_polygon(a, b, r)
        f = (phi[i] % (2 * np.pi)) / (2 * np.pi) * M_SEC
        i0 = int(np.floor(f)) % M_SEC; i1 = (i0 + 1) % M_SEC; w = f - np.floor(f)
        out[i] = poly[i0] * (1 - w) + poly[i1] * w
    return out


def min_ABR(span, s_list, inset):
    """Elementwise-min section over several stations (keeps a planar prism inside a changing outer surface)."""
    abr = [span.ABR(np.array([x]), inset) for x in s_list]
    return tuple(np.min([a[i] for a in abr], axis=0) for i in range(3))


def ring_rib(span, s, th, flange, inset):
    # outer edge sits 0.5*inset inside the outer surface (min over the rib thickness): penetrates the shell wall by >= 0.5*inset
    # even on ramps, so no sliver gap opens between the rib corner and the inclined inner wall
    A, B, R = min_ABR(span, [s - th / 2, s, s + th / 2], 0.5 * inset)
    Ai, Bi, Ri = span.ABR(np.array([s]), inset + flange)
    outer = rrect_polygon(A[0], B[0], R[0]); inner = rrect_polygon(Ai[0], Bi[0], max(Ri[0], 1.0))
    T, N, U = span.frame(np.array([s]))
    pr = ring_prism(outer, inner, -th / 2, th / 2)
    return place(pr, span.point(np.array([s]))[0], N[0], U[0], T[0])


def vertical_web(span, s_arr, n_off, t, inset):
    A, B, R = span.ABR(s_arr, inset)
    c = np.column_stack([np.full(len(s_arr), n_off), np.zeros(len(s_arr))])
    return sweep_rect(span, s_arr, c, t / 2, B + NEG_PAD)


def build_underlay(p, architecture=None, joint_type=None, cut_stations=None):
    from .joints import joint_plug
    arch = architecture or p["architecture"]
    jt = joint_type or p["joint"]["type"]
    cuts = cut_stations if cut_stations is not None else p["joint"]["cut_stations"]
    span = Span(p)
    ds = p["station_spacing"]
    t = p["shell_wall"]
    rb = p["ribs"]; st = p["body_stub"]; ap = p["anchor_plate"]
    L = span.L

    outer_tube = to_manifold(_loft_tube(span, 0.0, ds))
    inner_tube = to_manifold(_loft_tube(span, t, ds))
    a, bb = st["depth"], st["diameter"] / 2
    XB = -5.0  # build behind the wall plane, single clean trim at x=0 at the end
    dome_out = _ellipsoid_dome(a, bb, bb, XB)
    dome_cav = _ellipsoid_dome(a - st["wall"], bb - st["wall"], bb - st["wall"], XB - 1.0)
    envelope = union([outer_tube, dome_out])
    cavity = union([dome_cav, inner_tube])
    shell = envelope - cavity
    parts = [shell]
    # anchor plate (full slab) + perimeter ring flange tying plate to dome wall; back of dome otherwise open to wall
    pl = ap["size"]
    parts.append(box(((pl[2] + XB) / 2, 0, 0), (pl[2] - XB, pl[0], pl[1])))
    ring = m3d.Manifold.extrude(m3d.CrossSection.circle(bb - 1.0, 128) - m3d.CrossSection.circle(70.0, 128), pl[2] - XB).translate((0, 0, XB))
    parts.append(ring.transform(np.array([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]], float)))  # local z -> +x

    ct = st["cross_rib_t"]
    xp = ap["size"][2] - 0.4
    dome_clip = _ellipsoid_dome(a - st["wall"] + 1.0, bb - st["wall"] + 1.0, bb - st["wall"] + 1.0, xp)
    for sz in [(a + 10, ct, 2 * bb), (a + 10, 2 * bb, ct)]:
        parts.append(box((xp + (a + 10) / 2, 0, 0), sz) ^ dome_clip)
    hy, hz = ap["hole_pattern"][0] / 2, ap["hole_pattern"][1] / 2
    holes = [(sy * hy, sz_ * hz) for sy in (-1, 1) for sz_ in (-1, 1)]
    for (y, z) in holes:
        parts.append(cyl((xp, y, z), (ap["size"][2] + ap["boss_h"], y, z), ap["boss_d"] / 2, 48))

    s_main = _stations(span, ds, rb.get("start_s", -13.3), 0.955 * L)
    s_pad = _stations(span, ds, span.ramp_up0 - 6, 0.955 * L)
    ins = t
    rw, rh = rb["rail_w"], rb["rail_h"]

    def rails(s_arr):
        A, B, R = span.ABR(s_arr, ins)
        out = []
        for sg in (1, -1):
            u = sg * (B + NEG_PAD - rh / 2)
            out.append(sweep_rect(span, s_arr, np.column_stack([np.zeros(len(s_arr)), u]), rw / 2, rh / 2))
        return out

    def rings(s_vals, th=None):
        return [ring_rib(span, s, th or rb["thickness"], rb["flange"], ins) for s in s_vals]

    if arch == "rib_ladder":
        parts += rails(s_main)
        parts += rings(np.arange(rb["pitch"] * 0.5, 0.955 * L, rb["pitch"]))
    elif arch == "spine_beam":
        parts.append(vertical_web(span, s_main, 0.0, rb["spine_web_t"], ins))
        A, B, R = span.ABR(s_main, ins)
        for sg in (1, -1):
            u = sg * (B + NEG_PAD - rb["spine_flange_h"] / 2)
            parts.append(sweep_rect(span, s_main, np.column_stack([np.zeros(len(s_main)), u]),
                                    rb["spine_flange_w"] / 2, rb["spine_flange_h"] / 2))
        parts += rings(np.arange(rb["spine_ring_pitch"] * 0.5, 0.955 * L, rb["spine_ring_pitch"]))
    elif arch == "lattice":
        s_lat = _stations(span, ds, rb.get("start_s", -13.3), span.ramp_up0 + 8)
        k = rb["lattice_struts_per_family"]
        for fam in (+1, -1):
            for i in range(k):
                phi = 2 * np.pi * i / k + fam * 2 * np.pi * s_lat / rb["lattice_turn_len"]
                pt = _inner_pt(span, s_lat, phi, ins)
                er = np.column_stack([np.cos(phi), np.sin(phi)])
                ctr = pt - er * (rb["strut_h"] / 2 - NEG_PAD)
                parts.append(sweep_rect(span, s_lat, ctr, rb["strut_h"] / 2, rb["strut_w"] / 2, rot=phi))
        parts += rings(np.arange(rb["pitch"] * 0.5, span.ramp_up0 + 8, rb["pitch"] * 1.5))
        parts += rings([span.ramp_up0 + 4])
    else:
        raise ValueError(arch)

    # shelf deck stiffeners (all architectures)
    if arch != "spine_beam":
        parts.append(vertical_web(span, s_pad, 0.0, rb["deck_web_t"], ins))
    nw = rb["deck_web_n"]
    A, B, R = span.ABR(s_pad, ins)
    ok = (A - R) >= (nw + 4)
    if ok.sum() > 3:
        for sgn in (-1, 1):
            parts.append(vertical_web(span, s_pad[ok], sgn * nw, rb["deck_web_t"], ins))
    parts += rings(np.arange(span.ramp_up0 + 8, 0.955 * L, rb["deck_rib_pitch"]), th=rb["deck_web_t"])

    plugs, joints_meta = [], []
    for sc in cuts:
        jp = joint_plug(span, p, float(sc), jt)
        plugs.append(jp["plug"]); joints_meta.append(jp["meta"])
    parts += plugs

    under = union(parts)
    cuts_ = []
    for (y, z) in holes:
        cuts_.append(cyl((XB - 1, y, z), (ap["size"][2] + ap["boss_h"] + 1, y, z), ap["hole_d"] / 2, 32))
        cuts_.append(cyl((ap["size"][2] + ap["boss_h"], y, z), (75, y, z), ap["access_bore_d"] / 2, 40))
    under = under - union(cuts_)
    under = (under ^ envelope).trim_by_plane((1, 0, 0), 0.0)
    envelope = envelope.trim_by_plane((1, 0, 0), 0.0)

    # drain/vent holes through the underside wall, one set per sealed chamber (chambers are separated by the bulkhead plugs;
    # chamber 0 also has the screw-access bores but those get plugged). Axis along -U, offset in N, between ring ribs.
    vp = p["vents"]
    vent_cyls, vent_keepouts, vents_meta = [], [], []
    for sv in vp["stations"]:
        Tv, Nv, Uv = span.frame(np.array([float(sv)])); ov = span.point(np.array([float(sv)]))[0]
        Bv = float(span.ABR(np.array([float(sv)]))[1][0])
        for no in vp["n_offsets"]:
            p0 = ov + no * Nv[0]
            p1 = p0 - (Bv + 8.0) * Uv[0]
            vent_cyls.append(cyl(p0, p1, vp["d"] / 2, 24))
            vent_keepouts.append(cyl(p0 - 2.0 * Uv[0], p1 - 4.0 * Uv[0], vp["d"] / 2 + vp["skin_clear"], 32))
            vents_meta.append(dict(s=float(sv), n_offset=float(no), d=float(vp["d"]), p0=p0.tolist(), p1=p1.tolist()))
    under = under - union(vent_cyls)

    s_mid = 0.5 * (span.s_pad0 + span.s_pad1)
    T, N, U = span.frame(np.array([s_mid]))
    c0 = span.point(np.array([s_mid]))[0]
    ztop = span.top_plane_z()
    mg = p["shelf"]["keepout_margin"]
    t0, t1 = span.s_pad0 - mg - s_mid, span.s_pad1 + mg - s_mid
    vz0, vz1 = ztop - 1.0 - c0[2], ztop + 400 - c0[2]
    k_pad = place(box((0, (vz0 + vz1) / 2, (t0 + t1) / 2), (2 * (span.pad_A + 10), vz1 - vz0, t1 - t0)),
                  c0, N[0], U[0], T[0])
    k_wall = box((-10, 0, 0), (25, 600, 600))
    k_bore = union([cyl((0, y, z), (80, y, z), ap["access_bore_d"] / 2 + 3, 32) for (y, z) in holes])
    keepouts = [k_pad, k_wall, k_bore] + vent_keepouts

    meta = dict(
        architecture=arch, joint_type=jt, cut_stations=[float(c) for c in cuts], joints=joints_meta,
        ztop=float(ztop),
        pad_frame=dict(origin=c0.tolist(), N=N[0].tolist(), U=U[0].tolist(), T=T[0].tolist(),
                       t_range=[float(t0 + mg), float(t1 - mg)], n_half=float(span.pad_A - span.pad_R)),
        holes=[list(h) for h in holes], vents=vents_meta,
        tip_xyz=span.point(np.array([L]))[0].tolist(),
        span_arc3d=float(np.sum(np.linalg.norm(np.diff(span.point(np.linspace(0, L, 800)), axis=0), axis=1))),
    )
    return dict(underlay=under, envelope=envelope, keepouts=keepouts, meta=meta, span=span)
