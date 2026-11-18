# Report and finding templates

Write the report in the user's language. Keep it as long as the evidence requires and no longer.

## Report structure

```markdown
# Design audit — <object> — <gate> — <date>

## 1. Coverage
- Artifacts inspected: <file / revision / how it was inspected>
- Artifacts not available: <what, and which conclusions this limits>
- Tools run: <script/command + exit status>

## 2. Verdict
<PASS | PASS WITH CONDITIONS | FAIL> for <gate>. Open BLOCKERs: n. Open MAJORs: n.
One paragraph: the few things that decide the verdict.

## 3. Findings (by severity, then by risk ranking)
<finding blocks>

## 4. Checked without findings
<short list, with the evidence used — so the reader knows what was covered>

## 5. Not checked, and why
<item — missing artifact / requires test / out of scope>

## 6. Required physical tests before release
<test — what it proves — which findings it closes — when it must happen>

## 7. Open questions for the user (BLOCKED items)
<one specific question each, with how to obtain the answer>
```

## Finding block

```markdown
### <ID> · <SEVERITY> · <short title>
- **Component / feature:** <part, feature, interface>
- **Problem:** <what is wrong or unproven>
- **Why it matters:** <mechanism: how it fails, under which condition>
- **Evidence:** <file + section/line, measurement, calculation, source ID>
- **Assumptions and uncertainty:** <status of each input; what would change the conclusion>
- **Severity rationale:** <why this severity and not the next one>
- **Recommended correction:** <simplest robust fix; alternatives if relevant>
- **Verification method:** <how to prove the fix works: check, calculation, coupon, test>
- **Status:** OPEN | PENDING (evidence awaited) | BLOCKED (question to user) | ACCEPTED (user, date) | RESOLVED (evidence: …)
```

ID convention: `<DOMAIN LETTER>-<number>`, e.g. `C-03` for the third manufacturing finding; keep IDs stable across re-audits.

## Rules for statuses
- RESOLVED needs evidence of implementation **and** verification. A proposed change is still OPEN.
- ACCEPTED means the user knowingly accepts the risk; record who and when.
- A finding that depends on a missing value is PENDING or BLOCKED, never silently closed.
