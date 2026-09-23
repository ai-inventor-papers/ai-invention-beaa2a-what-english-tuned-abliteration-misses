#!/usr/bin/env bash
# Rebuild the whole frozen corpus from scratch. Needs: a CUDA GPU with >=16 GB, HF_TOKEN with access to gated
# openlanguagedata/flores_plus and meta-llama/Llama-Guard-3-8B, OPENROUTER_API_KEY (~$3.7 of calls; all responses are cached in
# work/llm_cache.jsonl, so a rerun with that file present costs $0 and reproduces the texts exactly).
set -euo pipefail
cd "$(dirname "$0")"
[ -d .venv ] || { uv venv .venv --python=3.12 && uv pip install --python .venv/bin/python -r requirements.txt; }
# fasttext-wheel 0.9.2 + numpy 2: drop the invalid copy=False (idempotent)
sed -i 's/, copy=False//g' .venv/lib/python3.12/site-packages/fasttext/FastText.py
cd src
PY=../.venv/bin/python
$PY s00_fetch.py                                   # raw sources pinned to commit SHAs -> temp/datasets/
$PY s01_prepare.py                                 # S1..S7 base items; S3 = pods' screen_dev.json when present; MC alignment; S4 pre-filter
$PY s02_translate.py                               # local NLLB-1.3B + MADLAD-3B forward alternates
$PY s02b_llm.py --tasks screenspec,cat,corr        # gemini screen-spec SL (S1/S2/S3), gpt-4.1-mini labeller 2 + correspondence judge
$PY s03_guard.py                                   # Llama-Guard-3-8B labeller 1 (local)
EMB_DEVICE=cpu $PY s02b_llm.py --tasks twins       # gpt-4.1 twins (+ gpt-4.1-mini safety, LaBSE, length checks)
$PY s03_guard.py --twins                           # Llama Guard on twin candidates
$PY s04b_select_twins.py                           # validate + select twins
$PY s05_assemble.py --phase freeze                 # categories -> balanced row_id assignment -> S5 core freeze
$PY s02b_llm.py --tasks strong                     # gpt-4.1 SL for S4 pairs, S6 (trigger), S5 core cross-translations (S5X)
$PY s02_translate.py --llm-qc                      # MADLAD back-translation of every canonical output
$PY s05_assemble.py                                # QC, audit, packet, split JSONL + SHA256 manifest
cd .. && uv run data.py                            # -> full_data_out.json, schema exp_sel_data_out
SK=/ai-inventor/.claude/skills/aii-json; SPY=$SK/../.ability_client_venv/bin/python
$SPY $SK/scripts/aii_json_format_mini_preview.py --input "$PWD/full_data_out.json"   # full_/mini_/preview_full_data_out.json
mv full_full_data_out.json full_data_out.json; mv mini_full_data_out.json mini_data_out.json; mv preview_full_data_out.json preview_data_out.json
