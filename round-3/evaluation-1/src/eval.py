#!/usr/bin/env python3
"""Entry point of the iteration-3 audit / judge-sensitivity evaluation (CPU only, ~1.5 min).

Runs every stage in order (the same sequence as run_all.sh), then the independent headline re-derivation:
  .venv/bin/python eval.py
Outputs: eval_out.json (+ full/mini/preview), results/*, figures/*. See README.md and reproducibility.md.
"""
import subprocess
import sys
from pathlib import Path

WS = Path(__file__).resolve().parent
STAGES = ["s01_labels", "s02_iter1", "s03_judges", "s04_claims", "s05_panels", "s06_ledger", "s07_placebos",
          "s08_assemble", "s09_figures", "s10_eval_out", "verify_headlines_indep"]
# s11_topup (optional gpt-4.1 top-up) is NOT run here: it needs OPENROUTER_API_KEY and was blocked (HTTP 403) in the recorded run.

if __name__ == "__main__":
    for s in STAGES:
        print(f"== {s}", flush=True)
        subprocess.run([sys.executable, str(WS / "scripts" / f"{s}.py")], cwd=WS, check=True)
