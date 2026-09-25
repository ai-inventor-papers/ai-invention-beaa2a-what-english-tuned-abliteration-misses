#!/bin/bash
# CONF chain: gemma + qwen3 full panel (they hold every eligible row), mistral W0/W2/W3 (pre-registered CUT ORDER:
# all its rows are ineligible, so it is a reported descriptive row). Then judge CONF, analysis, rederive, figures, output.
cd "$(dirname "$0")"; source env.sh
.venv/bin/python code/run_model.py --model gemma  --phase conf > logs/gemma_conf.out 2>&1  || echo "FAILED gemma"  >> logs/chain_conf.status
.venv/bin/python code/run_model.py --model qwen3  --phase conf > logs/qwen3_conf.out 2>&1  || echo "FAILED qwen3"  >> logs/chain_conf.status
echo GEN_GQ_DONE >> logs/chain_conf.status
.venv/bin/python code/run_model.py --model mistral --phase conf --cells W0,W2,W3 > logs/mistral_conf.out 2>&1 || echo "FAILED mistral" >> logs/chain_conf.status
echo GEN_ALL_DONE >> logs/chain_conf.status
