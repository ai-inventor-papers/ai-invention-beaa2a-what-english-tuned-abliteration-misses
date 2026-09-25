#!/usr/bin/env python3
"""T7 final audit: recompute every headline number from the saved per-item files through a separate plain-numpy code
path (rank-based AUROC, normal-equation OLS, plain means) and compare with results/analysis/summary.json and
results/<m>/mech_<m>.json (tolerance 1e-6); plus label-permutation placebos and budget / split-access checks.
Writes results/verify_numbers.json."""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

import common as C
from common import MODELS, jdump, jload

TOL = 1e-6
PM = {"arc_challenge": "acc_norm", "hellaswag": "acc_norm", "openbookqa": "acc_norm", "piqa": "acc_norm", "boolq": "acc", "winogrande": "acc"}


def rank_auc(y, s) -> float:
    """Mann-Whitney AUROC with average ranks (independent of sklearn)."""
    y = np.asarray(y).astype(bool)
    s = np.asarray(s, float)
    order = np.argsort(s, kind="mergesort")
    ranks = np.empty(len(s))
    ss = s[order]
    i = 0
    while i < len(ss):
        j = i
        while j + 1 < len(ss) and ss[j + 1] == ss[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2 + 1
        i = j + 1
    n1, n0 = y.sum(), (~y).sum()
    return float((ranks[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def ne_ols(X, y):
    X = np.column_stack([np.ones(len(y))] + list(X))
    return np.linalg.solve(X.T @ X, X.T @ y)


def main() -> None:
    S = jload(C.RES / "analysis" / "summary.json")
    checks, placebo = [], {}

    def chk(name, a, b, tol=TOL):
        ok = (a is None and b is None) or (a is not None and b is not None and np.isfinite(a) and np.isfinite(b) and abs(a - b) <= tol) \
             or (a is not None and b is not None and not np.isfinite(a) and not np.isfinite(b))
        checks.append({"check": name, "recomputed": a, "reported": b, "ok": bool(ok)})

    rng = np.random.default_rng(7)
    for m in MODELS:
        if m not in S.get("models", {}):
            continue
        R = S["models"][m]
        # utility
        for lang in C.LANGS:
            if not R["utility"]:
                break
            mac_o, mac_e = [], []
            for t in C.TASKS:
                vals = {}
                for ck in ("orig", "edit"):
                    rows = [r for r in jload(C.RES / m / f"utility_{ck}.json") if r["lang"] == lang and r["task"] == t]
                    vals[ck] = np.mean([r[PM[t]] for r in rows])
                chk(f"{m}|{lang}|{t}|delta", float(vals["edit"] - vals["orig"]), R["utility"][lang][t]["delta"])
                mac_o.append(vals["orig"])
                mac_e.append(vals["edit"])
            chk(f"{m}|{lang}|macro_delta", float(np.mean(mac_e) - np.mean(mac_o)), R["utility"][lang]["macro"]["delta"])
        # FLORES
        if R["flores"]:
            fo = pd.DataFrame(jload(C.RES / m / "flores_orig.json"))
            fe = pd.DataFrame(jload(C.RES / m / "flores_edit.json"))
            for lang in C.LANGS:
                chk(f"{m}|{lang}|flores_delta", float(fe[fe.lang == lang].nll.mean() - fo[fo.lang == lang].nll.mean()), R["flores"][lang]["delta"])
        # KL
        kl = pd.DataFrame(jload(C.RES / m / "kl_r1.json")["rows"])
        for lang in C.LANGS:
            for k in ("KL1", "KL32"):
                v = np.sort(kl[(kl.role == "harmless") & (kl.lang == lang)][k].values)
                n = len(v)
                med = float(v[n // 2]) if n % 2 else float((v[n // 2 - 1] + v[n // 2]) / 2)
                chk(f"{m}|{lang}|harmless_{k}_median", med, R["divergence"][f"harmless|{lang}"][k]["median"])
        # frozen probe AUROC at primary site (orig) from s4_scores.parquet vs mech json
        mech = jload(C.RES / m / f"mech_{m}.json")
        sc = pd.read_parquet(C.RES / m / "s4_scores.parquet")
        for lang in C.LANGS:
            d = sc[sc.lang == lang]
            y = (d.role == "harmful").values
            chk(f"{m}|{lang}|frozen_dim_orig_auc", rank_auc(y, d.s_frozen_orig.values),
                mech["primary"]["frozen_vs_refit"][f"plain|{lang}"]["dim"]["frozen_orig"]["auc"])
            fe_auc = mech["primary"]["frozen_vs_refit"][f"plain|{lang}"]["dim"]["frozen_orig"]["auc"] + \
                mech["primary"]["frozen_vs_refit"][f"plain|{lang}"]["dim"]["frozen_edit_minus_orig"]["diff_vs_2"]
            chk(f"{m}|{lang}|frozen_dim_edit_auc", rank_auc(y, d.s_frozen_edit.values), fe_auc)
            placebo[f"{m}|{lang}|frozen_auc_permuted_labels"] = rank_auc(rng.permutation(y), d.s_frozen_orig.values)
        # drift geometry: Cohen's d along the frozen axis from the saved per-item frozen scores (float32 path vs float64 path)
        dgp = C.RES / m / f"drift_geometry_{m}.json"
        if dgp.exists():
            dg = jload(dgp)["primary"]
            for lang in C.LANGS:
                d = sc[sc.lang == lang]
                y = (d.role == "harmful").values
                for ck in ("orig", "edit"):
                    v = d[f"s_frozen_{ck}"].values
                    a, b = v[y], v[~y]
                    cd = float((a.mean() - b.mean()) / np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2))
                    rep = dg[lang][f"sep_frozen_{ck}"]["value"]
                    chk(f"{m}|{lang}|drift_sep_frozen_{ck}", cd, rep, tol=max(2e-3, 2e-3 * abs(rep)))
        # gate AUROC
        gv = pd.read_parquet(C.RES / "generation_validity.parquet")
        a2i = pd.read_parquet(C.RES / m / "a2_items.parquet")
        src = S["label_source"]
        for lang in C.LANGS:
            g = R["gate"][lang]
            for Rn in ("R_seq", "R1"):
                if "item_auroc" not in g.get(Rn, {}):
                    continue
                ys, ss = [], []
                for ck in ("orig", "edit"):
                    lab = gv[(gv.model == m) & (gv.ckpt == ck) & (gv.lang == lang) & gv.kind.str.startswith("s4")]
                    lab = lab.assign(lbl=np.where(lab["empty"], "empty", np.where(lab.malformed_rule, "malformed", np.where(lab.kw_refusal, "refused", "complied")))
                                     if src == "markers" else
                                     np.where(~lab.judge_label.isin(["NOT_JUDGED", "unparsed"]), lab.judge_label,
                                              np.where(lab.judge2_label.notna() & (lab.judge2_label != "unparsed"), lab.judge2_label, "NOT_JUDGED")))
                    mm = a2i[a2i.lang == lang].merge(lab[["semantic_id", "role", "lbl"]], on=["semantic_id", "role"])
                    mm = mm[mm.lbl.isin(["refused", "complied"])]
                    ys.append((mm.lbl == "refused").values)
                    ss.append(mm[f"{Rn}_{ck}"].values)
                chk(f"{m}|{lang}|gate_{Rn}_auroc", rank_auc(np.concatenate(ys), np.concatenate(ss)), g[Rn]["item_auroc"])
        # A2 slope ratios (primary regression) by normal equations
        for Rn, a2 in R["A2"].items():
            if not isinstance(a2, dict) or "per_lang" not in a2:
                continue
            d0 = a2i.copy()
            s = (d0.s_frozen_orig - d0.s_frozen_orig.mean()) / d0.s_frozen_orig.std()
            d0 = d0.assign(s=s)
            for lang in C.LANGS:
                d = d0[d0.lang == lang]
                Xs = [d.s.values] + ([d[a2["p_term"]].values] if a2["p_term"] else [])
                b0 = ne_ols(Xs, d[f"{Rn}_orig"].values)
                b1 = ne_ols(Xs, d[f"{Rn}_edit"].values)
                chk(f"{m}|{lang}|A2_{Rn}_slope_ratio", float(b1[1] / b0[1]), a2["per_lang"][lang]["primary"]["slope_ratio"], 1e-6)
                chk(f"{m}|{lang}|A2_{Rn}_intercept_shift", float(b1[0] - b0[0]), a2["per_lang"][lang]["primary"]["intercept_shift"], 1e-6)
                sp = rng.permutation(d.s.values)
                pb0 = ne_ols([sp], d[f"{Rn}_orig"].values)
                placebo[f"{m}|{lang}|A2_{Rn}_shuffled_s_b0_over_true_b0"] = float(pb0[1] / ne_ols([d.s.values], d[f"{Rn}_orig"].values)[1])
    # budget + split access
    cost = 0.0
    cp = C.RES / "judge" / "cost_log.jsonl"
    if cp.exists():
        cost = sum(float(json.loads(l)["cost"]) for l in cp.read_text().splitlines() if l.strip())
    acc = [json.loads(l) for l in (C.LOGS / "split_access.log").read_text().splitlines()] if (C.LOGS / "split_access.log").exists() else []
    util_reads = {}
    for a in acc:
        if a["split"].startswith("S7_") and "--stages" in " ".join(a["caller"]) or a["split"].startswith("S7_"):
            util_reads[a["split"]] = util_reads.get(a["split"], 0) + 1
    out = {"n_checks": len(checks), "n_ok": sum(c["ok"] for c in checks), "all_ok": all(c["ok"] for c in checks), "checks": checks,
           "placebos": placebo, "api_cost_usd": cost, "cost_under_10": cost < 10,
           "split_access_counts_S7": util_reads,
           "split_access_note": "S7 files are read by freeze_protocol (sample freeze, before scoring), by each utility stage (scoring) and by the "
                                "mini/test runs; the FINAL scoring pass per model reads each S7 file once (logs/split_access.log)"}
    jdump(out, C.RES / "verify_numbers.json")
    print(f"verify: {out['n_ok']}/{out['n_checks']} ok; cost ${cost:.3f}; placebos {placebo}")


if __name__ == "__main__":
    main()
