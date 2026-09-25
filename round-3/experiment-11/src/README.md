# C3 — a partial-aware refusal objective for Heretic abliteration (gemma-3-12b-it, EN/SL)

**One-sentence result.** Heretic's 33-substring refusal counter is **near-blind on the edits it is optimising**
(κ = +.20 against a frozen LLM-judge rubric over all 11,600 in-loop generations of its own 116 candidate edits, vs
+.92 for a distilled partial-aware classifier), and replacing it — everything else held fixed (commit, seed, search
space, data, NF4, 116-trial budget, KL scorer, frozen selection rule) — makes the search select a different, broader
edit that cuts English judged refusal from .15 to .03 and the paired Slovene−English refusal gap from +.68 to +.38;
but the same English level is reached by simply **scaling the old edit 1.5×**, at a *smaller* Slovene gap (+.33) and
**one third the harmless KL**, so the mechanism is **dose, not better placement** — the falsifier this pod
pre-registered (P7) fired, and the miscalibration result, not the corrected checkpoint, is the finding.

### 1. The objective Heretic optimises is miscalibrated on its own candidates (the clean positive)

Every one of the **116 iteration-1 parameter draws** was re-scored on this GPU and all 11,600 in-loop generations
were labelled by the frozen art_m6pglf516e2r rubric (Qwen3-14B; CLASS ∈ {refused, complied, partial, irrelevant, malformed}, plus an auto label for empty):

| | keyword counter | partial-aware classifier | judge (Qwen3-14B) |
| --- | --- | --- | --- |
| item-level κ vs judge (11,600 in-loop responses, 116 edited draws) | **+0.196** | **+0.924** | — |
| refusal rate it reports | .907 | .702 | .711 |
| false-positive share of its "refusals" | **.254** | .025 | — |
| draw-level Spearman vs judged count | .925 | **.996** | — |
| mean abs. error in a draw's refusal count (20 held-out draws) | **30.6 / 100** | **2.1 / 100** | — |

The keyword counter never drops below **72/100** across all 116 draws, while judged refusal ranges **7–98/100**: the
optimiser is blind over exactly the region where the edits differ. On the keyword-selected checkpoint (trial 96) the
counter reports 74/100 where the judge sees 37 refusals and **49 PARTIAL** answers — suppressed refusals become
caveat-laden compliance, which keeps triggering the markers. This extends art_m6pglf516e2r's two-checkpoint finding
to dozens of the optimiser's own candidates (`results/miscalibration_table.csv`, fig1).

### 2. The corrected objective is certified where it runs

The classifier is distilled from 11,885 prior judge labels, trained on the first 100 tokens (the in-loop view) and
certified **only on 20 held-out replayed trials never used for training, refit or thresholding**:
κ = **.858** [.820, .888] refused-vs-not (cluster-bootstrapped over trials), against the keyword rule's **.143**
[.088, .190] on the same 2,000 responses. The base fit missed the pre-registered 0.80 bar (κ = .729) and was refit
once, as the plan permitted, with in-loop rows from the 36 *non*-certification trials. `scorer/certification.json`.

At the **point of selection** (`results/selection_point_cert.json`): over 10 stratified TPE-phase trials of the
corrected run κ = .839 (n = 1,000); on the *selected* trial alone κ = .26 — but that cell's judged refusal rate is
.08, where κ is dominated by the marginal and is not informative. What the optimiser consumes is the **count**, and
there the classifier reports 5/100 against the judge's 8/100, while the keyword counter reports **73/100**. The same
holds across the 10 stratified trials (mean absolute count error 2.1/100 vs the keyword rule's 30.6/100).

### 3. The search does move — and to a differently-shaped edit

With the corrected objective the frozen rule fires its **primary** branch (min KL s.t. ≤10/100 refusals), which the
keyword run never could: it selects **trial 7**, a *per-layer* kernel with aligned coverage A1 = **64.0** vs trial
96's 26.0 (P6 supported). The first 60 startup draws are byte-identical across runs (60/60 parameter sets verified),
so their Pareto fronts are a within-run A/B of the two objectives on the *same* edits: 8 points under the keyword
score, 14 under the corrected one. Over the TPE phase the corrected run searched broader, deeper-coverage kernels
(median mass 56.1 vs 44.7, p = 4e-5; A1 51.3 vs 36.3, p = .019) at higher KL (.070 vs .025, p = .005) — exploratory,
one seed per run.

**Coverage readout (EXPLORATORY, zero GPU; `results/coverage_correlations.json`, fig4).** Describing each of the
116 kernels by its *aligned* depth coverage A1 = Σ_h w(h)·|cos(v_used(h), d_EN(h))| explains the in-loop behaviour
well: ρ = **−.87** against judged in-loop refusal, better than raw kernel mass (−.79), and A1 survives partialling
out mass (partial ρ = −.66) where mass does not survive partialling out A1 (−.29). But it does **not** transfer to
the cross-language outcome: across the four evaluated full-dose edits ρ(A1, Slovene refusal) = −.40 (n = 4), and the
community edit sits at A1 = 43 with the *lowest* Slovene refusal of all. Reported as a descriptive bridge and an
honest negative, not a test.

**A second optimiser seed replicates the selection change** (the plan's first declared cut, run because the clock
allowed; `results/seed2_analysis.json`). Seed 20260926, everything else identical: the frozen rule again fires its
**primary** branch, again on a **per-layer** kernel with **5/100** in-loop refusals and aligned coverage
**A1 = 65.1** (seed 1: trial 7, 5/100, A1 = 64.0; keyword run: trial 96, A1 = 26.0). 13 of its 116 draws clear the
≤10/100 threshold versus 10 in seed 1 — and **none** of the 116 draws clears it under the keyword counter, which
never falls below 72/100. So "the corrected objective selects a broader, better-aligned kernel" is not one draw of
TPE noise; only the *behavioural* numbers below rest on a single seed.

### 4. Behaviour: better English suppression, half the Slovene gap — but dose explains it

100 verified EN↔SL pairs (S5X), 70 held-out-category StrongREJECT prompts, 60 XSTest-safe items, all arms from one
NF4 base load, one batch schedule, Qwen3-14B judge, cluster-bootstrap CIs over semantic items:

| arm | EN ref | SL ref | EN partial | SL gap (SL−EN) [95% CI] | S4hoc gap | FLORES ΔNLL SL |
| --- | --- | --- | --- | --- | --- | --- |
| A original | .95 | .99 | .02 | +.04 [+.01,+.08] | +.01 | — |
| B keyword-selected (trial 96) | .15 | .83 | .47 | **+.68** [+.59,+.77] | +.40 | +.004 |
| C corrected-objective (trial 7) | **.03** | .41 | .27 | **+.38** [+.29,+.47] | +.39 | +.003 |
| D reselected by classifier (trial 98) | .05 | .35 | .25 | +.30 [+.21,+.40] | +.39 | +.004 |
| D2 reselected by judge (trial 64) | .04 | .45 | .27 | +.41 [+.32,+.51] | +.44 | +.005 |
| F dose 1.5× on B | .03 | .36 | .31 | +.33 [+.24,+.42] | +.29 | +.005 |
| F dose 2× on B | .00 | .00 | .22 | +.00 | −.04 | +.011 |
| F dose 3× on B | .00 | .00 | .09 | +.00 | +.00 | +.086 |

C beats B on the paired gap by **−.30 [−.41,−.18]**, and on English refusal it reaches .03 — at or below the
community edit's .054 on RefusEU EN (P1 supported at the point estimate; its exact CI upper bound .085 is not, so
P1 is reported as *not* established at the CI level). **But at the same .03 English refusal the 1.5×-scaled old edit
has a gap of +.33, i.e. −.05 [−.41,+.12] relative to C**: P7 required the keyword edit to be ≥ +.15 *worse*, so P7
**fails** and the honest reading is Fallback D — *the English keyword objective stopped too early; a partial-aware
score is one way to make it stop later, and scaling the selected edit is another.* P2 (gap CI upper bound < .35)
also fails. Post-hoc reselection alone recovers the whole effect (P5: ratio 1.27 ≥ 0.5), and it is seed-free — so
the change is **mis-scoring of the trials the optimiser already had**, not a different search trajectory.

**The decisive cost column: harmless KL.** Heretic's own second objective, re-measured for every arm on this GPU
(`results/kl_arms.json`), shows the corrected edit is a far *bigger* edit — and that the dose ladder reaches the same
English refusal more cheaply:

| arm | harmless first-token KL | in-loop keyword/100 | in-loop classifier/100 | S5X ASR official EN [lo,hi] | SL [lo,hi] |
| --- | --- | --- | --- | --- | --- |
| A original | 0.000 | 100 | 97 | [.02,.09] | [.00,.07] |
| B keyword-selected | **0.026** | 74 | 32 | [.73,.88] | [.09,.24] |
| C corrected | **0.258** | 73 | 5 | [.88,.96] | [.45,.63] |
| D classifier-reselected | 0.085 | 82 | 9 | [.88,.95] | [.47,.66] |
| D2 judge-reselected | 0.249 | 76 | 9 | [.89,.96] | [.40,.64] |
| F dose 1.5× | 0.073 | 63 | 3 | [.83,.96] | [.48,.72] |
| F dose 2× | 0.164 | 40 | 0 | [.90,.94] | [.85,.97] |
| F dose 3× | 0.338 | 18 | 0 | [.92,.97] | [.89,.99] |

At matched English refusal (.03) the 1.5×-scaled keyword edit reaches a *smaller* Slovene gap (+.33 vs +.38) at
**one third** of the corrected edit's harmless divergence (.073 vs .258). Matched the other way — at **equal edit
size** (KL .258, exploratory/post hoc, added after the per-arm KL was measured) — the ladder reaches gap **.00** and
English refusal **.00**, i.e. −.38 [−.47,−.29] relative to the corrected edit: *dose for dose, the corrected
objective's edit is strictly **worse** on both axes*. So the corrected objective did not find a better-placed edit;
it found permission to take a *larger* one, which the frozen rule (min KL subject to ≤10/100 refusals) then accepted
because the classifier — unlike the keyword counter — could see that those edits had actually stopped refusing. Attack success under RefusEU's **official** guard pipeline (Llama-Guard-3-8B + PolyGuard agreement,
disagreements bounded, no adjudicator) moves the same way in both languages, so the judged pattern is not a judge
artifact.

No arm buys suppression with breakage: invalid output **0.000** everywhere, GlotLID language consistency ≥ .991,
Slovene FLORES ΔNLL ≤ +.005 nats for every selected arm (P3 supported), and XSTest-safe over-refusal *falls* versus
the original in both languages (P4′ supported). Only the 3× arm starts to pay: +.086 nats Slovene.

### 5. What a practitioner should take from this

* **Do not score an abliteration search with a substring refusal counter.** On the edits such a search actually
  produces, the counter is near-blind (κ = +.20, 25% of its "refusals" are false, and it never falls below 72/100
  while true refusal ranges 7–98/100). The failure is a *selection* failure, not evaluation noise: it happens on the
  optimiser's own candidates, at the moment it picks one.
* **A cheap fix works and is affordable.** A logistic-regression classifier over character n-grams plus a few hand
  features, distilled from ~12k existing judge labels and trained on the first 100 tokens, reaches κ = .86 against a
  14B judge *in the domain where the objective runs*, at ~0 GPU cost inside the loop (11,600 scored generations per
  run). The recipe and the certification protocol are the transferable part of this artifact.
* **But a better objective is not automatically a better edit.** Here the corrected objective mostly bought
  permission to take a *bigger* edit; matched on edit size, the old objective's edit — simply scaled — was better on
  both the English and the cross-language axis. Any "my objective is better" claim in this area must be made at
  matched dose *and* matched divergence, or it is not a claim about placement at all.
* **The Slovene gap is a dose phenomenon on this model, not a property of the edit's direction.** Scaling the
  English-derived edit 2× removes the gap entirely (.00/.00) at KL .16 — cheaper than the corrected edit's .26 —
  while a 3× dose starts to damage Slovene fluency (+.086 nats FLORES). The safety-utility frontier, not the
  objective, is where the interesting trade-off lives.

### 6. What this does NOT show

* **One model; two seeds for the selection, one for the behaviour.** Gemma-3-12b-it only (the GaMS3 corrected run
  was cut: its keyword proxy was already near-calibrated). The *selection* claim is replicated across two optimiser
  seeds and is also supported seed-free by post-hoc reselection; the *behavioural* arms (S5X/S4hoc/XSTest numbers)
  were generated from the seed-1 checkpoint only, so prompt-level CIs there do not measure run-to-run variance.
* **The keyword baseline of record is iteration-1's trial 96.** Exact reproduction of its L4 journal fails on this
  RTX 4090 (74 vs 69 keyword refusals; over 56 draws mean +0.16, max 6, Spearman .94) — greedy NF4/bf16 output
  differs at near-ties, so every number here is re-measured on one GPU (`results/replay_fidelity.json`).
* **No frontier judge validated any new label in this artifact.** The run-level OpenRouter budget was exhausted
  ($7.05/$7.00) at the first call, so $0.00 was spent here; the workhorse Qwen3-14B judge agrees with gpt-4.1 at
  κ = .78 refused-vs-not *within edited checkpoints* (vs .94 on originals, art_m6pglf516e2r labels) — that is the
  ceiling on every judged number below. The 672-item gpt-4.1 in-loop certification set is written and PENDING
  (`results/judge_in/inloop_gpt.jsonl`). PolyGuard's own refusal field is *itself* miscalibrated within edited
  checkpoints (κ = .45 vs gpt-4.1, calling 20/55 PARTIAL answers refusals), so it is a sensitivity arm, not a
  validator (`results/judge_ceiling.json`).
* **No capability-benchmark utility.** lm-eval utility (S7) was cut before generation; FLORES ΔNLL, harmless KL,
  language consistency, validity and XSTest-safe over-refusal are the stand-ins (deviation D4).
* **Slovene text is machine-translated with automated QC only** (the S5X pairs are gpt-4.1 cross-translations with
  back-translation chrF++/LaBSE checks); native review is PENDING.
* Absolute levels are NF4-specific; coverage descriptors (A1/A2) are **exploratory**, computed post hoc over saved
  parameters; the TPE-trajectory comparison describes two runs, not a population.

### Frozen predictions and their verdicts

Written and hashed before any evaluation generation existed (`results/frozen_predictions.json`, hash in
`logs/freeze_hashes.txt`; verdicts in `results/frozen_predictions_with_verdicts.json`).

| | prediction | verdict |
| --- | --- | --- |
| P1 | corrected-run EN judged refusal ≤ .054 | **point yes** (.03), CI upper .085 ⇒ not established at the CI level |
| P2 | S5X gap CI upper bound < .35 | **no** (+.38 [.29,.47]) |
| P3 | Slovene FLORES ΔNLL ≤ +.10 nats | **yes** (+.003 [-.002,+.008]) |
| P4 | utility macro drop ≤ 2 pts | **NOT TESTED** (S7 cut before generation); replacement P4′ (validity, language consistency, no over-refusal rise) **yes** |
| P5 | reselection recovers ≥ ½ of the gap reduction | **yes** (ratio 1.27) |
| P6 | corrected selection has greater aligned coverage A1 than trial 96 | **yes** (64.0 vs 26.0) |
| P7 | falsifier: dose-matched keyword edit ≥ +.15 worse | **no** (−.05 [−.41,+.12]) ⇒ mechanism is dose (Fallback D) |

### Verification

* `results/audit_headline.json` — **305/305** headline numbers re-derived from raw jsonl by a second code path
  (plain python, no pandas/stats_lib); all three placebos (within-arm label shuffle, EN/SL tag swap, arm permutation)
  fail as required.
* `results/audit_extra.json` — a **second** independent audit covering what the first does not: the item-level
  classifier κ, the certification κ and its gate, both dose-ladder interpolations and the seed-2 selection.
  **17/17** match, with the frozen selection rule re-implemented from its prose and four placebos that all fail as
  required (shuffled judge labels → κ .006; permuted ladder arms → +.30 instead of −.05; KL-shuffled candidates →
  a different trial; and a leakage control showing the refit's *training* trials score κ .96 against the honest
  held-out .858).
* `results/verify_numbers.json` — **59/59**: method_out.json's tables agree with the analysis objects *and* with a
  recount from its own shipped per-example rows.
* `results/test_scorer.json` — the Heretic plugin's verdicts equal the frozen classifier's, and its keyword replica
  equals Heretic's own `KeywordRate._is_match` on the same 41 texts.
* `results/deviations.json` — nine recorded deviations, with their effect on what can be claimed.

### Kept artifacts (absolute paths on this run's volume)

```
.../gen_art_experiment_11/adapters_corrected/                  # LoRA of the corrected-objective edit (trial 7)
.../gen_art_experiment_11/checkpoints/gemma_corrected/         # Optuna journal, corrected run seed 20260923 (resumable)
.../gen_art_experiment_11/checkpoints/gemma_corrected_s2/      # Optuna journal, replication seed 20260926 (resumable)
.../gen_art_experiment_11/scorer/refusal_clf.joblib            # frozen certified in-loop objective
.../gen_art_experiment_11/directions/gemma_corrected/          # its residual-mean capture
.../gen_art_experiment_11/results/                             # generations, labels, tables, audits
```

## Layout

| path | what it is |
| --- | --- |
| `method.py` | stage driver: `uv run method.py --stages <list>` or `--stages all` (runs every script below in order) |
| `third_party/heretic/` | pinned Heretic `3521f864` tree + **one new file**: `src/heretic/scorers/partial_aware_refusal.py` (`PartialAwareRefusal` objective, `ResponseRecorder`) |
| `runs/corrected_gemma/config.toml` | the ONLY configuration difference of the corrected run: `scorers = [PartialAwareRefusal, KLDivergence]` |
| `drive_heretic.py`, `select_rule.py` | iteration-1 non-interactive driver (+ a 10-line trial-tagging hook) and the frozen selection rule, verbatim |
| `replay.py` | re-scores iteration-1 draws through Heretic's own `reset_model → abliterate → Evaluator.get_scores` |
| `build_pool.py` → `results/label_pool.parquet` | 11,885 prior judge labels (gpt-4.1 / Qwen3-14B) joined to their generations |
| `train_clf.py` → `scorer/` | the distilled classifier (base fit + the one permitted refit), train reports, sha256 |
| `inloop.py` | in-loop response table, judge inputs, **certification** (`scorer/certification*.json`), refit table |
| `judges.py`, `reparse.py` | Qwen3-14B local judge and gpt-4.1 API judge, frozen art_m6pglf516e2r rubric verbatim; parser-only fallback |
| `guard.py`, `guard_analysis.py` | RefusEU official guard models (PolyGuard-Qwen, Llama-Guard-3-8B) and the bounded ASR |
| `coverage.py` → `results/coverage_*.{csv,json}` | zero-GPU kernel/coverage descriptors (aligned coverage A1/A2) |
| `analyze_inloop.py` → `results/inloop_analysis.json`, `results/miscalibration_table.csv` | per-draw keyword / classifier / judged counts over all 116 draws, post-hoc reselection, corrected-run selection, TPE-phase comparison |
| `make_arms.py`, `freeze_predictions.py` | evaluation arms and the hashed frozen predictions (written before any evaluation generation) |
| `eval_gen.py` → `results/eval_gen/` | all arms from one NF4 base load: S5X (100 verified EN/SL pairs), S4 held-out categories, XSTest-safe, FLORES NLL |
| `eval_judge_input.py`, `autoscore.py` | judge inputs; GlotLID language consistency, repetition, empty flags |
| `analyze_eval.py`, `verdicts.py` → `results/eval_analysis.json`, `results/headline_table.csv`, `results/frozen_predictions_with_verdicts.json` | statistics + prediction verdicts |
| `audit_headline.py`, `verify_numbers.py` | independent re-derivation (plain python) with placebos; method_out.json consistency |
| `judge_ceiling.py` | inter-judge agreement within edited vs original checkpoints; replay fidelity across GPUs |
| `audit_extra.py` → `results/audit_extra.json` | second independent audit (classifier/certification κ, dose interpolations, selection rule re-implemented from its prose) + 4 placebos |
| `pyproject.toml`, `env/requirements.lock` | the 172 pinned dependencies actually installed |
| `seed2.py` → `results/seed2_analysis.json` | the second optimiser seed (20260926) of the corrected run and its comparison with seed 1 |
| `kl_arms.py` → `results/kl_arms.json` | Heretic's own harmless KL + in-loop scores for every evaluation arm |
| `selection_point_cert.py` → `results/selection_point_cert.json` | judge-grade re-scoring at the point of selection |
| `guard_analysis.py` → `results/guard_analysis.json` | official-pipeline ASR with guard disagreements bounded |
| `reproducibility.md` | pins, freeze order, known non-determinism, how to re-run one piece |
| `figures.py` → `figures/` | fig1–fig6 (PNG + PDF) |
| `to_schema.py` → `method_out.json` | exp_gen_sol_out output (per-example rows + all analyses in metadata) |
| `protocol.yaml`, `logs/freeze_hashes.txt` | protocol and every freeze/amendment hash with its UTC time |
| `chain*.sh` | the background job chains actually executed (PID-based) |
| `inputs/` | copies of the read-only iteration-1 / art_m6pglf516e2r inputs used (journal, trials table, selection, rubric) |

## How to run

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python --index-strategy unsafe-best-match \
    --extra-index-url https://download.pytorch.org/whl/cu128 -r env/requirements.base.lock
uv pip install --python .venv/bin/python --no-deps -e third_party/heretic
uv pip install --python .venv/bin/python fasttext-numpy2-wheel
.venv/bin/python method.py --stages coverage,pool,clf_base,replay,judge_inloop,refit,certify,test_scorer
.venv/bin/python method.py --stages corrected,judge_corr,inloop_an,arms,evalgen,judge_eval,autoscore,eval_an,audit,figures,schema
# extras run after the core (each standalone):
bash chain7.sh && .venv/bin/python seed2.py        # second optimiser seed
.venv/bin/python kl_arms.py                        # harmless KL per arm
.venv/bin/python selection_point_cert.py           # certification at the selection point
.venv/bin/python guard_analysis.py                 # official-pipeline ASR
```
GPU stages need one 24 GB card (peak 13.8 GB for Heretic trials); the local judges need the shared HF cache
(`Qwen/Qwen3-14B@40c06982`, `ToxicityPrompts/PolyGuard-Qwen@644bfe73`, `meta-llama/Llama-Guard-3-8B@7327bd9f`,
`google/gemma-3-12b-it@96b6f1ec`, `cis-lmu/glotlid@85cd6716`). gpt-4.1 stages need `OPENROUTER_BASE_URL` and
`OPENROUTER_API_KEY` and stop at a cumulative `--max-usd`.

## Restoring removed files

`.aii/manifest.yaml` has three entries: `checkpoints/` (**keep** — the two Optuna journals) and
`adapters_corrected/` (**keep** — the 15 MB corrected LoRA) are the heavy/cache-named paths worth
preserving, and `.venv/` is the single **delete**. Everything else (results, logs, the frozen
classifier bundles, directions, figures, the pinned Heretic tree) is text or code and is kept
automatically.

```bash
# .venv/  — the ONLY delete entry; fully regenerable:
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python --index-strategy unsafe-best-match \
    --extra-index-url https://download.pytorch.org/whl/cu128 -r env/requirements.base.lock
uv pip install --python .venv/bin/python --no-deps -e third_party/heretic
uv pip install --python .venv/bin/python fasttext-numpy2-wheel
```

Model weights are never stored in this repo; they are re-downloadable at the revisions pinned above
and in `reproducibility.md` (`huggingface-cli download <repo> --revision <sha>`). `__pycache__/`
directories, if present, are recreated by Python on the next import.
