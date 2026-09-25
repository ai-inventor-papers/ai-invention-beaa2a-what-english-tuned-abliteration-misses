## What was done

This is the first real run of the main-hypothesis **P1 random-edit panel** on `cjvt/GaMS3-12B-Instruct@1d0b27af`. The model
runs in bnb_4bit NF4 with bf16 compute on an RTX 4090. Edits use Heretic `3521f864` with its default operator: LoRA
abliteration, `orthogonalize_direction=true`, `row_normalization=full`, rank 3.

**Edits.** Every edit is rebuilt with Heretic's own code: `Model.reset_model()` followed by
`Model.abliterate(directions, direction_index, parameters)`. The directions are iteration-1's S1 per-layer refusal
directions (`directions/gams/directions.pt`).

| set | size | source |
|---|---|---|
| E0 | 60 | iteration-1 journal trials 0-59 (the TPE startup draws) |
| E_TPE | 56 | journal trials 60-115; out of sample; contains core trial 88 (EN 16/100 refusals, KL 0.175) |
| E1 | 100 | fresh prior draws, seed 20260925 |
| E_R | 30 | prior draws from the reserved seed 20260924; out of sample |

E1 and E_R are drawn with Heretic's own `suggest_*` code under `TPESampler(n_startup_trials=inf)`. Two certificates check
this:
- **U1:** it reproduces journal trials 0-59 exactly (max |diff| = 0).
- **U1b:** `RandomSampler(seed)` gives the same draws, so the sibling Gemma pod gets identical edits.

The fitted set F is the non-collapsed E0 + E1 edits.

**Traits.** All traits are teacher-forced and scored per item, in EN and SL, on the S3 DEV halves A/B:

| trait | definition | items |
|---|---|---|
| `R` (R_seq) | mean log p(24-token refusal reference) − mean log p(24-token compliance reference) | 85 JBB harmful |
| `R1` | first-token refusal-set vs compliance-set log-odds | 85 JBB harmful |
| `Rb` | R_seq on the benign twins | 85 JBB benign |
| `K` | log of the mean truncated KL (top-256 + tail bucket) of the original's own 32-token greedy continuations | 100 Dolly prompts |
| `N` | per-token NLL rise | 200 FLORES dev sentences |
| `M` | change in the length-normalised gold-vs-best-distractor margin | 120 MC items (ARC-C / HellaSwag / PIQA) |

References come from the original model's generation when it refused, otherwise from the modal refusal opener. Compliance
references come from the core edit's generation when it complied, otherwise from the modal compliance opener.

**Per-edit covariates.** None of these needs a forward pass:
- Exposure **D = log E_SL − log E_EN**, where E is the mean ‖B A x‖² over 384 cached `o_proj`/`down_proj` input tokens per
  language. The tokens come from the original model's responses to 64 fresh, disjoint Dolly prompts (X_SET).
- The mean and variance split of D, and a per-response version.
- The realized LoRA energy on the Dolly continuations.
- **H:** harm-evidence removal along the frozen iteration-1 d_EN at hidden index 34.
- **P:** removal along r_prior, when r_prior is defined.
- Static baselines: `b1` (kernel-weighted EN/SL direction cosine), `b1x`, `b2` (|cos| of the used direction with the
  language direction), `b3` (kernel mass in 4 bands × 2 components, plus the total), and `Omega` (the share of LoRA
  energy in an LSAR-style 8-dim EN↔SL FLORES subspace).

**Analysis (`analysis.py`, frozen in `results/frozen_protocol.json` before any panel trait existed).**
- **Gap_t** = R²*(EN_A → EN_B) − R²*(EN_A → SL_B), averaged with the A↔B swap. Each R² is divided by its target's
  Spearman-Brown split-half ceiling. The learner is HistGBT, with ridge-on-splines as a sensitivity check.
- **Joint edit × item bootstrap:** edits are resampled together with sids within each family and half. EN/SL versions and
  harmful/benign twins move together, and CV is grouped by the original edit.
- **Tests:**
  - Holm over {K, N, M}.
  - **B_t**, the Heretic-parameter increment, with a stratified conditional permutation null.
  - SIMEX for noise in the predictors.
  - Stability across edit halves.
  - An MT-quality subset.
  - An **entropy-balanced margin-matched Gap** (the A4 rival).
- **Carrier regression:** the target is the SL-minus-EN out-of-fold residual. It reports ΔR²(C | S0) and ΔR²(S0 | C) for
  C ∈ {D, H, P, realized}, both ridge (primary) and GBT, plus an HC3 OLS coefficient.
- **Forecast:** SL traits are predicted from EN traits with CV+ conformal 90% PIs. Coverage is checked on the never-fitted
  E_TPE and E_R edits, together with the core-trial excess and a kNN support check.
- **Other outputs:** a secondary Gap_Heretic computed from the journal objective alone, and bilingual post-hoc reselection
  over the journal trials under the frozen iteration-1 rule with refusals := max(EN, SL_est).
- **Validity gate:** blind judge labels on 20 harmful + 20 benign half-B twins per language, for the original, the core
  edit and every 10th fitted edit. The planned judges were gpt-4.1 (primary) and gemini-2.5-flash (second judge on a
  stratified 200). The run-level OpenRouter budget ran out after gpt-4.1 had labelled most of the Stage-0c and early
  validity generations, so the remaining generations, and the second-judge role, use a local Qwen3-14B judge (4-bit; D20) with the
  same rubric (`local_judge.py`). The gate uses gpt-4.1 labels where they exist and local labels otherwise, and it is also
  reported for each label source alone.
- **Verdict:** `results/verdict.json` applies the frozen rules mechanically.
