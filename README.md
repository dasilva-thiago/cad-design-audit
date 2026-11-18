# cad-design-audit — Claude Skill

An adversarial engineering review skill for mechanical CAD designs and their documentation, before money is spent on manufacturing. It audits geometry, mechanics, manufacturability (with emphasis on 3D printing), assembly and maintenance, product appearance, and documentation traceability, and writes evidence-based findings with severity, correction and verification method.

It does not generate geometry. Pair it with a modeling workflow (Autodesk Fusion, CadQuery, etc.) and use it at review gates: concept, before CAD, before release, after the supplier coupon, and before paying for the final print.

## Architecture

```
cad-design-audit/
├── SKILL.md                     # rules, evidence statuses, missing-info protocol, 6-phase workflow
├── references/
│   ├── domains.md               # checklists + adversarial questions for domains A–F
│   ├── failure-modes.md         # FM-01..FM-16: mechanisms, what to look for, evidence, fixes
│   ├── methods.md               # tolerance stacks, uncertainty/decision rules, snap-fit strain,
│   │                            #   thermal expansion, airflow sanity, risk ranking, when to test
│   ├── cad-inspection.md        # what each artifact allows; Fusion API, STEP/OCC, mesh checks
│   ├── report-template.md       # report and finding format, status rules
│   └── sources.md               # research source register (S01–S21) with limits
├── scripts/
│   ├── mesh_audit.py            # STL/3MF integrity, volume, bbox, wall-thickness scan, bed fit
│   └── stack_up.py              # worst-case + RSS stack with correlation groups
├── tests/test_tools.py          # 18 tests on synthetic meshes and chains (stdlib only)
└── validation/
    ├── VALIDATION_REPORT.md     # script tests, 8 synthetic scenarios, weaknesses fixed
    ├── eduserver_box_integration_audit.md   # first real-project audit (project-specific)
    └── eduserver_chains/        # stack-up inputs/outputs used in that audit
```

Design choices:
- **Principles in the skill, numbers in the project.** The skill holds mechanisms, methods and questions; project values live only in the project's audit reports.
- **Evidence status on every input** (VERIFIED, DOCUMENTED NOT VERIFIED, ASSUMED, PENDING, UNKNOWN, BLOCKED) and a missing-information protocol: no invented values.
- **Separate domain passes**, then a cross-domain pass, because the costly errors live at interfaces (a strong joint printed in its weak direction; a test scheduled after the decision it should inform).
- **Honest coverage.** The report states what was opened and how; software checks are separated from conclusions that need tests.
- **Stdlib-only scripts**, so they run anywhere without installing CAD kernels. STEP/BRep checks are described for environments that have OCP/CadQuery.

## Installation

Personal scope (all projects):
```
cp -r cad-design-audit ~/.claude/skills/
```
Project scope (one project): copy to `<project>/.claude/skills/cad-design-audit/`.

Requirements: Python 3.8+ for the scripts (standard library only). Optional: Autodesk Fusion with API/MCP access, or an OCP/CadQuery environment for STEP checks.

Check the scripts:
```
cd ~/.claude/skills/cad-design-audit
python -m unittest discover -s tests -v
```

## Usage

Ask in natural language, for example:
- "Audit this enclosure before I send it to print" (attach STEP/STL per part, or open the Fusion design).
- "Review our tolerance budget for the lid lip."
- "Is this snap-fit OK in PETG printed upright?"
- "Run a full design review of the project documents."

Direct script use:
```
python scripts/mesh_audit.py part.stl --bed 256x256x256 --margin 8 --thickness --min-wall 1.2
python scripts/stack_up.py chain.json
```
Exit codes: `mesh_audit` 0 ok · 1 integrity/thin wall · 2 does not fit the bed · 3 unreadable; `stack_up` 0 worst case meets the requirement · 1 fails · 2 bad input.

## Capabilities and limits

Can do with the bundled tools: mesh integrity, volume, bounding box, approximate wall thickness, bed fit with margin; tolerance stacks with stated assumptions; structured adversarial review of documents, decisions and screenshots; Fusion checks when a live session is available (interference, minimum distance, thickness) — only when actually run.

Needs external tools: interference/clearance between parts (CAD), BRep validity and boolean interference in STEP (OCP/CadQuery), overhang/support analysis (slicer).

Needs physical evidence or supplier data: interlayer strength, snap-fit strain limits, insert pull-out/torque, creep and preload loss, real hole/scale accuracy, warping on a given printer, thermal behavior, vibration, real plug fit, flammability and standards compliance.

Validation status: scripts tested by execution; review behavior tested on 8 simulated scenarios and one real project without enclosure CAD (see `validation/VALIDATION_REPORT.md`). An independent validation by a reviewer without prior context is still recommended.

## Credits

Verification ideas (validity, solid count, volume derived from parameters instead of measured, point classification) were informed by the MIT-licensed 0oKevino0/claude-cad `cadquery-modeling` skill. No code from other projects is included; all scripts were written for this skill.

The `validation/` folder contains a real audit of the author's eduServer Box project as an integration example; its numbers are project-specific and are not rules of the skill.
