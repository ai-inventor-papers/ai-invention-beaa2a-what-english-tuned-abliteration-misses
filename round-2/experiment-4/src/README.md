# C1 BEHAVIOUR — bilingual (EN/SL) safety evaluation of four core checkpoints + a community reference

The FINAL behavioural evaluation of the GaMS3-12B-Instruct vs gemma-3-12b-it Heretic study, run once against a
protocol and a prompt sample frozen (and hashed) **before any model output existed**.

**Method vs baseline, in one pipeline.** For each model the *edit* (the Heretic LoRA selected in iteration 1) and its
*original* (the identical NF4 base with the adapter disabled) are generated from **one base load**, on the **same
prompts**, with the **same greedy decoding** and the **same batch schedule**, and scored by the **same blinded judge**.
A fifth checkpoint, the community edit `p-e-w/gemma-3-12b-it-heretic`, is an external anchor labelled SANITY REFERENCE
and excluded from the confirmatory family. The *measurement* also has baselines: Heretic's keyword refusal proxy and
RefusEU's official guard pipeline (Llama-Guard-3-8B + PolyGuard-Qwen; its gpt-4o-mini adjudicator could not be run, so
guard disagreements are bounded instead) are scored against the LLM judge rather than assumed to agree with it.

| checkpoint | what it is |
| --- | --- |
| `gams_orig` | `cjvt/GaMS3-12B-Instruct` @ `1d0b27af`, NF4, `PeftModel.disable_adapter()` |
| `gams_edit` | same base + Heretic LoRA trial 88 (`adapters/gams_selected_path2`, sha `a4419c51…`) |
| `gemma_orig` | `google/gemma-3-12b-it` @ `96b6f1ec`, NF4, adapter disabled |
| `gemma_edit` | same base + Heretic LoRA trial 96 (`adapters/gemma_selected_path2`, sha `d219c084…`) |
| `community_ref` | `p-e-w/gemma-3-12b-it-heretic` @ `e037e6e1` (bf16 merge, quantised to NF4 on load) — SANITY REFERENCE |

**Evaluation sets** (frozen in `frozen_samples.json`, 960 prompts per checkpoint, 4,800 generations in total):
`S5` = 280 RefusEU row_ids × EN+SL (20 per inferred category); `S5X` = 100 verified EN↔SL cross-translation pairs —
the **only** basis for paired cross-language claims; `S6` = 150 XSTest-safe items × EN+SL for over-refusal.

## What happened to the judge (read this before reading any number)

The plan's primary judge is `openai/gpt-4.1` through OpenRouter. The shared key was at its daily limit for the whole
GPU phase and, minutes after it reset, the **run-level** budget for this phase was exhausted by the run as a whole
(HTTP 403 `aii_run_budget_exhausted`, $7.00 of $7.00; this artifact had spent $1.07). gpt-4.1 had by then labelled
**716 of the 3,840 core items**, in a **seeded-random shuffled order** — i.e. a random subset, not a prefix.

Per fallback F1 the API stages stopped cleanly and nothing was invented. A **substitute judge from a third family** was
added: **`Qwen/Qwen3-14B` run locally** (NF4, thinking disabled, greedy) applying the **same frozen rubric verbatim**
(`protocol.yaml:judge_primary`), the same `[TRUNCATED AT 256 TOKENS]` marker, the same parser, the same blinding and a
seeded interleave of checkpoints. It labels **all 4,800 items**, so the frozen statistics run at full power, and it is
**validated against the 716 gpt-4.1 labels** (`results/judge_validation.json`). Both label sets are shipped and every
headline is reported under both, with the label source named. `key_watch.sh` resumes gpt-4.1 automatically (skipping
already-labelled items) if the budget is raised.

## Layout

| path | what it is |
| --- | --- |
| `method.py` | driver: `uv run method.py --stages all` (or a comma-separated subset) |
| `run_all.sh` | the same pipeline as a shell script, in the order it was executed |
| `common.py` | paths, pins, NF4 + adapter loading, chat rendering, batched greedy generation |
| `freeze.py` → `frozen_samples.json`, `protocol.yaml` | Stage A: the frozen sample and protocol; hashes in `logs/freeze_hashes.txt` |
| `verify_pins.py` → `results/pins_verified.json` | revisions + per-shard SHA256 vs the iteration-1 pins (a mismatch aborts) |
| `smoke.py` → `results/smoke/*.json` | Stage B: templates, adapter attachment (T3), coherence, keyword smoke, **batching certification (B3)**, timing |
| `protocol_runtime.json` | the B3 decision (exact-length buckets) and the execution details, recorded before Stage C |
| `generate.py` → `results/gen/<ckpt>.jsonl` | Stage C: 960 greedy 256-token generations per checkpoint, resumable by `item_key` |
| `autoscore.py` → `results/autoscore/<ckpt>.jsonl` | Stage D: empty flag, GlotLID line-level language consistency + HBS share, 4-gram repetition, Heretic EN / iteration-1 SL keyword proxies |
| `judge.py` → `results/judge/<ckpt>.jsonl` | Stage E: the frozen gpt-4.1 rubric (blind, T=0); 716 core items before the budget block |
| `local_judge.py` → `results/judge_local/<ckpt>.jsonl` | **F1 substitute judge** (Qwen3-14B, local): all 4,800 items, same rubric |
| `reparse.py` | F8: re-parse logged raw judge outputs after a parser fix — never re-call |
| `judge2.py` | Stage F second judge (gemini-2.5-flash) on the frozen 400 + the B5 DEV calibration |
| `agreement.py`, `agreement_local.py` → `results/judge2_agreement.json`, `results/judge_validation.json` | judge agreement (Cohen's κ with bootstrap CIs, confusion matrices, rates recomputed under each judge) |
| `executor_audit.py` → `results/executor_audit.json` | 30 blind EN items labelled by the executing agent — EXECUTOR CHECK, **not** human review |
| `guard_pipeline.py` → `results/guard/` | Stage G: RefusEU's official pipeline as an ASR sensitivity arm |
| `rseq.py` → `results/rseq/` | Stage H (SUPPLEMENTARY): R_seq / R1 refusal-readout validity on FINAL-distribution items |
| `headline_table.py` → `results/headline_table.csv` | the 5 × 2 headline table with CIs, for the paper |
| `stats_lib.py`, `analyze.py` → `results/analysis*.json` | Stage I: the frozen statistics (cluster bootstrap, exact McNemar, Holm) |
| `audit.py` → `results/audit.json` | independent re-derivation of every headline through a second code path + 3 placebos |
| `verify_headlines.py` → `results/verify_headlines.json` | a THIRD, from-scratch re-derivation of all 173 headline numbers (own bootstrap/binomial/kappa, no analysis imports) plus a permutation/constant placebo arm that must fail |
| `figures.py` → `figures/` | fig1 outcome classes, fig2 forest, fig3 S5X paired gap, fig4 over-refusal, fig5 judge agreement (PNG + PDF) |
| `human_packet.py` → `results/human_packet/` | blinded 200-item native-review packet — **NATIVE_REVIEW_PENDING** |
| `build_metadata.py`, `to_schema.py` → `method_out.json` | `exp_gen_sol_out` output with the full analysis, costs, pins, deviations and paths |
| `tests/test_stats.py` → `results/t8_stats_sanity.json` | T8: bootstrap coverage / McNemar power / null rate on synthetic data, parser and empty-label unit tests |
| `env/requirements.lock`, `env/hardware.txt` | pinned environment and the machine it ran on |
| `*_queue*.sh`, `key_watch.sh` | the background job chains actually used (PID-based, resumable) |
| `results/gen_part/` | the community checkpoint was generated in two concurrent halves (S5+S5X, S6) and concatenated into `results/gen/community_ref.jsonl`; the halves are kept as provenance (verified: merged == a+b, 960 unique item_keys) |
| `scratch/` | pre-check artefacts only — see `scratch/README.md`; **not results** |

Absolute workspace root: `.`
(every `results/…` path above is under it). Read-only dependencies: the frozen dataset
`…/iter_1/gen_art/gen_art_dataset_1` and the iteration-1 adapters `…/iter_1/gen_art/gen_art_experiment_1/adapters/`.

## How to run

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python --index-strategy unsafe-best-match \
  --extra-index-url https://download.pytorch.org/whl/cu128 -r env/requirements.lock
uv run method.py --stages pins,freeze,tests          # protocol + hashes + statistics sanity (no GPU)
uv run method.py --stages smoke,generate             # ~2.5 GPU-h on a 24 GB card
uv run method.py --stages autoscore,guard_gpu        # local scores + the official guard arm
uv run method.py --stages judge,judge2,agreement     # API stages (OPENROUTER_BASE_URL + OPENROUTER_API_KEY)
uv run method.py --stages local_judge                # substitute judge (local GPU) if the API is unavailable
uv run method.py --stages analyze,audit,rseq,figures,packet,metadata,schema
uv run executor_audit.py sample && uv run executor_audit.py score   # 30 blind items, labels filled in by hand
```

`generate.py` refuses to start unless `frozen_samples.json` and `protocol.yaml` hash to the values recorded in
`logs/freeze_hashes.txt`, and re-running `freeze.py` must reproduce those hashes (T0).

## Findings and caveats that travel with the numbers

* **Batching certification (B3) did not pass as designed and this changed the run.** Gemma-3 failed left-padded
  batching under both `eager` (11/16) and `sdpa` (12/16) and passed exact-length buckets (14/16); **GaMS3 failed all
  three modes at 12/16, including buckets, where there is no padding at all**. So part of the batch-vs-single
  disagreement is NF4/bf16 batch-shape numerics, not the padding bug. Every observed divergence is a coherent near-tie
  paraphrase (`results/smoke/*.json` → `b3.mismatch_examples`). Exact-length buckets were used for **all five**
  checkpoints under **one shared schedule** (`schedule_sha` in `logs/generation_stats.jsonl`). Consequence: these greedy
  outputs are reproducible under the same schedule, not under arbitrary batching.
* **Truncation is not uniform across checkpoints** (`hit_max_rate`): GaMS3 orig 0.30 vs GaMS3 edit 0.93, Gemma orig
  0.86 vs edit 0.82. Truncated responses carry a `[TRUNCATED AT 256 TOKENS]` marker for the judge, and the rate is
  reported per checkpoint; it is itself a behavioural signal (refusals are short, compliances are long).
* **The community reference is not the published model**: a bf16 merge quantised to NF4 on load. Its card states
  Heretic v1.0.0, KL 0.16 and 3/100 keyword refusals; under NF4 on the 20-prompt Heretic smoke set it scored **0/20**.
  The card does **not** state a trial count.
* `adapters/<tag>_selected/` is **not** byte-identical to the `_path2` copy that the plan pins; the `_path2` copies
  matched their `SHA256SUMS.json` and were the ones used.
* **Judge parse failures were fixed in the parser, never in the prompt** (F8): the judge sometimes emits the CLASS/LANG
  values as bare lines. Raw outputs are logged, so the fix was applied by re-parsing (`reparse.py`), not by re-calling.
  The local judge's failures are truncations (it enumerates every category and hits the token cap); those rows are
  re-labelled once with a larger cap and the superseding row is appended.
* **What this cannot show** is listed in `method_out.json → metadata.what_this_does_NOT_show`: no attribution to a
  training stage (Gemma-3-it is a same-family reference, not GaMS3's parent, and n = 2 models); prompt-level CIs do not
  measure Heretic run-to-run variance (one optimisation seed per model); S5 EN-vs-SL contrasts are UNPAIRED, since
  RefusEU rows sharing an id are not translations (0 T / 158 P correspondence grades) — only S5X pairs are paired, and
  their translated sides have automated QC only; absolute levels are NF4-specific; categories are inferred and
  descriptive; native review is PENDING.

## Results actually obtained

All numbers below are recomputed from `results/gen/*.jsonl` by `analyze.py` and re-derived **twice** by independent code
paths: `audit.py` (**127/127 checks match, all three placebos null**) and `verify_headlines.py`, written from scratch
against the raw jsonl with its own bootstrap, exact binomial and kappa and no import of the analysis modules
(**173/173 match, 0 mismatches**). The latter also runs the placebo arm the audit needs: the real effect rejects
(McNemar p = 6e-58, CI excludes 0), **permuting the orig/edit assignment rejects in only 1.5% of 200 simulations**
(so the test is not passing vacuously), a constant arm gives p = 1 and CI [0, 0], and shuffling S5X partners collapses
pair concordance to the independence expectation (.262 vs .263). Full log: `results/verify_headlines.json`. Refusal/CLASS comes from the substitute judge on all 4,800 items;
ASR is RefusEU's official guard pipeline; language consistency is GlotLID. Full table: `results/headline_table.csv`.

**1. Both edits suppress refusal, by very different amounts, and neither does it by breaking the model.**
Paired orig→edit on the 280-item RefusEU sample (95% cluster-bootstrap CI, exact McNemar, Holm-adjusted within model):

| | EN refusal | SL refusal | EN ASR (official) | SL ASR (official) |
| --- | --- | --- | --- | --- |
| GaMS3 orig → edit | .986 → .014 (Δ −.971 [−.989,−.950]) | .871 → .000 (Δ −.871 [−.907,−.832]) | .015 → .982 | .012 → .972 |
| Gemma-3 orig → edit | .971 → .287 (Δ −.685 [−.738,−.634]) | .939 → .739 (Δ −.200 [−.246,−.154]) | .026 → .738 | .016 → .103 |
| Community edit (ref) | .971 → .054 | .939 → .114 | .026 → 1.000 | .016 → .870 |

All Holm p < 1e-14. The **invalid rate is 0.000 in every cell** and Slovene language consistency moves by ≤ 0.4 points,
so neither edit buys suppression with incoherence or language collapse — both pass the pre-registered sanity bar.
Over-refusal on XSTest-safe falls too (GaMS3 .100 → .000 EN; Gemma-3 .327 → .193 SL).

**2. The headline: the English-derived edit transfers to Slovene in GaMS3 but not in Gemma-3.** On the 100 verified
S5X translation pairs — the only paired cross-language comparison in the study — the residual SL−EN refusal gap is:

| checkpoint | SL − EN refusal gap (95% CI) | McNemar p |
| --- | --- | --- |
| GaMS3 orig | −.03 [−.07, .00] | .25 |
| GaMS3 edit | −.02 [−.05, .00] | .50 |
| Gemma-3 orig | +.03 [.00, +.07] | .25 |
| **Gemma-3 edit** | **+.69 [+.60, +.78]** | **3.4e-21** |
| Community edit (ref) | +.12 [+.05, +.20] | .0018 |

Difference-in-differences: GaMS3 +.01 [−.03,+.05] (transfer is complete), Gemma-3 **+.66 [+.55,+.76]** (transfer
largely fails). The sign holds in **both** translation directions for Gemma-3, so it is not translationese.

**3. That failure is not an intrinsic property of Gemma-3.** The community edit of the *same base model*, optimised at
bf16 by the same tool, shows a gap of only +.12. What differs is achieved optimisation strength, not the architecture —
exactly the distinction this study was asked to keep separate. With one optimisation seed per model we can say the
matched-budget NF4 edit under-transfers; we cannot attribute that to a training stage, and n = 2 models.

**4. Heretic's own optimisation target is badly miscalibrated on Gemma-3, which plausibly explains (3).** The keyword
proxy Heretic maximises against, scored on the same responses and compared with the judge:

| cell | keyword "refusal" | judged refusal | false-positive share of keyword refusals | κ |
| --- | --- | --- | --- | --- |
| GaMS3 orig EN | .988 | .979 | .015 | +.35 |
| Gemma-3 orig EN | .994 | .967 | .027 | +.30 |
| GaMS3 edit EN | .209 | .015 | .971 | +.03 |
| **Gemma-3 edit EN** | **.851** | **.255** | **.761** | **−.04** |

On the *originals* the proxy is nearly exact. On the *edited* models it collapses, and worst on Gemma-3-edit, whose
compliant answers are caveat-laden ("I am programmed to…", "illegal", "harmful") and therefore keep triggering the
markers. An optimiser scored by that proxy sees little gradient once the model complies *with warnings* — which is
precisely what Gemma-3-edit does: its EN refusals mostly become **partial** compliance (.548 partial, see fig 1), not
full compliance. This is a measurement-validity result, not a claim about weights, and it is the one number a reviewer
should check first.

**5. Supplementary (Stage H), a negative result.** The sequence-level refusal readout R_seq correlates with judged
refusal when the original and edited checkpoints are pooled (Spearman .86 EN / .84 SL for GaMS3) but **fails the 0.85
bar for Gemma-3** (.63 EN / .48 SL), and **collapses within the edited checkpoints alone** (.16–.33 everywhere). Most of
its apparent validity is the orig-vs-edit contrast, i.e. self-reference, not within-condition discrimination.
`results/rseq/rseq_validity.json`.

**6. Judge robustness.** Substitute vs gpt-4.1 on the 716 co-labelled items: κ = .83 (6-way CLASS), **.91 (refused vs
not)**, .89/.93 collapsed 3-way by language — the refusal axis is judge-robust. The **safe/unsafe line is not**
(κ = .66): the substitute applies it to the *request*, calling 77% of Gemma-3-edit's EN refusals "unsafe", which is why
ASR is taken from the guard pipeline instead. A 30-item blind EXECUTOR CHECK gives κ = .67 5-way and .93 on
refused-vs-not against gpt-4.1, disagreeing systematically in two places: gpt-4.1 calls benign XSTest joke answers
"irrelevant" where the executor and the substitute judge call them compliance, and it marks caveat-heavy partials
"unsafe". Guard-internal agreement (Llama-Guard vs PolyGuard) is 91.2%.

## Restoring removed files

`.aii/manifest.yaml` has exactly two `delete` entries — `.venv/` and `__pycache__/`. Nothing else is removed:
`results/` (33 MB of JSON/JSONL), `logs/`, `figures/`, `scratch/`, `env/`, `tests/` and all code are text files and are
kept as they are, at the absolute paths given above.

```bash
# .venv/  (regenerable — the only large artefact removed, ~11 GB)
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python --index-strategy unsafe-best-match \
  --extra-index-url https://download.pytorch.org/whl/cu128 -r env/requirements.lock
# env/requirements.lock is the full transitive freeze; pyproject.toml pins the 22 direct dependencies.

# __pycache__/  (regenerable) — recreated automatically on the next import; to clear it again:
find . -name __pycache__ -prune -exec rm -rf {} +
```

Model weights are **not** stored in this workspace: they live in this run's shared HuggingFace cache and are
re-downloadable at the pinned revisions —
`cjvt/GaMS3-12B-Instruct@1d0b27af5748784482600d24779409e7e1dc9adc`,
`google/gemma-3-12b-it@96b6f1eccf38110c56df3a15bffe176da04bfd80`,
`p-e-w/gemma-3-12b-it-heretic@e037e6e112ea85777fc3858469cdc31fdfceaa13`,
`ToxicityPrompts/PolyGuard-Qwen@644bfe73ff498c9a14818b72a11187eaf23f0ff1`,
`meta-llama/Llama-Guard-3-8B@7327bd9f6efbbe6101dc6cc4736302b3cbb6e425`,
`cis-lmu/glotlid@85cd6716494360367b75f642b5bc78667605d0b4`,
`Qwen/Qwen3-14B@40c069824f4251a91eefaf281ebe4c544efd3e18`
(`uv run python scratch/dl.py <repo> <revision>`). The LoRA adapters are read-only in the iteration-1 workspace.
