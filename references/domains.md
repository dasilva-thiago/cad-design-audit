# Domain checklists and adversarial questions

Use one pass per domain. Each item says what to check and what evidence would settle it. A checklist item without evidence is a finding (PENDING, BLOCKED or MINOR), not a pass.

---

## A. Geometric integrity

| Check | How | Evidence that settles it |
|---|---|---|
| Solid validity | BRep check (Fusion body is solid; STEP via OCC `BRepCheck_Analyzer`); mesh: every edge shared by exactly two faces, consistent orientation | Tool output quoted in the report |
| Body count | One intended solid per part; extra tiny bodies are boolean debris | Solid count per part |
| Self-intersection, open surfaces, non-manifold edges | Mesh audit; CAD "check geometry" | Script/tool result |
| Duplicate or overlapping bodies | Volume of union vs sum of volumes; interference analysis between bodies of the same part | Interference result = none |
| Wall thickness and minimum feature size | Fusion `BRepBody.findThicknessAtFace`, section views, or measured sections; compare with process minimums **from the supplier or material data**, not from memory | Thinnest wall located and compared to a cited limit |
| Holes and slots | Diameter vs fastener, clearance class, print compensation, depth vs insert length | Table: hole, purpose, size, source of the size |
| Clearances and interferences | Interference analysis of the assembled state, plus minimum distance at every mating pair at nominal **and** worst-case | Results per pair, with the tolerance assumption |
| Parametric dependencies | Every named parameter traces to a verified value or a justified allowance; no orphan or hard-coded critical dimension | Parameter table with source column |
| Datums and coordinate system | Same origin, axis directions and handedness in CAD, drawings and measurement records; mirrored import check on an asymmetric feature | Side-by-side comparison of one asymmetric feature |
| Bounding box | Matches the intended envelope and the stated part size | Measured bbox per part |

Adversarial questions: Is the "clearance" really clearance at the worst tolerance? Was a dimension typed instead of linked to a parameter? Could the model be mirrored or shifted relative to the measured part? Is any thin wall hidden behind a fillet or cutout?

---

## B. Mechanical integrity

| Check | Questions | Evidence |
|---|---|---|
| Load path | Where does each load enter and leave? Through screws, bosses, walls, feet, cables? Is any load carried by a feature never meant for it (a lip, a snap, a connector)? | Free-body sketch or written load path |
| Loads | Static (weight, screw preload), handling (drop, lifting by the lid), dynamic (fan imbalance, HDD spin), thermal | Stated load cases with values and sources, or explicitly ASSUMED bounds |
| Stress concentration | Sharp internal corners at boss roots, clip roots, slots near edges, holes near walls | Root radius and distance to edges noted |
| Bending, torsion, buckling | Long thin walls, cantilevered panels, tall standoffs, lids spanning large areas | Span/thickness, support spacing, analysis or test |
| Anisotropy (additive) | For every loaded feature: does the critical stress act across layers? (Layer interfaces are weaker than in-plane material in FDM; magnitude is material- and process-specific) | Print orientation per part + direction of critical stress |
| Fasteners and threads | Thread engagement, screw type for the material (machine screw in insert vs self-tapping into plastic), clamp length, washer under head | Fastener table with type, length, engagement |
| Bosses and inserts | Boss outer diameter vs hole, wall around insert, root fillet, support by ribs/walls, insert hole per insert maker, orientation of the boss axis vs layers | Insert datasheet + boss geometry + orientation |
| Snap-fits | Required deflection, strain vs permissible strain for the material and print direction, root radius, assembly/disassembly force, number of cycles, preload after assembly | Calculation with cited permissible strain, or coupon test |
| Creep and preload loss | Any plastic part under permanent load (screw clamp directly on plastic, compressed elastomer, snap left deflected), especially warm | Design that limits clamp on plastic (metal sleeve, insert shoulder, compression limiter) or test |
| Vibration | Sources (fans, drives), isolation (elastomer), resonant panels, loosening of screws in plastic | Isolation present; screws retained; inspection after test |
| Temperature | Maximum part temperature vs the material's heat deflection temperature **under the relevant load**; thermal expansion mismatch with metal/PCB | Expected/measured temperature, datasheet HDT at stated load |
| Material suitability | Process, environment (UV, heat, chemicals), flammability, long-term behavior | Datasheet of the actual material and supplier |

Adversarial questions: What breaks first if someone lifts the assembly by the lid? What happens to the screw clamp after months at operating temperature? Does the clip have to bend across layers? What loosens under fan vibration?

---

## C. Manufacturing feasibility

| Check | Questions | Evidence |
|---|---|---|
| Process and material | Is the chosen process right for size, accuracy, quantity and function? Is the material decision made, or still "X or Y"? Which properties change between the candidates? | Decision record; datasheets of the candidates |
| Build volume | Does each part fit the **actual supplier printer** with margin for brim/skirt and the process' edge exclusion? | Supplier printer named; part bbox + brim vs bed |
| Orientation per part | Chosen to put critical stresses in-plane, cosmetic faces on the best surface, and minimize supports | Orientation written per part with reason |
| Overhangs, bridges, supports | Downward faces beyond the process limit, bridges length, enclosed supports that cannot be removed | List of support regions and how they are removed |
| Warping and shrinkage | Large flat areas, sharp corners, high-shrink materials, need for enclosed/heated chamber | Material shrink data, supplier chamber, geometry mitigations |
| Dimensional accuracy | General tolerance class **declared by the supplier** for that material/orientation; hole undersizing; scale error over long spans | Supplier statement or coupon measurement; compensation parameter |
| Clearances and fits | Fit clearances chosen from the supplier/coupon tolerance, not from generic tables | Coupon results |
| Inserts and post-processing | Insert installation access, hole size from insert maker, support removal, cosmetic finishing | Insert datasheet; steps listed |
| Segmentation | Why is each part split? Bed size, access, material, replaceability? Can the split be avoided? Where do joints go and how do they align and fasten? | Written reason per split |
| Supplier capability | Materials offered, printer volume, tolerance declared, coupon/test print offered, cost | Supplier quote or written answer |
| Cost and time | Mass, print time, reprint risk (one large part vs several small ones) | Slicer estimate or supplier quote |

Adversarial questions: Does it really fit the bed once the brim the material needs is added? Which face ends up on supports? Is the "tolerance" a supplier promise or a guess? If this part fails, how much has to be reprinted?

---

## D. Function, assembly and maintenance

| Check | Questions | Evidence |
|---|---|---|
| Assembly sequence | Is there an order in which every part goes in without forcing? Are inserts installed before parts that block access? | Written sequence; interference-free in each step |
| Tool access | Straight path for the screwdriver to every screw; hand space; hidden screws reachable | Access line per screw |
| Connectors | Real plugs (with their overmolded boots) fully insert; mating direction clear; strain on PCB connectors carried by the enclosure | Plug dimensions measured; insertion depth vs wall |
| Cable routing | Bend radius, length, fixation, clearance to fans/hot parts/sharp edges, disconnect points for removable parts | Route drawn; lengths checked |
| Maintenance | Which parts must come out for common service? What must be disconnected? Is anything glued or fragile (fine-pitch flat cables) on the service path? | Service procedure written |
| Thermal management | Heat sources and their power; airflow path from inlet to outlet; recirculation; vent area vs fan; component temperature limits; dust | Thermal budget or measured soak test |
| Electrical isolation and protection | Metal parts near live/powered areas; standoffs under the PCB; nothing conductive loose; ESD-sensitive parts protected | Clearance check under the PCB; materials |
| Fire and safety | Power level and source type; potential ignition sources; enclosure material flammability rating (e.g. UL 94 class) vs what the application needs; unattended operation | Material datasheet rating; power source data; applicable standard read by a competent person |
| Protection | Fingers away from fans, dust, liquids, curious users, strain on cables | Guarding feature; ingress expectation |

Write the assembly sequence as a table and check each step against the geometry; an assembly that only works "in the final state" fails here:

| Step | Part / operation | Fastener and tool | Access check (straight tool path, hand space) | Blocks what later? | Connections made |
|---|---|---|---|---|---|

Do the same in reverse for the most common maintenance task.

Adversarial questions: Which connector breaks first during maintenance? Can the part be removed without unplugging a fragile flat cable? Where does the hot air go, and does it come back in? What happens if the fan stops? Is the enclosure material acceptable for an unattended powered device?

---

## E. Product design and appearance

Judge appearance separately from engineering. Aesthetic preference is not an engineering requirement; but visible features must be intentional.

| Check | Questions |
|---|---|
| Purpose of every visible line | Does each seam, groove, split line and step correspond to a real part boundary or a stated design intent? A line that implies a joint where the part is continuous is a defect |
| Segmentation | Is every part split justified (bed, access, function)? Was a split copied from another part where its reason does not apply? |
| Primary face | Is the face the user looks at (front panel, display face) clean and continuous? Are joints routed away from it? |
| Seam treatment | Real seams treated consistently (e.g. reveal/shadow gap, lip, chamfer) and sized for the process' step and gap variation |
| Proportions and alignment | Openings aligned with each other; symmetry where it matters; consistent radii and chamfers |
| Manufacturability of the look | Can the intended finish be printed (face on bed, no support marks on cosmetic faces, layer lines direction)? |

Adversarial questions: If a product designer saw this, what would look improvised? What line would a user mistake for a crack or a cheap joint?

---

## F. Documentation and traceability

| Check | Questions | Evidence |
|---|---|---|
| CAD vs documents | Do dimensions, part counts, materials and decisions in CAD match the documents? | Spot-check list with results |
| Parameter traceability | Every critical parameter → verified source or written allowance | Parameter table |
| Revisions | Are document revisions and dates consistent? Does a newer decision leave stale text elsewhere? | Search for superseded values |
| Quantities and purchasing | Fasteners, inserts, spares match the current design | BOM vs design count |
| Instructions | Assembly, orientation, material, supplier notes present before release | Package checklist |
| Assumptions and open items | Listed, owned, with the test that will close them | Open-items table |
| Conflicts | Two documents stating different values or rules | Each conflict listed with both sources |
| Test timing | Is each verification scheduled **before** the decision it informs (e.g. a thermal test before choosing the material, a coupon before final fits)? | Plan order |
