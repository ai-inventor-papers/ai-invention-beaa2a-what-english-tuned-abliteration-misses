#!/usr/bin/env python3
"""STAGE S8 (audit half) - code-freeze honesty and final artifact checks.

  * every analysis source file hashed at the freeze (configs/code_hashes_at_freeze.json) is compared with its current
    content; analysis_py_unchanged / method_py_unchanged are set true/false honestly and a FULL unified diff against
    the snapshot in configs/code_at_freeze/ is written to results/code_changes_since_freeze.diff when anything changed.
  * the freeze file still verifies against configs/FREEZE.sha256.
  * no table/caption/summary string presents a reselected configuration as a better edit (T11 last bullet): every
    row of results/reselection_table.csv carries the P7 verdict.
  -> results/checks.json
"""
from __future__ import annotations

import csv
import difflib
import hashlib
import json
from pathlib import Path

WS = Path(__file__).resolve().parent


def main() -> None:
    frozen = json.loads((WS / "configs/code_hashes_at_freeze.json").read_text())
    changed, diffs = {}, []
    for f, h in frozen["files"].items():
        cur = hashlib.sha256((WS / f).read_bytes()).hexdigest()
        if cur != h:
            old = (WS / "configs/code_at_freeze" / f).read_text().splitlines(keepends=True)
            new = (WS / f).read_text().splitlines(keepends=True)
            d = list(difflib.unified_diff(old, new, fromfile=f"frozen/{f}", tofile=f"current/{f}"))
            changed[f] = {"frozen_sha": h, "current_sha": cur, "diff_lines": len(d)}
            diffs += d
    if diffs:
        (WS / "results/code_changes_since_freeze.diff").write_text("".join(diffs))
    fz_ok = hashlib.sha256((WS / "configs/frozen_predictions.json").read_bytes()).hexdigest() == \
        (WS / "configs/FREEZE.sha256").read_text().split()[0]
    rs = list(csv.DictReader(open(WS / "results/reselection_table.csv"))) if (WS / "results/reselection_table.csv").exists() else []
    p7 = all(r.get("not_a_better_edit", "").startswith("NOT A BETTER EDIT") for r in rs) and bool(rs)
    out = {"files_changed_since_freeze": changed,
           "analysis_py_unchanged": "analysis.py" not in changed, "method_py_unchanged": "method.py" not in changed,
           "files_created_after_freeze": frozen.get("missing_at_freeze", []),
           "diff_file": "results/code_changes_since_freeze.diff" if diffs else None,
           "freeze_file_verifies": fz_ok, "reselection_rows_all_carry_P7_verdict": p7, "n_reselection_rows": len(rs)}
    (WS / "results/checks.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
