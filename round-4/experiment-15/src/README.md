# Can an optimiser see its own refusals? — the gradient-blind fraction on a second Heretic search

**Result in brief.** The pre-registered prediction is **falsified**: measured pairwise on the 60 parameter draws
that both searches share, Heretic's keyword objective is **not** measurably blinder on gemma-3-12b-it than on
GaMS3-12B-Instruct. The classifier reference gives Δ = +0.006 [0, 0.019]. The judge reference gives the opposite
sign, Δ = −0.029 [−0.060, −0.005]. Both objectives rank candidates correctly at a coarse scale. What they share is a
**structural** blindness at the point of selection. In both searches the objective's floor (72/100 and 16/100) sits
above the frozen selection rule's 10/100 threshold. As a result, **every** candidate the reference places at ≤ 10/100
is invisible to the rule's primary branch (TBF = 1.00 in both searches, under both references), and the rule falls
back to "fewest keyword refusals". That fallback picks an **under**-edited candidate on Gemma (judged 63/100
refusals on the re-measured scores; 37/100 at iteration 1's actual pick, trial 96) and a fully suppressed but **~3× higher-KL** candidate on GaMS3 (KL 0.175 vs 0.060 for the judge's pick).
Nothing here is a better edit (P7 stands).

### Instruments first (all gates were computed and written before any GaMS3 blind-fraction number)

| check | result |
| --- | --- |
| G1: identical startup draws | **60/60** parameter vectors identical (rtol 1e-9); the raw-jsonl and optuna parses of both journals agree exactly |
| T0: instrument identity | classifier file sha256 `678cf09b…` and bundle sha `93a3f6d8…` verified; it reproduces the in-loop objective's stored probabilities **exactly** (max diff 0.0, 200 rows); Heretic `_is_match` matches the stored verdicts exactly; truncation matches exactly |
| T2: Gemma dress rehearsal | reproduces art_0XmNBGkzsJc_ exactly: keyword floor 72, judged range 7–98, κ(keyword) 0.196, κ(classifier) 0.924, MAE 30.55 vs 2.15 |
| G2: replay fidelity | **116/116 GaMS3 trials bit-exact** to the iteration-1 journal (keyword counts and KL identical; same GPU type, L4), 38 s/trial |
| judge gate (bought) | κ(Qwen3-14B workhorse, gpt-4.1) = **0.850** [0.772, 0.911] refused-vs-not within edited cells, n = 800 stratified rows, **$0.86**; Se 0.956, Sp 0.896 → **PASS** (the gate both iteration-3 artifacts missed) |
| G3: classifier on GaMS3 | κ = **0.841** [0.745, 0.910] vs workhorse (0.834 vs gpt-4.1) on the 20 held-out certification trials → **PASS without refitting** (Gemma, A11: 0.858). The keyword rule on the same rows scores 0.591 [0.431, 0.700] (Gemma: 0.143) |
| caveat found | the classifier **undercounts** GaMS3 refusals in mid-range cells (mean C − J = −6.8/100 on the 20 certification trials; trial 14: J 46, C 15). Over all 70 judged GaMS3 trials κ = 0.801 [0.752, 0.841] and count MAE 8.7/100, which is **worse** than the keyword rule's 6.7. On GaMS3 the judge is therefore the stronger reference (fig. 6) |
| unedited models | the keyword rule is near-exact on both originals (Gemma 100 vs judged 97, acc 0.97; GaMS3 98 vs 98, κ 1.0) |

### The statistic (fig. 1, fig. 2, fig. 6; `results/analysis.json`)

| | Gemma | GaMS3 | difference (gemma − gams) |
| --- | --- | --- | --- |
| **GBF, paired 60 startup draws, reference C (PRIMARY)** | 0.006 [0, 0.018] (4/652 pairs) | 0.000 (0/1,125) | **+0.006 [0, 0.019] → PRED-1 FALSIFIED** |
| same, drift-inflated σ (upper bound) / common tolerance | | | +0.011 [0, 0.026] |
| same, exploratory per-pair tolerance √(σᵢ²+σⱼ²) | 0.012 | 0.000 | +0.012 [0, 0.028] |
| P-d cross-search label swap (null) | | | null 95% [−0.024, +0.025], p = 0.38 |
| **GBF, paired 60, reference = judge J** (freeze-listed confirmation) | 0.005 (3/643) | 0.033 (39/1,174) | **−0.029 [−0.060, −0.005]** (opposite sign) |
| GBF, all 116, reference C (unpaired sensitivity; range restriction NOT controlled) | 0.051 [0.029, 0.074] | 0.002 [0, 0.007] | +0.048 [0.027, 0.072] |
| GBF, TPE-phase candidates, reference C | 0.213 [0.124, 0.318] | 0.001 [0, 0.007] | populations differ (TPE went to different places) |
| P-a permutation chance level (all 116) | 0.297 | 0.167 | observed ≪ chance: **both objectives carry ordinal information** |
| P-b self-comparison | 0 | 0 | bug detector, exact |
| P-c split-half, same instrument | 0.013 | 0.019 | small: the statistic is not measuring item noise |
| RCR (K range / C range), all 116 | 0.30 | 0.85 | |
| FLOOR (min K) · DEADBAND | 72 · 0.06 | 16 · 0.09 | |
| calibration: slope / intercept of K on J; mean K − J | 0.32 / 68; +19.6 | 0.81 / 17; +6.0 | |
| *secondary* GBF_low (candidates with C ≤ 50) | 0.47 (23 candidates) | 0.017 (67) | judge-referenced: 0.48 vs 0.22 |
| *secondary* **TBF** (share of C ≤ 10 candidates with K > 10) | **1.00** (6/6) | **1.00** (37/37) | judge-referenced: 1.00 (5/5) vs 1.00 (6/6) |

**Reading.** The F6 decomposition shows what is and is not matched across the two searches. The true spread is
matched (C spans 5–97 and 0–98), and so is the deadband (0.05 vs 0.07 on the paired draws). The floor (73 vs 25)
and the slope (0.29 vs 0.68) differ. A compressed but monotone objective still separates candidates that differ by
20/100: on Gemma, 20 reference points become about 6 keyword points, and the frozen tolerance is 1.4. So the
pairwise GBF cannot see the Gemma compression, and the premise that "the optimiser was blind over its own
candidates" fails as a *global* statement. The blindness is **local**. It sits in the low-refusal region on Gemma
(GBF_low 0.47; on the startup draws the keyword count stays at 73–84 while C runs 5–39) and at the rule's absolute threshold in **both** searches
(TBF = 1.00). The anchoring rows agree: across the 8 search × population × instrument rows, GBF correlates with κ at
ρ = −0.89 and with MAE at +0.80 (descriptive).

### Giving the incumbent its best shot (fig. 4; `results/conventional_table.csv`)

| vs judge, all judged edited rows | Gemma κ [95% CI] | MAE/100 | GaMS3 κ [95% CI] | MAE/100 |
| --- | --- | --- | --- | --- |
| keyword, shipped | 0.196 [0.178, 0.213] | 19.6 | 0.566 [0.505, 0.622] | 6.7 |
| keyword, oracle count threshold (t = 2, chosen in hindsight) | 0.567 [0.535, 0.600] | 10.5 | 0.655 [0.594, 0.708] | 6.6 |
| keyword, repaired list (5 content words + empty rule dropped) | 0.174 [0.147, 0.201] | 10.7 | **0.680** [0.616, 0.734] | **4.6** |
| certified classifier | 0.924 [0.909, 0.937]* | 1.2 | 0.801 [0.752, 0.841] | 8.7 |

\*Gemma TPE trials include 36 of the classifier's refit trials. False-refusal share of the shipped rule's positives:
0.254 (Gemma) and 0.206 (GaMS3). The repair **does** move the GaMS3 floor to 1 and halves its TBF (0.54), but it does
**nothing** for Gemma (κ 0.17, floor 45, TBF still 1.00). Gemma's false refusals are therefore not mainly the five
content words: content-word-only hits are 5–15% of keyword hits in each of the five largest harm categories (`results/dataset_audit.json`). The
oracle threshold leaves Gemma's TBF at 1.00 (floor 15). The incumbent's failure on Gemma is a property of the metric
family, not of five unlucky strings. On GaMS3 the cheap repair is the practitioner result.

### Mis-scoring vs mis-searching (S7; `results/reselection_table.csv`; decomposition only, NOT a recommendation)

| search | scorer | selected trial | rule branch | K | C | J | KL (replay) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Gemma | K (re-measured) | 107 | fallback 1 | 72 | 63 | 63 | 0.011 |
| Gemma | K (iteration-1 journal) | 96 | fallback 1 | 74 | 32 | 37 | 0.026 |
| Gemma | C | 98 | **primary** | 82 | 9 | 16 | 0.085 |
| Gemma | J | 64 | **primary** | 76 | 9 | 10 | 0.249 |
| GaMS3 | K (= journal) | 88 | fallback 1 | 16 | 0 | 1† | 0.175 |
| GaMS3 | C | 85 | **primary** | 35 | 7 | 23† | 0.015 |
| GaMS3 | J (70 judged candidates) | 115 | **primary** | 30 | 1 | 2 | 0.060 |

† post-hoc selection-point labels (tier J3; excluded from every agreement statistic). In both searches, re-scoring
the candidates the search **already held** changes the branch that fires and the candidate it picks. That is
mis-scoring, not mis-searching. The *direction* of the error differs with where the floor sits. On Gemma, fallback 1
("fewest keyword refusals") picks an under-edited candidate. On GaMS3 it picks a fully suppressed one at 3× the
KL of the judge's choice. The classifier's own choice on GaMS3 (trial 85) is **under**-edited by the judge (23/100,
37 PARTIAL), consistent with its GaMS3 undercount. Every row carries the P7 verdict: at equal English refusal the
1.5×-scaled old edit has gap +.33 (difference −.05 [−.41, +.12]); at equal harmless KL the dose ladder reaches gap
.00 (−.38 [−.47, −.29]); dose for dose the corrected edit is strictly worse.

### Bounds and the held-out-source row

* The in-loop population is AdvBench-derived (harmful_behaviors test[:100]). The dataset dependency confirms these
  are exactly the frozen S1 rows `mlhb:test:0–99`, with no near-duplicate in S4–S6 (max char-TF-IDF cosine 0.64).
  Every number above is about this population, **two searches, one seed each**.
* Held-out-source sanity (Gemma arms of iteration 3, S4 held-out-category StrongREJECT, first 100 tokens): keyword
  κ on edited English is **0.02** (81% of its "refusals" are false). On Slovene it is 0.00, because the marker list
  is English-only. The classifier scores 0.48 and 0.73. The miscalibration is therefore not an artefact of the
  in-loop set.
* The GaMS3 classifier undercount means the C-referenced GaMS3 statistics understate GaMS3's blindness. The
  judge-referenced rows are the robustness check, and they reverse the sign of the paired difference.

### Audit

`results/rederive.json`: **81/81** checks re-derived by a stdlib + numpy path with **0 mismatches**, and the
freeze-order check passes (every GaMS3 generation file is newer than `configs/FREEZE.sha256`).
`results/checks.json`: the freeze file verifies. Code edited after the freeze (`method.py`, `gbf.py`, `judges.py`,
`score.py`, `analysis.py`, `rederive.py`; so `analysis_py_unchanged = false`) is diffed in full in
`results/code_changes_since_freeze.diff`. No frozen definition changed. Every reselection row carries the P7 verdict.
`results/deviations.json` lists 18 numbered deviations. Unit tests: `results/test_gbf.json`, 8/8. OpenRouter spend:
**$0.86** (801 calls, all logged).

## What was done

A **replay-only measurement study** of the refusal objective that Heretic (pinned `3521f864`) optimises: a
33-substring English keyword counter (`KeywordRate`). Iteration 3 (art_0XmNBGkzsJc_) showed on *one* search
(google/gemma-3-12b-it) that this counter is near-exact on the unedited model but compressed on edited ones. This
artifact measures the same thing on the run's **second** search (cjvt/GaMS3-12B-Instruct, 116 trials, iteration-1
journal) and compares the two. The 60 startup parameter draws are **identical in both searches** (60/60 re-verified
from both raw journals), so the headline comparison is paired on parameters, which controls range restriction by
construction.

* **Incumbent (baseline):** Heretic's own `KeywordRate._is_match`, imported from the vendored pinned tree, never
  reimplemented. It is scored at its shipped rule, at an oracle marker-count threshold chosen in hindsight on the
  judge labels, and with a repaired list (five content words and the empty-response rule dropped).
* **Reference (method):** the certified partial-aware classifier from art_0XmNBGkzsJc_ (`scorer/refusal_clf.joblib`,
  threshold 0.52). It is re-certified here on GaMS3 text before any GaMS3 statistic is computed. The certification
  uses the frozen 4-way judge rubric: a Qwen3-14B workhorse judge on 20 certification trials, plus a bought gpt-4.1
  subsample that certifies the workhorse inside edited cells.
* **Statistic:** the **gradient-blind fraction** (GBF) is the share of candidate pairs that the reference says
  differ by at least 20/100 refusals while the objective cannot tell them apart. "Cannot tell apart" means the
  objective's two counts differ by no more than σ̄·√2, where σ̄ is the median prompt-bootstrap SD of the objective.
  The GBF is reported with cluster-bootstrap CIs over candidates, a paired bootstrap over the 60 shared draws, and
  four placebos. RCR, FLOOR and DEADBAND are reported beside it. Two secondaries were declared after the Gemma
  rehearsal and before any GaMS3 reference data: GBF_low (C ≤ 50) and the threshold-blind fraction TBF.
* **Not done, by design:** no new optimiser search; no new edited checkpoint selected, exported or recommended.
  The run's pre-registered falsifier P7 (iteration 3) stands: the corrected objective is **not a better edit**
  dose for dose. Every reselection row carries that verdict.

## Freeze and order of operations

1. S0/S1/T2 on CPU: instrument identity, both journals, and the Gemma dress rehearsal on known answers (all pass).
2. **S2 freeze** (`configs/frozen_predictions.json`, sha256 `0b3121b4…`, 16:27 UTC), written **before** any GaMS3
   generation existed. It contains the definitions, PRED-1 and its falsifier, the selection rule verbatim, both
   gates, the 20 GaMS3 certification trials (seed 20260924, 5 journal-keyword strata × 4), and the replay and judge
   tier order. It states what was already visible (the GaMS3 journal's keyword range; the whole Gemma side) and
   notes that PRED-1 was already at risk (Gemma startup GBF 0.006).
3. S3 probe → S4 replay of all 116 trials (tiers 60/10/46) → J1 workhorse labels → gpt-4.1 purchase → **both
   certifications written** → J2 extension (the remaining 50 startup draws) → analysis.
4. Post-hoc additions, all labelled: the J3 selection-point labels and the per-pair tolerance variant.

## Layout

| path | what it is |
| --- | --- |
| `method.py` | stage driver: `.venv/bin/python method.py --stages s0,s1,t2,s2,s3,s4,s4a,s4b,s4j2,s5,s6,s8,s9` (or `all`) |
| `common.py` | paths (read-only prior artifacts), I/O, logging |
| `journals.py` | S1: parses both iteration-1 Optuna journals two ways (raw jsonl and optuna), gate G1 → `results/journal_trials.csv`, `results/s1_journals.json` |
| `gbf.py` | the statistic library: prompt-bootstrap σ, GBF, per-candidate GBF, RCR/FLOOR/DEADBAND, GBF_low, TBF, calibration, bootstraps, placebos P-a…P-d, F6 decomposition |
| `tests/test_gbf.py` | T10 known-answer tests (GBF = 0 / 1 / 0 / chance) → `results/test_gbf.json` |
| `score.py` | T0 instrument identity (`results/t0_instrument.json`); K / K-count / repaired K / C / judge columns per in-loop row → `results/scored_{gemma,gams}.parquet`, `results/clf_rows_*.jsonl` |
| `analysis.py` | `--rehearsal`: Gemma dress rehearsal on known answers (`results/rehearsal_gemma.json`); default: S6 + S7 → `results/analysis.json`, `per_candidate.csv`, `conventional_table.csv`, `reselection_table.csv` |
| `freeze.py` | S2: `configs/frozen_predictions.json` + `configs/FREEZE.sha256` + code hashes (and `configs/code_at_freeze/` snapshot) |
| `replay_gams.py` | S3/S4: GaMS3 trials through Heretic's own `reset_model → abliterate → Evaluator.get_scores`, refuses to run before the freeze |
| `collect.py` | per-response logs → `results/replay/gams_inloop.jsonl`, `gams_inloop_orig.jsonl` (+ freeze-order check) |
| `judges.py` | frozen rubric judges: Qwen3-14B local, gpt-4.1 purchase (probe, cost projection, $3 hard stop) |
| `certify.py` | both certification gates → `results/judge_certification.json`, `results/gams_certification.json` |
| `descriptors.py` | closed-form kernel descriptors (validated on Gemma to < 1e-6) → `results/candidate_descriptors.csv` |
| `dataset_audit.py` | uses the dataset dependency: in-loop identity, overlap vs S4–S6, keyword failure by harm category → `results/dataset_audit.json` |
| `select_rule.py` | the frozen selection rule, verbatim copy of art_0XmNBGkzsJc_/select_rule.py (sha-identical) |
| `rederive.py` | S8: independent second code path (stdlib + numpy only) → `results/rederive.json` |
| `placebo_audit.py` | TODO-5 placebos on the independent path (shuffled judge labels, shuffled reference) → `results/placebo_audit.json` |
| `reproducibility.md` | exact commands, pins, hardware, runtimes, expected numbers |
| `checks.py` | code-freeze honesty (diff vs snapshot), P7 column present → `results/checks.json` |
| `deviations.py` | → `results/deviations.json` |
| `figures.py` | fig1–fig6 → `figures/*.pdf|png` (fig6 = K and C against the judge) |
| `to_schema.py` | → `method_out.json` (exp_gen_sol_out; one example per candidate) + `mini_`/`preview_` variants |
| `chain.sh` | the PID-based job chain actually executed after the replay |
| `third_party/heretic/` | pinned Heretic `3521f864` source tree (copied from art_0XmNBGkzsJc_, incl. its `ResponseRecorder` plugin) |
| `scorer/` | the certified classifier bundle and its iteration-3 certification/training reports (copied, sha-verified) |
| `inputs/` | copies of the frozen rubric (`exp4_protocol.yaml`), the selection rule, and the GaMS3 journal copy |
| `env/requirements.base.lock`, `pyproject.toml` | pinned environment |
| `results/replay/` | the 11,700 GaMS3 in-loop generations (116 trials × 100 + unedited baseline) and per-trial replay scores |
| `results/judge_in/`, `results/judge_out/` | judge inputs; Qwen3-14B and gpt-4.1 labels; `results/api_costs.jsonl` logs every paid call |
| `logs/` | every stage's log; `logs/inloop_scores/` holds raw per-response recorder files |

## How to run

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python --index-strategy unsafe-best-match \
    --extra-index-url https://download.pytorch.org/whl/cu128 -r env/requirements.base.lock
uv pip install --python .venv/bin/python --no-deps -e third_party/heretic
uv pip install --python .venv/bin/python fasttext-numpy2-wheel openai
.venv/bin/python method.py --stages all          # ~1.3 GPU-h replay + ~1.3 GPU-h judging on one L4 (24 GB)
# post-hoc selection-point labels (needs the reselection table from the first s6), then re-run the analysis:
.venv/bin/python method.py --stages s4j3 && .venv/bin/python method.py --stages s6,s8,s9 --force
```
The models are pulled into the shared HF cache: `cjvt/GaMS3-12B-Instruct@1d0b27af`, `Qwen/Qwen3-14B@40c06982`, and
the `google/gemma-3-12b-it@96b6f1ec` tokenizer files (gated; `HF_TOKEN` needed). The gpt-4.1 stage reads
`OPENROUTER_BASE_URL` / `OPENROUTER_API_KEY`. The Gemma side is read from art_0XmNBGkzsJc_'s stored generations
(no regeneration). Each stage writes `results/<stage>.done.json` and is skipped on re-run unless `--force` is given.

## Restoring removed files

`.aii/manifest.yaml` marks `.venv/` and the `__pycache__/` directories (top level and under `third_party/heretic/src/heretic/`) as `delete: regenerable`. The `__pycache__/` directories come back automatically the first time any script runs. Rebuild `.venv/` with:
```bash
uv venv .venv --python=3.12 && uv pip install --python .venv/bin/python --index-strategy unsafe-best-match \
  --extra-index-url https://download.pytorch.org/whl/cu128 -r env/requirements.base.lock && \
  uv pip install --python .venv/bin/python --no-deps -e third_party/heretic && \
  uv pip install --python .venv/bin/python fasttext-numpy2-wheel openai
```
Model weights are not stored in this directory. They live in the run's shared HF cache and are re-downloadable:
`huggingface-cli download cjvt/GaMS3-12B-Instruct --revision 1d0b27af5748784482600d24779409e7e1dc9adc` and
`huggingface-cli download Qwen/Qwen3-14B --revision 40c069824f4251a91eefaf281ebe4c544efd3e18`.
Everything under `results/`, `scorer/`, `figures/`, `configs/` and `logs/` is kept, and it stays on the run's volume.
Files of 100 MB or more are not pushed to the published repository; none are expected here.
