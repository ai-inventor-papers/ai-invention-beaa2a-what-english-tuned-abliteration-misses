#!/bin/bash
# Chain 2 (as run, after freeze.py): Phase 4 confirmation (Gemma) -> Phase 5A (Qwen3-8B gate + profile) -> judge ->
# freeze_outside.py -> Phase 5B (Qwen3-8B confirmation) -> judge. Stops at the first failure.
cd "$(dirname "$0")"
set -o pipefail
step() { echo "== $1 $(date -u +%T)"; shift; "$@" || { echo "FAILED: $*"; exit 1; }; }
step confirm   .venv/bin/python method.py --stage confirm      > logs/run_confirm.out 2>&1
step outsideA  .venv/bin/python method.py --stage outside      > logs/run_outsideA.out 2>&1
step judge2    .venv/bin/python judge/local_judge.py --batch 48 > logs/run_judge2.out 2>&1
step freezeO   .venv/bin/python freeze_outside.py              > logs/run_freeze_outside.out 2>&1
step outsideB  .venv/bin/python method.py --stage outside      > logs/run_outsideB.out 2>&1
step judge3    .venv/bin/python judge/local_judge.py --batch 48 > logs/run_judge3.out 2>&1
echo "== CHAIN2 DONE $(date -u +%T)"
