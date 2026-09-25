#!/usr/bin/env python3
"""STAGES S6 + S7 - the gradient-blind fraction, its CIs and placebos, the incumbent's best shot, the conventional
anchors, the held-out-source sanity row, the F6 decomposition, and the post-hoc reselection decomposition.

  python analysis.py --rehearsal   T2/T3: Gemma-only dress rehearsal on art_0XmNBGkzsJc_'s stored data (known answer)
                                   -> results/rehearsal_gemma.json   (must pass BEFORE the freeze)
  python analysis.py               full two-search analysis -> results/analysis.json, results/per_candidate.csv,
                                   results/reselection_table.csv, results/conventional_table.csv
                                   (REFUSES to run unless both certification files exist with explicit verdicts)
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
from loguru import logger
from scipy.stats import spearmanr
from sklearn.metrics import cohen_kappa_score

import gbf as G
from common import A11, CONFIGS, N_STARTUP, RESULTS, WS, read_jsonl, setup_logging, write_json

B = 2000
P7_VERDICT = ("NOT A BETTER EDIT (P7, iteration 3): at equal English refusal the 1.5x-scaled old edit has gap +.33 "
              "(difference -.05 [-.41,+.12]); at equal harmless KL the dose ladder reaches gap .00 (-.38 [-.47,-.29]); "
              "dose for dose the corrected edit is strictly worse. No row of this table is a recommendation.")


# ------------------------------------------------------------------ loading
def load_rows(model: str) -> pd.DataFrame:
    return pd.read_parquet(RESULTS / f"scored_{model}.parquet")


def matrices(df: pd.DataFrame, trials: list[int], col: str) -> np.ndarray:
    d = df[df.trial.isin(trials)].pivot(index="trial", columns="prompt_id", values=col).reindex(trials)
    if d.isna().any().any():
        raise ValueError(f"incomplete matrix for {col}")
    return d.values.astype(float)


def per_candidate(df: pd.DataFrame, model: str) -> pd.DataFrame:
    ed = df[df.trial >= 0]
    trials = sorted(ed.trial.unique())
    counts = ed.groupby("trial").agg(n=("K", "size"), K=("K", "sum"), C=("C", "sum"), K_repaired=("K_repaired", "sum"),
                                     K_content_only=("K_content_only", "sum"), K_empty=("K_empty", "sum"),
                                     C_trunc100=("C_trunc100", "sum"), mean_tokens=("n_tokens", "mean"),
                                     share_truncated=("truncated", "mean"))
    counts = counts.reindex(trials)
    jv = ed[ed.J.notna()] if "J" in ed else ed.iloc[:0]
    jc = jv.groupby("trial").agg(J_n=("J", "size"), J_ref=("J", "sum"),
                                 J_partial=("judge_cls", lambda s: int((s == "partial").sum())),
                                 J_complied=("judge_cls", lambda s: int((s == "complied").sum())),
                                 J_irrelevant=("judge_cls", lambda s: int((s == "irrelevant").sum())),
                                 J_empty=("judge_cls", lambda s: int((s == "empty").sum())))
    jm = ed[ed.judge_cls.notna()].groupby("trial").judge_cls.apply(lambda s: int((s == "malformed").sum())).rename("J_malformed")
    out = counts.join(jc).join(jm)
    out["J"] = 100.0 * out.J_ref / out.J_n  # scaled to /100 over valid (non-malformed) judged rows
    judged_rows = ed[ed.judge_cls.notna()].groupby("trial").size().rename("n_judged")
    out = out.join(judged_rows)
    out["J_full"] = out.n_judged.fillna(0) >= 95
    out.loc[~out.J_full, "J"] = np.nan
    out["model"] = model
    out["phase"] = np.where(out.index < N_STARTUP, "startup", "tpe")
    out.index.name = "trial"
    return out.reset_index()


def kl_table(model: str) -> pd.DataFrame:
    jt = pd.read_csv(RESULTS / "journal_trials.csv")
    jt = jt[jt.model == model][["trial", "keyword_count", "kl", "direction_scope", "params_json"]].rename(
        columns={"keyword_count": "K_journal", "kl": "KL_journal"})
    if model == "gemma":
        mt = pd.read_csv(A11 / "results/miscalibration_table.csv")[["trial", "kl"]].rename(columns={"kl": "KL_replay"})
    else:
        rows = read_jsonl(RESULTS / "replay/gams_trials.jsonl")
        mt = pd.DataFrame([{"trial": r["trial"], "KL_replay": r["kl"], "K_replay_heretic": r["keyword_refusals"]} for r in rows])
        mt = mt.drop_duplicates("trial", keep="first")
    return jt.merge(mt, on="trial", how="left")


# ------------------------------------------------------------------ blocks
def gbf_block(K, C, sigma, Kmat=None, label: str = "", with_placebos: bool = True, seed: int = 0) -> dict:
    K, C, sigma = np.asarray(K, float), np.asarray(C, float), np.asarray(sigma, float)
    sb, tol = float(np.median(sigma)), float(np.median(sigma) * np.sqrt(2))
    g = G.gbf(K, C, tol)
    blk = {"label": label, "n_cand": int(len(K)), "sigma_bar": sb, "tol": tol, **g,
           "ci95": G.cluster_bootstrap(K, C, tol, B=B, seed=seed + 1)["ci95"], **G.secondary(K, C, sb)}
    pc = G.per_candidate_gbf(K, C, tol)
    blk["per_candidate_gbf"] = {"median": float(np.nanmedian(pc)) if np.isfinite(pc).any() else None,
                                "q25_q75": [float(np.nanpercentile(pc, 25)), float(np.nanpercentile(pc, 75))] if np.isfinite(pc).any() else None,
                                "n_defined": int(np.isfinite(pc).sum())}
    if with_placebos:
        blk["P_a_permutation"] = G.placebo_permutation(K, C, tol, B=B, seed=seed + 4)
        blk["P_b_self"] = G.placebo_self(K, tol)
        if Kmat is not None:
            blk["P_c_split_half"] = G.placebo_split_half(Kmat, B_split=200, seed=seed + 5)
    blk["decomposition"] = G.decompose(K, C, sb)
    blk["secondary_gbf_low_C_le_50"] = G.gbf_low(K, C, tol)
    blk["secondary_threshold_blind_C_le_10"] = G.threshold_blind(K, C)
    blk["calibration"] = G.calibration(K, C)
    return blk


def kappa_row(y, p) -> float:
    y, p = np.asarray(y, int), np.asarray(p, int)
    return float(cohen_kappa_score(y, p)) if len(set(y) | set(p)) > 1 else float("nan")


def boot_kappa(y, p, groups, B_: int = 1000, seed: int = 0) -> list[float]:
    y, p, groups = np.asarray(y, int), np.asarray(p, int), np.asarray(groups)
    ug = np.unique(groups)
    idx = {g: np.where(groups == g)[0] for g in ug}
    rng = np.random.default_rng(seed)
    ks = []
    for _ in range(B_):
        s = np.concatenate([idx[g] for g in rng.choice(ug, len(ug))])
        if len(set(y[s]) | set(p[s])) > 1:
            ks.append(cohen_kappa_score(y[s], p[s]))
    return [float(np.percentile(ks, 2.5)), float(np.percentile(ks, 97.5))] if ks else [float("nan")] * 2


def conventional(df: pd.DataFrame, pc: pd.DataFrame, trials: list[int], verdict_cols: dict[str, str]) -> dict:
    """kappa / accuracy / base rate / false-'refusal' share (row level, judged edited rows, malformed excluded),
    MAE/100 and Spearman (trial level, fully judged trials), observed ranges of K, C, J."""
    e = df[df.trial.isin(trials) & df.J.notna()] if "J" in df else df.iloc[:0]
    full = pc[pc.trial.isin(trials) & pc.J_full]
    out = {"n_rows_judged": int(len(e)), "n_trials_fully_judged": int(len(full)),
           "base_rate_judge": float(e.J.astype(int).mean()) if len(e) else None}
    for name, col in verdict_cols.items():
        if not len(e):
            continue
        y, p = e.J.astype(int).values, e[col].astype(int).values
        agg = full[col if col in full else col]
        out[name] = {"kappa": kappa_row(y, p), "kappa_ci95_trial_cluster": boot_kappa(y, p, e.trial.values),
                     "acc": float((y == p).mean()), "rate_pred": float(p.mean()),
                     "fp_share": float(((p == 1) & (y == 0)).sum() / max((p == 1).sum(), 1)),
                     "mae_per100": float((agg - full.J).abs().mean()) if len(full) else None,
                     "spearman_trial": float(spearmanr(agg, full.J).statistic) if len(full) > 3 else None,
                     "range": [float(agg.min()), float(agg.max())] if len(full) else None}
    if len(full):
        out["J_range"] = [float(full.J.min()), float(full.J.max())]
    tt = pc[pc.trial.isin(trials)]
    out["K_range_all"] = [float(tt.K.min()), float(tt.K.max())]
    out["C_range_all"] = [float(tt.C.min()), float(tt.C.max())]
    return out


def oracle_threshold(df: pd.DataFrame) -> dict:
    """Incumbent's best shot (a): marker-count threshold t chosen IN HINDSIGHT to maximise kappa vs the judge on the
    judged edited rows (empty-response rule kept as shipped)."""
    e = df[(df.trial >= 0) & df.J.notna()]
    res = {}
    for t in range(1, 7):
        p = (e.K_count >= t) | e.K_empty
        res[t] = kappa_row(e.J.astype(int).values, p.astype(int).values)
    best = max(res, key=lambda t: (res[t], -t))
    return {"kappa_by_t": res, "best_t": int(best), "best_kappa": res[best]}


def apply_rule(rows: list[tuple[int, float, float]]) -> dict:
    import sys
    sys.path.insert(0, str(A11))
    from select_rule import apply_rule_rows  # the frozen rule, verbatim (art_0XmNBGkzsJc_/select_rule.py)
    return apply_rule_rows(rows)


# ------------------------------------------------------------------ one search
def analyse_search(model: str, df: pd.DataFrame, drift_var: float | None) -> tuple[dict, pd.DataFrame]:
    pc = per_candidate(df, model)
    trials = pc.trial.tolist()
    Kmat = matrices(df, trials, "K")
    sigma = G.prompt_bootstrap_sd(Kmat, B=B, seed=0)
    pc["sigma_K"] = sigma
    oracle = oracle_threshold(df) if df.J.notna().any() else None
    if oracle:
        df = df.assign(K_oracle=((df.K_count >= oracle["best_t"]) | df.K_empty))
        pc = pc.merge(df[df.trial >= 0].groupby("trial").K_oracle.sum().rename("K_oracle").reset_index(), on="trial")
    Krep = matrices(df, trials, "K_repaired")
    pc["sigma_K_repaired"] = G.prompt_bootstrap_sd(Krep, B=B, seed=0)
    res = {"model": model, "n_candidates": len(trials)}
    pops = {"all": trials, "startup": [t for t in trials if t < N_STARTUP], "tpe": [t for t in trials if t >= N_STARTUP]}
    res["gbf_C"] = {}
    for name, tt in pops.items():
        if len(tt) < 10:
            continue
        m = pc.trial.isin(tt).values
        res["gbf_C"][name] = gbf_block(pc.K.values[m], pc.C.values[m], sigma[m], Kmat[m], f"{model}:{name}:K vs C")
    # reference = judge (fully judged candidates only)
    jm = pc.J_full.values
    res["gbf_J"] = {}
    for name, tt in pops.items():
        m = pc.trial.isin(tt).values & jm
        if m.sum() >= 10:
            res["gbf_J"][name] = gbf_block(pc.K.values[m], pc.J.values[m], sigma[m], Kmat[m], f"{model}:{name}:K vs J")
            res["gbf_J"][name]["C_vs_J_self_check"] = G.gbf(pc.C.values[m], pc.J.values[m],
                                                            float(np.median(sigma[m]) * np.sqrt(2)))
    # drift-inflated sensitivity (upper bound)
    if drift_var is not None:
        s2 = np.sqrt(sigma ** 2 + drift_var)
        res["gbf_C_drift_inflated"] = {n: gbf_block(pc.K.values[pc.trial.isin(tt).values], pc.C.values[pc.trial.isin(tt).values],
                                                    s2[pc.trial.isin(tt).values], None, f"{model}:{n}:drift", with_placebos=False)
                                       for n, tt in pops.items() if len(tt) >= 10}
        res["drift_var"] = drift_var
    # incumbent's best shot
    shot = {}
    m = np.ones(len(pc), bool)
    shot["shipped"] = {"gbf_C_all": res["gbf_C"]["all"]["gbf"], "gbf_C_all_ci95": res["gbf_C"]["all"]["ci95"]}
    shot["repaired_list"] = gbf_block(pc.K_repaired.values, pc.C.values, pc.sigma_K_repaired.values, Krep,
                                      f"{model}:all:K_repaired vs C", with_placebos=False)
    if oracle:
        Kor = matrices(df, trials, "K_oracle")
        s_or = G.prompt_bootstrap_sd(Kor, B=B, seed=0)
        pc["sigma_K_oracle"] = s_or
        shot["oracle_threshold"] = {"oracle": oracle, **gbf_block(pc.K_oracle.values, pc.C.values, s_or, Kor,
                                                                  f"{model}:all:K_oracle vs C", with_placebos=False)}
    res["incumbent_best_shot"] = shot
    # per-candidate GBF (distribution, not only a scalar)
    tol = res["gbf_C"]["all"]["tol"]
    pc["gbf_i_C"] = G.per_candidate_gbf(pc.K.values, pc.C.values, tol)
    # conventional anchors vs the judge, per phase
    vc = {"keyword": "K", "classifier": "C", "keyword_repaired": "K_repaired"}
    if oracle:
        vc["keyword_oracle_t"] = "K_oracle"
    res["conventional"] = {name: conventional(df.assign(**({"K_oracle": df.K_oracle} if oracle else {})), pc, tt, vc)
                           for name, tt in pops.items()}
    return res, pc


def reselection(model: str, pc: pd.DataFrame) -> list[dict]:
    rows = []
    for scorer in ("K", "C", "J", "K_journal"):
        kl = "KL_journal" if scorer == "K_journal" else "KL_replay"
        d = pc[pc[scorer].notna() & pc[kl].notna()]
        if scorer == "J" and len(d) < len(pc):
            label = f"J (judged subset: {len(d)} of {len(pc)} candidates)"
        else:
            label = scorer
        if d.empty:
            continue
        sel = apply_rule([(int(r.trial), float(r[scorer]), float(r[kl])) for r in d.itertuples()])
        t = pc[pc.trial == sel["trial_number"]].iloc[0]
        rows.append({"model": model, "scorer": label, "kl_source": kl, "selected_trial": sel["trial_number"],
                     "branch": sel["rule_fired"], "n_candidates": sel["n_candidates"],
                     "K": t.K, "C": t.C, "J": t.J, "J_partial": t.get("J_partial"), "KL_replay": t.KL_replay,
                     "KL_journal": t.KL_journal, "direction_scope": t.direction_scope,
                     "sum_A1": t.get("sum_A1"), "sum_mass": t.get("sum_mass"), "sum_centroid": t.get("sum_centroid"),
                     "not_a_better_edit": P7_VERDICT})
    return rows


# ------------------------------------------------------------------ held-out-source sanity (Gemma, iteration 3)
def heldout_source() -> dict:
    import score
    Q = score.load_labels(A11 / "results/judge_out/eval_qwen.jsonl")
    out = {}
    recs = []
    for f in sorted((A11 / "results/eval_gen").glob("*.jsonl")):
        for r in read_jsonl(f):
            if r.get("set") != "S4hoc":
                continue
            k = f"{r['arm']}|{r['item_key']}"
            if k in Q and Q[k]["cls"] != "malformed":
                recs.append({"arm": r["arm"], "lang": r["lang"], "text": r["response_text"],
                             "y": int(Q[k]["cls"] in ("refused", "empty"))})
    if not recs:
        return {"n": 0}
    d = pd.DataFrame(recs)
    d["text100"] = score.truncate_tokens(d.text.tolist())
    kf = score.keyword_features(d.text100.tolist())
    d["K"] = kf.K.values
    _, d["C"] = score.clf_scores(d.text100.tolist())
    for (edited, lang), g in d.groupby([d.arm != "A_orig", "lang"]):
        out[f"{'edited' if edited else 'original'}_{lang}"] = {
            "n": int(len(g)), "base_rate_judge": float(g.y.mean()),
            "keyword_kappa": kappa_row(g.y, g.K.astype(int)), "classifier_kappa": kappa_row(g.y, g.C.astype(int)),
            "keyword_fp_share": float(((g.K == 1) & (g.y == 0)).sum() / max(g.K.sum(), 1))}
    out["source"] = ("art_0XmNBGkzsJc_ eval generations on S4 held-out-category StrongREJECT prompts (70 EN + 70 SL per "
                     "arm, Gemma arms), first 100 tokens, Qwen3-14B labels; keyword = Heretic _is_match")
    return out


# ------------------------------------------------------------------ rehearsal (T2/T3)
def rehearsal() -> dict:
    df = load_rows("gemma")
    res, pc = analyse_search("gemma", df, drift_var=None)
    cert = json.loads((WS / "scorer/certification.json").read_text())["certification_trials"]
    ed = df[df.trial >= 0]
    judged = ed[ed.J.notna()]
    chk = {
        "keyword_min_over_116": float(pc.K.min()), "keyword_max": float(pc.K.max()),
        "judged_range": [float(pc.J.min()), float(pc.J.max())],
        "keyword_kappa_all_rows": kappa_row(judged.J.astype(int), judged.K.astype(int)),
        "classifier_kappa_all_rows": kappa_row(judged.J.astype(int), judged.C.astype(int)),
        "mae_keyword_cert20": float((pc[pc.trial.isin(cert)].K - pc[pc.trial.isin(cert)].J_ref * 100 / pc[pc.trial.isin(cert)].J_n).abs().mean()),
        "mae_clf_cert20": float((pc[pc.trial.isin(cert)].C - pc[pc.trial.isin(cert)].J_ref * 100 / pc[pc.trial.isin(cert)].J_n).abs().mean()),
    }
    targets = {"keyword_min_over_116": 72, "judged_range": [7, 98], "keyword_kappa_all_rows": 0.196,
               "classifier_kappa_all_rows": 0.924, "mae_keyword_cert20": 30.6, "mae_clf_cert20": 2.1}
    ok = {"keyword_floor": abs(chk["keyword_min_over_116"] - 72) <= 1,
          "judged_range": abs(chk["judged_range"][0] - 7) <= 1 and abs(chk["judged_range"][1] - 98) <= 1,
          "keyword_kappa": abs(chk["keyword_kappa_all_rows"] - 0.196) < 0.01,
          "classifier_kappa": abs(chk["classifier_kappa_all_rows"] - 0.924) < 0.01,
          "mae_keyword": abs(chk["mae_keyword_cert20"] - 30.55) < 0.6,
          "mae_clf": abs(chk["mae_clf_cert20"] - 2.15) < 0.6}
    a = res["gbf_C"]["all"]
    plac = {"P_b_self_is_zero": a["P_b_self"]["gbf"] == 0.0,
            "P_c_split_half_small": a["P_c_split_half"]["mean"] < 0.5 * a["gbf"] if a["gbf"] > 0 else True,
            "P_a_chance_reported": a["P_a_permutation"]["chance_mean"] > 0}
    out = {"T2_reproduction": chk, "T2_targets_A11": targets, "T2_checks": ok, "T3_placebos": plac,
           "pass": all(ok.values()) and all(plac.values()),
           "summary": {"gemma_gbf_C_all": a["gbf"], "ci95": a["ci95"], "sigma_bar": a["sigma_bar"],
                       "startup_gbf_C": res["gbf_C"]["startup"]["gbf"], "RCR": a["RCR"], "FLOOR": a["FLOOR"],
                       "DEADBAND": a["DEADBAND"], "P_a_chance": a["P_a_permutation"]["chance_mean"],
                       "P_c_split_half": a["P_c_split_half"]["mean"], "gbf_J_all": res["gbf_J"]["all"]["gbf"]},
           "analysis": res}
    return out


# ------------------------------------------------------------------ full
def require_certifications() -> tuple[dict, dict]:
    p1, p2 = RESULTS / "gams_certification.json", RESULTS / "judge_certification.json"
    if not (p1.exists() and p2.exists()):
        raise SystemExit("T8: certification files missing - no GaMS3 blind-fraction number may be computed yet")
    c, j = json.loads(p1.read_text()), json.loads(p2.read_text())
    if "G3" not in c or "pass" not in c["G3"] or "gate" not in j:
        raise SystemExit("T8: certification files lack explicit verdicts")
    return c, j


def drift(model: str) -> dict:
    if model == "gemma":
        rf = json.loads((A11 / "results/replay_fidelity.json").read_text())
        return {"mean_abs_diff": None, "diff_sd": rf["keyword_diff_sd"], "diff_mean": rf["keyword_diff_mean"],
                "max_abs": rf["keyword_diff_max_abs"], "n": rf["n_draws"], "source": "art_0XmNBGkzsJc_ replay_fidelity.json"}
    rows = {r["trial"]: r for r in read_jsonl(RESULTS / "replay/gams_trials.jsonl")}
    d = np.array([r["keyword_refusals"] - r["journal_keyword_refusals"] for r in rows.values()], float)
    return {"mean_abs_diff": float(np.abs(d).mean()), "diff_sd": float(d.std(ddof=1)), "diff_mean": float(d.mean()),
            "max_abs": float(np.abs(d).max()), "n": int(len(d)), "exact_share": float(np.mean(d == 0)),
            "spearman_replay_vs_journal": float(spearmanr([r["keyword_refusals"] for r in rows.values()],
                                                          [r["journal_keyword_refusals"] for r in rows.values()]).statistic)}


def full() -> dict:
    cert, jcert = require_certifications()
    frozen = json.loads((CONFIGS / "frozen_predictions.json").read_text())
    desc = pd.read_csv(RESULTS / "candidate_descriptors.csv") if (RESULTS / "candidate_descriptors.csv").exists() else None
    out = {"frozen_prediction": frozen["prediction"], "gates": {"G3_classifier_on_gams": cert["G3"],
                                                                "judge_gate_gams": jcert["gate"]}}
    g3_pass = bool(cert["G3"]["pass"])
    judge_pass = jcert["gate"].get("pass")
    out["labels"] = {"gams_classifier_numbers": "CONFIRMATORY" if g3_pass else "EXPLORATORY (G3 failed)",
                     "judged_absolute_rates": "OK" if judge_pass else ("JUDGE_SENSITIVE" if judge_pass is False else "UNVERIFIED")}
    res, pcs, dfs = {}, {}, {}
    for model in ("gemma", "gams"):
        df = load_rows(model)
        dr = drift(model)
        dv = dr["diff_sd"] ** 2 if dr.get("diff_sd") is not None else None
        r, pc = analyse_search(model, df, drift_var=dv)
        r["replay_drift"] = dr
        pc = pc.merge(kl_table(model), on="trial", how="left")
        if desc is not None:
            pc = pc.merge(desc[desc.model == model].drop(columns=["model"]), on="trial", how="left")
        res[model], pcs[model], dfs[model] = r, pc, df
    out["searches"] = res
    # --- PAIRED HEADLINE: the 60 shared startup draws
    a, b = pcs["gemma"].set_index("trial"), pcs["gams"].set_index("trial")
    shared = [t for t in range(N_STARTUP) if t in a.index and t in b.index]
    sa, sb_ = a.loc[shared], b.loc[shared]
    tol_a = float(np.median(sa.sigma_K) * np.sqrt(2))
    tol_b = float(np.median(sb_.sigma_K) * np.sqrt(2))
    head = {"n_paired": len(shared), "reference": "C (certified classifier)",
            "gbf_gemma": G.gbf(sa.K.values, sa.C.values, tol_a), "gbf_gams": G.gbf(sb_.K.values, sb_.C.values, tol_b),
            "tol_gemma": tol_a, "tol_gams": tol_b,
            "paired_difference_gemma_minus_gams": G.paired_difference(sa.K.values, sa.C.values, tol_a,
                                                                      sb_.K.values, sb_.C.values, tol_b, B=B),
            "P_d_cross_search_swap": G.placebo_cross_search(sa.K.values, sa.C.values, tol_a, sb_.K.values, sb_.C.values, tol_b, B=B)}
    # drift-inflated (upper-bound) version of the paired difference
    dva, dvb = res["gemma"].get("drift_var") or 0.0, res["gams"].get("drift_var") or 0.0
    tol_a2 = float(np.median(np.sqrt(sa.sigma_K ** 2 + dva)) * np.sqrt(2))
    tol_b2 = float(np.median(np.sqrt(sb_.sigma_K ** 2 + dvb)) * np.sqrt(2))
    head["paired_difference_drift_inflated"] = G.paired_difference(sa.K.values, sa.C.values, tol_a2, sb_.K.values,
                                                                   sb_.C.values, tol_b2, B=B)
    head["paired_difference_drift_inflated"]["tols"] = [tol_a2, tol_b2]
    # common-tolerance sensitivity (removes the tol difference between searches as an explanation)
    tc = float(np.mean([tol_a, tol_b]))
    head["paired_difference_common_tol"] = G.paired_difference(sa.K.values, sa.C.values, tc, sb_.K.values, sb_.C.values, tc, B=B)
    head["paired_difference_common_tol"]["tol"] = tc
    d = head["paired_difference_gemma_minus_gams"]
    head["verdict_PRED_1"] = ("SUPPORTED" if d["ci95"][0] > 0 else "FALSIFIED (CI includes 0 or negative)")
    head["verdict_holds_under_drift_inflation"] = bool(head["paired_difference_drift_inflated"]["ci95"][0] > 0)
    head["classifier_status"] = out["labels"]["gams_classifier_numbers"]
    # judge-referenced paired version on draws judged in BOTH searches
    jj = [t for t in shared if bool(a.loc[t, "J_full"]) and bool(b.loc[t, "J_full"])]
    if len(jj) >= 10:
        ja, jb = a.loc[jj], b.loc[jj]
        head["judge_referenced_paired"] = {
            "n": len(jj), "trials": jj,
            "gbf_gemma": G.gbf(ja.K.values, ja.J.values, tol_a), "gbf_gams": G.gbf(jb.K.values, jb.J.values, tol_b),
            "paired_difference": G.paired_difference(ja.K.values, ja.J.values, tol_a, jb.K.values, jb.J.values, tol_b, B=B),
            "same_draws_C_reference": G.paired_difference(ja.K.values, ja.C.values, tol_a, jb.K.values, jb.C.values, tol_b, B=B)}
    else:
        head["judge_referenced_paired"] = {"n": len(jj), "note": "fewer than 10 startup draws judged in both searches"}
    # incumbent repairs on the paired draws
    for var, sig in (("K_repaired", "sigma_K_repaired"), ("K_oracle", "sigma_K_oracle")):
        if var in sa and var in sb_:
            ta, tb = float(np.median(sa[sig]) * np.sqrt(2)), float(np.median(sb_[sig]) * np.sqrt(2))
            head[f"paired_difference_{var}"] = G.paired_difference(sa[var].values, sa.C.values, ta, sb_[var].values,
                                                                   sb_.C.values, tb, B=B)
            head[f"paired_difference_{var}"]["gbf_gemma"] = G.gbf_value(sa[var].values, sa.C.values, ta)
            head[f"paired_difference_{var}"]["gbf_gams"] = G.gbf_value(sb_[var].values, sb_.C.values, tb)
    out["paired_headline"] = head
    # --- UNPAIRED 116 sensitivity
    ga, gb = res["gemma"]["gbf_C"]["all"], res["gams"]["gbf_C"]["all"]
    out["unpaired_all"] = G.unpaired_difference(pcs["gemma"].K.values, pcs["gemma"].C.values, ga["tol"],
                                                pcs["gams"].K.values, pcs["gams"].C.values, gb["tol"], B=B)
    out["unpaired_all"].update({"gbf_gemma": ga["gbf"], "gbf_gams": gb["gbf"]})
    # --- anchoring: GBF vs conventional quantities across (search x population x instrument) rows
    anc = []
    for model in ("gemma", "gams"):
        r = res[model]
        for pop in ("all", "startup", "tpe"):
            if pop not in r["gbf_C"]:
                continue
            conv = r["conventional"][pop]
            if "keyword" in conv:
                anc.append({"model": model, "pop": pop, "instrument": "keyword", "gbf": r["gbf_C"][pop]["gbf"],
                            "RCR": r["gbf_C"][pop]["RCR"], "kappa": conv["keyword"]["kappa"],
                            "mae": conv["keyword"]["mae_per100"], "fp_share": conv["keyword"]["fp_share"]})
        if "keyword_repaired" in r["conventional"]["all"]:
            anc.append({"model": model, "pop": "all", "instrument": "keyword_repaired",
                        "gbf": r["incumbent_best_shot"]["repaired_list"]["gbf"],
                        "RCR": r["incumbent_best_shot"]["repaired_list"]["RCR"],
                        "kappa": r["conventional"]["all"]["keyword_repaired"]["kappa"],
                        "mae": r["conventional"]["all"]["keyword_repaired"]["mae_per100"],
                        "fp_share": r["conventional"]["all"]["keyword_repaired"]["fp_share"]})
    an = pd.DataFrame(anc)
    out["anchoring"] = {"rows": anc, "note": "descriptive; few rows, not independent",
                        "spearman_gbf_vs": {k: float(spearmanr(an.gbf, an[k], nan_policy="omit").statistic)
                                            for k in ("kappa", "mae", "fp_share", "RCR")} if len(an) > 3 else None}
    out["heldout_source_sanity"] = heldout_source()
    # --- S7 reselection
    resel = []
    for model in ("gemma", "gams"):
        resel += reselection(model, pcs[model])
    pd.DataFrame(resel).to_csv(RESULTS / "reselection_table.csv", index=False)
    out["reselection"] = resel
    out["reselection_reading"] = mis_scoring(resel)
    # --- per-candidate deliverable
    pcat = []
    for model in ("gemma", "gams"):
        pc = pcs[model].copy()
        pc["run"] = "art_0XmNBGkzsJc_ replay" if model == "gemma" else "this artifact replay"
        pc["in_paired_60"] = pc.trial < N_STARTUP
        cset = set(json.loads((WS / "scorer/certification.json").read_text())["certification_trials"]) if model == "gemma" \
            else set(frozen["certification_trials_gams"]["trials"])
        pc["is_certification_trial"] = pc.trial.isin(cset)
        for r in resel:
            if r["model"] == model and r["kl_source"] == "KL_replay":
                col = {"K": "selected_by_K", "C": "selected_by_C"}.get(r["scorer"], "selected_by_J" if r["scorer"].startswith("J") else None)
                if col:
                    pc[col] = pc.trial == r["selected_trial"]
        pcat.append(pc)
    per = pd.concat(pcat, ignore_index=True)
    per.to_csv(RESULTS / "per_candidate.csv", index=False)
    # conventional table (flat)
    ct = []
    for model in ("gemma", "gams"):
        for pop, conv in res[model]["conventional"].items():
            for inst in ("keyword", "classifier", "keyword_repaired", "keyword_oracle_t"):
                if inst in conv:
                    ct.append({"model": model, "population": pop, "instrument": inst, **{k: v for k, v in conv[inst].items()
                                                                                         if not isinstance(v, list)},
                               "kappa_ci_lo": conv[inst]["kappa_ci95_trial_cluster"][0],
                               "kappa_ci_hi": conv[inst]["kappa_ci95_trial_cluster"][1],
                               "n_rows_judged": conv["n_rows_judged"], "n_trials_fully_judged": conv["n_trials_fully_judged"]})
    pd.DataFrame(ct).to_csv(RESULTS / "conventional_table.csv", index=False)
    # Rogan-Gladen twins for judged absolute rates if the judge gate was missed
    if jcert.get("Se_workhorse_vs_gpt41") is not None:
        se, sp = jcert["Se_workhorse_vs_gpt41"], jcert["Sp_workhorse_vs_gpt41"]
        from certify import rogan_gladen
        out["rogan_gladen_gams"] = {"Se": se, "Sp": sp, "applies": "judged refusal RATES (not the GBF difference)",
                                    "by_population": {p: {"raw": c.get("base_rate_judge"),
                                                          "corrected": rogan_gladen(c["base_rate_judge"], se, sp) if c.get("base_rate_judge") is not None else None}
                                                      for p, c in res["gams"]["conventional"].items()}}
    return out


def mis_scoring(resel: list[dict]) -> dict:
    out = {}
    for model in ("gemma", "gams"):
        rr = {r["scorer"]: r for r in resel if r["model"] == model and r["kl_source"] == "KL_replay"}
        k, c = rr.get("K"), rr.get("C")
        if not (k and c):
            continue
        out[model] = {"K_selected": k["selected_trial"], "K_branch": k["branch"], "C_selected": c["selected_trial"],
                      "C_branch": c["branch"], "same_trial": k["selected_trial"] == c["selected_trial"],
                      "C_count_at_K_selection": k["C"], "C_count_at_C_selection": c["C"],
                      "judged_at_K_selection": k["J"], "judged_at_C_selection": c["J"],
                      "reading": ("reselection INSIDE the same candidate pool changes the selected candidate -> the "
                                  "objective mis-scored candidates the search already held" if k["selected_trial"] != c["selected_trial"]
                                  else "same candidate under both scorers -> no mis-scoring at the point of selection")}
    return out


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rehearsal", action="store_true")
    a = ap.parse_args()
    setup_logging("analysis_rehearsal" if a.rehearsal else "analysis")
    if a.rehearsal:
        r = rehearsal()
        write_json(RESULTS / "rehearsal_gemma.json", r)
        logger.info(f"REHEARSAL pass={r['pass']} checks={r['T2_checks']} placebos={r['T3_placebos']}")
        logger.info(f"summary {r['summary']}")
        logger.info(f"reproduction {r['T2_reproduction']}")
        return
    out = full()
    write_json(RESULTS / "analysis.json", out)
    h = out["paired_headline"]
    logger.info(f"PAIRED: gemma {h['gbf_gemma']['gbf']:.3f} gams {h['gbf_gams']['gbf']:.3f} diff "
                f"{h['paired_difference_gemma_minus_gams']['diff']:.3f} {h['paired_difference_gemma_minus_gams']['ci95']} "
                f"-> {h['verdict_PRED_1']}")


if __name__ == "__main__":
    main()
