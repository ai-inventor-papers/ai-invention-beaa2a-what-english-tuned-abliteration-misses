#!/usr/bin/env python3
"""T5 (judge side): 10 real items through the primary judge into results/judge_t5/ (not the FINAL label files);
checks that every label parses and that costs accumulate. -> results/judge_t5_mini.json"""
import json
from pathlib import Path

from common import WS, read_jsonl

rows = [r for p in sorted((WS / "results/judge_t5").glob("*.jsonl")) for r in read_jsonl(p)]
costs = [r for r in read_jsonl(WS / "results/cost_log.jsonl")] if (WS / "results/cost_log.jsonl").exists() else []
out = {"n_rows": len(rows), "n_parsed": sum(not r.get("judge_fail") for r in rows),
       "classes": [r.get("cls") for r in rows], "raw_examples": [r["raw"][-1] if r["raw"] else None for r in rows[:5]],
       "cost_log_rows": len(costs), "cumulative_usd": sum(float(c.get("cost") or 0) for c in costs),
       "pass": len(rows) >= 10 and all(not r.get("judge_fail") for r in rows)}
(WS / "results/judge_t5_mini.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps(out, ensure_ascii=False)[:800])
raise SystemExit(0 if out["pass"] else 1)
