#!/bin/bash
# When a model's first run finishes its generation stage, stop it and relaunch with the amended pipeline
cd ..
declare -A done
while [ "${done[gams3]}" != 1 ] || [ "${done[gemma]}" != 1 ]; do
  for m in gams3 gemma; do
    if [ "${done[$m]}" != 1 ] && grep -a -q "stage generations took" logs/full_$m.out; then
      kill $(cat logs/full_$m.pid) 2>/dev/null; sleep 5
      if [ $m = gemma ]; then export A1_TOKEN_BUDGET=3072; else export A1_TOKEN_BUDGET=6144; fi
      PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True nohup .venv/bin/python method.py --model $m --skip-sensitivity > logs/full2_$m.out 2>&1 &
      echo $! > logs/full2_$m.pid; echo "$(date +%T) relaunched $m"; done[$m]=1
    fi
  done
  sleep 10
done
