# CAD inspection by artifact type

Decide in Phase 0 what each available artifact allows. Report the coverage honestly: what was opened, with which tool, and which conclusions therefore remain unverified.

## Coverage matrix

| Artifact | Reliable automated checks | Needs judgment or other evidence | Cannot provide |
|---|---|---|---|
| Live CAD session (e.g. Fusion via API/MCP) | Body validity, volumes, bounding boxes, interference, minimum distances, wall thickness at faces, parameter table and expressions, component structure | Design intent, load paths, print orientation choice | Material behavior, real tolerances, printer results |
| STEP (BRep) | Validity (OCC `BRepCheck_Analyzer`), solid count, volume, bounding box, boolean common between parts (interference volume), point-in-solid tests | Same as above | Parameters and design history |
| STL / 3MF (mesh) | Watertight/manifold edges, orientation consistency, degenerate/duplicate faces, components, volume, bbox, bed fit (`scripts/mesh_audit.py`) | Thin walls (needs ray casting or slicer), small features | Exact curvature, parameters, units in STL (STL has no units; 3MF does) |
| Engineering drawings / DXF | Dimensions and tolerances as stated, consistency with registers | Whether drawn geometry matches the model | 3D interferences |
| Screenshots / renders | Presence and rough arrangement of features, visual coherence, obvious collisions | Everything dimensional | Measurements (do not measure by pixels unless the image is a calibrated scan with a scale) |
| Measurement registers | Status, method and uncertainty of inputs | Whether the measured point was the right one (inspect photos of instrument contact points) | Anything not measured |
| Datasheets / supplier statements | Declared properties under stated test conditions | Applicability to the actual orientation, process and temperature | Independent validation (manufacturer data is a claim) |

If the needed artifact is missing, ask for it specifically, e.g. "export each part as STEP and as STL in mm, plus the assembled state as one STEP".

## Autodesk Fusion API (via MCP or scripts)

Verified in the current API reference (S19) unless marked otherwise:
- **Interference:** `design.createInterferenceInput(entities)` → `design.analyzeInterference(input)` returns `InterferenceResults` (check its `count`, not a boolean). `InterferenceInput.areCoincidentFacesIncluded` defaults to False — set it True when touching faces matter. `InterferenceResults.createBodies` works only in direct-modeling designs.
- **Minimum distance:** `app.measureManager.measureMinimumDistance(a, b)` accepts occurrences, bodies, faces, edges, vertices, construction geometry, sketch entities; temporary BRep bodies are not accepted (add them to the design first); some users report failures with two occurrences — pass bodies; the order of the returned positions is not guaranteed.
- **Wall thickness:** `BRepBody.findThicknessAtFace` exists in the reference (S19); confirm its signature before use.
- **Bounding boxes:** `BRepBody.orientedMinimumBoundingBox` and `MeasureManager.getOrientedBoundingBox` serve different purposes (S19 forum). Axis-aligned `boundingBox` and `physicalProperties` (volume, area, mass) are commonly used — **confirm names in the current reference before relying on them** (not verified in the research for this skill).
- **Parameters:** read user parameters and their expressions; every critical one should trace to a register entry or an allowance.

Never claim a Fusion check ran unless its output is in the conversation. If the CAD session is unavailable, say so and fall back to exported files.

## STEP with OCC (CadQuery/OCP) — optional environment

Requires a Python environment with OCP (CadQuery's kernel bindings); not bundled here. Typical checks:
- validity: `BRepCheck_Analyzer(shape).IsValid()`
- solid count: number of solids per part (expect 1)
- volume compared with a range **derived from the parameters**, never pasted from the result
- interference between two parts: volume of their boolean common; touching vs overlapping needs a tolerance
- point classification to confirm a feature is on the intended face

## Mesh checks (bundled)

`python scripts/mesh_audit.py part.stl [--bed 220x220x250] [--margin 5]` prints JSON: triangle count, bbox, volume, surface area, boundary edges, non-manifold edges, orientation consistency, degenerate and duplicate faces, connected components, bed fit (as placed and rotated 90° about Z). Exit code 0 = no integrity errors, 1 = integrity errors, 2 = does not fit the bed, 3 = cannot read.

`--thickness [--min-wall X]` adds an approximate wall-thickness scan (ray from each sampled face centroid along the inward normal to the nearest face). It underestimates near edges and fillets and is slow on large meshes (`--samples`, `--max-faces`); treat it as a locator of thin regions to confirm in CAD. The `--min-wall` limit must come from the supplier or material data.

What it does not do: overhang analysis, self-intersection between separate shells, interference between parts. Use the CAD or a slicer for those and say so.

## Screenshots and renders

Use them for appearance (domain E), arrangement and obvious conflicts. Name the view and what was seen. Do not derive dimensions from them.
