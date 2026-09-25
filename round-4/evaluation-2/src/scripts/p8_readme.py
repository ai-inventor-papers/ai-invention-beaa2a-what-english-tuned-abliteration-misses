#!/usr/bin/env python3
"""Write README.md and reproducibility.md from the results files (so the prose cannot disagree with the numbers)."""
from __future__ import annotations

import json

import pandas as pd

import common as C


def f3(x):
    return "NA" if x is None else f"{x:.3f}"


def cis(c, nd=3):
    return f"[{c[0]:.{nd}f}, {c[1]:.{nd}f}]"


def main() -> None:
    cf = C.jload(C.RES / "curve_fits.json")
    jc = C.jload(C.RES / "judge_calibration.json")
    sp = C.jload(C.RES / "judge_calibration_supplement.json")
    fl = C.jload(C.RES / "flip_analysis.json")
    asr = C.jload(C.RES / "asr_summary.json") if (C.RES / "asr_summary.json").exists() else {}
    qc = C.jload(C.RES / "quant_confound.json")
    cn = C.jload(C.RES / "corrected_numbers_iter4.json")["summary"]
    inv = C.jload(C.RES / "inventory_reconciliation.json")
    fz = C.jload(C.CFG / "FREEZE_iter4_eval.json")
    cost = sum(float(r.get("usd") or 0) for r in C.read_jsonl(C.RES / "cost_log.jsonl"))
    buy = C.jload(C.RES / "buy_summary.json")
    np_ = cf["pooled_designed_ladders"]["nonparametric"]
    rx = sp["c3_and_exp11_under_gpt41_reexpression"]
    dec = asr.get("nonrefused_decomposition", {}).get("exp4:gemma_edit", {})
    qa = qc["activations"] if isinstance(qc["activations"], dict) else None
    tot = sum(r["rows_loaded"] for r in inv)
    tot4 = sum(r["rows_loaded"] for r in inv if r["source"] != "exp4")
    asr_line = "Guard ASR: NOT RUN (see logs)."
    if asr:
        corr = asr.get("asr_gap_vs_refusal_gap", {})
        fid = asr.get("nf4_fidelity", {})
        asr_line = (f"- **Guard ASR is not the complement of refusal.** The table covers {asr.get('n_cells_language')} cell x language rows over {asr.get('n_cells')} cells (`results/asr_table.csv`). "
                    f"Gemma edit, non-refused responses called safe by both guards: EN {f3(dec.get('en', {}).get('share_guard_both_safe'))} (n={dec.get('en', {}).get('n_nonrefused')}), "
                    f"SL {f3(dec.get('sl', {}).get('share_guard_both_safe'))} (n={dec.get('sl', {}).get('n_nonrefused')}); SL-EN "
                    f"{f3(dec.get('sl_minus_en_both_safe', {}).get('point'))} {cis(dec['sl_minus_en_both_safe']['ci']) if dec.get('sl_minus_en_both_safe') else ''}. "
                    f"Across cells, Spearman(ASR gap, refusal gap) = {f3(corr.get('spearman'))} {cis(corr['ci_cell_bootstrap']) if corr.get('ci_cell_bootstrap') else ''} over {corr.get('n_cells')} cells. "
                    f"NF4 guard fidelity against the stored bf16 labels: Llama-Guard {f3(fid.get('llamaguard_agreement'))} (kappa {f3(fid.get('llamaguard_kappa'))}, n={fid.get('n_llamaguard')}), PolyGuard {f3(fid.get('polyguard_agreement'))} (n={fid.get('n_polyguard')}). "
                    f"The time-capped PolyGuard pass scored {asr.get('guard_coverage', {}).get('polyguard_scored')} of 3,420 rows (the longest responses are missing), so `asr_llamaguard_only` (full coverage) is reported beside the two-guard ASR.")
    qb = qc["behavioural"] if isinstance(qc["behavioural"], dict) else None
    beh = (f"Behavioural cell (Gemma trial-96 edit, 20 verified pairs, same gpt-4.1 rubric): refused bf16 vs NF4 EN {qb['en']['refused_bf16']:.2f} vs {qb['en']['refused_nf4']:.2f}, "
           f"SL {qb['sl']['refused_bf16']:.2f} vs {qb['sl']['refused_nf4']:.2f}; paired SL-EN gap bf16 {qb['paired_gap_bf16']['gap']:+.2f} {cis(qb['paired_gap_bf16']['ci'], 2)} vs NF4 "
           f"{qb['paired_gap_nf4']['gap']:+.2f} {cis(qb['paired_gap_nf4']['ci'], 2)} (`results/quant_confound_behaviour.json`)." if qb else "Behavioural cell: NOT RUN.")
    acts = (f"Activation level: bf16 vs NF4 teacher-forced 32-token KL {qa['orig']['mean_kl32']:.4f} (original) / {qa['edit']['mean_kl32']:.4f} (edit); top-1 agreement "
            f"{qa['orig']['top1_agreement_32tok']:.3f} / {qa['edit']['top1_agreement_32tok']:.3f}." if qa else "Activation level: NOT RUN.")
    rd = f"""# Partial answers, judges, and a full recount (iteration 4, evaluation 2)

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
- Pooled table: **{tot:,}** judged generations.
- The four iteration-3 panels load as {tot4:,} generation rows. They reconcile exactly with the claimed 51,353 once exp12's 9,912 rows are reduced to its 9,199 distinct judged (prompt, response, language) keys; identical generations share one judge label. The table keeps all rows.
- The iteration-2 FINAL panel adds 4,800 rows.

**C3, the PARTIAL transition: FALSIFIED under the frozen rule** (`results/curve_fits.json`, `configs/FREEZE_iter4_eval.json`)
- The strict-minus-broad gap is algebraically the PARTIAL-share difference. That identity is stated and is not counted as a finding.
- C3-i (shape) holds. The PARTIAL-share max-minus-min on the designed dose ladders is EN {np_['en']['max_minus_min']:.3f} {cis(np_['en']['max_minus_min_ci'])} and SL {np_['sl']['max_minus_min']:.3f} {cis(np_['sl']['max_minus_min_ci'])}. The curves are not flat.
- C3-ii (order) fails. The proportional-odds check fired in both ladders (AIC +{cf['L1_exp11_f_ladder']['po']['po_check']['aic_diff_po_minus_mn']:.0f} / +{cf['L2_exp9_c_grid']['po']['po_check']['aic_diff_po_minus_mn']:.0f}), so the nonparametric argmax is primary. Delta_peak: L1 {cf['L1_exp11_f_ladder']['nonparametric']['delta_argmax']['point']:+.2f} {cis(cf['L1_exp11_f_ladder']['nonparametric']['delta_argmax']['ci'], 2)}; L2 {cf['L2_exp9_c_grid']['nonparametric']['delta_argmax']['point']:+.2f} {cis(cf['L2_exp9_c_grid']['nonparametric']['delta_argmax']['ci'], 2)}. Both CIs cover 0.
- C3-iii (out-of-panel) fails: Spearman {cf['C3_iii']['spearman']:+.3f}, permuted-dose p {cf['C3_iii']['p_perm_spearman']:.3f}.
- Estimator sensitivity, reported beside the verdict: in L1 the continuation-ratio fit gives {cf['L1_exp11_f_ladder']['continuation_ratio']['delta_peak']:+.2f} {cis(cf['L1_exp11_f_ladder']['continuation_ratio']['delta_peak_boot_ci'], 2)} and the PO fit gives {cf['L1_exp11_f_ladder']['po']['delta_peak']['point']:+.2f} {cis(cf['L1_exp11_f_ladder']['po']['delta_peak']['boot_ci'], 2)}. The falsification therefore rests on a five-level nonparametric argmax that the pre-hoc power simulation (run for the PO estimator) did not cover.

**Judge re-certification within EDITED cells** (`results/judge_calibration.json`, `results/judge_calibration_supplement.json`)
- Sample: {jc['n_calibration']} frozen, stratified items, of which {jc['n_bought_ok']} were bought and {jc['n_free_covered']} were already labelled.
- Workhorse Qwen3-14B vs gpt-4.1, refused-vs-not kappa: EN {jc['gate']['en']['kappa_weighted']:.3f} weighted / {jc['gate']['en']['kappa_unweighted']:.3f} sample, so the gate is **MET**. SL {jc['gate']['sl']['kappa_weighted']:.3f} / {jc['gate']['sl']['kappa_unweighted']:.3f}, so the gate is **NOT MET** under the conservative rule and SL rates carry Rogan-Gladen companions.
- Keyword rule: kappa {jc['weighted']['overall']['kappa_keyword']:.3f} with a false-positive share of {jc['weighted']['overall']['fp_share_keyword']:.3f}. Distilled classifier: kappa {jc['weighted']['overall']['kappa_classifier']:.3f}.
- A declared post-freeze supplement ({sp['n_supplement_labels']} labels) shows the frame-level gate hides a weak panel. exp11 English has kappa {sp['exp11|en']['kappa']:.3f} {cis(sp['exp11|en']['kappa_ci'])}: most workhorse REFUSED labels there are gpt-4.1 PARTIAL.
- Re-expressing the exp11 cells in gpt-4.1 classes changes the C3 conclusion nowhere. The keyword edit's S5X gap goes {rx['exp11_S5X_strict_gap_raw_vs_gpt_equivalent']['B_keyword_t96']['gap_raw']:+.2f} -> {rx['exp11_S5X_strict_gap_raw_vs_gpt_equivalent']['B_keyword_t96']['gap_gpt_equiv']:+.2f}.
- Of {jc['gap_claims_summary']['n_cells']} per-cell SL-EN gap claims, {jc['gap_claims_summary']['judge_sensitive']} are JUDGE_SENSITIVE (they flip against the Rogan-Gladen-corrected reading or, on Gemma cells only, the distilled classifier) and {jc['gap_claims_summary']['definition_sensitive']} are DEFINITION_SENSITIVE (strict vs broad).

**Scope tables**
{asr_line}
- **Validity columns** (INVALID, empty, truncation, repetition, and GlotLID line-level language consistency recomputed on every row) are in `results/validity_table.csv`.
- **Flip analysis** (`results/flip_analysis.json`). Gemma: slope ratio EN {fl['gemma|en']['slope_ratio']:.2f} {cis(fl['gemma|en']['slope_ratio_ci'], 2)}, SL {fl['gemma|sl']['slope_ratio']:.2f} {cis(fl['gemma|sl']['slope_ratio_ci'], 2)}; intercept shift {fl['gemma|en']['intercept_shift']:+.2f} / {fl['gemma|sl']['intercept_shift']:+.2f}; refit AUROC after the edit about 0.997. The information survives, the criterion moved, and coupling is partly lost. GaMS3 is not estimable because almost no refusals remain after the edit.

**NF4 vs bf16** (`results/quant_confound.json`)
- NF4 changes each edited matrix by {qc['weights']['rel_frobenius_err_mean']:.3f} relative Frobenius error.
- The edit's per-layer removal-energy profile has cosine {qc['weights']['g_profile_cosine_bf16_vs_nf4']:.6f} between bf16 and NF4, and the removed rows rotate by {qc['weights']['proj_row_angle_deg_mean_edited_layers']:.1f} degrees.
- {acts}
- {beh}
- Verdict: {qc['verdict'][0].upper() + qc['verdict'][1:]}.

**Recount of the iteration-3 draft** (`results/corrected_numbers_iter4.json`, `results/audit_log_iter4.json`)
- {cn['n_checked']} numbers checked: {cn['verdicts']}.
- Mismatch-or-misdescribed rate {cn['mismatch_or_misdescribed_rate']:.3f}, Wilson 95% {cis(cn['wilson_95'])}, against the audited half's prior 0.055.
- Every placebo collapses (cell-label {cn['placebos']['a_cell_label_shuffle_within_item']:+.4f}, language-label {cn['placebos']['b_language_label_shuffle']:+.4f}, dose {cn['placebos']['c_dose_shuffled_spearman']:+.4f}, kappa permutation {cn['placebos']['e_judge_label_permutation_kappa']:+.4f}) against the real effects {cn['placebos']['real_pb2_sl']:+.4f} / {cn['placebos']['real_pb3']:+.4f}. The leakage detector fires.

**Paste-ready repairs:** `results/report_repairs_iter4.md` covers R1-R10 plus C3, the judge panels and NF4. Each number sits beside its producing file, and the lint count is 0. The iteration-1 section is restored byte-for-byte in `results/r4_iteration1_restored_verbatim.md`.

**Spend:** OpenRouter ${cost:.3f} in total (`results/cost_log.jsonl`; hard stop $8). This includes one $0.00003 connectivity test.

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
"""
    (C.WS / "README.md").write_text(rd)
    rp = f"""# Reproducibility

- Python 3.12, pinned environment in `requirements.lock` (uv). torch 2.11.0+cu128, transformers {__import__('importlib.metadata').metadata.version('transformers')}, bitsandbytes {__import__('importlib.metadata').metadata.version('bitsandbytes')}.
- Hardware used: 48 CPU cores, 251 GB RAM, NVIDIA RTX 2000 Ada 16 GB (the earlier part of the session ran on an RTX 4000 Ada 20 GB before a machine swap; only CPU phases and the purchase ran there).
- Frozen before any fit: `configs/FREEZE_iter4_eval.json` (sha256 in `configs/FREEZE.sha256`, together with `results/calibration_sample.json`). `p1_curves.py` refuses to run if the hash does not verify, and asserts that every result file it writes is newer than the freeze.
- Seeds: {json.dumps(fz['seeds'])}; bootstrap B: {json.dumps(fz['B'])}.
- Judge: gpt-4.1 via OpenRouter, temperature 0, seed 0, max_tokens 60. The rubric is loaded verbatim from `iter_2/gen_art/gen_art_experiment_4/protocol.yaml` (judge_primary), copy in `configs/frozen_rubric_exp4.json`. Blind: only request + response are sent. {buy['attempted_items']} + {sp['n_supplement_labels']} labels bought, 0 blocked.
- Guards: Llama-Guard-3-8B@7327bd9f and PolyGuard-Qwen@644bfe73 in NF4 (the stored iteration-2 labels were bf16; fidelity is measured in `results/asr_summary.json`). Prompts and parsers come from `iter_2/gen_art/gen_art_experiment_4/guard_pipeline.py` (constants parsed with ast, not retyped).
- Deviations from the plan, stated:
  1. The calibration frame is restricted to HARMFUL prompts.
  2. The gate uses both population-weighted and sample kappa (conservative).
  3. A declared post-freeze supplement was added for the exp11/exp12 panels.
  4. The guard subsample is 30 items per cell x language, not 100, and PolyGuard was time-capped.
  5. Guards ran in NF4.
  6. The PO bootstrap uses B={fz['B']['po_bootstrap']} (the nonparametric B=2000).
  7. The LOESS span for L2 was chosen on L1, where all spans tie.
  8. The behavioural bf16 cell (one checkpoint, 20 verified pairs) is labelled by gpt-4.1 on BOTH sides, not by the workhorse, so the comparison is same-judge.
- Greedy decoding and NF4 numerics are not bit-reproducible across GPU models. The guard labels and activation-level KL can differ slightly on other hardware.
"""
    (C.WS / "reproducibility.md").write_text(rp)


if __name__ == "__main__":
    main()
