#!/usr/bin/env python3
"""Entry point of the Gemma P1 random-edit panel ("what English misses in Slovene").

Runs the whole pipeline in order; every stage is resumable, so re-running skips finished work:
  0. test_T0.py     synthetic panels with known answers (Gap / ceiling / bootstrap / carrier code)
  1. refs_gams.py   compliance references from GaMS3-12B-Instruct + its iteration-1 core edit (trial 88)
  2. panel.py       GPU: setup checks, original caches, local judge, references, DEV geometry, frozen predictions
                    (hashed), Stage-A timing + frozen trim, edit panel E0 / E1 / E_TPE / E_R (+ validity generations)
  3. judge_api.py   frozen gpt-4.1 judge of the validity generations + the original's generations (cost-capped)
  4. analysis.py    gates, Gap / B / SIMEX / stability / margin-matched Gap / mixed model / carrier / forecasts / verdicts
  5. audit.py       independent numpy re-derivation + placebos
  6. figures.py     fig1..fig6
  7. make_output.py method_out.json (exp_gen_sol_out) -> then aii-json mini/preview variants
  8. make_readme.py  README.md results section recomputed from results/analysis.json + results/audit.json

The baseline is built into the design: the same-language prediction EN_A -> EN_B (noise ceiling) is the comparison for
every cross-language prediction EN_A -> SL_B, and the carrier covariate P is compared against the geometry baselines
b1 (direction-cosine transfer), b2 (language-identity entanglement analogue), b3 (layer-band kernel mass), Omega (LSAR
subspace overlap) and D (exposure).

  uv run python method.py [--deadline-min 200] [--skip-gpu] [--skip-api]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from loguru import logger

WS = Path(__file__).resolve().parent
PY = sys.executable
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add(WS / "logs" / "method.log", rotation="30 MB", level="DEBUG")


def run(args: list[str], timeout: float | None = None, check: bool = True) -> int:
    t0 = time.time()
    logger.info("RUN " + " ".join(args))
    r = subprocess.run([PY, *args], cwd=WS, timeout=timeout)
    logger.info(f"-> exit {r.returncode} in {time.time() - t0:.0f}s")
    if check and r.returncode != 0:
        raise RuntimeError(f"{args[0]} failed with exit code {r.returncode}")
    return r.returncode


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deadline-min", type=float, default=200.0, help="edit-scoring window of panel.py (minutes)")
    ap.add_argument("--skip-gpu", action="store_true", help="analysis only (panel results already on disk)")
    ap.add_argument("--skip-api", action="store_true", help="do not call the OpenRouter judge")
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    run(["test_T0.py"], timeout=1800)
    if not a.skip_gpu:
        if not (WS / "references" / "gams_core_generations.json").exists():
            run(["refs_gams.py"], timeout=3600)
        run(["panel.py", "--deadline-min", str(a.deadline_min)], timeout=(a.deadline_min + 90) * 60)
    if not a.skip_api:
        # 403/402 (key limit) is not an error: the local judge stays primary and judge_pending.json records the command
        run(["judge_api.py", "--targets", "orig,validity"], timeout=3600, check=False)
    run(["analysis.py", "--boot", str(a.boot), "--perm", str(a.boot)], timeout=4 * 3600)
    run(["audit.py"], timeout=3600)
    run(["rederive.py"], timeout=1800)
    run(["figures.py"], timeout=900)
    run(["make_output.py"], timeout=900)
    run(["make_readme.py"], timeout=300)
    logger.info("pipeline complete -> method_out.json, results/, figures/")


if __name__ == "__main__":
    main()
