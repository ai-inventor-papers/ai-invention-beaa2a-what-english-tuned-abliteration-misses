#!/usr/bin/env python3
"""F8: re-parse logged raw judge outputs with the (fixed) parser - never re-call. For each row with judge_fail, the FIRST
attempt whose raw text parses is used (that is the response the protocol would have used had the parser been right).
  python reparse.py <jsonl> [<jsonl> ...]   (rewrites in place, adds reparsed=true; keeps a .bak copy)"""
import json
import shutil
import sys
from pathlib import Path

from judge import parse_judge

for f in sys.argv[1:]:
    p = Path(f)
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    n_fix = 0
    for r in rows:
        if not r.get("judge_fail"):
            continue
        for raw in r.get("raw") or []:
            parsed = parse_judge(raw or "")
            if parsed:
                r.update(parsed)
                r["judge_fail"] = False
                r["reparsed"] = True
                n_fix += 1
                break
    shutil.copy(p, p.with_suffix(p.suffix + ".bak"))
    p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    print(f"{p}: {n_fix} re-parsed; remaining fails {sum(bool(r.get('judge_fail')) for r in rows)} / {len(rows)}")
