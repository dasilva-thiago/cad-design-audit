#!/usr/bin/env python3
"""1-D tolerance stack-up: worst case and RSS, with correlation groups (standard library only).

Usage:
  python stack_up.py chain.json

chain.json:
{
  "name": "lid lip clearance per side",
  "requirement": {"min": 0.0, "max": null},          # limits on the resulting gap (mm)
  "contributors": [
    {"name": "base lip outer half-width", "nominal": 100.0, "tol": 0.25, "sign": -1,
     "source": "supplier class / coupon / measurement", "group": "printer-scale"},
    {"name": "lid groove inner half-width", "nominal": 100.35, "tol": 0.25, "sign": 1,
     "source": "...", "group": "printer-scale"}
  ]
}

- "sign": +1 if the contributor increases the gap, -1 if it decreases it.
- "tol": symmetric tolerance (+/-). Use "tol_plus"/"tol_minus" (both positive numbers) for
  asymmetric tolerances.
- "group": contributors that are correlated (same printer scale error, same measurement) are
  added linearly inside the group; groups are then combined by RSS. Ungrouped contributors are
  independent.

Worst case is always reported. RSS is reported with its assumptions; it is not valid for
correlated contributors left ungrouped, for few contributors, or for one-off parts without a
process distribution. Exit code 0 if worst case meets the requirement, 1 if not, 2 on bad input.
"""

import json
import math
import sys


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def analyse(chain):
    contribs = chain["contributors"]
    req = chain.get("requirement", {})
    nominal = 0.0
    wc_low = 0.0
    wc_high = 0.0
    groups = {}
    rows = []
    for c in contribs:
        s = c.get("sign", 1)
        if s not in (1, -1):
            raise ValueError(f"sign must be +1 or -1 in '{c.get('name')}'")
        tp = float(c.get("tol_plus", c.get("tol", 0.0)))
        tm = float(c.get("tol_minus", c.get("tol", 0.0)))
        if tp < 0 or tm < 0:
            raise ValueError(f"tolerances must be positive in '{c.get('name')}'")
        nominal += s * float(c["nominal"])
        # effect on the gap of the contributor going to its upper / lower limit
        up, down = s * tp, -s * tm
        wc_low += min(up, down)
        wc_high += max(up, down)
        half = (tp + tm) / 2.0
        mid_shift = s * (tp - tm) / 2.0
        g = c.get("group")
        key = g if g else f"__{len(rows)}"
        groups.setdefault(key, [0.0, 0.0])
        groups[key][0] += half  # linear sum inside a correlation group
        groups[key][1] += mid_shift
        rows.append({"name": c.get("name"), "sign": s, "nominal": c["nominal"], "tol_plus": tp,
                     "tol_minus": tm, "group": g, "source": c.get("source", "NOT STATED")})
    rss_half = math.sqrt(sum(v[0] ** 2 for v in groups.values()))
    rss_center = nominal + sum(v[1] for v in groups.values())
    res = {
        "name": chain.get("name"),
        "nominal_gap": round(nominal, 4),
        "worst_case": {"min": round(nominal + wc_low, 4), "max": round(nominal + wc_high, 4)},
        "rss": {"min": round(rss_center - rss_half, 4), "max": round(rss_center + rss_half, 4),
                "independent_groups": len(groups),
                "assumptions": "groups independent, centered, roughly normal, comparable capability; "
                               "not valid for one-off parts or ungrouped correlated contributors"},
        "contributors": rows,
    }
    lo, hi = req.get("min"), req.get("max")
    wc_ok = (lo is None or res["worst_case"]["min"] >= lo) and (hi is None or res["worst_case"]["max"] <= hi)
    rss_ok = (lo is None or res["rss"]["min"] >= lo) and (hi is None or res["rss"]["max"] <= hi)
    res["requirement"] = {"min": lo, "max": hi}
    res["meets_requirement"] = {"worst_case": wc_ok, "rss": rss_ok}
    if lo is not None:
        res["margin_to_min"] = {"worst_case": round(res["worst_case"]["min"] - lo, 4),
                                "rss": round(res["rss"]["min"] - lo, 4)}
    missing = [r["name"] for r in rows if r["source"] == "NOT STATED"]
    if missing:
        res["warnings"] = [f"no source stated for: {', '.join(missing)}"]
    return res, wc_ok


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__)
        return 2
    try:
        res, ok = analyse(load(argv[0]))
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, indent=2))
        return 2
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
