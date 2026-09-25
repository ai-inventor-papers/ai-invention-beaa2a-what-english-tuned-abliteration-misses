#!/usr/bin/env python3
"""Can an optimiser see its own refusals? The GRADIENT-BLIND FRACTION of Heretic's keyword objective, measured
on a SECOND search (cjvt/GaMS3-12B-Instruct) against the first (google/gemma-3-12b-it). Replay-only.

METHOD    : the certified partial-aware classifier C (art_0XmNBGkzsJc_, frozen bundle, threshold 0.52) as the
            reference scorer over every in-loop response of every candidate of both searches, plus the frozen
            4-way judge rubric (Qwen3-14B workhorse, gpt-4.1 bought certification) on 20 certification trials;
            the gradient-blind fraction GBF (definitions frozen in configs/frozen_predictions.json).
BASELINE  : the incumbent objective itself - Heretic's own KeywordRate (imported, not reimplemented) - at its
            shipped rule, at an oracle marker-count threshold chosen in hindsight, and with a repaired marker list;
            and the unedited model on the same 100 prompts.
NOT DONE  : no new optimiser search; no new edited checkpoint selected, exported or recommended (P7 stands).

Stages (each resumable; GPU stages strictly one at a time):
  s0     env.json + T0 instrument identity (score.py t0)
  s1     journals.py                      both journals parsed two ways; GATE G1 (paired startup draws)
  t2     score.py gemma + descriptors.py + tests/test_gbf.py + analysis.py --rehearsal   (Gemma dress rehearsal)
  s2     freeze.py                        *** FREEZE *** (before any GaMS3 generation)
  s3     replay_gams.py --tag probe --trials 0,59,88  + GATE G2 (replay fidelity)
  s4     replay_gams.py --tag main --tiers --skip-done  + collect.py
  s4a    judges.py build J1 + judges.py local (Qwen3-14B workhorse)
  s4b    judges.py gpt_sample + gpt_buy   (bought gpt-4.1 certification subsample; <= $3)
  s5     score.py gams + certify.py       (both gates written BEFORE any GaMS3 GBF)
  s4j2   judges.py build J2 + local       (EXTENSION: remaining startup draws, time permitting) + score.py gams
  s6     analysis.py                      GBF, CIs, placebos, best shot, anchors, reselection (S7)
  s8     rederive.py + checks.py          independent second code path + audit
  s9     figures.py + to_schema.py        figures and method_out.json

  uv run method.py --stages s0,s1,t2,s2,s3      (or --stages all)
"""
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

from loguru import logger

WS = Path(__file__).resolve().parent
PY = str(WS / ".venv/bin/python")

STAGES: dict[str, list[list[str]]] = {
    "s0": [[PY, "method.py", "--env-only"], [PY, "score.py", "t0"]],
    "s1": [[PY, "journals.py"]],
    "t2": [[PY, "score.py", "gemma"], [PY, "descriptors.py"], [PY, "tests/test_gbf.py"], [PY, "analysis.py", "--rehearsal"]],
    "s2": [[PY, "freeze.py"]],
    "s3": [[PY, "replay_gams.py", "--tag", "probe", "--trials", "0,59,88"], [PY, "method.py", "--g2-only"]],
    "s4": [[PY, "replay_gams.py", "--tag", "main", "--tiers", "--skip-done"], [PY, "collect.py"]],
    "s4a": [[PY, "judges.py", "build", "--tier", "J1"],
            [PY, "judges.py", "local", "--inp", "results/judge_in/gams_J1.jsonl", "--out", "results/judge_out/gams_inloop_qwen.jsonl"]],
    "s4b": [[PY, "judges.py", "gpt_sample"], [PY, "judges.py", "gpt_buy"]],
    "s5": [[PY, "score.py", "gams"], [PY, "certify.py"]],
    "s4j2": [[PY, "judges.py", "build", "--tier", "J2"],
             [PY, "judges.py", "local", "--inp", "results/judge_in/gams_J2.jsonl", "--out", "results/judge_out/gams_inloop_qwen.jsonl"],
             [PY, "score.py", "gams"]],
    "s6": [[PY, "analysis.py"]],
    "s8": [[PY, "rederive.py"], [PY, "checks.py"]],
    "s9": [[PY, "figures.py"], [PY, "to_schema.py"]],
}
ORDER = ["s0", "s1", "t2", "s2", "s3", "s4", "s4a", "s4b", "s5", "s4j2", "s6", "s8", "s9"]


def env_json() -> None:
    import torch
    import sklearn
    import transformers
    from common import CLF_PATH, sha256_file
    cg = {}
    for p in ("/sys/fs/cgroup/memory.max", "/sys/fs/cgroup/cpu.max"):
        try:
            cg[p] = Path(p).read_text().strip()
        except OSError:
            cg[p] = None
    info = {"python": platform.python_version(), "torch": torch.__version__, "transformers": transformers.__version__,
            "sklearn": sklearn.__version__, "cuda": torch.version.cuda,
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "vram_gb": torch.cuda.get_device_properties(0).total_memory / 1e9 if torch.cuda.is_available() else 0,
            "cgroup": cg, "clf_sha256": sha256_file(CLF_PATH), "t": time.time()}
    (WS / "results").mkdir(exist_ok=True)
    (WS / "results/env.json").write_text(json.dumps(info, indent=1))
    logger.info(f"env: {info}")


def g2() -> None:
    """GATE G2 - replay fidelity on the 3 probe trials (0 startup, 59 boundary, 88 = iteration-1 selected)."""
    rows = [json.loads(l) for l in (WS / "results/replay/gams_trials.jsonl").read_text().splitlines() if l.strip()]
    probe = [r for r in rows if r["tag"] == "probe"]
    d = [abs(r["keyword_refusals"] - r["journal_keyword_refusals"]) for r in probe]
    mean = sum(d) / len(d)
    if all(x <= 2 for x in d):
        verdict = "PASS"
    elif mean <= 8:
        verdict = "PASS_WITH_CAVEAT (drift added to sigma_K as an upper-bound variant)"
    else:
        verdict = "NO-GO -> fallback F2"
    wall = [r["wall_s"] for r in probe]
    res = {"trials": [r["trial"] for r in probe], "abs_diffs": d, "mean_abs_diff": mean, "verdict": verdict,
           "kl_replay_vs_journal": [[r["kl"], r["journal_kl"]] for r in probe], "wall_s": wall,
           "extrapolated_116_trials_h": 116 * sum(wall) / len(wall) / 3600, "gpu": probe[0]["gpu"] if probe else None}
    (WS / "results/replay_fidelity_s3.json").write_text(json.dumps(res, indent=1))
    logger.info(f"G2: {res}")


def run(cmd: list[str]) -> None:
    logger.info(f"$ {' '.join(cmd)}")
    t0 = time.time()
    r = subprocess.run(cmd, cwd=WS)
    logger.info(f"exit {r.returncode} after {time.time() - t0:.0f}s")
    if r.returncode != 0:
        raise SystemExit(f"stage command failed: {' '.join(cmd)}")


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stages", default="")
    ap.add_argument("--env-only", action="store_true")
    ap.add_argument("--g2-only", action="store_true")
    ap.add_argument("--force", action="store_true", help="re-run stages that already wrote results/<stage>.done.json")
    a = ap.parse_args()
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    (WS / "logs").mkdir(exist_ok=True)
    logger.add(WS / "logs/method.log", rotation="30 MB", level="DEBUG")
    if a.env_only:
        env_json()
        return
    if a.g2_only:
        g2()
        return
    stages = ORDER if a.stages in ("", "all") else a.stages.split(",")
    for s in stages:
        done = WS / f"results/{s}.done.json"
        if done.exists() and not a.force:
            logger.info(f"stage {s}: already done ({done.name}); skip (use --force to redo)")
            continue
        for cmd in STAGES[s]:
            run(cmd)
        done.write_text(json.dumps({"stage": s, "t": time.time()}))


if __name__ == "__main__":
    main()
