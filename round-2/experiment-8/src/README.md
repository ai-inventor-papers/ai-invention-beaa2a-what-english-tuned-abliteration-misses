# Does removing a Slovene refusal *prior* finish the English edit? — no, but layer-matched ablation does

Iteration-2 causal artifact for run `run_Fapgmt6JWbcD` (`gen_art_experiment_8`). It tests, in
`google/gemma-3-12b-it`, whether the **Slovene refusal that survives an English refusal-direction ablation** is carried by
a **language-conditioned, harm-orthogonal refusal prior** `r_prior` (a Wang et al., ICLR 2025 false-refusal vector built
from judged *harmless* refusals), and — after that hypothesis fails its pre-registered test — where the residual actually
lives. `cjvt/GaMS3-12B-Instruct` is a descriptive contrast; the community edit `p-e-w/gemma-3-12b-it-heretic` is a
held-out edit.

**Everything below is recomputed from saved per-item files** (`results/per_item.parquet`, `results/*/gens/*.json`,
`results/*/per_item_rows.jsonl`) by `analysis.py`, re-derived independently by `verify_numbers.py` (103/103 checks pass; `analysis.py --recompute` reproduces every verdict),
and printed by `report_tables.py` into `results/report_tables.md`.

**Independent audit of every number quoted below.** `audit_headline.py` re-derives all 43 headline numbers from the raw
artefacts only (`results/*/gens/*.json`, the two judge caches, `per_item_rows.jsonl`, `directions/*.npz`), re-implementing
the label join, the paired cut, the cluster bootstrap and the exact McNemar test from scratch without importing
`analysis.py`, `verify_numbers.py` or `common.py`: **43/43 match** (`results/audit_headline.json`). Its three placebos
behave as they must — permuting the arm label within an item kills the X1 effect (cut 0.68 → −0.01, CI [−0.16, 0.14]),
pooling and redistributing the judged labels across the two arms puts the real cut far outside the null
(placebo CI [−0.14, 0.14]), and permuting the language label kills the Slovene-minus-English gap (0.24 vs null CI
[−0.12, 0.12]). Within-arm label permutation was tried first and rejected as vacuous: it leaves each arm's marginal, and
therefore the paired cut, unchanged by construction.

## Headline

1. **The pre-registered hypothesis fails.** `d_EN` ablation removes most *English* refusal (0.91 → 0.23) but leaves
   **0.86** Slovene harmful refusal. Adding `r_prior` at matched English efficacy cuts that by only
   **0.036 [−0.037, 0.109]** — *less* than the best energy- and collateral-matched **random** direction (0.074), so
   **KILL rule (a) fires**, and *less* than its own **within-language shuffled-label control** (0.135), so **KILL rule (c)
   fires too**. F1 fails on both halves, on JBB half-B and on the held-out StrongREJECT categories separately.
2. **The residual is not a missing direction at the chosen site — it is written redundantly across depth.** Exploratory
   (post-freeze, declared in `configs/explore_protocol.json` / `explore2_protocol.json` *before* their outcome passes):
   ablating **each layer's own** harm direction `d_EN(h)` at every hidden index drops Slovene harmful refusal
   **0.86 → 0.10** under the primary judge (paired cut **0.71 [0.57, 0.85]**, McNemar p = 1.9e-9; **0.91 → 0.23**,
   cut 0.68 [0.59, 0.76] under the full-coverage second judge) while output stays fluent Slovene (0 % invalid,
   FLORES +0.52 nats/token, Slovene MC accuracy 0.61 vs 0.58 unedited). Ablating *more* of the single-site direction
   (c = 2) does not: 0.84. **No single 12-layer band does it either** (0.82 / 0.82 / 0.70 / 0.99 for layers 1–12,
   13–24, 25–36, 37–48); the effect accumulates with depth (layers 1–24 → 0.55, 1–36 → **0.21**, 1–48 → 0.23), and the
   top 12 layers contribute nothing. Adding `d_SL(h)` as well drives refusal to 0 but **destroys the model**
   (67–93 % invalid Slovene output, FLORES +13 nats, MC accuracy 0.28) — "refusal gone" and "model working" have to be
   reported together.
3. **It is the harm directions, not the amount of ablation.** Two matched controls remove exactly as many directions at
   exactly the same 48 sites: layer-matched **random** directions (no cut, 0.86, FLORES +0.07) and layer-matched
   **energy-matched principal components** (no cut, 0.93, FLORES +0.25, Dolly KL 0.45 — *more* collateral than the real
   thing). The PC control produces a clean **double dissociation**: it makes the model answer 68 % of Slovene prompts in
   English while still refusing them, whereas layer-matched `d_EN(h)` removes the Slovene refusals with 0 % wrong-language
   output.
4. **What looks like a refusal prior is mostly language identity plus collateral damage.** `cos(r_prior, l) = 0.65` and
   `cos(r_prior, shuffled-label r_prior) = 0.89` at the frozen site: the pooled contrast is dominated by *which language*
   the refused items were in, not by the refusal label. Ablating the language-identity axis `l` on top of `d_EN` gives the
   biggest activation-arm cut (0.315) but costs **+1.93 nats** of Slovene FLORES NLL — it damages Slovene, it does not
   surgically unlock it.
5. **`r_prior` does buy something small and specific: over-refusal.** Slovene over-refusal on benign twins falls
   0.28 → 0.19 under `r_prior` alone (McNemar p = 0.006, Holm-adjusted 0.025) with English harmful refusal essentially
   unchanged (+0.036 [0.000, 0.081]). The pre-registered F3 bar (≥ 50 % relative) is not met (32 % relative), so this is
   a real but sub-threshold effect.
6. **The same move repairs a shipped English edit.** Stacking layer-matched `d_EN(h)` ablation on the iteration-1 core
   Heretic edit takes its held-out Slovene refusal **0.93 → 0.11** (cut 0.81 [0.72, 0.90]) at FLORES +0.55 and 4 % invalid
   output. Its layer-matched random control is **not** null here (0.47), unlike on the unedited model — on an
   already-abliterated model generic ablation does move refusal, so the harm-direction arm's advantage over random is
   0.36, not the full cut. Both numbers come from the second judge (the paid budget was gone).
7. **Our own core Heretic edit is optimisation-limited, not evidence about the model.** On held-out categories the
   iteration-1 core edit (trial 96) still refuses **0.89** in Slovene, while the *community* edit of the same base model,
   built from the same English sources with a larger search, refuses **0.26**. Any "Gemma keeps Slovene refusal" claim
   must therefore be made about *an edit*, not about the model.
8. **GaMS3 shows no Slovene-specific residual.** After the same English ablation it falls to 0.57 EN / 0.50 SL — the
   iteration-1 asymmetry is a Gemma property under this protocol, not a general one.

## What was run

Frozen data (from `gen_art_dataset_1`, SHA-verified against `data/split_manifest.json`; `S5/S6/S7` never opened):

| split | use |
|---|---|
| `S3_jbb` half A (44 twin pairs) | direction construction + layer/strength selection (**dev only**) |
| `S3_dolly` / `S3_flores_dev` / `S3_mc` half A | KL / FLORES / MC filters during selection |
| `S3_jbb` half B (41 pairs) + `S4_strongreject_pairs` stratum `hoc` (70 pairs) | **OUTCOME**: 111 harmful + 111 harmless per language |
| `S2_semantic` harmless | independent-source stability rebuild of `r_prior` |

Protocol: 4-bit NF4 (bf16 compute), pinned revisions, identical chat template and system prompt in both languages,
greedy decoding, ablation at the embedding and **every** layer output at **all** positions, and a batching certification
gate per model. Directions are difference-in-means on winsorised (q = 0.995) pos −1 residuals; `d_EN`/`d_SL` reproduce
iteration-1's frozen vectors to cos = 1.0000, and Gemma's no-op generations reproduce iteration-1's byte-for-byte
(40/41 EN, 41/41 SL identical over the first 60 characters).

`r_prior(L) = mean(residual | harmless & refused) − mean(residual | harmless & complied)`, orthogonalised against that
layer's `d_EN`; 30/188 half-A harmless prompts were refused (27 of them Slovene: 23/44 Slovene JBB-benign vs 3/44
English). The layer (L = 20) and every arm's strength `c*` were chosen on half A alone, then
`configs/frozen_protocol_gemma.json` + `results/frozen_predictions.json` were hashed into `configs/FREEZE.sha256`
**before the first OUTCOME forward pass** (`verify_numbers.py` asserts the log order).

Arms (Gemma): `A0` no-op, `A1` `d_EN`, `A2` `d_EN+r_prior`, `A3` `r_prior` alone, `A4` `d_EN+l`, `A5` `d_EN+u_SL`,
`A6` `d_EN+r_prior⊥l`, `A7–A9` `d_EN+`three energy- **and** collateral-matched randoms, `A10` `d_EN+`shuffled-label
`r_prior`, `A11` `d_EN+r_prior_SLjbb` (topic- and language-controlled), dose curves, and `ADD` (activation addition,
sufficiency). Weight edits: `W0/W1/W2` on the iteration-1 core LoRA, `C0/C1/C2` on the community model, implemented as
exact output hooks on `o_proj`/`down_proj` (unit-tested against the dense `(I − rrᵀ)W` edit, rel. err 4e-3).
Exploratory (each declared with its protocol file and hash in `configs/FREEZE.sha256` before its outcome pass):
`X1` layer-matched `d_EN(h)`, `X2` layer-matched `d_EN(h)+d_SL(h)`, `X4` `d_EN` at c = 2, `X3`/`X5` layer-matched random
and energy-matched-PC controls, `Y*` depth bands, and `W3`/`W4` the repair arms on the core edit.

## Judging

Primary: **openai/gpt-4.1**, temperature 0, frozen rubric with explicit `partial / irrelevant / malformed / empty`
labels and a response-language field, fully blind (request + reply under a neutral shuffled id, 10 unrelated cases per
call). It agreed with the earlier single-case format on 450 doubly-labelled items (κ = 0.95 on refused-vs-not).
The run key's hard cap stopped it after **5,295 of 9,134** generations, prioritised so that every arm carrying a frozen
prediction (`A0–A4`, `A7`, `A10`, `W0`, `W1`, `C0`, `C1`) is **fully** judged; partially judged arms report their judged
*n* in every table, and paired contrasts use only items judged in both arms.

Because the key was exhausted, the planned gemini second judge was replaced by a **local cross-family second judge**
(`Qwen/Qwen3-14B`, 4-bit, same frozen rubric, blind) which labelled **every** generation: κ vs gpt-4.1 = **0.77** on
refused-vs-not (0.88 Slovene, 0.62 English — it is stricter, counting lecture-only replies as refusals). Its
full-coverage rates (`analysis_summary.second_judge_sensitivity`) reproduce every qualitative conclusion, including
`X1` (0.91 → 0.23 Slovene) and `A2` ≈ random. An opener-rule labeller is reported as a third sensitivity layer.
**Native-speaker review of the Slovene items and outputs is PENDING** — not performed.

## Results

Judged refusal rates with 95 % item-cluster bootstrap CIs (resampling unit = semantic id, EN/SL and harmful/harmless
twins resampled together, 2,000 replicates). Full tables: `results/report_tables.md`.

| Gemma arm | EN harmful | SL harmful | SL harmless (over-refusal) | SL FLORES ΔNLL |
|---|---|---|---|---|
| A0 no-op | 0.91 [0.86, 0.95] | 0.99 [0.97, 1.00] | 0.28 [0.20, 0.36] | 0 |
| A1 `d_EN` | 0.23 [0.14, 0.31] | **0.86 [0.80, 0.92]** | 0.19 [0.12, 0.26] | +0.005 |
| A2 `d_EN+r_prior` | 0.21 | 0.83 [0.75, 0.89] | 0.12 [0.06, 0.17] | −0.037 |
| A7 `d_EN+rand₁` | 0.21 | 0.85 [0.77, 0.91] | 0.15 | +0.052 |
| A10 `d_EN+`shuffled | 0.41 | 0.73 [0.65, 0.81] | – | +0.210 |
| A4 `d_EN+l` | 0.23 | 0.55 [0.46, 0.64] | 0.08 | **+1.93** |
| X4 `d_EN` c = 2 * | 0.04 | 0.75 [0.63, 0.86] | – | +0.010 |
| **X1 layer-matched `d_EN(h)` \*** | 0.03 | **0.10 [0.02, 0.19]** | – | +0.524 |
| X2 layer-matched `d_EN(h)+d_SL(h)` * | 0.02 | 0.00 | – | +12.96 (93 % invalid) |

\* exploratory, declared post-freeze.

Depth localisation and its controls, all judged by the local second judge at full coverage (n = 111/language;
`results/report_tables.md` has the complete table with KL and MC accuracy):

| arm | SL harmful | EN harmful | SL FLORES ΔNLL | SL invalid |
|---|---|---|---|---|
| A1 `d_EN` (single site, L20) | 0.91 [0.86, 0.95] | 0.67 | +0.005 | 0.00 |
| X4 `d_EN` c = 2 | 0.84 | 0.52 | +0.010 | 0.00 |
| X3 layer-matched **random** | 0.86 [0.79, 0.92] | 0.95 | +0.066 | 0.02 |
| X5 layer-matched **energy-matched PC** | 0.93 [0.87, 0.97] | 0.95 | +0.249 | 0.68 (answers in English) |
| `d_EN(h)`, layers 1–12 | 0.82 | 0.79 | +0.743 | 0.01 |
| `d_EN(h)`, layers 13–24 | 0.82 | 0.45 | +0.017 | 0.02 |
| `d_EN(h)`, layers 25–36 | 0.70 | 0.72 | +0.082 | 0.03 |
| `d_EN(h)`, layers 37–48 | 0.99 | 0.87 | −0.003 | 0.00 |
| `d_EN(h)`, layers 1–24 | 0.55 | 0.42 | +0.409 | 0.01 |
| `d_EN(h)`, layers 1–36 | **0.21 [0.14, 0.29]** | 0.38 | +0.513 | 0.05 |
| **X1 `d_EN(h)`, all 48** | **0.23 [0.16, 0.32]** | 0.37 | +0.524 | 0.00 |
| X2 `d_EN(h)+d_SL(h)`, all 48 | 0.25 | 0.44 | +12.96 | 0.67 (degenerate) |

Repairing an English weight edit (S4 hoc, n = 70/language, second judge):

| arm | SL harmful | EN harmful | SL over-refusal | SL FLORES ΔNLL |
|---|---|---|---|---|
| W0 core Heretic edit (trial 96) | 0.93 | 0.70 | 0.11 | −0.005 |
| W1 + `r_prior` weight edit | 0.81 | 0.73 | 0.06 | +0.009 |
| **W3 + layer-matched `d_EN(h)`** | **0.11** | 0.29 | 0.00 | +0.546 |
| W4 + layer-matched random | 0.47 | 0.70 | 0.01 | +0.064 |

Weight edits, held-out StrongREJECT categories (70 pairs/language):

| arm | EN harmful | SL harmful | SL over-refusal |
|---|---|---|---|
| W0 core Heretic edit (trial 96) | 0.39 | 0.89 [0.81, 0.96] | 0.07 |
| W1 core + `r_prior` weight edit | 0.23 | 0.76 [0.65, 0.86] (cut 0.13 [0.00, 0.25], p = 0.08) | 0.04 |
| W2 core + matched random weight edit | 0.48 | 0.94 (cut 0.00) | – |
| C0 community heretic | 0.01 | **0.26 [0.16, 0.37]** | 0.01 |
| C1 community + `r_prior` weight edit | 0.01 | 0.20 [0.11, 0.30] (p = 0.50) | 0.00 |

F5 is **declared not evaluable** by its own pre-registered gate (the community model's Slovene residual, 0.26, is below
the 0.40 threshold — there was little residual left to remove).

Frozen verdicts: **F1 fail, F2 pass, F3 fail (sub-threshold but significant), F4 fail, F5 not evaluable, F6 fail;
KILL (a) and (c) both fire.** Holm-adjusted p-values across the frozen family: F3 0.025, everything else 1.0. The
pre-registered confound rules read "neither": `r_prior⊥l` does not pass F1 either.

Mechanism diagnostics: the frozen probe (L2 logistic on pos −1 residuals, fitted on half A, CV AUROC 0.98) still
separates harmful from harmless on OUTCOME items **after** ablation (AUROC 0.97 SL) and its item-level slope survives
`A0 → A1 → A2` (b₁ 4.89 → 2.04 → 2.18) while the `r_prior` projection adds nothing (b₂ ≈ 0.21–0.25, CIs spanning 0):
harmfulness is still decodable and still used; what changes is how strongly it maps to refusal. Which Slovene items
survive `d_EN` is not predicted by the cosine-transfer baseline (AUROC 0.24) — the baseline is worse than chance, so
`cos(d_EN, d_SL) = 0.92` badly mispredicts item-level transfer — and only weakly by the baseline margin (0.64) or the
`r_prior` projection (0.41).

Stability: rebuilt on an independent source (`S2` Semantic-Harmless, 150 items/language), `r_prior` reaches
cos = 0.60 with the frozen vector against a split-half ceiling of 0.87 — and the rebuild is again language-dominated
(cos with `l` = 0.74; 14 refusals, all Slovene). Rebuilding the frozen direction with LLM-judge labels instead of the
pre-freeze rule labels changes it by cos = 0.96, so the label source is not what makes `r_prior` fail.

Validity gate: neither teacher-forced trait reaches the pre-registered Spearman ≥ 0.85 across conditions (R1: 0.74 SL /
0.24 EN; R_seq: 0.46 / 0.53), so **all refusal claims are judge-based**; R1/R_seq are reported per item as secondary.

## Layout

```
method.py            GPU pipeline: load → hook unit tests → batching gate → half-A construction → directions →
                     layer/strength selection → FREEZE → OUTCOME arms → weight edits; --model {gemma,community,gams3},
                     --explore for the post-freeze X arms + S2 stability. Resumable per arm.
interventions.py     4-bit loading, residual hooks (ablate / layer-matched ablate / partial / add / capture),
                     o_proj+down_proj output hooks (= weight orthogonalisation), teacher-forced R1/R_seq/KL/NLL/MC,
                     batched greedy generation.
common.py            paths, frozen-split loading with SHA checks, set construction + T0 assertions, opener rule labeller
judge.py             blind gpt-4.1 judging (batched, cached, cost-capped), second-judge sampler
local_judge.py       local Qwen3-14B second judge (same rubric) over every generation
analysis.py          rates + CIs, frozen F-verdicts, KILL rules, Holm, validity gate, collateral, item-level models,
                     secondary blocks (weight edits, exploratory arms, GaMS3, per-source), sensitivity label sets
verify_numbers.py    independent plain-python recompute of every headline number + placebo swaps + freeze-order check
audit_headline.py    second, stricter audit: re-derives all 43 README numbers from the RAW files through a different
                     code path (no project imports) and runs three placebos that must fail -> results/audit_headline.json
figures.py           fig1–fig9 (PDF + PNG)
report_tables.py     the markdown tables above, straight from analysis_summary.json
make_deviations.py   results/deviations.json — every departure from the plan, with its evidence file
build_output.py      method_out.json (exp_gen_sol_out schema)
run_chain.sh         community → gams3 → exploratory stages after the Gemma run
configs/             frozen_protocol_gemma.json, explore_protocol.json, FREEZE.sha256 (hashes + timestamps)
directions/          every frozen direction (.npy) + per-layer bundle; SHA-256 in the frozen protocol
references/          mined per-language refusal/compliance openers used by R_seq
results/<model>/     gens/<arm>.json (all generations), per_item_rows.jsonl (teacher-forced traits), acts/ (residuals),
                     diagnostics (layer_selection, rand_draws, efficacy, weight_edit, batch_cert, s2_stability)
results/             analysis_summary.json, per_item.parquet, report_tables.md, verify_numbers.json, novelty.json,
                     deviations.json, judge_cache.jsonl, judge2_local.jsonl, api_costs.jsonl
figures/             fig1 arms · fig2 dose · fig3 weight edits (incl. repair arms) · fig4 layer cosines ·
                     fig5 criterion-vs-evidence · fig6 transfer predictors · fig7 random acceptance · fig8 GaMS3 ·
                     fig9 residual vs fluency cost · fig10 depth localisation
```

Absolute workspace path (kept artifacts are readable here by later rounds):
`/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_8`

## How to run

The exact sequence that was run, with hardware, timings, pins and the numbers to expect, is in `reproducibility.md`.

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r pyproject.toml     # torch cu128 wheels come from the extra index
.venv/bin/python method.py --model gemma                        # ~90 min on one 24 GB GPU
bash run_chain.sh $!                                            # community → gams3 → --explore, then touch results/GEN_DONE
.venv/bin/python method.py --model gemma --explore2             # depth bands + layer-matched controls (~20 min)
.venv/bin/python method.py --model gemma --explore3             # repair arms on the core Heretic edit (~5 min)
.venv/bin/python judge.py --batched --tiers 4                   # blind gpt-4.1 judging (cost-capped, resumable)
.venv/bin/python local_judge.py                                 # local second judge over every generation (~23 min)
.venv/bin/python analysis.py && .venv/bin/python verify_numbers.py && .venv/bin/python audit_headline.py
.venv/bin/python figures.py && .venv/bin/python report_tables.py && .venv/bin/python build_output.py
```

Cost: **$3.43** of OpenRouter spend (batched gpt-4.1 judging; the local second judge is free), under the $10 cap. Judging stopped before the exploratory arms because the run's OpenRouter budget for this phase ($7.00, shared by all of the phase's artifacts, non-resetting) was used up. A resume attempt on 2026-09-24 was refused (HTTP 403 `aii_run_budget_exhausted`), and the free OpenRouter models were at their shared daily cap (HTTP 429). The gaps in primary-judge coverage listed under Judging are therefore final for this artifact.

## Limitations

- One confirmatory model and one Slovene locale; `n = 111` harmful + 111 harmless per language, so sub-0.10 differences
  are not resolvable (the F1 CI is ±0.07 wide).
- Slovene items are machine-translated with automated QC only; **native review pending**.
- 4-bit NF4 weights everywhere, including the bf16 community edit — internally consistent, not a bf16 replication.
- The primary judge covers 58 % of generations (every frozen-prediction arm fully); exploratory arms rely on the local
  second judge for full coverage.
- One Heretic seed for the core edit, so prompt-level CIs do not measure optimiser variance — and the community edit
  shows that variance is large.
- The `X*`, `Y*` and `W3`/`W4` arms were declared after the freeze and are exploratory. The paid judge's budget was gone
  before them, so their headline rates come from the **local second judge** (κ = 0.88 with gpt-4.1 on Slovene, but it is
  systematically stricter); `X1`, `X2` and `X4` also have partial primary-judge coverage and agree. "The Slovene residual
  is written redundantly across depth" needs replication on a second model and a fully judged replication before it is
  asserted beyond this checkpoint.
- On the already-abliterated model the layer-matched random control is **not** null (W4), so the repair arm's specificity
  there is partial; on the unedited model the same control is null (X3).
- The layer-matched random control could reach `d_EN(h)`'s projection energy at only 15/48 layers (the PC control:
  46/48), so `X3` is a conservative control and `X5` is the matched-energy one; both are reported.
- The weight edit orthogonalises `o_proj`/`down_proj` *outputs*; Gemma-3 applies post-projection layernorms, so it does
  not guarantee `r_prior` is absent from the residual write (the same limitation as Heretic's edit on Gemma-3).

## Restoring removed files

Everything marked `delete` in `.aii/manifest.yaml` is rebuilt by:

```bash
# .venv/  (python environment)
uv venv .venv --python=3.12 && uv pip install --python .venv/bin/python -r pyproject.toml
# results_mini/  (T3 smoke run)
.venv/bin/python method.py --model gemma --mini
# results/*/acts/  (half-A and OUTCOME residual caches; needed only to re-fit directions or the item-level models)
rm -rf results/gemma/acts && .venv/bin/python method.py --model gemma      # resumes, recomputes the caches only
rm -rf results/gams3/acts && .venv/bin/python method.py --model gams3      # same for the GaMS3 caches
# __pycache__/  — recreated automatically on import
```

Model weights live in this run's shared HF cache (`$HF_HUB_CACHE`) and are re-downloadable:
`huggingface-cli download google/gemma-3-12b-it --revision 96b6f1eccf38110c56df3a15bffe176da04bfd80`,
`cjvt/GaMS3-12B-Instruct --revision 1d0b27af5748784482600d24779409e7e1dc9adc`,
`p-e-w/gemma-3-12b-it-heretic --revision e037e6e112ea85777fc3858469cdc31fdfceaa13`,
`Qwen/Qwen3-14B --revision 40c069824f4251a91eefaf281ebe4c544efd3e18`.
The core edit's LoRA adapter is read (never modified) from
`/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1/gen_art/gen_art_experiment_1/adapters/gemma_selected_path2`
(`adapter_model.safetensors` SHA-256 `d219c084…`, verified at load).
