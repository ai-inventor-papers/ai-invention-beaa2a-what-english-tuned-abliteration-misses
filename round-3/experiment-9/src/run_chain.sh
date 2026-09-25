#!/usr/bin/env bash
# Everything after `method.py --stage partA+screen`, in the frozen execution order.
# Usage: bash run_chain.sh   (expects results/gens/PA_* and the screen cells to exist)
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python

echo "== 1. judge every generation (partial-aware scorer) + 200 saved exp8 generations (Gate 3)"
$PY judge/local_judge.py --exp8 200
$PY judge/local_judge.py --refail   # unparsed replies: same model/rubric/decoding, larger token budget

echo "== 2. certify the scorer against gpt-4.1 labels already on disk (edited checkpoints only)"
$PY judge/certify.py | tee results/certify_stdout.txt

echo "== 3. if the on-disk kappa missed 0.80, buy ONE <=600-item gpt-4.1 subsample on THIS run's edited cells"
if $PY -c "import json,sys; d=json.load(open('results/judge_certification.json')); sys.exit(0 if not d['pass_on_disk'] else 1)"; then
  $PY judge/api_judge.py --n 600 || echo "gpt-4.1 subsample unavailable (budget/key); continuing with the local scorer"
  $PY judge/local_judge.py            # label any generation the sampler touched but the scorer had not
  $PY judge/certify.py | tee results/certify_stdout.txt
fi

echo "== 4. FREEZE the DEV index and the frozen predictions (before any confirmation generation)"
$PY freeze.py | tee results/freeze_stdout.txt

echo "== 5. confirmation pass (S4 hoc + ind, S6 over-refusal, S7 utility)"
$PY method.py --stage confirm

echo "== 6. judge the confirmation generations"
$PY judge/local_judge.py

echo "== 7. analysis, independent re-derivation, figures, tables, deviations, schema output"
$PY analysis.py | tee results/analysis_stdout.txt
$PY make_deviations.py
$PY rederive.py | tee results/rederive_stdout.txt
$PY figures.py
$PY report_tables.py
$PY build_output.py
echo "== done"

echo "== 8. FINAL declared second touch: S5X paired items for at most two cells"
$PY select_s5x.py
$PY method.py --stage s5x
$PY judge/local_judge.py
$PY judge/local_judge.py --refail
$PY analysis.py | tee results/analysis_stdout.txt
$PY make_deviations.py
$PY rederive.py | tee results/rederive_stdout.txt
$PY figures.py
$PY report_tables.py
$PY build_output.py
echo "== all done"
