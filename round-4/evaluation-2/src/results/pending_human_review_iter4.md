# Pending human review (consolidated, iteration 4)

This list supersedes `iter_3/gen_art/gen_art_evaluation_1/results/pending_human_review.md`. It was built by scanning every iteration-1/2/3 artifact workspace for review-packet files (patterns: packet, human_review, native_review, review_packet; answer keys excluded). **No native-speaker or human review has happened anywhere in the run.** Every judged rate in the paper is proxy-certified (gpt-4.1 as frontier proxy), not human-certified.

Paths are relative to the run's `3_invention_loop/` directory.

| # | file | kind | items | language mix | what it would resolve |
|---|---|---|---|---|---|
| 1 | `iter_1/gen_art/gen_art_dataset_1/data/native_review_packet.csv` | native-review packet (unlabelled) | 250 | None | translation fidelity of the frozen Slovene test sets (S3-S7), the basis of every paired EN/SL claim |
| 2 | `iter_1/gen_art/gen_art_experiment_1/results/sl_label_sample.json` | EXECUTOR check (not native; labelled by an artifact executor) | 40 | {} | iteration-1 Slovene refusal labels (executor-labelled, 40 items); needs native relabelling |
| 3 | `iter_2/gen_art/gen_art_experiment_4/results/executor_audit.json` | EXECUTOR check (not native; labelled by an artifact executor) | 30 | {} | 30-item executor check of the exp4 judge (kappa .67 5-way / .93 refused-vs-not); needs native relabelling |
| 4 | `iter_2/gen_art/gen_art_experiment_4/results/human_packet/packet.csv` | native-review packet (unlabelled) | 200 | {'sl': 100, 'en': 100} | blinded EN/SL refusal/partial/compliance labels on the FINAL four-checkpoint panel; certifies the workhorse and gpt-4.1 judges against humans |
| 5 | `iter_2/gen_art/gen_art_experiment_5/results/native_review_packet_c1u.csv` | native-review packet (unlabelled) | 120 | {'en': 60, 'sl': 60} | Slovene behaviour labels on the utility/inner-signal panel (c1u packet); certifies the S4 refusal rates used by the flip analysis |

Also pending (not packets): the executor-only 30-item blind check in art_m6pglf516e2r (kappa .67 5-way / .93 refused-vs-not) and this artifact's 900-item gpt-4.1 calibration (`results/calibration_sample.json`) are MODEL certifications. They are not human review.

Reference this list once in the paper, e.g. 'Native review is pending for N packets (Appendix: pending_human_review_iter4.md)'.
