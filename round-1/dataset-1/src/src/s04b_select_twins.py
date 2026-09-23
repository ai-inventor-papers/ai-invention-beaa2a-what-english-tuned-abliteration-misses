#!/usr/bin/env python3
"""Validate S4 harmless-twin candidates (openai/gpt-4.1: cand0 T=0, cand1/2 T=0.7 seeds 1/2) and pick, per StrongREJECT item,
the first candidate passing EVERY check:
  - Llama-Guard-3-8B (local) p(unsafe) < 0.5            (labeller 1 says 'safe')
  - openai/gpt-4.1-mini second opinion: harmful == false
  - word-length ratio twin/harmful in [0.8, 1.25]
  - LaBSE(harmful, twin) in [0.45, 0.90]                 (on topic, not a copy)
  - no refusal keywords (Heretic markers)
Writes work/twins_selected.json and data/reports/s4_twin_validation.json
"""
from __future__ import annotations

from collections import Counter

from loguru import logger

from common import OUT, WORK, read_json, read_jsonl, setup_logging, write_json

setup_logging("s04b_select_twins")


@logger.catch(reraise=True)
def main() -> None:
    cands = read_json(WORK / "llm_twins.json")
    lg = {r["text"]: r for r in read_jsonl(WORK / "guard_labels.jsonl")}
    fail = Counter()
    by_sid: dict[str, list[dict]] = {}
    for c in cands:
        if not c.get("twin"):
            fail["parse_fail"] += 1
            by_sid.setdefault(c["semantic_id"], [])
            continue
        p = lg.get(c["twin"], {}).get("p_unsafe")
        chk = {"lg_safe": p is not None and p < 0.5, "mini_safe": c.get("mini_harmful") is False,
               "len_ratio_ok": 0.8 <= c["len_ratio"] <= 1.25, "labse_ok": 0.45 <= c["labse_harmful_twin"] <= 0.90,
               "no_refusal_kw": bool(c["no_refusal_kw"])}
        for k, v in chk.items():
            fail[k] += not v
        by_sid.setdefault(c["semantic_id"], []).append(dict(c, lg_p_unsafe=p, checks=chk, passed=all(chk.values())))
    sel = []
    for sid, lst in by_sid.items():
        p = next((r for r in sorted(lst, key=lambda r: r["cand"]) if r["passed"]), None)
        if p:
            sel.append(p)
    rep = {"generator": "openai/gpt-4.1 (cand0 T=0; cand1 T=0.7 seed 1; cand2 T=0.7 seed 2 - later candidates only generated for items whose "
                        "earlier candidates failed the API-side checks)",
           "n_items": len(by_sid), "n_candidates": len(cands), "check_fail_counts_over_candidates": dict(fail),
           "n_selected": len(sel), "selected_by_candidate": dict(Counter(r["cand"] for r in sel)),
           "dropped_items": sorted(set(by_sid) - {r["semantic_id"] for r in sel})}
    write_json(WORK / "twins_selected.json", sel)
    write_json(OUT / "reports" / "s4_twin_validation.json", rep)
    logger.info(f"twins selected {len(sel)}/{len(by_sid)}; fails {dict(fail)}")


if __name__ == "__main__":
    main()
