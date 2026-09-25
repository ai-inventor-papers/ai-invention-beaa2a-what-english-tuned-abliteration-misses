#!/usr/bin/env python3
"""C3 - a partial-aware refusal objective for Heretic abliteration: end-to-end driver.

METHOD   : Heretic 3521f864 with objective 1 = PartialAwareRefusal (a frozen, judge-distilled classifier that scores
           PARTIAL, caveat-laden compliance as compliance) + the unchanged KL objective, frozen selection rule.
BASELINE : the identical Heretic run with objective 1 = KeywordRate (33 substrings) - iteration 1's trial 96, plus the
           seed-free POST-HOC RESELECTION of the same 116 parameter draws, a MATCHED-EFFICACY DOSE LADDER on trial 96,
           and the no-op original. All arms are generated from one NF4 base load and scored by the same blinded judge.

Stages (each idempotent / resumable; run in this order, GPU stages strictly one at a time):
  coverage       coverage.py                          zero-GPU coverage descriptors of all 116 draws + community edit
  pool           build_pool.py                        harvest prior judge labels -> results/label_pool.parquet
  clf_base       train_clf.py base                    distilled classifier (pool only)
  replay         replay.py --trials 96,60..115        GPU: re-score iteration-1 TPE draws in Heretic's own loop
  judge_inloop   inloop.py collect/judge_input + judges.py local       Qwen3-14B labels of in-loop responses
  refit          inloop.py refit_table + train_clf.py refit            the ONE permitted refit
  certify        inloop.py certify                    kappa gate on held-out in-loop trials
  test_scorer    tests/test_scorer.py                 plugin == frozen classifier; keyword replica == Heretic
  corrected      chain3.sh                            GPU: corrected-objective Heretic run (60 + 56 trials)
  judge_corr     inloop.py judge_input --select corrected + judges.py local
  inloop_an      analyze_inloop.py                    miscalibration table, reselection, corrected selection
  arms           make_arms.py + freeze_predictions.py arms.json + hashed predictions (BEFORE any eval generation)
  evalgen        eval_gen.py --arms arms.json         GPU: S5X / S4hoc / S6 / FLORES for every arm
  judge_eval     judges.py local (+ guard.py polyguard/llamaguard)     labels for every eval generation
  autoscore      autoscore.py                         GlotLID language consistency, rep4, empty, keyword
  eval_an        analyze_eval.py + verdicts.py        statistics, headline table, prediction verdicts
  audit          audit_headline.py + verify_numbers.py                independent re-derivation + placebos
  extras         kl_arms / selection_point_cert / guard_analysis / judge_ceiling   per-arm KL, selection-point
                 certification, official-pipeline ASR, inter-judge ceilings
  seed2          chain7.sh + seed2.py                 the second optimiser seed (cut_2, executed)
  figures        figures.py
  schema         to_schema.py                         method_out.json (exp_gen_sol_out)

  uv run method.py --stages coverage,pool,clf_base            (or --stages all)
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from loguru import logger

WS = Path(__file__).resolve().parent
PY = str(WS / ".venv/bin/python")
STAGES: dict[str, list[list[str]]] = {
    "coverage": [[PY, "coverage.py"]],
    "pool": [[PY, "build_pool.py"]],
    "clf_base": [[PY, "train_clf.py", "base"], ["cp", "scorer/refusal_clf.joblib", "scorer/refusal_clf_base.joblib"]],
    "replay": [[PY, "replay.py", "--tag", "tpe60_115", "--skip-done",
                "--trials", "96," + ",".join(str(i) for i in range(60, 116) if i != 96)]],
    "judge_inloop": [[PY, "inloop.py", "collect"],
                     [PY, "inloop.py", "judge_input", "--select", "cert", "--out", "results/judge_in/inloop_certset.jsonl"],
                     [PY, "inloop.py", "judge_input", "--tags", "tpe60_115", "--out", "results/judge_in/inloop_replay_all.jsonl"],
                     [PY, "judges.py", "local", "--inp", "results/judge_in/inloop_certset.jsonl", "--out", "results/judge_out/inloop_qwen.jsonl"],
                     [PY, "inloop.py", "certify", "--bundle", "scorer/refusal_clf_base.joblib", "--out", "scorer/certification_base.json"],
                     [PY, "judges.py", "local", "--inp", "results/judge_in/inloop_replay_all.jsonl", "--out", "results/judge_out/inloop_qwen.jsonl"]],
    "refit": [[PY, "inloop.py", "refit_table", "--qwen", "results/judge_out/inloop_qwen.jsonl", "--out", "results/judge_in/inloop_refit_rows.jsonl"],
              [PY, "train_clf.py", "refit", "--inloop", "results/judge_in/inloop_refit_rows.jsonl"]],
    "certify": [[PY, "inloop.py", "certify", "--out", "scorer/certification.json"]],
    "test_scorer": [[PY, "tests/test_scorer.py"]],
    "corrected": [["bash", "chain3.sh"]],
    "judge_corr": [[PY, "inloop.py", "collect"],
                   [PY, "inloop.py", "judge_input", "--select", "corrected", "--out", "results/judge_in/inloop_corrected.jsonl"],
                   [PY, "judges.py", "local", "--inp", "results/judge_in/inloop_corrected.jsonl", "--out", "results/judge_out/inloop_qwen.jsonl"]],
    "inloop_an": [[PY, "analyze_inloop.py"]],
    "arms": [[PY, "make_arms.py"], [PY, "freeze_predictions.py"]],
    "evalgen": [[PY, "eval_gen.py", "--arms", "arms.json"]],
    "judge_eval": [[PY, "eval_judge_input.py"],
                   [PY, "judges.py", "local", "--inp", "results/judge_in/eval_all.jsonl", "--out", "results/judge_out/eval_qwen.jsonl"],
                   [PY, "guard.py", "polyguard", "--inp", "results/judge_in/eval_all.jsonl", "--out", "results/judge_out/eval_polyguard.jsonl"],
                   [PY, "guard.py", "llamaguard", "--inp", "results/judge_in/eval_harmful.jsonl", "--out", "results/judge_out/eval_llamaguard.jsonl"]],
    "autoscore": [[PY, "autoscore.py"]],
    "eval_an": [[PY, "analyze_eval.py"], [PY, "verdicts.py"]],
    "audit": [[PY, "audit_headline.py"], [PY, "audit_extra.py"], [PY, "verify_numbers.py"]],
    "extras": [[PY, "kl_arms.py"], [PY, "selection_point_cert.py"], [PY, "guard_analysis.py"], [PY, "judge_ceiling.py"]],
    "seed2": [["bash", "chain7.sh"], [PY, "seed2.py"]],
    "figures": [[PY, "figures.py"]],
    "schema": [[PY, "to_schema.py"]],
}


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stages", default="all")
    a = ap.parse_args()
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    logger.add(WS / "logs/method.log", rotation="30 MB", level="DEBUG")
    stages = list(STAGES) if a.stages == "all" else a.stages.split(",")
    for s in stages:
        for cmd in STAGES[s]:
            t0 = time.time()
            logger.info(f"[{s}] {' '.join(cmd)}")
            r = subprocess.run(cmd, cwd=WS)
            if r.returncode != 0:
                logger.error(f"[{s}] failed with exit code {r.returncode}")
                raise SystemExit(r.returncode)
            logger.info(f"[{s}] done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
