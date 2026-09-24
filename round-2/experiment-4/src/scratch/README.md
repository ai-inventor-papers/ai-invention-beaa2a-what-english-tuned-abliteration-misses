# scratch/

Small pre-check artefacts, kept because they document how the pipeline was verified before real labels existed.

- `dl.py` — the model download helper referenced by the root README ("Restoring removed files").
- `testjudge/` — SYNTHETIC labels (keyword-proxy derived, random classes) used once to exercise
  `analyze.py` → `audit.py` end-to-end while generation was still running. **Not results.**
- `test_analysis.json` — the analysis produced from those synthetic labels. **Not results.**

The real label files are `results/judge/` (gpt-4.1, 716 core items) and `results/judge_local/` (substitute judge,
all 4,800), and the real analysis is `results/analysis.json`.
