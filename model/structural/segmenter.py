"""Split an assembly/underlay manifold at cut stations and apply joint features.

segment(man, span, p, joint_type, cuts) -> list of dict(index, man, s_lo, s_hi, joints_in, joints_out)
Cut plane: through centerline point at station, normal = tangent. Segment k spans cuts[k-1]..cuts[k].
"""
import numpy as np
import trimesh
from ..mtools import to_trimesh, union
from .joints import joint_features


def _plane(span, sc):
    T, N, U = span.frame(np.array([sc]))
    o = span.point(np.array([sc]))[0]
    return o, T[0]


def segment(man, span, p, joint_type, cuts):
    cuts = sorted(float(c) for c in cuts)
    feats = [joint_features(span, p, c, joint_type) for c in cuts]
    bounds = [-1e9] + cuts + [1e9]
    out = []
    for k in range(len(cuts) + 1):
        part = man
        if k > 0:
            o, T = _plane(span, cuts[k - 1])
            part = part.trim_by_plane(tuple(T), float(np.dot(T, o)))
        if k < len(cuts):
            o, T = _plane(span, cuts[k])
            part = part.trim_by_plane(tuple(-T), float(-np.dot(T, o)))
        # joint features
        if k < len(cuts):          # upper end: carries key
            part = part + feats[k]["key"]
            part = part - feats[k]["holes"]
        if k > 0:                  # lower end: socket
            part = part - feats[k - 1]["socket"]
            part = part - feats[k - 1]["holes"]
        out.append(dict(index=k, man=part, s_lo=None if k == 0 else cuts[k - 1],
                        s_hi=None if k == len(cuts) else cuts[k],
                        joint_hi=None if k == len(cuts) else k, joint_lo=None if k == 0 else k - 1))
    return out, feats


def print_orientation(mesh):
    """Return (4x4 transform, sorted extents): min-volume oriented box, longest dim on X, shortest on Z, rotation only
    (no mirroring), dropped so min z = 0. Heuristic: Verification/Fabrication own overhang-aware orientation."""
    T, ext = trimesh.bounds.oriented_bounds(mesh)
    order = np.argsort(-ext)
    P = np.eye(4)[[*order, 3]]
    if np.linalg.det(P[:3, :3]) < 0:
        P[2] *= -1
    M = P @ T
    m2 = mesh.copy(); m2.apply_transform(M)
    M[:3, 3] -= m2.bounds[0]
    m2.apply_transform(np.eye(4))
    m2 = mesh.copy(); m2.apply_transform(M)
    return M, (m2.bounds[1] - m2.bounds[0])
