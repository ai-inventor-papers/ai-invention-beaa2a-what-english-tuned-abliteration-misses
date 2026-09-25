#!/bin/bash
# after the corrected run: selection -> arms -> FROZEN predictions -> eval generation -> judge-grade reselection
# -> (optional D2 arm) -> judges on every eval generation. GPU stages strictly sequential.
cd "$(dirname "$0")"
PY=.venv/bin/python
while kill -0 $(cat logs/chain3.pid) 2>/dev/null; do sleep 5; done
$PY inloop.py collect || exit 1
$PY analyze_inloop.py > logs/analyze_inloop_1.out 2>&1 || { echo "analyze_inloop failed"; exit 1; }
$PY make_arms.py || exit 1
cp arms.json results/arms_frozen_v1.json
$PY freeze_predictions.py || exit 1
echo EVALGEN_START $(date +%T)
$PY eval_gen.py --arms arms.json > logs/eval_gen.out 2>&1 || { echo "eval_gen failed"; exit 1; }
echo EVALGEN_DONE $(date +%T)
$PY inloop.py judge_input --select corrected --out results/judge_in/inloop_corrected.jsonl
$PY judges.py local --inp results/judge_in/inloop_corrected.jsonl --out results/judge_out/inloop_qwen.jsonl --bs 32 > logs/judge_corr.out 2>&1
echo JUDGE_CORR_DONE $(date +%T)
$PY analyze_inloop.py > logs/analyze_inloop_2.out 2>&1
$PY make_arms.py
$PY eval_gen.py --arms arms.json > logs/eval_gen2.out 2>&1
echo EVALGEN2_DONE $(date +%T)
$PY eval_judge_input.py
$PY judges.py local --inp results/judge_in/eval_all.jsonl --out results/judge_out/eval_qwen.jsonl --bs 24 > logs/judge_eval.out 2>&1
echo JUDGE_EVAL_DONE $(date +%T)
$PY guard.py polyguard --inp results/judge_in/eval_all.jsonl --out results/judge_out/eval_polyguard.jsonl > logs/guard_pg.out 2>&1
$PY guard.py llamaguard --inp results/judge_in/eval_harmful.jsonl --out results/judge_out/eval_llamaguard.jsonl > logs/guard_lg.out 2>&1
echo CHAIN4_DONE $(date +%T)
