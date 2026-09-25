#!/usr/bin/env bash
# API chain after the shared OpenRouter key's daily reset (00:00 UTC):
# probe (1 call) -> B5 calibration (40 DEV items) -> T5 (10 items) -> [gate] -> primary judge on the 4 CORE checkpoints.
cd "$(dirname "$0")"
PY=.venv/bin/python
st() { echo "$(date -u +%H:%M:%S) $*" >> logs/api_queue.status; }
until curl -s "$OPENROUTER_BASE_URL/chat/completions" -H "Authorization: Bearer $OPENROUTER_API_KEY" -H "Content-Type: application/json" \
   -d '{"model":"openai/gpt-4.1","messages":[{"role":"user","content":"Say OK"}],"max_tokens":4,"usage":{"include":true}}' \
   > logs/key_probe_latest.json && grep -q '"choices"' logs/key_probe_latest.json; do sleep 60; done
st "KEY OK: $(head -c 300 logs/key_probe_latest.json)"
$PY judge2.py calibrate > logs/judge_calibrate.out 2>&1; st "calibrate rc=$?"
$PY judge.py --ckpts gams_orig,gams_edit --limit 10 --out-dir results/judge_t5 > logs/judge_t5.out 2>&1; st "t5 judge rc=$?"
$PY t5_check.py >> logs/api_queue.status 2>&1; T5=$?
CAL=$($PY -c "import json;print(json.load(open('results/judge_dev_calibration.json')).get('pass_0.8'))")
st "t5 pass rc=$T5 calibration pass=$CAL"
if [ "$T5" != "0" ] || [ "$CAL" != "True" ]; then st "GATE FAILED - stopping before FINAL judging"; exit 1; fi
until [ "$(wc -l < results/gen/gemma_orig.jsonl 2>/dev/null)" -ge 960 ] && [ "$(wc -l < results/gen/gemma_edit.jsonl 2>/dev/null)" -ge 960 ] \
   && [ "$(wc -l < results/gen/gams_edit.jsonl)" -ge 960 ]; do sleep 30; done
$PY judge.py --ckpts gams_orig,gams_edit,gemma_orig,gemma_edit > logs/judge_core.out 2>&1; st "core judge rc=$?"
echo CORE_DONE >> logs/api_queue.status
