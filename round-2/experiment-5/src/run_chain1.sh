#!/bin/bash
cd "$(dirname "$0")"
STAGES=util,flores,s5acts,rseq MODELS_TO_RUN=gams ./run_gpu.sh
STAGES=check,gen,acts,kl,hval,util,flores,s5acts,rseq MODELS_TO_RUN=gemma ./run_gpu.sh
