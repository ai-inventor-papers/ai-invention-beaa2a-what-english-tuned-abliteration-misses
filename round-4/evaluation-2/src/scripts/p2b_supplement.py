#!/usr/bin/env python3
"""PHASE 2b - DECLARED POST-FREEZE SUPPLEMENT (does not change the frozen gate).

Why: the frozen stratified sample filled the workhorse-REFUSED strata with already-labelled (free) exp9/exp10 items first,
so exp11 and exp12 contributed NO workhorse-REFUSED items and their per-panel kappa was not estimable (one labeller constant).
This supplement buys gpt-4.1 labels for a hash-frozen draw of workhorse-REFUSED harmful items from EDITED cells of
exp11 and exp12 (up to 40 per panel x language), with the same frozen rubric, and reports per-panel agreement on
(frozen sample + supplement) SEPARATELY from the gate, which stays on the frozen sample."""
from __future__ import annotations

import asyncio
import json

import numpy as np
import pandas as pd
import yaml
from loguru import logger

import common as C
import p2_buy as PB

OUT = C.RES / "gpt41_supplement_labels.jsonl"


@logger.catch(reraise=True)
def main() -> None:
    C.setup_logging("p2b_supplement")
    df = pd.read_parquet(C.RES / "pooled_generations.parquet", columns=["gid", "source", "cell_id", "language", "role", "edited",
                                                                        "class_4way", "prompt", "response", "n_tokens", "hit_token_cap", "semantic_item_id", "arm_kind"])
    calib = {p["gid"] for p in C.jload(C.RES / "calibration_sample.json")["items"]}
    fr = df[df.source.isin(["exp11", "exp12"]) & df.edited & (df.role == "harmful") & df.language.isin(["en", "sl"])
            & (df.class_4way == "REFUSED") & ~df.gid.isin(calib) & (df.response.str.strip().str.len() > 0)].copy()
    fr["h"] = [C.sha_text(f"supp|{g}") for g in fr.gid]
    pick = fr.sort_values("h").groupby(["source", "language"]).head(40)
    frozen = {"rule": "sha256('supp|'+gid) order, first 40 workhorse-REFUSED harmful items per (exp11|exp12) x language from edited cells, "
                      "excluding the frozen calibration sample", "gids": pick.gid.tolist(), "n": int(len(pick))}
    fp = C.RES / "calibration_supplement.json"
    if not fp.exists():
        C.jdump(frozen, fp)
    logger.info(f"supplement: {len(pick)} items")
    done = {r["gid"] for r in C.read_jsonl(OUT) if r.get("status") == "ok"} if OUT.exists() else set()
    cap = df.groupby("cell_id").n_tokens.max()
    items = [{"gid": r.gid, "prompt": r.prompt, "response": r.response, "hit": bool(r.hit_token_cap), "cap": int(cap[r.cell_id])}
             for r in pick.itertuples() if r.gid not in done]
    PB.STATE["cum"] = sum(float(r.get("usd") or 0) for r in C.read_jsonl(PB.COST_LOG))
    logger.info(f"buying {len(items)}; cumulative so far ${PB.STATE['cum']:.3f}")
    proto = yaml.safe_load((C.EXP4 / "protocol.yaml").read_text())["judge_primary"]
    if items:
        res = asyncio.run(PB.run(items, proto["system"], proto["user_template"]))
        with open(OUT, "a") as f:
            for r in res:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    lab = {r["gid"]: C.canon(r.get("cls")) for r in C.read_jsonl(OUT) if r.get("status") == "ok"}
    # per-panel agreement on frozen sample + supplement (UNWEIGHTED; the supplement is refusal-enriched by design)
    bought = {r["gid"]: C.canon(r.get("cls")) for r in C.read_jsonl(C.RES / "gpt41_calibration_labels.jsonl") if r.get("status") == "ok"}
    it = pd.DataFrame(C.jload(C.RES / "calibration_sample.json")["items"])
    d = it.merge(df, on=["gid", "source", "cell_id"], how="left")
    d["gpt"] = d.gid.map(bought)
    lbl = pd.read_parquet(C.RES / "pooled_generations.parquet", columns=["gid", "label_gpt41"]).set_index("gid").label_gpt41
    d.loc[d.covered_free, "gpt"] = d.loc[d.covered_free, "gid"].map(lbl)
    s = df[df.gid.isin(lab)].copy()
    s["gpt"] = s.gid.map(lab)
    s["origin"] = "supplement"
    d["origin"] = "frozen"
    allx = pd.concat([d, s], ignore_index=True)
    allx = allx[allx.gpt.notna() & allx.class_4way.notna()]
    rng = np.random.default_rng(99)
    res = {"declared": "post-freeze supplement; per-panel agreement below is UNWEIGHTED on frozen+supplement and does NOT enter the gate",
           "n_supplement_labels": len(lab), "cumulative_usd": round(sum(float(r.get("usd") or 0) for r in C.read_jsonl(PB.COST_LOG)), 4)}
    for src in ("exp11", "exp12"):
        for lang in ("en", "sl", "all"):
            x = allx[(allx.source == src) & ((allx.language == lang) if lang != "all" else True)]
            a = (x.class_4way == "REFUSED").to_numpy(); b = (x.gpt == "REFUSED").to_numpy()
            kb = C.cluster_boot(lambda ix: C.kappa(a[ix], b[ix]), x.semantic_item_id.to_numpy(), 500, int(rng.integers(1 << 30)))
            res[f"{src}|{lang}"] = {"n": int(len(x)), "kappa": C.kappa(a, b), "kappa_ci": C.ci(kb), "ac1": C.gwet_ac1(a, b), **C.se_sp(a, b),
                                    "crosstab_gpt_rows_workhorse_cols": pd.crosstab(x.gpt, x.class_4way).to_dict()}
    C.jdump(res, C.RES / "judge_calibration_supplement.json")
    logger.info({k: (v["n"], round(v["kappa"], 3)) for k, v in res.items() if isinstance(v, dict)})




# ------------------------------------------------------------------------------------------------ correction
def conditional_matrices(allx: pd.DataFrame) -> dict:
    """P(gpt class | workhorse class) per panel x language. Unbiased per workhorse class because every draw
    (frozen strata and supplement) was conditioned on the workhorse class."""
    out = {}
    for (src, lang), x in allx.groupby(["source", "language"]):
        x = x[x.class_4way.isin(C.CLASSES4) & x.gpt.isin(C.CLASSES4)]
        M = pd.crosstab(x.class_4way, x.gpt).reindex(index=C.CLASSES4, columns=C.CLASSES4).fillna(0)
        out[(src, lang)] = M
    return out


def corrected_c3() -> None:
    import statsmodels.api as sm
    sup = C.jload(C.RES / "judge_calibration_supplement.json")
    df = pd.read_parquet(C.RES / "pooled_generations.parquet", columns=["gid", "source", "cell_id", "language", "class_4way", "semantic_item_id"])
    bought = {r["gid"]: C.canon(r.get("cls")) for f in ("gpt41_calibration_labels.jsonl", "gpt41_supplement_labels.jsonl")
              for r in C.read_jsonl(C.RES / f) if r.get("status") == "ok"}
    lbl = pd.read_parquet(C.RES / "pooled_generations.parquet", columns=["gid", "label_gpt41"]).set_index("gid").label_gpt41
    cal = {p["gid"] for p in C.jload(C.RES / "calibration_sample.json")["items"]} | set(C.jload(C.RES / "calibration_supplement.json")["gids"])
    x = df[df.gid.isin(cal)].copy()
    x["gpt"] = x.gid.map(bought).fillna(x.gid.map(lbl))
    Ms = conditional_matrices(x)
    cf = C.jload(C.RES / "curve_fits.json")
    grid = np.linspace(-2.0, 2.5, 181)
    res = {"method": "cell shares re-expressed in gpt-4.1 classes: p_gpt = sum_i p_wh(i) * P(gpt | wh=i), panel x language "
                     "matrices from frozen sample + supplement (rows with < 5 items fall back to identity); matrices are estimated on EDITED cells and are NOT applied to the unedited arm"}
    for key, src in (("L1_exp11_f_ladder", "exp11"), ("L2_exp9_c_grid", "exp9")):
        cells = pd.DataFrame(cf[key]["cells"])
        r = {}
        for lang in ("en", "sl"):
            M = Ms.get((src, lang))
            P = np.eye(4)
            if M is not None:
                for i, k in enumerate(C.CLASSES4):
                    if M.loc[k].sum() >= 5:
                        P[i] = (M.loc[k] / M.loc[k].sum()).to_numpy()
            c = cells[cells.language == lang].copy()
            obs = c[C.CLASSES4].to_numpy(float) / c.n.to_numpy(float)[:, None]
            noop = c.cell_id.isin(["A_orig", "noop"]).to_numpy()
            corr = obs @ P
            corr[noop] = obs[noop]  # matrices are estimated on EDITED cells only; the unedited arm keeps its raw labels
            rpc = corr[:, :3].sum(axis=1)
            c["partial_corr"] = corr[:, 1] / rpc
            c["refused_corr"] = corr[:, 0]
            fit = sm.nonparametric.lowess(c.partial_corr, c.z, frac=cf[key]["span"], it=0, return_sorted=True)
            xs = np.unique(fit[:, 0]); ys = np.array([fit[fit[:, 0] == u, 1].mean() for u in xs])
            curve = np.interp(grid, xs, ys, left=np.nan, right=np.nan)
            m = np.isfinite(curve)
            r[lang] = {"P_gpt_given_workhorse_rows": {k: P[i].round(3).tolist() for i, k in enumerate(C.CLASSES4)},
                       "argmax_z_corrected": float(grid[m][np.argmax(curve[m])]), "max_minus_min_corrected": float(np.nanmax(curve) - np.nanmin(curve)),
                       "argmax_z_raw": cf[key]["nonparametric"][lang]["peak_z"], "max_minus_min_raw": cf[key]["nonparametric"][lang]["max_minus_min"]}
            if key.startswith("L1"):
                r[lang]["refused_by_cell_raw_vs_corrected"] = {cc: [round(a, 3), round(b, 3)] for cc, a, b in
                                                               zip(c.cell_id, c.REFUSED / c.n, c.refused_corr)}
        r["delta_argmax_corrected"] = r["sl"]["argmax_z_corrected"] - r["en"]["argmax_z_corrected"]
        r["delta_argmax_raw"] = r["sl"]["argmax_z_raw"] - r["en"]["argmax_z_raw"]
        res[key] = r
    # exp11 S5X strict gap re-expressed in gpt-4.1 terms (refused share only)
    e = df[(df.source == "exp11") & df.class_4way.notna()]
    sets = pd.read_parquet(C.RES / "pooled_generations.parquet", columns=["gid", "split", "role"]).set_index("gid")
    e = e[e.gid.map(sets.split) == "S5X"]
    e = e[e.gid.map(sets.role) == "harmful"]
    g = {}
    for arm, s in e.groupby("cell_id"):
        rr = {}
        for lang in ("en", "sl"):
            ss = s[s.language == lang]
            M = Ms.get(("exp11", lang)) if arm != "A_orig" else None  # edited-cell matrices never applied to the unedited arm
            pref = []
            for k in C.CLASSES4:
                row = M.loc[k] if M is not None else None
                pref.append(float(row["REFUSED"] / row.sum()) if row is not None and row.sum() >= 5 else float(k == "REFUSED"))
            share = np.array([(ss.class_4way == k).mean() for k in C.CLASSES4])
            rr[lang] = {"raw": float(share[0]), "gpt_equiv": float(share @ np.array(pref))}
        g[arm] = {"gap_raw": rr["sl"]["raw"] - rr["en"]["raw"], "gap_gpt_equiv": rr["sl"]["gpt_equiv"] - rr["en"]["gpt_equiv"], **rr}
    res["exp11_S5X_strict_gap_raw_vs_gpt_equivalent"] = g
    sup["c3_and_exp11_under_gpt41_reexpression"] = res
    C.jdump(sup, C.RES / "judge_calibration_supplement.json")
    logger.info(json.dumps({k: (v.get("delta_argmax_raw"), v.get("delta_argmax_corrected")) for k, v in res.items() if isinstance(v, dict) and "delta_argmax_raw" in v}))
    logger.info(json.dumps({a: (round(v["gap_raw"], 3), round(v["gap_gpt_equiv"], 3)) for a, v in g.items()}))


if __name__ == "__main__":
    main()
    corrected_c3()
