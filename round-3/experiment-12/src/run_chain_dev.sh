#!/bin/bash
# DEV chain: wait for Gemma DEV, then Qwen3 DEV, Mistral DEV, then local-judge calibration + labelling of DEV/CAL.
cd "$(dirname "$0")"; source env.sh
while kill -0 $(cat logs/gemma_dev.pid) 2>/dev/null; do sleep 5; done
.venv/bin/python code/run_model.py --model qwen3 --phase dev > logs/qwen3_dev.out 2>&1
.venv/bin/python code/run_model.py --model mistral --phase dev > logs/mistral_dev.out 2>&1
.venv/bin/python code/judge_local.py --calibrate --label --phases dev,cal > logs/judge_dev.out 2>&1
echo CHAIN_DONE >> logs/chain_dev.status
