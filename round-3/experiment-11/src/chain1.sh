#!/bin/bash
# GPU chain 1: after the replay -> collect in-loop rows -> Qwen3-14B labels for every replayed row (+ orig baseline)
cd "$(dirname "$0")"
while kill -0 1278 2>/dev/null; do sleep 5; done
.venv/bin/python inloop.py collect
.venv/bin/python inloop.py judge_input --select cert --out results/judge_in/inloop_certset.jsonl
.venv/bin/python inloop.py judge_input --tags tpe60_115 --out results/judge_in/inloop_replay_all.jsonl
# certification trials first (so the gate can be computed early), then everything else (resumable by key)
.venv/bin/python judges.py local --inp results/judge_in/inloop_certset.jsonl --out results/judge_out/inloop_qwen.jsonl --bs 32
echo CERTSET_LABELLED
.venv/bin/python judges.py local --inp results/judge_in/inloop_replay_all.jsonl --out results/judge_out/inloop_qwen.jsonl --bs 32
echo CHAIN1_DONE
