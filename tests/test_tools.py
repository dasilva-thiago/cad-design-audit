"""Tests for the bundled scripts, on synthetic meshes and chains with known answers.

Run:  python -m unittest discover -s tests -v      (from the skill folder)
Standard library only.
"""

import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(HERE), "scripts")
sys.path.insert(0, SCRIPTS)

import mesh_audit  # noqa: E402
import stack_up  # noqa: E402


def box_tris(x0, y0, z0, x1, y1, z1):
    """Closed box, outward normals (counter-clockwise seen from outside)."""
    p = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    quads = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (1, 2, 6, 5), (3, 0, 4, 7)]
    tris = []
    for a, b, c, d in quads:
        tris.append((p[a], p[b], p[c]))
        tris.append((p[a], p[c], p[d]))
    return tris


def write_binary_stl(path, tris):
    with open(path, "wb") as fh:
        fh.write(b"\0" * 80)
        fh.write(struct.pack("<I", len(tris)))
        for t in tris:
            fh.write(struct.pack("<3f", 0, 0, 0))
            for v in t:
                fh.write(struct.pack("<3f", *v))
            fh.write(b"\0\0")


def write_ascii_stl(path, tris):
    with open(path, "w") as fh:
        fh.write("solid t\n")
        for t in tris:
            fh.write(" facet normal 0 0 0\n  outer loop\n")
            for v in t:
                fh.write(f"   vertex {v[0]} {v[1]} {v[2]}\n")
            fh.write("  endloop\n endfacet\n")
        fh.write("endsolid t\n")


def write_3mf(path, tris, unit="millimeter"):
    verts, idx, faces = [], {}, []
    for t in tris:
        f = []
        for v in t:
            if v not in idx:
                idx[v] = len(verts)
                verts.append(v)
            f.append(idx[v])
        faces.append(f)
    vx = "".join(f'<vertex x="{v[0]}" y="{v[1]}" z="{v[2]}"/>' for v in verts)
    tx = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in faces)
    model = (f'<?xml version="1.0"?><model unit="{unit}" '
             f'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
             f'<resources><object id="1" type="model"><mesh><vertices>{vx}</vertices>'
             f'<triangles>{tx}</triangles></mesh></object></resources>'
             f'<build><item objectid="1"/></build></model>')
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("3D/3dmodel.model", model)


def run_mesh(path, *extra):
    proc = subprocess.run([sys.executable, os.path.join(SCRIPTS, "mesh_audit.py"), path, *extra],
                          capture_output=True, text=True)
    return proc.returncode, json.loads(proc.stdout)


class MeshAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def path(self, name):
        return os.path.join(self.tmp, name)

    def test_closed_cube_binary(self):
        p = self.path("cube.stl")
        write_binary_stl(p, box_tris(0, 0, 0, 10, 10, 10))
        code, r = run_mesh(p)
        self.assertEqual(code, 0)
        self.assertTrue(r["watertight_manifold"])
        self.assertAlmostEqual(r["volume_mm3"], 1000.0, places=2)
        self.assertEqual(r["components"], 1)
        self.assertEqual(r["bbox_mm"]["size"], [10.0, 10.0, 10.0])

    def test_closed_cube_ascii(self):
        p = self.path("cube_ascii.stl")
        write_ascii_stl(p, box_tris(0, 0, 0, 20, 10, 5))
        code, r = run_mesh(p)
        self.assertEqual(code, 0)
        self.assertEqual(r["format"], "stl-ascii")
        self.assertAlmostEqual(r["volume_mm3"], 1000.0, places=2)

    def test_open_box_detected(self):
        p = self.path("open.stl")
        write_binary_stl(p, box_tris(0, 0, 0, 10, 10, 10)[:-2])  # one side missing
        code, r = run_mesh(p)
        self.assertEqual(code, 1)
        self.assertEqual(r["boundary_edges"], 4)
        self.assertFalse(r["watertight_manifold"])

    def test_flipped_face_detected(self):
        tris = box_tris(0, 0, 0, 10, 10, 10)
        a, b, c = tris[0]
        tris[0] = (a, c, b)
        p = self.path("flipped.stl")
        write_binary_stl(p, tris)
        code, r = run_mesh(p)
        self.assertEqual(code, 1)
        self.assertEqual(r["orientation_inconsistent_edges"], 3)

    def test_inverted_normals_detected(self):
        tris = [(a, c, b) for a, b, c in box_tris(0, 0, 0, 10, 10, 10)]
        p = self.path("inverted.stl")
        write_binary_stl(p, tris)
        code, r = run_mesh(p)
        self.assertEqual(code, 1)
        self.assertLess(r["volume_mm3"], 0)
        self.assertTrue(any("inverted" in e for e in r["errors"]))

    def test_two_cubes_sharing_an_edge_nonmanifold(self):
        tris = box_tris(0, 0, 0, 10, 10, 10) + box_tris(10, 10, 0, 20, 20, 10)
        p = self.path("edge_share.stl")
        write_binary_stl(p, tris)
        code, r = run_mesh(p)
        self.assertEqual(code, 1)
        self.assertEqual(r["nonmanifold_edges"], 1)

    def test_duplicate_face_detected(self):
        tris = box_tris(0, 0, 0, 10, 10, 10)
        tris.append(tris[0])
        p = self.path("dup.stl")
        write_binary_stl(p, tris)
        code, r = run_mesh(p)
        self.assertEqual(code, 1)
        self.assertEqual(r["duplicate_faces"], 1)

    def test_3mf_units_converted(self):
        p = self.path("cube_cm.3mf")
        write_3mf(p, box_tris(0, 0, 0, 1, 2, 3), unit="centimeter")
        code, r = run_mesh(p)
        self.assertEqual(code, 0)
        self.assertEqual(r["bbox_mm"]["size"], [10.0, 20.0, 30.0])
        self.assertAlmostEqual(r["volume_mm3"], 6000.0, places=1)

    def test_bed_fit_with_and_without_brim_margin(self):
        # 208.25 x 165 x 24 part on a 220 x 220 bed: fits with 5 mm, not with an 8 mm brim
        p = self.path("base.stl")
        write_binary_stl(p, box_tris(0, 0, 0, 208.25, 165, 24))
        code, r = run_mesh(p, "--bed", "220x220x250", "--margin", "5")
        self.assertEqual(code, 0)
        self.assertTrue(r["bed_fit"]["fits"])
        code, r = run_mesh(p, "--bed", "220x220x250", "--margin", "8")
        self.assertEqual(code, 2)
        self.assertFalse(r["bed_fit"]["fits"])

    def test_rotation_used_for_fit(self):
        p = self.path("long.stl")
        write_binary_stl(p, box_tris(0, 0, 0, 200, 240, 10))
        code, r = run_mesh(p, "--bed", "250x210x220", "--margin", "5")
        self.assertEqual(code, 0)
        self.assertFalse(r["bed_fit"]["fits_as_placed"])
        self.assertTrue(r["bed_fit"]["fits_rotated_90"])

    def test_wall_thickness_hollow_box(self):
        # outer 40 x 30 x 20, cavity leaves 2 mm walls in X and Z, 1 mm walls in Y
        outer = box_tris(0, 0, 0, 40, 30, 20)
        inner = [(a, c, b) for a, b, c in box_tris(2, 1, 2, 38, 29, 18)]
        p = self.path("hollow.stl")
        write_binary_stl(p, outer + inner)
        code, r = run_mesh(p, "--thickness", "--samples", "48")
        self.assertEqual(code, 0)
        self.assertEqual(r["components"], 2)
        self.assertAlmostEqual(r["volume_mm3"], 40 * 30 * 20 - 36 * 28 * 16, places=1)
        self.assertAlmostEqual(r["wall_thickness"]["min_mm"], 1.0, places=3)
        code, r = run_mesh(p, "--thickness", "--samples", "48", "--min-wall", "1.2")
        self.assertEqual(code, 1)
        self.assertTrue(r["wall_thickness"]["below_min_wall"])

    def test_thickness_skipped_on_open_mesh(self):
        p = self.path("open2.stl")
        write_binary_stl(p, box_tris(0, 0, 0, 10, 10, 10)[:-2])
        code, r = run_mesh(p, "--thickness")
        self.assertIn("skipped", r["wall_thickness"])

    def test_bad_bed_spec(self):
        p = self.path("c.stl")
        write_binary_stl(p, box_tris(0, 0, 0, 10, 10, 10))
        code, r = run_mesh(p, "--bed", "ender3")
        self.assertEqual(code, 3)

    def test_unreadable_file(self):
        p = self.path("bad.stl")
        with open(p, "wb") as fh:
            fh.write(b"not a mesh")
        code, r = run_mesh(p)
        self.assertEqual(code, 3)


class StackUpTests(unittest.TestCase):
    def test_worst_case_and_rss_independent(self):
        chain = {"requirement": {"min": 0.0}, "contributors": [
            {"name": "a", "nominal": 10.0, "tol": 0.1, "sign": 1, "source": "x"},
            {"name": "b", "nominal": 9.8, "tol": 0.1, "sign": -1, "source": "x"},
            {"name": "c", "nominal": 0.0, "tol": 0.1, "sign": 1, "source": "x"}]}
        r, ok = stack_up.analyse(chain)
        self.assertAlmostEqual(r["nominal_gap"], 0.2)
        self.assertAlmostEqual(r["worst_case"]["min"], -0.1)
        self.assertFalse(ok)
        self.assertAlmostEqual(r["rss"]["min"], 0.2 - (3 * 0.01) ** 0.5, places=4)

    def test_correlated_group_adds_linearly(self):
        chain = {"requirement": {"min": 0.0}, "contributors": [
            {"name": "a", "nominal": 1.0, "tol": 0.3, "sign": 1, "group": "scale", "source": "x"},
            {"name": "b", "nominal": 0.0, "tol": 0.3, "sign": -1, "group": "scale", "source": "x"}]}
        r, _ = stack_up.analyse(chain)
        self.assertAlmostEqual(r["rss"]["min"], 1.0 - 0.6)
        self.assertEqual(r["rss"]["independent_groups"], 1)

    def test_asymmetric_tolerance(self):
        chain = {"contributors": [{"name": "hole", "nominal": 3.0, "tol_plus": 0.0, "tol_minus": 0.4,
                                   "sign": 1, "source": "coupon"}]}
        r, ok = stack_up.analyse(chain)
        self.assertAlmostEqual(r["worst_case"]["min"], 2.6)
        self.assertAlmostEqual(r["worst_case"]["max"], 3.0)
        self.assertTrue(ok)

    def test_missing_source_warns(self):
        chain = {"contributors": [{"name": "x", "nominal": 1.0, "tol": 0.1, "sign": 1}]}
        r, _ = stack_up.analyse(chain)
        self.assertIn("warnings", r)


if __name__ == "__main__":
    unittest.main()
