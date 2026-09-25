"""S3 (exp7 frozen predictions + slopes), S4 (exp8 F-block + cuts), S5 (exp4 extras), S6 (exp6/exp7 bounds), S7 (exp3 restoration),
plus exp5 T1 extras. Point estimates are recomputed from per-item/per-edit files where cheap; HistGBT gap CIs are SUMMARY_ONLY
(located by value in the artifact's summary JSON and cross-checked against its own rederive file)."""
from __future__ import annotations

import json
import math

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from lib import DS1, E3, E4, E5, E6, E7, E8, RES, SEED, Recorder, cluster_boot_mean, mcnemar_exact, read_json, read_jsonl, setup, write_json

R = Recorder("s3_s7_panels")


def locate(obj, target, tol, path="$"):
    """all json paths whose numeric value is within tol of target."""
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            hits += locate(v, target, tol, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:500]):
            hits += locate(v, target, tol, f"{path}[{i}]")
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool) and math.isfinite(obj):
        if abs(obj - target) <= tol:
            hits.append((path, obj))
    return hits


def summary_only(id, section, claim, draft, file, target, tol, note="", plan=None, unit="", key_hint=None):
    obj = read_json(file)
    hits = locate(obj, target, tol)
    if key_hint:
        hh = [h for h in hits if key_hint in h[0]]
        hits = hh or hits
    val = hits[0][1] if hits else None
    st = "SUMMARY_ONLY" if hits else "UNTRACEABLE"
    R.add(id, section, claim, None, draft=draft, summary=val, plan=plan, status=st, unit=unit, source_file=file,
          source_key=hits[0][0] if hits else None, method="located by value in artifact summary (not recomputed)",
          note=(note + ("" if hits else f"; no value within {tol} of {target} in the file")).strip("; "), paste=f"{val}" if val is not None else "")
    return val


# ------------------------------------------------------------------ S3 exp7
def exp7():
    sec = "Exp7 Gemma panel"
    fp = read_json(E7 / "protocol/frozen_predictions.json")
    an = read_json(E7 / "results/analysis.json")
    rd = read_json(E7 / "results/rederive.json")
    pred = fp["predictions"]
    V = an["verdicts"]
    quotes = {k: pred[k] for k in ("P-a", "P-b", "P-c", "P-d")}
    write_json(RES / "exp7_frozen_predictions_verbatim.json", {"source": str(E7 / "protocol/frozen_predictions.json"), "predictions": quotes,
                                                               "verdicts": V})
    R.add("exp7_Pa_definition", sec, "draft: 'P-a (Gap_R is small, <= 0.05): NOT CONFIRMED ... exceeded the pre-registered threshold of 0.05'",
          None, status="RECOMPUTED_MISMATCH", unit="text", source_file=E7 / "protocol/frozen_predictions.json", source_key="predictions.P-a",
          paste=f"P-a (frozen, verbatim): \"{pred['P-a']}\". Observed Gap_R1 = 0.054 [0.022, 0.128]: NOT CONFIRMED because the gap is SMALLER than 0.10.",
          note="the draft INVERTS the prediction: P-a predicted a LARGE gap (>= 0.10); it failed because the observed gap is small")
    R.recs[-1]["recomputed_value"] = pred["P-a"]
    R.recs[-1]["draft_value"] = "Gap_R is small, <= 0.05"
    R.add("exp7_Pd_definition", sec, "draft: 'P-d (matched-margin gap is small)'", None, status="MISDESCRIBED", unit="text",
          source_file=E7 / "protocol/frozen_predictions.json", source_key="predictions.P-d",
          paste=f"P-d (frozen): \"{pred['P-d']}\"; observed 0.057 [0.029, 0.130]: NOT CONFIRMED (gap small)",
          note="P-d also predicted a LARGE (>= 0.10) margin-matched gap; the draft states it as 'small'")
    g = V["P-a"]
    R.add("exp7_gap_R1", sec, "Gap_R1 = 0.054 [0.022, 0.128]", None, draft=0.054, summary=g["Gap_R"], plan=0.054, status="SUMMARY_ONLY", unit="R2* gap",
          ci=tuple(g["ci95"]), source_file=E7 / "results/analysis.json", source_key="verdicts.P-a",
          note=f"HistGBT two-level bootstrap not re-run (CPU budget); rederive.json independent polyOLS gap {rd['gap_independent']['R1']['Gap_R2star_polyOLS']:.3f}")
    R.add("exp7_placebo_share", sec, "label-swap placebo: share of swaps >= observed", None, summary=rd["gap_independent"]["placebo_lang_swap_frac_ge_observed"],
          plan=0.155, status="SUMMARY_ONLY", unit="share", source_file=E7 / "results/rederive.json", source_key="gap_independent.placebo_lang_swap_frac_ge_observed",
          note="15.5% of language-label swaps reach the observed gap: the R1 gap sits inside the placebo distribution")
    e6 = read_json(E6 / "results/analysis_results.json")
    R.add("exp6_gap_R1_beside", sec, "GaMS3 Gap_R1 (for R1-vs-R1 comparison)", None, summary=e6["gap"]["R1"]["Gap"], plan=0.042, status="SUMMARY_ONLY",
          ci=tuple(e6["bootstrap"]["R1"]["gap_ci95"]), unit="R2* gap", source_file=E6 / "results/analysis_results.json", source_key="gap.R1.Gap",
          note="Gemma R1 0.054 [0.022,0.128] vs GaMS3 R1 0.042 [0.027,0.070]: intervals overlap; the draft compared Gemma R1 with GaMS3 R (0.015)")
    R.add("exp7_vs_exp6_comparison", sec, "draft: 'Gemma surrogacy gap larger than GaMS3's (0.054 vs. 0.015 for R1)'", None, status="MISDESCRIBED",
          draft=0.015, summary=e6["gap"]["R"]["Gap"], unit="R2* gap", source_file=E6 / "results/analysis_results.json", source_key="gap.R.Gap",
          note="0.015 is GaMS3's Gap_R (R_seq), not R1; the like-for-like R1 values 0.054 vs 0.042 have overlapping CIs")
    # ---- slopes recomputed from per-edit rows (zero point: ORIG with the same trim AND device)
    items = read_jsonl(DS1 / "data/splits/S3_jbb.jsonl")
    half = {r["metadata_semantic_id"]: r["metadata_half"] for r in items}
    rows = [read_json(p) for p in sorted((E7 / "results/panel/edits").glob("*.json"))]
    origs = [r for r in rows if r["set"] == "ORIG"]
    eds = [r for r in rows if r["set"] in ("E0", "E1") and not r["collapsed"]]
    Bsid = sorted({s for s, h in half.items() if h == "B"})
    out = {}
    for trait in ("R1", "R_seq", "lp_ref", "lp_comp"):
        xs, ys = [], []
        keep = [s for s in Bsid if all(f"{s}|harmful|{lg}" in e["items"][trait] for e in eds for lg in ("en", "sl"))]
        for e in eds:
            base = [o for o in origs if o["trim"] == e["trim"] and o.get("device") == e.get("device")]
            b = base[-1]["items"][trait] if base else {}
            xs.append(np.mean([e["items"][trait][f"{s}|harmful|en"] - b.get(f"{s}|harmful|en", 0.0) for s in keep]))
            ys.append(np.mean([e["items"][trait][f"{s}|harmful|sl"] - b.get(f"{s}|harmful|sl", 0.0) for s in keep]))
        x, y = np.array(xs), np.array(ys)
        slope_int = float(np.polyfit(x, y, 1)[0])
        slope_0 = float((x * y).sum() / (x * x).sum())
        rng = np.random.default_rng(42)
        bs = [np.polyfit(x[i], y[i], 1)[0] for i in (rng.integers(0, len(x), len(x)) for _ in range(1000))]
        out[trait] = dict(n_edits=len(x), n_items=len(keep), slope_with_intercept=slope_int, slope_through_origin=slope_0,
                          ci95=[float(np.quantile(bs, .025)), float(np.quantile(bs, .975))])
    summ = {"R1": an["transfer_slope"]["R1"]["slope_SL_on_EN"], "R_seq": an["transfer_slope"]["R_seq"]["slope_SL_on_EN"],
            "lp_ref": an["R_seq_decomposition_halfB"]["component_harmful_lp_ref"]["slope_SL_on_EN"],
            "lp_comp": an["R_seq_decomposition_halfB"]["component_harmful_lp_comp"]["slope_SL_on_EN"]}
    draft = {"R1": 0.436, "R_seq": None, "lp_ref": None, "lp_comp": None}
    plan = {"R1": 0.436, "R_seq": 0.220, "lp_ref": 0.081, "lp_comp": 0.849}
    for t, o in out.items():
        R.add(f"exp7_slope_{t}", sec, f"SL-on-EN transfer slope {t}", o["slope_with_intercept"], draft=draft[t], summary=summ[t], plan=plan[t], kind="rate",
              draft_tol=0.002, ci=tuple(o["ci95"]), n=o["n_edits"], unit="slope", source_file=E7 / "results/panel/edits",
              source_key=f"items.{t} (half-B harmful, minus same-trim same-device ORIG)", method="OLS with intercept; edit bootstrap B=1000",
              note=f"through-origin slope {o['slope_through_origin']:.3f}; {o['n_items']} items")
    write_json(RES / "exp7_slopes_recomputed.json", out)
    # judge gating note: self-judge validated on originals only
    jl = read_json(E7 / "results/judge_local.json")["validation_vs_gpt41"]
    R.add("exp7_selfjudge_validation", sec, "exp7 validity judge = gemma-3-12b-it self-judge, agreement with gpt-4.1 on ORIGINAL generations only",
          None, summary=jl["agreement_refused_binary"], status="SUMMARY_ONLY", unit="binary agreement", n=jl["n"],
          source_file=E7 / "results/judge_local.json", source_key="validation_vs_gpt41",
          note=f"kappa 6-way {jl['kappa_6way']:.3f}, binary {jl['kappa_refused_binary']:.3f}; NO validation on edited outputs (SINGLE_JUDGE on edits)")


# ------------------------------------------------------------------ S6 exp6
def exp6():
    sec = "Exp6 GaMS3 panel"
    f = E6 / "results/analysis_results.json"
    a = read_json(f)
    for id, claim, draft, tgt, tol, hint, plan in [
        ("exp6_gapK", "Gap_K = 0.147 [0.074, 0.265]", 0.147, a["gap"]["K"]["Gap"], 1e-9, "gap.K", 0.147),
        ("exp6_gapR", "Gap_R = 0.015 [0.006, 0.031]", 0.015, a["gap"]["R"]["Gap"], 1e-9, "gap.R", None),
        ("exp6_BK", "B_K = 0.050 [0.001, 0.121]", 0.050, a["B_t"]["K"]["B"], 1e-9, "B_t.K", 0.050),
        ("exp6_gap_heretic_K", "Gap_Heretic_K (on journal trials)", None, a["gap_heretic"]["K"]["Gap_Heretic"], 1e-9, "gap_heretic", 0.018),
        ("exp6_ratio_K", "mean-change ratio SL/EN for K", None, a["transfer_slopes"]["K"]["ratio_mean_change_SL_over_EN_B"], 1e-9, "transfer_slopes", 0.59),
    ]:
        v = summary_only(id, sec, claim, draft, f, tgt, tol, plan=plan, unit="R2*/ratio", key_hint=hint)
        if id == "exp6_gapK":
            R.recs[-1]["ci_low"], R.recs[-1]["ci_high"] = a["bootstrap"]["K"]["gap_ci95"]
    rev = a["gap"]["K"]["reverse_SL_source"]
    rv = rev["R2s_plac"] - rev["R2s_test"] if "R2s_test" in rev else None
    R.add("exp6_reverse_gapK", sec, "reverse (SL-source) Gap_K", None, summary=rv, plan=-0.124, status="SUMMARY_ONLY", unit="R2* gap",
          source_file=f, source_key="gap.K.reverse_SL_source (R2s_plac - R2s_test)", method="difference of stored R2* values",
          note="negative: SL->EN prediction is easier than EN->SL; the KL gap is directional")
    rs = a["reselection"]
    R.add("exp6_reselection", sec, "bilingual reselection keeps trial 88 (SL_est 1.1)", None, summary=rs["selected"]["SL_est"], plan=1.1,
          status="SUMMARY_ONLY", unit="estimated SL refusals/100", source_file=f, source_key="reselection.selected", paste=f"{rs['selected_edit']}, SL_est {rs['selected']['SL_est']:.2f}")
    sc = a["source_carrier"]
    for t, pv in (("R", 0.009), ("K", 0.005)):
        if t in sc:
            v = sc[t]["SRC"]["dR2_C_given_S0_ridge"]
            R.add(f"exp6_srcnull_{t}", sec, f"frozen-residual-target source-layer carrier dR2 ({t})", None, summary=v, plan=pv, status="SUMMARY_ONLY",
                  ci=tuple(sc[t]["SRC"]["ci95_dR2_C_given_S0"]), unit="dR2", source_file=f, source_key=f"source_carrier.{t}.SRC.dR2_C_given_S0_ridge")
    # Spearman 0.77 recomputed from panel_edits.jsonl
    P = pd.DataFrame(read_jsonl(E6 / "results/panel_edits.jsonl"))
    P = P[(~P.collapsed.astype(bool)) & P.KL_en.notna() & P.KL_sl.notna()]
    P = P[(P.KL_en > 0) & (P.KL_sl > 0) & P.direction_index.notna()]
    lr = np.log(P.KL_sl.values / P.KL_en.values)
    rho = spearmanr(lr, P.direction_index.values).statistic
    R.add("exp6_srclayer_spearman", sec, "log(KL_SL/KL_EN) vs refusal-direction source layer: Spearman 0.77 (post-freeze)", float(rho), plan=0.77,
          kind="rate", draft_tol=0.01, n=len(P), unit="Spearman rho", source_file=E6 / "results/panel_edits.jsonl",
          source_key="KL_sl/KL_en vs direction_index", method="Spearman over non-collapsed panel edits (recomputed)", status="NEW",
          note="EXPLORATORY, chosen after seeing the data")
    rp = read_json(E6 / "results/repro_check.json")
    mx = max(v["max_abs"] for v in rp["edits"].values())
    R.add("exp6_repro_maxabs", sec, "draft: 'max |diff| up to 97.2' (cross-machine repro)", float(mx), draft=97.2, kind="rate", draft_tol=0.05,
          unit="raw residual-projection units (Hproj, layer 34; magnitude ~2000-3000)", source_file=E6 / "results/repro_check.json",
          source_key="edits.*.max_abs", status="MISDESCRIBED",
          note=("the 97.2 is a raw hidden-state projection (Hproj), not a behavioural or nats quantity; per-trait maxima: R_seq <= 0.041 (log-odds), "
                "K-KL <= 0.0021 (nats), FLORES NLL <= 0.12 (nats/token), R1 <= 0.25 (first-token log-odds)"))
    # judged gating
    jm = read_json(E6 / "results/judge_meta.json")
    R.add("exp6_judge_meta", sec, "exp6 judges: gpt-4.1 1,130 + Qwen3-14B 1,010, kappa .875", None, status="SUMMARY_ONLY",
          summary=next((v for p, v in locate(jm, 0.875, 0.001)), None), unit="kappa", source_file=E6 / "results/judge_meta.json",
          note="recomputed pooled binary kappa on the 1,130 overlap: see judge_agreement.csv (exp6 gpt41 vs qwen pooled_all)")


# ------------------------------------------------------------------ S7 exp3
def exp3():
    sec = "Exp3 A1 screen"
    J = read_json(E3 / "results/judged_generations.json")
    D = pd.DataFrame(J)
    D = D[D.kind == "jbb_harmful"]
    tab = D.assign(ref=D.judge_label == "refused").groupby(["model", "condition", "lang"]).ref.agg(["mean", "size"]).reset_index()
    tab.to_csv(RES / "exp3_judged_rates.csv", index=False)
    get = lambda m, c, l: float(tab[(tab.model == m) & (tab.condition == c) & (tab.lang == l)]["mean"].iloc[0])
    anchors = [("gams3", "C0", "en", .90), ("gams3", "C1", "en", .46), ("gams3", "C0", "sl", .93), ("gams3", "C1", "sl", .34),
               ("gemma", "C0", "en", .83), ("gemma", "C1", "en", .07), ("gemma", "C0", "sl", 1.00), ("gemma", "C1", "sl", .85)]
    for m, c, l, pv in anchors:
        draft = .99 if (m, c, l) == ("gemma", "C0", "en") else None
        R.add(f"exp3_{m}_{c}_{l}", sec, f"exp3 judged refusal {m} {c} {l.upper()}" + (" (draft: '99%')" if draft else ""), get(m, c, l), draft=draft,
              plan=pv, kind="rate", draft_tol=0.0055, n=int(tab[(tab.model == m) & (tab.condition == c) & (tab.lang == l)]["size"].iloc[0]),
              judge="gpt41", source_file=E3 / "results/judged_generations.json", source_key="judge_label (jbb_harmful)", method="proportion",
              note="C1 = d_EN ablation; C0 = no-op")
    # gaps (SL - EN change) with cluster bootstrap over semantic items
    for m, pv in (("gams3", -0.15), ("gemma", 0.77)):
        h = D[(D.model == m) & D.condition.isin(["C0", "C1"])]
        pv_ = h.pivot_table(index=["semantic_id"], columns=["condition", "lang"], values="judge_label", aggfunc="first").dropna()
        r = lambda c, l: (pv_[(c, l)] == "refused").values.astype(float)
        d = (r("C1", "sl") - r("C0", "sl")) - (r("C1", "en") - r("C0", "en"))
        lo, hi = cluster_boot_mean(d, np.arange(len(d)))
        R.add(f"exp3_gap_{m}", sec, f"exp3 {m} DiD (SL drop smaller than EN drop) under d_EN", float(d.mean()), plan=pv, kind="rate", draft_tol=0.01,
              ci=(lo, hi), n=len(d), judge="gpt41", source_file=E3 / "results/judged_generations.json", method="paired DiD over semantic items, B=2000",
              note="positive = Slovene refusal survives more than English")
    for m, pv in (("gams3", None), ("gemma", 0.77)):
        v = get(m, "C1", "sl") - get(m, "C1", "en")
        R.add(f"exp3_levelgap_{m}", sec, f"exp3 {m} post-ablation SL - EN refusal level (C1)", v, plan=pv, kind="rate", draft_tol=0.01, judge="gpt41",
              source_file=E3 / "results/judged_generations.json", note="level gap after d_EN ablation; the plan's Gemma '+0.77' is this quantity, its GaMS3 '-0.15' is the DiD")
    R.add("exp3_judge_provenance", sec, "draft: 'gpt-4.1 for 1,596 outputs ... and Qwen3-14B locally for the remainder'", None, status="MISDESCRIBED",
          summary=len(J), unit="labels", source_file=E3 / "results/judge_meta.json", paste="gpt-4.1 labelled all 1,596 judged outputs; no second judge",
          note="no Qwen labels exist in exp3 (judged_generations.json carries judge_label only); SINGLE_JUDGE")
    R.recs[-1]["recomputed_value"] = len(J)
    f = E3 / "results/analysis_summary.json"
    a = read_json(f)
    for id, claim, key, plan in [("exp3_rgate_gams_sp", "R-gate GaMS3 condition-level Spearman .51 (gate FAILS)", "validity.gams3.spearman_condition_level", .51),
                                 ("exp3_rgate_gams_auc", "R-gate GaMS3 item AUROC .70", "validity.gams3.item_auroc", .70),
                                 ("exp3_rgate_gemma_sp", "R-gate Gemma Spearman .91", "validity.gemma.spearman_condition_level", .91)]:
        summary_key(id, sec, claim, f, a, key, plan)
    for m, pv in (("gams3", .11), ("gemma", .23)):
        hb = read_json(E3 / f"results/{m}/heretic_bridge.json")
        summary_key(f"exp3_bridge_{m}", sec, f"Heretic bridge mean gap {m} {pv}", E3 / f"results/{m}/heretic_bridge.json", hb, "mean_gap", pv,
                    ci_key="mean_gap_ci95")
    mf = E3 / "results/margin_decomposition_exploratory.json"
    mm = read_json(mf)
    for id, claim, key, plan in [("exp3_margin_sl", "margin decomposition: Gemma SL baseline R 13.9", "gemma.sl.mean_R0", 13.9),
                                 ("exp3_margin_en", "Gemma EN baseline R 3.6", "gemma.en.mean_R0", 3.6),
                                 ("exp3_benign_sl_twins", "69% of benign SL twins refused (Gemma)", "gemma.sl.benign_C0_judged_refusal", .69)]:
        summary_key(id, sec, claim, mf, mm, key, plan)
    vn = read_json(E3 / "results/verify_numbers.json")
    hits = [h for h in locate(vn, 3.47, 0.006) if "T_en->sl" in h[0]]
    R.add("exp3_T", sec, "transfer ratio T(en->sl) 3.47 (Gemma)", None, summary=hits[0][1] if hits else None, plan=3.47, status="SUMMARY_ONLY" if hits else "UNTRACEABLE",
          source_file=E3 / "results/verify_numbers.json", source_key=hits[0][0] if hits else None, unit="ratio")
    cv = a.get("cos_vs_transfer", {})
    R.add("exp3_cos", sec, "cos(d_EN, d_SL) .92 (Gemma, selected site)", None, status="SUMMARY_ONLY", plan=.92,
          summary=getk(read_json(E8 / "results/analysis_summary.json"), "transfer_predictors.cos_dEN_dSL"), unit="cosine",
          source_file=E8 / "results/analysis_summary.json", source_key="transfer_predictors.cos_dEN_dSL",
          note="Gemma cos(d_EN,d_SL) at L20 as stored in exp8; exp3 stores per-layer raw/corrected cosines under cos_vs_transfer")


def getk(obj, key):
    """value at a dotted key path; if the path is not rooted, the first nested occurrence whose path ENDS with it."""
    parts = key.split(".")
    def rec(o, path):
        if path[-len(parts):] == parts:
            return o, True
        if isinstance(o, dict):
            for k, v in o.items():
                r, ok = rec(v, path + [k])
                if ok:
                    return r, True
        return None, False
    v, ok = rec(obj, [])
    if not ok:
        raise KeyError(key)
    return v


def summary_key(id, section, claim, file, obj, key, plan=None, draft=None, ci_key=None, unit=""):
    try:
        v = getk(obj, key)
        ci = tuple(getk(obj, ci_key)) if ci_key else None
        R.add(id, section, claim, None, draft=draft, summary=v, plan=plan, status="SUMMARY_ONLY", ci=ci, unit=unit, source_file=file, source_key=key,
              method="read from artifact summary by key (not recomputed)")
    except (KeyError, TypeError) as e:
        R.add(id, section, claim, None, draft=draft, plan=plan, status="UNTRACEABLE", source_file=file, source_key=key, note=f"key missing: {e}")


# ------------------------------------------------------------------ S4 exp8 frozen block
def exp8():
    sec = "Exp8 causal test"
    L = pd.read_parquet(RES / "labels_long.parquet")
    X = L[(L.artifact == "exp8") & (L.judge == "gpt41")].dropna(subset=["label"])
    def arm(a, lang, ds):
        g = X[(X.cell == f"gemma:{a}") & (X.lang == lang) & X.dataset.isin(ds)]
        return g.set_index("item").label
    JH = ["jbb_harmful", "hoc_harmful"]
    a1 = arm("A1", "sl", JH)
    cuts = {}
    for a in ("A2", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A2d_c0.5"):
        b = arm(a, "sl", JH)
        ov = sorted(set(a1.index) & set(b.index))
        if len(ov) < 3:
            continue
        x = (a1.loc[ov] == "REFUSED").values.astype(float)
        y = (b.loc[ov] == "REFUSED").values.astype(float)
        d = x - y
        lo, hi = cluster_boot_mean(d, np.arange(len(d)))
        cuts[a] = (float(d.mean()), lo, hi, len(ov))
    plan = {"A2": 0.036, "A6": 0.324, "A9": 0.074, "A10": 0.135}
    draft = {"A2": 0.036}
    for a, (v, lo, hi, n) in cuts.items():
        R.add(f"exp8_cut_{a}", sec, f"SL harmful refusal cut vs A1 for {a} (gpt-4.1, paired items)", v, draft=draft.get(a), plan=plan.get(a), kind="rate",
              draft_tol=0.0055, ci=(lo, hi), n=n, judge="gpt41", source_file=E8 / "results/per_item.parquet", source_key="judge_label", method="paired difference A1 - arm")
    # F3 over-refusal McNemar (A0 vs A3, SL harmless)
    HH = ["jbb_benign", "hoc_harmless", "jbb_harmless"]
    a0, a3 = arm("A0", "sl", HH), arm("A3", "sl", HH)
    ov = sorted(set(a0.index) & set(a3.index))
    mc = mcnemar_exact((a0.loc[ov] == "REFUSED").values, (a3.loc[ov] == "REFUSED").values)
    R.add("exp8_F3_p", sec, "F3 McNemar raw p (A0 vs A3 SL over-refusal)", mc["p_exact"], plan=0.00635, kind="p", n=len(ov), unit="p",
          source_file=E8 / "results/per_item.parquet", method=f"exact McNemar n10={mc['n10_a1_b0']} n01={mc['n01_a0_b1']}", status="NEW")
    R.add("exp8_F3_holm", sec, "F3 Holm-adjusted p 0.025", min(1.0, mc["p_exact"] * 4), plan=0.025, kind="p", unit="p (Holm, family of 4; smallest raw p x4)",
          source_file=E8 / "results/per_item.parquet", status="NEW", note="F3 FAILS its frozen criterion despite p=.025 (relative drop CI/EN-harm condition)")
    s = read_json(E8 / "results/analysis_summary.json")
    summary_key("exp8_auroc_cos", sec, "item-level cosine-transfer AUROC 0.240", E8 / "results/analysis_summary.json", s,
                "transfer_predictors.cosine_baseline.auroc", 0.240)
    ah = read_json(E8 / "results/audit_headline.json")
    summary_key("exp8_rprior_cos_lang", sec, "r_prior cos with the language axis 0.65", E8 / "results/audit_headline.json", ah, "geometry.cos_rprior_l", 0.65)
    summary_key("exp8_rprior_cos_shuf", sec, "r_prior cos with its shuffled twin 0.89", E8 / "results/audit_headline.json", ah, "geometry.cos_rprior_shuffled", 0.89)


# ------------------------------------------------------------------ S5 exp4 extras + exp5 extras
def exp4_exp5():
    sec = "Exp4 RefusEU"
    O = pd.read_csv(RES / "exp4_official_asr.csv")
    for lg, pv in (("en", .738), ("sl", .103)):
        r = O[(O.cell == "gemma_edit") & (O.lang == lg)].iloc[0]
        R.add(f"exp4_official_asr_gemma_edit_{lg}", sec, f"official-guard ASR gemma_edit {lg.upper()}", float(r.asr), plan=pv, kind="rate",
              ci=(r.wilson_lo, r.wilson_hi), n=int(r.n), judge="official RefusEU guard (harmfulness)", source_file=E4 / "results/guard/official_labels.jsonl",
              source_key="official_unsafe (S5; unadjudicated disagreements excluded)", method="proportion", status="NEW")
    A = pd.read_csv(RES / "judge_agreement.csv")
    q = A[(A.artifact == "exp4") & (A.judge_a == "gpt41") & (A.judge_b == "qwen3_14b")]
    for defn, dv in (("binary", 0.91), ("4class", 0.83)):
        allk = q[(q.scope == "pooled_all") & (q.definition == defn)].iloc[0]
        ed = q[(q.scope == "pooled_edited") & (q.definition == defn)].iloc[0]
        R.add(f"exp4_kappa_pooled_{defn}", sec, f"Qwen vs gpt-4.1 kappa ({defn}) '0.83 6-way / 0.91 refused-vs-not'", float(allk.kappa), draft=dv, kind="rate",
              draft_tol=0.006, ci=(allk.kappa_ci_low, allk.kappa_ci_high), n=int(allk.n), judge="gpt41 vs qwen3_14b", source_file=E4 / "results/judge",
              method="Cohen kappa on the item overlap (all checkpoints pooled)", note="pooled over originals + edits (inflated; see edited-only)")
        R.add(f"exp4_kappa_edited_{defn}", sec, f"Qwen vs gpt-4.1 kappa ({defn}) within EDITED checkpoints only", float(ed.kappa), kind="rate",
              ci=(ed.kappa_ci_low, ed.kappa_ci_high), n=int(ed.n), judge="gpt41 vs qwen3_14b", source_file=E4 / "results/judge", status="NEW",
              note=f"kappa inflation (pooled-all minus edited-only) = {allk.kappa - ed.kappa:.3f}; AC1 edited {ed.ac1:.3f}")
    R.add("exp4_judge_provenance", sec, "draft: 'tested on a calibration set before deployment'", None, status="MISDESCRIBED", unit="text",
          source_file=E4 / "results/judge_local_cert.json",
          paste=("Qwen3-14B was a post-hoc substitute under fallback F1 after gpt-4.1 was budget-blocked at 716/3,840 core items; it was validated "
                 "against those 716 gpt-4.1 labels (kappa .83 4-class / .91 refused-vs-not, pooled over originals and edits; .73 / .78 within edits)"))
    for f, nm in ((E4 / "results/judge_blocked.json", "judge_blocked"), (E4 / "results/judge_local_cert.json", "judge_local_cert")):
        if f.exists():
            R.recs[-1]["correction_note"] += f"; {nm}: {json.dumps(read_json(f))[:220]}"
    rs = E4 / "results/rseq/rseq_validity.json"
    if rs.exists():
        hits = [h for h in locate(read_json(rs), 0.245, 0.09) if "within" in h[0].lower() or "edit" in h[0].lower()]
        R.add("exp4_rseq_within_edit", sec, "R_seq within-edit Spearman (.16-.33) vs pooled (.84-.86)", None, status="SUMMARY_ONLY",
              summary=hits[0][1] if hits else None, source_file=rs, source_key=hits[0][0] if hits else None, unit="Spearman",
              note="; ".join(f"{p}={v:.3f}" for p, v in hits[:6]))
    sm = sorted((E4 / "results/smoke").glob("*.json"))
    notes = []
    for f in sm:
        d = read_json(f)
        b3 = {k: v for k, v in d.items() if "b3" in k.lower() or "batch" in k.lower()}
        notes.append(f"{f.name}: {json.dumps(b3)[:200]}")
    R.add("exp4_B3_batching", sec, "B3 batching certification (smoke)", None, status="SUMMARY_ONLY", unit="text", source_file=E4 / "results/smoke",
          note=" | ".join(notes))
    # S5X anchors (Qwen) re-derived in gap_range.csv
    G = pd.read_csv(RES / "gap_range.csv")
    def g(ck, j, d, col="gap"):
        r = G[(G.checkpoint == ck) & (G.dataset.str.startswith("exp4 S5X")) & (G.judge == j) & (G.definition == d)]
        return r.iloc[0] if len(r) else None
    r = g("gemma_edit", "qwen3_14b", "strict")
    R.add("exp4_s5x_gap_gemma", sec, "S5X paired gap gemma_edit +0.69 [0.60, 0.78]", float(r.gap), draft=0.69, plan=0.69, kind="rate", draft_tol=0.0055,
          ci=(r.ci_low, r.ci_high), n=int(r.n_pairs), judge="qwen3_14b", source_file=E4 / "frozen_samples.json", source_key="s5x_pairs x judge_local",
          method=f"paired; exact McNemar p={r.mcnemar_p:.2e}", note="STRICT definition; BROAD (refused+partial) gap is much smaller (see gap_range)")
    R.add("exp4_s5x_mcnemar", sec, "S5X McNemar p 3.4e-21", float(r.mcnemar_p), plan=3.4e-21, kind="p", unit="p", judge="qwen3_14b",
          source_file=E4 / "frozen_samples.json", status="NEW")
    R.add("exp4_s5x_did_gemma", sec, "S5X DiD +0.66 [0.55, 0.76]", float(r.did), draft=0.66, plan=0.66, kind="rate", draft_tol=0.0055,
          ci=(r.did_ci_low, r.did_ci_high), n=int(r.did_n), judge="qwen3_14b", source_file=E4 / "frozen_samples.json")
    rb = g("gemma_edit", "qwen3_14b", "broad")
    R.add("exp4_s5x_gap_gemma_broad", sec, "S5X paired gap gemma_edit, BROAD (refused+partial)", float(rb.gap), kind="rate", ci=(rb.ci_low, rb.ci_high),
          n=int(rb.n_pairs), judge="qwen3_14b", source_file=E4 / "frozen_samples.json", status="NEW",
          note="the strict +0.69 gap shrinks to this when PARTIAL counts as refusal: most EN 'non-refusals' are hedged partial answers")
    rc = g("community_ref", "qwen3_14b", "strict")
    R.add("exp4_s5x_gap_community", sec, "community gap +0.12 [0.05, 0.20]", float(rc.gap), draft=0.12, plan=0.12, kind="rate", draft_tol=0.0055,
          ci=(rc.ci_low, rc.ci_high), n=int(rc.n_pairs), judge="qwen3_14b", source_file=E4 / "frozen_samples.json")
    # 2.6x ratio
    C = pd.read_csv(RES / "claims_registry.csv").set_index("id")
    ratio = C.loc["exp4_gemma_edit_S5_sl", "recomputed"] / C.loc["exp4_gemma_edit_S5_en", "recomputed"]
    R.add("exp4_ratio_26", sec, "residual SL refusal 2.6x residual EN (0.739/0.287)", float(ratio), draft=2.6, kind="ratio", draft_tol=0.05,
          unit="ratio", judge="qwen3_14b", source_file=E4 / "results/judge_local", note="judge-sensitive: EN S5 under gpt-4.1 subset is lower")
    R.add("exp4_invalid_zero", sec, "Invalid rate 0.000 across all cells", float(pd.read_csv(RES / "judge_sensitivity.csv").query(
        "artifact=='exp4' and judge=='qwen3_14b' and dataset=='S5'").p_invalid.max()), draft=0.0, kind="rate", judge="qwen3_14b",
        source_file=E4 / "results/judge_local", method="max over S5 cells")
    # ------------- exp5 T1 extras
    sec = "Exp5 T1"
    J = pd.read_csv(RES / "judge_sensitivity.csv")
    t1 = J[(J.artifact == "exp5") & (J.dataset == "s4_harmful") & (J.judge == "gpt41")]
    gap = float(t1[(t1.cell == "gemma:edit") & (t1.lang == "sl")].p_refused.iloc[0] - t1[(t1.cell == "gemma:edit") & (t1.lang == "en")].p_refused.iloc[0])
    R.add("exp5_T1_gap25", sec, "25-percentage-point gap (70.3% vs 95.3%)", gap, draft=0.25, kind="rate", draft_tol=0.0055, judge="gpt41",
          source_file=E5 / "results/judged_generations.jsonl")
    A5 = A[(A.artifact == "exp5") & (A.judge_a == "gpt41") & (A.judge_b == "nemotron") & (A.scope == "pooled_all")]
    for defn, dv, col in (("4class", 0.765, "kappa"), ("binary", 0.828, "kappa"), ("4class", 0.885, "raw_agreement")):
        r = A5[A5.definition == defn].iloc[0]
        R.add(f"exp5_agree_{defn}_{col}", sec, f"second judge vs gpt-4.1 on 200: {col} {dv}", float(r[col]), draft=dv, kind="rate", draft_tol=0.0015,
              n=int(r.n), judge="gpt41 vs nemotron", source_file=E5 / "results/judged_generations.jsonl", method="pooled over originals + edits",
              note="raw agreement .885 is the 4-class agreement (binary raw agreement is .920)" if col == "raw_agreement" else "")
    cov = J[(J.artifact == "exp5") & (J.dataset == "s4_harmful") & (J.judge == "gpt41")]
    D5 = read_jsonl(E5 / "results/judged_generations.jsonl")
    pr = pd.DataFrame(D5)
    pr = pr[pr.kind == "s4_harmful"]
    by = pr.assign(j=pr.label != "NOT_JUDGED").groupby("priority").j.mean().to_dict()
    R.add("exp5_T1_provenance", sec, "draft: 'gpt-4.1 judge labelled a random ~52% subsample; remaining items used ... Nemotron'", float(pr.assign(
        j=pr.label != "NOT_JUDGED").j.mean()), draft=0.52, kind="rate", draft_tol=0.02, unit="share of S4 harmful gpt-4.1-labelled",
        source_file=E5 / "results/judged_generations.jsonl", status="MISDESCRIBED",
        note=(f"coverage by priority tier {({k: round(v, 3) for k, v in by.items()})}: the subset is PRIORITY-ORDERED, not a random draw; and the T1 "
              "rates use gpt-4.1 labels ONLY (n=118-150 per cell), not a gpt-4.1 + Nemotron mixture"))


def main():
    setup("s05_panels")
    for f in (exp7, exp6, exp3, exp8, exp4_exp5):
        try:
            f()
        except Exception as e:  # keep going; the failure is logged and reported
            from loguru import logger
            logger.exception(f"{f.__name__} failed: {e}")
            R.add(f"{f.__name__}_FAILED", f.__name__, "step failed", None, status="UNTRACEABLE", note=repr(e))
    R.save()


if __name__ == "__main__":
    main()
