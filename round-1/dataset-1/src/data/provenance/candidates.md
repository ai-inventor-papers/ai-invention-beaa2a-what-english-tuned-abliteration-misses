# Candidate datasets considered (TODO 3-5)

Downloads, gating and row counts come from the HF Hub API and the datasets-server, fetched on 2026-09-23. The 50 broad searches are in `temp/search/`. The full candidate previews are in `temp/candidates_preview.json`.

| # | dataset | downloads | gated | rows (all configs) | decision | role / reason |
|---|---|---|---|---|---|---|
| 1 | `mlabonne/harmful_behaviors` | 23139 | False | 520 | KEEP | S1 Heretic default harmful (AdvBench lineage; verified exact-match to llm-attacks CSV) |
| 2 | `mlabonne/harmless_alpaca` | 22387 | False | 31323 | KEEP | S1 Heretic default harmless (Alpaca) |
| 3 | `heretic-org/Semantic-Harmful` | 887 | False | 416 | KEEP | S2 mechanistic DEV; built FROM harmful_behaviors train (416/416 rows) -> DEV-only |
| 4 | `heretic-org/Semantic-Harmless` | 665 | False | 416 | KEEP | S2 twins (Hungarian-matched, embeddinggemma, thr 0.60) |
| 5 | `JailbreakBench/JBB-Behaviors` | 49614 | False | 500 | KEEP | S3 trait DEV (screen spec); NeurIPS'24 D&B; 100 harmful + 100 topic-matched benign |
| 6 | `databricks/databricks-dolly-15k` | 62679 | False | 15011 | KEEP | S3 harmless continuation prompts (screen spec) |
| 7 | `openlanguagedata/flores_plus` | 12666 | auto | 898930 | KEEP | S3 FLORES dev (first 200) + S7 FLORES devtest; human-translated eng/slv parallel |
| 8 | `cjvt/slovenian-llm-eval` | 194 | False | 271374 | KEEP | S7 Slovene utility (6 tasks); Apache-2.0; the GaMS team's own eval suite |
| 9 | `allenai/ai2_arc` | 878509 | False | 7787 | KEEP | S7 EN original ARC-Challenge test (harness split) |
| 10 | `google/boolq` | 210427 | False | 12697 | KEEP | S7 EN original BoolQ validation (row order == aps/super_glue harness split, verified) |
| 11 | `Rowan/hellaswag` | 447374 | False | 59950 | KEEP | S7 EN original HellaSwag validation (harness split) |
| 12 | `allenai/openbookqa` | 484782 | False | 11914 | KEEP | S7 EN original OBQA main test (harness split) |
| 13 | `baber/piqa` | 140307 | False | 21035 | KEEP | S7 EN original PIQA validation (the parquet mirror lm-eval uses) |
| 14 | `allenai/winogrande` | 403758 | False | 81442 | KEEP | S7 EN original winogrande_xl validation (harness split) |
| 15 | `walledai/StrongREJECT` | 4710 | auto | None | KEEP via ungated original CSV | S4 held-out mechanistic validation; NeurIPS'24 D&B; used github:alexandrasouly/strongreject CSV (same 313 rows) |
| 16 | `walledai/XSTest` | 7662 | auto | None | KEEP via ungated original CSV | S6 over-refusal; NAACL'24; used github:paul-rottger/xstest xstest_prompts.csv (450 rows, v2) |
| 17 | `NASK-PIB/RefusEU` | 56 | False | 86136 | KEEP (user-mandated) | S5 FINAL behaviour; ACL Findings 2026; only 56 downloads but mandated by the study and documented by a paper |
| 18 | `sorry-bench/sorry-bench-202406` | 846 | auto | None | DISCARD | gated top-up source; not needed (S4 reached 257 pairs without top-up) |
| 19 | `walledai/MaliciousInstruct` | 1708 | False | 100 | DOWNLOADED, NOT USED | top-up reserve; 12 of its prompts already inside StrongREJECT |
| 20 | `bench-llm/or-bench` | 9371 | False | 82333 | DISCARD | over-refusal alternative; XSTest is the plan's standard small set; OR-Bench-hard is LLM-generated and large |
| 21 | `DAMO-NLP-SG/MultiJail` | 1073 | False | 315 | DISCARD | human-translated multilingual jailbreak set but NO Slovene |
| 22 | `CohereLabs/aya_redteaming` | 1159 | False | None | DISCARD | multilingual red-teaming but NO Slovene; datasets-server 501 |
| 23 | `walledai/AdvBench` | 14749 | auto | None | DISCARD (use original CSV) | lineage audit uses github llm-attacks harmful_behaviors.csv directly |
| 24 | `walledai/HarmBench` | 7494 | auto | None | DISCARD (use original CSV) | lineage context via github centerforaisafety HarmBench CSV (JBB TDC/HarmBench rows) |
| 25 | `LibrAI/do-not-answer` | 4009 | False | 939 | DISCARD | no Slovene, no benign twins; not needed by the protocol |

Also downloaded as ungated originals from GitHub, each pinned to its commit: StrongREJECT CSV, XSTest CSV, AdvBench `harmful_behaviors.csv` (lineage audit) and HarmBench `behaviors_text_all.csv`. See `data/provenance/sources.json`.

The 15 datasets that carry the protocol are: harmful_behaviors, harmless_alpaca, Semantic-Harmful, Semantic-Harmless, JBB-Behaviors, dolly-15k, flores_plus, slovenian-llm-eval, ai2_arc, boolq, hellaswag, openbookqa, piqa, winogrande, StrongREJECT, XSTest and RefusEU. That is 17 repositories: the 6 English utility originals count as one family and Semantic-Harmful/Harmless as one.
