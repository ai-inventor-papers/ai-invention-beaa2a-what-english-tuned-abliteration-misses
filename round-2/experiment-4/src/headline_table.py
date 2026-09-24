#!/usr/bin/env python3
"""results/analysis.json -> results/headline_table.csv (5 ckpts x 2 langs x the reported outcomes, with CIs)."""
import csv
import json

from common import WS

A = json.loads((WS / "results/analysis.json").read_text())
H = A["headline"]
COLS = [("S5_refusal", "refusal (S5)"), ("S5_asr", "ASR official (S5)"), ("S5_partial", "partial (S5)"),
        ("S5_invalid", "invalid (S5)"), ("S6_over_refusal", "over-refusal (S6)"),
        ("S6_over_refusal_or_partial", "over-refusal incl. partial (S6)"),
        ("all_judged_lang_ok", "language consistency (GlotLID)"), ("all_hit_max", "truncated at 256 tokens")]
rows = []
for k, h in H.items():
    ck, lang = k.split("|")
    r = {"checkpoint": ck, "lang": lang}
    for c, name in COLS:
        v = h.get(c, {})
        r[name] = "" if v.get("rate") is None else f"{v['rate']:.3f} [{v['ci'][0]:.3f},{v['ci'][1]:.3f}] (n={v['n']})"
    r["rep4 mean"] = "" if h.get("all_rep4_mean") is None else f"{h['all_rep4_mean']:.4f}"
    rows.append(r)
p = WS / "results/headline_table.csv"
with open(p, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(f"wrote {p} ({len(rows)} rows)")
