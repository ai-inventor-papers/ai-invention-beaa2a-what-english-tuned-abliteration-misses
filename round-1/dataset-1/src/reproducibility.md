# Reproducibility: frozen EN/SL safety and utility test sets

This artifact builds, freezes, hashes and audits the English/Slovene data splits (S1–S7) for the GaMS3-12B-Instruct vs gemma-3-12b-it Heretic study. It runs no study model. The "results" are the frozen data files and their audit reports, not model scores.

Everything below comes from files in this folder (`README.md`, `run_all.sh`, `data.py`, `src/*.py`, `pyproject.toml`, `requirements.txt`, `data/`, `logs/`). Points the workspace does not record are marked **not recorded**.

## 1. Get the artifact

The workspace is one folder of a public GitHub repository. Clone that repository and `cd` into this folder (`gen_art_dataset_1`). The repository URL is not stored in the workspace, so use the one where you found this artifact. All paths below are relative to this folder.

The repository ships the frozen outputs (`full_data_out.json`, `data/splits/*.jsonl`, `data/split_manifest.json`, `data/reports/*`). `work/llm_cache.jsonl` is in the workspace listing, but whether it is in the public repository was not checked (`git ls-files` showed no tracked copy). If it is absent, the LLM steps re-call OpenRouter and outputs may differ. `temp/datasets/` (raw source dumps) and `.venv/` are not in the workspace listing, and `work/labse_cache/` is regenerated.

## 2. System, Python, environment

- Ubuntu (the run was on Linux 6.8). Needs `uv` and Python 3.12 (`requires-python >=3.12`; `uv venv --python=3.12` was used).
- A C compiler was not available on the build machine, so torch compilation is disabled in the code (`TORCHDYNAMO_DISABLE=1` is set in `src/common.py` and `src/s02_translate.py`).
- Create the venv with the exact pins in `requirements.txt` (identical to `pyproject.toml`; both come from `uv pip freeze`). Key pins: torch 2.14.0, transformers 4.55.4, tokenizers 0.21.4, sentence-transformers 5.7.0, bitsandbytes 0.50.2, accelerate 1.15.0, datasets 5.0.1, huggingface-hub 0.36.2, numpy 2.2.6, pandas 3.0.6, scikit-learn 1.9.1, sacrebleu 2.6.0, fasttext-wheel 0.9.2, loguru 0.7.3.

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r requirements.txt
# fasttext-wheel 0.9.2 with numpy 2: remove the invalid copy=False (idempotent)
sed -i 's/, copy=False//g' .venv/lib/python3.12/site-packages/fasttext/FastText.py
```

## 3. Downloads, keys, inputs

Environment variables (names only):
- `HF_TOKEN`: needed for the gated `openlanguagedata/flores_plus` and `meta-llama/Llama-Guard-3-8B`.
- `OPENROUTER_API_KEY`: read by `src/orclient.py`. It is only needed for calls not already in `work/llm_cache.jsonl`. With `work/llm_cache.jsonl` present the rerun is meant to cost $0 and reproduce the texts exactly, keyed by sha256(model, messages, temperature, seed, extra).
- `EMB_DEVICE` (optional, `cuda` by default; `run_all.sh` sets `cpu` for the twins step).

Data: `src/s00_fetch.py` downloads the raw sources into `temp/datasets/`, pinned to the revisions in `data/provenance/sources.json`. These include:
- mlabonne/harmful_behaviors `01cead01…`, mlabonne/harmless_alpaca `02c6a92c…`
- heretic-org/Semantic-Harmful `001ca2ce…` and Semantic-Harmless `7e9f2b01…`
- JailbreakBench/JBB-Behaviors `886acc35…`, databricks-dolly-15k `bdd27f4d…`
- openlanguagedata/flores_plus `5fec6c13…`, cjvt/slovenian-llm-eval `ca2f68d3…`
- allenai/ai2_arc, google/boolq, Rowan/hellaswag, allenai/openbookqa, baber/piqa, allenai/winogrande
- NASK-PIB/RefusEU `5523ce30…`
- the StrongREJECT, XSTest, AdvBench and HarmBench GitHub repos, and walledai/MaliciousInstruct

Full SHAs and row counts are in `sources.json`.

Models (shared HF cache, `huggingface-cli download <id> --revision <sha>`), as listed in `README.md`:
- `facebook/nllb-200-distilled-1.3B@7be3e246`
- `google/madlad400-3b-mt@fa184c67`
- `meta-llama/Llama-Guard-3-8B@7327bd9f` (gated; run locally in NF4 4-bit)
- `sentence-transformers/LaBSE@836121a0`
- `cis-lmu/glotlid@85cd6716`

Hosted LLMs via OpenRouter: `openai/gpt-4.1`, `openai/gpt-4.1-mini`, `google/gemini-2.5-flash`, plus claude-sonnet-4.5 for 1 row of S5X.

**Sibling-artifact inputs (not fully portable).** `src/s01_prepare.py` reads the pods' files from `gen_art_experiment_3/data/` (`screen_dev.json`, `dev_carveout_ids.json`) and `gen_art_experiment_1/data/sl_harmful_behaviors_test100.json`. It finds them through the constant `RUN_ITER1` in `src/common.py:24`, which is an absolute path on the original server: `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1`. These are sibling artifacts (`gen_art_experiment_3`, `gen_art_experiment_1`) published as sibling folders.
- To rebuild, edit `RUN_ITER1` in `src/common.py` to point at the parent folder that holds `gen_art/…`, or otherwise make those files reachable.
- If the pod files are absent, the code reproduces S3 from the shared screen spec alone. It records "pod equality UNVERIFIED", and S3 ids, halves and S1/S2 SL texts will then differ from the frozen data.
- The frozen result was built with the pod files present. The shipped `data/splits/*.jsonl` and the manifest already contain them.

## 4. Commands, in the order run (`run_all.sh`)

```bash
bash run_all.sh
```

This is equivalent to the following, run from `src/`. `$PY` is `../.venv/bin/python`.

```bash
$PY s00_fetch.py
$PY s01_prepare.py
$PY s02_translate.py
$PY s02b_llm.py --tasks screenspec,cat,corr
$PY s03_guard.py
EMB_DEVICE=cpu $PY s02b_llm.py --tasks twins
$PY s03_guard.py --twins
$PY s04b_select_twins.py
$PY s05_assemble.py --phase freeze
$PY s02b_llm.py --tasks strong
$PY s02_translate.py --llm-qc
$PY s05_assemble.py
cd .. && uv run data.py
```

The last two lines of `run_all.sh` call the aii-json script `aii_json_format_mini_preview.py` through an absolute `/ai-inventor/.claude/skills/aii-json` path on the original server. That script produces `mini_data_out.json` and `preview_data_out.json` and renames its outputs. This tooling is not in the repository. The shipped mini and preview files are the result, and `data.py` alone regenerates `full_data_out.json`.

To only re-standardise the frozen splits: `uv run data.py`. It does three things:
- re-checks the raw files in `temp/datasets/` against `sources.json` (this needs those files, otherwise it exits);
- checks each `data/splits/<family>.jsonl` SHA256 (of the sorted lines) against `data/split_manifest.json`, and exits if a split was modified;
- writes `full_data_out.json`.

`data.py` therefore refuses to run without `temp/datasets/`. Run `src/s00_fetch.py` first.

Seeds and configs found in the code:
- Dolly: `np.random.default_rng(0)`.
- S5 core: `np.random.default_rng(20260923)`, 50 per category (`data/s5_core_freeze.json`).
- MC carve-out: 40 per task, seed 0.
- S4 twins: gpt-4.1 candidate 0 at T=0. Candidates 1 and 2 at T=0.7 with seeds 1 and 2, only for items whose earlier candidates failed.
- Translation and QC LLM calls: T=0 (per the README and the `screenspec_layout_check` report).
- Half assignment: `half = 'A' if int(sha1(semantic_id).hexdigest(),16) % 2 == 0 else 'B'`.

Hardware and runtime: a CUDA GPU with at least 16 GB is required (per `run_all.sh`). The GPU model, VRAM and total wall-clock time were **not recorded**; the machine had no `nvidia-smi` when this file was written. The logs show OOM fallbacks to batch 24 during MADLAD translation (`logs/s02_full.out`, about 2.6–16 texts/s). Llama Guard labelling of 3,979 items ran at about 6 items/s (`logs/s03_full.out`). The whole build was done on 2026-09-23. `split_manifest.json` has `frozen_utc` 2026-09-23T16:26:24Z.

Cost: `data/cost_log.jsonl` records every OpenRouter call, 5,474 calls, cumulative $4.77 (last `cum_usd` about 4.77). `run_all.sh` comments estimate about $3.7. `data/corpus_metadata.json` says `llm_api_spend_usd: 0.0`, which is stale and contradicts the cost log.

## 5. Expected outputs and numbers

- `full_data_out.json`: 48,696 examples in 10 blocks, schema `exp_sel_data_out`, 67.6 MB. Also `mini_data_out.json` and `preview_data_out.json`.
- `data/split_manifest.json`: per-split SHA256, seeds, `protocol_hash` = `dc33bde4e8ea39ee416af3e9c65eeb9d8583303bdd39130cb8c86831624c9306`. This hash includes the freeze timestamp, so a rebuild gives a different hash unless the manifest is kept.
- `data/splits/*.jsonl`: 17 frozen families.
- Block sizes (EN+SL rows):

| block | rows |
|---|---|
| S1 | 1000+1000 |
| S2 | 832+832 |
| S3 prompts | 270+270 |
| S3 utility | 320+320 |
| S4 | 514+514 (257 pairs: 70 `hoc`, 187 `ind`) |
| S5 | 1400+1400 (core 700 per language) |
| S5X | 700+700 |
| S6 | 450+450 (219 primary safe items) |
| S7 tasks | 17850+17850 |
| S7 FLORES devtest | 1012+1012 |

- RefusEU EN–SL correspondence (`data/reports/refuseu_correspondence.json`, `data/verified_pairs.json`): 0 grade T, 158 P, 1,092 C, 150 N. Same with the MADLAD back-translation. Official rows therefore support no item-paired claims.
- Category inference: Llama-Guard-3-8B 64.5% EN / 49.7% SL on the 141+141 gold rows, labelled low-confidence.
- Screen-spec layout check (`data/reports/screenspec_layout_check.json`): layout A (system message) gemini answered or refused 830 of 1,692 items (49%). Layout B fell to 129 of 1,692.
- S3 pod agreement: `data/reports/s3_pod_agreement.json` (Dolly 100/100, FLORES 200/200, only 50.7% of halves agree with spec strings).
- Overlap audit: `data/reports/overlap_audit.json` (no near-duplicate above 0.85 or exact overlap of S4–S7 with S1–S3, after dropping `srj:184`).
- Translation QC: `data/reports/translation_qc.json`. Native review is **PENDING**: `data/native_review_packet.csv` (250 rows, blinded) and `data/native_review_packet_key.json`. No human review was done; every quality number is automated.
- RefusEU scoring protocol: `data/refuseu_protocol.md`. lm-eval split map: `data/lm_eval_task_map.json`.

**Paper mapping:** the workspace holds no paper or figure files. Where these numbers appear in a paper is **not recorded**.

## 6. Reproducibility caveats

- The rebuild depends on the pods' files (see the `RUN_ITER1` note in section 3) and on hosted LLM outputs (gpt-4.1, gpt-4.1-mini, gemini-2.5-flash). It is deterministic only with the shipped `work/llm_cache.jsonl`.
- Hosted-model versions are not pinned beyond their OpenRouter names.
- The GPU type and runtime are not recorded, and the Llama Guard labelling used NF4 4-bit rather than bf16.
