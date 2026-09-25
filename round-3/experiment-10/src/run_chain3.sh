#!/usr/bin/env bash
# After the T1/T2 judging finishes: run the T3 coverage grid (screen-only cells that widen the energy x coverage range
# for the regression), judge them, then mark generation complete.
set -u
cd "$(dirname "$0")"
PY=.venv/bin/python
while ! grep -q "judge_B1 exit" logs/chain.log; do sleep 20; done
export AII_DEADLINE="${1:-0}"
echo "=== stage B T3 $(date -u)" >> logs/chain.log
$PY method.py --stage B --tiers T3 > logs/B_T3.out 2>&1; echo "B_T3 exit $?" >> logs/chain.log
$PY judge_local.py > logs/judge_B2.out 2>&1; echo "judge_B2 exit $?" >> logs/chain.log
touch results/GEN_DONE
echo "=== chain3 done $(date -u)" >> logs/chain.log
