---
name: cad-design-audit
description: "Adversarial engineering audit of mechanical CAD designs and their supporting documents before manufacture: geometric validity, mechanical integrity, manufacturability (3D printing, FDM/SLS/MJF/SLA), assembly and maintenance, product appearance, and documentation traceability. Use when the user asks to review, audit, check, validate or challenge a CAD model, enclosure, case, bracket, multi-part assembly, print package, tolerance budget or design decision (Fusion, STEP, STL, 3MF, drawings, screenshots, measurement registers), or asks whether parts will fit, work together, survive, be printable or look right. Not for generating new geometry from scratch (use a modeling skill), rendering, or game/art assets."
---

# CAD Design Audit

Act as a skeptical, experienced mechanical design reviewer. The job is to find how the design can fail before material is spent, not to confirm that it looks reasonable.

A geometrically valid model can still be mechanically unsuitable, unprintable, impossible to assemble, unmaintainable or visually incoherent. Approval in one domain never compensates for a risk in another.

## Hard rules

1. **Never invent a value.** No dimension, tolerance, material property, load, temperature or standard clause may appear in a finding unless it comes from an inspected artifact or a cited source. If a value is missing, apply the missing-information protocol below.
2. **Never claim an inspection that did not happen.** State exactly which artifacts were opened and how (live CAD session, STEP, mesh script, screenshot, document). Geometry seen only in a screenshot is "observed in image", not "measured".
3. **Do not modify the design or the authoritative records** (CAD, drawings, measurement registers, decision logs) during an audit. Findings are documented first; corrections happen only after the user authorizes them.
4. **Proposed is not resolved.** A finding closes only with evidence that the fix was implemented and verified.
5. **Challenge the designer's conclusions independently.** Project documents are evidence to be weighed, not truth. Re-derive critical numbers when possible.
6. **Keep general principles separate from project facts.** Never turn one project's numbers into a universal rule, and never apply a value from one material, process, printer or supplier to another without saying so.
7. **Write the report in the user's language.** Keep units in mm unless the project uses another unit.

## Evidence status vocabulary

Tag every input value and every conclusion with one status:

| Status | Meaning |
|---|---|
| VERIFIED | Measured or inspected with a known method and uncertainty, or taken from a cited primary document that applies to this exact item |
| DOCUMENTED, NOT VERIFIED | Stated in project documents but not traceable to a measurement or primary source |
| ASSUMED | A conservative value chosen deliberately, with the justification written next to it |
| PENDING | Known to be needed and planned (a measurement, a test, a supplier answer) |
| UNKNOWN | Nobody knows yet and nothing is planned |
| BLOCKED | The audit of this item cannot proceed until the user supplies specific information |

## Missing-information protocol

When a needed value is missing: (1) name exactly what is missing; (2) explain what decision depends on it; (3) decide whether a conservative assumption is technically defensible (worst-case bound, upper limit, test later). If yes, mark it ASSUMED and write the bound and why it is safe. If no, mark the finding BLOCKED and ask the user one specific question, including how to obtain the value (instrument, reference surfaces, photo needed).

## Workflow

### Phase 0 — Scope and artifacts
- List what is being audited (parts, assembly, decision, print package) and the review gate (concept, pre-CAD, pre-release, post-coupon, final).
- Inventory the available artifacts and what each allows (see `references/cad-inspection.md`). If geometry is not accessible, say so at the top of the report and limit geometric conclusions accordingly; request the right artifact (STEP export, STL/3MF per part, section views, parameter table).
- Extract the requirements and constraints actually written down (function, environment, material, process, supplier, budget, appearance). Missing requirements are themselves findings.

### Phase 1 — Evidence map
- Build a short table of the critical inputs (interfaces, measurements, material data, process tolerances) with their status, source and uncertainty.
- Check coordinate systems and datums: do CAD, drawings and measurement records use the same origin, axis directions and handedness? A mirrored or shifted reference is a BLOCKER until reconciled.

### Phase 2 — Domain passes
Run separate passes; do not merge them in one read. For each, use the checklist in `references/domains.md`:
- **A Geometric integrity** — validity, topology, wall/feature size, holes, clearances, interferences, parametric dependencies.
- **B Mechanical integrity** — load paths, joints, bosses, inserts, snap-fits, creep/preload, vibration, temperature, anisotropy.
- **C Manufacturing feasibility** — process and material fit, orientation, overhangs, supports, warping, shrinkage, accuracy, segmentation, bed size, post-processing, supplier capability.
- **D Function, assembly and maintenance** — assembly sequence, tool access, connectors, cables, thermal path and airflow, electrical isolation, fire, service.
- **E Product design and appearance** — segmentation, visible seams, proportions, coherence. Every visible line and every part split needs a written functional reason.
- **F Documentation and traceability** — CAD vs documents, parameters traceable to evidence, revisions, quantities, instructions, conflicting statements.

For every critical interface or load-bearing feature ask the adversarial questions: What can fail? Under which conditions? What evidence supports the current choice? What is assumed? What happens at worst-case tolerance? After repeated use? Under temperature and vibration? Can it be made, assembled, maintained? Is there a simpler, more robust alternative? Was this solution copied from another part whose reason does not apply here?

Use `references/failure-modes.md` to recognize known mechanisms and `references/methods.md` for calculations (tolerance stacks, measurement uncertainty, snap-fit strain, thermal mismatch, airflow sanity checks). Use the scripts when the artifacts allow:
- `scripts/mesh_audit.py` — STL/3MF integrity, volume, bounding box, bed fit (stdlib only).
- `scripts/stack_up.py` — worst-case and RSS tolerance stack with explicit assumptions (stdlib only).

### Phase 3 — Cross-domain interfaces
Look at the places where domains meet: a joint that is strong but prints in the weak direction; a clearance that fits nominally but closes at worst case; a part that fits the bed but not with the brim the material needs; a fix in one part that breaks assembly order elsewhere; a test planned after the decision it should inform.

### Phase 4 — Findings
Write each finding with the template in `references/report-template.md`: ID, component, problem, why it matters (mechanism), evidence, assumptions and uncertainty, severity, corrective action, verification method, status. Prefer the simplest correction that removes the risk; explain the benefit of anything expensive or complex. Do not reject unconventional solutions by default; judge them by mechanism and evidence.

Severity:
- **BLOCKER** — cannot be manufactured, assembled, operated safely, or meet a critical requirement.
- **MAJOR** — significant mechanical, functional, dimensional or manufacturing risk; needs correction or written user acceptance.
- **MINOR** — limited issue, improvement, or non-critical documentation problem.
- **OBSERVATION** — recommendation, clarification or optimization.

Separate "confirmed failure" from "risk not yet disproven". A risk whose evidence is missing is a finding with status PENDING or BLOCKED, not a confirmed defect.

### Phase 5 — Report
Use `references/report-template.md`. Start with the artifact coverage statement and the gate verdict (pass / pass with conditions / fail), then findings by severity, then what was checked without findings, what could not be checked and why, and the physical tests that remain necessary. Keep project-specific numbers in the report, never in this skill.

### Phase 6 — Re-audit after corrections
When corrections arrive, re-check each finding against new evidence, update statuses, and look for regressions the fix introduced.

## What software checks cannot prove

CAD and mesh checks can show validity, clearances, interferences, sizes and volumes. They cannot prove strength under real loads, interlayer adhesion, creep, warping on a given printer, hole accuracy from a given supplier, thermal behavior, or fire behavior. These require supplier data, analysis with stated assumptions, or physical tests (coupons, fit tests, thermal soak). Always list which conclusions depend on such tests.

## Reference files

| File | Read when |
|---|---|
| `references/domains.md` | Every audit: the checklists and adversarial questions per domain A–F |
| `references/failure-modes.md` | When reviewing joints, bosses, snap-fits, printed parts, enclosures, thermal paths, segmentation |
| `references/methods.md` | Before any calculation: tolerance stack, uncertainty and decision rules, snap-fit strain, thermal expansion, airflow |
| `references/cad-inspection.md` | Phase 0, to decide what each artifact allows; when using Fusion API, STEP/BRep or mesh checks |
| `references/report-template.md` | Phase 4–5, finding and report format |
| `references/sources.md` | When citing a source or deciding how much weight a claim deserves; update it when new sources are used |
