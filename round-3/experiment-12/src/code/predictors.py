#!/usr/bin/env python3
"""Turn every competing predictor into an actual out-of-sample PREDICTION for EVERY generation in the study, so the
methods can be compared head to head on identical rows.

THE TASK. For each generation, predict whether it was judged a refusal. A generation belongs to a group
(model, condition, role, language) - e.g. (gemma, conf_W3, harmful, sl). Every competing predictor supplies one frozen
DEV number per (model, language):

  depth_index        - our method: cumulative depth coverage needed to push DEV harmful refusal below 0.5
  depth_auc          - our method's pre-registered continuous secondary
  single_site        - refusal left by the single-site (Arditi) English ablation
  direction_cosine   - mean per-layer cos(d_EN(h), d_L(h))
  baseline_refusal   - the unedited model's judged refusal in that language
  first_token_margin - teacher-forced first-token refusal log-odds
  majority           - trivial control: no predictor at all, only the cell level

THE MODEL is a one-way fixed-effects (within) estimator:

    rate(model, cond, role, lang) = level(cond, role) + b * ( X(model, lang) - mean X in training )

`level(cond, role)` is the mean judged rate of that condition among the TRAINING rows and `b` is a single slope fitted
on training rows after centring the outcome within each (cond, role) group. This is the honest way to ask what these
per-language predictors can add: a no-op cell refuses far more than an edited one, so a predictor that only varies by
language cannot be blamed for the cell's own level, and must instead earn its keep on the cross-language variation
*inside* each cell. `majority` is the same model with b = 0, i.e. the cell level alone, so any predictor that fails to
beat `majority` has contributed nothing.

EVERYTHING IS LEAVE-ONE-MODEL-OUT: rows of model m are predicted only from the other models' rows, for both the level
and the slope, so no row is ever predicted by a fit that saw it. If a predictor has no variance among the training rows
(this is exactly what happens to depth_index, whose eligible qwen3 languages all share one value) the slope degenerates
to 0 and the predictor collapses onto `majority`; that is reported, not patched around.

Per item the predicted rate is thresholded at 0.5 into predict_<method> in {refused, not_refused}, and the rate itself
is kept in metadata_predicted_rate_<method>. All items of a group share its rate, because every one of these predictors
is constant within a group by construction.

Scored with accuracy / balanced accuracy / Brier overall, on the frozen active edited cells (the headline comparison),
and on eligible rows only. Output: results/predictions.json."""
from __future__ import annotations

import numpy as np
from loguru import logger

import common as C

PREDICTORS = {"depth_index": "index", "depth_auc": "auc", "single_site": "B_ss", "direction_cosine": "B_cos",
              "baseline_refusal": "B_base", "first_token_margin": "B_margin"}
ACTIVE = ["W1", "W2", "W3"]


def observed_groups(models: list[str], labels: dict, qkey) -> dict:
    """{(model, cond, role, lang): [0/1 refusal indicators]} over every judged generation of the study."""
    g: dict = {}
    for m in models:
        for p in sorted((C.RES / m / "gens").glob("*.jsonl")):
            for r in C.read_jsonl(p):
                if r["phase"] not in ("dev", "conf"):
                    continue
                lab = labels.get(qkey(r))
                if not lab or lab["four"] not in ("REFUSED", "PARTIAL", "COMPLIED"):
                    continue
                g.setdefault((r["model"], r["cond"], r["role"], r["lang"]), []).append(1.0 if lab["four"] == "REFUSED" else 0.0)
    return g


def main() -> None:
    C.setup_logging("predictors")
    frozen = C.jload(C.CFG / "frozen_predictions.json")
    table = frozen["per_model_lang"]
    models = frozen["models"]
    from judge_local import load_labels, qkey
    groups = observed_groups(models, load_labels(), qkey)
    rows = [{"m": m, "cond": c, "role": ro, "L": L, "y": float(np.mean(v)), "n": len(v),
             "key": f"{m}|{c}|{ro}|{L}", "cell": f"{c}|{ro}"} for (m, c, ro, L), v in sorted(groups.items())]
    logger.info(f"{len(rows)} (model, condition, role, language) groups over {sum(r['n'] for r in rows)} judged generations")
    out: dict = {"method": "leave-one-model-out one-way fixed-effects fit: rate = level(condition, role) + b * (X - mean X); "
                           "majority is the same model with b = 0 (cell level only)",
                 "n_groups": len(rows), "n_generations": sum(r["n"] for r in rows), "predictors": {}, "group_predictions": {}}

    def predict_for(col: str | None) -> tuple[dict, dict]:
        preds, fits = {}, {}
        for m in models:
            tr = [r for r in rows if r["m"] != m]
            lvl = {}
            for r in tr:
                lvl.setdefault(r["cell"], []).append(r["y"])
            lvl = {k: float(np.mean(v)) for k, v in lvl.items()}
            glob = float(np.mean([r["y"] for r in tr])) if tr else float("nan")
            b, xbar, degen = 0.0, 0.0, True
            if col is not None:
                xs, ys = [], []
                for r in tr:
                    x = table[f"{r['m']}|{r['L']}"][col]
                    if x is None or x != x:
                        continue
                    xs.append(x)
                    ys.append(r["y"] - lvl[r["cell"]])           # centre the outcome within its cell
                xs, ys = np.asarray(xs, float), np.asarray(ys, float)
                xbar = float(xs.mean()) if len(xs) else 0.0
                if len(xs) >= 2 and float(xs.std()) > 1e-12:
                    b = float(np.polyfit(xs - xbar, ys, 1)[0])
                    degen = False
            fits[m] = {"slope": b, "x_mean_train": xbar, "n_train_groups": len(tr),
                       "train_models": sorted({r["m"] for r in tr}), "degenerate_zero_variance": degen,
                       "n_cell_levels": len(lvl)}
            for r in (r for r in rows if r["m"] == m):
                x = table[f"{r['m']}|{r['L']}"][col] if col is not None else None
                base = lvl.get(r["cell"], glob)
                p = base + (b * (x - xbar) if (col is not None and x is not None and x == x) else 0.0)
                preds[r["key"]] = float(min(1.0, max(0.0, p)))
        return preds, fits

    for name, col in list(PREDICTORS.items()) + [("majority", None)]:
        preds, fits = predict_for(col)
        out["group_predictions"][name] = preds
        out["predictors"][name] = {"frozen_column": col, "fits": fits,
                                   "n_degenerate_fits": sum(f["degenerate_zero_variance"] for f in fits.values())}
    # ---------------- scoring
    scopes = {"all_rows": lambda r: True,
              "active_edited_cells_harmful": lambda r: r["cond"].replace("conf_", "") in ACTIVE and r["role"] == "harmful"
              and r["cond"].startswith("conf_"),
              "eligible_active_cells": lambda r: r["cond"].replace("conf_", "") in ACTIVE and r["role"] == "harmful"
              and r["cond"].startswith("conf_") and table[f"{r['m']}|{r['L']}"]["eligible"]}
    scores: dict = {}
    for name in out["group_predictions"]:
        for sc, keep in scopes.items():
            yt, yp = [], []
            for r in rows:
                if not keep(r):
                    continue
                p = out["group_predictions"][name][r["key"]]
                ys = groups[(r["m"], r["cond"], r["role"], r["L"])]
                yt += ys
                yp += [p] * len(ys)
            if not yt:
                continue
            yt_, yp_ = np.asarray(yt), np.asarray(yp)
            yh = (yp_ >= 0.5).astype(float)
            pos, neg = yt_ == 1, yt_ == 0
            scores.setdefault(name, {})[sc] = {
                "n_items": int(len(yt_)), "accuracy": float((yh == yt_).mean()),
                "balanced_accuracy": float(0.5 * ((yh[pos] == 1).mean() if pos.any() else 0.0)
                                           + 0.5 * ((yh[neg] == 0).mean() if neg.any() else 0.0)),
                "brier": float(np.mean((yp_ - yt_) ** 2))}
    out["scores"] = scores
    C.jdump(out, C.RES / "predictions.json")
    for name, s in scores.items():
        a, h = s.get("all_rows", {}), s.get("eligible_active_cells", {})
        logger.info(f"{name:19s} all: acc={a.get('accuracy', float('nan')):.3f} bal={a.get('balanced_accuracy', float('nan')):.3f} "
                    f"brier={a.get('brier', float('nan')):.3f} | eligible active: bal={h.get('balanced_accuracy', float('nan')):.3f} "
                    f"brier={h.get('brier', float('nan')):.3f} | degen={out['predictors'][name]['n_degenerate_fits']}/{len(models)}")


if __name__ == "__main__":
    main()
