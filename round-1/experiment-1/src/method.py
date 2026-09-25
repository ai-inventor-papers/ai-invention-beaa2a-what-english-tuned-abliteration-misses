#!/usr/bin/env python3
"""Matched Heretic runs on two sibling 12B models (cjvt/GaMS3-12B-Instruct vs google/gemma-3-12b-it).

Top-level, resumable orchestrator. Every stage is idempotent: it skips work whose output already
exists, so the pipeline can be re-entered after an interruption or a time-budget stop.

  uv run method.py --stages all
  uv run method.py --stages phaseA_gams,phaseA_gemma,a3,select,eval,analyze,figures
  uv run method.py --stages phaseB_gams            # resume a journal to its stored n_trials

Stages
  phaseA_<tag>  drive_heretic.py <tag> A      60 TPE startup trials (identical draws in both models)
  phaseB_<tag>  drive_heretic.py <tag> B      +140 trials, then frozen selection + Heretic adapter export
  select_<tag>  drive_heretic.py <tag> RESUME selection+export on an unfinished (PROVISIONAL) journal
  a3            a3_screen.py                 sibling agreement over the shared startup edits
  eval_<tag>    swap_eval.py <tag>            orig / own / swap + retest conditions, EN+SL+FLORES
  analyze       analyze.py                    paired tests, sanity flags -> method_out.json
  figures       figures.py                    Pareto fronts, A3 scatter, swap bars (PNG + PDF)

The BASELINE in every comparison is the unedited original model scored in the same pipeline, same
quantization, same batch size, same chat template, same greedy decoding; the swap condition is the
second baseline for "is the selected edit specific to the model it was optimized on?".
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from loguru import logger

WS = Path(__file__).resolve().parent
PY = str(WS / ".venv" / "bin" / "python")
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add(WS / "logs" / "method.log", rotation="30 MB", level="DEBUG")

TAGS = ["gams", "gemma"]
JOURNAL = {"gams": WS / "checkpoints" / "gams" / "cjvt--GaMS3-12B-Instruct.jsonl",
           "gemma": WS / "checkpoints" / "gemma" / "google--gemma-3-12b-it.jsonl"}
BATCH_SIZE = 128  # explicit and identical for both models (documented deviation)


def run(cmd: list[str], log: Path, deadline: float | None = None) -> int:
    logger.info(f"$ {' '.join(cmd)}  -> {log.name}")
    with log.open("a") as f:
        p = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, cwd=str(WS))
        while True:
            rc = p.poll()
            if rc is not None:
                logger.info(f"exit {rc} ({log.name})")
                return rc
            if deadline is not None and time.time() > deadline:
                logger.warning(f"deadline reached, terminating pid {p.pid}")
                p.terminate()
                try:
                    p.wait(timeout=300)
                except subprocess.TimeoutExpired:
                    p.kill()
                return -1
            time.sleep(10)


def n_trials(tag: str) -> int:
    p = WS / "logs" / f"trials_{tag}.jsonl"
    if not p.exists():
        return 0
    return sum(1 for _ in p.open())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stages", default="all")
    ap.add_argument("--budget-min", type=float, default=1e9, help="wall-clock budget for GPU stages")
    args = ap.parse_args()
    deadline = time.time() + args.budget_min * 60
    stages = ([f"phaseA_{t}" for t in TAGS] + ["a3"] + [f"phaseB_{t}" for t in TAGS]
              + [f"eval_{t}" for t in TAGS] + ["analyze", "figures"]) if args.stages == "all" \
        else args.stages.split(",")
    logger.info(f"stages: {stages}")

    for s in stages:
        if s.startswith("phaseA_"):
            tag = s.split("_", 1)[1]
            if JOURNAL[tag].exists() and JOURNAL[tag].stat().st_size > 0:
                logger.info(f"{s}: journal exists ({n_trials(tag)} trials logged) -> skip")
                continue
            run([PY, "drive_heretic.py", tag, "A", "--batch-size", str(BATCH_SIZE),
                 "--deadline-epoch", str(deadline)], WS / "logs" / f"{tag}_A.log", deadline)
        elif s.startswith("phaseB_"):
            tag = s.split("_", 1)[1]
            run([PY, "drive_heretic.py", tag, "B", "--batch-size", str(BATCH_SIZE),
                 "--deadline-epoch", str(deadline)], WS / "logs" / f"{tag}_B.log", deadline)
        elif s.startswith("select_"):
            tag = s.split("_", 1)[1]
            run([PY, "drive_heretic.py", tag, "RESUME", "--batch-size", str(BATCH_SIZE),
                 "--deadline-epoch", str(deadline)], WS / "logs" / f"{tag}_SEL.log", deadline)
        elif s == "a3":
            run([PY, "a3_screen.py"], WS / "logs" / "a3_run.log")
        elif s.startswith("eval_"):
            tag = s.split("_", 1)[1]
            run([PY, "swap_eval.py", tag], WS / "logs" / f"eval_{tag}.log", deadline)
        elif s == "analyze":
            run([PY, "analyze.py"], WS / "logs" / "analyze_run.log")
        elif s == "figures":
            run([PY, "figures.py"], WS / "logs" / "figures.log")
        else:
            raise SystemExit(f"unknown stage {s}")

    status = {}
    for t in TAGS:
        n = n_trials(t)
        status[t] = {"trials_logged": n, "status": "COMPLETE_200" if n >= 200 else f"RESUMABLE_AT_{n}",
                     "journal": str(JOURNAL[t]),
                     "resume_cmd": f"uv run method.py --stages phaseB_{t}"}
    (WS / "results").mkdir(exist_ok=True)
    (WS / "results" / "status.json").write_text(json.dumps(status, indent=1))
    logger.info(json.dumps(status, indent=1))


if __name__ == "__main__":
    main()
