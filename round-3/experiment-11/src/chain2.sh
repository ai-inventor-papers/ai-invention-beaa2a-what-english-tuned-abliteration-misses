#!/bin/bash
# after chain 1: the ONE permitted refit + recertification on the held-out certification trials
cd "$(dirname "$0")"
while kill -0 $(cat logs/chain1.pid) 2>/dev/null; do sleep 5; done
.venv/bin/python inloop.py refit_table --qwen results/judge_out/inloop_qwen.jsonl --out results/judge_in/inloop_refit_rows.jsonl
.venv/bin/python train_clf.py refit --inloop results/judge_in/inloop_refit_rows.jsonl
.venv/bin/python inloop.py certify --out scorer/certification.json
echo CHAIN2_DONE
