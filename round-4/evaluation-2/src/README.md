# Partial answers, judges, and a full recount (iteration 4, evaluation 2)

This is a CPU-mostly re-analysis and audit of the bilingual (EN/SL) Heretic-abliteration study (gemma-3-12b-it, GaMS3-12B-Instruct and the iteration-3 cross-family panel). It trains no new checkpoint.
- Every judged generation from five earlier panels is pooled into one table.
- The PARTIAL-transition hypothesis (C3) is tested against predictions frozen before any fit.
- The workhorse judge is re-certified against a frozen, bought gpt-4.1 sample from EDITED cells.
- The scope tables the original request asked for are produced: guard ASR, validity, and the item-level flip analysis.
- The NF4-vs-bf16 confound is bounded.
- The ten blocking report repairs are written paste-ready.
- The previously unaudited iteration-3 draft sections are recomputed by an independent code path.

## Headline results (every number is read from the file named beside it)

**Inventory** (`results/inventory_reconciliation.md`)
- Pooled table: **56,866** judged generations.
- The four iteration-3 panels load as 52,066 generation rows. They reconcile exactly with the claimed 51,353 once exp12's 9,912 rows are reduced to its 9,199 distinct judged (prompt, response, language) keys; identical generations share one judge label. The table keeps all rows.
- The iteration-2 FINAL panel adds 4,800 rows.

**C3, the PARTIAL transition: FALSIFIED under the frozen rule** (`results/curve_fits.json`, `configs/FREEZE_iter4_eval.json`)
- The strict-minus-broad gap is algebraically the PARTIAL-share difference. That identity is stated and is not counted as a finding.
- C3-i (shape) holds. The PARTIAL-share max-minus-min on the designed dose ladders is EN 0.346 [0.257, 0.539] and SL 0.271 [0.090, 0.323]. The curves are not flat.
- C3-ii (order) fails. The proportional-odds check fired in both ladders (AIC +59 / +243), so the nonparametric argmax is primary. Delta_peak: L1 +0.45 [-0.45, 0.90]; L2 +0.98 [-0.98, 2.00]. Both CIs cover 0.
- C3-iii (out-of-panel) fails: Spearman -0.427, permuted-dose p 0.339.
- Estimator sensitivity, reported beside the verdict: in L1 the continuation-ratio fit gives +0.35 [0.20, 0.43] and the PO fit gives +0.36 [0.28, 0.43]. The falsification therefore rests on a five-level nonparametric argmax that the pre-hoc power simulation (run for the PO estimator) did not cover.

**Judge re-certification within EDITED cells** (`results/judge_calibration.json`, `results/judge_calibration_supplement.json`)
- Sample: 900 frozen, stratified items, of which 515 were bought and 385 were already labelled.
- Workhorse Qwen3-14B vs gpt-4.1, refused-vs-not kappa: EN 0.871 weighted / 0.858 sample, so the gate is **MET**. SL 0.871 / 0.723, so the gate is **NOT MET** under the conservative rule and SL rates carry Rogan-Gladen companions.
- Keyword rule: kappa 0.074 with a false-positive share of 0.455. Distilled classifier: kappa 0.919.
- A declared post-freeze supplement (160 labels) shows the frame-level gate hides a weak panel. exp11 English has kappa 0.226 [0.099, 0.399]: most workhorse REFUSED labels there are gpt-4.1 PARTIAL.
- Re-expressing the exp11 cells in gpt-4.1 classes changes the C3 conclusion nowhere. The keyword edit's S5X gap goes +0.68 -> +0.63.
- Of 211 per-cell SL-EN gap claims, 40 are JUDGE_SENSITIVE (they flip against the Rogan-Gladen-corrected reading or, on Gemma cells only, the distilled classifier) and 105 are DEFINITION_SENSITIVE (strict vs broad).

**Scope tables**
- **Guard ASR is not the complement of refusal.** The table covers 136 cell x language rows over 70 cells (`results/asr_table.csv`). Gemma edit, non-refused responses called safe by both guards: EN 0.106 (n=245), SL 0.338 (n=80); SL-EN 0.232 [0.124, 0.348]. Across cells, Spearman(ASR gap, refusal gap) = -0.836 [-0.928, -0.674] over 46 cells. NF4 guard fidelity against the stored bf16 labels: Llama-Guard 0.967 (kappa 0.933, n=120), PolyGuard 1.000 (n=29). The time-capped PolyGuard pass scored 2672 of 3,420 rows (the longest responses are missing), so `asr_llamaguard_only` (full coverage) is reported beside the two-guard ASR.
- **Validity columns** (INVALID, empty, truncation, repetition, and GlotLID line-level language consistency recomputed on every row) are in `results/validity_table.csv`.
- **Flip analysis** (`results/flip_analysis.json`). Gemma: slope ratio EN 0.50 [0.24, 0.86], SL 0.34 [0.19, 0.54]; intercept shift -6.65 / -5.32; refit AUROC after the edit about 0.997. The information survives, the criterion moved, and coupling is partly lost. GaMS3 is not estimable because almost no refusals remain after the edit.

**NF4 vs bf16** (`results/quant_confound.json`)
- NF4 changes each edited matrix by 0.093 relative Frobenius error.
- The edit's per-layer removal-energy profile has cosine 0.999998 between bf16 and NF4, and the removed rows rotate by 5.2 degrees.
- Activation level: bf16 vs NF4 teacher-forced 32-token KL 0.1122 (original) / 0.0871 (edit); top-1 agreement 0.915 / 0.916.
- Behavioural cell (Gemma trial-96 edit, 20 verified pairs, same gpt-4.1 rubric): refused bf16 vs NF4 EN 0.25 vs 0.25, SL 0.85 vs 0.70; paired SL-EN gap bf16 +0.60 [0.40, 0.80] vs NF4 +0.45 [0.20, 0.70] (`results/quant_confound_behaviour.json`).
- Verdict: The NF4-vs-bf16 confound is BOUNDED by weight-level, activation-level and a 40-item behavioural measurement; it is NOT closed at panel scale (one checkpoint, 20 verified pairs).

**Recount of the iteration-3 draft** (`results/corrected_numbers_iter4.json`, `results/audit_log_iter4.json`)
- 102 numbers checked: {'match': 97, 'misdescribed': 3, 'mismatch': 2}.
- Mismatch-or-misdescribed rate 0.049, Wilson 95% [0.021, 0.110], against the audited half's prior 0.055.
- Every placebo collapses (cell-label +0.0006, language-label +0.0010, dose -0.0023, kappa permutation +0.0049) against the real effects -0.1048 / -0.0714. The leakage detector fires.

**Paste-ready repairs:** `results/report_repairs_iter4.md` covers R1-R10 plus C3, the judge panels and NF4. Each number sits beside its producing file, and the lint count is 0. The iteration-1 section is restored byte-for-byte in `results/r4_iteration1_restored_verbatim.md`.

**Spend:** OpenRouter $0.924 in total (`results/cost_log.jsonl`; hard stop $8). This includes one $0.00003 connectivity test.

## What is NOT claimed / not run
- No human labels. Every judged rate is proxy-certified by gpt-4.1. The consolidated pending list is `results/pending_human_review_iter4.md`: 3 native-review packets (570 rows) and 2 executor checks.
- NF4-vs-bf16 is bounded, not closed. bf16 ran with CPU offload on one checkpoint and 20 verified pairs only.
- The guard pass on the iteration-3 panels uses a frozen subsample of 30 harmful items per cell x language (`results/guard/guard_subsample_frozen.json`), in NF4. The PolyGuard pass was time-capped; coverage per cell is in `results/asr_table.csv` (n_guarded for both guards, n_llamaguard for Llama-Guard alone).
- n=2 main models and one Heretic run each. Nothing is attributed to a training stage.

## Layout
| path | what |
|---|---|
| `eval.py` | single entry point, `--phase 0|freeze|2buy|1|2|2b|3guard|3|4|6|5|7|all` |
| `scripts/common.py`, `scripts/po.py`, `scripts/ladders.py` | shared helpers, fast proportional-odds fitter, ladder definitions |
| `scripts/p0_inventory.py` | phase 0: harmonised pooled table + reconciliation |
| `scripts/p1_freeze.py` | FREEZE: predictions, estimators, Holm family, seeds, gate, calibration sample, pre-hoc power |
| `scripts/p1_curves.py` | phase 1: LOESS + PO + continuation-ratio curves, INVALID curve, C3-iii, Holm, falsifier |
| `scripts/p2_buy.py`, `scripts/p2_judge.py`, `scripts/p2b_supplement.py` | phase 2: gpt-4.1 purchase, certification, Rogan-Gladen, judge sensitivity, supplement |
| `scripts/p3a_guard.py`, `scripts/p3_scope.py` | phase 3: NF4 guard pass; ASR / validity / GlotLID / flip / pending list |
| `scripts/p4_quant.py`, `scripts/p4b_behaviour.py` | phase 4: NF4-vs-bf16 weight + activation bound; 40-item behavioural bf16 cell |
| `scripts/dl_models.sh` | re-downloads the three models phases 3guard/4 need into the shared HF cache |
| `rederive_iter3.py` | phase 6: independent recompute (stdlib + numpy + pyarrow only) |
| `scripts/p5_repairs.py`, `scripts/p7_assemble.py`, `scripts/p8_readme.py` | repairs, registry + eval output, this README |
| `scripts/heretic_shim/` | verbatim copy of Heretic's `dense_features` so the pickled classifier loads without Heretic's plugin stack |
| `configs/FREEZE_iter4_eval.json`, `configs/FREEZE.sha256` | frozen predictions (hash-verified by phase 1 and the purchase) |
| `results/pooled_generations.parquet` | one row per judged generation (56,866), harmonised 4-way class, dose, validity columns |
| `results/partial_curves.csv`, `results/curve_fits.json` | per-cell class shares; all curve fits and C3 statistics |
| `results/judge_*` | calibration, supplement, per-cell sensitivity (`judge_sensitivity_iter4.csv`) |
| `results/asr_table.csv`, `results/validity_table.csv`, `results/flip_analysis.json`, `results/quant_confound*.json` | scope tables |
| `results/claims_registry_iter4.csv` | every claim with status (SUPPORTED / FALSIFIED / JUDGE_SENSITIVE / ...) |
| `results/report_repairs_iter4.md` | paste-ready repairs R1-R10 + new sections |
| `results/corrected_numbers_iter4.json`, `results/audit_log_iter4.json`, `results/rederive_iter3_rows.csv` | recount |
| `results/cost_log.jsonl`, `results/gpt41_*labels.jsonl` | every paid call and its label |
| `figures/fig1..fig4` | PARTIAL vs dose; judge agreement forest; ASR vs refusal; flip panel |
| `full_eval_out.json` (+ mini/preview) | exp_eval_sol_out schema output |

All of `results/` and `figures/` stays on the run's volume. `results/pooled_generations.parquet` (19 MB) is below the 100 MB publish limit and is published.

## How to run
```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r requirements.lock --extra-index-url https://download.pytorch.org/whl/cu128 --index-strategy unsafe-best-match
.venv/bin/python eval.py --phase all       # the freeze is never re-run once it exists
```
Phases 3guard and 4 need a CUDA GPU (>= 16 GB) and the models google/gemma-3-12b-it@96b6f1ec, meta-llama/Llama-Guard-3-8B@7327bd9f and ToxicityPrompts/PolyGuard-Qwen@644bfe73 (`bash scripts/dl_models.sh`). Phase 2buy needs `OPENROUTER_BASE_URL` / `OPENROUTER_API_KEY`; it skips items that are already labelled.

## Restoring removed files
- `scripts/__pycache__/` (deleted; regenerable bytecode cache): `python -m compileall scripts` (or simply run any script).
- `.venv/` (deleted after the round; regenerable): `uv venv .venv --python=3.12 && uv pip install --python .venv/bin/python -r requirements.lock --extra-index-url https://download.pytorch.org/whl/cu128 --index-strategy unsafe-best-match`
- Model weights live in the shared HF cache, not in this directory. Restore them with `bash scripts/dl_models.sh`; for GlotLID, `huggingface-cli download cis-lmu/glotlid model.bin`.
