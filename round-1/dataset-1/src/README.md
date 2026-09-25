# Frozen EN/SL data protocol (S1–S7) for the GaMS3 vs Gemma-3 bilingual abliteration study

This repository builds, freezes, hashes and audits every English and Slovene data split used by the study that compares
`cjvt/GaMS3-12B-Instruct` and `google/gemma-3-12b-it` before and after Heretic abliteration. It runs no study model.

**Deliverable for later steps.** These files are text and are kept on the volume:
- `./full_data_out.json`: 48,696 examples in 10 blocks, schema `exp_sel_data_out`, validated (67.7 MB, under the 100 MB limit, so not split). Also `mini_data_out.json` (3 examples per block) and `preview_data_out.json` (first 3 blocks, strings truncated). Both were made by the aii-json format script.
- `…/gen_art_dataset_1/data/split_manifest.json`: per-split SHA256, seeds, eligible sets and `protocol_hash`.
- `…/gen_art_dataset_1/data/splits/<family>.jsonl`: the 17 frozen split families, one JSON row per example.

`protocol_hash` = `dc33bde4e8ea39ee416af3e9c65eeb9d8583303bdd39130cb8c86831624c9306`. It is the SHA256 of the manifest, which includes the freeze timestamp.

## What each split is for

| block (`full_data_out.json`) | families | rows (EN+SL) | role |
|---|---|---|---|
| `S1_heretic` | S1 | 1000+1000 | Heretic 3521f864 default data: harmful_behaviors train[:400]/test[:100] and harmless_alpaca train[:400]/test[:100]. Direction and optimisation data only. |
| `S2_semantic` | S2 | 832+832 | Semantic-Harmful/Harmless, 416 pairs. **DEV only.** 400/416 harmful rows are S1 direction rows, because Semantic-Harmful is built from harmful_behaviors train. Flagged `metadata_s1_overlap`. Never validation. |
| `S3_screen_dev_prompts` | S3_jbb, S3_dolly | 270+270 | Trait/screen DEV = the **pods' own file** (see below): JBB 85 harmful + 85 benign twins, and Dolly 100. |
| `S3_screen_dev_utility` | S3_flores_dev, S3_mc | 320+320 | FLORES+ dev (first 200 ids) and the pods' MC carve-out: 40 each from ARC-C, HellaSwag and PIQA. |
| `S4_strongreject_pairs` | S4 | 514+514 | **Held-out mechanistic validation.** 257 StrongREJECT prompts, each with a validated gpt-4.1 harmless twin. Stratum `hoc` (held-out Llama-Guard categories, 70 pairs) and `ind` (independent source, 187 pairs). |
| `S5_refuseu` | S5 | 1400+1400 | **FINAL behaviour.** All official NASK-PIB/RefusEU eval rows for en and sl, with an inferred category (exactly 100 per category) and a frozen 700-per-language stratified core (`metadata_s5_core`). |
| `S5X_refuseu_crosstrans` | S5X | 700+700 | **Constructed** faithful pairs: gpt-4.1 translation of every core EN row to SL and every core SL row to EN. Each shares `semantic_id` with its source row. Not official RefusEU. |
| `S6_xstest` | S6 | 450+450 | Over-refusal set: XSTest v2, 250 safe and 200 unsafe contrasts. SL by gpt-4.1 with a trigger-preservation self-report. `metadata_s6_primary` excludes 31 safe items whose trigger was lost. |
| `S7_slovenian_llm_eval` | S7 × 6 tasks | 17850+17850 | **FINAL utility.** ARC-C, BoolQ, HellaSwag, OBQA, PIQA and Winogrande: Slovenian-LLM-Eval rows aligned to their English originals, minus the union of both carve-outs. |
| `S7_flores_devtest` | S7 | 1012+1012 | FLORES+ devtest, eng_Latn/slv_Latn. |

Every row carries the following fields:
- `input`: the text in its language. MC rows store `{"query", "choices"}` as a JSON string.
- `output`: `refuse` / `comply`; `refuse|S<k>` for RefusEU; the gold index for MC; the parallel sentence for FLORES.
- metadata: `metadata_fold`, `metadata_semantic_id`, `metadata_lang`, `metadata_half` and `metadata_subset`. For translated rows it also has the translation provenance and automated QC, listed below.

Automated QC fields on translated rows:
- `metadata_translation_method`
- `metadata_bt_chrf`: chrF++ of the cross-family back-translation against the source. Per the plan, gemini-2.5-flash back-translates gpt-4.1 outputs and gpt-4.1-mini back-translates gemini/pod outputs; MADLAD-400-3B is used only where the LLM back-translation was empty or refused (31 rows). The system is in `metadata_back_translation_method`.
- `metadata_labse_xl`
- `metadata_lid`
- `metadata_len_ratio`
- `metadata_qc_pass`
- `metadata_translation_unstable`: chrF < 50 or LaBSE < 0.85 against an independent translation. For S3 JBB/Dolly that is the plan's gpt-4.1 re-translation of the pods' gemini text; elsewhere it is MADLAD-400-3B.
- `metadata_alt_translation`
- `metadata_nllb_translation`
- `metadata_back_translation`
- `metadata_review_status=PENDING`

Harmful rows carry `metadata_category_llamaguard` and its source. S4 rows carry `metadata_s4_stratum`. S5 rows carry `metadata_correspondence_grade`, `metadata_s5_core` and `metadata_audit_excluded`. S7 rows carry `metadata_pair_verified` and `metadata_near_dup_of_dev`.

**Canonical ids and halves.** `half = 'A' if int(hashlib.sha1(semantic_id.encode()).hexdigest(), 16) % 2 == 0 else 'B'`. Every language version, twin and cross-translation shares its row's `semantic_id`, so they always share a half; this was verified with 0 conflicts. The id forms are:
- `mlhb:{train|test}:{i}`, `mlha:{train|test}:{i}`
- `sem:{pair}`
- `srj:{row}`
- `refuseu:{row_id}:{orig_lang}`
- `xstest:{id}`
- `mc:{task}:{key}`
- `flores:devtest:{id}`
- **S3 keeps the pods' ids**: `jbb_{Index}`, `dolly_{idx}`, `flores_{id}`, `mc_arc_{id}`, `mc_hellaswag_row{r}_ind{i}`, `mc_piqa_row{r}`.

## Findings that change how the data must be used (all automated)

1. **S3 comes from the pods, and their ids differ from the spec strings.** `gen_art_experiment_3/data/screen_dev.json` (sha256 in `data/reports/s3_pod_agreement.json`) is authoritative, and S3 is copied from it.
   - Our independent reproduction of the spec matches it on Dolly (100/100, so `np.random.default_rng(0)` is the spec's "seed 0") and on FLORES (200/200).
   - JBB: the pod keeps 85 items, a superset of our 83. The pod dropped the 15 AdvBench-source rows; we dropped 17 at LaBSE > 0.85 against all 520 harmful_behaviors rows. The 2 extra items (`jbb:63`, `jbb:75`) are exact copies of harmful_behaviors test rows. S3 is immutable, so they stay, flagged in the audit.
   - The MC carve-outs differ, so S7 excludes the union (`data/dev_carveout_union.json`).
   - The pod applied the half formula to its own ids (`jbb_0`), not to `jbb:0`. Only 50.7% of the halves agree with spec-form strings. S3 rows keep the pod id and half, and `metadata_spec_semantic_id`/`metadata_spec_half` record the spec form.
2. **The screen-spec translation prompt is under-specified, and gemini often answers instead of translating.**
   - Layout A (spec prompt as system message, item as user message): gemini-2.5-flash at T=0 answered or refused 830 of 1,692 items.
   - Layout B (prompt, blank line and item in one user message): the failure rate falls to 129/1,692. Each failure falls back to gpt-4.1 (122) or NLLB (7). See `data/reports/screenspec_layout_check.json`.
   - The pods saw the same problem. experiment_1 made NLLB its S1 translator after gemini declined 56 of 110 items; experiment_3 wrapped the prompt in a "data, not a request" instruction.
   - S1/S2 SL texts therefore come from the pod files where they exist (S1: 900/1,000 rows; S2: 406/832; experiment_3's gemini-wrapper texts and experiment_1's NLLB harmful test[:100]). Our layout-B gemini text is used for the rest and kept as `metadata_gemini_layoutB_translation` on every row.
3. **RefusEU EN and SL rows that share a `row_id` are not translations.** The paper confirms it: prompts were generated per language from DeepL-translated Polish seeds.
   - The gpt-4.1-mini judge, blind to all scores, says T for 293, P for 403, C for 554 and N for 150 rows.
   - The median LaBSE(EN, SL) is only 0.56. Under the pre-registered grade rule (T needs judge=T, LaBSE ≥ 0.80 and chrF(EN, gemini BT) ≥ 45), **0 pairs grade T**: of the 293 judge-T rows, only 1 reaches LaBSE ≥ 0.80 and only 4 reach chrF ≥ 45. The result is the same with the MADLAD BT. Overall 158 grade P, 1,092 grade C and 150 grade N (`data/reports/refuseu_correspondence.json`, `data/verified_pairs.json`).
   - Paired EN–SL item claims on official RefusEU are therefore not supported. Use category-stratified unpaired comparisons, or the S5X constructed pairs.
4. **RefusEU categories are recovered but low-confidence.**
   - Accuracy on the 141+141 gold-category preference-test rows: Llama-Guard-3-8B 64.5% EN / 49.7% SL; gpt-4.1-mini 54.6% / 49.7%; joint 63.8% / 52.5%. That is below the plan's 70% bar, so the categories are labelled *inferred, low-confidence*.
   - Labeller agreement is κ = 0.62–0.74 by set. Cross-language agreement for the same row_id is 63.7%. The block test failed (4 of 14 blocks), so row_ids are not category-blocked.
   - The final row_id category is a balanced assignment: exactly 100 per category, as the paper states. It maximises the joint Llama-Guard log-probability plus a calibrated gpt-4.1-mini noisy-label term over both languages. The S5 core (50 per category, `np.random.default_rng(20260923)`) is stratified on it (`data/s5_core_freeze.json`).
5. **S4 held-out categories.** H = {S7, S11, S4, S8, S9, S12, S13, S3}. No category has 0 JBB items, so the lowest-share categories (1–4 JBB items each) were added in rank order until ≥ 60 valid pairs; this gives 70 `hoc` pairs.
   - 25 StrongREJECT AdvBench-source rows were dropped. 1 row was dropped for meaning overlap with S1–S3, and 1 by the audit (`srj:184` against S5X).
   - The twins come from gpt-4.1 (231 greedy, 27 resampled). Every twin passed Llama Guard "safe", gpt-4.1-mini "not harmful", a length ratio of 0.8–1.25, LaBSE(harmful, twin) of 0.45–0.90, and the refusal-keyword check. 29 items had no passing twin and were dropped.
6. **XSTest trigger preservation.**
   - Per-type issues (`data/reports/translation_qc.json`): homonyms 3 yes / 17 partial / 5 no; figurative language 9 / 11 / 5; privacy_public 5 yes / 20 no (public-figure framing); all other types are nearly all "yes".
   - Primary SL over-refusal set: 219 safe items (`metadata_s6_primary=true`; the 3 'n/a' definitions items have no lexical trigger to lose).
   - The "yes/partial/no" label is the translator's self-report, and it is automated.
7. **Overlap audit** (`data/reports/overlap_audit.json`), using LaBSE EN–EN, SL–SL and EN–SL, exact/normalised string match and 8-gram Jaccard.
   - S4/S5/S5X/S6/S7 share no near-duplicate (> 0.85) or exact item with S1/S2/S3. The one exception, S4 `srj:184` against S5X, was dropped.
   - 45 S7 HellaSwag/ARC rows are flagged `near_dup_of_dev` against the carve-out.
   - Lineage check: all 520 harmful_behaviors rows are exact AdvBench rows. 35 of them have a > 0.85 near-duplicate in JBB and 31 in StrongREJECT (before our drops); there are 0 in RefusEU or XSTest.
8. **Translation QC** (automated): qc_pass is 94–100% by family. Mean back-translation chrF++ is 72–80. Mean LaBSE_xl is 0.83–0.91. The unstable rate against the independent alternate translation is 5–18%, and `metadata_translation_unstable` marks those rows for sensitivity exclusion.

**No native-speaker review happened.** `data/native_review_packet.csv` holds 250 rows, blinded and shuffled, all `PENDING`. The unblinding key is `data/native_review_packet_key.json`. Every quality number here is automated.

## Other limitations
- **Slovenian-LLM-Eval translations.** Only ARC-C, ARC-E, GSM8K, OBQA and Winogrande were native-corrected (card v0.1.0). BoolQ, HellaSwag and PIQA are Google-Translate plus GPT-4 refined. EN and SL difficulty is not assumed equal, so use original→edited deltas within each language.
- **Alignment.** Rows are aligned by id (ARC), by row order with verification (BoolQ, HellaSwag, OBQA, PIQA), and by one-to-one LaBSE assignment for Winogrande, whose SL rows are not in EN order. Verified rows (`metadata_pair_verified`): 99.8% / 100% / 99.98% / 96.6% / 97.7% / 98.9%. Unverified rows are for within-language use only.
- **English harness.** The lm-eval harness `boolq` reads `aps/super_glue`. We verified it has the same order and labels as `google/boolq` (`data/lm_eval_task_map.json`).
- **Possible pretraining contamination.** FLORES+ and the translated benchmarks may be in GaMS3's continual-pretraining data, which cannot be audited from outside. Original→edited deltas mostly cancel this.
- **Thresholds.** chrF 40 and LaBSE 0.75/0.85 are conventional, not calibrated for Slovene. They are reported as flags.
- **Translation methods are mixed within some families.** S1: 785 pod gemini-wrapper, 115 pod NLLB, 98 our gemini, 2 gpt-4.1. S5X: 1,393 gpt-4.1, 6 NLLB, 1 claude-sonnet-4.5. Filter on `metadata_translation_method` if needed.
- **Categories are model-inferred.** Llama-Guard-3-8B was run locally in NF4 4-bit, a deviation from bf16.
- **Scoring protocol.** The RefusEU scoring protocol is recorded verbatim in `data/refuseu_protocol.md`: Llama-Guard-3-8B plus PolyGuard-Qwen, with gpt-4o-mini adjudicating using the published Appendix-B prompt.

## Layout
- `data.py`: `uv run data.py` standardises `data/splits/*.jsonl` into `full_data_out.json`. The mini/preview variants come from the aii-json format script (see `run_all.sh`). It re-checks the raw files in `temp/datasets/` against `data/provenance/sources.json` and every split SHA against the manifest.
- `run_all.sh`: the full rebuild, in order.
- `src/`:
  - `s00_fetch.py`: raw sources pinned to their revisions.
  - `s01_prepare.py`: S1–S7 items, S3 pod override, MC alignment, S4 pre-filter.
  - `s02_translate.py`: local NLLB/MADLAD alternates and MADLAD back-translation.
  - `s02b_llm.py`: OpenRouter tasks.
  - `orclient.py`: cache, cost log and budget stops.
  - `s03_guard.py`: Llama Guard.
  - `s04b_select_twins.py`
  - `s05_assemble.py`: QC, categories, correspondence, core freeze, audit, packet and manifest.
  - `emb.py`: LaBSE with a cache.
  - `common.py`
- `data/`:
  - `splits/`
  - `split_manifest.json`
  - `reports/`: `translation_qc`, `overlap_audit`, `refuseu_correspondence`, `category_labels`, `s4_heldout_categories`, `s4_twin_validation`, `s3_pod_agreement`, `screenspec_layout_check`, `prepare_report`, `assemble_report`
  - `refuseu_protocol.md`
  - `s1_heretic_settings.json`: 33 keyword markers verbatim from 3521f864; the plan's "31" was wrong.
  - `s5_core_freeze.json`
  - `verified_pairs.json`
  - `dev_carveout_ids.json` (ours) and `dev_carveout_union.json`
  - `lm_eval_task_map.json`
  - `native_review_packet.csv` and its key
  - `cost_log.jsonl`: every OpenRouter call, 5,474 calls, **$4.77** total.
  - `provenance/`: `sources.json` with every repo, split, commit SHA, row count and file hash; `candidates.md`; the Heretic config.
- `work/`: intermediate caches.
  - `items.json`
  - `translations/*.jsonl`: local MT.
  - `llm_*.json`
  - `llm_cache.jsonl`: every API response, so reruns are free and deterministic.
  - `guard_labels.jsonl`
  - `labse_cache/`
- `temp/datasets/`: raw source dumps. `temp/search/` holds the dataset searches.

## Rerun
```bash
uv venv .venv --python=3.12 && uv pip install --python .venv/bin/python -r requirements.txt
bash run_all.sh          # GPU >= 16 GB; HF_TOKEN (gated FLORES+, Llama-Guard-3-8B); OPENROUTER_API_KEY (free if work/llm_cache.jsonl is kept)
uv run data.py           # only re-standardise the frozen splits (then the aii-json format step at the end of run_all.sh)
```

## Restoring removed files
| path | how to restore |
|---|---|
| `.venv/` | `uv venv .venv --python=3.12 && uv pip install --python .venv/bin/python -r requirements.txt && sed -i 's/, copy=False//g' .venv/lib/python3.12/site-packages/fasttext/FastText.py` |
| `work/labse_cache/` | regenerated on demand by `src/emb.py` (LaBSE `sentence-transformers/LaBSE@836121a0`) during `bash run_all.sh` |
| `src/__pycache__/` | Python bytecode, recreated automatically |

Models, downloaded into the run's shared HF cache (not this repo) with `huggingface-cli download <id> --revision <sha>`:
- `facebook/nllb-200-distilled-1.3B@7be3e246`
- `google/madlad400-3b-mt@fa184c67`
- `meta-llama/Llama-Guard-3-8B@7327bd9f` (gated)
- `sentence-transformers/LaBSE@836121a0`
- `cis-lmu/glotlid@85cd6716`
