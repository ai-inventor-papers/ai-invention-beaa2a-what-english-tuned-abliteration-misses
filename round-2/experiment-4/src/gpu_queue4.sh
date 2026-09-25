#!/usr/bin/env bash
# After gpu_queue3: local-judge parse-failure retry (160-token cap) -> Stage H R_seq (labels = substitute local judge).
cd "$(dirname "$0")"
PY=.venv/bin/python
until grep -q ALL_DONE logs/gpu_queue3.status 2>/dev/null; do sleep 20; done
$PY local_judge.py retry > logs/local_judge_retry.out 2>&1; echo "local_judge retry rc=$?" >> logs/gpu_queue4.status
$PY rseq.py refs --labels-dir results/judge_local > logs/rseq_refs.out 2>&1; echo "rseq refs rc=$?" >> logs/gpu_queue4.status
for m in gams gemma community; do
  $PY rseq.py score --model $m --labels-dir results/judge_local > logs/rseq_score_$m.out 2>&1; echo "rseq score $m rc=$?" >> logs/gpu_queue4.status
done
$PY rseq.py report --labels-dir results/judge_local > logs/rseq_report.out 2>&1; echo "rseq report rc=$?" >> logs/gpu_queue4.status
echo ALL_DONE >> logs/gpu_queue4.status
