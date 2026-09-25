#!/bin/bash
# reordered remainder of chain4 (eval labels first): eval judges -> judge-grade labels of the corrected run's
# startup draws -> analysis 2 -> optional D2 arm (judge-grade reselection) -> its labels -> guards
cd "$(dirname "$0")"
PY=.venv/bin/python
while kill -0 8287 2>/dev/null; do sleep 2; done
$PY autoscore.py > logs/autoscore.out 2>&1
$PY eval_judge_input.py
$PY judges.py local --inp results/judge_in/eval_all.jsonl --out results/judge_out/eval_qwen.jsonl --bs 24 > logs/judge_eval.out 2>&1
echo JUDGE_EVAL_DONE $(date +%T)
$PY judges.py local --inp results/judge_in/inloop_corrected.jsonl --out results/judge_out/inloop_qwen.jsonl --bs 32 > logs/judge_corr.out 2>&1
echo JUDGE_CORR_DONE $(date +%T)
$PY reparse.py results/judge_out/inloop_qwen.jsonl results/judge_out/eval_qwen.jsonl
$PY analyze_inloop.py > logs/analyze_inloop_2.out 2>&1
$PY make_arms.py > logs/make_arms_2.out 2>&1
$PY eval_gen.py --arms arms.json > logs/eval_gen2.out 2>&1
echo EVALGEN2_DONE $(date +%T)
$PY autoscore.py > logs/autoscore.out 2>&1
$PY eval_judge_input.py
$PY judges.py local --inp results/judge_in/eval_all.jsonl --out results/judge_out/eval_qwen.jsonl --bs 24 > logs/judge_eval2.out 2>&1
echo JUDGE_EVAL2_DONE $(date +%T)
$PY guard.py polyguard --inp results/judge_in/eval_all.jsonl --out results/judge_out/eval_polyguard.jsonl > logs/guard_pg.out 2>&1
$PY guard.py llamaguard --inp results/judge_in/eval_harmful.jsonl --out results/judge_out/eval_llamaguard.jsonl > logs/guard_lg.out 2>&1
echo CHAIN5_DONE $(date +%T)
