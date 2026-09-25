#!/bin/bash
cd "$(dirname "$0")"
export NUMPY_MADVISE_HUGEPAGE=0
for m in gemma gams; do
  .venv/bin/python dose.py --model $m >> logs/dose_$m.out 2>&1
  echo "dose $m exit $? $(date -u +%H:%M:%S)" >> logs/run_gpu_status.txt
done
