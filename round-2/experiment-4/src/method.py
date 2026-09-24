#!/usr/bin/env python3
"""C1 BEHAVIOUR - entry point for the whole FINAL bilingual behavioural evaluation.

METHOD vs BASELINE (side by side, same pipeline, same prompts, same greedy decoding, same batch schedule, same judge):
  method   = the Heretic-abliterated checkpoints (gams_edit = trial 88 LoRA, gemma_edit = trial 96 LoRA; read-only from
             iteration 1) and, as an external anchor, the community edit p-e-w/gemma-3-12b-it-heretic (SANITY REFERENCE).
  baseline = the ORIGINAL model of each pair (the same NF4 base with the LoRA adapter disabled: one base load serves both).
  Secondary baseline for the MEASUREMENT: Heretic's keyword refusal proxy and RefusEU's official guard pipeline
  (Llama-Guard-3-8B + PolyGuard-Qwen + gpt-4o-mini adjudicator) against the frozen gpt-4.1 extended-rubric judge.

Each stage is its own resumable script (item_key based); this driver runs them in the executed order:
  uv run method.py --stages all          # everything
  uv run method.py --stages judge,analyze
Stages: pins freeze tests smoke generate autoscore guard_gpu calib judge local_judge judge2 adjudicate agreement
        analyze audit rseq figures packet metadata schema

The executor audit (30 blind EN items) is a two-step human-in-the-loop stage and is NOT in --stages all:
  uv run executor_audit.py sample   # then fill results/executor_audit_labels.json by hand
  uv run executor_audit.py score"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

from loguru import logger

from common import WS, setup_logging

PY = str(WS / ".venv/bin/python") if (WS / ".venv/bin/python").exists() else sys.executable

STAGES: dict[str, list[list[str]]] = {
    "pins": [["verify_pins.py"]],
    "freeze": [["freeze.py"]],
    "tests": [["tests/test_stats.py"]],
    "smoke": [["smoke.py", "gams"], ["smoke.py", "gemma", "--quick"]],
    # generation: orig+edit of one model share one base load; the frozen bucket schedule is identical for all 5 ckpts
    "generate": [["generate.py", "--model", "gams", "--ckpts", "gams_orig,gams_edit"],
                 ["generate.py", "--model", "gemma", "--ckpts", "gemma_orig,gemma_edit"],
                 ["generate.py", "--model", "community", "--ckpts", "community_ref"],
                 ["smoke.py", "community", "--quick", "--b12-only"]],
    "autoscore": [["autoscore.py"]],
    "guard_gpu": [["guard_pipeline.py", "polyguard"], ["guard_pipeline.py", "llamaguard"]],
    "calib": [["judge2.py", "calibrate"]],
    "judge": [["judge.py"]],
    # F1 substitute judge (third family, local): the run-level API budget blocked gpt-4.1 at 716/3,840 core items
    "local_judge": [["local_judge.py", "all"], ["local_judge.py", "retry"], ["agreement_local.py"]],
    "judge2": [["judge2.py", "sample"]],
    "adjudicate": [["guard_pipeline.py", "adjudicate"], ["guard_pipeline.py", "combine"], ["guard_pipeline.py", "summary"]],
    "agreement": [["agreement.py"]],
    # PRIMARY analysis: substitute-judge CLASS labels, ASR from the official guard pipeline, GlotLID language consistency
    "analyze": [["analyze.py", "--judge-dir", "results/judge_local", "--label-name", "judge_local_qwen3_14b",
                 "--no-fallback", "--asr-from-judge", "no", "--lang-source", "glotlid"],
                ["analyze.py", "--judge-dir", "results/judge", "--label-name", "judge_gpt41", "--no-fallback",
                 "--lang-source", "glotlid", "--out", "results/analysis_gpt41_subset.json"],
                ["headline_table.py"]],
    "audit": [["audit.py", "--judge-dir", "results/judge_local", "--asr-from-guard", "--lang-from-glotlid"],
              ["verify_headlines.py"]],
    "rseq": [["rseq.py", "refs", "--labels-dir", "results/judge_local"],
             ["rseq.py", "score", "--model", "gams", "--labels-dir", "results/judge_local"],
             ["rseq.py", "score", "--model", "gemma", "--labels-dir", "results/judge_local"],
             ["rseq.py", "score", "--model", "community", "--labels-dir", "results/judge_local"],
             ["rseq.py", "report", "--labels-dir", "results/judge_local"]],
    "figures": [["figures.py"]],
    "packet": [["human_packet.py"]],
    "metadata": [["build_metadata.py"]],
    "schema": [["to_schema.py"]],
}


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stages", default="all")
    args = ap.parse_args()
    setup_logging("method")
    order = list(STAGES) if args.stages == "all" else args.stages.split(",")
    for st in order:
        if st not in STAGES:
            raise SystemExit(f"unknown stage {st}; choose from {list(STAGES)}")
        for cmd in STAGES[st]:
            logger.info(f"[{st}] {' '.join(cmd)}")
            rc = subprocess.run([PY, *cmd], cwd=WS, env=os.environ.copy()).returncode
            if rc != 0:
                raise SystemExit(f"stage {st} failed: {' '.join(cmd)} rc={rc}")
    logger.info("done")


if __name__ == "__main__":
    main()
