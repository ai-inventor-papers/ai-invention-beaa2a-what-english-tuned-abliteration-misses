#!/usr/bin/env python3
"""Collect the GaMS3 replay's per-response logs into the deliverable tables.

  logs/inloop_scores/<tag>/rec_*.jsonl  ->  results/replay/gams_inloop.jsonl       (edited trials)
                                         ->  results/replay/gams_inloop_orig.jsonl  (unedited GaMS3 baseline)
Row: {model, run, trial, prompt_id, prompt, response, n_tokens, truncated, keyword_refused_recorder}
n_tokens with the GaMS3 tokenizer at its pinned revision. Also records the freeze-order check (every GaMS3
generation file is newer than configs/FREEZE.sha256).
"""
from __future__ import annotations

import glob
import json
from pathlib import Path

from loguru import logger

from common import CONFIGS, GAMS, LOGS, RESULTS, read_jsonl, setup_logging, write_json, write_jsonl


@logger.catch(reraise=True)
def main() -> None:
    setup_logging("collect")
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(snapshot_download(GAMS[0], revision=GAMS[1], local_files_only=True))
    rows: dict[tuple, dict] = {}
    base: dict[int, dict] = {}
    conflicts, base_mismatch = [], 0
    freeze_t = (CONFIGS / "FREEZE.sha256").stat().st_mtime
    files = sorted(glob.glob(str(LOGS / "inloop_scores/*/rec_*.jsonl")))
    older = [f for f in files if Path(f).stat().st_mtime <= freeze_t]
    for f in files:
        tag = Path(f).parent.name
        for r in read_jsonl(Path(f)):
            t = r.get("trial")
            if t is None or t == -1:
                b = base.setdefault(r["i"], {"model": "gams", "run": tag, "trial": -1, "prompt_id": r["i"],
                                             "prompt": r["prompt"], "response": r["response"],
                                             "keyword_refused_recorder": r["keyword_refused"]})
                if b["response"] != r["response"]:
                    base_mismatch += 1
                continue
            key = (int(t), r["i"])
            if key in rows:
                if rows[key]["response"] != r["response"]:
                    conflicts.append({"trial": t, "i": r["i"], "runs": [rows[key]["run"], tag]})
                continue
            rows[key] = {"model": "gams", "run": tag, "trial": int(t), "prompt_id": r["i"], "prompt": r["prompt"],
                         "response": r["response"], "keyword_refused_recorder": r["keyword_refused"]}
    out = sorted(rows.values(), key=lambda r: (r["trial"], r["prompt_id"]))
    ob = [base[i] for i in sorted(base)]
    for group in (out, ob):
        if not group:
            continue
        lens = tok([r["response"] for r in group], add_special_tokens=False)["input_ids"]
        for r, ids in zip(group, lens):
            r["n_tokens"] = len(ids)
            r["truncated"] = len(ids) >= 100
    write_jsonl(RESULTS / "replay/gams_inloop.jsonl", out)
    write_jsonl(RESULTS / "replay/gams_inloop_orig.jsonl", ob)
    trials = sorted({r["trial"] for r in out})
    incomplete = [t for t in trials if sum(1 for r in out if r["trial"] == t) != 100]
    rep = {"n_rows": len(out), "n_trials": len(trials), "trials": trials, "incomplete_trials": incomplete,
           "n_baseline_rows": len(ob), "baseline_mismatch_across_processes": base_mismatch,
           "conflicting_duplicate_rows": conflicts[:20], "n_conflicts": len(conflicts),
           "freeze_order": {"n_log_files": len(files), "n_older_than_freeze": len(older), "pass": not older}}
    write_json(RESULTS / "collect_report.json", rep)
    logger.info(f"collected {len(out)} rows over {len(trials)} trials, {len(ob)} baseline rows; "
                f"incomplete {incomplete}; conflicts {len(conflicts)}; freeze-order pass {not older}")


if __name__ == "__main__":
    main()
