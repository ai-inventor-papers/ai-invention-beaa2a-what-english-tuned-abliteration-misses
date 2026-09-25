# Pending human review: ONE consolidated list (status PENDING; nothing here has been reviewed)

No native-speaker or human review has been conducted anywhere in the run. The reviewing is UNOWNED. Every Slovene behavioural number is machine-translated and machine-judged, and carries that constraint.

## Carried list (verbatim from `round-4/evaluation-2/src/results/pending_human_review_iter4.md`)

# Pending human review (consolidated, iteration 4)

This list supersedes `round-3/evaluation-1/src/results/pending_human_review.md`. It was built by scanning every iteration-1/2/3 artifact workspace for review-packet files (patterns: packet, human_review, native_review, review_packet; answer keys excluded). **No native-speaker or human review has happened anywhere in the run.** Every judged rate in the paper is proxy-certified (gpt-4.1 as frontier proxy), not human-certified.

Paths are relative to the run's `3_invention_loop/` directory.

| # | file | kind | items | language mix | what it would resolve |
|---|---|---|---|---|---|
| 1 | `round-1/dataset-1/src/data/native_review_packet.csv` | native-review packet (unlabelled) | 250 | None | translation fidelity of the frozen Slovene test sets (S3-S7), the basis of every paired EN/SL claim |
| 2 | `round-1/experiment-1/src/results/sl_label_sample.json` | EXECUTOR check (not native; labelled by an artifact executor) | 40 | {} | iteration-1 Slovene refusal labels (executor-labelled, 40 items); needs native relabelling |
| 3 | `round-2/experiment-4/src/results/executor_audit.json` | EXECUTOR check (not native; labelled by an artifact executor) | 30 | {} | 30-item executor check of the exp4 judge (kappa .67 5-way / .93 refused-vs-not); needs native relabelling |
| 4 | `round-2/experiment-4/src/results/human_packet/packet.csv` | native-review packet (unlabelled) | 200 | {'sl': 100, 'en': 100} | blinded EN/SL refusal/partial/compliance labels on the FINAL four-checkpoint panel; certifies the workhorse and gpt-4.1 judges against humans |
| 5 | `round-2/experiment-5/src/results/native_review_packet_c1u.csv` | native-review packet (unlabelled) | 120 | {'en': 60, 'sl': 60} | Slovene behaviour labels on the utility/inner-signal panel (c1u packet); certifies the S4 refusal rates used by the flip analysis |

Also pending (not packets): the executor-only 30-item blind check in art_m6pglf516e2r (kappa .67 5-way / .93 refused-vs-not) and this artifact's 900-item gpt-4.1 calibration (`results/calibration_sample.json`) are MODEL certifications. They are not human review.

Reference this list once in the paper, e.g. 'Native review is pending for N packets (Appendix: pending_human_review_iter4.md)'.


## Also pending

- `round-2/experiment-5/src/results/native_review_packet_c1u.csv` with its key `native_review_packet_c1u_KEY.csv` (blinded C1 utility/refusal packet).
- `results/sl_recert_draw_spec.json` (this audit): a gpt-4.1 purchase, not a human review; listed so the two are never confused.
