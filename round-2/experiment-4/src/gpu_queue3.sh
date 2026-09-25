#!/usr/bin/env bash
# Re-ordered post-generation GPU chain after the primary judge was blocked (F1):
# community smoke (already running) -> autoscore -> LOCAL SUBSTITUTE JUDGE -> PolyGuard -> Llama-Guard
cd "$(dirname "$0")"
PY=.venv/bin/python
while kill -0 6728 2>/dev/null; do sleep 10; done
echo "smoke_community done" >> logs/gpu_queue3.status
$PY autoscore.py > logs/autoscore.out 2>&1; echo "autoscore rc=$?" >> logs/gpu_queue3.status
$PY local_judge.py all > logs/local_judge.out 2>&1; echo "local_judge rc=$?" >> logs/gpu_queue3.status
$PY guard_pipeline.py polyguard > logs/guard_polyguard.out 2>&1; echo "polyguard rc=$?" >> logs/gpu_queue3.status
$PY guard_pipeline.py llamaguard > logs/guard_llamaguard.out 2>&1; echo "llamaguard rc=$?" >> logs/gpu_queue3.status
echo ALL_DONE >> logs/gpu_queue3.status
