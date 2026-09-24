#!/usr/bin/env bash
# Stage B onward (stage A + DEV judging + FREEZE already done): T1/T2 decisive cells -> judge -> T3/T4 grid -> judge.
# Usage: bash run_chain2.sh [deadline_epoch]
set -u
cd "$(dirname "$0")"
PY=.venv/bin/python
export AII_DEADLINE="${1:-0}"
echo "=== stage B T1/T2 $(date -u)" >> logs/chain.log
$PY method.py --stage B --tiers T1 T2 > logs/B_T1T2.out 2>&1; echo "B_T1T2 exit $?" >> logs/chain.log
$PY judge_local.py > logs/judge_B1.out 2>&1; echo "judge_B1 exit $?" >> logs/chain.log
$PY method.py --stage B --tiers T3 T4 > logs/B_T3T4.out 2>&1; echo "B_T3T4 exit $?" >> logs/chain.log
$PY judge_local.py > logs/judge_B2.out 2>&1; echo "judge_B2 exit $?" >> logs/chain.log
touch results/GEN_DONE
echo "=== chain done $(date -u)" >> logs/chain.log
