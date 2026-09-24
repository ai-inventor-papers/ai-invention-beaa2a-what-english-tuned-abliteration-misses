#!/usr/bin/env python3
"""Stage F: second judge (google/gemini-2.5-flash, reasoning disabled, T=0, annotation framing) on the FROZEN
400-item stratified sample (frozen_samples.json:judge2_sample); plus B5 DEV calibration of the primary rubric.

  python judge2.py sample [--n-per-cell 20]     -> results/judge2/<ckpt>.jsonl
  python judge2.py calibrate                    -> results/judge_dev_calibration.json (40 iteration-1 DEV items, gpt-4.1)"""
from __future__ import annotations

import argparse
import asyncio
import json
from collections import Counter

import numpy as np
from loguru import logger

from common import EXP3, WS, read_jsonl, setup_logging
from judge import auto_empty, judge_rows, load_gen_rows, protocol, cumulative_cost

J2_MODEL = "google/gemini-2.5-flash"


def run_sample(n_per_cell: int, model: str, out_sub: str) -> None:
    P = protocol()
    frozen = json.loads((WS / "frozen_samples.json").read_text())
    samp = frozen["judge2_sample"]
    if n_per_cell < 20:  # cut (4): first n of each frozen cell, in frozen order
        cnt, keep = Counter(), []
        for s in samp:
            c = (s["ckpt"], s["lang"], s["set_type"])
            if cnt[c] < n_per_cell:
                keep.append(s)
                cnt[c] += 1
        samp = keep
    want = {(s["ckpt"], s["item_key"]) for s in samp}
    rows = [r for r in load_gen_rows(sorted({s["ckpt"] for s in samp}), frozen) if (r["ckpt"], r["item_key"]) in want]
    out_dir = WS / out_sub
    out_dir.mkdir(parents=True, exist_ok=True)
    done = set()
    for p in out_dir.glob("*.jsonl"):
        done |= {(r["ckpt"], r["item_key"]) for r in read_jsonl(p) if not r.get("judge_fail")}
    todo = [r for r in rows if (r["ckpt"], r["item_key"]) not in done]
    for r in [r for r in todo if not r["response_text"].strip()]:
        from common import append_jsonl
        append_jsonl(out_dir / f"{r['ckpt']}.jsonl", [auto_empty(r, model)])
    todo = [r for r in todo if r["response_text"].strip()]
    np.random.default_rng(7).shuffle(todo)
    logger.info(f"judge2 {model}: sample {len(samp)} / available {len(rows)} / to send {len(todo)}; cumulative ${cumulative_cost():.3f}")
    extra = {"reasoning": {"enabled": False}} if "gemini" in model else None
    st = asyncio.run(judge_rows(todo, model=model, system=P["judge_secondary"]["system"],
                                template=P["judge_primary"]["user_template"], out_path_fn=lambda ck: out_dir / f"{ck}.jsonl",
                                max_tokens=60, extra=extra))
    logger.info(f"judge2 stats {st}; cumulative ${cumulative_cost():.3f}")


def calibrate() -> None:
    P = protocol()
    jp = P["judge_primary"]
    recs = json.loads((EXP3 / "results" / "judged_generations.json").read_text())
    rng = np.random.default_rng(20260923)
    strata = {}
    for i, r in enumerate(recs):
        if r["judge_label"] in ("refused", "complied", "partial", "malformed") and r["response"].strip():
            strata.setdefault((r["judge_label"], r["lang"]), []).append(i)
    quota = {("refused", "en"): 8, ("refused", "sl"): 8, ("complied", "en"): 8, ("complied", "sl"): 8,
             ("partial", "en"): 2, ("partial", "sl"): 2, ("malformed", "en"): 2, ("malformed", "sl"): 2}
    pick = []
    for k, q in quota.items():
        pool = strata.get(k, [])
        pick += [int(x) for x in rng.choice(pool, size=min(q, len(pool)), replace=False)]
    rows = [{"ckpt": "dev_calibration", "item_key": f"iter1:{i}", "prompt": recs[i]["prompt"],
             "response_text": recs[i]["response"], "hit_max": False} for i in pick]
    out = WS / "results" / "judge_dev_calibration.jsonl"
    if out.exists():
        out.unlink()
    st = asyncio.run(judge_rows(rows, model=jp["model"], system=jp["system"], template=jp["user_template"],
                                out_path_fn=lambda ck: out, max_tokens=jp["max_tokens"]))
    summarize_calibration(recs, pick, st)


def summarize_calibration(recs: list, pick: list[int], st: dict) -> None:
    out = WS / "results" / "judge_dev_calibration.jsonl"
    new = {r["item_key"]: r for r in read_jsonl(out)} if out.exists() else {}
    comp = []
    for i in pick:
        n = new.get(f"iter1:{i}")
        if n is None or n.get("judge_fail"):
            continue
        comp.append({"old": recs[i]["judge_label"], "new": n["cls"], "lang": recs[i]["lang"]})
    rc = [c for c in comp if c["old"] in ("refused", "complied")]
    agree = float(np.mean([(c["old"] == "refused") == (c["new"] == "refused") for c in rc])) if rc else None
    res = {"n_sent": len(pick), "n_parsed": len(comp), "stats": st, "agreement_refused_vs_not_on_refused_complied_items": agree,
           "confusion": Counter(f"{c['old']}->{c['new']}" for c in comp), "pass_0.8": agree is not None and agree >= 0.8,
           "note": "iteration-1 labels came from a 4-way gpt-4.1 rubric at 128 tokens; the new rubric is frozen in protocol.yaml"}
    (WS / "results" / "judge_dev_calibration.json").write_text(json.dumps(res, indent=1))
    logger.info(f"B5 calibration: {res}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["sample", "calibrate", "recalibrate"])
    ap.add_argument("--n-per-cell", type=int, default=20)
    ap.add_argument("--model", default=J2_MODEL)
    ap.add_argument("--out-sub", default="results/judge2")
    args = ap.parse_args()
    setup_logging("judge2")
    logger.add(WS / "logs" / "judge_debug.log", level="DEBUG", filter=lambda r: r["message"].startswith("RAW"))
    if args.mode == "calibrate":
        calibrate()
    elif args.mode == "recalibrate":  # F8: recompute from re-parsed raw outputs, no API calls
        recs = json.loads((EXP3 / "results" / "judged_generations.json").read_text())
        rows = read_jsonl(WS / "results" / "judge_dev_calibration.jsonl")
        pick = [int(r["item_key"].split(":")[1]) for r in rows]
        summarize_calibration(recs, pick, {"sent": len(rows), "reparsed": sum(bool(r.get("reparsed")) for r in rows),
                                           "note": "labels re-parsed from logged raw outputs after the F8 parser fix"})
    else:
        run_sample(args.n_per_cell, args.model, args.out_sub)


if __name__ == "__main__":
    main()
