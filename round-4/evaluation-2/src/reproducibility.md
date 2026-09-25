# Reproducibility

- Python 3.12, pinned environment in `requirements.lock` (uv). torch 2.11.0+cu128, transformers 5.17.0, bitsandbytes 0.50.2.
- Hardware used: 48 CPU cores, 251 GB RAM, NVIDIA RTX 2000 Ada 16 GB (the earlier part of the session ran on an RTX 4000 Ada 20 GB before a machine swap; only CPU phases and the purchase ran there).
- Frozen before any fit: `configs/FREEZE_iter4_eval.json` (sha256 in `configs/FREEZE.sha256`, together with `results/calibration_sample.json`). `p1_curves.py` refuses to run if the hash does not verify, and asserts that every result file it writes is newer than the freeze.
- Seeds: {"master": 20260924, "bootstrap_nonpar": 20260925, "bootstrap_po": 20260926, "permutation": 20260927, "calibration_sample": 20260924}; bootstrap B: {"nonparametric": 2000, "po_bootstrap": 400, "power_sim": 120, "c3iii_perm": 1000}.
- Judge: gpt-4.1 via OpenRouter, temperature 0, seed 0, max_tokens 60. The rubric is loaded verbatim from `round-2/experiment-4/src/protocol.yaml` (judge_primary), copy in `configs/frozen_rubric_exp4.json`. Blind: only request + response are sent. 512 + 160 labels bought, 0 blocked.
- Guards: Llama-Guard-3-8B@7327bd9f and PolyGuard-Qwen@644bfe73 in NF4 (the stored iteration-2 labels were bf16; fidelity is measured in `results/asr_summary.json`). Prompts and parsers come from `round-2/experiment-4/src/guard_pipeline.py` (constants parsed with ast, not retyped).
- Deviations from the plan, stated:
  1. The calibration frame is restricted to HARMFUL prompts.
  2. The gate uses both population-weighted and sample kappa (conservative).
  3. A declared post-freeze supplement was added for the exp11/exp12 panels.
  4. The guard subsample is 30 items per cell x language, not 100, and PolyGuard was time-capped.
  5. Guards ran in NF4.
  6. The PO bootstrap uses B=400 (the nonparametric B=2000).
  7. The LOESS span for L2 was chosen on L1, where all spans tie.
  8. The behavioural bf16 cell (one checkpoint, 20 verified pairs) is labelled by gpt-4.1 on BOTH sides, not by the workhorse, so the comparison is same-judge.
- Greedy decoding and NF4 numerics are not bit-reproducible across GPU models. The guard labels and activation-level KL can differ slightly on other hardware.
