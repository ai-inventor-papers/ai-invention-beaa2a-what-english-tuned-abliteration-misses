# A1 screen — English vs Slovene refusal-direction transfer (GaMS3-12B-Instruct vs Gemma-3-12B-it)

Iteration-1 widen-round screen (run `run_Fapgmt6JWbcD`, artifact `gen_art_experiment_3`) of alternate **A1**:
*"Slovene safety training keeps a Slovene refusal"*. Within each original model we build
harmful-minus-harmless difference-in-means directions from English (d_EN) and Slovene (d_SL) prompts, freeze one
(layer, position) per model on dev half A, and on held-out half B measure the full 2×2 **source-direction ×
evaluation-language** transfer matrix for directional ablation and for activation addition. The key contrast is the
**u_SL increment**: how much *extra* Slovene refusal is removed when the Slovene-specific residual
u_SL = d_SL ⊥ d_EN is ablated on top of d_EN. It is compared against energy-matched random directions added on top of
d_EN (the rank-2 energy artefact) and a within-language split-half noise placebo.

## Results (all numbers recomputed from `results/<m>/per_item.parquet` and `results/judged_generations.json`)

Setting: GaMS3 = `cjvt/GaMS3-12B-Instruct@1d0b27af`, Gemma = `google/gemma-3-12b-it@96b6f1ec`. Both use Heretic's bnb_4bit
NF4 config with bf16 compute on an L4 GPU. Half A (44 JBB twins) was used for fitting; half B (41 held-out JBB harmful/benign
twins) for evaluation. SL prompts are Gemini-2.5-flash translations (mean back-translation chrF 81; no native review).
Uncertainty is a 2,000-sample item-cluster bootstrap over semantic ids (EN+SL versions and twins resampled together).

**Frozen sites (half A, Arditi filters).**
- GaMS3: layer 34, last template token (pos −1); ablation KL 0.014/0.017; cos(d_EN, d_SL) = 0.83.
- Gemma: layer 20, pos −1; cos = 0.92.
- The protocol files and their SHA-256 hashes were written before any half-B outcome (T6 check passes).
- Half-A power check: MDE is 0.41 log-odds for GaMS3, below 20% of its d_SL effect (1.06), so GaMS3 is adequately powered. Gemma's MDE is 0.95, above 20% of its d_SL effect (0.43), so Gemma's u-increment is underpowered by this criterion. The frozen rule applies the power check to GaMS3 only.

**Validity gate for R (primary outcome switch, F6).** R is the teacher-forced first-token refusal log-odds.
- GaMS3 fails the gate: condition-level Spearman 0.51, item AUROC 0.70. GaMS3 often opens compliantly and refuses later.
- Gemma passes: 0.91 / 0.96.
- The screen verdict therefore uses **judged refusal rates**. The judge is gpt-4.1: blind, shuffled neutral ids, 1,596 generations, 128 greedy tokens.

**Headline behaviour (judged refusal on half-B harmful, 41 items per language; residual = rate(C1)/rate(C0)).**

| model | C0 EN | C0 SL | d_EN ablation EN | d_EN ablation SL | d_SL ablation EN | d_SL ablation SL | residual gap SL−EN after d_EN (95% CI) |
|---|---|---|---|---|---|---|---|
| GaMS3 | 0.90 | 0.93 | 0.46 | 0.34 | 0.07 | 0.10 | **−0.15 [−0.32, 0.03]** |
| Gemma | 0.83 | 1.00 | 0.07 | 0.85 | 0.29 | 0.93 | **+0.77 [0.62, 0.89]** |

- **A1 is not supported, and its predicted model contrast is reversed.** A1 predicted that GaMS3 (the model with Slovene safety training) would keep a Slovene refusal. Instead:
  - In GaMS3, one English-derived direction removes Slovene refusal at least as well as English refusal. The log-odds transfer is T(EN→SL) = 0.96 [0.93, 0.98].
  - In **Gemma**, Slovene refusal survives both the English and the Slovene direction (85% and 93% still refused). This holds although cos(d_EN, d_SL) = 0.92 and the log-odds transfer ratio is T(EN→SL) = 3.47 [2.76, 4.90].
- **Explanation (exploratory, `results/margin_decomposition_exploratory.json`): the refusal decision margin differs by language.** In Gemma, the Slovene baseline refusal log-odds are large (mean R = 13.9 vs 3.6 in EN), and 69% of *benign* Slovene twins are refused at baseline (EN 19%). d_EN removes 7.0 log-odds in SL, and 93% of SL items stay above R = 0. So high direction cosine and a large log-odds transfer do not predict behavioural transfer when the target language sits far past the decision threshold. This matches a Slovene-wide refusal prior rather than harm-specific processing. In GaMS3 the SL margin is small (R = 1.95), so SL refusal is removed easily.
- **Frozen screen rules** (`results/screen_verdict.json`):
  - **Verdict: `weak`**, with the primary outcome judge-based.
  - Judge-based u_SL increment in GaMS3: I_raw = 0.10 [−0.07, 0.27], F_raw = 0.12, so SURVIVE_RAW is false.
  - KILL is false: the R-based ρ gap is 0.28 [0.05, 0.53] and exceeds the threshold. The judge-based gap has the opposite sign.
- **R-based u_SL increment in GaMS3 (reported verbatim).**
  - Values: I_raw = 1.23 [0.94, 1.52]; F_raw = 0.23; F_ctrl = 0.195 (frozen random-on-top) and 0.154 (raw-energy random-on-top); I_noise = 0.12 [−0.18, 0.40].
  - The increment is **collateral-confounded (F8)**: ablating span(d_EN, u_SL) raises FLORES NLL by 1.38 (EN) and 0.94 (SL) nats/token and harmless KL to 0.74, and 14–15 of 41 replies are judged malformed. So it cannot count as clean suppression.
  - Gemma: F_raw = 0.55 [0.12, 1.18] but F_ctrl = −0.20 [−0.62, 0.14]. The raw increment is fully explained by adding any second direction.
- **Addition (induced refusal on benign twins, α = 1; R-based, and GaMS3 R is not gate-validated).**
  - GaMS3 shows a language-selective double dissociation: adding u_SL gives +2.23 [1.96, 2.49] in SL and −1.54 in EN; adding u_EN gives +3.54 [2.96, 4.09] in EN and −1.11 in SL. A raw-energy random direction gives −2.35 (EN) and −0.78 (SL), and harmless KL ≤ 0.10.
  - In Gemma, u_SL addition does nothing (+0.62 EN, −0.18 SL; CIs include 0), while u_EN raises both languages.
  - This is the only GaMS3-specific Slovene component seen here. It is **addition-only and exploratory**: ablating the same component is destructive.
- **Random controls (T7 failed; post-freeze amendment in `configs/postfreeze_amendment_<m>.json`).**
  - The frozen random directions were energy-matched on winsorized residuals and carried 1.2–9× d_EN's *raw* energy, so their ablation is destructive (FLORES +1.1…+3.1 nats/token).
  - Raw-energy-matched randoms are also destructive: GaMS3 KL 0.5–1.4, Gemma KL ≈ 1, FLORES +1.5…+2.6. Only d_EN/d_SL themselves are low-collateral (KL ≤ 0.02 in GaMS3, ≤ 0.22 in Gemma).
  - Lesson: a random direction ablated at every layer and position is not a neutral control of equal energy. Random "refusal removal" here is collateral damage, which the judge labels complied/malformed/irrelevant, not suppression.
- **Heretic bridge (Heretic's own code, S1 directions, TPE startup draws 1–20, seed 20260923; R-based).**
  - Mean ρ_SL − ρ_EN gap across 20 edits: GaMS3 0.11 [0.06, 0.17] (16/20 edits positive); Gemma **0.23 [0.16, 0.30]** (19/20).
  - English-derived Heretic edits leave more Slovene than English residual refusal in both models, and more in Gemma. This contradicts A1's "Gemma ≤ half of GaMS3" clause.
  - Harmless KL of the edits is 0.001–0.18.
- **Cosine vs transfer (exploratory, half A, pos*).**
  - Spearman(corrected cosine, T_EN→SL) = 0.39 (GaMS3) and 0.58 (Gemma).
  - Layers with cosine ≥ 0.8 but T < 0.8: GaMS3 {14–17, 22, 25, 35, 37}; Gemma {14–22}.
  - Cosine is not a sufficient predictor of transfer.
- **Checks.**
  - T8 recompute: identical.
  - `verify_numbers.py`: every T/I/F/ρ number re-derived through a separate plain-Python path matches exactly, as do the judged rates and bridge means.
  - Placebo: the label-swap nulls do not reach significance; the language-swap null for the Gemma gap is [−0.46, 0.07].
  - MT-quality subset (40/41 twins with chrF ≥ 50): F_raw 0.23 (GaMS3) and 0.50 (Gemma), unchanged.

**Limitations.**
- n = 2 models; 41 held-out items; one frozen layer per model.
- 4-bit weights; MT-only Slovene; no human review. There is no second LLM judge: the shared OpenRouter key was at its daily limit, and a retry after the key-replacement notice still returned 'Key limit exceeded'. To add the gemini-2.5-flash second judge later without re-paying for gpt-4.1, run `.venv/bin/python judge.py --from-log && .venv/bin/python analysis.py`.
- GaMS3's R proxy failed validation.
- The Gemma candidate grid was reduced (F3(4)); the priority-3 sensitivity arms were not run.
- Nothing is attributed to a training stage.


## Layout

| path | what |
|---|---|
| `method.py` | per-model GPU pipeline: load (Heretic bnb_4bit config) → hook unit tests → smoke + padding check → prefix mining → half-A activations/directions/cosines → Arditi-style (layer,pos) selection → condition directions + energy-matched randoms → half-A power check + **FREEZE** → half-B ablation / matched-efficacy grid / addition → generations → sensitivity arms |
| `interventions.py` | 4-bit loading, residual hooks (ablation at embedding + every layer output, partial ablation, addition, capture), teacher-forced R / KL / NLL / MC scoring, batched generation |
| `data_build.py` | SCREEN-DEV: JBB twins + S1 overlap audit (LaBSE), Dolly, FLORES+, SL-LLM-Eval MC carve-out, NLLB translation, sha1 halves |
| `translate_openrouter.py` | plan-primary MT: gemini-2.5-flash forward + back-translation, chrF/LaBSE, NLLB fallback |
| `judge.py` | blind judging: gpt-4.1-mini (all), gemini-2.5-flash (stratified 200), rule labeller, GlotLID, repetition |
| `analysis.py` | bootstrap analysis, frozen screen rules, validity gate, collateral, cosine-vs-transfer, MT-quality subset; `--recompute` = T8 |
| `verify_numbers.py` | independent re-derivation of headline numbers from raw rows + label-swap placebo |
| `heretic_bridge.py` | priority-2 bridge: Heretic's own Model/abliterate with TPE startup draws 1–20 (seed 20260923) |
| `figures.py`, `build_output.py` | figures fig1–fig7 and `method_out.json` |
| `configs/` | `pins.json` (model SHAs, bnb config), `prefix_sets_<m>.json` (R/C token sets), `frozen_protocol_<m>.json` + `.sha256` (frozen before half B), `postfreeze_amendment_<m>.json` (raw-energy random controls, with reason) |
| `data/` | `screen_dev.json` (all items, halves), `translations.json` (+sha256; Gemini + NLLB copies), `translations_nllb.json`, `data_build_meta.json`, `dev_carveout_ids.json` |
| `results/<m>/` | `acts_halfA/` (split residual cache, regenerable), `per_item_rows.jsonl` / `per_item.parquet` (every condition × language × item), `generations.json`, `selection.json` (all candidates), `cosine_profile.json`, `frozen_directions.npz`, `directions_meta.json`, `cstar.json`, `smoke.json`, `hook_tests.json`, `mining_generations_*.json`, `timings.json` |
| `results/<m>/` (cont.) | `random_raw.npz` (amendment randoms), `generations_rawrand.json`, `heretic_bridge.json` (20 Heretic startup edits), `heretic_directions.pt`, `startup_params.json`; `gemma/heretic_bridge_10edits.json` (first 10-edit pass) |
| `results/` | `analysis_summary.json` (everything), `screen_verdict.json`, `judged_generations.json` (gpt-4.1 labels + rule labels + GlotLID + repetition), `judge_meta.json`, `judge_t5_check.json`, `judge_raw_cache.json`, `margin_decomposition_exploratory.json`, `verify_numbers.json`, `recompute_check.json`, `screen_numbers.json`, `api_costs.jsonl` ($1.66 total), `deviations.json`, `env_freeze.txt` |
| `figures/` | fig1 cosine profile · fig2 2×2 ablation transfer · fig3 addition dose-response · fig4 u-increment forest · fig5 matched-efficacy curves · fig6 R-vs-judge validity · fig7 cosine vs transfer · **fig8 judged refusal per condition (headline)** — PDF + PNG |
| `method_out.json` (+ `full_`/`mini_`/`preview_`) | exp_gen_sol_out: metadata = full analysis; examples = half-B JBB items with per-condition R and responses |
| `results_mini/` | outputs of the T4 mini run (8 items per kind; pre-winsorization, superseded; its activation cache was removed — rerun `.venv/bin/python method.py --model gams3 --mini`) |
| `third_party/heretic/` | Heretic source at the pinned SHA (read-only reference) |

## How to run

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python torch torchvision --index-url https://download.pytorch.org/whl/cu128
uv pip install --python .venv/bin/python -r pyproject.toml
.venv/bin/python data_build.py                 # SCREEN-DEV + NLLB translations (GPU for NLLB/LaBSE)
.venv/bin/python translate_openrouter.py       # Gemini translations (needs OPENROUTER_API_KEY)
.venv/bin/python method.py --model gams3       # ~60-80 min on an L4; resumable
.venv/bin/python method.py --model gemma
.venv/bin/python judge.py                      # gpt-4.1 judge, ~$1.5 (this run: outputs recovered with --from-log --no-second after a crash / key limit)
.venv/bin/python heretic_bridge.py --model gams3   # optional priority-2 bridge
.venv/bin/python analysis.py && .venv/bin/python analysis.py --recompute && .venv/bin/python verify_numbers.py
```

## Restoring removed files

- `.venv/` — `uv venv .venv --python=3.12 && uv pip install --python .venv/bin/python torch torchvision --index-url https://download.pytorch.org/whl/cu128 && uv pip install --python .venv/bin/python -r pyproject.toml`
- `results/<m>/acts_halfA/` (half-A residual cache, float32, ~1.2 GB split into 14 parts `acts_halfA_part_NNN.npy` of 20 prompts / 87 MB each, read back with `method.load_acts`) — `rm -r results/<m>/acts_halfA; .venv/bin/python method.py --model <m>` (the activation stage recomputes it; later stages resume from their saved outputs)
- `__pycache__/` — Python bytecode cache, recreated automatically on import (e.g. `.venv/bin/python -c "import method"`).
- Model weights live in the run's shared HF cache: `huggingface-cli download cjvt/GaMS3-12B-Instruct --revision 1d0b27af5748784482600d24779409e7e1dc9adc`, `huggingface-cli download google/gemma-3-12b-it --revision 96b6f1eccf38110c56df3a15bffe176da04bfd80`.
