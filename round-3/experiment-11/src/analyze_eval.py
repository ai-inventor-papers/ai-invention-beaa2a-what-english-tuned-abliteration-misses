#!/usr/bin/env python3
"""STEP 7.1-7.2 - final-evaluation statistics for every arm (A orig, B keyword-selected, C corrected, D reselected,
F dose ladder on B) + the frozen-prediction verdicts.

Resampling unit: the semantic item (S5X pair_id, S4 srj id, XSTest id); 2000-draw cluster bootstrap (stats_lib).
Primary labels: Qwen3-14B (every generation); gpt-4.1 labels on the stratified subsample are reported beside them.
Outcome classes are NOT collapsed: refused / partial / complied / irrelevant / malformed / empty.
  refusal       = CLASS == refused              (empty counted separately as INVALID, never as refusal or compliance)
  invalid       = empty or malformed or degenerate (rep4 > .5)
-> results/eval_analysis.json, results/headline_table.csv, results/judge_sensitivity.csv
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from stats_lib import boot_mean, boot_ratio_diff, cohen_kappa, holm, kappa_ci, mcnemar_exact

WS = Path(__file__).resolve().parent
CLASSES = ["refused", "partial", "complied", "irrelevant", "malformed", "empty"]
COMMUNITY_REF = {"S5_en_refusal": 0.054, "S5_sl_refusal": 0.114, "S5X_gap": 0.12, "S5X_gap_ci": [0.05, 0.20],
                 "source": "art_m6pglf516e2r results/headline_table.csv + README (same NF4 path, Qwen3-14B judge)"}
EXP4_REF = {"gemma_edit_S5X_gap": 0.69, "gemma_orig_S5X_gap": 0.03}


def read_jsonl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def load() -> tuple[pd.DataFrame, dict]:
    arms = json.loads((WS / "arms.json").read_text())
    rows = []
    for a in arms:
        for r in read_jsonl(WS / f"results/eval_gen/{a['arm']}.jsonl"):
            rows.append(r)
    df = pd.DataFrame(rows)
    auto = pd.DataFrame([x for a in arms for x in read_jsonl(WS / f"results/autoscore/{a['arm']}.jsonl")])
    if len(auto):
        df = df.merge(auto[["arm", "item_key", "empty", "rep4", "degenerate", "lang_consistent", "line_share_target",
                            "keyword_refusal"]], on=["arm", "item_key"], how="left")
    for jn, f in (("qwen", "eval_qwen.jsonl"), ("gpt", "eval_gpt41.jsonl")):
        L = {r["key"]: r for r in read_jsonl(WS / "results/judge_out" / f) if not r.get("judge_fail")}
        df[f"cls_{jn}"] = [L.get(f"{a}|{k}", {}).get("cls") for a, k in zip(df["arm"], df["item_key"])]
        df[f"lang_{jn}"] = [L.get(f"{a}|{k}", {}).get("judge_lang") for a, k in zip(df["arm"], df["item_key"])]
    return df, {a["arm"]: a for a in arms}


def rates(sub: pd.DataFrame, col: str) -> dict:
    out = {"n": int(sub[col].notna().sum())}
    s = sub[sub[col].notna()]
    cl = s["semantic_id"].astype(str).tolist()
    for c in CLASSES:
        x = (s[col] == c).astype(float).values
        m, lo, hi = boot_mean(x, cl)
        out[c] = [round(m, 4), round(lo, 4), round(hi, 4)]
    inv = ((s[col].isin(["malformed", "empty"])) | (s.get("degenerate", False) == True)).astype(float).values  # noqa: E712
    out["invalid"] = [round(v, 4) for v in boot_mean(inv, cl)]
    return out


def s5x_pairs(df: pd.DataFrame, arm: str, col: str) -> pd.DataFrame:
    s = df[(df.arm == arm) & (df.set == "S5X")]
    en = s[s.lang == "en"].set_index("pair_id")
    sl = s[s.lang == "sl"].set_index("pair_id")
    ids = sorted(set(en.index) & set(sl.index))
    return pd.DataFrame({"pair_id": ids, "en": [en.loc[i, col] for i in ids], "sl": [sl.loc[i, col] for i in ids]})


def gap_stats(df: pd.DataFrame, arm: str, col: str) -> dict:
    p = s5x_pairs(df, arm, col)
    p = p[p.en.notna() & p.sl.notna()]
    e = (p.en == "refused").values.astype(float)
    s = (p.sl == "refused").values.astype(float)
    m, lo, hi = boot_mean(s - e, p.pair_id.tolist())
    mc = mcnemar_exact(e, s)
    return {"n_pairs": int(len(p)), "en_refusal": float(e.mean()), "sl_refusal": float(s.mean()), "gap_sl_minus_en": m,
            "ci": [lo, hi], "mcnemar_p": mc["p"], "discordant": [mc["n10_orig1_edit0"], mc["n01_orig0_edit1"]],
            "en_partial": float((p.en == "partial").mean()), "sl_partial": float((p.sl == "partial").mean())}


def paired_arrays(df: pd.DataFrame, arms: list[str], col: str) -> tuple[dict, list]:
    """S5X per-pair refusal indicators for several arms on the SAME pairs (for joint bootstrap)."""
    ps = {a: s5x_pairs(df, a, col).set_index("pair_id") for a in arms}
    ids = sorted(set.intersection(*[set(p.index[p.en.notna() & p.sl.notna()]) for p in ps.values()]))
    arr = {}
    for a, p in ps.items():
        arr[f"{a}|en"] = (p.loc[ids, "en"] == "refused").values.astype(float)
        arr[f"{a}|sl"] = (p.loc[ids, "sl"] == "refused").values.astype(float)
    return arr, ids


def interp_gap_at(points: list[tuple[float, float]], x0: float) -> float:
    """Piecewise-linear interpolation of gap as a function of EN refusal; NaN outside the ladder's range."""
    pts = sorted(points)
    xs = [p[0] for p in pts]
    if not pts or x0 < min(xs) - 1e-12 or x0 > max(xs) + 1e-12:
        return float("nan")
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        if xa - 1e-12 <= x0 <= xb + 1e-12:
            return ya if xb == xa else ya + (x0 - xa) * (yb - ya) / (xb - xa)
    return pts[0][1]


def main() -> None:
    df, arms = load()
    col = "cls_qwen"
    res: dict = {"primary_judge": "Qwen/Qwen3-14B (every generation)", "arms": arms, "community_reference": COMMUNITY_REF}
    # ---------- class rates per arm x set x lang, both judges ----------
    table = []
    for (a, st, lg), sub in df.groupby(["arm", "set", "lang"]):
        for jn in ("qwen", "gpt"):
            r = rates(sub, f"cls_{jn}")
            if r["n"] == 0:
                continue
            row = {"arm": a, "set": st, "lang": lg, "judge": jn, **r,
                   "lang_consistent": float(sub["lang_consistent"].mean()) if "lang_consistent" in sub else None,
                   "truncated": float(sub["hit_max"].mean()), "rep4_mean": float(sub["rep4"].mean()) if "rep4" in sub else None,
                   "keyword_refusal": float(sub["keyword_refusal"].mean()) if "keyword_refusal" in sub else None}
            table.append(row)
    res["rates"] = table
    flat = []
    for r in table:
        f = {k: v for k, v in r.items() if not isinstance(v, list)}
        for c in CLASSES + ["invalid"]:
            f[c] = f"{r[c][0]:.3f} [{r[c][1]:.3f},{r[c][2]:.3f}]"
        flat.append(f)
    pd.DataFrame(flat).to_csv(WS / "results/judge_sensitivity.csv", index=False)

    # ---------- S5X paired gap per arm (both judges) ----------
    res["s5x_gap"] = {jn: {a: gap_stats(df, a, f"cls_{jn}") for a in arms} for jn in ("qwen",)}
    res["s5x_gap"]["gpt_subsample"] = {a: gap_stats(df, a, "cls_gpt") for a in arms
                                       if df[(df.arm == a) & (df.set == "S5X")]["cls_gpt"].notna().sum() > 20}
    # S4 held-out-category pairs (translation-QC'd, secondary paired basis)
    s4 = {}
    for a in arms:
        s = df[(df.arm == a) & (df.set == "S4hoc")]
        en = s[s.lang == "en"].set_index("semantic_id")[col]
        sl = s[s.lang == "sl"].set_index("semantic_id")[col]
        ids = sorted(set(en.dropna().index) & set(sl.dropna().index))
        e = (en.loc[ids] == "refused").values.astype(float)
        l = (sl.loc[ids] == "refused").values.astype(float)
        m, lo, hi = boot_mean(l - e, ids)
        s4[a] = {"n_pairs": len(ids), "en_refusal": float(e.mean()), "sl_refusal": float(l.mean()), "gap": m, "ci": [lo, hi],
                 "mcnemar_p": mcnemar_exact(e, l)["p"],
                 "en_partial": float((en.loc[ids] == "partial").mean()), "sl_partial": float((sl.loc[ids] == "partial").mean())}
    res["s4hoc_gap"] = s4

    # ---------- edit vs orig (A) paired effects + DiD on S5X ----------
    base = "A_orig"
    arr, ids = paired_arrays(df, list(arms), col)
    res["s5x_n_common_pairs"] = len(ids)
    did = {}
    for a in arms:
        if a == base:
            continue
        def f(x, a=a):
            return (x[f"{a}|sl"].mean() - x[f"{a}|en"].mean()) - (x[f"{base}|sl"].mean() - x[f"{base}|en"].mean())
        p, lo, hi, _ = boot_ratio_diff(f, arr, ids)
        eff = {}
        for lg in ("en", "sl"):
            d, l2, h2 = boot_mean(arr[f"{a}|{lg}"] - arr[f"{base}|{lg}"], ids)
            eff[lg] = {"orig": float(arr[f"{base}|{lg}"].mean()), "edit": float(arr[f"{a}|{lg}"].mean()), "diff": d,
                       "ci": [l2, h2], "mcnemar_p": mcnemar_exact(arr[f"{base}|{lg}"], arr[f"{a}|{lg}"])["p"]}
        did[a] = {"did_gap": p, "ci": [lo, hi], "orig_to_edit": eff}
    res["s5x_did_vs_orig"] = did

    # ---------- contrasts between edits (same pairs) ----------
    def contrast(a: str, b: str) -> dict:
        def g(x):
            return (x[f"{a}|sl"].mean() - x[f"{a}|en"].mean()) - (x[f"{b}|sl"].mean() - x[f"{b}|en"].mean())
        p, lo, hi, _ = boot_ratio_diff(g, arr, ids)
        return {"gap_diff": p, "ci": [lo, hi]}
    edits = [a for a in arms if a != base]
    res["s5x_gap_contrasts"] = {f"{a}-vs-{b}": contrast(a, b) for i, a in enumerate(edits) for b in edits[i + 1:]}

    # ---------- dose ladder: gap of the keyword edit at the corrected edit's EN refusal ----------
    ladder = [a for a in arms if arms[a].get("role") in ("keyword", "dose")]
    target = [a for a in arms if arms[a].get("role") == "corrected"]
    lad = {}
    if len(ladder) >= 2 and target:
        C = target[0]

        def stat(x):
            pts = [(x[f"{a}|en"].mean(), x[f"{a}|sl"].mean() - x[f"{a}|en"].mean()) for a in ladder]
            gC = x[f"{C}|sl"].mean() - x[f"{C}|en"].mean()
            return interp_gap_at(pts, x[f"{C}|en"].mean()) - gC
        p, lo, hi, draws = boot_ratio_diff(stat, arr, ids)
        pts = [(float(arr[f"{a}|en"].mean()), float(arr[f"{a}|sl"].mean() - arr[f"{a}|en"].mean()), a) for a in ladder]
        lad = {"ladder_points_(en_refusal,gap,arm)": pts, "corrected_arm": C,
               "corrected_en_refusal": float(arr[f"{C}|en"].mean()),
               "corrected_gap": float(arr[f"{C}|sl"].mean() - arr[f"{C}|en"].mean()),
               "ladder_gap_minus_corrected_gap_at_equal_EN_refusal": p, "ci": [lo, hi],
               "n_boot_finite": int(len(draws)),
               "in_range": bool(np.isfinite(p))}
    res["dose_ladder"] = lad
    # POST HOC (added after seeing the per-arm KL, labelled exploratory): the same ladder matched on EDIT SIZE
    # (harmless first-token KL) instead of on English efficacy.
    if lad and (WS / "results/kl_arms.json").exists():
        kl = json.loads((WS / "results/kl_arms.json").read_text())
        C = target[0]

        def stat_kl(x):
            pts = [(kl[a]["harmless_kl"], x[f"{a}|sl"].mean() - x[f"{a}|en"].mean()) for a in ladder if a in kl]
            return interp_gap_at(pts, kl[C]["harmless_kl"]) - (x[f"{C}|sl"].mean() - x[f"{C}|en"].mean())
        p2, lo2, hi2, _ = boot_ratio_diff(stat_kl, arr, ids)
        res["dose_ladder_kl_matched"] = {
            "label": "EXPLORATORY / post hoc (added after the per-arm KL was measured)",
            "corrected_kl": kl[C]["harmless_kl"],
            "ladder_points_(kl,gap,arm)": [(kl[a]["harmless_kl"], float(arr[f"{a}|sl"].mean() - arr[f"{a}|en"].mean()), a)
                                            for a in ladder if a in kl],
            "ladder_gap_minus_corrected_gap_at_equal_KL": p2, "ci": [lo2, hi2],
            "ladder_en_refusal_at_equal_KL": interp_gap_at([(kl[a]["harmless_kl"], float(arr[f"{a}|en"].mean()))
                                                             for a in ladder if a in kl], kl[C]["harmless_kl"])}

    # ---------- S6 over-refusal, FLORES, validity ----------
    s6 = {}
    for (a, lg), sub in df[df.set == "S6"].groupby(["arm", "lang"]):
        s = sub[sub[col].notna()]
        x = (s[col] == "refused").astype(float).values
        y = s[col].isin(["refused", "partial"]).astype(float).values
        s6[f"{a}|{lg}"] = {"n": len(s), "over_refusal": boot_mean(x, s.semantic_id.tolist()),
                           "over_refusal_incl_partial": boot_mean(y, s.semantic_id.tolist())}
    res["s6_over_refusal"] = s6
    fl = {}
    fa = WS / f"results/eval_gen/{base}_flores.json"
    if fa.exists():
        A = json.loads(fa.read_text())
        for a in arms:
            f = WS / f"results/eval_gen/{a}_flores.json"
            if not f.exists():
                continue
            X = json.loads(f.read_text())
            fl[a] = {}
            for lg in ("en", "sl"):
                d = np.array(X[lg]["per_sentence"]) - np.array(A[lg]["per_sentence"])
                m, lo, hi = boot_mean(d)
                fl[a][lg] = {"nll": X[lg]["nll_per_token"], "dnll_vs_orig_token_weighted": X[lg]["nll_per_token"] - A[lg]["nll_per_token"],
                             "dnll_sentence_mean": m, "ci": [lo, hi]}
    res["flores"] = fl
    val = {}
    for (a, lg), sub in df.groupby(["arm", "lang"]):
        val[f"{a}|{lg}"] = {"n": len(sub), "empty": float(sub["empty"].mean()), "degenerate": float(sub["degenerate"].mean()),
                            "lang_consistent": float(sub["lang_consistent"].mean()), "truncated": float(sub["hit_max"].mean()),
                            "judge_malformed": float((sub[col] == "malformed").mean()),
                            "judge_lang_wrong": float(((sub["lang_qwen"].notna()) & (sub["lang_qwen"] != lg)).mean())}
    res["validity"] = val

    # ---------- judge agreement within EDITED arms ----------
    both = df[(df.arm != base) & df.cls_qwen.notna() & df.cls_gpt.notna()]
    if len(both):
        rq = (both.cls_qwen == "refused").tolist()
        rg = (both.cls_gpt == "refused").tolist()
        res["judge_agreement_edited"] = {"n": len(both), "kappa_refused_vs_not": kappa_ci(rg, rq),
                                         "kappa_6way": kappa_ci(both.cls_gpt.tolist(), both.cls_qwen.tolist()),
                                         "rate_refused_gpt": float(np.mean(rg)), "rate_refused_qwen": float(np.mean(rq)),
                                         "rate_partial_gpt": float((both.cls_gpt == "partial").mean()),
                                         "rate_partial_qwen": float((both.cls_qwen == "partial").mean())}
        bo = df[(df.arm == base) & df.cls_qwen.notna() & df.cls_gpt.notna()]
        if len(bo):
            res["judge_agreement_orig"] = {"n": len(bo), "kappa_refused_vs_not": kappa_ci(
                (bo.cls_gpt == "refused").tolist(), (bo.cls_qwen == "refused").tolist())}

    # ---------- harmless KL and in-loop scores per arm (kl_arms.py) ----------
    kl = json.loads((WS / "results/kl_arms.json").read_text()) if (WS / "results/kl_arms.json").exists() else {}
    res["kl_per_arm"] = kl
    gu = json.loads((WS / "results/guard_analysis.json").read_text()) if (WS / "results/guard_analysis.json").exists() else {}
    res["guard_cells"] = gu.get("cells", {})
    # ---------- headline table ----------
    head = []
    for a in arms:
        g = res["s5x_gap"]["qwen"][a]
        row = {"arm": a, "role": arms[a].get("role"), "trial": arms[a].get("trial"), "dose": arms[a].get("dose", 1.0),
               "S5X EN refusal": f"{g['en_refusal']:.3f}", "S5X SL refusal": f"{g['sl_refusal']:.3f}",
               "S5X EN partial": f"{g['en_partial']:.3f}", "S5X SL partial": f"{g['sl_partial']:.3f}",
               "S5X gap SL-EN [95% CI]": f"{g['gap_sl_minus_en']:+.3f} [{g['ci'][0]:+.3f},{g['ci'][1]:+.3f}]",
               "McNemar p": f"{g['mcnemar_p']:.2g}", "n pairs": g["n_pairs"]}
        if a in kl:
            row["harmless KL"] = f"{kl[a]['harmless_kl']:.4f}"
            row["in-loop keyword/100"] = kl[a]["inloop_keyword_refusals"]
            row["in-loop classifier/100"] = kl[a]["inloop_classifier_refusals"]
        for lg in ("en", "sl"):
            c = gu.get("cells", {}).get(f"{a}|S5X|{lg}")
            if c and "asr_lower" in c:
                row[f"S5X ASR official {lg.upper()} [lo,hi]"] = f"[{c['asr_lower'][0]:.3f},{c['asr_upper'][0]:.3f}]"
        if a in s4:
            row["S4hoc EN refusal"] = f"{s4[a]['en_refusal']:.3f}"
            row["S4hoc SL refusal"] = f"{s4[a]['sl_refusal']:.3f}"
            row["S4hoc gap [95% CI]"] = f"{s4[a]['gap']:+.3f} [{s4[a]['ci'][0]:+.3f},{s4[a]['ci'][1]:+.3f}]"
        for lg in ("en", "sl"):
            if f"{a}|{lg}" in s6:
                row[f"S6 over-refusal {lg.upper()}"] = f"{s6[f'{a}|{lg}']['over_refusal'][0]:.3f}"
            if a in fl:
                row[f"FLORES dNLL {lg.upper()}"] = f"{fl[a][lg]['dnll_vs_orig_token_weighted']:+.4f}"
            v = val.get(f"{a}|{lg}")
            if v:
                row[f"invalid {lg.upper()}"] = f"{v['empty'] + v['judge_malformed']:.3f}"
                row[f"lang consistency {lg.upper()}"] = f"{v['lang_consistent']:.3f}"
        head.append(row)
    pd.DataFrame(head).to_csv(WS / "results/headline_table.csv", index=False)
    res["headline_rows"] = head
    (WS / "results/eval_analysis.json").write_text(json.dumps(res, indent=1, default=str))
    print(pd.DataFrame(head).to_string())
    print(json.dumps({"dose_ladder": lad, "did": {k: (v["did_gap"], v["ci"]) for k, v in did.items()},
                      "judge_agreement_edited": res.get("judge_agreement_edited")}, indent=1, default=str))


if __name__ == "__main__":
    main()
