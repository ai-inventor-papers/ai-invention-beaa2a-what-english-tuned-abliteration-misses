"""S2(d-h): judge-sensitivity table, within-edit agreement, keyword miscalibration, Gemma SL-EN gap range, exp8 per-judge re-split.

Reads only results/labels_long.parquet (built by s01 from raw per-item files) plus exp4 frozen S5X pairs and official guard labels.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from loguru import logger

from lib import E4, RES, SEED, agreement, cluster_boot_mean, fmt, mcnemar_exact, read_json, read_jsonl, setup, wilson, write_json

CLASSES = ["REFUSED", "PARTIAL", "COMPLIED", "INVALID"]
LLM = ["gpt41", "qwen3_14b", "nemotron", "gemma_self"]
RANDOM_SUBSET = {("exp4", "gpt41"): True, ("exp4", "qwen3_14b"): True, ("exp5", "gpt41"): False, ("exp5", "nemotron"): False,
                 ("exp6", "gpt41"): False, ("exp6", "qwen3_14b"): True, ("exp7", "gemma_self"): True, ("exp7", "gpt41"): True,
                 ("exp8", "gpt41"): False, ("exp8", "qwen3_14b"): True, ("exp3", "gpt41"): True}
SUBSET_NOTE = {("exp5", "gpt41"): "priority-ordered (~52% of S4 harmful), not a seeded random draw",
               ("exp5", "nemotron"): "fill-in + stratified 200 overlap; not random",
               ("exp6", "gpt41"): "gpt-4.1 labelled until blocked (1,130 of 2,140); remainder Qwen",
               ("exp8", "gpt41"): "ARM-PRIORITISED (5,298 of 12,136): NOT random; compare with Qwen only on overlap",
               ("exp7", "gpt41"): "originals only (440)"}


def cell_table(L: pd.DataFrame) -> pd.DataFrame:
    gen_n = L[L.judge == "keyword"].groupby(["artifact", "dataset", "cell", "lang"]).size()
    out = []
    for (art, ds, cell, lang, judge), g in L.dropna(subset=["label"]).groupby(["artifact", "dataset", "cell", "lang", "judge"]):
        n = len(g)
        ngen = int(gen_n.get((art, ds, cell, lang), g.item.nunique()))
        row = dict(artifact=art, dataset=ds, cell=cell, lang=lang, judge=judge, is_orig=bool(g.is_orig.iloc[0]), role=g.role.iloc[0],
                   n=n, n_generated=ngen, coverage=n / ngen if ngen else np.nan,
                   random_subset=RANDOM_SUBSET.get((art, judge), judge == "keyword"), subset_note=SUBSET_NOTE.get((art, judge), ""))
        classes = CLASSES if judge != "keyword" else ["REFUSED", "NOT_REFUSED"]
        for c in classes:
            x = (g.label == c).values.astype(float)
            k = int(x.sum())
            lo, hi = wilson(k, n)
            clo, chi = cluster_boot_mean(x, g.cluster.values, b=1000)
            row |= {f"p_{c.lower()}": k / n, f"p_{c.lower()}_wilson_lo": lo, f"p_{c.lower()}_wilson_hi": hi,
                    f"p_{c.lower()}_cboot_lo": clo, f"p_{c.lower()}_cboot_hi": chi}
        out.append(row)
    return pd.DataFrame(out)


def agreement_tables(L: pd.DataFrame):
    W = L.dropna(subset=["label"]).pivot_table(index=["artifact", "dataset", "cell", "lang", "item", "cluster", "is_orig"],
                                                columns="judge", values="label", aggfunc="first").reset_index()
    rows, confs = [], []
    for art, g in W.groupby("artifact"):
        judges = [j for j in ["gpt41", "qwen3_14b", "nemotron", "gemma_self", "keyword"] if j in g.columns]
        for i, j1 in enumerate(judges):
            for j2 in judges[i + 1:]:
                h = g.dropna(subset=[j1, j2])
                if len(h) < 30:
                    continue
                binary_only = "keyword" in (j1, j2)
                for scope, hh in (("pooled_all", h), ("pooled_orig", h[h.is_orig]), ("pooled_edited", h[~h.is_orig])):
                    for defn in (["binary"] if binary_only else ["binary", "4class"]):
                        if len(hh) < 30:
                            rows.append(dict(artifact=art, judge_a=j1, judge_b=j2, scope=scope, cell="*", lang="*", definition=defn, n=len(hh),
                                             note="overlap < 30: not estimated"))
                            continue
                        a, b = hh[j1].values, hh[j2].values
                        if defn == "binary":
                            a = np.where(a == "REFUSED", "REFUSED", "NOT")
                            b = np.where(b == "REFUSED", "REFUSED", "NOT")
                        r = agreement(a, b, clusters=None)
                        rows.append(dict(artifact=art, judge_a=j1, judge_b=j2, scope=scope, cell="*", lang="*", definition=defn,
                                         **{k: v for k, v in r.items() if k not in ("labels", "confusion")}))
                        confs.append(dict(artifact=art, judge_a=j1, judge_b=j2, scope=scope, definition=defn, confusion=r["confusion"]))
                # per edited cell (pool languages and datasets within the cell)
                for (cell,), hc in h[~h.is_orig].groupby(["cell"]):
                    if len(hc) < 30:
                        continue
                    for defn in (["binary"] if binary_only else ["binary", "4class"]):
                        a, b = hc[j1].values, hc[j2].values
                        if defn == "binary":
                            a = np.where(a == "REFUSED", "REFUSED", "NOT")
                            b = np.where(b == "REFUSED", "REFUSED", "NOT")
                        r = agreement(a, b, b_reps=1000)
                        rows.append(dict(artifact=art, judge_a=j1, judge_b=j2, scope="cell_edited", cell=cell, lang="*", definition=defn,
                                         **{k: v for k, v in r.items() if k not in ("labels", "confusion")}))
                        if defn == "4class" or binary_only:
                            confs.append(dict(artifact=art, judge_a=j1, judge_b=j2, scope=f"cell:{cell}", definition=defn, confusion=r["confusion"]))
    A = pd.DataFrame(rows)
    return A, confs, W


def keyword_miscal(W: pd.DataFrame) -> pd.DataFrame:
    out = []
    for (art, cell, lang, role), g in W.groupby(["artifact", "cell", "lang", W.dataset.map(lambda d: d)]) if False else []:
        pass
    W = W.copy()
    for (art, cell, lang), g in W.groupby(["artifact", "cell", "lang"]):
        for j in ["gpt41", "qwen3_14b", "nemotron", "gemma_self"]:
            if j not in g.columns or "keyword" not in g.columns:
                continue
            for harm, gh in ((True, g[g.dataset.str.contains("harm|S5|hb_test", regex=True) & ~g.dataset.str.contains("harmless|ben", regex=True)]),
                             (False, g[g.dataset.str.contains("harmless|ben|S6|dolly", regex=True)])):
                h = gh.dropna(subset=[j, "keyword"])
                if len(h) < 10:
                    continue
                k = h.keyword.values == "REFUSED"
                jr = h[j].values == "REFUSED"
                fp = (k & ~jr).sum() / k.sum() if k.sum() else np.nan
                fn = (~k & jr).sum() / jr.sum() if jr.sum() else np.nan
                fp_partial = ((k & (h[j].values == "PARTIAL")).sum() / (k & ~jr).sum()) if (k & ~jr).sum() else np.nan
                r = agreement(np.where(k, "R", "N"), np.where(jr, "R", "N"), b_reps=500)
                out.append(dict(artifact=art, cell=cell, lang=lang, harmful=harm, judge=j, is_orig=bool(h.is_orig.iloc[0]), n=len(h),
                                keyword_rate=k.mean(), judged_rate=jr.mean(), fp_share=fp, fn_share=fn, fp_share_partial=fp_partial,
                                kappa=r["kappa"], kappa_ci_low=r["kappa_ci_low"], kappa_ci_high=r["kappa_ci_high"], ac1=r["ac1"]))
    return pd.DataFrame(out)


# ------------------------------------------------------------------ gap range
CKPT_MAP = {  # canonical checkpoint -> list of (artifact, dataset-filter, cell, orig_cell, dataset label)
    "gemma_edit": [("exp4", ["S5"], "gemma_edit", "gemma_orig", "exp4 S5 (RefusEU, unpaired)"),
                   ("exp5", ["s4_harmful"], "gemma:edit", "gemma:orig", "exp5 S4 harmful (twins)"),
                   ("exp8", ["hoc_harmful"], "gemma:W0", "gemma:A0", "exp8 W0 S4-hoc"),
                   ("exp7", ["jbb_harmful"], "gemma:ET_096", "gemma:ORIG", "exp7 ET_096 JBB (self-judge)"),
                   ("exp1", ["hb_test100"], "gemma:own", "gemma:orig", "iter-1 exp1 harmful_behaviors")],
    "gams_edit": [("exp4", ["S5"], "gams_edit", "gams_orig", "exp4 S5 (RefusEU, unpaired)"),
                  ("exp5", ["s4_harmful"], "gams:edit", "gams:orig", "exp5 S4 harmful (twins)"),
                  ("exp6", ["jbb_harm"], "gams:core_stage0c", "gams:orig", "exp6 core JBB"),
                  ("exp1", ["hb_test100"], "gams:own", "gams:orig", "iter-1 exp1 harmful_behaviors")],
    "community_ref": [("exp4", ["S5"], "community_ref", "gemma_orig", "exp4 S5 (RefusEU, unpaired)"),
                      ("exp8", ["hoc_harmful"], "community:C0", "gemma:A0", "exp8 C0 S4-hoc")],
    "gemma_orig": [("exp4", ["S5"], "gemma_orig", None, "exp4 S5 (RefusEU, unpaired)"),
                   ("exp5", ["s4_harmful"], "gemma:orig", None, "exp5 S4 harmful (twins)"),
                   ("exp1", ["hb_test100"], "gemma:orig", None, "iter-1 exp1 harmful_behaviors")],
    "gams_orig": [("exp4", ["S5"], "gams_orig", None, "exp4 S5 (RefusEU, unpaired)"),
                  ("exp5", ["s4_harmful"], "gams:orig", None, "exp5 S4 harmful (twins)"),
                  ("exp1", ["hb_test100"], "gams:orig", None, "iter-1 exp1 harmful_behaviors")],
}


def ind(labels: np.ndarray, defn: str) -> np.ndarray:
    if defn == "strict":
        return (labels == "REFUSED").astype(float)
    return np.isin(labels, ["REFUSED", "PARTIAL"]).astype(float)


def gap_cluster(g: pd.DataFrame, judge: str, defn: str, seed=SEED):
    """SL - EN on one cell; bootstrap over semantic clusters (items of both languages resampled together)."""
    h = g[g.judge == judge].dropna(subset=["label"])
    if judge == "keyword" and defn == "broad":
        return None
    en, sl = h[h.lang == "en"], h[h.lang == "sl"]
    if len(en) < 10 or len(sl) < 10:
        return None
    xe, xs = ind(en.label.values, defn), ind(sl.label.values, defn)
    clus = np.unique(np.concatenate([en.cluster.values, sl.cluster.values]))
    ci_ = {c: i for i, c in enumerate(clus)}
    ie = np.array([ci_[c] for c in en.cluster.values])
    is_ = np.array([ci_[c] for c in sl.cluster.values])
    se, ne = np.bincount(ie, xe, len(clus)), np.bincount(ie, minlength=len(clus))
    ss, ns = np.bincount(is_, xs, len(clus)), np.bincount(is_, minlength=len(clus))
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(clus), (2000, len(clus)))
    with np.errstate(invalid="ignore", divide="ignore"):
        bs = ss[idx].sum(1) / ns[idx].sum(1) - se[idx].sum(1) / ne[idx].sum(1)
    bs = bs[np.isfinite(bs)]
    shared = len(set(en.cluster) & set(sl.cluster))
    return dict(n_en=len(en), n_sl=len(sl), n_shared_clusters=shared, p_en=xe.mean(), p_sl=xs.mean(), gap=xs.mean() - xe.mean(),
                ci_low=float(np.quantile(bs, .025)), ci_high=float(np.quantile(bs, .975)))


def s5x_rows(L: pd.DataFrame, fr: dict) -> list[dict]:
    out = []
    pairs = fr["s5x_pairs"]
    X = L[L.artifact == "exp4"].set_index(["cell", "item", "judge"]).label
    for ck, oc in (("gemma_edit", "gemma_orig"), ("gams_edit", "gams_orig"), ("community_ref", "gemma_orig"), ("gemma_orig", None), ("gams_orig", None)):
        for judge in ("qwen3_14b", "gpt41", "keyword"):
            for defn in ("strict", "broad"):
                if judge == "keyword" and defn == "broad":
                    continue
                en, sl, eo, so, pid = [], [], [], [], []
                for p in pairs:
                    e, s = X.get((ck, p["en_item"], judge)), X.get((ck, p["sl_item"], judge))
                    if e is None or s is None or pd.isna(e) or pd.isna(s):
                        continue
                    en.append(e), sl.append(s), pid.append(p["pair_id"])
                    if oc:
                        eo.append(X.get((oc, p["en_item"], judge)))
                        so.append(X.get((oc, p["sl_item"], judge)))
                n = len(en)
                row = dict(checkpoint=ck, dataset="exp4 S5X (paired, verified translations)", artifact="exp4", judge=judge, definition=defn,
                           n_pairs=n, paired=True)
                if n == 0:
                    out.append(row)
                    continue
                xe, xs = ind(np.array(en), defn), ind(np.array(sl), defn)
                row |= dict(n_en=n, n_sl=n, p_en=xe.mean(), p_sl=xs.mean(), gap=xs.mean() - xe.mean())
                mc = mcnemar_exact(xs.astype(bool), xe.astype(bool))
                row |= dict(mcnemar_p=mc["p_exact"], n_sl1_en0=mc["n10_a1_b0"], n_sl0_en1=mc["n01_a0_b1"])
                if n >= 30:
                    lo, hi = cluster_boot_mean(xs - xe, np.arange(n))
                    row |= dict(ci_low=lo, ci_high=hi)
                else:
                    row |= dict(note=f"only {n} pairs with both members labelled (<30): no CI")
                if oc:
                    ok = [i for i in range(n) if eo[i] is not None and so[i] is not None and not pd.isna(eo[i]) and not pd.isna(so[i])]
                    if len(ok) >= 30:
                        oe, os_ = ind(np.array([eo[i] for i in ok]), defn), ind(np.array([so[i] for i in ok]), defn)
                        d = (xs[ok] - os_) - (xe[ok] - oe)
                        lo, hi = cluster_boot_mean(d, np.arange(len(ok)))
                        row |= dict(did=d.mean(), did_ci_low=lo, did_ci_high=hi, did_n=len(ok))
                out.append(row)
    return out


def gap_range(L: pd.DataFrame, fr: dict) -> pd.DataFrame:
    rows = s5x_rows(L, fr)
    for ck, specs in CKPT_MAP.items():
        for art, dss, cell, oc, label in specs:
            g = L[(L.artifact == art) & (L.cell == cell) & (L.dataset.isin(dss))]
            for judge in sorted(g.judge.unique()):
                for defn in ("strict", "broad"):
                    r = gap_cluster(g, judge, defn)
                    if r is None:
                        continue
                    row = dict(checkpoint=ck, dataset=label, artifact=art, judge=judge, definition=defn, paired=False, **r)
                    if oc:
                        go = L[(L.artifact == art) & (L.cell == oc) & (L.dataset.isin(dss))]
                        ro = gap_cluster(go, judge, defn)
                        if ro is not None:
                            row |= dict(orig_gap=ro["gap"], did=r["gap"] - ro["gap"])
                    rows.append(row)
    G = pd.DataFrame(rows)
    return G


def range_summary(G: pd.DataFrame) -> pd.DataFrame:
    out = []
    for (ck, ds, defn), g in G.dropna(subset=["gap"]).groupby(["checkpoint", "dataset", "definition"]):
        llm = g[g.judge != "keyword"]
        ci_ok = g.dropna(subset=["ci_low"])
        side = np.sign(ci_ok.ci_low.values) * (np.sign(ci_ok.ci_low.values) == np.sign(ci_ok.ci_high.values))
        out.append(dict(checkpoint=ck, dataset=ds, definition=defn, judges=",".join(g.judge), n_judges=len(g),
                        gap_min=g.gap.min(), gap_max=g.gap.max(), llm_gap_min=llm.gap.min() if len(llm) else np.nan,
                        llm_gap_max=llm.gap.max() if len(llm) else np.nan,
                        widest_ci=f"[{fmt(ci_ok.ci_low.min())}, {fmt(ci_ok.ci_high.max())}]" if len(ci_ok) else "",
                        sign_stable=bool(len(side) and (np.all(side > 0) or np.all(side < 0))),
                        sign_of_points_stable=bool(np.all(g.gap > 0) or np.all(g.gap < 0))))
    return pd.DataFrame(out)


def exp8_split(L: pd.DataFrame) -> pd.DataFrame:
    X = L[(L.artifact == "exp8")].dropna(subset=["label"])
    out = []
    for (cell, lang, role, judge), g in X.groupby(["cell", "lang", "role", "judge"]):
        out.append(dict(cell=cell, arm=cell.split(":")[1], model=cell.split(":")[0], lang=lang, role=role, judge=judge, n=len(g),
                        p_refused=(g.label == "REFUSED").mean(), p_refused_or_partial=g.label.isin(["REFUSED", "PARTIAL"]).mean(),
                        p_invalid=(g.label == "INVALID").mean(), datasets=",".join(sorted(g.dataset.unique()))))
    D = pd.DataFrame(out)
    # overlap-only comparison gpt41 vs qwen per arm (the only valid between-judge comparison for a non-random subset)
    W = X[X.judge.isin(["gpt41", "qwen3_14b"])].pivot_table(index=["cell", "lang", "role", "item"], columns="judge", values="label", aggfunc="first").dropna().reset_index()
    ov = []
    for (cell, lang, role), g in W.groupby(["cell", "lang", "role"]):
        a = (g.gpt41 == "REFUSED").values.astype(float)
        b = (g.qwen3_14b == "REFUSED").values.astype(float)
        if len(g) >= 10:
            lo, hi = cluster_boot_mean(b - a, np.arange(len(g)), b=1000)
        else:
            lo = hi = np.nan
        ov.append(dict(cell=cell, lang=lang, role=role, n_overlap=len(g), gpt41_refused=a.mean(), qwen_refused=b.mean(), qwen_minus_gpt41=b.mean() - a.mean(),
                       ci_low=lo, ci_high=hi))
    return D, pd.DataFrame(ov)


def official_asr() -> pd.DataFrame:
    rows = []
    for r in read_jsonl(E4 / "results/guard/official_labels.jsonl"):
        rows.append(dict(cell=r["ckpt"], item=r["item_key"], set=r["item_key"].split(":")[0], lang=r["item_key"].split(":")[-1][-2:],
                         unsafe=r.get("official_unsafe")))
    D = pd.DataFrame(rows)
    D = D[D.set == "S5"].dropna(subset=["unsafe"])
    out = []
    for (c, lg), g in D.groupby(["cell", "lang"]):
        k, n = int(g.unsafe.sum()), len(g)
        out.append(dict(cell=c, lang=lg, n=n, asr=k / n, wilson_lo=wilson(k, n)[0], wilson_hi=wilson(k, n)[1]))
    return pd.DataFrame(out)


def main():
    setup("s03_judges")
    L = pd.read_parquet(RES / "labels_long.parquet")
    fr = read_json(E4 / "frozen_samples.json")
    logger.info("cell table")
    C = cell_table(L)
    C.to_csv(RES / "judge_sensitivity.csv", index=False)
    logger.info("agreement")
    A, confs, W = agreement_tables(L)
    A.to_csv(RES / "judge_agreement.csv", index=False)
    write_json(RES / "judge_confusions.json", confs)
    logger.info("keyword miscalibration")
    K = keyword_miscal(W)
    K.to_csv(RES / "keyword_miscalibration.csv", index=False)
    # exp4 keyword reimplementation check (placebo P6)
    k4 = L[(L.artifact == "exp4") & (L.judge == "keyword")]
    p6 = dict(n=len(k4), n_match=int((k4.label == k4.prior_autoscore_kw).sum()))
    write_json(RES / "p6_keyword_check.json", p6)
    logger.info(f"P6 keyword reimplementation: {p6}")
    logger.info("gap range")
    G = gap_range(L, fr)
    G.to_csv(RES / "gap_range.csv", index=False)
    S = range_summary(G)
    S.to_csv(RES / "gap_range_summary.csv", index=False)
    logger.info("exp8 split")
    D, OV = exp8_split(L)
    D.to_csv(RES / "exp8_by_judge.csv", index=False)
    OV.to_csv(RES / "exp8_overlap_gpt41_vs_qwen.csv", index=False)
    O = official_asr()
    O.to_csv(RES / "exp4_official_asr.csv", index=False)
    logger.info("done")


if __name__ == "__main__":
    main()
