#!/usr/bin/env bash
# GPU chain: (stage A must already be running or done) -> local judge on the DEV arms -> FREEZE -> stage B cells in
# priority order (T1 matched-energy groups + controls, T2 anchors, T3/T4 grid) -> judge -> analysis.
# Usage: bash run_chain.sh <stage_A_pid|0> [deadline_epoch]
set -u
cd "$(dirname "$0")"
PY=.venv/bin/python
if [ "${1:-0}" != "0" ]; then while kill -0 "$1" 2>/dev/null; do sleep 15; done; fi
echo "=== judging DEV $(date -u)" >> logs/chain.log
$PY judge_local.py --splits dev dev_ben > logs/judge_dev.out 2>&1; echo "judge_dev exit $?" >> logs/chain.log
$PY freeze.py > logs/freeze.out 2>&1; echo "freeze exit $?" >> logs/chain.log
export AII_DEADLINE="${2:-0}"
$PY method.py --stage B --tiers T1 T2 > logs/B_T1T2.out 2>&1; echo "B_T1T2 exit $?" >> logs/chain.log
$PY judge_local.py > logs/judge_B1.out 2>&1; echo "judge_B1 exit $?" >> logs/chain.log
$PY method.py --stage B --tiers T3 T4 > logs/B_T3T4.out 2>&1; echo "B_T3T4 exit $?" >> logs/chain.log
$PY judge_local.py > logs/judge_B2.out 2>&1; echo "judge_B2 exit $?" >> logs/chain.log
touch results/GEN_DONE
echo "=== chain done $(date -u)" >> logs/chain.log
