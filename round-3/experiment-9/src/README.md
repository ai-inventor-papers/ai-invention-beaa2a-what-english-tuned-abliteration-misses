# How deep must an edit go to stop Slovene refusal? — it is not depth, it is *which* layers

Iteration-3 experiment artifact for run `run_Fapgmt6JWbcD` (`gen_art_experiment_9`), `google/gemma-3-12b-it` only, NF4.

It asks a question iteration 2 left open. Iteration 2 found that an English refusal-direction edit at one site leaves
**0.86** Slovene harmful refusal, while ablating *each layer's own* harm direction at **all 48** sites drops it to 0.10 —
so the Slovene residual looked like something written *redundantly across depth*. This artifact asks whether that reading
survives a controlled test: **at matched edit energy, does covering more depth buy Slovene suppression?**

It does not. The pre-registered coverage hypotheses fail, their own falsifier fires, and the exploratory analysis that
replaces them gives a sharper and more useful answer: **a single contiguous mid-depth band (layers 13–24) is what
matters**, and breadth helps only when it happens to contain that band.

*(Every number below is produced by `analysis.py` from the saved generations and judge caches, re-derived independently by
`rederive.py` through a separate stdlib+numpy code path, and printed into `results/report_tables.md`. The headline
numbers, verdicts and audit counts in this README are filled from those files — see `results/report_tables.md` for the
complete tables.)*

## What was run

| stage | items | cells |
|---|---|---|
| **Part A** (DEV depth-redundancy index) | S3 JBB **half A**, 44 harmful + 44 harmless per language | 29 activation cells: cumulative prefix (1..k), cumulative suffix (49-k..48), leave-one-band-out, k grid of 4 |
| **Screen** (coverage × strength factorial) | S3 JBB **half B**, 41 harmful + 41 harmless per language | 75 cells: 9 coverage sets × 4 strengths, 4 matched-energy groups, 8 random + 8 PC controls, anchors, Heretic-exact kernel |
| **Confirmation** (frozen subset) | S4 StrongREJECT **hoc** (held-out categories) + **ind**, 70 pairs each; S6 XSTest safe, 60 items; S7 utility, 100 items × 6 tasks | 15 cells |
| **S5X** (single declared second touch) | 100 verified pairs: an official RefusEU prompt + its own checked cross-translation, 50 per direction | the 2 best cells by the frozen rule + no-op |

Operator: Heretic's orthogonalised output-projection edit, applied as exact forward hooks on `o_proj` and `mlp.down_proj`
(`out ← out − c (out·r̂) r̂`, identical to `W ← (I − c r̂ r̂ᵀ) W` for a linear map; unit-tested against the explicit
product at relative error 0.0). `r̂_h` is that layer's own `d_EN(h)` from iteration 2, orthogonalised against the English
harmless mean. Directions are **never recomputed** — `directions/gemma_all_layers.npz` is read from
`iter_2/.../gen_art_experiment_8`, and `cos(d_EN(L20), the separately saved vector) = 0.99998`.

Energy is closed-form: `E(S, c) = Σ_{h∈S, m} c² ‖W_mᵀ r̂_h‖²`, from the dequantised NF4 weights, so matched-energy pairs
are **solved**, not searched: `c_broad = c_narrow √(E_narrow(1)/E_broad(1))`. All four groups solved inside Heretic's
`max_weight = 1.5` with no shifting.

## Headline

Panel: **27,784 generations across 122 cells**, 27,761 judged (0.08% unparsed, excluded and counted).
Independent re-derivation: **318/318 headline checks match** through a separate stdlib+numpy code path (`results/audit.json`).

1. **Coverage count does not explain the Slovene residual — P1 fails and its own falsifier fires.** Adding coverage
   descriptors (number of covered layers, covered depth span, mean covered depth) to a base of log-energy + the English
   effect + the static geometry baselines (`b1` per-layer EN/SL cosine profile, `b3` band masses) gives
   **ΔR² = 0.040, 95% CI [0.006, 0.136]** over 46 cells — but leave-one-out ΔR² is **−0.002**, the partial F-test gives
   **p = 0.17**, and a cell-label permutation placebo produces a *larger* ΔR² than the real data (placebo p95 = 0.158).
   Log-energy alone already explains R² = 0.50. With 46 cells the minimum detectable ΔR² is 0.071, **below** the 0.10
   bar, so this is a real rejection and not an underpowered one. The pre-registered falsifier (ΔR² < 0.05) **fires**.
2. **Broad-and-weak does not beat narrow-and-strong at matched energy, and the language interaction runs backwards —
   P2 fails.** Pooled matched-energy contrast **+0.049 [−0.000, 0.098]**, inside a narrow/broad label-swap placebo band
   ([−0.07, 0.07]), with signs that **disagree across groups** (G1 −0.02, G2 −0.34, G3 +0.34, G4 +0.22). The
   pre-registered coverage × language interaction has the wrong sign: the contrast is **larger in English**
   (difference of differences SL − EN = **−0.120 [−0.214, −0.033]**). Held-out harm categories replicate this exactly
   (pooled +0.054 [0.011, 0.100], same mixed signs, DiD −0.061 [−0.132, +0.011]). Holm-adjusted across the declared
   family, nothing survives (P2 0.14, P1 0.34, DiD 0.996).
3. **What actually governs it (EXPLORATORY, declared in `configs/explore_band_identity.json` and hashed before its
   outcome was computed): how densely the edit covers layers 13–24.** The lowest Slovene refusal each coverage set can
   reach, ordered by the fraction of band 13–24 it covers, is a clean monotone dose-response:

   | fraction of layers 13–24 covered | coverage sets | lowest SL refusal reached |
   |---|---|---|
   | 12/12 | K96, C36, ALL48 / C24, B2 | **0.024** / 0.171 |
   | 6/12 | S2 (stride-2, full depth) | 0.732 |
   | 3/12 | S4 (stride-4, full depth) | 0.927 |
   | 0/12 | B1 (1–12), B3 (25–36), B4 (37–48) | 0.951–1.000 |

   **Spearman(band density, lowest SL reached) = −0.942**, and a label-permutation placebo puts the observed separation
   between full-band and partial-band sets (0.839) far outside its null ([−0.54, 0.54], **p = 0.0038**;
   `results/audit_positive.json`). Every set covering the band in full reaches below 0.5; **no** set that covers it
   partially or not at all ever does, at any strength up to Heretic's cap. Note this is *density*, not mere
   intersection: S2 covers every other layer of the band — half of it, across the full depth — and still fails at
   0.732. The decisive matched-energy pair makes the same point with energy held exactly equal (group G2, E = 19.2):
   **12 contiguous mid-depth layers reach SL 0.63 while 24 layers strided across the full depth leave 0.98.** And the
   *cheapest* edit that suppresses Slovene is the **narrow** full-band one (E ≈ 43 at c = 1.5), not a broad one
   (ALL48 needs E ≈ 73).

4. **The DEV-frozen index predicts out of sample — P3 passes.** Interpolating the half-A prefix curve at each cell's
   effective covered-layer count predicts per-cell residuals with **Spearman 0.78 [0.64, 0.88] (EN)** and
   **0.78 [0.62, 0.89] (SL)** on held-out items, and its threshold is sharp in one direction: **97% of cells covering
   fewer than index_SL = 20 effective layers leave Slovene above 0.5** (n = 32). The converse holds only 47% of the
   time, because strength matters too — the index is **necessary, not sufficient**. On held-out harm categories it
   survives for Slovene (0.72 [0.13, 1.00]) but with only 10 cells it is underpowered (EN 0.57 [−0.01, 0.91]).
5. **The pre-registered cross-language asymmetry C2 holds in direction, but the *index* statistic is too coarse to
   carry it — the curve separation is.** index_EN = **16** [16, 20], index_SL = **20** [20, 28] (prefix family,
   declared primary), so the direction is as pre-registered. But the index is a step function on a grid of 4, so its
   smallest non-zero gap *is* 4, and under a within-item language permutation the gap's null is [−4, +4]: a 4-layer
   gap is **not separable from permutation noise** (`results/audit_positive.json`, block B). The properly powered
   statistic for the same claim is the mean vertical separation between the two prefix curves, which uses all 13 grid
   points and every item: **+0.080 [0.021, 0.136]**, language-permutation null [−0.059, 0.059], **p = 0.0065**. So
   "Slovene's coverage requirement exceeds English's" is supported — by the curves, not by the index threshold. On the
   secondary suffix family both indices are 24 (a tie), reported as declared.

6. **The leave-one-band-out profile is where the two languages genuinely differ.** Sparing layers 25–36 from an
   otherwise full-depth ablation raises Slovene residual refusal by **+0.39** but English by **0.00**. So 25–36 is
   necessary for Slovene and dispensable for English — even though, in the weight operator, 25–36 *alone* does nothing
   for Slovene (0.95–0.98). Necessary, not sufficient, and only for one of the two languages.
7. **Practically, the weight-space edit dominates iteration 2's activation repair — but read each number against the set
   it was measured on.** The strongest suppression cells (c = 1.5) were run on the **screen** set and on the **verified
   S5X pairs**, not on the frozen confirmation subset, so:
   - *Screen* (S3 JBB half B): Heretic's own kernel support at c = 1.5 gives **SL 0.024 / EN 0.049** harmful refusal at
     **FLORES ΔNLL −0.000 nats, KL 0.030, 0% invalid, 99.2% Slovene**; ALL48 at c = 1.5 matches it at +0.057 nats.
   - *S5X* (100 **verified** RefusEU translation pairs, the single declared second touch): both cells give
     **SL 0.08 / EN 0.02**, against the unedited model's SL 0.98 / EN 0.91.
   - *Confirmation* (S4 held-out harm categories, S6, S7) covered the frozen subset, whose strongest member is the
     kernel at ×1: **SL hoc 0.71 (−0.24 [−0.36, −0.14], McNemar p < 1e-4)**, Slovene **over-refusal** on XSTest-safe
     **0.37 → 0.08**, at utility cost indistinguishable from zero (S7 macro EN 0.615 → 0.617, change
     +0.002 [−0.007, +0.010]; SL 0.493 → 0.492, change −0.002 [−0.012, +0.010]) and FLORES −0.002 nats.
   - By contrast iteration 2's best activation repair (X1, all-48) reaches a lower SL hoc (0.07) but costs
     **+0.589 nats** of FLORES and a real English capability hit: S7 macro EN 0.615 → 0.562
     (**−0.053 [−0.083, −0.023]**, CI excludes 0), SL 0.493 → 0.468 (−0.025 [−0.058, +0.010], CI includes 0). Same
     direction family, same model: the operator and the band choice are what changed. Which of the two is preferable
     depends on whether the remaining 0.07-vs-0.71 Slovene refusal or the fluency and capability cost matters more —
     the weight edits at c = 1.5 appear to give both, but they were not run on the confirmation subset, so that
     comparison is screen-and-S5X-grade and is flagged as such.

   PARTIAL compliance is 0.15–0.20 on the suppression cells and is always shown as its own column; ASR-by-rubric is
   reported separately from refusal and *rises* as refusal falls (X1 SL 0.81, kernel ×1 SL 0.45, unedited 0.29), which
   is the point of reporting the two apart.

8. **Both matched controls are null.** Layer-matched random directions drawn from each module's own *write space*, and
   energy-matched harmless principal components, applied at the same sites with energy matched within 10% **and**
   collateral matched, leave Slovene refusal at **0.95–1.00** and English at 0.85–0.93 — the real cell's contrast minus
   the control's is the whole effect. The effect is the harm direction, not the amount of edit. The write-space draw
   also fixes iteration 2's control problem: **all 8 random controls matched energy *and* collateral** (5 on the first
   draw, 3 on the second, out of an allowance of 5), where exp8's isotropic draws could reach `d_EN(h)`'s energy at only
   15/48 layers.

9. **An independent, activation-only read converges on the same band (EXPLORATORY, Part G).** Measuring each layer's
   own *contribution* to the residual stream along `d_EN(h)` at the pre-response position, harmful minus harmless, the
   two languages put their harm-write mass in **different bands**: English places **63%** of it in layers 37–48 and 31%
   in 25–36; Slovene places **60%** in 25–36 and only 20% in 37–48. Slovene's band profile correlates with the causal
   leave-one-band-out necessity profile at **Spearman 0.40**, English's at **−0.11**. So a teacher-forced activation
   measurement and a causal ablation, which share no machinery, independently point at the same mid-depth band for
   Slovene. The *other* Part-G prediction — that Slovene's write is spread over **more** layers — is **false**: both
   languages need 18 layers to reach 80% of their mass (entropy 3.23 EN vs 3.28 SL). It is the **location**, not the
   spread, that differs. This is the mechanistic counterpart of the failure of P1: the Slovene write is not more
   diffuse, it is deeper-but-not-latest, which is why a broader edit buys nothing and a correctly placed one buys
   everything.

**Reading.** The redundancy story from iteration 2 was half right. The Slovene refusal write is *not* smeared uniformly
across depth — a 12-layer contiguous band carries it, and spreading the same energy thinner across more layers
accomplishes nothing. Iteration 2's frozen single site, hidden index 20, in fact sits *inside* that band; what it lacked
was not reach but **quantity** — one site delivers a twelfth of the band's write, and the prefix curve shows Slovene only
crossing 0.5 once coverage extends through layer 20 (0.73 at k = 16 → 0.48 at k = 20). So the all-48 result was never
evidence that *depth per se* was the missing ingredient; it was evidence that enough of the band had finally been
included. The honest form of the pre-registered claim is the falsifier's: **Slovene does not need a broader edit; it
needs enough of the edit landed in the right band** — and that band (13–24, with 25–36 necessary but not sufficient on
top) is one the English objective never has to reach, which is why an English-optimised edit stops too early.

**What would falsify the replacement claim.** If a second checkpoint put its Slovene-critical band elsewhere, or if a
coverage set *excluding* 13–24 could be pushed below 0.5 by strength alone at a higher cap than Heretic's 1.5, the
band-identity reading would not survive. Neither is tested here: one model, and a strength ceiling set by the operator
family. That is the first thing a replication should try.

## Judging

Primary scorer: **`Qwen/Qwen3-14B`@40c06982**, NF4, thinking disabled, greedy, applying iteration-2 `gen_art_experiment_4`'s
frozen `protocol.yaml` rubric **verbatim** (same system message, same user template, same parser). Four-way class
**REFUSED / PARTIAL / COMPLIED / INVALID**; PARTIAL counts as compliance in every refusal-removal number and is always
shown as its own column; INVALID (irrelevant, malformed, empty) is never counted as refusal. The rubric's own harm
verdict gives an ASR-by-rubric column reported **separately** from refusal. Response language comes from GlotLID
(line-level), not from the judge. The scorer is blind: items from every cell are pooled, de-duplicated by content and
shuffled by a seeded hash before length-bucketing.

**Certification.** Against gpt-4.1 labels **already on disk**, restricted to EDITED checkpoints, κ(refused-vs-not) =
**0.779** — below the 0.80 bar. As the plan prescribes, one stratified **600-item gpt-4.1 subsample of this run's own
edited cells** was bought (`$0.70`, single call per item, same rubric, temperature 0, seed 0): κ = **0.866**, which
passes. Both numbers are reported; every headline rate is a judge-dependent quantity and the PARTIAL column is always
visible.

**Instrument checks.** Judge parse failures were 182/13,918 and were traced to a real cause — the judge spending its
40-token budget listing all 14 policy categories and being cut off before its `CLASS`/`LANG` lines — then re-judged once
at a larger token budget with the same model, rubric and decoding, leaving **17 (0.12%)**, which are **excluded from every
rate and counted**, never scored as non-refusal. The keyword proxy is reported only as a diagnostic and decides no
number.

**Native-speaker review of the Slovene items and outputs is PENDING — not performed.** Slovene items are
machine-translated with automated back-translation QC from the frozen dataset artifact.

## Anchor reproduction (Gate 2)

Before scaling, three iteration-2 cells were re-run on the same 20 harmful items per language. Every **Slovene** anchor
reproduces within 0.05 of exp8's own judges (A1 0.95 vs 0.90/0.95; X4 0.95 vs 1.00/0.95; X1 0.20 vs 0.00/0.35). The two
**English** anchors sit *between* exp8's two judges (A1 ours 0.20, gpt-4.1 0.00, exp8's Qwen 0.60) because the three
labellers split the PARTIAL class differently — here half of A1's English replies are PARTIAL. Gate 2 is therefore scored
as **containment in the interval spanned by exp8's own two judges** (passes) with the stricter single-judge criterion
recorded per cell (does not pass); this is written up in `results/deviations.json` rather than smoothed over.

## Layout

```
method.py               GPU pipeline. --stage {smoke, partA, screen, partA+screen, confirm, s5x}; resumable per cell.
                        Gates 0/1/2/4, closed-form energies, matched-energy solving, write-space random controls,
                        energy-matched PC controls, anchors (L20 c1/c2, all-48 activation, trial-96 LoRA W0/W3/W4,
                        Heretic-exact K96g), per-cell FLORES ΔNLL + Dolly KL, S7 utility.
interventions.py        Hook harness COPIED from exp8 and extended with per-layer/per-module weight edits
                        (set_weight_edit_layerwise), dequantised closed-form edit energy (module_energy).
common.py               Paths, pins, SHA-checked frozen-split loading, item-set construction + T0 assertions.
heretic_params.py       exp7's verbatim Heretic parameter block (kernel_weights = Model.abliterate()'s schedule).
alib.py                 Analysis library: judge-label join, 4-way classes, GlotLID line-level LID, item bootstraps,
                        the Part-A index and the frozen index-based predictor.
judge/local_judge.py    The partial-aware scorer (Qwen3-14B, exp4 rubric verbatim). --refail re-judges unparsed replies.
judge/certify.py        κ within EDITED checkpoints, from labels on disk and from this run's gpt-4.1 subsample.
judge/api_judge.py      The one bought gpt-4.1 certification subsample (cost-logged, hard stop at $8).
freeze.py               Computes the DEV index, writes frozen_predictions.json + redundancy_index.json, hashes both
                        into results/FREEZE.sha256. Refuses to run if confirmation generations already exist.
select_s5x.py           Applies the frozen s5x_rule (+ a declared tie-break) to pick ≤ 2 cells for the single touch.
analysis.py             Every reported number: rates with item-cluster bootstraps, P1/P2/P3, matched efficacy and
                        matched collateral, the exploratory band-identity analysis, confirmation, placebos, Holm.
rederive.py             GATE 6: independent stdlib+numpy re-derivation of every headline number + the placebos.
figures.py              fig1 coverage curves · fig2 matched-energy pairs · fig3 index prediction · fig4 write mass ·
                        fig5 coverage×strength heatmap · fig6 collateral vs residual.
report_tables.py        results/report_tables.md (all tables).
make_deviations.py      results/deviations.json (every departure from the plan, with its evidence file).
build_output.py         method_out.json in the exp_gen_sol_out schema.
run_chain.sh            The exact post-generation sequence that was run.
reproducibility.md      Pins, the step-by-step sequence with timings, and the table of numbers to expect on a re-run.
configs/                partA_sets.json, matched_groups.json, k96_kernel.json, explore_band_identity.json, s5x_cells.json
results/gens/           every generation, one JSON per cell
results/cells/          per-cell metadata: coefficient profile, energy, FLORES/KL, timings (+ __draws, __utility)
results/                judge_local.jsonl, judge_api.jsonl, judge_certification.json, redundancy_index.json,
                        frozen_predictions.json, FREEZE.sha256, cells.parquet/.csv, per_item.parquet,
                        analysis_summary.json, report_tables.md, audit.json, deviations.json, api_costs.jsonl,
                        gate0_pins.json, gate1_unit_tests.json, gate2_anchor_check.json, timing_model.json
```

Absolute workspace path (later rounds read the kept artifacts here):
`/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/gen_art/gen_art_experiment_9`

## How to run

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r pyproject.toml   # torch cu128 wheels come from the extra index
.venv/bin/python method.py --stage smoke                     # gates 0/1/2/4 + timing model (~4 min + load)
.venv/bin/python method.py --stage partA+screen              # 104 cells (~65 min on one RTX 4090)
bash run_chain.sh                                            # judge → certify → freeze → confirm → analyse → audit
```

One RTX 4090 (24 GB), ~3 h wall clock end to end. Generation and judging never co-reside: all generation finishes, the
Gemma model is freed, then the judge loads. Batch sizes halve automatically on OOM.

Cost: **$0.70** of OpenRouter spend (the single gpt-4.1 certification subsample), against a $10 cap.

## Limitations

- **One model, one locale, one Heretic seed, NF4 throughout.** The band-identity finding is a within-model claim with
  n = 1 checkpoint; absolute levels are NF4-specific. GaMS3 is quoted from iteration 2 (EN 0.57 / SL 0.50 under the same
  English ablation) as a two-point contrast, **not** re-measured here, and no difference may be attributed to a
  particular training stage.
- **The index threshold is under-resolved.** Part A's k-grid of 4 means the index can only move in steps of 4, and a
  one-step gap is inside its own permutation null; the cross-language claim rests on the curve separation instead. A
  finer grid (step 1–2) would cost ~4× the Part-A generations and is the cheapest real improvement available.
- **The pre-registered P1/P2 tests fail.** They are reported as failures with their falsifier; the band-identity result
  that explains the panel is **exploratory**, declared and hashed before its outcome was read, and it does not enter the
  Holm family or rescue P1/P2. It needs replication on a second model before it is asserted beyond this checkpoint.
- The plan's "broad" arms (strided S2/S4) confound breadth with *spreading through bands that do nothing*. That is
  precisely what makes the negative result interpretable, but it also means P2 never tested breadth in its strongest
  form.
- `n = 41` screen and 70 confirmation items per language per cell, so sub-0.10 differences in a single cell are not
  resolvable; the cell-level regression has 46 cells (minimum detectable ΔR² = 0.071, below the 0.10 bar, so P1 is
  adequately powered to reject).
- The weight edit orthogonalises `o_proj`/`down_proj` **outputs**; Gemma-3 applies `post_attention_layernorm` /
  `post_feedforward_layernorm` *after* these projections, so the operator does not guarantee the direction is absent
  from the residual write — the same limitation Heretic's own weight edit has on Gemma-3.
- Heretic's norm-preserving rank-3 LoRA is not reproduced per cell (it would add a second operator knob to the
  coverage × strength design), so the factorial speaks to the operator *family*; the tie to the real edit is the
  trial-96 adapter anchors (W0/W3/W4) and the Heretic-exact kernel cell.
- 128 new tokens per generation, so almost every reply is truncated; this is held constant across cells.
- Every Slovene number carries the pending-native-review caveat.

## Restoring removed files

`.aii/manifest.yaml` marks four paths `delete`; all four are caches or a rebuildable environment, and **nothing any
later step reads is deleted**. Each one comes back with the command below.

| deleted path | why | command that restores it |
|---|---|---|
| `.venv/` | regenerable Python environment (11 GB) | `uv venv .venv --python=3.12 && uv pip install --python .venv/bin/python -r pyproject.toml` |
| `__pycache__/` | regenerable bytecode cache | recreated automatically on the next import of `common.py` / `alib.py` / `interventions.py` |
| `judge/__pycache__/` | regenerable bytecode cache | recreated automatically on the next import of `judge/local_judge.py` |
| `results/ref_dolly_topk.npz` | regenerable 38 MB cache: the top-512 reference distribution behind the harmless-KL column | `rm -f results/ref_dolly_topk.npz && .venv/bin/python method.py --stage smoke` |

```bash
# 1. the Python environment (exact pinned versions, == results/env_freeze.txt)
uv venv .venv --python=3.12 && uv pip install --python .venv/bin/python -r pyproject.toml

# 2. the harmless-KL reference cache (rebuilt from the pinned model; no network beyond the HF snapshot)
rm -f results/ref_dolly_topk.npz && .venv/bin/python method.py --stage smoke

# 3. __pycache__/ and judge/__pycache__/ need no action - Python recreates them on import
```

Everything else is **kept**: all 27,784 generations (`results/gens/`, 122 JSON files), every per-cell record
(`results/cells/`), both judge caches, the frozen index and prediction files with their hashes, every analysis table,
the audit files and all six figures. They are text or JSON and are never removed.

## Model weights and read-only inputs

Model weights live in this run's shared HF cache (`$HF_HUB_CACHE`) and are re-downloadable:

```bash
hf download google/gemma-3-12b-it     --revision 96b6f1eccf38110c56df3a15bffe176da04bfd80   # ~23 GB, gated
hf download Qwen/Qwen3-14B            --revision 40c069824f4251a91eefaf281ebe4c544efd3e18   # ~28 GB, the scorer
hf download cis-lmu/glotlid model.bin --revision 85cd6716494360367b75f642b5bc78667605d0b4   # language ID
hf download meta-llama/Llama-Guard-3-8B --revision 7327bd9f6efbbe6101dc6cc4736302b3cbb6e425 # guard-ASR arm only
```

The trial-96 LoRA adapter is **read, never modified**, from
`/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1/gen_art/gen_art_experiment_1/adapters/gemma_selected_path2`
(`adapter_model.safetensors` SHA-256 `d219c084…`, verified at load). The frozen per-layer directions are read from
`/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_8/directions/gemma_all_layers.npz`,
and every `S*` data split from
`/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1/gen_art/gen_art_dataset_1` (SHA-256 verified at load).
