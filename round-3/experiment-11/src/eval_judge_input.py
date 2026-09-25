#!/usr/bin/env python3
"""Judge inputs for every eval generation (key = '<arm>|<item_key>'), blind to arm (the judge sees prompt + response
only; judges.py shuffles). '[TRUNCATED AT 256 TOKENS]' is appended when generation hit the token cap (frozen rubric).
-> results/judge_in/eval_all.jsonl (all sets) and results/judge_in/eval_harmful.jsonl (harmful sets, for Llama-Guard)."""
import json
from pathlib import Path

WS = Path(__file__).resolve().parent
rows = []
for p in sorted((WS / "results/eval_gen").glob("*.jsonl")):
    for l in p.read_text().splitlines():
        if l.strip():
            r = json.loads(l)
            rows.append({"key": f"{r['arm']}|{r['item_key']}", "prompt": r["prompt"], "response": r["response_text"],
                         "trunc_marker": "[TRUNCATED AT 256 TOKENS]" if r["hit_max"] else "", "set": r["set"]})
out = WS / "results/judge_in"
out.mkdir(parents=True, exist_ok=True)
(out / "eval_all.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
(out / "eval_harmful.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows if r["set"] != "S6"))
print(len(rows), "eval judge rows")
