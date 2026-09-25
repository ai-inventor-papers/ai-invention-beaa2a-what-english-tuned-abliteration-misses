#!/bin/bash
# poll: judge new validity generation files with gpt-4.1 until panel.py (PID given) has exited and all files are judged
cd ..
PANEL_PID=$1
while true; do
  .venv/bin/python judge_api.py --targets validity >> logs/judge_loop.out 2>&1
  if ! kill -0 $PANEL_PID 2>/dev/null; then
    .venv/bin/python judge_api.py --targets validity >> logs/judge_loop.out 2>&1
    break
  fi
  sleep 90
done
echo LOOP_DONE >> logs/judge_loop.out
