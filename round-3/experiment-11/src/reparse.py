#!/usr/bin/env python3
"""Re-parse logged raw judge outputs that failed the strict parser (parser fix only; no model re-call). A superseding
row with parse_mode='class_only' is APPENDED (readers take the last non-failed row per key); the failed row is kept."""
import json
import sys
from pathlib import Path

from judges import parse_judge_classonly

for f in sys.argv[1:]:
    p = Path(f)
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    ok = {r["key"] for r in rows if not r.get("judge_fail")}
    new = []
    for r in rows:
        if r.get("judge_fail") and r["key"] not in ok:
            q = parse_judge_classonly((r.get("raw") or [""])[-1].split("<<RETRY160>>")[-1])
            if q:
                new.append({**r, **q, "judge_fail": False, "reparsed": True})
                ok.add(r["key"])
    with p.open("a") as fh:
        for r in new:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{f}: re-parsed {len(new)} rows; still failing {sum(1 for r in rows if r.get('judge_fail') and r['key'] not in ok)}")
