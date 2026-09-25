# Inventory reconciliation (phase 0)

Pooled table: `results/pooled_generations.parquet`, **56,866 rows** in total (52,066 from the four iteration-3 panels + 4,800 from the iteration-2 FINAL panel).

The plan's claimed four-panel total is 27,784 + 10,690 + 3,680 + 9,199 = 51,353.
The four iteration-3 panels load as **52,066** rows (+713 against the claim). The whole difference is exp12: its 9,912 generation rows carry 9,199 DISTINCT judge keys sha256('qwen:V2|prompt|response|lang') (identical generations share one label), which is the 9,199 the artifact reports. So the claim reconciles exactly at the level of distinct judged generations.

| source | artifact | claimed | loaded | with workhorse label | no label | missing response | with gpt-4.1 label | cells |
|---|---|---|---|---|---|---|---|---|
| exp9 | art_ex4hbgThhJaL | 27,784 | 27,784 | 27,784 | 0 | 0 | 600 | 122 |
| exp10 | art_xLy2vVlI7OEL | 10,690 | 10,690 | 10,690 | 0 | 0 | 302 | 57 |
| exp11 | art_0XmNBGkzsJc_ | 3,680 | 3,680 | 3,680 | 0 | 0 | 0 | 8 |
| exp12 | art_kfCCWf7o8eJ9 | 9,199 | 9,912 | 9,912 | 0 | 0 | 0 | 96 |
| exp4 | art_m6pglf516e2r | 4,800 | 4,800 | 4,799 | 1 | 0 | 716 | 5 |

## What was dropped and why
- exp12: generation files hold more rows than were judged; only rows whose judge-cache key `sha256('qwen:V2|prompt|response|lang')` is present in `results/labels_qwen.jsonl` enter the table (the judged set is the panel's reported 9,199).
- Rows whose workhorse label failed to parse (judge_fail) stay in the table with `class_4way = null` and are excluded from every rate's denominator.
- Nothing else is dropped. INVALID is kept as its own class and never folded into COMPLIED.

## Dose axis
- `dose_logE = log1p(E)` where a closed-form removal energy is on disk (exp9 cells.csv `E`, exp10 meta `E_exact`, exp12 panel_info `energy`, exp11 `(f * ||Delta||_F)^2` from adapter_delta_norms.json).
- Where only a strength multiplier exists (exp12 calibration ladders), `2*log(strength)` is used as the E proxy.
- Activation arms use `log1p(n_layers covered)`.
- `dose_z` is z-scored WITHIN `dose_group = panel|operator` over cells. Raw doses are never pooled across panels.
- exp4 (orig vs edit only) carries no dose and is excluded from the curve fits.
