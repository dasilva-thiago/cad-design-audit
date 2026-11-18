#!/usr/bin/env python3
"""Mesh integrity and bed-fit audit for STL and 3MF files (Python standard library only).

Usage:
  python mesh_audit.py PART.stl [--bed 220x220x250] [--margin 5] [--weld 1e-5]
  python mesh_audit.py PART.3mf --bed 256x256x256

Prints one JSON object. Exit codes:
  0  no integrity errors (and fits the bed, if --bed was given)
  1  integrity errors (open edges, non-manifold edges, inconsistent orientation,
     inverted volume, degenerate or duplicate faces)
  2  integrity OK but the part does not fit the bed
  3  file could not be read

Checks: triangle count, bounding box, volume (signed, divergence theorem), surface area,
boundary edges, non-manifold edges, orientation consistency, degenerate faces, duplicate
faces, connected components, bed fit as placed and rotated 90 degrees about Z, with a
margin per side.

Optional --thickness: approximate wall thickness by ray casting from face centroids (slow on
large meshes; see --samples/--max-faces). With --min-wall, thinner walls are reported as errors;
the limit itself must come from the supplier or material data.

Not checked (needs CAD or a slicer): overhangs, intersections between separate shells,
interference between parts. STL carries no units: the values are
reported in the file's units and assumed to be mm. 3MF units are read from the file. For 3MF,
all object meshes are merged and build-item transforms are ignored (reported in "notes").

The bed is always given explicitly as WxDxH in mm: use the usable build volume of the actual
supplier printer, not a nominal catalogue value.
"""

import argparse
import json
import math
import os
import struct
import sys
import xml.etree.ElementTree as ET
import zipfile


UNIT_TO_MM = {
    "micron": 0.001,
    "millimeter": 1.0,
    "centimeter": 10.0,
    "inch": 25.4,
    "foot": 304.8,
    "meter": 1000.0,
}


def parse_bed(spec):
    """Parse "WxDxH" (or a single number for a cube) in mm."""
    raw = spec.strip().lower().replace(" ", "")
    try:
        nums = [float(p) for p in raw.split("x")]
    except ValueError:
        nums = []
    if len(nums) == 1:
        nums = nums * 3
    if len(nums) != 3 or not all(math.isfinite(n) and n > 0 for n in nums):
        raise ValueError(f"bad bed '{spec}': use WxDxH in mm, e.g. 220x220x250 (usable volume of the supplier printer)")
    return tuple(nums)


def read_stl(path):
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) >= 84:
        (n,) = struct.unpack_from("<I", data, 80)
        if 84 + 50 * n == len(data):
            tris = []
            off = 84
            for _ in range(n):
                v = struct.unpack_from("<12f", data, off)
                tris.append((v[3:6], v[6:9], v[9:12]))
                off += 50
            return tris, "stl-binary", 1.0, []
    text = data.decode("utf-8", errors="replace")
    verts = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[0].lower() == "vertex":
            verts.append(tuple(float(p) for p in parts[1:]))
    if not verts or len(verts) % 3:
        raise ValueError("not a valid STL (binary size mismatch and no ASCII vertices)")
    tris = [tuple(verts[i : i + 3]) for i in range(0, len(verts), 3)]
    return tris, "stl-ascii", 1.0, []


def read_3mf(path):
    notes = []
    with zipfile.ZipFile(path) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith(".model")]
        if not names:
            raise ValueError("3MF without a .model part")
        tris = []
        scale = 1.0
        for name in names:
            root = ET.fromstring(zf.read(name))
            unit = root.attrib.get("unit", "millimeter")
            scale = UNIT_TO_MM.get(unit, 1.0)
            if unit not in UNIT_TO_MM:
                notes.append(f"unknown 3MF unit '{unit}', assumed mm")
            for mesh in root.iter():
                if not mesh.tag.endswith("}mesh") and mesh.tag != "mesh":
                    continue
                vs = []
                for el in mesh.iter():
                    if el.tag.endswith("vertex"):
                        vs.append((float(el.attrib["x"]), float(el.attrib["y"]), float(el.attrib["z"])))
                for el in mesh.iter():
                    if el.tag.endswith("triangle"):
                        a, b, c = (int(el.attrib[k]) for k in ("v1", "v2", "v3"))
                        tris.append((vs[a], vs[b], vs[c]))
            if any(el.tag.endswith("item") and "transform" in el.attrib for el in root.iter()):
                notes.append("build-item transforms present and ignored: bed fit uses object coordinates")
        if len(names) > 1:
            notes.append(f"{len(names)} model parts merged")
    tris = [tuple(tuple(c * scale for c in v) for v in t) for t in tris]
    return tris, "3mf", scale, notes


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def audit(tris, weld):
    index = {}
    faces = []
    for t in tris:
        ids = []
        for v in t:
            key = (round(v[0] / weld), round(v[1] / weld), round(v[2] / weld))
            if key not in index:
                index[key] = (len(index), v)
            ids.append(index[key][0])
        faces.append(tuple(ids))
    pts = [None] * len(index)
    for _, (i, v) in index.items():
        pts[i] = v

    degenerate = 0
    area = 0.0
    vol6 = 0.0
    seen = {}
    duplicates = 0
    undirected = {}
    directed = {}
    for f in faces:
        a, b, c = f
        pa, pb, pc = pts[a], pts[b], pts[c]
        n = cross(sub(pb, pa), sub(pc, pa))
        tri_area = 0.5 * math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
        if len({a, b, c}) < 3 or tri_area < (weld * weld):
            degenerate += 1
            continue
        area += tri_area
        vol6 += pa[0] * (pb[1] * pc[2] - pb[2] * pc[1]) - pa[1] * (pb[0] * pc[2] - pb[2] * pc[0]) + pa[2] * (pb[0] * pc[1] - pb[1] * pc[0])
        key = tuple(sorted(f))
        if key in seen:
            duplicates += 1
        seen[key] = True
        for u, v in ((a, b), (b, c), (c, a)):
            e = (u, v) if u < v else (v, u)
            undirected[e] = undirected.get(e, 0) + 1
            directed[(u, v)] = directed.get((u, v), 0) + 1

    boundary = sum(1 for k in undirected.values() if k == 1)
    nonmanifold = sum(1 for k in undirected.values() if k > 2)
    inconsistent = 0
    for (u, v), k in undirected.items():
        if k == 2 and (directed.get((u, v), 0) == 2 or directed.get((v, u), 0) == 2):
            inconsistent += 1

    parent = list(range(len(pts)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b, c in faces:
        for u, v in ((a, b), (b, c)):
            ru, rv = find(u), find(v)
            if ru != rv:
                parent[ru] = rv
    used = {v for f in faces for v in f}
    components = len({find(v) for v in used})

    xs = [p[0] for p in pts] or [0.0]
    ys = [p[1] for p in pts] or [0.0]
    zs = [p[2] for p in pts] or [0.0]
    bbox = {
        "min": [min(xs), min(ys), min(zs)],
        "max": [max(xs), max(ys), max(zs)],
        "size": [max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)],
    }
    volume = vol6 / 6.0
    errors = []
    if boundary:
        errors.append(f"{boundary} boundary (open) edges: mesh is not closed")
    if nonmanifold:
        errors.append(f"{nonmanifold} non-manifold edges (shared by more than two faces)")
    if inconsistent:
        errors.append(f"{inconsistent} edges with inconsistent face orientation")
    if degenerate:
        errors.append(f"{degenerate} degenerate faces")
    if duplicates:
        errors.append(f"{duplicates} duplicate faces")
    if not boundary and not nonmanifold and not inconsistent and volume < 0:
        errors.append("negative volume: faces point inward (normals inverted)")
    return {
        "triangles": len(faces),
        "vertices_welded": len(pts),
        "bbox_mm": {k: [round(x, 4) for x in v] for k, v in bbox.items()},
        "volume_mm3": round(volume, 3),
        "area_mm2": round(area, 3),
        "boundary_edges": boundary,
        "nonmanifold_edges": nonmanifold,
        "orientation_inconsistent_edges": inconsistent,
        "degenerate_faces": degenerate,
        "duplicate_faces": duplicates,
        "components": components,
        "watertight_manifold": not (boundary or nonmanifold or inconsistent),
        "errors": errors,
    }


def wall_thickness(tris, samples, max_faces):
    """Approximate wall thickness by ray casting from face centroids along the inward normal.

    For each sampled face, the distance to the nearest other face hit by the ray is taken as the
    local thickness. Needs a closed, consistently oriented mesh. Cost ~ samples x faces, so the
    mesh is refused above max_faces. Returns the thinnest samples found.
    """
    n = len(tris)
    if n > max_faces:
        return {"skipped": f"{n} faces > --max-faces {max_faces}; decimate or check in CAD/slicer"}
    eps = 1e-9

    def ray_hit(o, d, tri):
        v0, v1, v2 = tri
        e1, e2 = sub(v1, v0), sub(v2, v0)
        p = cross(d, e2)
        det = e1[0] * p[0] + e1[1] * p[1] + e1[2] * p[2]
        if abs(det) < eps:
            return None
        inv = 1.0 / det
        t0 = sub(o, v0)
        u = (t0[0] * p[0] + t0[1] * p[1] + t0[2] * p[2]) * inv
        if u < 0 or u > 1:
            return None
        q = cross(t0, e1)
        v = (d[0] * q[0] + d[1] * q[1] + d[2] * q[2]) * inv
        if v < 0 or u + v > 1:
            return None
        t = (e2[0] * q[0] + e2[1] * q[1] + e2[2] * q[2]) * inv
        return t if t > 1e-6 else None

    step = max(1, n // samples) if samples else 1
    results = []
    for i in range(0, n, step):
        a, b, c = tris[i]
        nn = cross(sub(b, a), sub(c, a))
        ln = math.sqrt(nn[0] ** 2 + nn[1] ** 2 + nn[2] ** 2)
        if ln < eps:
            continue
        d = (-nn[0] / ln, -nn[1] / ln, -nn[2] / ln)  # inward
        o = ((a[0] + b[0] + c[0]) / 3, (a[1] + b[1] + c[1]) / 3, (a[2] + b[2] + c[2]) / 3)
        best = None
        for j, other in enumerate(tris):
            if j == i:
                continue
            t = ray_hit(o, d, other)
            if t is not None and (best is None or t < best):
                best = t
        if best is not None:
            results.append((best, o))
    if not results:
        return {"skipped": "no ray hits: mesh open or inverted?"}
    results.sort(key=lambda r: r[0])
    return {
        "method": "ray from face centroid along inward normal to the nearest face (approximate; "
                  "underestimates near edges/fillets, misses walls thinner than the weld tolerance)",
        "samples": len(results),
        "min_mm": round(results[0][0], 4),
        "thinnest": [{"thickness_mm": round(t, 4), "at": [round(x, 3) for x in o]} for t, o in results[:5]],
    }


def bed_fit(size, bed, margin):
    bx, by, bz = bed
    ux, uy = bx - 2 * margin, by - 2 * margin
    sx, sy, sz = size
    as_placed = sx <= ux and sy <= uy and sz <= bz
    rotated = sy <= ux and sx <= uy and sz <= bz
    return {
        "bed_mm": list(bed),
        "margin_per_side_mm": margin,
        "usable_xy_mm": [ux, uy],
        "fits_as_placed": as_placed,
        "fits_rotated_90": rotated,
        "fits": as_placed or rotated,
        "note": "bed sizes are nominal; add the brim the material needs to the margin and confirm the supplier printer",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("path")
    ap.add_argument("--bed", help="usable build volume WxDxH in mm, e.g. 220x220x250")
    ap.add_argument("--margin", type=float, default=5.0, help="free margin per side in mm (default 5)")
    ap.add_argument("--weld", type=float, default=1e-5, help="vertex weld tolerance in file units")
    ap.add_argument("--thickness", action="store_true", help="approximate wall thickness by ray casting")
    ap.add_argument("--min-wall", type=float, help="flag walls thinner than this (mm); the limit must come "
                    "from the supplier/material data, not from this script")
    ap.add_argument("--samples", type=int, default=400, help="faces sampled for --thickness (default 400)")
    ap.add_argument("--max-faces", type=int, default=20000, help="refuse --thickness above this face count")
    args = ap.parse_args(argv)
    try:
        ext = os.path.splitext(args.path)[1].lower()
        tris, fmt, scale, notes = read_3mf(args.path) if ext == ".3mf" else read_stl(args.path)
    except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError, KeyError, struct.error) as exc:
        print(json.dumps({"file": args.path, "error": f"cannot read: {exc}"}, indent=2))
        return 3
    result = {"file": args.path, "format": fmt, "units": "mm (assumed for STL)" if fmt.startswith("stl") else "mm"}
    result.update(audit(tris, args.weld))
    if notes:
        result["notes"] = notes
    code = 1 if result["errors"] else 0
    if args.thickness:
        if result["watertight_manifold"]:
            result["wall_thickness"] = wall_thickness(tris, args.samples, args.max_faces)
            mn = result["wall_thickness"].get("min_mm")
            if args.min_wall is not None and mn is not None and mn < args.min_wall:
                result["wall_thickness"]["below_min_wall"] = True
                result["errors"].append(f"wall {mn} mm thinner than --min-wall {args.min_wall} mm")
                code = 1
        else:
            result["wall_thickness"] = {"skipped": "mesh not closed/consistent: fix integrity first"}
    if args.bed:
        try:
            result["bed_fit"] = bed_fit(result["bbox_mm"]["size"], parse_bed(args.bed), args.margin)
        except ValueError as exc:
            print(json.dumps({"file": args.path, "error": str(exc)}, indent=2))
            return 3
        if code == 0 and not result["bed_fit"]["fits"]:
            code = 2
    print(json.dumps(result, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
