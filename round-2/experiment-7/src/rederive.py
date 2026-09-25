#!/usr/bin/env python3
"""Independent re-derivation of the headline numbers (TODO 5), from RAW files only:
results/panel/edits/*.json (per-edit item deltas vs the cached original), the frozen S3 split JSONL (halves/roles),
and results/validity/judged.json (raw local-judge labels). No import of analysis.py / gapcore.py / common.py, and no
reading of analysis.json or the parquet tables. Different code paths: own zero-point matching, closed-form slopes,
pandas rank correlation, and a polynomial-OLS CV learner (instead of HistGradientBoosting) for the Gap.
Placebos: per-edit EN/SL label swap (Gap must centre on 0) and permuted edit order (R2 must be <= ~0).
  uv run python rederive.py  -> results/rederive.json"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

WS = Path(__file__).resolve().parent
SPL = Path(__file__).resolve().parents[3] / "round-1/dataset-1/src/data/splits"


def load_meta() -> dict:
    meta = {}
    for fam in ("S3_jbb", "S3_dolly", "S3_flores_dev", "S3_mc"):
        for line in (SPL / f"{fam}.jsonl").read_text().splitlines():
            r = json.loads(line)
            meta[(r["metadata_semantic_id"], r["metadata_lang"])] = r["metadata_half"]
    return meta


def main() -> None:
    meta = load_meta()
    raw = [json.loads(p.read_text()) for p in sorted((WS / "results" / "panel" / "edits").glob("*.json"))]
    origs = [r for r in raw if r["set"] == "ORIG"]
    edits = [r for r in raw if r["set"] in ("E0", "E1", "E_TPE")]
    # own zero point: ORIG row with identical trim dict and device string
    for e in edits:
        z = [o for o in origs if o["device"] == e["device"] and json.dumps(o["trim"], sort_keys=True) == json.dumps(e["trim"], sort_keys=True)]
        assert z, e["edit_id"]
        zo = z[-1]["items"]
        e["_d"] = {t: {k: v - zo[t].get(k, 0.0) for k, v in d.items()} for t, d in e["items"].items()}
    fit = [e for e in edits if e["set"] in ("E0", "E1") and not e["collapsed"]]
    out = {"n_fitted_noncollapsed": len(fit), "n_by_set": pd.Series([e["set"] for e in edits]).value_counts().to_dict()}

    def common_keys(trait, role, lang, half):
        ks = None
        for e in edits:
            s = {k for k in e["_d"][trait] if k.split("|")[1:] == [role, lang] and meta[(k.split("|")[0], lang)] == half}
            ks = s if ks is None else ks & s
        return sorted(ks)

    def lvl(es, trait, role, lang, half):
        ks = common_keys(trait, role, lang, half)
        M = np.array([[e["_d"][trait][k] for k in ks] for e in es])
        return M

    def agg(M, trait):
        return np.log(np.maximum(M.mean(1), 1e-4)) if trait == "K" else M.mean(1)
    roles = {"R1": "harmful", "R_seq": "harmful", "Rb": "harmless", "K": "harmless", "N": "parallel", "M": "mc"}
    tk = {"Rb": "R_seq"}
    # ---- transfer slopes (closed-form cov/var), half B, fitted edits
    TS = {}
    for t in ("R1", "R_seq", "Rb"):
        x = agg(lvl(fit, tk.get(t, t), roles[t], "en", "B"), t)
        y = agg(lvl(fit, tk.get(t, t), roles[t], "sl", "B"), t)
        TS[t] = float(np.cov(x, y, bias=True)[0, 1] / x.var())
    for comp in ("lp_ref", "lp_comp"):
        x = lvl(fit, comp, "harmful", "en", "B").mean(1)
        y = lvl(fit, comp, "harmful", "sl", "B").mean(1)
        TS[f"harmful_{comp}"] = {"slope": float(np.cov(x, y, bias=True)[0, 1] / x.var()), "mean_EN": float(x.mean()), "mean_SL": float(y.mean())}
    out["transfer_slopes"] = TS
    # ---- judged validity counts + edit-level Spearman (pandas rank corr)
    J = json.loads((WS / "results" / "validity" / "judged.json").read_text())
    byid = {e["edit_id"]: e for e in edits}
    cnt, rows = {}, []
    for eid, g in J.items():
        c = {}
        for lg in ("en", "sl"):
            for role in ("harmful", "harmless"):
                labs = [x["label"] for x in g if x["lang"] == lg and x["role"] == role]
                c[f"{lg}_{role}"] = f"{sum(lb == 'refused' for lb in labs)}/{len(labs)}"
        cnt[eid] = c
        for lg in ("en", "sl"):
            rate = np.mean([x["label"] == "refused" for x in g if x["lang"] == lg and x["role"] == "harmful"])
            tv = 0.0 if eid == "ORIG" else float(lvl([byid[eid]], "R1", "harmful", lg, "B").mean())
            rows.append((eid, lg, tv, rate))
    df = pd.DataFrame(rows, columns=["edit", "lang", "R1", "rate"])
    out["validity_counts"] = {k: cnt[k] for k in ("ORIG", "ET_096") if k in cnt}
    out["validity_min_SL_harmful_refused"] = min(int(v["sl_harmful"].split("/")[0]) for v in cnt.values())
    out["validity_spearman_R1"] = {lg: float(d["R1"].corr(d["rate"], method="spearman")) for lg, d in df.groupby("lang")}
    # ---- Gap via polynomial OLS (standardised X + squares, ridge 1e-3), own folds, own split-half ceilings
    rng = np.random.default_rng(7)
    folds = rng.permutation(len(fit)) % 5

    def cv_r2(X, y, fo=folds):
        Z = (X - X.mean(0)) / (X.std(0) + 1e-12)
        F = np.c_[np.ones(len(Z)), Z, Z ** 2]
        pred = np.empty_like(y)
        for k in range(5):
            tr, te = fo != k, fo == k
            w = np.linalg.solve(F[tr].T @ F[tr] + 1e-3 * np.eye(F.shape[1]), F[tr].T @ y[tr])
            pred[te] = F[te] @ w
        return float(1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum())

    def ceiling(M, t, n=50):
        r = np.random.default_rng(11)
        cs = []
        for _ in range(n):
            p = r.permutation(M.shape[1])
            a, b = agg(M[:, p[: len(p) // 2]], t), agg(M[:, p[len(p) // 2:]], t)
            c = np.corrcoef(a, b)[0, 1]
            cs.append(2 * c / (1 + c))
        return float(np.mean(cs))

    def X_of(half):
        return np.c_[tuple(agg(lvl(fit, tk.get(t, t), roles[t], "en", half), t) for t in ("R1", "Rb", "K", "N", "M"))]
    G = {}
    for t in ("R1", "Rb", "K"):
        gs, graw = [], []
        for hx, hy in (("A", "B"), ("B", "A")):
            X = X_of(hx)
            Men, Msl = lvl(fit, tk.get(t, t), roles[t], "en", hy), lvl(fit, tk.get(t, t), roles[t], "sl", hy)
            yen, ysl = agg(Men, t), agg(Msl, t)
            ren, rsl = cv_r2(X, yen), cv_r2(X, ysl)
            graw.append(ren - rsl)
            gs.append(ren / ceiling(Men, t) - rsl / ceiling(Msl, t))
            if t == "R1" and hx == "A":
                G["R1_R2_EN_AtoB"], G["R1_R2_SL_AtoB"] = ren, rsl
                # placebo 1: per-edit random EN/SL label swap -> Gap centred on 0
                pl = []
                for s in range(200):
                    sw = np.random.default_rng(100 + s).random(len(yen)) < 0.5
                    a_, b_ = np.where(sw, ysl, yen), np.where(sw, yen, ysl)
                    pl.append(cv_r2(X, a_) - cv_r2(X, b_))
                G["placebo_lang_swap_rawGap_mean"] = float(np.mean(pl))
                G["placebo_lang_swap_rawGap_95"] = [float(np.percentile(pl, 2.5)), float(np.percentile(pl, 97.5))]
                G["placebo_lang_swap_covers_0"] = bool(np.percentile(pl, 2.5) <= 0 <= np.percentile(pl, 97.5))
                G["placebo_lang_swap_frac_ge_observed"] = float(np.mean(np.array(pl) >= ren - rsl))
                # placebo 2: permuted edit order of the target -> R2 <= ~0
                pe = [cv_r2(X, np.random.default_rng(500 + s).permutation(ysl)) for s in range(50)]
                G["placebo_permuted_target_R2_mean"] = float(np.mean(pe))
                G["placebo_permuted_target_R2_max"] = float(np.max(pe))
        G[t] = {"Gap_R2star_polyOLS": float(np.mean(gs)), "Gap_raw_polyOLS": float(np.mean(graw))}
    out["gap_independent"] = G
    (WS / "results" / "rederive.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
