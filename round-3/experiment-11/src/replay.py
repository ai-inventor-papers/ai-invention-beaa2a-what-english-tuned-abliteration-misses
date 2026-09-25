#!/usr/bin/env python3
"""Replay iteration-1 Heretic trials through Heretic's OWN code path (Model.reset_model -> Model.abliterate ->
Evaluator.get_scores) with the study's stored settings, and record every in-loop response.

Used for
  * RUNG 4  exact-reproduction check (trial 96 must re-score to 69/100 keyword refusals, KL 0.0243);
  * STEP 2  in-loop certification generations (100 harmful_behaviors test[:100] prompts, 100 new tokens);
  * STEP 5  post-hoc reselection (score the SAME parameter draws under the corrected objective).

  python replay.py --trials 96,60,61,... --tag replay60 [--clf scorer/refusal_clf.joblib] [--kl-order-stop]

Scorers in the replay: KeywordRate (the iteration-1 objective), KLDivergence (unchanged), ResponseRecorder
(logs text), and - if --clf is given - PartialAwareRefusal (the corrected objective). All share one Context,
so one generation pass per trial feeds every scorer.
Output: results/replay/<tag>.jsonl (one row per trial) + logs/inloop_scores/<tag>/*.jsonl (per-response rows).
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

WS = Path(__file__).resolve().parent
RUN = Path(__file__).resolve().parents[3]
W1 = RUN / "round-1/experiment-1/src"
JOURNAL_SRC = W1 / "checkpoints/gemma/google--gemma-3-12b-it.jsonl"
MEANS_SRC = W1 / "directions/gemma/residual_means_A.pt"


def load_iter1_study() -> tuple[dict, dict]:
    """Returns (settings_json_dict, {trial_number: trial_record}) from a COPY of the iteration-1 journal."""
    import optuna
    from optuna.storages import JournalStorage
    from optuna.storages.journal import JournalFileBackend

    dst = WS / "inputs" / "iter1_journal_gemma.jsonl"
    dst.parent.mkdir(exist_ok=True)
    if not dst.exists():
        shutil.copy2(JOURNAL_SRC, dst)
    st = optuna.load_study(study_name="heretic", storage=JournalStorage(JournalFileBackend(str(dst))))
    settings = json.loads(st.user_attrs["settings"])
    trials = {}
    for t in st.trials:
        if t.state.name != "COMPLETE":
            continue
        trials[t.number] = {"number": t.number, "values": list(t.values), "params": dict(t.params),
                            "direction_index": t.user_attrs.get("direction_index"),
                            "parameters": t.user_attrs.get("parameters")}
    return settings, trials


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", default="", help="comma list of iteration-1 trial numbers, in replay order")
    ap.add_argument("--kl-order", action="store_true", help="replay ALL trials sorted by ascending iteration-1 KL")
    ap.add_argument("--kl-order-stop", action="store_true",
                    help="with --kl-order and --clf: stop at the first trial whose corrected count <= 10 (rule-1 winner)")
    ap.add_argument("--skip-done", action="store_true")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--clf", default="")
    ap.add_argument("--batch-size", type=int, default=0, help="0 = iteration-1 stored value")
    ap.add_argument("--deadline-epoch", type=float, default=float("inf"))
    args = ap.parse_args()
    sys.argv = [sys.argv[0]]  # Heretic's Settings parses the CLI; give it nothing.

    from loguru import logger
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    (WS / "logs").mkdir(exist_ok=True)
    logger.add(WS / "logs" / f"replay_{args.tag}.log", rotation="30 MB", level="DEBUG")

    import torch
    import torch.nn.functional as F
    from heretic.config import Settings
    from heretic.evaluator import Evaluator
    from heretic.model import AbliterationParameters, Model
    import heretic.scorers.partial_aware_refusal as par

    s_json, trials = load_iter1_study()
    logger.info(f"iteration-1 study: {len(trials)} complete trials; model {s_json['model']} @ {s_json.get('model_commit')}")
    log_dir = str(WS / "logs" / "inloop_scores" / args.tag)
    s_json["scorers"] = [
        {"plugin": "heretic.scorers.keyword_rate.KeywordRate", "optimization": "minimize"},
        {"plugin": "heretic.scorers.kl_divergence.KLDivergence", "optimization": "minimize"},
        {"plugin": "heretic.scorers.partial_aware_refusal.ResponseRecorder", "optimization": "none"},
    ]
    s_json["scorer"] = {"ResponseRecorder": {"log_dir": log_dir}}
    if args.clf:
        s_json["scorers"].append({"plugin": "heretic.scorers.partial_aware_refusal.PartialAwareRefusal",
                                  "optimization": "none"})
        s_json["scorer"]["PartialAwareRefusal"] = {"model_path": str(Path(args.clf).resolve()), "log_dir": log_dir}
    if args.batch_size:
        s_json["batch_size"] = args.batch_size
    settings = Settings.model_validate_json(json.dumps(s_json))
    logger.info(f"settings: quant={settings.quantization} batch={settings.batch_size} max_resp={settings.max_response_length} "
                f"seed={settings.seed} prefix={settings.response_prefix!r} rownorm={settings.row_normalization} "
                f"orth={settings.orthogonalize_direction}")

    t0 = time.time()
    model = Model(settings)
    logger.info(f"model loaded in {time.time() - t0:.0f}s")

    m = torch.load(MEANS_SRC, map_location="cpu")
    good_means, bad_means = m["means"][0].float(), m["means"][1].float()
    dirs = F.normalize(bad_means - good_means, p=2, dim=1)
    if settings.orthogonalize_direction:
        gd = F.normalize(good_means, p=2, dim=1)
        proj = torch.sum(dirs * gd, dim=1)
        dirs = F.normalize(dirs - proj.unsqueeze(1) * gd, p=2, dim=1)
    ref = W1 / "directions/gemma/directions.pt"
    if ref.exists():
        try:
            d2 = torch.load(ref, map_location="cpu")
            d2 = d2["directions"] if isinstance(d2, dict) and "directions" in d2 else d2
            if isinstance(d2, torch.Tensor):
                logger.info(f"directions vs iteration-1 directions.pt: max abs diff {float((d2.float() - dirs).abs().max()):.3e}")
        except Exception as e:  # noqa: BLE001 - diagnostic only
            logger.warning(f"could not compare with directions.pt: {e!r}")

    par.CURRENT_TRIAL.clear()
    par.CURRENT_TRIAL.update({"trial": -1, "tag": "baseline_orig"})
    ev = Evaluator(settings, model)  # baseline scores (orig model) are recorded by ResponseRecorder too
    logger.info("baseline: " + "; ".join(f"{n}={s.md_display}" for n, s in ev.baseline_scores))

    if args.kl_order:
        order = sorted(trials, key=lambda n: (trials[n]["values"][1], n))
    else:
        order = [int(x) for x in args.trials.split(",") if x.strip()]
    out = WS / "results" / "replay" / f"{args.tag}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if args.skip_done and out.exists():
        done = {json.loads(l)["trial"] for l in out.read_text().splitlines() if l.strip()}
    for n in order:
        if n in done:
            continue
        if time.time() > args.deadline_epoch:
            logger.warning(f"deadline reached before trial {n}")
            break
        tr = trials[n]
        params = {k: AbliterationParameters(**v) for k, v in tr["parameters"].items()}
        par.CURRENT_TRIAL.clear()
        par.CURRENT_TRIAL.update({"trial": n, "tag": args.tag})
        t1 = time.time()
        model.reset_model()
        model.abliterate(dirs, tr["direction_index"], params)
        scores = ev.get_scores()
        sc = {name: s.value for name, s in scores}
        row = {"trial": n, "iter1_keyword_refusals": round(tr["values"][0] * 100), "iter1_kl": tr["values"][1],
               "keyword_refusals": round(sc["Refusals"] * 100), "kl": sc["KL divergence"],
               "corrected_refusals": (round(sc["Refusals (partial-aware)"] * 100) if "Refusals (partial-aware)" in sc else None),
               "direction_scope": tr["params"]["direction_scope"], "wall_s": time.time() - t1,
               "peak_vram_gb": torch.cuda.max_memory_allocated() / 1e9}
        torch.cuda.reset_peak_memory_stats()
        with out.open("a") as f:
            f.write(json.dumps(row) + "\n")
        logger.info(f"trial {n}: kw {row['keyword_refusals']} (iter1 {row['iter1_keyword_refusals']}), KL {row['kl']:.5f} "
                    f"(iter1 {row['iter1_kl']:.5f}), corrected {row['corrected_refusals']}, {row['wall_s']:.1f}s")
        if args.kl_order_stop and row["corrected_refusals"] is not None and row["corrected_refusals"] <= 10:
            logger.info(f"RULE-1 WINNER under KL-order replay: trial {n} (all later trials have higher KL)")
            break
    logger.info("REPLAY_DONE")


if __name__ == "__main__":
    main()
