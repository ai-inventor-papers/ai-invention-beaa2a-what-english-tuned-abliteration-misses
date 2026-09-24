#!/usr/bin/env bash
# GPU chain after the Gemma run: community held-out edit (Stage 4), then GaMS3 descriptive contrast (Stage 5).
# Usage: bash run_chain.sh <gemma_pid>
cd "$(dirname "$0")"
while kill -0 "$1" 2>/dev/null; do sleep 20; done
.venv/bin/python method.py --model community > logs/full_community.out 2>&1; echo "community exit $?" >> logs/chain.log
.venv/bin/python method.py --model gams3 > logs/full_gams3.out 2>&1; echo "gams3 exit $?" >> logs/chain.log
.venv/bin/python method.py --model gemma --explore > logs/full_explore.out 2>&1; echo "explore exit $?" >> logs/chain.log
touch results/GEN_DONE
