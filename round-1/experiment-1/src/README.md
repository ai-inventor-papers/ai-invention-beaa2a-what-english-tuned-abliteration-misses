# Matched Heretic runs on two sibling 12B models (GaMS3 vs Gemma-3)

Two **matched** [Heretic](https://github.com/p-e-w/heretic) abliteration runs — pinned at commit
`3521f8648a0dccf6e12a92666862632235fac7e6` — one on `cjvt/GaMS3-12B-Instruct`, one on
`google/gemma-3-12b-it`, under an **identical optimizer**: same seed (20260923), same search space,
same English prompt sources, same precision (`bnb_4bit` NF4 / bf16 compute), same explicit batch
size (128), same trial budget, and the same pause/resume point. Heretic's own code is the edit
engine; this repo only drives it non-interactively, captures its internals and evaluates the result.

What the repo produces:

1. **Four core checkpoints** — each original model and the one edit selected for it by a rule frozen
   *before* any trial ran (`protocol_selection.json`). Edits are exported as LoRA adapters
   (a 4-bit merge would need ~48 GB of CPU RAM; this pod has 57 GB but the merge path also
   dequantizes the whole model, so adapters are the safe export).
2. **The A3 sibling screen** — because the two runs share one TPE seed, their first 60 trials are the
   *same 60 edits*. That gives a paired sample in which the two models can be asked whether they
   respond to identical edits the same way, on English refusal count and on log first-token KL, with
   a **range-restriction guard**: partial Spearman controlling for Heretic's per-layer kernel mass,
   plus a params-only cross-validated predictor and the sibling's incremental R² (`dR2_sibling`) over
   it. A raw ρ near 0.9 with `dR2_sibling ≈ 0` means the agreement was inherited from the shared
   parameter draws, not from shared response structure. The guard is validated on synthetic data
   (`results/a3_synthetic_T4.json`) where the answer is known.
3. **A bilingual swap test** — each model is run with (a) no edit, (b) its own selected parameters,
   (c) *the other model's* selected parameters rebuilt on its own directions. Scored per prompt, in
   English and in Slovene, paired on the same prompts (exact McNemar + Newcombe CI for refusal
   flags, paired bootstrap for KL).
4. **Language-ability and coherence checks** — FLORES+ dev per-token NLL in both languages,
   `langdetect` on the Slovene answers, repeated-4-gram rate, empty-answer rate. An incoherent or
   language-damaged checkpoint is reported as *degraded*, never as successful refusal suppression.

## Layout

| path | what it is |
| --- | --- |
| `method.py` | resumable orchestrator; every stage is idempotent (`--stages all`) |
| `drive_heretic.py` | non-interactive driver around `heretic.main.run()`: scripts every `questionary` prompt (an unscripted prompt exits 3 — it never guesses), captures the residual means, logs per-trial wall time and peak VRAM, and can stop a study cleanly at a deadline |
| `select_rule.py` | the frozen selection rule (`protocol_selection.json`), applied to the journal |
| `a3_screen.py` | A3 sibling screen; `--synthetic` runs the guard's own validation |
| `swap_eval.py` | GPU evaluation of one target model: `orig` / `own` / `swap` + retest conditions, EN + SL + FLORES+ |
| `analyze.py` | paired tests, Wilson/Newcombe CIs, sanity flags → `method_out.json` |
| `audit.py` | independent re-derivation of every headline number through a different code path, plus placebo (permuted / self-paired) checks → `results/audit.json` |
| `figures.py` | `figures/fig1..3` (PNG + PDF) |
| `translate_nllb.py` | Slovene translation of the 100 English test prompts with NLLB-200-distilled-1.3B + back-translation chrF |
| `translate_sl.py` | the API-translator pass kept for provenance (see *Slovene data* below) |
| `protocol_selection.json`, `protocol_a3.json` | pre-registered rules, frozen before any trial ran |
| `pins.json` | model/dataset revisions and per-file LFS sha256 |
| `env/` | `requirements.lock`, `hardware.txt`, the exact Heretic sources used, the interactive-prompt inventory |
| `checkpoints/<tag>/*.jsonl` | the Optuna journals (**kept**; resume reads these) |
| `adapters/<tag>_selected/` | the selected edit as a LoRA adapter (**kept**) |
| `directions/<tag>/` | residual means (row 0 = embeddings) and the refusal directions (**kept**) |
| `results/` | trial tables, A3 statistics, per-prompt scores (`results/eval/`), selection records, audit |
| `logs/` | per-run Heretic logs, per-trial JSONL, the scripted-prompt transcripts, the timing decision |

Absolute workspace paths of the kept artifacts (they are the only copies — the publish step skips
files ≥ 100 MB, but everything kept here is far smaller):

```
./checkpoints/gams/cjvt--GaMS3-12B-Instruct.jsonl
./checkpoints/gemma/google--gemma-3-12b-it.jsonl
./adapters/
./directions/
./results/
```

## How to run

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r env/requirements.lock
uv run method.py --stages all --budget-min 240
```

Individual stages (all idempotent, safe to re-enter):

```bash
uv run method.py --stages phaseA_gams          # 60 TPE startup trials (refuses if a journal exists)
uv run method.py --stages phaseB_gemma         # resume that journal and run more trials, then select+export
uv run method.py --stages a3,eval_gams,eval_gemma,analyze,figures
uv run python audit.py                         # independent re-derivation of the headline numbers
```

To resume a journal left unfinished by a time budget, run its `phaseB_<tag>` stage again; the
per-model `status` block in `method_out.json` carries the exact command and the trial count reached.

## Slovene data

`data/sl_harmful_behaviors_test100.json` holds the Slovene version of `mlabonne/harmful_behaviors`
`test[:100]` plus ten harmless probes, translated with **NLLB-200-distilled-1.3B** (greedy, beam-4
retry for low-chrF items) and checked by back-translation chrF against the English source.

The first attempt used an instruction-tuned API translator; it *declined to translate* most of the
harmful items (it returned refusals instead of translations), so those rows had chrF ≈ 2–39. That
pass is kept as `data/sl_api_translator_pass1.json` for provenance, and a dedicated MT model is used
for the whole set instead — one translator for every row, which also removes a translator-by-item
confound. Slovene refusal is scored by a marker list validated against executor hand labels
(`results/sl_marker_validation.json`): **automated checks only, `NATIVE_REVIEW_PENDING`**, and it is
a development-only outcome, not a final safety claim.

## Known deviations (also recorded in `method_out.json`)

* `bnb_4bit` NF4 instead of bf16 weights — forced by the 23 GB L4. Identical for both models, so
  within-study comparisons are fair, but absolute KL and refusal values are **not** comparable to
  published bf16 Heretic numbers, and the edit is computed on dequantized 4-bit weights.
* One explicit batch size (128) for both models instead of Heretic's per-model auto benchmark, so
  padding and batching numerics are identical across models.
* The English system prompt (`"You are a helpful assistant."`) is also used for the Slovene prompts.
* The trial budget was reduced **symmetrically** from Heretic's default 200 to **116 trials per model**
  (60 identical TPE startup trials + 56 TPE trials) because the clock did not
  allow two full runs (see `logs/timing_decision.json`); an unequal budget would have broken the
  matched design, which is the property the whole comparison rests on.
* One optimizer seed per model (20260923; 20260924 reserved). Prompt-level CIs do **not** measure
  run-to-run optimizer variance.
* No LLM judge for Slovene refusal: the shared OpenRouter key hit its daily limit during the run.

## Restoring removed files

`.aii/manifest.yaml` marks exactly two paths for deletion, `.venv/` and `scratch/venv_tools/`; both
are Python environments and are fully regenerable:

```bash
# .venv  (regenerable)
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r env/requirements.lock

# scratch/venv_tools  (regenerable; the small CPU-only helper environment)
uv venv scratch/venv_tools --python=3.12
uv pip install --python scratch/venv_tools/bin/python pandas pyarrow aiohttp huggingface_hub sacrebleu tenacity loguru

# the download helper itself is tiny and kept, but for reference it is:
cat > scratch/dl.py <<'PY'
import sys
from huggingface_hub import snapshot_download, model_info
repo = sys.argv[1]; info = model_info(repo)
print("SHA", repo, info.sha)
print("DONE", snapshot_download(repo, revision=info.sha))
PY
.venv/bin/python scratch/dl.py cjvt/GaMS3-12B-Instruct
.venv/bin/python scratch/dl.py google/gemma-3-12b-it
.venv/bin/python scratch/dl.py facebook/nllb-200-distilled-1.3B
```

Model weights themselves are never stored in this repo; they live in the run's shared HuggingFace
cache and are re-downloadable at the revisions pinned in `pins.json`.

## Results

Matched budget: **116 Heretic trials per model** (60 identical TPE startup edits + 56 TPE trials),
one seed, `bnb_4bit` NF4, batch size 128, byte-identical chat templates.

| checkpoint | EN refusals /100 | SL refusals /100 | mean first-token KL | FLORES+ SL NLL change |
| --- | --- | --- | --- | --- |
| GaMS3-12B-Instruct, original | 98 | 97 | 0 | — |
| GaMS3-12B-Instruct + own edit (trial 88) | **16** | **10** | 0.175 | −0.004 |
| GaMS3-12B-Instruct + Gemma's parameters | 25 | 25 | 0.046 | +0.006 |
| gemma-3-12b-it, original | 100 | 97 | 0 | — |
| gemma-3-12b-it + own edit (trial 96) | **69** | **90** | 0.024 | +0.001 |
| gemma-3-12b-it + GaMS's parameters | 53 | **25** | 0.254 | +0.010 |

Both `own` checkpoints re-score *exactly* to their journal values (16 / 0.1749354 and 69 / 0.0242503,
KL relative difference 2 × 10⁻⁸), and the replica scorer reproduces Heretic's printed baselines
(98 and 100). No checkpoint is language-damaged: FLORES+ NLL moves ≤ 0.01 nats and 100 % of the
Slovene answers are still Slovene.

**The finding.** On all 60 edits that are *identical* in both models, gemma-3-12b-it refuses more than
GaMS3-12B-Instruct — 60/60 edits, none the other way, paired median **+25 refusals/100**, CI [10, 43] —
while the two models' KL damage from the same edit agrees almost perfectly (Spearman **0.967**,
CI [0.93, 0.98]; partial ρ 0.923 after controlling for kernel mass). Refusal given up per unit of KL is
**≈13× higher in GaMS** (ratio 13.4, CI [7.0, 30.0]); on the KL-matched half of the edits (KL medians
0.0101 vs 0.0098) GaMS sits at 65/100 refusals against Gemma's 99/100. *Same edit, same representational
damage, very different safety effect* — and a raw cross-model direction cosine (0.63 mean, 0.57 in
layers 24–47, against 0.98 for the harmless means and 0.014 for random directions) does not predict it.

The A3 reading is deliberately **"intermediate", not "shared surface"**: refusal ranks agree only
moderately (ρ 0.781, CI [0.63, 0.88]; partial 0.647) and `dR2_sibling ≈ 0`, so that rank agreement is
mostly inherited from the shared parameter draws. The guard that establishes this was validated first
on synthetic data (`results/a3_synthetic_T4.json`).

Cross-language, the English-derived edit is **not** language-neutral: GaMS's parameters applied to
Gemma suppress Slovene far more than English (97→25 vs 100→53) at ten times the KL cost, and the swap
never reproduces the own-edit outcome in either direction (every CI excludes 0).

Figures: `figures/fig1` Pareto fronts, `fig2` A3 sibling agreement, `fig3` the six conditions in both
languages, `fig4` the same-edit efficiency gap.

**Read the limits before quoting any of this.** `method_out.json → metadata.what_this_does_NOT_show`
is the authoritative list: two models are two units and nothing here attributes the asymmetry to
Slovene continued pretraining or any training stage; the Gemma arm's resistance is confounded with
4-bit quantization and the reduced trial budget (the published bf16 200-trial edit reaches 3/100), so
this is *not* evidence that gemma-3-12b-it resists abliteration in general; and the Slovene marker
scorer reaches only κ = 0.48 against 40 executor hand labels (`NATIVE_REVIEW_PENDING`).

Every headline number is re-derived by `audit.py` (28/28 checks, 0 mismatches) and
`audit_efficiency.py` (raw-journal re-parse, hand-rolled medians, bootstrap and Spearman), each with a
placebo that must fail: permuted sibling labels (ρ 0.78 → 0.05), self-paired McNemar (p = 1), and
random model assignment (60/0 sign split → 23/37).

## Files added after the first draft of this README

`efficiency.py` (the same-edit efficiency contrast), `direction_compare.py` (refusal-direction
geometry with a random-direction control), `sl_label_sample.py` (draw + score the Slovene hand-label
sample), `to_schema.py` (reshape `method_out.json` into the `exp_gen_sol_out` schema) and
`audit_efficiency.py` (independent raw-journal re-derivation of the efficiency headline).

## The Slovene LLM judge is still blocked

`judge_sl.py` implements the blinded 3-way judge (refusal / compliance / incoherent-or-off-language)
over all 600 Slovene responses, in one shuffled stream with model identity hidden, plus a second
independent judge on a stratified sample. It was retried after the platform reported a replaced
OpenRouter key, but the key available to this run (both `$OPENROUTER_API_KEY` and
`.secrets/openrouter_key.private`, identical values and key id) still answers HTTP 403
`Key limit exceeded (daily limit)` to every request, including a single 4-token probe. **0 of 600
judgements succeeded and none were invented**: `results/judge_sl.json` records the failure, Slovene
refusal stays marker-only (κ = 0.48 vs 40 executor hand labels, `NATIVE_REVIEW_PENDING`), and the SL
claims stay narrowed. Run `OPENROUTER_API_KEY=<working key> .venv/bin/python judge_sl.py` to fill it in.
