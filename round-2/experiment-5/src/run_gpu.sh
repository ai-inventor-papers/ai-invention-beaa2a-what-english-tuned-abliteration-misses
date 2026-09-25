#!/bin/bash
# Full GPU chain: GaMS session, then Gemma session (one model on the GPU at a time). Stages are idempotent (skip if output exists).
cd "$(dirname "$0")"
export NUMPY_MADVISE_HUGEPAGE=0
STAGES=${STAGES:-check,gen,acts,kl,hval,util,flores,s5acts,rseq}
for m in ${MODELS_TO_RUN:-gams gemma}; do
  .venv/bin/python method.py --model $m --stages $STAGES >> logs/full_$m.out 2>&1
  echo "$m exit $? $(date -u +%H:%M:%S) stages=$STAGES" >> logs/run_gpu_status.txt
done
