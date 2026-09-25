#!/usr/bin/env python3
"""Single entry point for the whole study: freeze the data, measure the DEV depth-coverage index per language, FREEZE the
predictions, run the English-derived Heretic weight panel on held-out items, judge everything blind, and analyse.

The stages live in code/ and are also runnable individually (see README.md); this driver just runs them in the order the
protocol requires and refuses to run them out of order. The freeze is enforced inside code/run_model.py --phase conf,
which raises if configs/frozen_predictions.json is missing or its sha256 is absent from configs/FREEZE.sha256.

  uv run method.py --all                     # everything, in order
  uv run method.py --stage dev               # directions + DEV index curves + CAL, for every model
  uv run method.py --stage freeze            # indices -> configs/frozen_predictions.json (once, irreversible)
  uv run method.py --stage conf              # weight panel on the confirmation set (requires the freeze)
  uv run method.py --stage analyse           # judge -> analysis -> rederive -> figures -> outputs
  uv run method.py --mini                    # tiny smoke run of dev+conf (writes to results_mini/, needs AII_RES set)

Thread caps matter: source env.sh first (48 default BLAS threads on a shared host slowed the SVDs by >10x)."""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = str(ROOT / ".venv" / "bin" / "python")
MODELS = ["gemma", "qwen3", "mistral"]


def run(args: list[str], what: str) -> None:
    print(f"\n=== {what} ===", flush=True)
    t = time.time()
    r = subprocess.run([PY] + args, cwd=ROOT)
    if r.returncode != 0:
        raise SystemExit(f"FAILED ({r.returncode}): {what}")
    print(f"=== {what} done in {time.time() - t:.0f}s ===", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["setup", "dev", "freeze", "conf", "analyse"], default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--mini", action="store_true")
    ap.add_argument("--models", default=",".join(MODELS))
    a = ap.parse_args()
    models = [m for m in a.models.split(",") if m]
    stages = ["setup", "dev", "freeze", "conf", "analyse"] if a.all else ([a.stage] if a.stage else [])
    if not stages:
        ap.error("pass --all or --stage")
    mini = ["--mini"] if a.mini else []

    if "setup" in stages:
        run(["code/dl_models.py", "gemma", "judge", "qwen3", "mistral", "nllb", "labse", "glotlid"], "download pinned models")
        run(["code/certify_judge.py"], "stage 1: certify the judge on existing gpt-4.1 labels")
        run(["code/data_prep.py", "--no-api"], "stage 2: frozen items + NLLB DE/LT translation + QC")
    if "dev" in stages:
        for m in models:
            run(["code/run_model.py", "--model", m, "--phase", "dev"] + mini, f"stage 3a-3c: DEV phase [{m}]")
        run(["code/judge_local.py", "--calibrate", "--label", "--phases", "dev,cal"], "stage 4: judge DEV + CAL")
    if "freeze" in stages:
        run(["code/dev_index.py", "--models", ",".join(models), "--freeze"], "stage 3d: indices + FREEZE (irreversible)")
    if "conf" in stages:
        # M3 was dropped from the weight panel under the pre-registered cut order (all its rows are ineligible).
        for m in models:
            extra = ["--cells", "W0,W2,W3"] if m == "mistral" else []
            run(["code/run_model.py", "--model", m, "--phase", "conf"] + extra + mini, f"stage 3e: weight panel [{m}]")
        run(["code/judge_local.py", "--label", "--phases", "conf"], "stage 4: judge CONF")
    if "analyse" in stages:
        run(["code/analysis.py"], "stage 6: frozen confirmatory analysis")
        run(["code/rederive.py"], "stage 7: independent re-derivation + placebos")
        run(["code/posthoc.py"], "post-hoc (exploratory) within/between-model decomposition")
        run(["code/checks.py"], "final audit")
        run(["code/figures.py"], "stage 8: figures")
        run(["code/predictors.py"], "head-to-head out-of-sample predictions (predict_* fields)")
        run(["code/report_tables.py"], "stage 8: report tables")
        run(["code/cleanup.py"], "slim the direction archives")
        run(["code/build_output.py"], "stage 8: method_out.json")
    print("\nAll requested stages complete.", flush=True)


if __name__ == "__main__":
    sys.exit(main())
