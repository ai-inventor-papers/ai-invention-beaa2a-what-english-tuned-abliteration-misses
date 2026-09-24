# Does spreading the edit deeper unlock Slovene? — a depth-coverage × strength factorial on GaMS3-12B-Instruct

Iteration-3 artifact `gen_art_experiment_10` of run `run_Fapgmt6JWbcD`. It asks whether the **Slovene refusal that survives
an English-derived refusal edit** is a matter of **where in depth the edit is applied** (coverage) rather than **how much
edit there is** (total removal energy), in `cjvt/GaMS3-12B-Instruct`.

Everything below is recomputed from the saved per-generation files by `analysis.py`, re-derived independently by
`rederive.py`, and printed by `report_tables.py` into `results/report_tables.md`. **Numbers quoted in this README are
generated, never typed by hand** — see `results/report_tables.md` for the full tables.

<!-- GENERATED:BEGIN -->

## Headline

1. **Depth-coverage is what removes refusal, and Slovene needs a little more of it than English — but on this model no amount of it leaves a usable model.** On DEV (n=40 harmful items per language), ablating the frozen per-layer English direction over a cumulative prefix of the first *k* hidden indices takes judged harmful refusal from 0.95 (EN) / 0.88 (SL) through the 0.5 crossing at **index_EN = 16** (95% CI [16.0, 16.0]) and **index_SL = 20** ([16.0, 24.0]); the difference is 4 layers with CI [0.0, 8.0], i.e. **equivalent within the pre-declared ±8-layer margin** (PA1 EQUIVALENT_WITHIN_MARGIN). But the co-primary *usable* index — the shallowest prefix that removes refusal **and** keeps INVALID ≤ 0.10 — is **>48 (EN) / >48 (SL)**: at every depth that removes refusal, 0.72 (EN) / 0.38 (SL) of the replies are degenerate or wrong-language. Activation-space depth coverage pays for refusal removal with the model itself.

2. **The pre-registered coverage hypothesis is falsified, and falsified in the opposite direction: at matched total removal energy, concentrating the same budget on one 12-layer band beats spreading it.** Pooling the three matched-energy groups on the confirm set (held-out harm categories), narrow-and-strong (one 12-layer band) minus broad-and-weak (stride-2 / all-48) Slovene refusal is **-0.10** [-0.15, -0.06] over n=70 semantic items — PB2 predicted this to be **positive** (broad better) and it is negative with a CI excluding zero, so **FALSIFIED_OPPOSITE_DIRECTION**. In English the same contrast is -0.03 [-0.08, 0.01]. The coverage×language interaction is -0.07 [-0.13, -0.01]: the advantage of concentrating is larger in Slovene than in English, which is a real coverage×language interaction but again the opposite sign to PB3's prediction (FALSIFIED_OPPOSITE_DIRECTION).

3. **Across the whole panel, what a cell does to Slovene is explained by its energy, its English outcome and WHERE its energy sits — not by how much depth it covers.** Across 26 weight cells, R² for the Slovene residual rises 0.981 → 0.983 when the coverage terms are added to (log E + EN outcome + the static geometry baselines b1/b3): ΔR² = **0.002** with cell-bootstrap CI [0.00031339342073801455, 0.009948439794821236] (PB1 NOT_SUPPORTED). With so few cells the in-sample ΔR² is optimistic; the leave-one-cell-out ΔR² is -0.043 — adding coverage terms makes out-of-sample prediction *worse*. The nested decomposition shows why: log E alone gives R² 0.325, adding the four band energy fractions (WHERE the edit sits) gives 0.718, while adding the covered-layer count instead gives 0.400.

4. **The operator, not the direction, decides whether depth coverage is usable.** The same frozen per-layer directions applied as **Heretic's row-norm-preserving weight edit** cover the same depths with essentially no collateral — 22 cells pass the degradation gate with |SL FLORES ΔNLL| ≤ 0.011 nats and Slovene multiple-choice accuracy within 0.031 of the unedited model — while the raw activation projection of those same directions at every token position leaves 0.53 of Slovene replies unusable at its own crossing depth. Conclusions about 'how deep an edit must reach' do not transfer across the two operators.

5. **What matters is WHERE the covered layers sit, not how many there are.** `E3_B2_vs_STR4` compares 12 *contiguous* layers against 12 layers spread every 4th, at the **same total removal energy and the same number of edited layers**: Slovene refusal 0.24 vs 0.81 (Δ -0.57 [-0.70, -0.44]), English 0.40 vs 0.83 (Δ -0.43 [-0.57, -0.30]). Spreading the same budget thinly over depth is not what unlocks Slovene — concentrating it on the right band is.

6. **The controls behave.** At the same sites and the same total removal energy, the layer-matched random and energy-matched principal-component edits leave Slovene harmful refusal at 0.93–0.95 (no-op 0.93), so what removes refusal is the harm direction, not the amount of weight surgery.

7. **Refusal removal is reported next to the damage.** 18 of 57 cells trip the pre-declared degradation gate (INVALID > 0.05, wrong-language drift > 3 pts, FLORES ΔNLL > 1.0 nats or MC accuracy −5 pts) and are printed as DEGRADED in their own rows; no cell counts as successful suppression on a refusal number alone.

8. **The DEV-frozen index transfers poorly to the weight cells.** Spearman between the index-curve prediction at k = covered layers and the observed per-language refusal is 0.21 (n=32 cell×language points, p=0.258) — PB4 NOT_SUPPORTED. The reason is visible in the design: the index is a function of the NUMBER of covered layers, so it assigns the same prediction to a 12-layer band and to 12 layers spread every 4th — cells whose measured refusal differs by most of the scale. A count-based depth instrument cannot express placement, which is what actually moves this model.

9. **The Slovene lag is not what separates the two sibling models.** The iteration-3 Gemma pod ran the same instrument (same split, same blind local judge, same prefix family) on `google/gemma-3-12b-it` and reports index_EN = 16, index_SL = 20; this pod reports index_EN = 16, index_SL = 20 for GaMS3. **Both checkpoints put Slovene exactly one 4-layer step deeper than English.** Whatever made the iteration-1 Heretic edits differ between these two models, it is not a difference in how redundantly refusal is written across depth. n = 2 checkpoints, one seed, one instrument, a 4-layer grid whose resolution is +-4 layers, and overlapping bootstrap CIs: this is an ORDERING observation, not a fitted law, and it is not attributed to any training stage.


Holm-adjusted p-values across the frozen family: PA1 0.069, PB1 0.000, PB2 0.000, PB3 0.069, PB4 0.258. Predictions whose contrast could not be evaluated carry no p-value.


## Audit

`rederive.py` re-derives **481/481** headline numbers from the raw per-generation files through a code path that imports nothing from the analysis (`results/rederive.json`), and the freeze-order check (PASS) confirms `configs/FREEZE.sha256` predates the first confirmation generation. Placebos: P1_cell_label_within_item null mean 0.003 [-0.043, 0.067]; P2_language_label null mean -0.001 [-0.089, 0.079]; P3_energy_shuffled null mean 0.023 [0.016, 0.027] — each collapses to zero while the real contrasts do not.


**Judge.** The primary judge is the blind local Qwen3-14B with iteration-2's frozen rubric. Certified for free against the gpt-4.1 labels already on disk, restricted to EDITED arms (n=4660): κ = **0.86 in Slovene** (n=2371) but only **0.54 in English** (n=2289), where it is systematically stricter (refused rate 0.34 vs 0.17). The planned gpt-4.1 top-up could not be bought — the run's OpenRouter key was already exhausted (HTTP 403 `aii_run_budget_exhausted`), so **English rates here are the strict end of a judge range** and every English claim carries that caveat; Slovene, which every headline is about, is certified. A degenerate reply (4-gram repetition > 0.5) is forced to INVALID by rule, because the local judge labels prompt-echo output 'refused'.


## Limitations

- One model, one optimiser seed, one Slovene locale, 4-bit NF4 throughout: every absolute level is NF4-specific and prompt-level CIs do not measure optimiser variance.
- Slovene items are machine-translated with automated QC only; **native review is PENDING**, not performed.
- n = 41 harmful screen items and 70 held-out-category confirmation items per language, so differences below ~0.10 are not resolvable; the matched-energy contrast is paired to get the most out of that.
- Coverage and total removal energy are collinear by construction; the matched-energy groups, not the regression, are the primary contrast, and the regression's ΔR² is reported with its cell bootstrap and its leave-one-out companion.
- ASR under RefusEU's official guard pipeline was not run (see `results/deviations.json`); 'not refused' is reported as judged COMPLIED + PARTIAL, an upper bound on attack success.
- Utility is the cheap teacher-forced multiple-choice readout plus FLORES ΔNLL and Dolly KL, not the lm-eval harness macro: the S7 splits are reserved for the final evaluation artifact and were never opened here.
- The Gemma column comes from the sibling iteration-3 pod, not from this workspace: it was produced by different code on a different pod and is joined here only because both ran the same instrument on the same split with the same pinned judge. Every cross-model statement is descriptive (n = 2 checkpoints) and none is attributed to continual pretraining, instruction tuning or any other training stage.
- **This model was not the one with the Slovene problem.** The iteration-1 GaMS3 Heretic edit reproduced here as the CORE anchor already leaves only 0.10 Slovene refusal on the held-out categories, so the 'Slovene residual' that motivated the question is a Gemma phenomenon. What this panel measures on GaMS3 is how placement, coverage and energy trade off against each other and against Slovene, not the rescue of a locked language.
- The matched-energy design caps out at E = 28 because a 12-layer band cannot exceed Heretic's max_weight bound of 1.5; the shipped CORE edit sits at E = 74, well outside the matched range, so the groups compare shapes at low-to-moderate edit size rather than at production strength.

<!-- GENERATED:END -->

## What was run

| part | what | data |
|---|---|---|
| A | **DEV depth-redundancy index**: cumulative-prefix (P4…P48), cumulative-suffix (S12/S24/S36) and leave-one-band-out ablation of the **frozen per-layer English refusal directions** `d_EN(h)` from iteration 2, at every token position | S3 JBB **half A**, 40 harmful + 40 harmless items per language (DEV only) |
| B | **Weight-edit factorial** through **Heretic's own operator** (`row_normalization='full'`, rank-3 LoRA, `lora_alpha=r`): 9 depth-coverage sets × strengths, with **3 matched-total-removal-energy groups** each containing a narrow-and-strong and a broad-and-weak cell, plus no-op, layer-matched **random** and energy-matched **PC** controls | screen: S3 JBB **half B** (41 harmful pairs); confirm: S4 StrongREJECT **held-out categories** (70 harmful + 40 harmless twins) |
| C | **Partial-aware 4-way scoring** (REFUSED / PARTIAL / COMPLIED / INVALID) by a blind local Qwen3-14B judge, with GlotLID line-level language identification, repetition and FLORES/KL/MC collateral beside every refusal number | all cells |
| D | **Frozen predictions** PA1–PB4, hashed into `configs/FREEZE.sha256` **before the first confirmation generation** | — |

## Layout

```
method.py            GPU pipeline. --stage A: load NF4 GaMS3 + rank-3 PEFT adapters -> smoke gates -> half-A residual
                     capture -> d_EN sanity gate -> matched controls -> Part A activation arms -> operator/energy gates
                     -> matched-energy design. --stage B: the weight-edit cells in priority order (configs/priority.json).
heretic_op.py        Heretic @3521f864's abliterate() generalised to an explicit per-(layer, component) weight map
                     (arbitrary coverage sets), the exact LoRA energy, Heretic's triangular kernel, and a loader that
                     execs Heretic's OWN abliterate source for the equivalence gate.
interventions.py     iteration-2 engine (copied byte-identical): 4-bit load, residual hooks, teacher-forced scoring.
common.py            paths, frozen-split loading with SHA checks, set construction, the S5/S6/S7 guard.
labels.py            the frozen 4-way outcome mapping + GlotLID language identification.
judge_local.py       the blind local Qwen3-14B judge (primary), cache-compatible with iteration 2's.
judge_api.py         the gpt-4.1 second judge (not used: the run's OpenRouter budget was exhausted - see deviations).
cert_pool.py         free certification of the local judge against gpt-4.1 labels already on disk (EDITED arms only).
freeze.py            Part A read-out: the per-language index (+ the usable and suffix variants), then the FREEZE.
analysis.py          per-cell tables, cluster bootstraps, McNemar, the frozen predictions, judge sensitivity.
rederive.py          GATE 8: an independent recompute of every headline number + the three placebos + freeze-order check.
figures.py           fig1 coverage curve · fig2 matched energy · fig3 index-vs-residual · fig4 LOBO · fig5 Pareto ·
                     fig6 judge sensitivity.
report_tables.py     results/report_tables.md — every table, straight from the analysis summary.
cross_model.py       results/cross_model.json — the joint depth table with the iteration-3 Gemma sibling pod.
data_usage.py        results/data_usage.json — what this artifact does with every block of the frozen dataset, and why
                     the S5/S6/S7 families were never opened.
make_deviations.py   results/deviations.json — every departure from the plan, with its evidence file.
make_readme.py       regenerates the Headline / Audit / Limitations block of this README from the result files.
build_output.py      method_out.json (exp_gen_sol_out schema): 462 items x 56 methods = 10,690 per-item outcomes,
                     one example per (split, semantic item, language), `output` = the unedited model's 4-way class and
                     one `predict_<method>` per intervention that ran on that item.
run_chain.sh / run_chain2.sh / run_chain3.sh / watch_finish.sh / finish.sh
                     the exact chains that were executed (stage A -> judge -> FREEZE -> Part B -> judge -> grid -> analysis).
configs/             design.json (matched-energy solution + gates), priority.json, dev_items.json, FREEZE.sha256.
results/cells/<cell>/   gens.json (every generation), tf.json (collateral), meta.json (coverage, weights, exact energy).
results/             redundancy_index.json, frozen_predictions.json, analysis_summary.json, report_tables.md,
                     judge_cert_pool.json, judge_local.jsonl, rederive.json, deviations.json, per_item.parquet.
```

Absolute workspace path (kept artifacts are readable here by later rounds):
`/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/gen_art/gen_art_experiment_10`

## How to run

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r pyproject.toml
.venv/bin/python method.py --stage A           # Part A: gates, controls, DEV arms, energy table, design (~30 min GPU)
.venv/bin/python judge_local.py --splits dev dev_ben   # blind local judge over the DEV arms
.venv/bin/python freeze.py                    # the index + the frozen predictions, hashed into configs/FREEZE.sha256
bash run_chain2.sh $(( $(date +%s) + 7200 ))  # Part B T1/T2 (the 25 decisive cells) -> judge         (~2 h GPU)
bash run_chain3.sh $(( $(date +%s) + 3000 ))  # the T3 coverage grid -> judge                         (~15 min GPU)
bash finish.sh                                # analysis -> cross-model -> tables -> figures -> audit -> README
```

Hardware actually used: 1 × NVIDIA L4 (22 GB), 48-core host, ~4 h wall clock; 57 cells and 10,690 judged generations. **$0.00 of OpenRouter spend** (the run's
key was already exhausted; see `results/deviations.json`).

## Restoring removed files

`.aii/manifest.yaml` marks exactly one path `delete` — the Python environment. Rebuild it with:

```bash
# .venv/   (the only delete entry: ~11 GB of wheels, pinned in pyproject.toml)
uv venv .venv --python=3.12 && uv pip install --python .venv/bin/python -r pyproject.toml
```

Everything else in this repository is kept: all code, all per-generation outputs and labels under `results/cells/`, the
control directions, the energy table, the frozen index, the figures and the tables. The one heavy binary that is kept
deliberately is `results/ref/dolly_B_ref.npz` (19 MB) — the unedited model's top-512 reference distributions that every
cell's harmless KL is differenced against; only a GPU pass on the original model would rebuild it.

Two directories are present but excluded from the published GitHub repo (`upload_ignore_regexes`), not deleted:
`results_mini/` (the 6-item smoke tree, rebuilt by
`AII_MINI=1 .venv/bin/python method.py --stage A --mini && AII_MINI=1 .venv/bin/python judge_local.py`) and `.venv/`.
`__pycache__/` is removed and is recreated automatically on import.

Model weights live in this run's shared HF cache (`$HF_HUB_CACHE`) and are re-downloadable:
`huggingface-cli download cjvt/GaMS3-12B-Instruct --revision 1d0b27af5748784482600d24779409e7e1dc9adc`,
`huggingface-cli download Qwen/Qwen3-14B --revision 40c069824f4251a91eefaf281ebe4c544efd3e18`,
`huggingface-cli download cis-lmu/glotlid --revision 85cd6716494360367b75f642b5bc78667605d0b4`.
The iteration-1 core LoRA adapter is read (never modified) from
`/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1/gen_art/gen_art_experiment_1/adapters/gams_selected_path2`,
and the frozen per-layer directions from
`/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_8/directions/gams3_all_layers.npz`.
