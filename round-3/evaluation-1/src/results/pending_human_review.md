# Pending human review (consolidated)

No native-speaker review has been carried out anywhere in the run. Every judge is automated. The packets below are ready; until they are labelled, all behavioural numbers are 'ranges across automated judges'.

| path | n | language mix | status | note |
|---|---|---|---|---|
| `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_4/results/human_packet/packet.csv` | 200 | {'sl': 100, 'en': 100} | PENDING native review | blinded EN/SL behaviour packet (class, harmful, language_ok); NOT yet labelled by a native speaker |
| `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_5/results/native_review_packet_c1u.csv` | 120 | {'en': 60, 'sl': 60} | PENDING native review | native-review packet for C1 utility/refusal replies; key in *_KEY.csv |
| `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1/gen_art/gen_art_dataset_1/data/native_review_packet.csv` | 250 | {'en->sl': 229, 'sl->en': 21} | PENDING native review | translation adequacy/fluency/trigger-preservation packet |
| `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1/gen_art/gen_art_experiment_1/results/sl_label_sample.json` | 40 | {'sl': 40} | EXECUTOR-labelled (NOT native) | labeller: artifact executor (NOT a native speaker) - NATIVE_REVIEW_PENDING |
| `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_4/results/executor_audit.json` | 30 | EN+SL | EXECUTOR check (NOT native) | 30-item executor check of the judge (kappa .67 5-way / .93 binary as reported by exp4) |

## Translation provenance per set (from gen_art_dataset_1 split files; automated QC only)

| set | rows | SL rows | SL translation methods (top) | mean back-translation chrF++ (n) |
|---|---|---|---|---|
| S1_heretic | 2000 | 1000 | {'pod_file(google/gemini-2.5-flash)': 785, 'pod_file(facebook/nllb-200-distilled-1.3B@7be3e24664b38ce1cac29b8aeed6911aa0cf0576)': 100, 'gemini25flash_screenspec': 98, 'pod_file(facebook/nllb-200-distilled-1.3B (fallback: gemini chrF<40))': 9, 'pod_file(facebook/nllb-200-distilled-1.3B (fallback))': 6, 'gpt41': 2} | 79.7 (1000) |
| S2_semantic | 1664 | 832 | {'gemini25flash_screenspec': 422, 'pod_file(google/gemini-2.5-flash)': 399, 'pod_file(facebook/nllb-200-distilled-1.3B (fallback))': 4, 'pod_file(facebook/nllb-200-distilled-1.3B (fallback: gemini chrF<40))': 3, 'gpt41': 3, 'nllb13b': 1} | 79.2 (832) |
| S3_dolly | 200 | 100 | {'pod_file(google/gemini-2.5-flash)': 96, 'pod_file(facebook/nllb-200-distilled-1.3B (fallback: gemini chrF<40))': 4} | 76.6 (100) |
| S3_flores_dev | 400 | 200 | {'original': 200} |  (0) |
| S3_jbb | 340 | 170 | {'pod_file(google/gemini-2.5-flash)': 167, 'pod_file(facebook/nllb-200-distilled-1.3B (fallback))': 2, 'pod_file(facebook/nllb-200-distilled-1.3B (fallback: gemini chrF<40))': 1} | 77.4 (170) |
| S3_mc | 240 | 120 | {'original': 120} |  (0) |
| S4_strongreject_pairs | 1028 | 514 | {'gpt41': 514} | 80.1 (514) |
| S5X_refuseu_crosstrans | 1400 | 700 | {'gpt41': 700} | 78.9 (700) |
| S5_refuseu | 2800 | 1400 | {'original': 1400} |  (0) |
| S6_xstest | 900 | 450 | {'gpt41': 449, 'nllb13b': 1} | 78.5 (450) |
| S7_arc_challenge | 2184 | 1092 | {'original': 1092} |  (0) |
| S7_boolq | 6540 | 3270 | {'original': 3270} |  (0) |
| S7_flores_devtest | 2024 | 1012 | {'original': 1012} |  (0) |
| S7_hellaswag | 19924 | 9962 | {'original': 9962} |  (0) |
| S7_openbookqa | 1000 | 500 | {'original': 500} |  (0) |
| S7_piqa | 3518 | 1759 | {'original': 1759} |  (0) |
| S7_winogrande | 2534 | 1267 | {'original': 1267} |  (0) |

Notes: S5 (official RefusEU) EN and SL rows that share a row_id are NOT translations (0 of 1,400 pairs grade T; `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1/gen_art/gen_art_dataset_1/data/reports/refuseu_correspondence.json`), so paired cross-language claims use S5X only. FLORES+ devtest is human-translated.

## Cross-machine reproducibility (exp6 repro_check.json), with units

| edit | trait | max abs diff | mean abs diff | unit |
|---|---|---|---|---|
| E0_000 | Ereal | 0.04554 | 0.008096 | realised exposure (norm units) |
| E0_000 | Hproj | 92.72 | 13.61 | raw residual projection, layer 34 (magnitude ~2000-3000) |
| E0_000 | KL | 0.001538 | 0.0003249 | nats (truncated KL) |
| E0_000 | MCmargin | 0.1392 | 0.01902 | log-prob margin |
| E0_000 | NLL | 0.01831 | 0.004696 | nats/token |
| E0_000 | NLLflo | 0.03712 | 0.008625 | nats/token (FLORES) |
| E0_000 | Pproj | 41.72 | 11.11 | raw residual projection |
| E0_000 | R1 | 0.2284 | 0.04442 | first-token log-odds |
| E0_000 | R_seq | 0.03168 | 0.008458 | log-odds (sequence refusal readout) |
| E0_000 | Rb1 | 0.2442 | 0.06311 | log-odds |
| E0_000 | Rb_seq | 0.03909 | 0.01083 | log-odds |
| E0_049 | Ereal | 0.01855 | 0.002446 | realised exposure (norm units) |
| E0_049 | Hproj | 97.23 | 18.62 | raw residual projection, layer 34 (magnitude ~2000-3000) |
| E0_049 | KL | 0.00207 | 0.0002975 | nats (truncated KL) |
| E0_049 | MCmargin | 0.1359 | 0.01849 | log-prob margin |
| E0_049 | NLL | 0.0175 | 0.004974 | nats/token |
| E0_049 | NLLflo | 0.1156 | 0.008911 | nats/token (FLORES) |
| E0_049 | Pproj | 58.96 | 10.98 | raw residual projection |
| E0_049 | R1 | 0.2526 | 0.05958 | first-token log-odds |
| E0_049 | R_seq | 0.03997 | 0.009664 | log-odds (sequence refusal readout) |
| E0_049 | Rb1 | 0.25 | 0.05842 | log-odds |
| E0_049 | Rb_seq | 0.03148 | 0.009516 | log-odds |
| E0_051 | Ereal | 0.05711 | 0.01046 | realised exposure (norm units) |
| E0_051 | Hproj | 41.86 | 8.39 | raw residual projection, layer 34 (magnitude ~2000-3000) |
| E0_051 | KL | 0.001727 | 0.0003705 | nats (truncated KL) |
| E0_051 | MCmargin | 0.1304 | 0.01834 | log-prob margin |
| E0_051 | NLL | 0.01606 | 0.004416 | nats/token |
| E0_051 | NLLflo | 0.04918 | 0.00826 | nats/token (FLORES) |
| E0_051 | Pproj | 54.6 | 9.844 | raw residual projection |
| E0_051 | R1 | 0.2494 | 0.05365 | first-token log-odds |
| E0_051 | R_seq | 0.04089 | 0.008667 | log-odds (sequence refusal readout) |
| E0_051 | Rb1 | 0.2425 | 0.04702 | log-odds |
| E0_051 | Rb_seq | 0.03267 | 0.009659 | log-odds |
