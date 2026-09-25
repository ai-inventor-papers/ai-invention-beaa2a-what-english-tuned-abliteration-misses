#!/usr/bin/env bash
# Llama-Guard retry (the cached snapshot was incomplete; missing files fetched) -> combine/summary -> R_seq chain.
# Waits for the already-running local_judge retry (PID 8855) so only one process holds the GPU.
cd "$(dirname "$0")"
PY=.venv/bin/python
while kill -0 8855 2>/dev/null; do sleep 10; done
echo "local_judge retry finished" >> logs/gpu_queue5.status
$PY guard_pipeline.py llamaguard > logs/guard_llamaguard2.out 2>&1; echo "llamaguard rc=$?" >> logs/gpu_queue5.status
$PY guard_pipeline.py combine > logs/guard_combine.out 2>&1; echo "combine rc=$?" >> logs/gpu_queue5.status
$PY guard_pipeline.py summary > logs/guard_summary.out 2>&1; echo "summary rc=$?" >> logs/gpu_queue5.status
$PY rseq.py refs --labels-dir results/judge_local > logs/rseq_refs.out 2>&1; echo "rseq refs rc=$?" >> logs/gpu_queue5.status
for m in gams gemma community; do
  $PY rseq.py score --model $m --labels-dir results/judge_local > logs/rseq_score_$m.out 2>&1; echo "rseq score $m rc=$?" >> logs/gpu_queue5.status
done
$PY rseq.py report --labels-dir results/judge_local > logs/rseq_report.out 2>&1; echo "rseq report rc=$?" >> logs/gpu_queue5.status
echo ALL_DONE >> logs/gpu_queue5.status
