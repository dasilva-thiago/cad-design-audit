# Failure-mode catalog

Known mechanisms to recognize during an audit. Each entry: mechanism, what to look for in the design, evidence needed to accept the design, typical corrections. Source IDs refer to `sources.md`. Numbers here are examples with their scope; never apply them to another material, process or supplier without saying so.

---

## FM-01 Interlayer failure in additively made parts
- **Mechanism:** In FDM/FFF the bond between layers is weaker than the material along the deposited roads; tensile strength depends on build direction (S01: ABS FDM tensile strength ≈ 65–72 % of the molded material for one tested road overlap; compressive ≈ 80–90 %). The ratio for other materials, printers and settings is different.
- **Look for:** clips, bosses, hooks, thin posts, screw columns whose critical tensile/bending stress acts across layers in the chosen orientation.
- **Accept when:** the orientation puts the critical stress in-plane, or the interlayer property of the actual material is known and the stress is checked against it, or a coupon in the final orientation passes.
- **Corrections:** reorient the part or print the feature as a separate part in its strong orientation; add root radius and thickness; change the joint type (screw + insert instead of clip).

## FM-02 Screw boss cracking and pull-out
- **Mechanism:** Radial stress from insert installation or self-tapping screws splits thin bosses; pull-out tears layers when the screw axis is along the build direction; unsupported tall bosses bend.
- **Look for:** boss wall thinner than the insert maker's recommendation; bosses standing free without ribs; hole size not taken from the insert/screw maker; boss axis along Z with axial load.
- **Accept when:** hole and wall from the insert datasheet; boss tied to walls/ribs; pull-out/torque checked on a coupon in final orientation (manufacturer-sponsored insert data exist but are not independent, S06).
- **Corrections:** ribs to walls, larger boss, insert instead of self-tapping, through-bolt with nut, metal standoff.

## FM-03 Creep and preload loss
- **Mechanism:** Polymers deform slowly under constant load, faster when warm; a screw clamping plastic loses preload; a permanently deflected clip relaxes (S09 shows relaxation in PETG; quantitative data for printed bolted joints are scarce).
- **Look for:** screws clamping printed plastic directly, elastomer compressed by plastic, snaps that stay deflected, lids held only by friction, warm zones near heat sources.
- **Accept when:** the clamp bears on metal (insert flange, sleeve, compression limiter) or the elastomer defines the clamp; nothing stays deflected; temperature margin to the material's HDT under load is known.
- **Corrections:** compression limiters, inserts with shoulders, elastomer washers sized to set the clamp, ASA/other higher-HDT material if hot.

## FM-04 Snap-fit failure
- **Mechanism:** Strain at the root exceeds the permissible strain during assembly (fracture) or the clip is under permanent strain (relaxation). For AM the injection-molding rules do not transfer directly; orientation dominates (S03, S04, S05).
- **Look for:** clips bending across layers; no root radius; permissible strain taken from an injection-molding guide; repeated service cycles; clip used as the only retention against vibration.
- **Accept when:** strain calculated with a cited permissible strain for the actual material/orientation and a margin for repeated use, or coupon-tested; retention does not rely on the clip alone where vibration or misuse matters.
- **Corrections:** lay the beam in the build plane, make the clip a separate replaceable part, use screws for retention and clips only for positioning.

## FM-05 Tolerance stack closes a clearance
- **Mechanism:** Nominal clearance is positive, but the sum of contributor variations at worst case is larger. Common errors: budgeting a long feature with the tolerance class of a short one; treating correlated errors (same printer scale error on both parts) as independent; ignoring measurement uncertainty of the input dimensions.
- **Look for:** lips, sliding fits, pins, port openings, parts that span long distances; clearances justified by a small-feature tolerance class.
- **Accept when:** a stack with every contributor listed, the right tolerance for the governing length, correlation stated, and the measurement uncertainty added (see `methods.md`).
- **Corrections:** locate on a few short datums instead of a long perimeter; compliant features; coupon measuring the supplier's scale error over a comparable length; adjustable features (slots, shims).

## FM-06 Holes and pins out of size (additive)
- **Mechanism:** Printed holes come out undersized and out of round; reported 0.1–0.5 mm on common printers depending on wall generator and material (S11, practitioner data).
- **Look for:** fits designed to nominal fastener size; press fits without a test.
- **Accept when:** compensation chosen from a coupon of the same supplier/material, or the hole is drilled/reamed after printing.

## FM-07 Warping and dimensional distortion
- **Mechanism:** Thermal contraction of hot layers on cooler ones curls large flat parts and corners; worse in high-shrink materials (ABS/ASA) on open printers (S12 for thin ABS plates; vendor guides for others).
- **Look for:** large flat bases or lids, sharp corners, thick solid areas, high-shrink material, unknown supplier chamber, brims that do not fit the bed.
- **Accept when:** material and printer known; geometry mitigations (ribs instead of thick plates, corner radii); supplier confirms process.

## FM-08 Part does not fit the build volume
- **Mechanism:** Part bbox plus brim/skirt and the printer's usable area exceed the bed; diagonal placement rarely helps for long rectangles.
- **Look for:** "fits" claims made against nominal bed size without brim; supplier printer not named.
- **Accept when:** bed of the actual supplier printer known; margin covers the brim the material needs.

## FM-09 Assembly impossible or unmaintainable
- **Mechanism:** Every part fits in the final state but there is no sequence to get there (screw behind a wall, insert installed after the part that blocks the iron, cable shorter than the path during assembly), or service requires disconnecting a fragile connector.
- **Look for:** screws without straight tool access; connectors that cross a part joint; removable modules wired to fine-pitch connectors; no written assembly order.
- **Accept when:** a written sequence checked step by step; an accessible disconnect point at every removable joint.

## FM-10 Connector and cable failures
- **Mechanism:** Plug boots larger than the opening; wall too deep for the plug's metal length; cable weight carried by PCB solder joints; bend radius violated; cable rubbing a fan or a sharp edge.
- **Accept when:** real plugs measured; opening depth vs plug metal length checked; strain relief on the enclosure; route with clips.

## FM-11 Thermal: no flow path or recirculation
- **Mechanism:** Inlet and outlet too close or unbalanced, fan recirculates its own exhaust, vents blocked by internal parts, heat source far from the outlet; plastic near hot parts creeps or softens.
- **Look for:** no thermal budget; vent area much smaller than fan area; outlets behind components; temperature-sensitive parts (drives, batteries) in the exhaust path; thermal test planned only after printing.
- **Evidence:** power dissipation per source, component limits, a soak test on a mock-up with the real vent layout, or analysis with stated assumptions. Rules of thumb such as "vent area ≥ 1.5 × fan area" come from trade sources (S16) and are only sanity checks.

## FM-12 Vibration, noise and loosening
- **Mechanism:** Fans and drives excite thin panels; screws in plastic loosen; rigid mounts transmit noise.
- **Accept when:** elastomer isolation, retained fasteners, stiff panels or ribs; checked after a run-in test.

## FM-13 PCB stress and support
- **Mechanism:** Uneven standoffs or overtightened screws bend the board; strain at BGA/fine-pitch joints can crack them; limits depend on strain rate (S15 is the test guideline; acceptable limits are defined elsewhere and are component-specific).
- **Look for:** standoff heights not tied to measured underside clearances; screws pulling a warped board onto rigid bosses; supports far from connectors that take plug forces.
- **Accept when:** support heights from measured data; floating or shimmed supports; plug forces supported near the connector; fit check without forcing.

## FM-14 Electrical isolation and fire
- **Mechanism:** Conductive debris, metal parts or screws touching the board underside; overheating components igniting nearby plastic; enclosure material not suited for an unattended powered device.
- **Look for:** metal near the PCB underside; no statement of the material flammability rating; power source class and ignition sources not considered. Common FDM PETG and ASA are often HB-rated or unrated; flame-retardant grades exist (S13, S14). Product safety standards for ICT equipment (IEC 62368-1) define requirements by power source class; interpretations vary (S17), so read the current edition or consult a certification body.
- **Accept when:** the application's safety requirement is stated and the material/design meet it with evidence, or the user accepts the residual risk in writing.

## FM-15 Unjustified segmentation and visible lines
- **Mechanism:** A split copied from another part (e.g. base + lid) where its reason (access) does not apply adds a seam, fasteners and tolerance; a model drawn as several bodies shows false edges; decorative lines cross the primary face.
- **Look for:** parts or seams without a written functional reason; lines on the display/front face; a continuous part modeled as several bodies.
- **Accept when:** every split and visible line has a reason; primary face clean; seams treated consistently.

## FM-16 Documentation drift
- **Mechanism:** A later decision changes counts or dimensions but older documents (BOM, summaries, drawings) keep the old value; tests are scheduled after the decisions they should inform.
- **Look for:** quantities in the BOM vs the current design; superseded dimensions in summaries; a verification gate placed after manufacturing for an input of material selection.
