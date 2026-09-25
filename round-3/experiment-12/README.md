# Depth index fails to predict cross-lingual refusal-edit failure

`demo/` — Self-contained demo (Colab-ready notebook or markdown). Run without setup.  
`src/` — Full source code, data, and outputs from the experiment execution.

**Type:** experiment  
**ID:** `art_kfCCWf7o8eJ9`

## Layman Summary

English-only edits that stop an AI refusing often leave it still refusing in other languages. Our pre-registered predictor of which languages resist failed; two far simpler measurements predicted it well.

## Full Summary

Iteration-3 predictive test in google/gemma-3-12b-it (anchor, NF4, pinned 96b6f1ec), Qwen/Qwen3-8B and mistralai/Mistral-7B-Instruct-v0.3 (EuroLLM-9B-Instruct was the planned M3 but is gated and returned HTTP 403; the recorded fallback order was followed, results/load_log.json), in EN/SL plus DE/LT newly translated with NLLB-200-distilled-1.3B. QUESTION: can iteration-2's depth-redundancy observation be turned into a PREDICTIVE instrument? A per-language index (smallest cumulative depth coverage of d_EN(h) activation ablation at which judged harmful refusal falls below 0.5, measured on DEV-only S3 JBB half-B items) was computed, FROZEN and hashed (configs/frozen_predictions.json in configs/FREEZE.sha256; run_model.py --phase conf raises without it) BEFORE any confirmation generation, then tested out of sample on 60 held-out StrongREJECT harmful items per language (30 held-out-category + 30 in-distribution, paired by semantic id) against English-derived Heretic-operator WEIGHT edits (Heretic 3521f864's projected, row-norm-preserving rank-3 LoRA with OUR per-layer directions injected): W0 no-op, W1 narrow 25%-depth band, W2 energy-matched all-depth stride, W3 selected kernel (Gemma = the REAL iteration-1 trial-96 adapter, sha256-verified), W4 energy- AND collateral-matched random. RESULT: the pre-registered claim is FALSIFIED. P1 pooled Spearman(index, residual refusal) = -0.009 [-0.131, 0.192] over 21 rows (permutation p 0.16); the AUC secondary gives +0.167; P2 concordance 8/12 decided (0.67, below the 0.75 bar, and 6/12 under judge-error correction); P3 alone holds in sign (Spearman(index, W2-W1) = -0.474). CRITICALLY, EN/L direction cosine ALSO fails (+0.010), so the 'familiar geometry stops predicting' boundary is real but stops for our index too, while two CHEAP baselines beat both by margins whose paired item-bootstrap CIs exclude zero: single-site transfer rho +0.732 (index-baseline -0.741 [-0.810, -0.528]) and the unedited model's baseline refusal in that language rho +0.661 (-0.670 [-0.721, -0.497]). Gemma's real trial-96 adapter on held-out items leaves EN 0.60 / DE 0.53 / LT 0.75 / SL 0.92 from a 0.93-0.98 no-op, replicating the iteration-1/2 English-Slovene asymmetry on a new harm source and extending it to two new languages; its energy- and collateral-matched random control leaves SL at 0.98, and the SL-NLLB vs SL-gpt translation-method control moves every rate by <=0.09, closing that confound. POST-HOC (exploratory, changes no verdict, prompted by the language-shuffle placebo returning -0.356 instead of ~0): within the anchor model the index DOES order the languages (rho +0.678) but Qwen3's eligible languages all share one index value so it has zero variance there; pooled within-model-centred rho is +0.458 (AUC +0.620), and cosine REVERSES sign between models (-0.748 gemma, +0.556 qwen3). The frozen eligibility gate did real work pre-hoc: Mistral refuses only 0.07-0.53 at baseline (0.07 in Lithuanian) so all four of its rows were excluded before any confirmation data existed, and it was dropped from the weight panel under the pre-registered cut order rather than swapped silently. AUDIT: rederive.py (stdlib+numpy only, reading only raw generations, labels and the frozen file) reproduces every index, AUC, eligibility flag, residual and P1-P4 statistic: 102 checks, 0 mismatches; placebos (b) index permutation -0.009, (c) label swap flips sign, (d) DEV-as-CONF correctly flagged LEAKAGE. Positive control 4/4: the Gemma DEV curve reproduces iteration-2's anchor (EN P50 0.39 vs 0.42, SL P75 0.27 vs 0.21). JUDGE LIMITATION, reported not buried: the run's OpenRouter budget was exhausted before this artifact began ($0.00 spent here), so gpt-4.1 was unavailable and the planned fallback could not fire; the local Qwen3-14B judge (rubric variant chosen on a DEV split of the free existing gpt-4.1 label pool, certified once on a disjoint holdout) reaches kappa 0.683 [0.629, 0.737], BELOW its 0.80 gate, with Se 0.984 / Sp 0.741, so absolute refusal levels are biased upward and a Rogan-Gladen corrected re-run of P1/P2 is reported. analysis.py was patched after the freeze for numerical robustness only (empty-bootstrap quantile; undefined differences must not count as decided); both hashes and the full diff are in results/analysis_patch.json and checks.py flags analysis_py_unchanged=false. Native review PENDING. 9,199 blind 4-way judged generations; method_out.json has 8,520 per-example rows. Workspace: /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/gen_art/gen_art_experiment_12

## Dependencies

- `art_qdUCJWbc5kHh` — dataset

## Output Files

- `method.py`
- `full_method_out.json`
- `mini_method_out.json`
- `preview_method_out.json`
- `reproducibility.md`

## Demo Files

- **method.py** — Research methodology implementation

---
*Generated by AI Inventor Pipeline*
