#!/usr/bin/env python3
"""Single entry point for the iteration-4 evaluation. Every phase is resumable and idempotent where it spends money
(purchases skip items already labelled; the freeze refuses to be silently rewritten).

  uv run eval.py --phase all
  uv run eval.py --phase 0      # inventory -> results/pooled_generations.parquet
  uv run eval.py --phase freeze # FREEZE (predictions, estimators, power simulation, calibration sample) - run ONCE
  uv run eval.py --phase 2buy   # buy gpt-4.1 labels for the frozen sample (OpenRouter; hard stop $8)
  uv run eval.py --phase 1      # PARTIAL transition curves (asserts the freeze hash + mtime order)
  uv run eval.py --phase 2      # judge re-certification, Rogan-Gladen, judge-sensitivity table
  uv run eval.py --phase 2b     # declared post-freeze supplement (exp11/exp12 refusal items) + gpt-4.1 re-expression
  uv run eval.py --phase 3guard # GPU: NF4 guard pipeline on the frozen subsample
  uv run eval.py --phase 3      # ASR assembly, validity/GlotLID, flip analysis, pending-review list
  uv run eval.py --phase 4      # GPU: NF4-vs-bf16 weight + activation bound + 40-item behavioural bf16 cell
  uv run eval.py --phase 6      # independent recompute of the iteration-3 draft (stdlib+numpy+pyarrow)
  uv run eval.py --phase 5      # paste-ready report repairs (+ lint)
  uv run eval.py --phase 7      # claims registry + full_eval_out.json
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from loguru import logger

WS = Path(__file__).resolve().parent
S = WS / "scripts"
PY = sys.executable
PHASES = {
    "0": [[PY, "p0_inventory.py"]],
    "freeze": [[PY, "p1_freeze.py"]],
    "2buy": [[PY, "p2_buy.py"]],
    "1": [[PY, "p1_curves.py"]],
    "2": [[PY, "p2_judge.py"]],
    "2b": [[PY, "p2b_supplement.py"]],
    "3guard": [[PY, "p3a_guard.py"]],
    "3": [[PY, "p3_scope.py", "asr", "validity", "flip", "pending"]],
    "4": [[PY, "p4_quant.py", "weights"], [PY, "p4_quant.py", "acts"], [PY, "p4b_behaviour.py"]],
    "6": [[PY, str(WS / "rederive_iter3.py")]],
    "5": [[PY, "p5_repairs.py"]],
    "7": [[PY, "p7_assemble.py"], [PY, "p8_readme.py"]],
}
ORDER = ["0", "freeze", "2buy", "1", "2", "2b", "3guard", "3", "4", "6", "5", "7"]


@logger.catch(reraise=True)
def main() -> None:
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    (WS / "logs").mkdir(exist_ok=True)
    logger.add(WS / "logs" / "eval.log", rotation="30 MB", level="DEBUG")
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="all", help="one of " + ", ".join(ORDER) + " or all")
    a = ap.parse_args()
    phases = ORDER if a.phase == "all" else [a.phase]
    if a.phase == "all" and (WS / "configs" / "FREEZE_iter4_eval.json").exists():
        phases = [p for p in phases if p != "freeze"]  # never re-freeze after results exist
        logger.info("freeze exists - skipping the freeze phase (delete configs/FREEZE* deliberately to re-freeze)")
    for p in phases:
        for cmd in PHASES[p]:
            t = time.time()
            logger.info(f"phase {p}: {' '.join(cmd[1:])}")
            r = subprocess.run(cmd, cwd=S)
            if r.returncode != 0:
                raise SystemExit(f"phase {p} failed ({r.returncode})")
            logger.info(f"phase {p} done in {time.time() - t:.0f}s")


if __name__ == "__main__":
    main()
