#!/usr/bin/env python3
"""STAGES S3/S4 - replay the SECOND search (cjvt/GaMS3-12B-Instruct, iteration-1 journal, 116 trials) through
Heretic's OWN code path (Model.reset_model -> Model.abliterate -> Evaluator.get_scores) with the journal's stored
settings, recording every in-loop response. Adapted from art_0XmNBGkzsJc_/replay.py (the Gemma replay), with the
model, journal and residual means switched to GaMS3; nothing else changed.

Scorers in the replay: KeywordRate (the iteration-1 objective, Heretic's own class), KLDivergence (unchanged),
ResponseRecorder (optimisation 'none'; logs every (prompt, response) with the keyword verdict).
The unedited-model baseline responses are recorded once per process (trial = -1).

  python replay_gams.py --tag probe --trials 0,59,88              (S3 fidelity probe, gate G2)
  python replay_gams.py --tag main --tiers --skip-done             (S4, pre-registered tier order from the freeze)

Outputs: results/replay/gams_trials.jsonl (one row per trial), logs/inloop_scores/<tag>/rec_*.jsonl (per response).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

WS = Path(__file__).resolve().parent
sys.path.insert(0, str(WS))
from common import A1, CONFIGS, J_GAMS, RESULTS, read_jsonl  # noqa: E402

MEANS_SRC = A1 / "directions/gams/residual_means_A.pt"
MEANS_SRC_B = A1 / "directions/gams/residual_means_B.pt"
DIRS_REF = A1 / "directions/gams/directions.pt"


def load_study() -> tuple[dict, dict]:
    import optuna
    from optuna.storages import JournalStorage
    from optuna.storages.journal import JournalFileBackend

    dst = WS / "inputs" / "iter1_journal_gams.jsonl"
    dst.parent.mkdir(exist_ok=True)
    if not dst.exists():
        shutil.copy2(J_GAMS, dst)
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
    ap.add_argument("--trials", default="")
    ap.add_argument("--tiers", action="store_true", help="use the tier order frozen in configs/frozen_predictions.json")
    ap.add_argument("--skip-done", action="store_true")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--batch-size", type=int, default=0, help="0 = journal value (128)")
    ap.add_argument("--deadline-epoch", type=float, default=float("inf"))
    args = ap.parse_args()
    sys.argv = [sys.argv[0]]  # Heretic's Settings parses the CLI; give it nothing.

    from loguru import logger
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    (WS / "logs").mkdir(exist_ok=True)
    logger.add(WS / "logs" / f"replay_gams_{args.tag}.log", rotation="30 MB", level="DEBUG")

    # FREEZE-ORDER GUARD: no GaMS3 generation before the hashed freeze exists and verifies.
    fz, fh = CONFIGS / "frozen_predictions.json", CONFIGS / "FREEZE.sha256"
    import hashlib
    if not (fz.exists() and fh.exists()):
        raise SystemExit("freeze missing: run stage s2 before any GaMS3 generation")
    if hashlib.sha256(fz.read_bytes()).hexdigest() != fh.read_text().split()[0]:
        raise SystemExit("freeze hash mismatch")
    frozen = json.loads(fz.read_text())

    # memory caps (aii-use-hardware): raise instead of being OOM-killed
    import resource
    import torch
    import torch.nn.functional as F
    resource.setrlimit(resource.RLIMIT_AS, (200 * 1024 ** 3, 200 * 1024 ** 3))
    torch.cuda.set_per_process_memory_fraction(0.95)

    from heretic.config import Settings
    from heretic.evaluator import Evaluator
    from heretic.model import AbliterationParameters, Model
    import heretic.scorers.partial_aware_refusal as par

    s_json, trials = load_study()
    logger.info(f"iteration-1 GaMS3 study: {len(trials)} complete trials; model {s_json['model']} @ {s_json.get('model_commit')}")
    log_dir = str(WS / "logs" / "inloop_scores" / args.tag)
    s_json["scorers"] = [
        {"plugin": "heretic.scorers.keyword_rate.KeywordRate", "optimization": "minimize"},
        {"plugin": "heretic.scorers.kl_divergence.KLDivergence", "optimization": "minimize"},
        {"plugin": "heretic.scorers.partial_aware_refusal.ResponseRecorder", "optimization": "none"},
    ]
    s_json["scorer"] = {"ResponseRecorder": {"log_dir": log_dir}}
    if args.batch_size:
        s_json["batch_size"] = args.batch_size
    settings = Settings.model_validate_json(json.dumps(s_json))
    logger.info(f"settings: quant={settings.quantization} batch={settings.batch_size} max_resp={settings.max_response_length} "
                f"seed={settings.seed} prefix={settings.response_prefix!r} rownorm={settings.row_normalization} "
                f"orth={settings.orthogonalize_direction} sys={settings.system_prompt!r}")

    t0 = time.time()
    model = Model(settings)
    logger.info(f"model loaded in {time.time() - t0:.0f}s")

    m = torch.load(MEANS_SRC, map_location="cpu")
    good_means, bad_means = m["means"][0].float(), m["means"][1].float()
    try:
        mb = torch.load(MEANS_SRC_B, map_location="cpu")
        logger.info(f"residual means A vs B (phase-B process): max abs diff "
                    f"{max(float((mb['means'][k].float() - m['means'][k].float()).abs().max()) for k in (0, 1)):.3e}")
    except (FileNotFoundError, KeyError, RuntimeError) as e:
        logger.warning(f"means B not comparable: {e!r}")
    dirs = F.normalize(bad_means - good_means, p=2, dim=1)
    if settings.orthogonalize_direction:
        gd = F.normalize(good_means, p=2, dim=1)
        proj = torch.sum(dirs * gd, dim=1)
        dirs = F.normalize(dirs - proj.unsqueeze(1) * gd, p=2, dim=1)
    if DIRS_REF.exists():
        try:
            d2 = torch.load(DIRS_REF, map_location="cpu")
            d2 = d2["directions"] if isinstance(d2, dict) and "directions" in d2 else d2
            if isinstance(d2, torch.Tensor):
                logger.info(f"directions vs iteration-1 directions.pt: max abs diff {float((d2.float() - dirs).abs().max()):.3e}")
        except (RuntimeError, KeyError) as e:
            logger.warning(f"could not compare with directions.pt: {e!r}")

    par.CURRENT_TRIAL.clear()
    par.CURRENT_TRIAL.update({"trial": -1, "tag": f"{args.tag}:baseline_orig"})
    ev = Evaluator(settings, model)  # baseline (unedited) responses are recorded by ResponseRecorder
    logger.info("baseline: " + "; ".join(f"{n}={s.md_display}" for n, s in ev.baseline_scores))

    if args.tiers:
        order = [t for tier in frozen["replay_tiers"]["order"] for t in tier["trials"]]
    else:
        order = [int(x) for x in args.trials.split(",") if x.strip()]
    out = RESULTS / "replay" / "gams_trials.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if args.skip_done:
        done = {r["trial"] for r in read_jsonl(out)}
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
        row = {"trial": n, "tag": args.tag, "journal_keyword_refusals": round(tr["values"][0] * 100),
               "journal_kl": tr["values"][1], "keyword_refusals": round(sc["Refusals"] * 100),
               "kl": sc["KL divergence"], "direction_scope": tr["params"]["direction_scope"],
               "wall_s": time.time() - t1, "peak_vram_gb": torch.cuda.max_memory_allocated() / 1e9,
               "gpu": torch.cuda.get_device_name(0), "batch_size": settings.batch_size, "t_end": time.time()}
        torch.cuda.reset_peak_memory_stats()
        with out.open("a") as f:
            f.write(json.dumps(row) + "\n")
        done.add(n)
        logger.info(f"trial {n}: kw {row['keyword_refusals']} (journal {row['journal_keyword_refusals']}), KL {row['kl']:.5f} "
                    f"(journal {row['journal_kl']:.5f}), {row['wall_s']:.1f}s")
    logger.info("REPLAY_DONE")


if __name__ == "__main__":
    main()
