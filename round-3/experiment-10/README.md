# Where to cut refusal in a bilingual model

`demo/` — Self-contained demo (Colab-ready notebook or markdown). Run without setup.  
`src/` — Full source code, data, and outputs from the experiment execution.

**Type:** experiment  
**ID:** `art_xLy2vVlI7OEL`

## Layman Summary

Tests whether spreading a safety-removal edit across more layers of a Slovene-English model unlocks Slovene, and finds that placing the edit on the right layers matters far more than spreading it.

## Full Summary

GaMS3-12B-Instruct half of the iteration-3 depth-coverage test. 57 cells, 10,690 judged generations, $0.00 OpenRouter spend (the run key was exhausted; judging is the local Qwen3-14B with iteration-2's frozen rubric).

PART A (DEV only, S3 JBB half A, 40 harmful+40 harmless per language). Cumulative-prefix / suffix / leave-one-band-out ablation of the FROZEN per-layer English refusal directions d_EN(h) reused from art_hmbXDppkPZnR (cos>=0.9964 vs a fresh recompute at every h). index_EN=16 [16,16], index_SL=20 [16,24], difference 4 [0,8] -> PA1 EQUIVALENT_WITHIN_MARGIN against the pre-declared +/-8 margin (Holm p 0.069). CRITICAL CAVEAT: the co-primary USABLE index (refusal<0.5 AND INVALID<=0.10) is '>48' in BOTH languages - activation-space depth coverage only removes refusal by destroying the model (INVALID 0.72 EN / 0.38 SL at the crossing, FLORES +1.4 nats).

PART B (the decisive panel). Heretic's own abliterate() generalised to arbitrary per-(layer,component) weights (heretic_op.py; operator-equivalence vs Heretic's own source max rel err 1.7e-06; trial-88 adapter rebuild median 3.3e-07; energy identity <1e-06). 3 matched-total-removal-energy groups (E*=6.9/13.9/27.8, every member within 2%), each with narrow bands B2/B3, spread sets STR4/STR2/ALL, plus no-op, layer-matched RANDOM and energy-matched PC controls; anchors G1 single-site, CORE trial-88 adapter, SWAP_in (Gemma trial-96 kernel); plus a 10-cell coverage grid at c=1.

HEADLINE RESULTS (confirmation = S4 held-out Llama-Guard categories, 70 pairs/language, frozen BEFORE generation; freeze mtime precedes all 25 confirmation files):
- PB2 FALSIFIED IN THE OPPOSITE DIRECTION: narrow-and-strong minus broad-and-weak SL refusal = -0.10 [-0.150,-0.060]; CONCENTRATING the same energy on one 12-layer band beats spreading it (Holm p 0.000).
- PB3 FALSIFIED OPPOSITE: coverage x language interaction -0.07 [-0.131,-0.007]; the advantage of concentrating is LARGER in Slovene.
- Placement at matched energy AND matched layer count (12 contiguous vs every 4th): SL 0.24 vs 0.81 (E3), 0.51 vs 0.89 (E2), 0.83 vs 0.93 (E1), every CI excluding 0.
- PB1 NOT SUPPORTED: coverage dR2 = 0.002 [0.000,0.010] over 26 cells; leave-one-cell-out dR2 = -0.043. Nested decomposition: log E alone R2 0.325 -> +WHERE the energy sits (band fractions) 0.718 -> +HOW MANY layers 0.400. Placement, not coverage count, carries the variance.
- PB4 NOT SUPPORTED (Spearman 0.21): a count-based index cannot express placement (it gives a 12-layer band and 12 spread layers the same prediction).
- Band profile at c=1 (SL): layers 1-12 0.93, 13-24 0.24, 25-36 0.02, 37-48 0.85.
- Controls null everywhere: random / PC at matched energy leave SL refusal 0.93-0.95 (screen) vs no-op 0.93.
- OPERATOR MATTERS MORE THAN DEPTH: the same directions as Heretic's row-norm-preserving weight edit remove refusal at ~zero collateral (|SL FLORES dNLL| <= 0.011, MC accuracy within 0.031 of no-op, INVALID ~0.01), while the raw activation projection of those same directions breaks the model.
- CROSS-MODEL (descriptive, n=2): the sibling iteration-3 Gemma pod independently reports index_EN=16 / index_SL=20 - identical to GaMS3. The Slovene lag is common to both checkpoints, so it is NOT what distinguishes them; no difference is attributed to any training stage.

AUDIT: rederive.py re-derives 481/481 headline numbers (228 per-cell rates, 24 prefix points, 2 indices, PB1/PB2/PB3/PB4, the nested R2 decomposition, 218 exact McNemar tests) from the raw per-generation files through a code path importing nothing from the analysis; freeze-order check PASS; three placebos collapse (cell-label-within-item 0.003, language-label -0.001, energy-shuffled 0.023) against real effects of -0.105 and -0.071.

JUDGE LIMITATION: on-disk certification vs gpt-4.1 gives kappa 0.86 Slovene but 0.54 English within EDITED arms (paid top-up impossible, HTTP 403), so English rates are the strict end of a judge range; PARTIAL is always its own column. GaMS3's shipped edit already left only 0.10 SL refusal, so this panel measures trade-offs, not a rescue. S5/S6/S7 never opened; ASR and the lm-eval macro not run (deviations.json, 9 entries).

OUTPUT LAYOUT: method_out.json IS the comparison table - 462 examples (one per split x item x language) x 56 distinct predict_<method> fields = 10,690 per-item outcomes, exactly the 10,690 generations produced. `output` is the UNEDITED model's 4-way class; each predict_<method> is the class the same item got under one intervention that ran (band edits, matched-energy spread edits, random/PC controls, prefix/suffix/LOBO activation arms, single-site ablation, shipped Heretic edit, Gemma kernel swap), with its text, gpt-4.1 label, rule label and GlotLID language in metadata_*. Headline recomputes from this file alone: SL narrow-broad -0.1048 over n=70; controls null at 0.957 vs 0.957 baseline.

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
