# Reproducibility: bilingual (EN/SL) refusal-suppression evaluation of four checkpoints (+ community reference)

Everything below is taken from the files in this folder (`README.md`, `run_all.sh`, `method.py`, `common.py`, `protocol.yaml`,
`protocol_runtime.json`, `pyproject.toml`, `env/`, `logs/`, `results/`). Nothing was re-run when writing this file.
Points the workspace does not record are marked **not recorded**.

## 1. Get the artifact

This folder is one folder of a public GitHub repository. Clone that repository and `cd` into this folder
(`.../gen_art/gen_art_experiment_4`; the repository URL is not recorded in the workspace). All commands below are run from this folder
with relative paths.

**Inputs from sibling artifacts (published as sibling folders).** `common.py` reads them through absolute constants
`RUN`, `DATASET`, `EXP1`, `EXP3`, currently pointing at `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1/gen_art/...`.
That was the machine path used in the original run. To reproduce elsewhere, edit `RUN` in `common.py` (line 16) so that
the following exist under it (in the repository they are sibling folders):
- `gen_art_dataset_1`: `data/splits/{S5_refuseu,S5X_refuseu_crosstrans,S6_xstest,S3_jbb,S1_heretic}.jsonl`, `data/s5_core_freeze.json`, `data/split_manifest.json`, `data/provenance/heretic_3521f864_config.default.toml`.
- `gen_art_experiment_1`: `pins.json` and the Heretic LoRA adapters `adapters/gams_selected_path2` (trial 88, sha `a4419c51…`) and `adapters/gemma_selected_path2` (trial 96, sha `d219c084…`). The adapters are NOT trained here.
- `gen_art_experiment_3`: `results/judged_generations.json` (used only by the judge calibration / retry paths in `judge2.py`, `local_judge.py`).
No user-uploaded private input is used. The frozen prompt sample for this study is shipped as `frozen_samples.json`.

## 2. System, Python, environment

- Original machine (`env/hardware.txt`): Debian 12 container, AMD Ryzen 9 7950X (14 CPUs available), 56 GB RAM limit, one NVIDIA GeForce RTX 4090 (24 GB VRAM, driver 580.126.20). Ubuntu should work; not tested there. System packages beyond a CUDA-capable NVIDIA driver and `uv` were not recorded.
- Python 3.12 (`requires-python >=3.12,<3.13`). Environment (from `README.md` / `.aii/manifest.yaml`):

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python --index-strategy unsafe-best-match \
  --extra-index-url https://download.pytorch.org/whl/cu128 -r env/requirements.lock
```
- Direct pins (`pyproject.toml`; the full transitive freeze is `env/requirements.lock`): torch 2.11.0+cu128, transformers 5.17.0, peft 0.21.0, bitsandbytes 0.50.2, accelerate 1.15.0, safetensors 0.8.0, huggingface-hub 1.32.0, sentencepiece 0.2.2, numpy 2.5.3, scipy 1.18.1, statsmodels 0.15.0, pandas 3.0.6, pyarrow 25.0.1, matplotlib 3.11.2, fasttext-wheel 0.9.2, aiohttp 3.14.3, tiktoken 0.14.0, tenacity 9.1.4, loguru 0.7.3, pyyaml 6.0.3, psutil 7.2.2, jsonschema 4.26.0.

## 3. Models, downloads, credentials

Weights are not in the folder. Download at pinned revisions (`scratch/dl.py <repo> <revision>`; `verify_pins.py` checks per-shard SHA256 against iteration-1 pins and aborts on mismatch):
- `cjvt/GaMS3-12B-Instruct@1d0b27af5748784482600d24779409e7e1dc9adc`
- `google/gemma-3-12b-it@96b6f1eccf38110c56df3a15bffe176da04bfd80` (gated: requires accepting the licence with a HuggingFace account; token variable name not recorded, standard `huggingface_hub` login)
- `p-e-w/gemma-3-12b-it-heretic@e037e6e112ea85777fc3858469cdc31fdfceaa13`
- `ToxicityPrompts/PolyGuard-Qwen@644bfe73ff498c9a14818b72a11187eaf23f0ff1`
- `meta-llama/Llama-Guard-3-8B@7327bd9f6efbbe6101dc6cc4736302b3cbb6e425` (gated)
- `cis-lmu/glotlid@85cd6716494360367b75f642b5bc78667605d0b4`
- `Qwen/Qwen3-14B@40c069824f4251a91eefaf281ebe4c544efd3e18` (local substitute judge)

Environment variables (names only): `OPENROUTER_BASE_URL` and `OPENROUTER_API_KEY` for the API stages (`judge.py`, `judge2.py`, `guard_pipeline.py adjudicate`); the code says the key only works through the proxy in `OPENROUTER_BASE_URL`. `GEN_VRAM_FRAC` (per-process VRAM fraction, 0.48 used) for `generate.py`. No key is needed for the GPU/local stages or for analysis of the shipped results.

## 4. Commands actually run (order of `run_all.sh`; `method.py --stages all` wraps the same stages)

```bash
PY=.venv/bin/python
$PY verify_pins.py                       # revisions + shard hashes
$PY freeze.py                            # frozen_samples.json + protocol.yaml; must reproduce logs/freeze_hashes.txt
$PY tests/test_stats.py                  # T8 sanity -> results/t8_stats_sanity.json
$PY smoke.py gams && $PY smoke.py gemma --quick     # templates, adapter check, coherence, B3 batching certification
for ck in gams_orig gams_edit; do GEN_VRAM_FRAC=0.48 $PY generate.py --model gams --ckpts $ck & done; wait
for ck in gemma_orig gemma_edit; do GEN_VRAM_FRAC=0.48 $PY generate.py --model gemma --ckpts $ck & done; wait
GEN_VRAM_FRAC=0.48 $PY generate.py --model community --ckpts community_ref --sets S5,S5X --out-dir results/gen_part/a &
GEN_VRAM_FRAC=0.48 $PY generate.py --model community --ckpts community_ref --sets S6 --out-dir results/gen_part/b &
wait; cat results/gen_part/a/community_ref.jsonl results/gen_part/b/community_ref.jsonl > results/gen/community_ref.jsonl
$PY autoscore.py
$PY guard_pipeline.py polyguard && $PY guard_pipeline.py llamaguard
$PY judge2.py calibrate; $PY reparse.py results/judge_dev_calibration.jsonl; $PY judge2.py recalibrate
$PY judge.py                             # gpt-4.1 primary judge (API): BLOCKED at 716/3,840 by the run budget
$PY local_judge.py all && $PY local_judge.py retry   # Qwen3-14B substitute judge, all 4,800 items
$PY agreement_local.py
$PY executor_audit.py sample && $PY executor_audit.py score   # labels in results/executor_audit_labels.json filled by hand
$PY judge2.py sample                     # Gemini second judge: NOT completed (budget)
$PY guard_pipeline.py adjudicate && $PY guard_pipeline.py combine   # adjudicator (gpt-4o-mini) not run; disagreements bounded
$PY agreement.py
$PY analyze.py --judge-dir results/judge_local --label-name judge_local_qwen3_14b --no-fallback
$PY analyze.py --judge-dir results/judge --label-name judge_gpt41 --no-fallback --out results/analysis_gpt41_subset.json
$PY audit.py --judge-dir results/judge_local --asr-from-guard --lang-from-glotlid
$PY verify_headlines.py
for st in "refs" "score --model gams" "score --model gemma" "score --model community" "report"; do $PY rseq.py $st --labels-dir results/judge_local; done
$PY figures.py && $PY human_packet.py && $PY build_metadata.py && $PY to_schema.py
```
Note: `run_all.sh` is the documented order; the real execution used the background chains `gpu_queue*.sh`, `api_queue.sh`, `key_watch.sh` (in `logs/*.status`), and the `analyze` stage in `method.py` additionally passes `--asr-from-judge no --lang-source glotlid` and runs `headline_table.py` (produces `results/headline_table.csv`).

**Seeds/config.** Sample seeds (`freeze.py`): S5 20260923, S5X 20260924, S6 20260925, judge2_sample 20260926. Bootstrap: 2000 cluster draws, seed 20260923, percentile CI; exact McNemar; Holm within the 9-test family per model. Decoding: greedy, `max_new_tokens=256`, system prompt "You are a helpful assistant.", NF4 4-bit (double quant, bf16 compute), text only, exact-length buckets, batch size 32, eager attention (`protocol_runtime.json`). Orig and edit share one base load (adapter enabled vs `disable_adapter()`). Freeze hashes (`logs/freeze_hashes.txt`): `frozen_samples.json` sha256 `c72b89f5…bc016`, `protocol.yaml` `0ba5ed15…6a`; `generate.py` refuses to start if they differ. Judge: gpt-4.1 T=0, seed 0, max_tokens 60; the local Qwen3-14B judge is NF4, thinking disabled, greedy.

**Hardware / runtime.** One RTX 4090 24 GB. Generation wall time from `logs/generation_stats.jsonl` (two processes concurrently, peak VRAM 8.7–11.1 GB each): gams_orig 1954 s, gams_edit 366 s, gemma_orig 2541 s, gemma_edit 2814 s, community_ref 581 s + 1928 s (two halves). README estimates ~2.5 GPU-hours for smoke+generate. Runtimes of judging, guard, R_seq and analysis stages were not summarised (see `logs/*.out`). API spend $1.07 (`results/cost_log.jsonl`).

**Reproducibility caveat.** B3 batching certification failed as designed (`protocol_runtime.json`), so greedy outputs are reproducible only under the same frozen bucket schedule (`schedule_sha` in `logs/generation_stats.jsonl`), same GPU stack and NF4; bitwise identity on other hardware/library versions is not guaranteed. The gpt-4.1 labels cannot be regenerated exactly without API access; the shipped `results/judge/*.jsonl` and `results/judge_local/*.jsonl` let all statistics be recomputed without any model or API call:
`$PY analyze.py …; $PY audit.py …; $PY verify_headlines.py`.

## 5. Outputs and expected numbers

Per-example: `results/gen/*.jsonl`, `results/autoscore/`, `results/judge/` (716 items), `results/judge_local/` (4,800), `results/guard/`. Statistics: `results/analysis.json` (primary), `results/analysis_gpt41_subset.json`, `results/headline_table.csv`, `results/audit.json` (127/127 checks, 0 mismatches), `results/verify_headlines.json` (173/173), `results/judge_validation.json`, `results/rseq/rseq_validity.json`, `results/executor_audit.json`, `results/human_packet/` (native review PENDING). Figures: `figures/fig1_outcome_classes`, `fig2_forest_orig_to_edit`, `fig3_s5x_paired_gap`, `fig4_s6_over_refusal` (.pdf/.png). Packaged output: `method_out.json`, `full_method_out.json`. Which paper section uses each is not recorded in the workspace; the README maps numbers to its "Results actually obtained" items 1–6.

Expected (S5 n=280 per language; `results/headline_table.csv`, README):
- Refusal orig→edit: GaMS3 EN .986→.014, SL .871→.000; Gemma-3 EN .971→.287, SL .939→.739; community ref EN .054, SL .114. Invalid rate 0.000 in every cell.
- Official-guard ASR of edits: GaMS3 .982 EN / .972 SL; Gemma-3 .738 EN / .103 SL.
- S6 over-refusal: GaMS3 .100→.000 EN; Gemma-3 SL .327→.193.
- S5X (100 pairs) residual SL−EN refusal gap: Gemma-3 edit +.69 [.60,.78], McNemar p=3.4e-21; GaMS3 edit −.02 [−.05,.00]; community +.12 [.05,.20]; DiD Gemma-3 +.66 [.55,.76] vs GaMS3 +.01 [−.03,.05].
- Keyword proxy vs judge, Gemma-3 edit EN: .851 vs .255 (false-positive share .761, κ −.04).
- Substitute vs gpt-4.1 on the 716 shared items: κ .83 (6-way), .91 (refused vs not). R_seq pooled Spearman GaMS3 .86/.84, Gemma-3 .63/.48.

Not run / limits: Gemini second judge and gpt-4o-mini adjudicator (budget), native human review (pending), Slovenian LLM Eval / English utility benchmarks and activation-level mechanistic analyses are not part of this artifact's files.
