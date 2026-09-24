#!/usr/bin/env python3
"""Independent re-derivation of the headline numbers from the RAW per-item files, through a different code path.

Nothing from analysis.py / audit.py is imported. Inputs: results/panel_items/*.parquet (per-item trait values),
results/baseline_items.parquet, results/judged_generations.json, results/validity_sids.json.
Own code for: trait aggregation (pandas groupby), Spearman-Brown ceilings, the learner (sklearn ExtraTrees, 10-fold CV;
plus a pure-numpy leave-one-out quadratic ridge), Spearman (rank + Pearson), Cohen's kappa (confusion matrix).

Each claim is also run on a placebo input on which it must FAIL:
  Gap_K >= 0.10    -> self-placebo (EN_B as 'SL') and a noise-matched placebo (EN_B + noise at SL reliability)
  TOST Gap_R       -> SL rows shuffled across edits (the 'visible' claim must break)
  validity rho     -> judged refusal rates shuffled across conditions
  judge kappa      -> local labels shuffled across rows

  uv run rederive_headlines.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.model_selection import KFold

ROOT = Path(__file__).resolve().parent
RES = ROOT / "results"
TRAITS = {"R": "R_seq", "R1": "R1", "Rb": "Rb_seq", "K": "KL"}  # the four reliable traits (N, M: F8 'no signal')


def load_panel() -> pd.DataFrame:
    parts = [pd.read_parquet(p) for p in sorted((RES / "panel_items").glob("*.parquet"))]
    d = pd.concat(parts, ignore_index=True)
    return d[d.trait.isin(TRAITS.values())]


def agg(d: pd.DataFrame, raw: str, by_sub: bool = False) -> pd.DataFrame:
    """Per edit x lang x half (x sub) mean; K = log(mean KL + 1e-6)."""
    keys = ["edit_id", "lang", "half"] + (["sub"] if by_sub else [])
    g = d[d.trait == raw].groupby(keys).value.mean()
    if raw == "KL":
        g = np.log(g.clip(lower=0) + 1e-6)
    return g


def sb_ceiling(sub: pd.Series, edits: list[str], lang: str, half: str) -> float:
    a = np.array([sub[(e, lang, half, 0)] for e in edits])
    b = np.array([sub[(e, lang, half, 1)] for e in edits])
    r = np.corrcoef(a, b)[0, 1]
    return 2 * r / (1 + r)


def r2_et(X: np.ndarray, y: np.ndarray, seed: int = 0) -> float:
    pred = np.zeros_like(y)
    for tr, te in KFold(10, shuffle=True, random_state=seed).split(X):
        m = ExtraTreesRegressor(n_estimators=300, min_samples_leaf=3, random_state=seed, n_jobs=4).fit(X[tr], y[tr])
        pred[te] = m.predict(X[te])
    return 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()


def r2_loo_quad_ridge(X: np.ndarray, y: np.ndarray, lam: float = 1.0) -> float:
    Z = (X - X.mean(0)) / X.std(0)
    iu = np.triu_indices(Z.shape[1])
    F = np.c_[np.ones(len(Z)), Z, (Z[:, :, None] * Z[:, None, :])[:, iu[0], iu[1]]]
    P = np.eye(F.shape[1]) * lam
    P[0, 0] = 0
    H = F @ np.linalg.solve(F.T @ F + P, F.T)
    res = (y - H @ y) / (1 - np.diag(H))  # exact LOO residuals of a linear smoother
    return 1 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum()


def gap(Xs: dict, target_en: dict, target_sl: dict, ceil: dict, learner) -> float:
    """Average of A->B and B->A: R2*(EN->EN) - R2*(EN->SL)."""
    out = []
    for hs, ht in (("A", "B"), ("B", "A")):
        pl = learner(Xs[hs], target_en[ht]) / ceil[("en", ht)]
        te = learner(Xs[hs], target_sl[ht]) / ceil[("sl", ht)]
        out.append((pl, te))
    pl, te = np.mean(out, 0)
    return float(pl - te), float(pl), float(te)


def spearman(a, b) -> float:
    ra, rb = pd.Series(a).rank().to_numpy(), pd.Series(b).rank().to_numpy()
    return float(np.corrcoef(ra, rb)[0, 1])


def kappa(a: list, b: list) -> float:
    labs = sorted(set(a) | set(b))
    ix = {l: i for i, l in enumerate(labs)}
    M = np.zeros((len(labs), len(labs)))
    for x, y in zip(a, b):
        M[ix[x], ix[y]] += 1
    n = M.sum()
    po = np.trace(M) / n
    pe = (M.sum(0) * M.sum(1)).sum() / n ** 2
    return float((po - pe) / (1 - pe))


def main() -> None:
    rng = np.random.default_rng(20260924)
    d = load_panel()
    edits = sorted(e for e in d.edit_id.unique() if e.startswith(("E0_", "E1_")))  # F: E0 + E1 (0 collapsed)
    d = d[d.edit_id.isin(edits)]
    A = {t: agg(d, raw) for t, raw in TRAITS.items()}
    S = {t: agg(d, raw, by_sub=True) for t, raw in TRAITS.items()}
    vec = lambda t, lang, half: np.array([A[t][(e, lang, half)] for e in edits])
    Xs = {h: np.c_[[vec(t, "en", h) for t in TRAITS]].T for h in ("A", "B")}
    out: dict = {"n_F": len(edits), "learners": "ExtraTrees(300, leaf 3, 10-fold) and numpy LOO quadratic ridge (lambda 1)",
                 "note": "predictors = EN R, R1, Rb, K of the source half (N, M omitted: F8 no-signal); primary analysis used all six + HistGBT"}
    for t in ("R", "K"):
        ceil = {(l, h): sb_ceiling(S[t], edits, l, h) for l in ("en", "sl") for h in ("A", "B")}
        ten = {h: vec(t, "en", h) for h in ("A", "B")}
        tsl = {h: vec(t, "sl", h) for h in ("A", "B")}
        res = {"ceilings": {f"{l}_{h}": c for (l, h), c in ceil.items()}}
        for nm, L in (("extratrees", r2_et), ("loo_quad_ridge", r2_loo_quad_ridge)):
            g, pl, te = gap(Xs, ten, tsl, ceil, L)
            res[nm] = {"Gap": g, "R2s_plac": pl, "R2s_test": te}
        # placebos
        ceil_self = dict(ceil) | {("sl", h): ceil[("en", h)] for h in ("A", "B")}
        g_self, _, _ = gap(Xs, ten, ten, ceil_self, r2_loo_quad_ridge)
        # noise-matched: EN_B + noise so that its split-half reliability matches SL's, ceiling from the implied reliability
        noisy, ceil_nm = {}, dict(ceil)
        for h in ("A", "B"):
            v = ten[h]
            rel_sl = ceil[("sl", h)]
            rel_en = ceil[("en", h)]
            extra = max(v.var() * (rel_en / rel_sl - 1), 0)
            noisy[h] = v + rng.normal(0, np.sqrt(extra), len(v))
            ceil_nm[("sl", h)] = rel_sl
        g_nm, _, _ = gap(Xs, ten, noisy, ceil_nm, r2_loo_quad_ridge)
        perm = {h: tsl[h][rng.permutation(len(edits))] for h in ("A", "B")}
        g_shuf, _, te_shuf = gap(Xs, ten, perm, ceil, r2_loo_quad_ridge)
        res["placebo_self_EN_as_SL_Gap"] = g_self
        res["placebo_noise_matched_Gap"] = g_nm
        res["placebo_shuffled_SL_Gap"] = g_shuf
        res["placebo_shuffled_SL_R2s_test"] = te_shuf
        out[t] = res
    out["K_claim_Gap_ge_0.10"] = {"real": [out["K"][k]["Gap"] >= 0.10 for k in ("extratrees", "loo_quad_ridge")],
                                  "self_placebo_passes": out["K"]["placebo_self_EN_as_SL_Gap"] >= 0.10,
                                  "noise_matched_placebo_passes": out["K"]["placebo_noise_matched_Gap"] >= 0.10}
    out["R_claim_visible_|Gap|<0.10"] = {"real": [abs(out["R"][k]["Gap"]) < 0.10 for k in ("extratrees", "loo_quad_ridge")],
                                         "shuffled_SL_placebo_passes": abs(out["R"]["placebo_shuffled_SL_Gap"]) < 0.10}
    # ---------------- validity gate from raw judge labels + raw R_seq
    J = pd.DataFrame(json.loads((RES / "judged_generations.json").read_text()))
    vs = set(json.loads((RES / "validity_sids.json").read_text()))
    base = pd.read_parquet(RES / "baseline_items.parquet")
    allp = pd.concat([pd.read_parquet(p) for p in (RES / "panel_items").glob("*.parquet")] + [base])
    rseq = allp[allp.trait == "R_seq"].set_index(["edit_id", "sid", "lang"]).value
    val = {}
    for lang in ("en", "sl"):
        rows = []
        for cnd, g in J[(J.lang == lang) & (J.kind == "jbb_harm") & J.sid.isin(vs)].groupby("edit_id"):
            if cnd == "core_stage0c":
                continue
            g = g[g.judge_label_final.isin(["refused", "complied", "partial", "irrelevant", "malformed", "empty"])]
            rows.append((np.mean([rseq[(cnd, s, lang)] for s in g.sid]), (g.judge_label_final == "refused").mean()))
        r = np.array(rows)
        null = [spearman(r[:, 0], rng.permutation(r[:, 1])) for _ in range(2000)]
        val[lang] = {"n_conditions": len(r), "spearman_Rseq_vs_refused": spearman(r[:, 0], r[:, 1]),
                     "placebo_shuffled_rates_mean_rho": float(np.mean(null)),
                     "placebo_share_rho_ge_0.85": float(np.mean(np.array(null) >= 0.85))}
    out["validity"] = val
    # ---------------- judge agreement
    both = J[(J.final_label_source == "gpt-4.1") & J.judge_local_label.notna()]
    a = (both.judge_label == "refused").tolist()
    b = (both.judge_local_label == "refused").tolist()
    kb = [kappa(a, list(rng.permutation(b))) for _ in range(500)]
    out["judge"] = {"n_overlap": len(both), "kappa_refused": kappa(a, b),
                    "kappa_6way": kappa(both.judge_label.tolist(), both.judge_local_label.tolist()),
                    "placebo_shuffled_kappa_mean": float(np.mean(kb)), "placebo_shuffled_kappa_max": float(np.max(kb))}
    (RES / "rederive_headlines.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
