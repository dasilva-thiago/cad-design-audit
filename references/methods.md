# Methods and calculations

Every calculation in a report shows: inputs with status and source, the formula, the assumptions, the result, and what would invalidate it. Use the scripts when possible so the arithmetic is reproducible.

---

## 1. Tolerance stack-up

**Steps**
1. Draw the chain: from the functional requirement (gap ≥ 0, clearance ≥ x) through every contributing dimension, each with a direction (+ increases the gap, − decreases it).
2. Give each contributor a tolerance **from its real source**: supplier declaration, coupon measurement, measurement uncertainty of the input dimension, general tolerance class only if it is the contractual basis.
3. Use the tolerance that belongs to the **governing length** of the feature. A perimeter lip on a 200 mm part varies with the 200 mm outline, not with the 2 mm thickness of the lip.
4. Compute worst case. Compute RSS only if its assumptions hold (below).
5. Compare with the requirement. If worst case fails, the design is at risk unless a statistical argument is justified and accepted.

**Worst case**: gap_min = nominal − Σ|t_i| ; gap_max = nominal + Σ|t_i| (symmetric tolerances). It assumes every contributor at its limit simultaneously (S07).

**RSS**: t_total = √(Σ t_i²). Assumes contributors are statistically independent, centered at the nominal, roughly normal, with a consistent capability level (S07). It does **not** hold for:
- correlated contributors (two parts printed on the same machine share the scale error; treat them as one contributor or add linearly),
- few contributors (RSS gains little and the distribution assumption is weak),
- one-off or few-off parts where there is no process distribution.

**Measurement uncertainty**: dimensions taken from a measurement carry the instrument's uncertainty; add it as a contributor. Decide conformity with a decision rule (ISO 14253-1 defines rules for proving conformity or non-conformity given uncertainty; guard bands reduce false acceptance; S08).

**General tolerance classes** (ISO 2768-1, linear, for reference only when the supplier has adopted them): secondary sources agree on f ±0.2 and m ±0.5 for the 120–400 mm range, and c ±1.2 is given by calculators (S10). These classes were written for machining; an additive supplier must state which class, if any, it guarantees for a given material and orientation.

Script: `scripts/stack_up.py` (worst case, RSS, correlation groups, margin).

---

## 2. Additive process accuracy inputs

- Ask the supplier for the declared tolerance per material/process/orientation (ISO/ASTM 52901 deals with requirements for purchased AM parts; ISO/ASTM 52910 gives general design guidance and explicitly no process- or material-specific data, S02).
- Hole undersizing and scale error must come from a coupon of the same supplier/material. Practitioner data (S11) show undersizing in the 0.1–0.5 mm range on common printers; use only to decide that a coupon is needed.
- Long-span scale error (shrinkage) matters for fits that span the whole part. A small coupon does not reveal it; include a long feature in the coupon or measure the first part.

---

## 3. Cantilever snap-fit strain (screening)

For a straight cantilever of constant rectangular section, thickness h, length l, tip deflection y, the maximum outer-fiber strain is approximately

  ε ≈ 1.5 · h · y / l²

(form given in the Bayer/Covestro snap-fit guide and repeated by BASF-derived calculators; S03). Tapered beams and other sections have different coefficients in the guide.

- Compare ε with the **permissible strain** for the actual material, from the material maker or a coupon. Guide examples (e.g. a value for a polycarbonate blend) are examples, not general limits; for repeated assembly the guide reduces the permissible value (S03).
- For additive parts, the permissible strain depends on orientation; for FDM, bending across layers can be several times weaker than in-plane. AM-specific guidelines (S04) and later studies (S05) show that injection-molding rules do not transfer directly.
- If the permissible strain for the real material and orientation is unknown, the result is a screening value only and the finding stays PENDING until a coupon is tested.

---

## 4. Thermal expansion mismatch

  ΔL = (α₁ − α₂) · L · ΔT

Use α of the actual materials from datasheets. Check clearances that span long distances between a printed part and a PCB or metal part at the temperature extremes of storage and operation.

---

## 5. Heat and airflow sanity checks

- List dissipation per source (W) and the limit temperature of each sensitive component. Without these numbers, thermal adequacy is UNKNOWN, not "probably fine".
- Check the flow path: inlet → heat sources → outlet, no short circuit between inlet and outlet, outlets near the hottest parts, warm air rising to the outlet where possible (S16, trade sources).
- Air temperature rise through a forced-air path (energy balance): ΔT_air ≈ P / (ρ · c_p · Q), with P the heat carried by the air (W), Q the actual volumetric flow (m³/s), air ρ ≈ 1.2 kg/m³ and c_p ≈ 1005 J/(kg·K) near room conditions. The fan's catalogue flow is free-air; the real flow is lower once the enclosure's pressure drop is added (fan curve × system curve), so this gives an optimistic lower bound on ΔT. It estimates bulk air temperature only, not hot spots on components.
- Trade rule of thumb: total vent area around 1.5 × the fan's opening area to avoid choking the fan (S16, non-authoritative). Use only to flag gross under-sizing.
- Compare the expected internal temperature with the enclosure material's heat deflection temperature **at the load level of the feature** (datasheets give HDT at 0.45 and 1.8 MPa; e.g. one PETG datasheet lists 68 °C, S13).
- Thermal adequacy requires a test (soak with thermocouples at worst ambient, worst load, fan off case if the fan can fail). The test must happen **before** decisions that depend on it (material, fan necessity).

---

## 6. Risk ranking (when many findings compete)

Use the report severities. When ordering within a severity, rank by: consequence (safety > function > cost > appearance), likelihood given the evidence, and detectability before release (a risk only detectable after the final print ranks higher). This mirrors the severity/occurrence/detection logic of DFMEA (S18) without pretending to a numerical RPN the evidence cannot support.

---

## 7. When a physical test is required

Require a test (and say which) whenever the conclusion depends on: interlayer strength, insert pull-out/torque, snap-fit strain limits, creep/preload over time, actual hole and scale accuracy, warping on the actual printer, thermal behavior, vibration/noise, or real plug fit. Typical tests: 1:1 paper template for layout, supplier coupon in final material/orientation with the critical features, first-article inspection of a few control dimensions, dry fit without forcing, thermal soak, run-in under vibration.
