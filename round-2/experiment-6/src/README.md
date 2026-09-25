# P1 random-edit panel on GaMS3-12B-Instruct: what English Heretic edits miss in Slovene

Iteration-2 experiment of run `run_Fapgmt6JWbcD` (artifact `gen_art_experiment_6`). Up to 246 Heretic abliteration edits (journal startup draws, journal TPE trials, fresh prior draws and a reserved-seed out-of-sample set) are rebuilt through Heretic's own code on `cjvt/GaMS3-12B-Instruct`. Each edit is scored in English and Slovene on teacher-forced refusal, divergence, language-NLL and multiple-choice traits. The question is whether the English traits, which are all Heretic's optimiser sees, are a sufficient surrogate for the same traits in Slovene. The test compares EN->SL prediction with a same-language EN->EN placebo on independent items, each normalised by its own noise ceiling.

## Headline results

- **Panel.** 246 Heretic edits scored. The fitted set F has 160 non-collapsed E0+E1 edits (floor 150: True); 0 fitted edits collapsed (Dolly NLL rise > 1 nat/token). The primary learner is gbt and the joint edit x item bootstrap uses B = 1000.
- **Refusal-proxy validity** (gpt-4.1 where labelled, else local Qwen3-14B (same rubric)). Spearman(condition R_seq, judged refusal rate) is EN 0.970 and SL 0.910 over 18 validity conditions; for R1 it is EN 0.937 and SL 0.886. REF = **R** (gate 0.85 in both languages).
- **Claim 1: refusal removal is visible in Slovene.** Gap_R = 0.015 (90% CI [0.008, 0.027], MDE 0.018), so the TOST within +/-0.10 **HOLDS** (confirmatory). English half-A traits predict Slovene half-B refusal as well as they predict English half-B refusal: R2* = 0.968 vs 0.983.
- **Exploratory, post-freeze: SL is predictable but attenuated.** Per unit of English change on independent items, the Slovene R_seq moves 0.82x (95% CI [0.74, 0.90]). The ratio is 0.50x for R1, 0.99x for Rb and 0.39x [0.34, 0.48] for K. Relative to each language's own original level, the SL/EN R_seq change ratio is 1.28.
- **Main hypothesis (damage blind to English): SUPPORTED.** K: Gap 0.147 [0.074, 0.265], label 'BLIND' (confirmatory, MDE 0.137); N: Gap -0.642 [-14.817, 0.984], label 'no signal to predict' (exploratory, MDE 32.157); M: Gap 0.040 [-8.373, 5.221], label 'no signal to predict' (exploratory, MDE 21.854).
- **Exposure carrier D** (dR2 over the static baselines S0 = cosine, entanglement, band mass, Omega; ridge, out of fold): R -0.026 [-0.065, -0.002]; R1 -0.013 [-0.023, -0.003]; Rb 0.011 [-0.012, 0.020]; K -0.011 [-0.058, 0.027]; N -0.016 [-0.063, 0.018]; M 0.001 [-0.005, 0.008]. Frozen carrier rule met: False (confirmatory).
- **Frozen predictions.** G1 True, G2 True, G3 True (with the B CI: True), G4 False, G5 rule-labelled False / judge False, G6 False (share of trait x set meeting 85% coverage: 0.50).
- **Bilingual reselection** (logistic map of SL R_seq -> judged refusal on validity conditions): the rule refusals := max(EN, SL_est) selects ETPE_088 (EN 16, SL_est 1.1, KL 0.175). The core trial's SL_est is 1.1. Some trial reaches SL_est <= 20 at KL <= 1: True.
- **API spend** for this artifact: $1.06 (cap $7 hard stop, $10 budget).

## Interpretation, failed predictions and limits

**Observations.**
- English half-A traits predict the Slovene half-B refusal traits almost as well as they predict the English half-B traits: R2* EN->SL is 0.968 for R_seq, 0.956 for R1 and 0.954 for Rb. Refusal suppression by these edits is therefore *visible* from English at the edit level (claim 1).
- Visible does not mean equal in size. Per unit of English change, Slovene R_seq moves 0.82x, R1 0.50x and the harmless-KL trait K only 0.39x. The benign-twin trait Rb moves 0.99x. So Slovene is systematically attenuated but predictable (exploratory; not a frozen rule).
- **K (harmless divergence on Dolly continuations) is the one trait English misses.** EN half-A traits explain R2* = 0.977 of reliable EN_B K variance but only 0.830 of SL_B K variance: Gap_K = 0.147 (95% CI [0.074, 0.265], MDE 0.137, Holm p 0.000). It survives every frozen check: SIMEX 0.112, margin-matched 0.131 [0.078, 0.241], edit halves 0.118 / 0.150, ridge learner 0.129, and B_K = 0.050 [0.001, 0.121] (Heretic's own parameters add SL-specific information). Frozen label: 'BLIND' (confirmatory). With Slovene as the source the gap reverses (-0.124): each language's K predicts itself better than the other's, so K has a language-specific, edit-dependent component.
- 'Blind' here is about *which* edits hurt Slovene, not about Slovene being hurt more on average: Slovene KL is smaller than English KL for most edits (mean-change ratio 0.59, slope ratio 0.39), but a subset of edits push Slovene divergence up relative to English (`fig8`, middle), and English traits cannot rank them.
- Boundary: on the 116 journal trials (E0 + E_TPE) with only Heretic's own objective (EN keyword refusals + log first-token KL) as X, SL K is as predictable as EN K (Gap_Heretic_K = 0.018). That analysis differs in both the predictors and the edit set, so it only suggests that the blind component lives in the wider prior (E0 + E1) rather than in the region TPE explores; it does not isolate which difference matters.
- N (FLORES NLL rise) and M (MC margin change) barely move under any edit. The F8 rule labels them 'no signal to predict' and 'no signal to predict': with these automatic traits, no language damage is visible to predict in either language. This repeats iteration 1's finding at the core checkpoints, now across the whole edit distribution.
- **Carrier.** The frozen exposure carrier D fails (G4): over the static baselines it adds -0.011 [-0.058, 0.027] for the K residual and nothing for any other trait. Exploratory, post-freeze: the language-divergence ratio log(KL_SL/KL_EN) tracks the depth of the layer Heretic takes its refusal direction from (Spearman 0.77; late-layer directions hit Slovene relatively hardest; `fig8`, left). EN traits plus S0 predict this ratio with CV R2 0.77. Source-layer geometry adds 0.047 (95% CI [0.008, 0.074]; GBT 0.069) and exposure D adds 0.020 [-0.006, 0.043]. The source layer is the lead for the next iteration, but it was chosen after seeing the data and misses the frozen 0.05 bar under ridge.

**Failed or unsupported predictions.** See the scorecard table. The main-hypothesis prediction G3 (a blind damage trait) is evaluated mechanically, together with the carrier prediction G4 (exposure D) and G5 (r_prior undefined for GaMS3). Under both rule and judge labels, the original GaMS3 refuses at least 10 harmless half-A prompts, so r_prior is defined and the P covariate was computed.

**Limits.**
- One model (GaMS3) and one Heretic optimiser seed. Optimiser-run variance is not measured. Joining this pod with the Gemma P1 pod (identical E0/E1/E_R edits, certified in `results/unit_tests.json` U1b_sibling_diff) gives n = 2 models; nothing is attributed to training stages.
- Numerics: the per-item truncated KL of weak edits moves by 17-26% of its mean when re-scored on a different GPU model (`results/repro_check.json`); the two RTX 4090 hosts that scored the panel show no offset (`host_check.py`). K for the weakest edits therefore carries a hardware-dependent floor; all panel comparisons are within one GPU model.
- The traits are teacher-forced automatic proxies (4-bit NF4, 24-token references). A Gap near 0 on the damage traits means 'no blind damage visible to these automatic traits', not 'no damage'.
- Judging: gpt-4.1 labelled 1130/2140 generations before the run-level OpenRouter budget ($7 for the whole 'Test idea' phase, shared by all pods) ran out at 00:04 UTC. The rest, and the planned gemini-2.5-flash second judge, were replaced by a local Qwen3-14B judge (4-bit) using the same rubric; the free-tier models were also exhausted for the day (deviation D20). It agrees with gpt-4.1 at kappa 0.875 (refused vs not; EN 0.919, SL 0.831) and 0.702 (6-way) on 1130 shared generations. Qwen3 is from a different family than GaMS3 (Gemma-3) and gpt-4.1. Nine of the 18 validity conditions per language are labelled by it alone. The validity gate is also reported for gpt-4.1-only, local-only and rule labels.
- Slovene items are machine-translated with automated QC only; native review is pending. The X_SET exposure prompts were translated with NLLB, because the primary translator was blocked.
- The fitted set is 160 edits (floor 150: True). Labels are confirmatory only where the frozen gates (reliability >= 0.6, MDE <= 0.15, refusal validity >= 0.85) all hold; each trait's status is in `results/verdict.json`.

## Independent re-derivation of the headline numbers (`rederive_headlines.py`)

A separate script reads the raw per-item parquets and judge labels, and re-derives the numbers with its own aggregation, ceilings and learners (ExtraTrees(300, leaf 3, 10-fold) and numpy LOO quadratic ridge (lambda 1); predictors = EN R, R1, Rb, K of the source half (N, M omitted: F8 no-signal); primary analysis used all six + HistGBT). Gap_K = 0.115 (ExtraTrees) / 0.105 (LOO ridge) vs the primary 0.147: the >= 0.10 'blind' bar is met by both independent learners, but the magnitude is learner-dependent. Gap_R = 0.009 / 0.010 (primary 0.015). Validity Spearman EN 0.970, SL 0.910; judge kappa 0.875 (refused vs not). Placebos, each of which must FAIL the claim: K self-placebo Gap 0.000, noise-matched placebo -0.001; R with SL shuffled across edits 1.068 (the 'visible' claim breaks); validity with shuffled rates mean rho EN -0.000 / SL 0.014; kappa with shuffled labels 0.001.

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

## Results tables (generated by `summary_tables.py` from `results/analysis_results.json`)

Fitted set F = 160 non-collapsed E0+E1 edits (0 collapsed fitted edits excluded); primary learner = gbt; bootstrap B = 1000.

| trait | R2 EN->EN (raw) | R2 EN->SL (raw) | ceil EN_B | ceil SL_B | R2* plac | R2* test | **Gap** | 95% CI | 90% CI | MDE | Holm p | B_t [95% CI] | Gap_mm [95% CI] | Gap_SIMEX | halves |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R | 0.982 | 0.967 | 0.999 | 0.999 | 0.983 | 0.968 | **0.015** | [0.006, 0.031] | [0.008, 0.027] | 0.018 | NA | 0.004 [-0.004, 0.009] | 0.017 [0.007, 0.038] | 0.012 | 0.025 / 0.009 |
| R1 | 0.997 | 0.954 | 0.999 | 0.998 | 0.998 | 0.956 | **0.042** | [0.027, 0.070] | [0.029, 0.067] | 0.032 | NA | 0.015 [0.002, 0.030] | NA [NA, NA] | 0.052 | 0.054 / 0.050 |
| Rb | 0.979 | 0.953 | 0.997 | 0.999 | 0.982 | 0.954 | **0.028** | [0.012, 0.068] | [0.014, 0.060] | 0.041 | NA | 0.005 [-0.007, 0.013] | 0.029 [0.017, 0.081] | 0.016 | 0.033 / 0.037 |
| K | 0.971 | 0.823 | 0.993 | 0.992 | 0.977 | 0.830 | **0.147** | [0.074, 0.265] | [0.083, 0.249] | 0.137 | 0.000 | 0.050 [0.001, 0.121] | 0.131 [0.078, 0.241] | 0.112 | 0.118 / 0.150 |
| N | -0.065 | 0.310 | 0.384 | 0.722 | -0.225 | 0.417 | **-0.642** | [-14.817, 0.984] | [-8.648, 0.450] | 32.157 | 0.954 | -0.061 [-0.290, 0.449] | 0.057 [-19.538, 8.044] | -0.375 | -0.271 / -1.214 |
| M | 0.151 | 0.057 | 0.630 | -0.363 | 0.272 | 0.232 | **0.040** | [-8.373, 5.221] | [-3.704, 2.398] | 21.854 | 0.954 | -0.144 [-0.372, 0.555] | -4.571 [-20.969, 1.937] | 0.217 | -0.148 / -0.786 |

Reliabilities (Spearman-Brown, split-half, fitted set):

| trait | EN_A | EN_B | SL_A | SL_B | no-signal (F8) EN / SL |
|---|---|---|---|---|---|
| R | 1.000 | 0.999 | 1.000 | 0.999 | False / False |
| R1 | 0.999 | 0.999 | 0.999 | 0.998 | False / False |
| Rb | 0.998 | 0.997 | 0.999 | 0.999 | False / False |
| K | 0.995 | 0.993 | 0.990 | 0.992 | False / False |
| N | 0.313 | 0.384 | 0.757 | 0.722 | True / False |
| M | 0.439 | 0.630 | 0.712 | -0.363 | True / True |

Carrier regression on y_t = SL residual - EN residual (ridge, out-of-fold; S0 = b1, b1x, b2, b3 x9, Omega):

| trait | R2(S0) | dR2(D given S0) [95% CI] | dR2(S0 given D) | dR2(H given S0) | dR2(realized given S0) | dR2(P given S0) | OLS std coef of D [95% CI] |
|---|---|---|---|---|---|---|---|
| R | 0.075 | -0.026 [-0.065, -0.002] | 0.058 | -0.009 | -0.013 | 0.002 | 0.003 [-0.003, 0.008] |
| R1 | 0.208 | -0.013 [-0.023, -0.003] | 0.191 | -0.005 | -0.009 | -0.002 | -0.015 [-0.090, 0.059] |
| Rb | -0.077 | 0.011 [-0.012, 0.020] | -0.045 | -0.002 | 0.012 | -0.006 | -0.000 [-0.006, 0.005] |
| K | 0.215 | -0.011 [-0.058, 0.027] | 0.164 | 0.028 | -0.004 | 0.018 | 0.036 [-0.011, 0.082] |
| N | -0.032 | -0.016 [-0.063, 0.018] | -0.028 | 0.006 | -0.007 | 0.004 | 0.000 [-0.001, 0.001] |
| M | -0.041 | 0.001 [-0.005, 0.008] | -0.020 | -0.001 | 0.004 | -0.001 | 0.000 [-0.001, 0.002] |

Out-of-sample forecast (90% CV+ conformal PI of SL traits from EN traits; never-fitted edits):

| trait | coverage E_TPE | coverage E_R | +D: E_TPE | +D: E_R | core observed | core predicted | core excess | outside PI | out of support |
|---|---|---|---|---|---|---|---|---|---|
| R | 0.71 | 0.97 | 0.71 | 1.00 | -0.458 | -0.198 | -0.259 | True | True |
| R1 | 0.95 | 0.93 | 0.93 | 1.00 | -3.323 | -3.141 | -0.181 | False | True |
| Rb | 0.59 | 0.77 | 0.61 | 0.83 | -0.386 | -0.270 | -0.117 | True | True |
| K | 0.82 | 0.93 | 0.84 | 0.97 | -4.405 | -4.903 | 0.498 | True | True |
| N | 0.62 | 0.93 | 0.68 | 1.00 | 0.001 | 0.004 | -0.003 | True | True |
| M | 0.84 | 0.93 | 0.79 | 0.90 | -0.002 | -0.003 | 0.001 | False | True |

Secondary Gap_Heretic (X = journal EN keyword refusals + log KL, E0+E_TPE):

| trait | R2* EN | R2* SL | Gap_Heretic |
|---|---|---|---|
| R | 0.862 | 0.875 | -0.012 |
| R1 | 0.895 | 0.865 | 0.030 |
| Rb | 0.701 | 0.817 | -0.116 |
| K | 0.915 | 0.897 | 0.018 |
| N | -0.301 | 0.363 | -0.664 |
| M | 0.364 | -7.024 | 7.387 |

Validity gate (gpt-4.1 where labelled, else local Qwen3-14B (same rubric)): REF = R; en: n_cond 18, rho(R_seq) 0.970 [0.878, 0.993], rho(R1) 0.937, AUROC item R_seq 0.905; sl: n_cond 18, rho(R_seq) 0.910 [0.674, 0.983], rho(R1) 0.886, AUROC item R_seq 0.846

Bilingual reselection (logistic map of SL R_seq -> judged refusal on validity conditions): selected ETPE_088 = {'EN_refusals': 16.0, 'SL_est': 1.084590805845597, 'KL': 0.17493541538715363, 'R_seq_en': -0.164784778128652, 'R_seq_sl': -0.45753266451989905}; any trial with SL_est <= 20 at KL <= 1: True; core SL_est 1.1.

Unit tests: U1 True, U1b True, U1c True, U2 True (max rel diff 0.0000037), U3 True, U7 gen False / tf False; U4 True, U5 ratio 1.026.

Gap robustness (point estimates; 2 CV repeats): other learner / collapsed edits included / SL half-A as the source / MT-stable items only / low-R x low-K stratum (descriptive):

| trait | other learner | with collapsed | reverse (SL_A source) | MT-stable subset | stratum n | stratum Gap |
|---|---|---|---|---|---|---|
| R | 0.016 | 0.014 | -0.016 | 0.013 | 11 | NA |
| R1 | 0.034 | 0.044 | -0.036 | 0.046 | 11 | NA |
| Rb | 0.031 | 0.027 | -0.026 | 0.028 | 11 | NA |
| K | 0.129 | 0.142 | -0.124 | 0.138 | 11 | NA |
| N | -0.339 | -0.651 | -1.160 | -0.651 | 11 | NA |
| M | -0.003 | 0.084 | -0.268 | 0.084 | 11 | NA |

Item x edit mixed model (half-B items; d ~ ENt*margin + lang + lang:ENt + (1|item) + (1|edit); standardized ENt, margin; descriptive p-values):

| trait | n rows | lang [95% CI] | lang:ENt [95% CI] | ENt | margin | ENt:margin |
|---|---|---|---|---|---|---|
| R | 13120 | 0.1007 [0.0972, 0.1041] | -0.0528 [-0.0559, -0.0497] | 0.2735 | 0.0578 | -0.0072 |
| M | 20480 | 0.0003 [-0.0006, 0.0013] | -0.0022 [-0.0031, -0.0013] | 0.0026 | -0.0120 | 0.0022 |

EXPLORATORY transfer slopes (post-freeze): how much the SL trait moves per unit EN move, on independent items (slope dSL_B~dEN_A over placebo slope dEN_B~dEN_A; 1 = equal response):

| trait | slope placebo | slope test [95% CI] | **ratio** [95% CI] | mean-change ratio SL/EN [95% CI] | relative-to-baseline ratio |
|---|---|---|---|---|---|
| R | 0.978 | 0.800 [0.714, 0.891] | **0.818** [0.744, 0.904] | 0.787 [0.718, 0.867] | 1.278 |
| R1 | 1.020 | 0.514 [0.455, 0.563] | **0.504** [0.460, 0.547] | 0.419 [0.381, 0.455] | 1.083 |
| Rb | 1.027 | 1.020 [0.787, 1.273] | **0.993** [0.874, 1.121] | 0.960 [0.826, 1.113] | 2.585 |
| K | 1.042 | 0.410 [0.302, 0.538] | **0.394** [0.336, 0.475] | 0.587 [0.519, 0.691] | NA |
| N | 0.316 | 0.068 [-0.391, 0.503] | **0.216** [-11.465, 5.461] | -0.565 [-8.232, 0.810] | NA |
| M | 0.573 | 0.019 [-0.155, 0.210] | **0.033** [-1.517, 2.208] | -0.052 [-2.545, 4.182] | NA |

EXPLORATORY parameter attribution of B_t (add-one increment of each raw Heretic parameter, SL minus EN; top 3):

| trait | top parameters (increment) |
|---|---|
| R | attn.o_proj.max_weight_position 0.003; mlp.down_proj.min_weight 0.001; direction_index 0.001 |
| R1 | mlp.down_proj.max_weight 0.010; attn.o_proj.min_weight_distance 0.006; attn.o_proj.max_weight 0.003 |
| Rb | attn.o_proj.max_weight_position 0.004; mlp.down_proj.min_weight 0.003; direction_index 0.001 |
| K | direction_index 0.030; mlp.down_proj.max_weight_position 0.018; mlp.down_proj.max_weight 0.016 |
| N | attn.o_proj.max_weight_position 0.129; mlp.down_proj.max_weight 0.008; attn.o_proj.min_weight_distance 0.008 |
| M | attn.o_proj.min_weight_distance 0.111; direction_index 0.047; scope_per_layer 0.042 |

EXPLORATORY language-divergence ratio y = log(mean KL_trunc SL_B / mean KL_trunc EN_B) (n = 160, sd 0.303). CV R2 of each block alone (ridge): X 0.592, S0 0.288, D 0.192, SRC 0.598, H 0.228, P 0.367; GBT: X 0.551, S0 0.422, D 0.191, SRC 0.655, H 0.175, P 0.252. Base X+S0 R2 = 0.767.

| carrier C | dR2(C given X+S0) ridge [95% CI] | dR2(C given X+S0) GBT | dR2(C given X) ridge [95% CI] | Spearman(C, y) |
|---|---|---|---|---|
| D | 0.020 [-0.006, 0.043] | 0.023 | 0.035 [-0.007, 0.073] | 0.475 |
| SRC | 0.047 [0.008, 0.074] | 0.069 | 0.132 [0.048, 0.204] | 0.767 (depth) |
| H | 0.015 [-0.005, 0.030] | -0.004 | 0.046 [0.004, 0.079] |  |
| P | 0.025 [-0.001, 0.047] | -0.003 | 0.095 [0.045, 0.134] |  |

EXPLORATORY source-layer carrier on the frozen residual target y_t (SL resid - EN resid): dR2(SRC given S0) ridge = R 0.009 [-0.033, 0.054]; R1 -0.019 [-0.030, -0.002]; Rb 0.016 [-0.007, 0.034]; K 0.005 [-0.047, 0.051]; N 0.007 [-0.065, 0.083]; M -0.001 [-0.008, 0.004].

Quantile-GBT 90% PI coverage (secondary) and core-trial log-ratio excess log|SL|-log|EN| (z vs F):

| trait | QGBT cov E_TPE | QGBT cov E_R | core log-ratio | F mean | z | pct rank in F |
|---|---|---|---|---|---|---|
| R | 0.54 | 0.70 | 0.671 | -0.527 | 3.97 | 0.99 |
| R1 | 0.57 | 0.73 | -0.130 | -0.570 | 0.88 | 0.86 |
| Rb | 0.45 | 0.77 | 1.718 | -0.760 | 3.93 | 1.00 |
| K | 0.62 | 0.77 | -0.989 | -0.285 | -2.81 | 0.00 |
| N | 0.57 | 0.77 | 1.712 | -0.000 | 1.50 | 0.92 |
| M | 0.68 | 0.83 | -2.658 | -0.217 | -2.56 | 0.00 |

Judging: openai/gpt-4.1 labelled 1130/2140 generations; label counts {'refused': 310, 'complied': 805, 'partial': 12, 'irrelevant': 3, 'malformed': 0, 'empty': 0, 'unparsed': 0, 'PENDING_JUDGE': 1010}; second judge google/gemini-2.5-flash on 0: kappa 6-way NA, kappa refused-vs-not NA, raw agreement NA; kappa judge vs keyword rule (refused) 0.762.

Rule-labelled Stage-0c decisions re-checked with judge labels: reference source disagreements 24/340 (refusal refs), 56/340 (compliance refs), by kind/lang {'comp|jbb_ben|en': 17, 'ref|jbb_ben|sl': 12, 'comp|jbb_ben|sl': 12, 'ref|jbb_ben|en': 6, 'comp|jbb_harm|en': 15, 'comp|jbb_harm|sl': 12, 'ref|jbb_harm|en': 3, 'ref|jbb_harm|sl': 3}; r_prior judge counts {'en': 8, 'sl': 11} (pooled 19, defined under judge = True; rule counts {'en': 9, 'sl': 14}). EN-vs-SL judged refusal over 18 validity conditions: Spearman 0.896, mean refused EN 0.519 / SL 0.478.

Frozen predictions scorecard (results/frozen_predictions.json, evaluated mechanically):

| id | evaluation | holds |
|---|---|---|
| G1 Gap_R 90% CI in +/-0.10 | [0.008, 0.027] | True |
| G2 Gap_Rb 90% CI in +/-0.10 | [0.014, 0.060] | True |
| G3 some Gap_K/N/M >= 0.10 with B_t > 0 | K: Gap 0.147, B 0.050 [0.001, 0.121]; N: Gap -0.642, B -0.061 [-0.290, 0.449]; M: Gap 0.040, B -0.144 [-0.372, 0.555] | point True; with B CI True |
| G4 D adds dR2 >= 0.05 over S0 | R: -0.026 [-0.065, -0.002]; R1: -0.013 [-0.023, -0.003]; Rb: 0.011 [-0.012, 0.020]; K: -0.011 [-0.058, 0.027]; N: -0.016 [-0.063, 0.018]; M: 0.001 [-0.005, 0.008] | any False |
| G5 r_prior undefined | rule counts {'en': 9, 'sl': 14} (defined True); judge counts {'en': 8, 'sl': 11} (defined True) | rule False; judge False |
| G6 PI coverage >= 85% on E_TPE/E_R | share of trait x set meeting 85%: 0.50 | all False |

Cross-machine / rerun reproducibility (repro_check.py): E0_000 (stored on host1): bit-identical False, max |diff| 92.7; E0_049 (stored on host1): bit-identical False, max |diff| 97.2; E0_051 (stored on host2): bit-identical False, max |diff| 54.6

U6 FLORES NLL vs iteration-1 EXP3: n 166, mean |diff| 0.0094, max 0.0349 (tolerance 2e-3: pass False).

U7 diagnostic: same-length unpadded batch vs bs1 max |dlogp| 0.2709; padded mixed batch vs bs1 max 0.2802 (per-sequence mean NLL max diff 0.0486); repeated batched pass bit-identical True.

Verdict: {'REF': 'R', 'gates': {'floor_150': True, 'ref_valid': True}, 'claim1_refusal_visible_TOST': {'trait': 'R', 'gap_ci90': [0.007549556713095496, 0.027407286539540082], 'holds': True, 'status': 'confirmatory'}, 'damage_blind': {'K': {'conditions': {'gap_ge_0.10': True, 'holm_LB_gt_0': True, 'B_ci_excludes_0': True, 'gap_mm_ge_0.10': True, 'sign_stable_halves': True, 'sign_stable_simex': True}, 'blind': True, 'reliable': True, 'MDE': 0.13690101688464287, 'no_signal': False, 'label': 'BLIND', 'status': 'confirmatory'}, 'N': {'conditions': {'gap_ge_0.10': False, 'holm_LB_gt_0': False, 'B_ci_excludes_0': False, 'gap_mm_ge_0.10': False, 'sign_stable_halves': False, 'sign_stable_simex': False}, 'blind': False, 'reliable': False, 'MDE': 32.15743758464277, 'no_signal': True, 'label': 'no signal to predict', 'status': 'exploratory'}, 'M': {'conditions': {'gap_ge_0.10': False, 'holm_LB_gt_0': False, 'B_ci_excludes_0': False, 'gap_mm_ge_0.10': False, 'sign_stable_halves': False, 'sign_stable_simex': True}, 'blind': False, 'reliable': False, 'MDE': 21.853558521579203, 'no_signal': True, 'label': 'no signal to predict', 'status': 'exploratory'}}, 'damage_blind_any': True, 'carrier_hits': {'R:D': False, 'R:P': False, 'R:H': False, 'R:realized': False, 'R1:D': False, 'R1:P': False, 'R1:H': False, 'R1:realized': False, 'Rb:D': False, 'Rb:P': False, 'Rb:H': False, 'Rb:realized': False, 'K:D': False, 'K:P': False, 'K:H': False, 'K:realized': False, 'N:D': False, 'N:P': False, 'N:H': False, 'N:realized': False, 'M:D': False, 'M:P': False, 'M:H': False, 'M:realized': False}, 'carrier_any': False, 'forecast_coverage_ge_85': {'R': {'E_TPE': False, 'E_R': True}, 'R1': {'E_TPE': True, 'E_R': True}, 'Rb': {'E_TPE': False, 'E_R': False}, 'K': {'E_TPE': False, 'E_R': True}, 'N': {'E_TPE': False, 'E_R': True}, 'M': {'E_TPE': False, 'E_R': True}}, 'forecast_all_meet_85': False, 'carrier_status': 'confirmatory', 'frozen_predictions_scorecard': {'G1': {'gap_R_ci90': [0.007549556713095496, 0.027407286539540082], 'holds': True}, 'G2': {'gap_Rb_ci90': [0.014106098554974111, 0.060072335822604045], 'holds': True}, 'G3': {'per_trait': {'K': {'Gap': 0.14690901702481562, 'B_t': 0.049963850548316535, 'B_t_ci95': [0.000767020472260388, 0.12148347996415709], 'holds_point': True, 'holds_with_B_ci': True}, 'N': {'Gap': -0.6424079388230739, 'B_t': -0.06093681463725295, 'B_t_ci95': [-0.2903772288158322, 0.4487159124566439], 'holds_point': False, 'holds_with_B_ci': False}, 'M': {'Gap': 0.03999484603931411, 'B_t': -0.14374445121105908, 'B_t_ci95': [-0.37167665505249514, 0.5553973043642406], 'holds_point': False, 'holds_with_B_ci': False}}, 'holds_point': True, 'holds_with_B_ci': True}, 'G4': {'per_trait': {'R': {'dR2_D_given_S0': -0.026127176437721812, 'ci95': [-0.06509566633088551, -0.001871694456889553], 'holds': False}, 'R1': {'dR2_D_given_S0': -0.01327587304145586, 'ci95': [-0.023193559943054422, -0.002793496272549912], 'holds': False}, 'Rb': {'dR2_D_given_S0': 0.010758261798101396, 'ci95': [-0.012242038936888888, 0.020078794368764905], 'holds': False}, 'K': {'dR2_D_given_S0': -0.010745766510453447, 'ci95': [-0.057926141616678736, 0.02735676388188573], 'holds': False}, 'N': {'dR2_D_given_S0': -0.01572523564029893, 'ci95': [-0.06280721506134906, 0.017500911848317865], 'holds': False}, 'M': {'dR2_D_given_S0': 0.0013549147665763428, 'ci95': [-0.004908279652049524, 0.007514086414026203], 'holds': False}}, 'holds_any': False}, 'G5': {'rule_labels_defined': True, 'rule_counts': {'en': 9, 'sl': 14}, 'judge_defined': True, 'judge_counts': {'en': 8, 'sl': 11}, 'holds_rule': False, 'holds_judge': False}, 'G6': {'coverage_90PI': {'R': {'E_TPE': 0.7142857142857143, 'E_R': 0.9666666666666667}, 'R1': {'E_TPE': 0.9464285714285714, 'E_R': 0.9333333333333333}, 'Rb': {'E_TPE': 0.5892857142857143, 'E_R': 0.7666666666666667}, 'K': {'E_TPE': 0.8214285714285714, 'E_R': 0.9333333333333333}, 'N': {'E_TPE': 0.625, 'E_R': 0.9333333333333333}, 'M': {'E_TPE': 0.8392857142857143, 'E_R': 0.9333333333333333}}, 'holds_all': False, 'share_trait_sets_meeting_85': 0.5}}}

OpenRouter spend for this artifact: $1.06

## Figures (`figures/`, PNG + PDF, generated by `figures.py`)

- `figures/fig1_en_vs_sl_scatter.png`: per-edit EN_B vs SL_B trait means on F, with R2* in the titles
- `figures/fig2_gap_forest.png`: Gap forest: R2*, raw, SIMEX, margin-matched and edit halves, with the +/-0.10 band
- `figures/fig3_carrier_dr2.png`: carrier dR2 both ways (C given S0 and S0 given C)
- `figures/fig4_exposure_D.png`: the distribution of exposure D, and D vs the SL-minus-EN residual y for K/N/M
- `figures/fig5_forecast_coverage.png`: out-of-sample conformal PI coverage on E_TPE / E_R, with the core trial
- `figures/fig6_validity.png`: validity: condition-level R_seq and R1 vs the judged refusal rate, per language
- `figures/fig7_reselection_pareto.png`: bilingual reselection: EN keyword refusals vs SL_est, coloured by KL
- `figures/fig8_transfer_exploratory.png`: EXPLORATORY: SL/EN KL ratio vs refusal-direction source layer; EN vs SL KL; transfer ratios

## Deviations from the plan (`results/deviations.json`)

- **D1**: GPU = RTX 4090 24 GB for Stages 0-B and the whole panel (plan: A4500 20 GB); the post-panel steps (local judge, post_tests, repro_check, final analysis) ran on host 3 = RTX 2000 Ada 16 GB after a second server restart (see D20) (impact: panel: faster, nothing else changes; host 3 only re-scores 3 edits for the reproducibility check)
- **D2**: OpenRouter key HTTP 403 (shared $50 daily limit) at the Stage -1 probe (21:05 UTC) (fallback: F1: references chosen with the EXP3 rule labeller (references.json meta label_source=rule_labelled); gpt-4.1 judging deferred to after the 00:00 UTC reset; X_SET translated with NLLB-200-distilled-1.3B (F11) instead of gemini-2.5-flash; impact: reference choice may differ from judge-based choice; the disagreement count is reported after judging)
- **D3**: r_prior status decided with rule labels (pooled 23 benign half-A refusals: EN 9, SL 14 >= 10) -> r_prior DEFINED and P computed; G5 predicted undefined (impact: keyword rule over-counts refusals ('illegal', 'harmful' in compliant text); judge-based recount reported in r_prior_status after judging; P treated as exploratory)
- **D4**: U7 batching certification FAILED: left-padded batched greedy generation token-identical on only 5/8 (EN) and 7/8 (SL) prompts; teacher-forced right-padded batched vs batch-size-1 max |dlogp| 0.18 / 0.12 nats (> 0.02) (fallback: generation switched automatically to equal-length buckets (no padding) for ALL generations; teacher-forced batching kept (deterministic batch composition, identical across edits) and diagnosed in post_tests.json (U7_diagnostic: unpadded same-length batches vs bs1); impact: item-level numerical noise of ~0.01 nats enters every trait; it is absorbed by the split-half ceilings)
- **D5**: U6 FLORES NLL cross-check vs EXP3 C0: mean |diff| 0.009, max 0.035 nats (tolerance 2e-3 FAILED) (impact: EXP3 used its own eager-attention 4-bit load and different batch shapes; same magnitude as D4 numerics; N (FLORES rise) edit effects are of the same order, see F8 no-signal rule)
- **D6**: U4 and U5 were run after the panel (post_tests.py, second model instance) instead of in stage0b (impact: none on the panel (they validate formulas/approximations, not inputs))
- **D7**: Winsorization implemented per vector (|x| 0.995-quantile clip over dims, Heretic/EXP3 semantics) rather than 'per-dim pooled quantiles' (impact: tames dim 2339 as intended; w_H cos with EXP3 frozen d_EN = 0.99997)
- **D8**: Bootstrap draws use one CV repeat per draw (seed varies) and GroupKFold by original edit index (duplicated edits never straddle folds); point estimates use 5 repeats (impact: repeat noise enters the bootstrap spread (conservative); the grouped CV fixes a leak found by synth_test scenario (b) where plain KFold on resampled edits shrank the bootstrap Gap)
- **D10**: Validity generations are 64 tokens, bucketed decoding (~110 s per validity edit) (impact: none on design)
- **D11**: P covariate layer = hidden index 34 (the frozen H probe layer) (impact: r_prior is computed at every layer but P only at 34)
- **D12**: 30-local-draw augmentation for the core forecast not run (as allowed by the plan) (impact: core excess uses the global forecast / GP if out of support)
- **D13**: F8 no-signal rule operationalised with the edit x item interaction SE (item means removed) as the per-edit item SE; the first implementation used the raw between-item SD (why: a debug run on 43 edits (outputs not used for decisions) showed the raw version flags R as 'no signal' although its split-half reliability is 1.0 - fixed item offsets cancel in between-edit comparisons, so raw between-item SD is not measurement noise; impact: both versions are reported (no_signal and no_signal_raw_version); the verdict uses the interaction version)
- **D14**: Carrier bootstrap CIs resample edits over FIXED out-of-fold predictions (5 repeats averaged) instead of refitting CV inside each draw; 1000 draws (why: refitting at n~43 gave unstable intervals of +/-10 in R2 units in the debug run; impact: CIs reflect edit sampling of prediction errors, not refit variance)
- **D15**: SUPERSEDED: the rehearsal analysis used B = 500 (fallback) on a shared CPU; the FINAL analysis ran with the frozen B = 1000 on a 48-core host (bootstrap of 500 took ~64 s, far below the 30-min fallback trigger) (impact: none: the final CIs use the frozen B = 1000)
- **D9**: Mixed model d_ie ~ EN_trait x margin + lang + lang:EN_trait + (1|item) + (1|edit) IS run (analysis.mixed_model, statsmodels MixedLM with crossed variance components) on the R and M traits, half-B items, F edits (impact: p-values treat item x edit x language rows as the unit and are descriptive; the joint bootstrap is the inferential tool)
- **D16**: Session interrupted at 22:38 UTC after 51/246 panel edits (E0_000..E0_050, host 1: Ryzen 9 7950X + RTX 4090); the panel resumed at 22:52 UTC on a different container (host 2: EPYC 7352 + RTX 4090, same driver family) from E0_051, via the append-only resume path (edits already in panel_edits.jsonl are skipped; no edit was scored twice). The panel's time guard was extended with P1_TOTAL_BUDGET_S=27600 s from the original start (20:59 UTC) because the restarted session has its own budget (check: repro_check.py re-scores two host-1 edits (E0_000, E0_049) and one host-2 edit (E0_051) after the panel and compares every per-item value to the stored parquet (results/repro_check.json); impact: if host-1 vs host-2 values differ, the difference is GPU-kernel numerics (same GPU model); its magnitude is reported next to the item-level noise; outcome: repro_check.py ran on host 3 (RTX 2000 Ada) after a further restart, so it measures cross-GPU-model numerics: All teacher-forced traits re-score within bf16/NF4 numerics on a different GPU (RTX 2000 Ada vs RTX 4090): R_seq max |diff| <= 0.041, K-KL <= 0.0021, FLORES NLL <= 0.12, MC margin <= 0.14, R1 <= 0.25 (first-token log-odds). Hproj/Pproj are raw residual projections at hidden layer 34 (magnitude ~2000-3000); their mean |diff| is <1% of the stored per-item SD, so the H/P covariates are unaffected at the scale they vary across edits. No row is bit-identical across GPUs. Exception: the per-item truncated KL of these three WEAK edits (stored mean KL E0_000 0.0014, E0_049 0.0012, E0_051 0.0022 nats) moves by a mean |diff| of 0.00032, 0.00030, 0.00037 (17-26% of the mean KL; 0.29-0.56 of the per-item SD) across GPUs, because the original-model reference continuation distribution was cached on host 1: K = log mean KL therefore can shift by up to ~0.2-0.3 log-units for the weakest edits across GPUs (less if item-level differences cancel; signed diffs were not saved). All panel edits were scored on RTX 4090s (hosts 1 and 2); host 3 only re-scored. host_check.py then tested host 1 vs host 2 directly on the panel: max |host-2 offset| = 0.071 log units vs residual SD ~0.45: no detectable host offset in K between the two RTX 4090 hosts)
- **D17**: judge.py originally posted to a hard-coded openrouter.ai URL; fixed to os.environ['OPENROUTER_BASE_URL'] before any judging call. Stage -1 probe of the previous session was a direct curl to openrouter.ai (403, $0) (impact: none on results (no call succeeded before the fix))
- **D18**: Static baseline b2 = kernel-weighted |cos(v_l, lang_l)| uses Heretic's interpolated refusal direction BEFORE the per-layer harmless-mean orthogonalization (plan: after it); b1 uses the per-layer EN/SL diff-in-means cosine as planned (impact: b2 is one of 13 S0 features; the orthogonalization removes a component along the harmless mean, which is not the language direction, so the ranking of edits on b2 is expected to change little)
- **D19**: Added after the freeze (exploratory, labelled so everywhere): EN->SL transfer slopes/attenuation ratio (analysis.transfer_slopes), quantile-GBT PI coverage, core log-ratio excess, judge re-checks of the rule-labelled references and r_prior, predictions scorecard, cross-pod edit identity check (unit_tests.json U1b_sibling_diff) (impact: none on the frozen decision rules; they add interpretation (Gap ~ 0 means 'predictable', not 'equal size'))
- **D20**: Second server restart (~02:57 UTC) moved the module to host 3 (RTX 2000 Ada 16 GB, empty model cache, .venv removed). The .venv was rebuilt from pyproject.toml (identical pins) and the models re-downloaded at the pinned revisions (GaMS3 main == 1d0b27af verified via the Hub API). The planned local gemma-3-12b-it fill-in judge had been interrupted at 409/2140 by the restart and saved nothing. (fallback: The OpenRouter run budget was still exhausted (403 aii_run_budget_exhausted, $7.05 of $7.00 for the whole 'Test idea' phase, shared by all pods) and the org's free-model daily quota (1000/day) was also used up, so the second judge and the fill-in for the 1010 unlabelled generations use a LOCAL Qwen/Qwen3-14B@40c06982 (bnb_4bit, same rubric and user message, thinking disabled, label = argmax of the six label first-token log-probs). Qwen3 is a different family from GaMS3/Gemma-3 and from gpt-4.1.; check: Agreement with gpt-4.1 on all 1130 generations both judged: kappa refused-vs-not 0.875 (EN 0.919, SL 0.831), 6-way kappa 0.702, raw refused agreement 0.951 (results/judge_meta.json local_judge). The validity gate is reported for merged labels (primary), gpt-4.1-only, local-only and rule labels.; impact: 9 of the 18 validity conditions (E1_010..E1_090) are labelled only by the local judge; ~20 of 80 generations in each of the other 9 conditions are local-labelled. The planned cross-family API second judge (gemini-2.5-flash) and its 200-row stratified kappa were NOT run; the local-judge kappa over 1130 rows stands in for it.; post_tests: post_tests.py ran on host 3: U4 formula-vs-PEFT max rel diff 1.9e-7 (PASS); U5 truncated/full KL ratio 1.026 (PASS, >= 0.95; the truncated reference was cached on host 1 and the full one recomputed on host 3, so cross-GPU noise enters the ratio); U7 diagnostic: unpadded same-length batches differ from batch size 1 by the same magnitude as padded batches (max 0.27 vs 0.28 nats; per-sequence mean NLL <= 0.049), and a repeated batched pass is bit-identical -> batch-shape numerics, not an attention-mask error)

## Layout

| path | what |
|---|---|
| `method.py` | GPU orchestrator. Stages: stage0b (model, edit sets, U1-U3/U7), stage0c (generations, references, r_prior), stage0d (geometry, caches, baselines), freeze, stageA (timing + ladder), panel (resumable) |
| `engine.py` | Heretic `Model` wrapper: edits via `reset_model` + `abliterate`, LoRA factors, teacher-forced scoring at the scored positions only, hooks, generation |
| `common.py` | paths, pins, logging, hashing, Heretic parameter sampler, OpenRouter cost ledger |
| `data_prep.py` | S3 DEV extraction with split-hash verification; disjoint exposure set X_SET (NLLB EN->SL, LaBSE/GlotLID QC) |
| `protocol.py` | frozen protocol + predictions, written with sha256 before any panel trait existed |
| `judge.py` | blind gpt-4.1 judge (6-label rubric), gemini-2.5-flash second judge, rule labeller, `--from-log` recovery |
| `analysis.py` | Stage D: Gap, bootstrap, B_t, SIMEX, stability, margin-matched Gap, mixed model, carrier, forecast, reselection, validity, verdict, scorecard, transfer slopes |
| `synth_test.py` | T0: four simulated scenarios run through the real analysis code (`results/synth_test.json`) |
| `audit.py` | T5: independent plain-numpy recomputation + placebos (`results/audit.json`) |
| `rederive_headlines.py` | second independent re-derivation of the headline numbers from raw files, with placebos (`results/rederive_headlines.json`) |
| `reproducibility.md` | exact commands, pins, hardware and expected numbers |
| `post_tests.py` | U4 / U5 / U7-diagnostic on a second model instance after the panel (`results/post_tests.json`) |
| `repro_check.py` | re-scores host-1 and host-2 edits to quantify cross-machine numerics (`results/repro_check.json`; ran on host 3, see D16/D20) |
| `host_check.py` | CPU check that host 1 vs host 2 (both RTX 4090) shifted no K values (`results/repro_check.json` host1_vs_host2_K_offset_check) |
| `figures.py`, `summary_tables.py`, `to_schema.py`, `make_readme.py` | outputs: figures, tables, `method_out.json` (exp_gen_sol_out), this README |
| `local_judge.py` | local Qwen3-14B judge (same rubric): second judge vs gpt-4.1 and fill-in for unlabelled generations (D20) |
| `run_judge_after_reset.sh`, `finish_after_panel.sh` | helper drivers: wait for the shared key's daily reset, then judge; post-panel sequence |
| `data/s3_items.json`, `data/x_set.json` | frozen DEV items (pod ids / halves) and the 64-prompt disjoint exposure set (+ sha256) |
| `results/edits_manifest.json` | all 246 edits: set, seed, trial number, raw + transformed parameters, journal objectives |
| `results/panel_edits.jsonl`, `results/panel_items/*.parquet` | per-edit covariates/aggregates and per-item trait values (the panel itself) |
| `results/baseline_items.parquet` | original-model per-item values |
| `results/references.json`, `results/compliance_refs_gams_core.json` | 24-token refusal/compliance references; the shared export for the Gemma P1 pod |
| `results/validity_gens.jsonl`, `results/judged_generations.json`, `results/judge_meta.json` | validity generations and their blind labels |
| `results/frozen_protocol.json`, `results/frozen_predictions.json`, `results/ladder_decision.json` (+ `.sha256`) | pre-registration files |
| `results/analysis_results.json`, `results/verdict.json`, `results/variances_for_power.json` | analysis outputs |
| `results/unit_tests.json`, `results/u6_flores_check.json`, `results/timings.json`, `results/api_costs.jsonl` | checks, timing, spend |
| `results/*_quick.json`, `results/*_rehearsal131.json`, `results/synth_test_v*.json` | DEBUG runs on partial panels / earlier code versions; kept for transparency, never used for decisions |
| `results/post_tests.json`, `results/repro_check.json`, `results/judge_local_cache.json` | U4/U5/U7 post-tests, cross-GPU re-scoring + host-offset check, local-judge label probabilities |
| `cache/` | original-model caches: geometry.npz, k_cache.pt (kept), r_prior.npy, x_acts_*.pt (deleted after the round; regenerable) |
| `third_party/heretic/` | pinned Heretic 3521f864 source |
| `method_out.json` (+ mini/preview) | exp_gen_sol_out: one example per edit, metadata = all results |
| `logs/` | run logs (the judge's raw outputs are logged at DEBUG) |

## How to run

```bash
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python torch==2.11.0+cu128 torchvision==0.26.0+cu128 --index-url https://download.pytorch.org/whl/cu128
uv pip install --python .venv/bin/python -r pyproject.toml
uv pip install --python .venv/bin/python -e third_party/heretic --no-deps
.venv/bin/python data_prep.py                                   # S3 items + X_SET
.venv/bin/python method.py --stages stage0b,stage0c,stage0d,freeze,stageA,panel   # GPU, ~3.5 h on an RTX 4090 (resumable)
.venv/bin/python judge.py                                       # blind judging (needs OPENROUTER_API_KEY / OPENROUTER_BASE_URL)
.venv/bin/python local_judge.py                                 # local Qwen3-14B second judge + fill-in (D20)
.venv/bin/python post_tests.py && .venv/bin/python repro_check.py && .venv/bin/python host_check.py
.venv/bin/python synth_test.py --B 100                          # T0
AN_JOBS=24 .venv/bin/python analysis.py --B 1000                # Stage D (CPU; ~87 min on a 5-CPU quota)
.venv/bin/python audit.py && .venv/bin/python figures.py && .venv/bin/python summary_tables.py
.venv/bin/python to_schema.py && .venv/bin/python make_readme.py
```

Read-only inputs come from iteration 1: the Optuna journal, the directions and the trial-88 adapter in `gen_art_experiment_1`;
the prefix sets and frozen directions in `gen_art_experiment_3`; and the frozen dataset `gen_art_dataset_1`. The model is
`cjvt/GaMS3-12B-Instruct@1d0b27af5748784482600d24779409e7e1dc9adc` from the shared HF cache.

## Kept artifacts (workspace paths)

- panel: `./results/panel_items/` and `./results/panel_edits.jsonl`
- references and the Gemma-pod export: `./results/references.json`, `./results/compliance_refs_gams_core.json`
- judged generations: `./results/judged_generations.json`
- K reference cache: `./cache/k_cache.pt`; geometry: `./cache/geometry.npz`; r_prior: `./cache/r_prior.npy`

## Restoring removed files

- `.venv/`: run the four `uv` lines at the top of "How to run".
- `__pycache__/` and `third_party/heretic/src/heretic/__pycache__/`: created automatically on import (`.venv/bin/python -c "import method, heretic"`).
- `cache/x_acts_en.pt`, `cache/x_acts_sl.pt` (the 685 MB X_SET exposure caches of `o_proj`/`down_proj` inputs): run
  `rm results/baseline_done.json && .venv/bin/python method.py --stages stage0d`. This recomputes them, together with the
  geometry, the K cache and the baseline traits, from the pinned model and `data/x_set.json`.
