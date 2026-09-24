#!/usr/bin/env bash
# F1: watch the run-level OpenRouter budget (free /key endpoint); if it is raised, resume the PRIMARY gpt-4.1 judge
# (judge.py skips item_keys already labelled): core checkpoints first, then community_ref, then the frozen second-judge sample.
cd "$(dirname "$0")"
PY=.venv/bin/python
st() { echo "$(date -u +%H:%M:%S) $*" >> logs/key_watch.status; }
while true; do
  REM=$(curl -s "$OPENROUTER_BASE_URL/key" -H "Authorization: Bearer $OPENROUTER_API_KEY" | python3 -c "import json,sys;print(json.load(sys.stdin)['data'].get('limit_remaining') or 0)" 2>/dev/null || echo 0)
  if python3 -c "import sys; sys.exit(0 if float('$REM') > 1.0 else 1)"; then
    st "budget available: limit_remaining=$REM -> resuming primary judge"
    $PY judge.py --ckpts gams_orig,gams_edit,gemma_orig,gemma_edit > logs/judge_core_resume.out 2>&1; st "core resume rc=$?"
    if [ ! -f results/judge_blocked_again.flag ] && ! grep -q "KEY BLOCKED" logs/judge_core_resume.out; then
      $PY judge.py --ckpts community_ref > logs/judge_community.out 2>&1; st "community rc=$?"
      $PY judge2.py sample > logs/judge2.out 2>&1; st "judge2 rc=$?"
      st "DONE"; exit 0
    fi
    st "blocked again during resume; continuing to watch"
  fi
  sleep 180
done
