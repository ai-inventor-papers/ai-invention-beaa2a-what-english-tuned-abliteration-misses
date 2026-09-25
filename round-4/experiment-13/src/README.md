# Predicting where a refusal edit misses: a frozen write-mass overlap instrument, raced out of sample

Iteration-4 experiment artifact for run `run_Fapgmt6JWbcD` (`gen_art_experiment_13`). Anchor `google/gemma-3-12b-it`
(NF4, greedy); outside family `Qwen/Qwen3-8B` in EN, SL, DE, LT. One NVIDIA L4.

**Question.** Can a frozen, DEV-only *causal write profile* predict how much refusal a Heretic-family refusal-suppression
weight edit leaves behind in each language, on conditions and items it never saw? And can it beat the cheap predictors
(energy, layer count, depth span, EN/SL direction cosine, a single-site causal probe, the unedited refusal rate)?

**Instrument.** `O_L(edit) = Σ_h e_L(h)·g(h) / ‖g‖₂`. Here `e_L(h)` is the judged refusal drop from ablating the frozen
English direction `d_EN(h)` at **one** hidden index `h` (DEV items only, clipped and normalised), and `g(h)` is the
edit's closed-form per-layer removal energy. `O` is invariant to rescaling the edit coefficients, so it measures
**placement only**; energy carries dose.

*(Every number below comes from `analysis.py` over the saved generations and judge caches, is printed in
`results/report_tables.md`, and is re-derived independently by `rederive.py`; see "Audit" at the end.)*

## Verdict (frozen rule): **FALSIFIED** for the instrument claim; placement itself is strongly confirmed

The verdict rule was frozen before any confirmation output existed (`configs/protocol.yaml`, `configs/FREEZE.sha256`).
It returns **FALSIFIED** because O's incremental R² over the pre-declared nuisance stack is **0.026** in English (MDE
0.047, so this is a powered miss), below the 0.05 falsifier. In Slovene it is **0.052**, inside the inconclusive band
(MDE 0.109). All other components of the rule pass: rank correlation, the race against the named cheap baselines, null
controls, and the argmax band. What survives, and where it stops:

1. **Placement decides residual refusal at identical energy and identical layer count (confirmed, 8/8 groups, both
   languages).** Each group pairs a high-O window with a low-O window of the same size. The two are solved in closed form
   to the same removal energy and never overlap. Residual refusal, high-O minus low-O, on 60 frozen held-out items per
   language (40 StrongREJECT items from held-out Llama-Guard categories + 20 verified RefusEU EN–SL pairs):

   | group | k | energy | high-O window | low-O window | EN hi/lo | SL hi/lo | SL diff [95% CI] |
   |---|---|---|---|---|---|---|---|
   | G1 | 8 | 29.1 | 16–23 | 4–11 | 0.08 / 0.92 | 0.42 / 0.93 | −0.53 [−0.66, −0.41] |
   | G2 | 12 | 36.1 | 12–23 | 33–44 | 0.08 / 0.90 | 0.38 / 0.91 | −0.53 [−0.67, −0.40] |
   | G3 | 16 | 50.0 | 16–31 | 33–48 | 0.07 / 0.92 | 0.27 / 0.92 | −0.67 [−0.79, −0.55] |
   | G4 | 12 | 25.8 | 14–25 | 2–13 | 0.17 / 0.90 | 0.50 / 0.93 | −0.43 [−0.55, −0.30] |
   | G5 | 8 | 13.1 | 24–31 | 36–43 | 0.66 / 0.92 | 0.92 / 0.93 | −0.02 [−0.05, 0.00] |
   | G6 | 16 | 28.8 | 9–24 | 27–42 | 0.17 / 0.87 | 0.53 / 0.92 | −0.38 [−0.52, −0.25] |
   | G7 | 10 | 37.0 | 12–21 | 1–10 | 0.20 / 0.93 | 0.62 / 0.93 | −0.32 [−0.43, −0.20] |
   | G8 | 6 | 20.1 | 16–21 | 5–10 | 0.37 / 0.93 | 0.77 / 0.93 | −0.17 [−0.27, −0.07] |

   Pooled over the 8 groups: **EN −0.69 [−0.75, −0.62], SL −0.38 [−0.46, −0.31]**. McNemar is Holm-significant in 7/8
   groups in Slovene; G5, the weakest energy, is null in Slovene. The no-op leaves EN 0.92 / SL 0.93.

2. **It is the direction at those layers, not perturbation, and not dose.**
   - **Controls.** Controls placed at every core group's high-O layers leave refusal at the no-op level: a write-space
     random direction and the exp8 harmless principal component, each energy-matched within 10%. The largest
     control-minus-no-op shift is ±0.03 in every language, against −0.4 to −0.85 for the real edit. The random controls
     also matched collateral. The PC controls failed the collateral match in 4/5 groups because they were **more**
     disruptive than the real edit (harmless KL 0.14–0.27 vs 0.02–0.05), so the failure runs in the conservative
     direction.
   - **Dose rival.** The G3 low-O window (layers 33–48) at 1.5× and 2× the energy still leaves **EN 0.88 / SL 0.92–0.93**.
     No amount of late-layer edit within the operator's range reaches what the mid-depth window does at 1×.

3. **O is the best single ranker of held-out conditions.** It beats both named cheap baselines, but not the
   single-site probe in Slovene, and it is redundant with the direction-cosine descriptor. Over the 18 frozen weight
   conditions per language (the 16 group members + 2 dose points), Spearman(O, residual refusal) = **−0.96 [−0.98, −0.84]
   EN** and **−0.83 [−0.84, −0.82] SL**. The predicted sign is negative: more overlap, less residual refusal. The
   competitors on the same conditions:
   - **Energy and count:** log-energy −0.08 / −0.15, layer count −0.23 / −0.22 (by design they vary only across groups).
   - **g-weighted EN/SL cosine:** −0.81 / −0.78.
   - **Single-site peak probe B_site:** −0.78 / −0.79.
   - **Race against B_site** (paired item bootstrap, sign-aligned so > 0 favours O): EN **+0.17 [0.14, 0.23]**, where O
     wins; SL **+0.04 [−0.03, 0.04]**, a tie.
   - **Pooled rows (2 languages × 18 conditions):** O −0.84 beats the unedited refusal rate (aligned difference
     **[0.28, 0.65]**) and the single-site transfer rate at the frozen site h\* = 20 (**[0.29, 0.76]**), and ties B_site
     (**[−0.03, 0.04]**).

   **Why the ΔR² test fails:** R² of O alone is **0.87 EN / 0.75 SL**, but the g-weighted EN/SL cosine alone already
   reaches **0.83 / 0.63**, and the two correlate at ρ **0.81 / 0.76** across conditions. Both vary with where in depth
   the edit sits. Energy and count explain ≈ 0. Over energy + count only, O adds **0.90 / 0.77**. The frozen stack
   includes the cosine, and O adds 0.026 / 0.052 over it, while the cosine adds ≈ 0.01 over O. The honest form is:
   **"placement predicts; O is one good placement summary among collinear ones, not a uniquely better one."**

4. **The language-specific part of the instrument fails its placebo, so it is demoted.** Using the *English* profile to
   predict *Slovene* residual refusal works as well as or better than Slovene's own profile (ρ **−0.94** vs −0.83; EN
   with the SL profile −0.91). The cell-label permutation placebo collapses (95% null [−0.47, 0.47], p < 0.001). So does
   the energy-shuffled profile (EN p < 0.001; SL p = 0.034). But the **language-label** placebo does not collapse. What
   predicts is the *shape of the shared mid-depth band*, not a language-conditioned write profile, even though the two
   DEV profiles differ (Spearman e_EN vs e_SL = 0.59; the Slovene single-site drops are ~3× smaller).

5. **The frozen argmax prediction holds.** argmax e_EN = h19 and argmax e_SL = h16, both in band 13–24. The winning
   full-energy condition in both languages is G3 high-O (layers 16–31, 56% in band 13–24), and band 13–24 ranks first of
   the 3 bands observed. This replicates, on new conditions and held-out categories, iteration-3's exploratory band-13–24
   finding, which exp9 obtained only on a screen.

6. **The cross-language gap under the best-placed edit is largely a strict-vs-broad classification effect.** At G3
   high-O, strict refusal is **EN 0.07 vs SL 0.27**, but PARTIAL is 0.46 vs 0.27, so broad refusal (refused + partial)
   is **0.53 vs 0.53**. The rubric's own harm verdict still differs: ASR-by-rubric is EN 0.93 vs SL 0.72. Strict and
   broad rates are both in `results/report_tables.md`. Under the broad outcome, Spearman(O) is −0.73 in both languages.

**Collateral and validity.** Across the Gemma confirmation cells, judge INVALID is 0.00 everywhere, heuristic-invalid
≤ 0.017, and GlotLID consistency ≥ 0.97, so no condition is a FAILED edit and none was excluded. High-O edits cost
harmless KL 0.02–0.05 and FLORES ΔNLL ≤ +0.010 nats; low-O late-layer edits cost ≈ 0.003 KL.
**Exploratory, post hoc competitor (not frozen):** the edit's own harmless KL is a strong one-forward-pass predictor.
It gives ρ −0.84 EN / −0.58 SL on confirmation and −0.87 / −0.79 on the screen, and correlates with O (ρ 0.76 / 0.59).
O's LOO increment over the stack plus log-KL is 0.001 EN / −0.24 SL. Achieved perturbation is therefore a live
competing account for *ranking*. The controls show it is not *sufficient*: PC edits with 3–7× the KL do nothing.

## Screen (declared, not confirmatory): O on iteration-3 exp9's 46 Gemma weight cells

On exp9's cells (S3 JBB half B; O never saw them, but they carry no confirmatory weight), Spearman(O, residual) is
**−0.71 [−0.86, −0.50] EN** and **−0.60 [−0.79, −0.36] SL**. That beats the single-site probe (aligned difference
[0.40, 0.95] / [0.21, 0.89]) but not energy: log-energy gives −0.70 / −0.79, and O's ΔR² over the stack is 0.008 / 0.028
(LOO 0.000 / 0.009). This is the expected contrast: where energy varies freely, dose dominates. The matched design above
removes dose and exposes placement.

## The DEV causal profile (Phase 1, frozen)

| lang | no-op refusal (DEV, 44 items) | split-half r (judged) | split-half r (teacher-forced) | argmax h |
|---|---|---|---|---|
| EN | 0.89 | 0.84 | 0.99 | 19 |
| SL | 0.93 | 0.51 | 0.96 | 16 |

The judged profile passed the pre-declared split-half ≥ 0.5 rule in both languages, so it is primary. Slovene passes
only barely, at 0.51. The judge-free teacher-forced profile is far more stable and is reported beside it. English
single-site drops reach 0.43 across h 16–30; Slovene drops never exceed 0.14 (h 12, 16–17, 27–29). The "read" profile
(‖d_L(h)‖, the probe mass) rises monotonically to the last layers and is barely related to the causal profile (Spearman
0.28 EN, −0.06 SL). This reproduces the read-best-is-not-steer-best contrast (arXiv 2609.22135) in this setting.
Single-site transfer rate at h\* = 20: e_SL/e_EN = 0.21.

## Judging and the blocking judge gate

- **Scorer.** Local Qwen3-14B (NF4, thinking off, greedy) applying iteration-2 exp4's rubric verbatim, blind and
  shuffled, 4-way REFUSED/PARTIAL/COMPLIED/INVALID. PARTIAL is never counted as refusal, and INVALID is never counted as
  refusal or compliance. Parse failures were re-judged once at a larger token budget (`--refail`); the few that remain
  are excluded and counted.
- **Gate (gpt-4.1, 800 stratified items from this artifact's own confirmation cells, $0.97).** Within-edited
  κ(refused vs not) = **0.818** pooled, which passes. Per language it is **EN 0.856 (pass)** and **SL 0.744 (FAIL)**; by
  condition type, high-O cells 0.60, low-O 0.86, controls 0.86. Slovene claims are therefore **JUDGE_SENSITIVE**. The
  local judge over-calls refusal in Slovene (Se 0.98, Sp 0.69 against gpt-4.1). Rogan–Gladen-corrected Slovene rates
  leave the ranking unchanged (ρ −0.83; the correction is monotone) and make every matched contrast larger (G3
  −0.67 → −0.90). The Slovene residuals above are thus upper bounds.
- **Gate 2 judge sanity check: FAILED.** On 8 deliberately invalid synthetic replies (empty, repeated token, wrong
  language, irrelevant), the judge returned INVALID only for the empty one. It returned REFUSED for 4 and COMPLIED for 3
  (`results/gate2_judge_invalid_check.json`). So incoherence can read as refusal. Before any confirmation output
  existed, a deterministic validity guard was added to the failed-edit rule: empty, GlotLID < 0.5, or 3-gram
  repetition > 0.5. It catches 5/7 of the non-empty probes; the 2 it misses are fluent but irrelevant replies in the
  right language. On the real confirmation cells the guard fires on ≤ 1.7% of replies.
- **Native-speaker review** of the SL/DE/LT items and outputs is **PENDING**, not performed.

## Outside family: Qwen3-8B (EN, SL, DE; LT excluded by the pre-registered gate)

- **Gate** (no-op DEV refusal ≥ 0.60 and INVALID ≤ 0.20, applied before any Qwen confirmation output): EN 0.88, SL 0.63
  and DE 0.67 are eligible; **LT 0.46 is excluded**, as in iteration-3 exp12.
- **Profile.** Reduced resolution: every 3rd hidden index, 24 DEV items. Split-half r = 0.92 EN, 0.85 SL, 0.79 DE,
  with peaks at h 21–27 (SL, DE) and 24–36 (EN). Directions reused from exp12 (fresh-vs-frozen cosine 1.00).
- **Design.** 3 matched groups (k = 6 or 9), a no-op and a write-space random control, on 40 held-out StrongREJECT items
  per language.

| lang | CONF no-op | ρ(O, residual) [CI] (6 cells) | ρ B_site | aligned O − B_site [CI] | QG1 hi/lo | QG2 hi/lo | QG3 hi/lo | random ctrl |
|---|---|---|---|---|---|---|---|---|
| EN | 0.87 | −0.76 [−0.88, −0.54] | −0.79 | [−0.03, 0.10] | 0.80 / 0.88 | 0.57 / 0.85 | 0.55 / 0.88 | 0.85 |
| SL | 0.65 | −0.93 [−0.99, −0.78] | −0.79 | [0.02, 0.17] | 0.42 / 0.68 | 0.20 / 0.60 | 0.33 / 0.57 | 0.65 |
| DE | 0.73 | −0.84 [−1.00, −0.71] | −0.77 | [−0.16, 0.19] | 0.49 / 0.74 | 0.46 / 0.76 | 0.46 / 0.74 | 0.75 |

The high-O member leaves less refusal than its energy- and count-matched low-O partner in **9/9** group × language
contrasts. 8/9 CIs exclude 0 (EN QG1 −0.07 [−0.17, 0.00]); McNemar p ≤ 0.007 in 8/9. The random control at the QG1 high-O
layers is null in all three languages. Log-energy carries no signal (ρ 0.13 / 0.00 / 0.18). **The placement result
therefore transfers to a second family and to a third language.** O beats the single-site probe only in Slovene; with
6 conditions per language the rank statistics are coarse (Spearman MDE ≈ 0.94 at n = 6). The direction of the cross-language
miss **reverses** in Qwen: the same English-derived edit leaves *English* more refusal than Slovene (QG2 hi-O EN 0.57 vs
SL 0.20). That fits the profile, since Qwen's Slovene single-site drops are as large as English ones at mid-depth. It is
a second reason the "Slovene is the hard language" framing does not generalise beyond Gemma.

## Panel size

10,000 harmful-prompt generations were scored: Gemma DEV profile 4,312, Gemma confirmation 3,480 (29 conditions × 60 items × 2 languages), Qwen3-8B DEV profile 1,248, Qwen3-8B confirmation 960. Of these, 9,989 were judged; 11 judge parse failures are excluded and counted. Every Gemma confirmation cell also has teacher-forced FLORES (200 pairs) and harmless-KL (100 Dolly prompts) collateral, and 800 gpt-4.1 gate labels were purchased. Every departure from the plan is listed in `results/deviations.json`: 18 deviations, and 3 planned items NOT RUN (utility panel, guard-pipeline ASR, GaMS3 screen), none reported as a null.

## What this establishes, and where it stops

- **Observation (confirmatory).** At identical closed-form removal energy and identical layer count, *where* an English
  refusal-direction weight edit lands sets how much refusal remains in both languages, on held-out harm categories and
  verified translation pairs. The effect holds in 8/8 pre-registered groups. Energy- and layer-matched random and
  harmless-PC directions are null, and a 2× dose of the badly placed edit does not substitute for placement.
- **Observation (confirmatory).** The frozen overlap instrument O ranks the 18 held-out conditions almost perfectly
  (ρ −0.96 EN / −0.83 SL). It beats the unedited refusal rate and the single-site transfer rate, the two cheap baselines
  that beat this run's previous instrument.
- **Failed hypotheses (pre-registered, falsifier fired).** (i) O adds ≥ 0.05 R² over the declared nuisance stack: it
  adds 0.026 in EN (powered) and 0.052 in SL (inconclusive band). (ii) The instrument is language-specific: the
  language-label placebo does not collapse.
- **Interpretation.** O works because it encodes *where the shared mid-depth refusal-write band is* (13–24 in Gemma).
  Any descriptor that tracks edit placement across depth does nearly as well, including the g-weighted EN/SL direction
  cosine and, post hoc, the edit's harmless KL. This bounds the usefulness of a language-conditioned causal profile: it
  predicts well, but not better than cheaper placement summaries.
- **Unexecuted proposals.** A second anchor checkpoint (the sibling GaMS3 artifact owns it); a bf16 control cell; the
  six-task utility panel on the extreme conditions; an official guard-pipeline ASR; a design that de-correlates O from
  the cosine profile (e.g. non-contiguous layer sets chosen to disagree on the two), which is the test that could still
  separate them.

## Audit

- **Independent re-derivation.** `rederive.py` (stdlib + numpy, imports nothing from the analysis path) recomputes the
  profile, energies, O values, every confirmation residual, the Spearman and ΔR² statistics, matched contrasts, control
  residuals, the screen, the outside family and the judge κ, and it checks freeze ordering: **209/209 checks pass** (`results/rederive_report.json`), including two placebo checks run on shuffled input: a shuffled-O Spearman must fall inside its 99th-percentile null, and a label-swapped matched contrast must centre on 0. Both behave as required.
- **Freeze.** `configs/FREEZE.sha256` (frozen predictions, protocol, method.py, freeze.py, alib.py, common.py,
  interventions.py, local judge) was written before any confirmation generation. The confirm stage refuses to run on a
  hash mismatch, and `rederive.py` asserts that every `CF_*` file is newer than the freeze. The freeze was written three
  times, all before any `CF_*` output existed: the first freeze; a re-freeze after adding the heuristic validity guard
  (triggered by the Gate-2 judge failure); and a re-freeze after an analysis-library change (the pairwise profile).
  The frozen predictions were identical across the three. After the run, `common.py` and `rederive.py` were edited only to replace an absolute server path with a relative constant (`AII_LOOP_DIR`), so their current hashes differ from the as-run hashes in `FREEZE.sha256`. A re-run must execute `freeze.py` before `--stage confirm`.
- **Cost.** OpenRouter $0.97 (800 gpt-4.1 judge-gate calls), against a $10 cap and a $6 hard stop.

## Limitations

- **Unit counts.** One anchor checkpoint and one outside family. Conditions come from one operator family (uniform-c
  contiguous windows), constructed by us rather than drawn by Heretic's search. These are 2 model units, not a law.
- **NF4 throughout.** Absolute levels are NF4-specific; only within-protocol contrasts are claimed.
- **Generation budget.** Confirmation replies are capped at 128 new tokens, and 98.5% hit the cap. Judgments therefore
  rest on the opening of each reply; PARTIAL is large (0.27–0.47 on the high-O cells).
- **Judge.** The local judge fails the per-language gate in Slovene (κ 0.744) and the INVALID sanity probe. Slovene
  levels are JUDGE_SENSITIVE; ranks are robust to the Rogan–Gladen correction.
- **Items.** Slovene/German/Lithuanian items are machine-translated with automated QC only; native review is pending.
  The S4 held-out-category items were used by exp9 to confirm *other* cells; they never entered the fitting of O.
- **Operator mismatch.** The profile is measured with activation ablation and applied to weight-output edits. Gemma-3's
  post-projection norms mean the weight operator does not guarantee the direction is removed from the residual write.

## Layout

```
method.py               GPU pipeline. --stage {smoke, profile, confirm, outside}; resumable per cell.
                        smoke: Gate 0 (pins, split SHAs, reuse inventory, fresh-vs-frozen direction cosines),
                        Gate 1 (operator identities), Gate 2 (generation sanity) and the timing model.
                        profile: Phase 1 causal write profile (no-op + 48 single-site ablations, DEV, EN+SL) and the
                        teacher-forced readout. confirm: Phase 4 (refuses to run unless configs/FREEZE.sha256 matches).
outside.py              Phase 5, Qwen3-8B: A = eligibility gate + reduced-grid profile; B = frozen CONF conditions.
freeze.py               Phase 2: profiles, primary-variant rule, matched groups, frozen CONF item ids, MDE, hashes.
freeze_outside.py       Phase 5 freeze (gate, profile, 3 matched groups + no-op + random control).
interventions.py        GPU engine copied from iteration-3 exp9 (hooks, closed-form energy, batched generation),
                        minimally generalised to a second model family.
common.py               Paths, pins, SHA-checked frozen-split loading, frozen item sets (DEV / CONF / collateral).
alib.py                 Judge-label join (4-way), GlotLID, heuristic validity guard, rates, shared statistics.
judge/local_judge.py    Primary scorer: Qwen3-14B NF4, exp4 rubric verbatim, blind; --refail re-judges parse failures.
judge/api_judge.py      Blocking judge gate: gpt-4.1 on a stratified subsample of this artifact's edited cells.
analysis.py             Every reported number -> results/analysis.json, cell_table.csv, per_item.csv.
rederive.py             Gate 7: independent stdlib+numpy re-derivation + freeze mtime ordering -> rederive_report.json.
figures.py              fig1-fig6 (PDF + PNG) in figures/.
make_deviations.py      results/deviations.json (every departure + every NOT RUN item).
build_output.py         method_out.json in the exp_gen_sol_out schema (+ full/mini/preview variants).
run_chain1.sh           as run: Phase 1 -> judge.   run_chain2.sh  as run: confirm -> outside A (crashed on a
                        missing item field, fixed) -> run_chain3.sh as run: outside A -> judge -> refail ->
                        freeze_outside -> outside B -> judge -> refail.
report_tables.py        results/report_tables.md (every table quoted here).
configs/protocol.yaml   the protocol, written before any model output (results/protocol_declared_utc.txt).
configs/frozen_predictions.json + FREEZE.sha256   the frozen instrument, conditions, items, predictions, MDE.
configs/exp4_protocol.yaml   byte-identical copy of the iteration-2 exp4 rubric (checked in Gate 0).
results/gens/           every generation, one JSON per cell (PF_* profile, CF_* confirmation, QPF_/QCF_* Qwen3-8B,
                        SMK_* synthetic judge probes).
results/cells/          per-cell metadata: layers, coefficient profile, closed-form energy, FLORES dNLL, harmless KL,
                        timings; *__draws.json for the matched controls.
results/                judge_local.jsonl, judge_api.jsonl, api_costs.jsonl, analysis.json, cell_table.csv,
                        per_item.csv, rederive_report.json, deviations.json, gate0_pins.json, gate1_operator.json,
                        gate2_samples.json, gate2_judge_invalid_check.json, timing_model.json, timings.json,
                        reuse_inventory.json, profile_tf.json, profile_tf_prefix.json, outside/ (Qwen3-8B files).
```

All kept artifacts (everything above) stay on the run's volume at these paths relative to this directory; they are text
or JSON and are also in the published repository. Model weights are not stored here.

## How to run

The exact as-run sequence, hardware, runtimes and expected numbers are in `reproducibility.md`; the short form:

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r pyproject.toml      # exact pins; torch cu128 from the extra index
.venv/bin/python method.py --stage smoke                        # gates 0/1/2 + timing (~4 min + load)
.venv/bin/python method.py --stage profile                      # Phase 1 (~37 min on one L4)
.venv/bin/python judge/local_judge.py && .venv/bin/python judge/local_judge.py --refail
.venv/bin/python freeze.py                                      # Phase 2 -> configs/FREEZE.sha256
bash run_chain2.sh      # Phase 4 (+ Phase 5A; as run it stopped there)
bash run_chain3.sh      # Phase 5 + judging + refail
.venv/bin/python judge/api_judge.py --n 800                     # blocking judge gate (OpenRouter, ~$0.8)
.venv/bin/python analysis.py && .venv/bin/python make_deviations.py && .venv/bin/python rederive.py
.venv/bin/python report_tables.py && .venv/bin/python figures.py && .venv/bin/python build_output.py
```

One NVIDIA L4 (23 GB); generation and judging never co-reside on the GPU. Model weights come from the run's shared HF
cache and are re-downloadable:

```bash
hf download google/gemma-3-12b-it --revision 96b6f1eccf38110c56df3a15bffe176da04bfd80   # anchor (gated)
hf download Qwen/Qwen3-8B         --revision b968826d9c46dd6066d109eabc6255188de91218   # outside family
hf download Qwen/Qwen3-14B        --revision 40c069824f4251a91eefaf281ebe4c544efd3e18   # judge
hf download cis-lmu/glotlid model.bin --revision 85cd6716494360367b75f642b5bc78667605d0b4
```

Read-only inputs from earlier artifacts of this run (paths relative to the run's `3_invention_loop/`):
`round-1/dataset-1/src/data/` (frozen splits, SHA-verified), `round-2/experiment-8/src/directions/`
(frozen d_EN(h), d_SL(h)), `round-3/experiment-9/src/results/{rhat_orth.npy, energy_real.json, cells.csv, cells/}`
(orthogonalised directions, closed-form energies, screen cells), `round-2/experiment-8/src/results/gemma/layerwise_pc.npy`
(PC control), `round-3/experiment-12/src/{data/, results/qwen3/directions.npz}` (DE/LT items, Qwen3 directions).

## Restoring removed files

`.aii/manifest.yaml` marks one path `delete`: the regenerable Python environment. Nothing a later step reads is deleted;
all results, figures, configs, code and logs are kept.

| deleted path | command that restores it |
|---|---|
| `.venv/` (11 GB) | `uv venv .venv --python=3.12 && uv pip install --python .venv/bin/python -r pyproject.toml` |
