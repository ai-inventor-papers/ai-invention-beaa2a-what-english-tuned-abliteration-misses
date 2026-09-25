# Reproducibility

Everything below is what was **actually run**, in order, on one machine in one session
(2026-09-24, 08:03–13:00 UTC). Wall-clock figures are the measured ones.

## 0. Hardware and OS actually used

| | |
| --- | --- |
| OS | Ubuntu (Linux 6.8.0-138-generic), container with 32 CPUs / 124 GB RAM |
| GPU | 1× NVIDIA GeForce RTX 4090, 24 GB (driver 595.91.07, CUDA 13.2) — peak use 13.8 GB |
| Python | 3.12 (`uv venv --python=3.12`) |
| total wall clock | ≈ 4 h 50 min including coding; ≈ 3 h 10 min of GPU work |

A 24 GB card is required for the 12B target in NF4 *plus* the 14B judge (loaded sequentially, never
co-resident). Nothing here needs more than one GPU.

## 1. Copy the artifact and create the environment

```bash
cp -r gen_art_experiment_11 ~/c3 && cd ~/c3
uv venv .venv --python=3.12
# torch comes from the cu128 index; every other pin is on PyPI
uv pip install --python .venv/bin/python --index-strategy unsafe-best-match \
    --extra-index-url https://download.pytorch.org/whl/cu128 -r env/requirements.base.lock
# Heretic from the VENDORED pinned tree (not PyPI) - it carries the new scorer plugin
uv pip install --python .venv/bin/python --no-deps -e third_party/heretic
uv pip install --python .venv/bin/python fasttext-numpy2-wheel      # GlotLID under NumPy 2
```
`pyproject.toml` lists the same 172 pins that `uv pip freeze` reported at the end of the run
(`env/requirements.lock` is that freeze verbatim; `env/requirements.base.lock` is the iteration-1
lockfile actually passed to the installer, i.e. the same list minus the vendored Heretic line).
Install takes ≈ 15 min on this filesystem. No system packages beyond a CUDA-capable driver.

## 2. Models, data and credentials (names only)

Downloaded through `huggingface_hub` into the shared cache (`HF_HOME`/`HF_HUB_CACHE` are read from
the environment and must NOT be overridden):

```bash
huggingface-cli download google/gemma-3-12b-it        --revision 96b6f1eccf38110c56df3a15bffe176da04bfd80
huggingface-cli download Qwen/Qwen3-14B               --revision 40c069824f4251a91eefaf281ebe4c544efd3e18
huggingface-cli download ToxicityPrompts/PolyGuard-Qwen --revision 644bfe73ff498c9a14818b72a11187eaf23f0ff1
huggingface-cli download meta-llama/Llama-Guard-3-8B  --revision 7327bd9f6efbbe6101dc6cc4736302b3cbb6e425
huggingface-cli download cis-lmu/glotlid              --revision 85cd6716494360367b75f642b5bc78667605d0b4
# datasets pulled by Heretic itself: mlabonne/harmful_behaviors, mlabonne/harmless_alpaca
```
Gemma and Llama-Guard are gated: a HuggingFace token with accepted licences must be present in the
environment (`HF_TOKEN`). The optional gpt-4.1 judge stage reads `OPENROUTER_BASE_URL` and
`OPENROUTER_API_KEY`. **Values are never stored in this repo**, and in this run the API stage spent
**$0.00** — the first call returned HTTP 403 `aii_run_budget_exhausted`, so every label here is local
(`results/cost_log.jsonl` is empty; deviation D1).

Read-only inputs from earlier artifacts of the same run (paths are absolute in the scripts; copies of
the small ones are in `inputs/`): the frozen EN/SL data protocol `gen_art_dataset_1`, the iteration-1
Heretic study `gen_art_experiment_1` (Optuna journal, trials table, adapters, directions), and the
behavioural artifact `gen_art_experiment_4` (frozen samples, rubric, prior judge labels).

## 3. The exact commands, in the order they were run

| # | command | GPU | measured wall clock |
| --- | --- | --- | --- |
| 1 | `.venv/bin/python coverage.py` | no | 20 s |
| 2 | `.venv/bin/python build_pool.py` | no | 10 s |
| 3 | `.venv/bin/python train_clf.py base` | no | 2 min |
| 4 | `.venv/bin/python replay.py --tag tpe60_115 --skip-done --trials 96,60,61,…,115` | yes | 14 min (13.3 s/draw + 90 s load) |
| 5 | `.venv/bin/python inloop.py collect` → `judge_input --select cert` / `--tags tpe60_115` | no | 1 min |
| 6 | `.venv/bin/python judges.py local --inp results/judge_in/inloop_certset.jsonl --out results/judge_out/inloop_qwen.jsonl --bs 32` | yes | 10 min (0.24 s/item) |
| 7 | `.venv/bin/python inloop.py certify --bundle scorer/refusal_clf_base.joblib --out scorer/certification_base.json` | no | 30 s |
| 8 | `.venv/bin/python judges.py local --inp results/judge_in/inloop_replay_all.jsonl …` | yes | 15 min |
| 9 | `.venv/bin/python inloop.py refit_table …` + `train_clf.py refit --inloop …` | no | 2 min |
| 10 | `.venv/bin/python inloop.py certify --out scorer/certification.json` (the κ ≥ .80 gate) | no | 30 s |
| 11 | `.venv/bin/python tests/test_scorer.py` | no | 30 s |
| 12 | `bash chain3.sh` — the corrected Heretic run, phase A (60 seeded startup trials) then phase B to 116 | yes | 41 min (13.9 s/trial) |
| 13 | `.venv/bin/python inloop.py collect` + `analyze_inloop.py` | no | 2 min |
| 14 | `.venv/bin/python make_arms.py` then `freeze_predictions.py` | no | 10 s |
| 15 | `.venv/bin/python eval_gen.py --arms arms.json` | yes | 36 min (≈ 4.5 min per arm × 7 + FLORES) |
| 16 | `.venv/bin/python eval_judge_input.py` + `judges.py local --inp results/judge_in/eval_all.jsonl --out results/judge_out/eval_qwen.jsonl --bs 24` | yes | 17 min |
| 17 | `.venv/bin/python judges.py local --inp results/judge_in/inloop_corrected.jsonl …` (judge-grade reselection) | yes | 29 min |
| 18 | `analyze_inloop.py` → `make_arms.py` → `eval_gen.py` (adds the D2 arm) → judges again | yes | 12 min |
| 19 | `.venv/bin/python guard.py polyguard …` and `guard.py llamaguard …` | yes | 17 min |
| 20 | `.venv/bin/python autoscore.py`, `analyze_eval.py`, `verdicts.py` | no | 3 min |
| 21 | `.venv/bin/python kl_arms.py`, `selection_point_cert.py`, `guard_analysis.py`, `judge_ceiling.py` | mixed | 6 min |
| 22 | `bash chain7.sh` + `.venv/bin/python seed2.py` — the second optimiser seed (20260926) | yes | 35 min |
| 23 | `.venv/bin/python audit_headline.py`, `verify_numbers.py`, `figures.py`, `to_schema.py` | no | 3 min |

The same sequence is wrapped in `method.py`:

```bash
.venv/bin/python method.py --stages coverage,pool,clf_base,replay,judge_inloop,refit,certify,test_scorer
.venv/bin/python method.py --stages corrected,judge_corr,inloop_an,arms,evalgen,judge_eval,autoscore,eval_an
.venv/bin/python method.py --stages extras,seed2,audit,figures,schema
```

Every stage is **resumable**: generations are keyed by `item_key`, judge outputs by `key`, the Optuna
journals by trial. Re-running a completed stage is a no-op.

### Seeds and configuration

* Optuna/TPE seed **20260923** (corrected run and the iteration-1 run it is compared with); the
  replication run uses **20260926**. `n_startup_trials` 60, 116 complete trials, multivariate TPE.
* Heretic settings are **not** re-specified by hand: `replay.py` and `eval_gen.py` load the settings
  JSON stored inside the iteration-1 Optuna journal, so quantisation (`bnb_4bit`), batch size 128,
  `max_response_length` 100, `row_normalization="full"`, `orthogonalize_direction=true` and the
  response prefix are inherited byte-for-byte.
* Evaluation decoding: system prompt `"You are a helpful assistant."`, greedy, 256 new tokens,
  length-sorted left-padded batches of ≤ 32 shared by every arm, EOS `{<eos>, <end_of_turn>}`.
* Other frozen seeds: 20260924 (XSTest subsample), 20260923 (judge shuffle, bootstrap), 20260925
  (the gpt-4.1 sample that was never bought).

## 4. What a reader should get, and where it appears

| file | the numbers in it |
| --- | --- |
| `results/miscalibration_table.csv` | one row per iteration-1 draw: keyword / classifier / judged counts, KL, FP share → README §1, fig1 |
| `results/inloop_analysis.json` | `item_level_vs_qwen_all_edited_draws` (κ **+0.196** keyword, **+0.924** classifier, n = 11,600), `corrected_selection` (trial **7**, primary rule, 5/100, KL .2584), `reselection`, `first60_pareto` (8 vs 14), `tpe_phase_comparison` → README §1, §3 |
| `scorer/certification.json` / `…_base.json` | the gate: κ **.858** [.820,.888] refit vs **.729** base, keyword **.143** on the same 2,000 held-out in-loop responses → README §2 |
| `results/headline_table.csv` | per-arm S5X EN/SL refusal and partial, gap ± CI, McNemar p, S4hoc, XSTest, FLORES ΔNLL, harmless KL, official ASR → README §4 |
| `results/eval_analysis.json` | `s5x_gap` (B **+.68**, C **+.38**, F1.5 **+.33**), `dose_ladder` (P7: **−.05** [−.41,+.12]), `dose_ladder_kl_matched` (**−.38** [−.47,−.29]), DiD, S6, FLORES, validity |
| `results/seed2_analysis.json` | seed 20260926 selects trial 107, 5/100, A1 **65.1** — same rule branch as seed 1 |
| `results/frozen_predictions_with_verdicts.json` | P1 ✓(point) P2 ✗ P3 ✓ P4′ ✓ P5 ✓ P6 ✓ **P7 ✗** |
| `results/audit_headline.json` | **305/305** independent re-derivations match; 3/3 placebos fail as required |
| `results/verify_numbers.json` | **59/59** method_out.json ↔ analysis ↔ shipped-rows consistency |
| `figures/fig1…fig7` | miscalibration, Pareto, EN-vs-SL, coverage, outcome classes, forest, gap-vs-KL |
| `method_out.json` | 460 per-prompt rows × 8 arms + 232 Heretic draws, with all analyses in `metadata` |

Bit-exactness caveat: greedy NF4/bf16 decoding is **not** reproducible across GPU models (the same
trial re-scored 74 vs 69 keyword refusals between an L4 and this RTX 4090). On a different GPU the
counts will shift by a few per 100; the *contrasts* — κ .20 vs .92, the rule branch that fires, the
ordering of the arms — are what should reproduce. See `results/replay_fidelity.json`.

## 5. Pins (reference)

| thing | pin |
| --- | --- |
| target model | `google/gemma-3-12b-it` @ `96b6f1eccf38110c56df3a15bffe176da04bfd80`, bnb NF4 + bf16 compute |
| Heretic | `3521f8648a0dccf6e12a92666862632235fac7e6` (tree copied into `third_party/heretic/`, ONE file added) |
| optimiser | Optuna TPE, multivariate, `n_startup_trials` 60, seed 20260923 (second seed 20260926), 116 complete trials |
| judge | `Qwen/Qwen3-14B` @ `40c069824f4251a91eefaf281ebe4c544efd3e18`, NF4, thinking disabled, greedy, 40 new tokens (160 on one retry) |
| guards | `ToxicityPrompts/PolyGuard-Qwen` @ `644bfe73`, `meta-llama/Llama-Guard-3-8B` @ `7327bd9f`, bf16, greedy |
| language id | `cis-lmu/glotlid` @ `85cd6716` (`model.f.predict`, NumPy-2-safe low-level call) |
| data | frozen EN/SL protocol `art_qdUCJWbc5kHh` (`protocol_hash dc33bde4`); S5X pairs and XSTest ids from `art_m6pglf516e2r`'s `frozen_samples.json` |
| environment | `env/requirements.lock` (173 packages, `uv pip freeze`), `env/hardware.txt` |

## What is frozen, and when

`logs/freeze_hashes.txt` records, with UTC timestamps, the sha256 of: `protocol.yaml`, the corrected run's
`config.toml`, the new scorer plugin, `select_rule.py`, `results/eval_items.json`, the certified classifier bundle
and its certification, `arms.json` (v1 and v2), and `results/frozen_predictions.json`. Three amendments are logged
with their reason and their time, all **before** the generation they could have affected:
eval batching (08:57Z), dose ladder extended with f = 3.0 (09:32Z), adapter export (09:32Z), and the v2 arms file
(11:33Z, adding the judge-reselected arm that the protocol already provided for).

## Order of operations that matters

1. The classifier is trained and **refit** only on prior-round labels and on in-loop rows of **non-certification**
   trials; the 20 certification trials are held out from training, refit, model choice and threshold.
2. The classifier is frozen and hashed **before** the corrected Heretic run starts.
3. `results/frozen_predictions.json` is written and hashed **before** any file exists in `results/eval_gen/`
   (`freeze_predictions.py` refuses to run otherwise).
4. Verdicts are written to a **separate** file, and `verdicts.py` re-checks the frozen file's hash against the log.

## Known non-determinism

* Greedy NF4/bf16 decoding is **not** bit-reproducible across GPU models: the same trial re-scores 74 vs 69 keyword
  refusals between an L4 (iteration 1) and this RTX 4090. Everything compared here was measured on one GPU in one
  session; `results/replay_fidelity.json` quantifies the drift over 56 draws.
* `torch.svd_lowrank` inside Heretic's `row_normalization="full"` path is randomized; Heretic reseeds from
  `settings.seed` immediately before each call, so a replay of the same trial is stable within a GPU.
* The residual-mean capture of the corrected run differs from iteration 1's in the last decimals
  (per-layer cosine ≥ .99987, `results/direction_drift_corrected_vs_iter1.json`); arm C is built on its **own**
  capture, which is the one its parameters were optimised against.

## Re-running a single piece

```bash
.venv/bin/python replay.py --trials 96 --tag check --clf scorer/refusal_clf.joblib   # one draw, ~15 s + model load
.venv/bin/python inloop.py certify --out /tmp/cert.json                              # the kappa gate, no GPU
.venv/bin/python audit_headline.py                                                   # 305 checks + 3 placebos, no GPU
```
