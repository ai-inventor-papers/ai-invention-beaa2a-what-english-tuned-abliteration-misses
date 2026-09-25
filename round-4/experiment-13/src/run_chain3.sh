#!/bin/bash
# Chain 3 (as run): resumes chain 2 after the outside Phase-A crash (exp12 items lacked a 'kind' field; fixed in outside.py).
cd "$(dirname "$0")"
step() { echo "== $1 $(date -u +%T)"; shift; "$@" || { echo "FAILED: $*"; exit 1; }; }
step outsideA  .venv/bin/python method.py --stage outside      > logs/run_outsideA2.out 2>&1
step judge2    .venv/bin/python judge/local_judge.py --batch 48 > logs/run_judge2.out 2>&1
step refail2   .venv/bin/python judge/local_judge.py --refail --batch 32 > logs/run_refail2.out 2>&1
step freezeO   .venv/bin/python freeze_outside.py              > logs/run_freeze_outside.out 2>&1
step outsideB  .venv/bin/python method.py --stage outside      > logs/run_outsideB.out 2>&1
step judge3    .venv/bin/python judge/local_judge.py --batch 48 > logs/run_judge3.out 2>&1
step refail3   .venv/bin/python judge/local_judge.py --refail --batch 32 > logs/run_refail3.out 2>&1
echo "== CHAIN3 DONE $(date -u +%T)"
