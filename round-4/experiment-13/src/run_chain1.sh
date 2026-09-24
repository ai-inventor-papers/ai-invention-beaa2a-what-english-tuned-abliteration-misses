#!/bin/bash
# Chain 1 (as run): wait for Phase 1 generation, then judge every generation with the local Qwen3-14B scorer.
cd "$(dirname "$0")"
until grep -q "^EXIT" logs/run_profile.out; do sleep 10; done
grep -q "^EXIT 0" logs/run_profile.out || { echo "profile failed"; exit 1; }
.venv/bin/python judge/local_judge.py --batch 48 > logs/run_judge1.out 2>&1
echo "EXIT $?" >> logs/run_judge1.out
