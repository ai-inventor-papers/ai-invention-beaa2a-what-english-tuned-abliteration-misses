#!/usr/bin/env python3
"""T5 independent audit (plain numpy, no sklearn/analysis imports for the recomputation path):
aggregates and ceilings straight from the per-item parquet parts, Gap for R and K through a closed-form ridge learner
(second path), the reselection objective, and placebos (SL rows shuffled across edits -> R2_test ~ 0; self-placebo
EN_B as 'SL' -> Gap ~ 0).

  uv run audit.py
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from common import RES, jdump, jload, setup_logging


def agg_plain(V: np.ndarray, half: np.ndarray, h: str, lang: int, sub: np.ndarray | None = None, s: int | None = None) -> np.ndarray:
    cols = [i for i in range(V.shape[1]) if half[i] == h and (s is None or sub[i] == s)]
    return np.array([sum(V[e, i, lang] for i in cols) / len(cols) for e in range(V.shape[0])])


def ceil_plain(V, half, sub, h, lang) -> float:
    a = agg_plain(V, half, h, lang, sub, 0)
    b = agg_plain(V, half, h, lang, sub, 1)
    a, b = a - a.mean(), b - b.mean()
    r = float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum()))
    return 2 * r / (1 + r)


def ridge_cv_r2(X: np.ndarray, y: np.ndarray, alpha: float = 1.0, k: int = 5, seed: int = 0) -> float:
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(y))
    folds = np.array_split(idx, k)
    pred = np.zeros(len(y))
    for f in folds:
        tr = np.setdiff1d(idx, f)
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-12
        Z = (X[tr] - mu) / sd
        ym = y[tr].mean()
        beta = np.linalg.solve(Z.T @ Z + alpha * np.eye(Z.shape[1]), Z.T @ (y[tr] - ym))
        pred[f] = ((X[f] - mu) / sd) @ beta + ym
    return float(1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum())


def main() -> None:
    setup_logging("audit")
    import analysis as AN  # only to load the panel structure identically; recomputation below is plain numpy

    p, _ = AN.build_panel()
    ed = p.edits
    F = np.where(ed.set.isin(["E0", "E1"]).values & ~ed.collapsed.values.astype(bool))[0]
    res = jload(RES / "analysis_results.json")
    out = {"n_F": int(len(F)), "checks": []}
    # raw parquet -> aggregates (independent of TraitMat building): R_seq EN half B for 5 random edits
    items = {it["sid"]: it for it in jload(RES.parent / "data" / "s3_items.json")["items"] if it["kind"] == "jbb_harm"}
    for e in ed.edit_id.values[F][:5]:
        d = pd.read_parquet(RES / "panel_items" / f"{e}.parquet")
        v = d[(d.trait == "R_seq") & (d.lang == "en") & (d.kind == "jbb_harm")]
        vb = v[v.sid.map(lambda s: items[s]["half"] == "B")]
        i = int(np.where(ed.edit_id.values == e)[0][0])
        a2 = AN.aggregate(p.traits["R"], np.ones(len(p.traits["R"].sid)), "B", 0, None, np.array([i]))[0]
        out["checks"].append({"what": f"R_seq EN_B mean {e}", "plain": float(vb.value.mean()), "analysis": float(a2),
                              "match": abs(float(vb.value.mean()) - float(a2)) < 1e-6})
    # ceilings
    for t in ("R", "K", "N", "M"):
        tm = p.traits[t]
        V = tm.vals[F]
        if tm.agg == "logmean":
            continue
        for li, l in enumerate(("en", "sl")):
            c = ceil_plain(V, tm.half, tm.sub, "B", li)
            out["checks"].append({"what": f"ceiling {t}_{l}_B", "plain": c, "analysis": res["reliability"][f"{t}_{l}_B"],
                                  "match": abs(c - res["reliability"][f"{t}_{l}_B"]) < 1e-6})
    # Gap via closed-form ridge (second learner path) for R and K
    for t in ("R", "K"):
        tm = p.traits[t]
        X = np.stack([np.log(np.clip(agg_plain(p.traits[s].vals[F], p.traits[s].half, "A", 0), 0, None) + 1e-6)
                      if p.traits[s].agg == "logmean" else agg_plain(p.traits[s].vals[F], p.traits[s].half, "A", 0) for s in AN.TRAITS], 1)
        tr = (lambda v: np.log(np.clip(v, 0, None) + 1e-6)) if tm.agg == "logmean" else (lambda v: v)
        yen = tr(agg_plain(tm.vals[F], tm.half, "B", 0))
        ysl = tr(agg_plain(tm.vals[F], tm.half, "B", 1))
        cen = AN.reliability(tm, np.ones(len(tm.sid)), "B", 0, F)
        csl = AN.reliability(tm, np.ones(len(tm.sid)), "B", 1, F)
        r_pl = np.mean([ridge_cv_r2(X, yen, seed=s) for s in range(5)])
        r_te = np.mean([ridge_cv_r2(X, ysl, seed=s) for s in range(5)])
        g = r_pl / cen - r_te / csl
        rng = np.random.default_rng(0)
        r_shuf = np.mean([ridge_cv_r2(X, rng.permutation(ysl), seed=s) for s in range(5)])
        g_self = r_pl / cen - np.mean([ridge_cv_r2(X, yen, seed=s + 10) for s in range(5)]) / cen
        se = res["bootstrap"][t]["gap_se"]
        out["checks"].append({"what": f"Gap_{t} closed-form ridge (A->B)", "ridge_gap": float(g), "primary_gap": res["gap"][t]["Gap"],
                              "bootstrap_se": se, "within_2se": bool(abs(g - res["gap"][t]["Gap"]) <= 2 * se),
                              "placebo_shuffled_SL_R2": float(r_shuf), "placebo_shuffled_ok": bool(r_shuf < 0.1),
                              "self_placebo_gap": float(g_self), "self_placebo_ok": bool(abs(g_self) < 0.05)})
    # reselection objective recompute
    rs = res.get("reselection", {})
    if rs.get("pareto_points"):
        pts = rs["pareto_points"]
        obj = np.array([max(x["EN"], x["SL_est"]) for x in pts])
        kl = np.array([x["KL"] for x in pts])
        ok = np.where(obj <= 10)[0]
        if len(ok):
            sel = ok[np.argmin(kl[ok])]
        else:
            ok = np.where(kl <= 1)[0]
            m = obj[ok].min()
            c = ok[obj[ok] == m]
            sel = c[np.argmin(kl[c])]
        out["checks"].append({"what": "reselection", "plain": pts[sel]["edit_id"], "analysis": rs["selected_edit"],
                              "match": pts[sel]["edit_id"] == rs["selected_edit"]})
    out["n_checks"] = len(out["checks"])
    out["n_fail"] = sum(1 for c in out["checks"] if not all(v for k, v in c.items() if k in ("match", "placebo_shuffled_ok", "self_placebo_ok")))
    jdump(out, RES / "audit.json")
    print(json.dumps({"n_checks": out["n_checks"], "n_fail": out["n_fail"]}))


if __name__ == "__main__":
    main()
