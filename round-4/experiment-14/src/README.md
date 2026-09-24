# Where a refusal edit must land — a causal write profile for `cjvt/GaMS3-12B-Instruct`

Iteration-4 artifact `gen_art_experiment_14` of run `run_Fapgmt6JWbcD` (slot 2: the boundary-and-confound half).

An English-derived Heretic abliteration removes English refusal from this checkpoint and leaves a different amount of
Slovene refusal depending on **where in depth the edit's energy lands**. This pod asks whether that "where" can be
turned into an *instrument*: measure, on development items only, a **per-language causal write profile** `e_L(h)` — the
judged drop in harmful refusal caused by applying Heretic's own operator at **one** decoder layer with the frozen
English refusal direction `d_EN(h)` — freeze it, and use it to predict, out of sample, which matched-energy edit wins
on **held-out harm categories**:

```
O_L(edit) = sum_h e_L(h) * g(h) / ||g||_2        g(h) = closed-form per-layer removal energy of the edit
```

Everything is frozen before the confirmation generations exist (`configs/frozen_predictions.json`, hashed into
`configs/FREEZE.sha256`; `method.py --stage confirm` refuses to start without it), every outcome is a blind 4-way judged
class (REFUSED / PARTIAL / COMPLIED / INVALID), every headline is re-derived by an independent code path
(`rederive.py`), and the instrument is raced against the cheap predictors that beat every geometric instrument in this
run's iteration 3.

<!-- GENERATED:BEGIN -->

## Headline

1. **The write profile is sharp, and it is not where the sibling checkpoint's is.** Single-layer Heretic-operator edits at c = 2.5 on 40 DEV harmful items per language put the causal peak at hidden index **27 (EN)** and **27 (SL)**, with band mass EN 1-12 0.00, 13-24 1.05, 25-36 1.50, 37-48 0.27 and SL 1-12 0.02, 13-24 0.55, 25-36 0.57, 37-48 0.05. The DEV-named band is **25-36**, not the 13-24 that the sibling panel reported - but the Slovene profile's split-half reliability is only 0.312 (EN 0.812), so by the pre-registered rule the Slovene profile is **declared unreliable at this item count and its argmax prediction is exploratory**, recorded before the freeze.

2. **Out of sample, the overlap statistic orders the matched-energy cells as predicted.** Over 20 confirmation cells that the profile never saw (70 held-out-category StrongREJECT pairs each, 12 edited layers each, energy matched), Spearman(O_SL, surviving Slovene refusal) = **-0.903** (CI [-0.928, -0.857], permutation p 0.000); the instrument predicts REMOVAL, so its expected sign is negative and the removal-aligned statistic is 0.903. Pre-registered verdict: **PARTIAL**.

3. **Against the honest competitors it buys something.** With log total removal energy alone the Slovene outcome is at R^2 0.088 (leave-one-cell-out -0.125); adding O gives dR^2 0.580 with LOO dR^2 0.594. Adding n_layers instead: dR^2 0.000 (LOO -0.000). Adding span instead: dR^2 0.028 (LOO -0.072). Adding O_cos instead: dR^2 0.702 (LOO 0.834). Adding O_band4 instead: dR^2 0.718 (LOO 0.845).

3b. **But the expensive instrument does not earn its cost.** The same overlap computed from a FOUR-number band profile (`O_band4`) and the purely geometric EN/SL direction-cosine overlap (`O_cos`) - neither of which needs 48 judged single-layer measurements - reach LOO dR^2 0.845 and 0.834 against O's 0.594, and the same cell's ENGLISH outcome predicts the Slovene one at rho 0.945 - statistically indistinguishable from O. What the 48-layer profile establishes is that **placement matters**; it is not the cheapest way to measure placement.

4. **The cheap predictors are the bar, and they are reported beside it.** logE rho -0.384 (|rho| difference vs O 0.519 [+0.425, +0.617]); n_layers rho n/a (|rho| difference vs O n/a n/a); span rho -0.039 (|rho| difference vs O 0.864 [+0.785, +0.914]); mean_depth rho -0.328 (|rho| difference vs O 0.576 [+0.516, +0.661]); O_cos rho -0.879 (|rho| difference vs O 0.024 [+0.005, +0.074]); O_sl_band4 rho -0.860 (|rho| difference vs O 0.044 [+0.028, +0.100]); en_outcome rho 0.945 (|rho| difference vs O -0.042 [-0.079, +0.009]).

5. **The band check.** At E2 the matched-energy bands rank B2 0.50, B3 0.59, B4 0.93, B1 0.97; the DEV-named band is 25-36 and the observed winner is 13-24 -> **NAMED_AND_LOST**. At E3 the matched-energy bands rank B2 0.30, B3 0.53, B4 0.94, B1 0.97; the DEV-named band is 25-36 and the observed winner is 13-24 -> **NAMED_AND_LOST**.

6. **Placement and achieved dose, separated by construction.** placement_at_fixed_E_high (A1 vs A3): dSL -0.029 [-0.129, +0.071] (McNemar p 0.774); placement_at_fixed_E_low (A4 vs A2): dSL 0.000 [-0.086, +0.086] (McNemar p 1.000); dose_at_fixed_O_ship (A1 vs A4): dSL -0.186 [-0.286, -0.086] (McNemar p 0.001); dose_at_fixed_O_swap (A3 vs A2): dSL -0.157 [-0.243, -0.071] (McNemar p 0.003). A1 and A4 share their placement profile and differ only in total energy; A2 and A3 likewise; A1 and A3 share energy and differ in placement, as do A2 and A4.

6b. **Both accounts hold, in their own stratum.** At fixed dose the overlap still orders the cells (E2|sl rho -0.967 over 10 cells; E3|sl rho -0.948 over 10 cells), and at fixed placement doubling the dose from E = 13.9 to 27.8 lowers Slovene strict refusal by 0.114 on average over the 10 matched layer sets. Placement and dose are both real; neither is an artefact of the other.

7. **Controls.** At the same 12 layers and the same total removal energy, X_PC0_E3 SL strict 0.943 (d vs no-op -0.014); X_PC1_E3 SL strict 0.986 (d vs no-op 0.029); X_PC2_E3 SL strict 0.943 (d vs no-op -0.014); X_RND0_E3 SL strict 0.943 (d vs no-op -0.014); X_RND1_E3 SL strict 0.957 (d vs no-op 0.000); X_RND2_E3 SL strict 0.971 (d vs no-op 0.014). All null: **True** (no-op SL strict 0.957).

8. **The outcome definition, not the placement, decides which band 'wins'.** On the same generations the 33-substring opener rule and the judged 4-way class rank the four matched-energy bands differently: opener rule B3 > B2 > B4 > B1, judged STRICT B2 > B3 > B4 > B1, judged BROAD B3 > B2 > B4 > B1. The mean Slovene gap between the judged strict rate and the opener-rule rate over the confirmation cells is 0.182 (max 0.514), and 11/190 cell pairs change order between the two metrics. The rank correlation of O with the outcome is nevertheless the same under both (-0.903 vs -0.903).

9. **Post-freeze exploratory (declared, never in the pre-registered family): the two production kernels are indistinguishable once their dose is matched.** at E2 the shipped kernel and the sibling checkpoint's kernel at the same total removal energy leave Slovene strict refusal at 0.471 and 0.400 (d 0.071 [-0.029, +0.171]); at E3 the shipped kernel and the sibling checkpoint's kernel at the same total removal energy leave Slovene strict refusal at 0.314 and 0.286 (d 0.029 [-0.057, +0.114]). Both production kernels spread their mass over the layers the profile calls effective, so the 'swap' contrast that motivated this pod is a dose contrast, not a placement contrast.

10. **The screen, and the mis-specification arm that undercuts it.** On the 57-cell iteration-3 GaMS3 panel O correlates -0.278 with surviving Slovene refusal (33 cells). Applying the SAME GaMS3 profile to 50 cells of the sibling checkpoint gives -0.442 - no worse, so the profile is not demonstrably checkpoint-specific on these screens. Both screens are weak for a reason the confirmation panel removes by design: those cells vary in total removal energy by an order of magnitude, and O is scale-invariant, so on an unmatched panel dose swamps placement. Placement is visible only at matched energy.


## Audit

`rederive.py` re-derives **352/352** headline numbers from the raw per-generation files through a code path that imports nothing from the analysis; freeze order {'freeze_sha_matches': True, 'freeze_precedes_every_confirmation_file': True, 'n_confirmation_files': 36}. In that same independent path the primary statistic is placebo-tested: the real Spearman is -0.903, the cell-permutation null 0.003 (p 0.000) and the energy-profile-shuffled null -0.017 (p 0.000) - both collapse.

Third label channel (free, weak, and the only one available on THESE generations): the iteration-3 partial-aware refusal classifier agrees with the blind local judge on 0.837 of Slovene confirmation items (kappa 0.664) and 0.697 of English ones (kappa 0.426) - but the two channels' CELL-LEVEL rates, which is what every claim here rests on, correlate at Spearman 0.975 (SL) and 0.954 (EN) over 36 cells. The panel's ordering does not depend on the scorer.

Freeze guard, tested adversarially on a scratch copy (`gate_freeze_test.py`): the confirmation entry point raises when `FREEZE.sha256` is missing and when one byte of `frozen_predictions.json` is changed, and runs only on the intact freeze - guard_works = **True**.

Placebos: P1_cell_label_within_item 0.015 [-0.358, +0.482]; P2_cross_language_profile -0.843 n/a; P3_energy_profile_shuffled 0.019 [-0.379, +0.386] - against a real statistic of -0.903.


**Judge.** Primary scorer: blind local Qwen3-14B with the frozen iteration-2 rubric. Reference judge openai/gpt-4.1|batch10. The stratified 600-item buy this pod had budgeted could NOT be made: the platform's shared OpenRouter key hit its daily limit mid-run (HTTP error `aii_openrouter_key_limit`), so $0.00 was spent and certification fell back to - FALLBACK: gpt-4.1 labels already on disk for GaMS3 EDITED arms (iteration-2 gen_art_experiment_8 cells, NOT this pod's own generations); the OpenRouter key hit the platform's daily limit, so $0.00 was spent and no new label was bought. Measured on harmful-item rows: kappa (refused vs not) sl 0.830 (n=59), en 0.721 (n=53). Confirmatory languages: ['sl']; JUDGE_SENSITIVE: ['en'].


Deviations from the plan, each with its evidence file: **10** (see `results/deviations.json`).


## Limitations

- One checkpoint, one optimiser seed, NF4 throughout: absolute levels are NF4-specific and prompt-level CIs do not measure optimiser run-to-run variance.
- 20 confirmation cells: a rank statistic over cells at this n cannot resolve differences below roughly 0.4 in Spearman, and the paper says so rather than reading small differences.
- Slovene items are machine-translated with automated QC only; native review is PENDING.
- The Slovene write profile's split-half reliability is below the pre-registered 0.5, so every Slovene profile-derived claim is exploratory; the English profile is reliable but English is judge-blocked.
- Attack success is reported as judged COMPLIED (+PARTIAL), an upper bound: the RefusEU official guard pipeline was not run here (see `results/deviations.json`).
- The sibling-checkpoint columns are read from the iteration-3 panel's files, never re-measured here; every cross-checkpoint statement is descriptive (n = 2 checkpoints) and none is attributed to a training stage.

<!-- GENERATED:END -->

## What was run

| part | what | data |
|---|---|---|
| 0 | **Gates**: pins, input inventory with SHA256, operator equivalence against Heretic's own `abliterate()` source, the `||BA||_F^2` energy identity, the `k^2` energy-rescaling law, the shipped adapter rebuilt from its Optuna journal row, anchor reproduction against the iteration-3 panel's stored generations, baseline-refusal sanity | S3 JBB half A/B |
| 1 | **The DEV causal write profile** `e_EN(h)`, `e_SL(h)`: no-op plus **48 single-layer weight edits**, judged on 40 DEV harmful items per language, plus a pre-freeze strength pilot (c = 1.0 / 1.5 / 2.5) and FLORES collateral spot checks | S3 JBB **half A**, DEV only |
| 2 | **The freeze**: the profile, the overlap formula, the 28 confirmation cells with their closed-form matched energies, the predicted winning band, the predicted O of every cell, the competing predictors and the outcome ladder | — |
| 3 | **The screen** (zero GPU): O on 57 iteration-3 GaMS3 cells and, as a **mis-specification arm**, on 122 sibling-checkpoint (`gemma-3-12b-it`) cells scored with the *GaMS3* profile | iteration-3 panels |
| 4 | **The confirmation panel**: 20 cells, each exactly 12 edited layers, energy matched in closed form at E = 13.9 and 27.8 — four contiguous bands, three stride-4 phase shifts, three hybrid high-/low-effect mixes — plus a no-op, three layer-matched **random** draws and three energy-matched **PC** draws | S4 StrongREJECT **held-out categories** (70 harmful + 40 harmless twins), EN + SL |
| 5 | **The placement/dose dissociation**: A1 the shipped GaMS3 edit, A2 the sibling checkpoint's kernel as-is, A3 the sibling kernel rescaled to A1's energy, A4 the shipped edit rescaled to A2's energy — so O and E are crossed by construction; plus a declared **post-freeze exploratory** pair at E3/E2 where the ladder is not at the refusal floor | same |
| 6 | **Judge certification bought inside this pod**: a stratified `gpt-4.1` subsample of this pod's own edited generations, kappa within edited arms per language, Se/Sp, Rogan-Gladen | same |
| 7 | **Audit**: independent re-derivation, three placebos, the freeze-order check, Holm across the pre-registered family | — |

## Layout

```
method.py               GPU pipeline. --stage smoke (gates, controls, energy table, timing model)
                        --stage profile (the strength pilot + the 48 single-layer write probes)
                        --stage reuse   (re-label, never regenerate, the iteration-3 anchors)
                        --stage confirm (the frozen panel; refuses to run without configs/FREEZE.sha256)
heretic_op.py           Heretic @3521f864's abliterate() generalised to an explicit per-(layer, component) weight map,
                        the exact LoRA removal energy, Heretic's triangular kernel, and a loader that executes
                        Heretic's OWN abliterate source for the equivalence gate.
interventions.py        the iteration-2 engine (4-bit load, residual hooks, teacher-forced readouts, generation).
common.py               paths, frozen-split loading with SHA checks, item sets, the S5/S6/S7 guard.
labels.py               the frozen 4-way outcome mapping + line-level GlotLID language identification.
judge_local.py          the blind local Qwen3-14B judge (primary), cache-compatible with the earlier panels.
judge.py / judge_api.py the frozen rubric and the OpenRouter batched reference judge.
certify.py              the stratified gpt-4.1 certification of the local judge, inside this pod, with a $3 cap.
freeze.py               e_L(h) -> O -> the confirmation cells -> configs/frozen_predictions.json + FREEZE.sha256.
third_channel.py        results/third_channel.json - the free third label channel (iteration-3 refusal classifier).
gate_freeze_test.py     GATE 5: the confirmation entry point must refuse a missing or tampered freeze.
cert_pool.py            the free certification path against gpt-4.1 labels already on disk.
make_cells_csv.py       results/cells.csv - one flat row per cell.
screen.py               results/screen.json: the 57-cell GaMS3 screen and the sibling mis-specification arm.
analysis.py             per-cell tables, the primary rank statistic, nested R2 with LOO, baseline races, the argmax
                        check, controls, the dissociation ladder, placebos, Holm, the pre-registered verdict.
rederive.py             GATE 8: an independent recompute of every headline number + the freeze-order check.
alib.py                 the shared statistics (item-cluster bootstrap, permutation nulls, exact McNemar, Holm).
report_tables.py        results/report_tables.md - every table, each caption naming the file that produced it.
figures.py              figures/ - the write profile, O vs outcome, matched-energy bands, the dissociation, collateral.
build_output.py         method_out.json (exp_gen_sol_out schema) + results/per_item.parquet.
make_deviations.py      results/deviations.json - every departure from the plan with its evidence file.
make_readme.py          regenerates the block between the GENERATED markers above.
configs/                frozen_predictions.json, FREEZE.sha256, profile_c.json (the pre-freeze strength choice),
                        post_freeze_cells.json (the declared exploratory rungs).
results/cells/<cell>/   gens.json (every generation), meta.json (layers, weights, exact energy, per-layer energy),
                        tf.json (FLORES dNLL, harmless KL).
results/                gate0_pins.json, gate1_unit_tests.json, gate3_anchor.json, inputs_manifest.json,
                        direction_sanity.json, controls/, energy_table.npz, screen.json, analysis_summary.json,
                        judge_cert.json, rederive.json, deviations.json, report_tables.md, per_item.parquet,
                        judge_local.jsonl, api_costs.jsonl, timings.json.
```

Kept artifacts live on this run's storage volume at the paths above (relative to this repository root); files of
100 MB or more are never pushed to GitHub, so anything large stays only on the volume.

## How to run

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r pyproject.toml
bash run_chain.sh          # the exact chain that produced this repository
```

Hardware actually used: 1 x NVIDIA L4 (23 GB), 48-core host; ~3 h wall clock.

## Restoring removed files

`.aii/manifest.yaml` marks two paths `delete`, both regenerable, and keeps everything else:

```bash
# .venv/        the Python environment; every version is pinned in pyproject.toml and results/env_freeze.txt
uv venv .venv --python=3.12 && uv pip install --python .venv/bin/python -r pyproject.toml

# __pycache__/  byte-code caches; recreated on the next import
.venv/bin/python -c "import common, method"
```

`results/` is kept: it holds the 12,024 judged generations, every cell's per-layer removal-energy profile, the frozen
instrument's inputs and the unedited model's top-512 KL reference (`results/ref/dolly_ref.npz`, 19 MB, rebuildable only
by a GPU pass on the original checkpoint). Those files stay on this run's storage volume at the relative paths above;
files of 100 MB or more are never pushed to GitHub, so the panel's bulk lives only there. `configs/` (the freeze) is
text and is always kept.

Model weights are read from this run's shared HuggingFace cache and are re-downloadable:

```bash
huggingface-cli download cjvt/GaMS3-12B-Instruct --revision 1d0b27af5748784482600d24779409e7e1dc9adc
huggingface-cli download Qwen/Qwen3-14B        --revision 40c069824f4251a91eefaf281ebe4c544efd3e18
huggingface-cli download cis-lmu/glotlid       --revision 85cd6716494360367b75f642b5bc78667605d0b4
```

Read-only inputs from earlier rounds (frozen directions, the shipped adapter, the Optuna journals, the iteration-3
panels, the frozen data protocol) are listed with their SHA256 and their recovery path in
`results/inputs_manifest.json`; this repository never modifies them.
