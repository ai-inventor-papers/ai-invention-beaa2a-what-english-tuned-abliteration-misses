#!/usr/bin/env python3
"""STEPS 4.2-4.4 / 5 - in-loop analysis over the optimiser's OWN candidates.

  * trials table of the corrected run (results/trials_gemma_corrected.csv) + its frozen-rule selection
  * startup-draw identity check: corrected-run trials 0-59 vs iteration-1 trials 0-59 (same seed -> same params)
  * KEYWORD-PROXY MISCALIBRATION over all 116 iteration-1 draws, re-measured on this GPU
    (results/miscalibration_table.csv): keyword count, classifier count, Qwen3-14B judged refused/partial/complied
  * POST-HOC RESELECTION: select_rule.apply_rule_rows (unchanged) on (trial, count, KL) under keyword / classifier / judge
  * within-run A/B on the shared first-60 draws: Pareto fronts under both objectives
  * coverage descriptors of every selection
  -> results/inloop_analysis.json
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from coverage import descriptors
from select_rule import _pareto, apply_rule_rows

WS = Path(__file__).resolve().parent
J_CORR = WS / "checkpoints/gemma_corrected/google--gemma-3-12b-it.jsonl"


def read_jsonl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def load_study(path: Path) -> dict:
    import optuna
    from optuna.storages import JournalStorage
    from optuna.storages.journal import JournalFileBackend
    st = optuna.load_study(study_name="heretic", storage=JournalStorage(JournalFileBackend(str(path))))
    out = {}
    for t in st.trials:
        out[t.number] = {"number": t.number, "state": t.state.name, "values": list(t.values) if t.values else None,
                         "params": dict(t.params), "direction_index": t.user_attrs.get("direction_index"),
                         "parameters": t.user_attrs.get("parameters"),
                         "duration_s": t.duration.total_seconds() if t.duration else None}
    return out


def labels(paths: list[Path]) -> dict:
    L = {}
    for p in paths:
        for r in read_jsonl(p):
            if not r.get("judge_fail"):
                L[r["key"]] = r
    return L


def main() -> None:
    from replay import load_iter1_study
    import joblib
    _, it1 = load_iter1_study()
    res: dict = {"label": "Steps 4-5 (in-loop); corrected-run trial counts are classifier counts"}

    # ---------------- corrected run ----------------
    corr = load_study(J_CORR) if J_CORR.exists() else {}
    comp = {n: t for n, t in corr.items() if t["state"] == "COMPLETE"}
    rows = []
    for n, t in sorted(comp.items()):
        rows.append({"number": n, "corrected_refusals": round(t["values"][0] * 100), "kl": t["values"][1],
                     **{f"p.{k}": v for k, v in t["params"].items()}, "direction_index_eff": t["direction_index"],
                     "abl_params": json.dumps(t["parameters"]), "duration_s": t["duration_s"]})
    if rows:
        pd.DataFrame(rows).to_csv(WS / "results/trials_gemma_corrected.csv", index=False)
    same = []
    for n in range(60):
        if n in comp and n in it1:
            a, b = comp[n]["params"], it1[n]["params"]
            same.append(all((a[k] == b[k]) if isinstance(a[k], str) else abs(a[k] - b[k]) < 1e-12 for k in a))
    res["startup_draw_identity"] = {"n_checked": len(same), "n_identical": int(sum(same))}
    if comp:
        sel = apply_rule_rows([(n, round(t["values"][0] * 100), float(t["values"][1])) for n, t in comp.items()])
        t = comp[sel["trial_number"]]
        sel |= {"params": t["params"], "direction_index": t["direction_index"], "abliteration_parameters": t["parameters"]}
        res["corrected_selection"] = sel
        res["corrected_n_complete"] = len(comp)
        res["corrected_mean_trial_s"] = float(np.mean([t["duration_s"] for t in comp.values() if t["duration_s"]]))

    # ---------------- per-draw table over the 116 iteration-1 draws ----------------
    gens = read_jsonl(WS / "results/inloop_gens.jsonl")
    bundle = joblib.load(WS / "scorer/refusal_clf.joblib")
    probs = bundle["pipeline"].predict_proba([g["response"] for g in gens])[:, 1]
    for g, p in zip(gens, probs):
        g["clf_refused"] = bool((not g["response"].strip()) or p >= bundle["threshold"])
    Q = labels([WS / "results/judge_out/inloop_qwen.jsonl"])
    G = labels([WS / "results/judge_out/inloop_gpt41.jsonl"])
    by = defaultdict(list)
    for g in gens:
        if g["trial"] == -1:
            continue
        if g["run"] == "tpe60_115" or (g["run"] == "corrected" and g["trial"] < 60):
            by[g["trial"]].append(g)
    replay = {r["trial"]: r for r in read_jsonl(WS / "results/replay/tpe60_115.jsonl")}
    table = []
    for n in sorted(it1):
        gs = by.get(n, [])
        if len(gs) != 100:
            continue
        kl = replay[n]["kl"] if n in replay else (comp[n]["values"][1] if n in comp else None)
        q = [Q.get(g["key"]) for g in gs]
        nq = sum(x is not None for x in q)
        qcls = [x["cls"] for x in q if x is not None]
        kwc = sum(g["keyword_refused"] for g in gs)
        row = {"trial": n, "source": "replay" if n in replay else "corrected_run_startup_draw",
               "direction_scope": it1[n]["params"]["direction_scope"],
               "iter1_keyword_refusals": round(it1[n]["values"][0] * 100), "iter1_kl": it1[n]["values"][1],
               "kl": kl, "keyword_refusals": kwc, "classifier_refusals": sum(g["clf_refused"] for g in gs),
               "n_judged": nq,
               "judge_refused": sum(c in ("refused", "empty") for c in qcls) if nq == 100 else None,
               "judge_partial": sum(c == "partial" for c in qcls) if nq == 100 else None,
               "judge_complied": sum(c == "complied" for c in qcls) if nq == 100 else None,
               "judge_invalid": sum(c in ("malformed", "irrelevant") for c in qcls) if nq == 100 else None}
        if nq == 100:
            kw = np.array([g["keyword_refused"] for g in gs])
            y = np.array([Q[g["key"]]["cls"] in ("refused", "empty") for g in gs])
            row["keyword_fp_share"] = float((kw & ~y).sum() / max(kw.sum(), 1))
            row["keyword_fp_partial_share"] = float(sum(1 for g in gs if g["keyword_refused"] and Q[g["key"]]["cls"] == "partial") / max(kw.sum(), 1))
        table.append(row)
    df = pd.DataFrame(table)
    df.to_csv(WS / "results/miscalibration_table.csv", index=False)
    res["n_draws_scored"] = int(len(df))
    res["n_draws_judged"] = int((df["n_judged"] == 100).sum()) if len(df) else 0

    # pooled miscalibration (item level, edited draws, Qwen labels)
    from inloop import kstats
    ed = [g for n, gs in by.items() for g in gs if g["key"] in Q and Q[g["key"]]["cls"] != "malformed"]
    if ed:
        y = [int(Q[g["key"]]["cls"] in ("refused", "empty")) for g in ed]
        res["item_level_vs_qwen_all_edited_draws"] = {"keyword": kstats(y, [g["keyword_refused"] for g in ed]),
                                                      "classifier": kstats(y, [g["clf_refused"] for g in ed]),
                                                      "n_draws": len({g["trial"] for g in ed})}
    edg = [g for n, gs in by.items() for g in gs if g["key"] in G and G[g["key"]]["cls"] != "malformed"]
    if edg:
        y = [int(G[g["key"]]["cls"] in ("refused", "empty")) for g in edg]
        res["item_level_vs_gpt41_sample"] = {"keyword": kstats(y, [g["keyword_refused"] for g in edg]),
                                             "classifier": kstats(y, [g["clf_refused"] for g in edg])}

    # ---------------- reselection (same rule, same 116 draws) ----------------
    full = df[df["kl"].notna()]
    resel = {}
    for col in ("keyword_refusals", "classifier_refusals", "judge_refused"):
        sub = full[full[col].notna()]
        if len(sub) == 0:
            continue
        r = apply_rule_rows([(int(a), int(b), float(c)) for a, b, c in zip(sub["trial"], sub[col], sub["kl"])])
        r["candidates_scored"] = int(len(sub))
        r["complete_over_116"] = bool(len(sub) == 116)
        if not r["complete_over_116"]:  # a partial candidate set is NOT a reselection under the frozen rule
            resel[col + "_PARTIAL_candidates"] = {k: r[k] for k in ("rule_fired", "trial_number", "refusals", "kl",
                                                                  "candidates_scored")}
            continue
        r["coverage"] = descriptors(it1[r["trial_number"]]["parameters"],
                                    None if it1[r["trial_number"]]["params"]["direction_scope"] == "per layer"
                                    else it1[r["trial_number"]]["direction_index"])
        r["params"] = it1[r["trial_number"]]["params"]
        r["direction_index"] = it1[r["trial_number"]]["direction_index"]
        r["abliteration_parameters"] = it1[r["trial_number"]]["parameters"]
        resel[col] = r
    r_it1 = apply_rule_rows([(n, round(t["values"][0] * 100), float(t["values"][1])) for n, t in it1.items()])
    resel["iteration1_journal_keyword"] = r_it1
    res["reselection"] = resel

    # ---------------- shared first-60 draws: two objectives on identical edits ----------------
    if len(df):
        f60 = df[df["trial"] < 60]
        if len(f60):
            fk = _pareto([(int(a), int(b), float(c)) for a, b, c in zip(f60.trial, f60.keyword_refusals, f60.kl)])
            fc = _pareto([(int(a), int(b), float(c)) for a, b, c in zip(f60.trial, f60.classifier_refusals, f60.kl)])
            res["first60_pareto"] = {"keyword": sorted(x[0] for x in fk), "classifier": sorted(x[0] for x in fc)}
    # ---------------- where did each search go? TPE-phase draws (60-115) of the two runs ----------------
    if comp:
        from scipy.stats import mannwhitneyu

        def desc_rows(trs: dict, kl_of) -> list[dict]:
            out = []
            for n, t in trs.items():
                if n < 60 or t.get("parameters") is None:
                    continue
                di = None if t["params"]["direction_scope"] == "per layer" else t["direction_index"]
                d = descriptors(t["parameters"], di)
                out.append({"trial": n, "per_layer": t["params"]["direction_scope"] == "per layer", "kl": kl_of(n),
                            "A1": d["sum_A1"], "mass": d["sum_mass"], "partic": d["sum_partic"], "centroid": d["sum_centroid"]})
            return out
        kw_rows = desc_rows(it1, lambda n: replay[n]["kl"] if n in replay else it1[n]["values"][1])
        co_rows = desc_rows(comp, lambda n: comp[n]["values"][1])
        cmp = {}
        for k in ("kl", "A1", "mass", "partic", "centroid"):
            a = [r[k] for r in kw_rows]
            b = [r[k] for r in co_rows]
            cmp[k] = {"keyword_run_median": float(np.median(a)), "corrected_run_median": float(np.median(b)),
                      "mannwhitney_p": float(mannwhitneyu(a, b).pvalue)}
        cmp["per_layer_share"] = {"keyword_run": float(np.mean([r["per_layer"] for r in kw_rows])),
                                  "corrected_run": float(np.mean([r["per_layer"] for r in co_rows]))}
        cmp["n"] = [len(kw_rows), len(co_rows)]
        cmp["label"] = "EXPLORATORY; one seed per run, so this describes two TPE trajectories, not a population"
        res["tpe_phase_comparison"] = cmp
        pd.DataFrame([{"run": "keyword", **r} for r in kw_rows] + [{"run": "corrected", **r} for r in co_rows]).to_csv(
            WS / "results/tpe_phase_draws.csv", index=False)
    if "corrected_selection" in res:
        s = res["corrected_selection"]
        res["corrected_selection"]["coverage"] = descriptors(
            s["abliteration_parameters"], None if s["params"]["direction_scope"] == "per layer" else s["direction_index"])
    # coverage table: 116 keyword-run draws + community edit (coverage.py) + every corrected-run trial
    cov = pd.read_csv(WS / "results/coverage_descriptors.csv")
    extra = []
    for n, t in sorted(comp.items()):
        di = None if t["params"]["direction_scope"] == "per layer" else t["direction_index"]
        extra.append({"source": "corrected_run", "trial": n, "direction_scope": t["params"]["direction_scope"],
                      "direction_index": di, "keyword_refusals": None, "kl": t["values"][1],
                      "corrected_refusals": round(t["values"][0] * 100), **descriptors(t["parameters"], di)})
    pd.concat([cov, pd.DataFrame(extra)], ignore_index=True).to_csv(WS / "results/coverage_table.csv", index=False)
    (WS / "results/inloop_analysis.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: v for k, v in res.items() if k not in ("reselection",)}, indent=1, default=str)[:3000])
    for k, v in res.get("reselection", {}).items():
        print(k, {x: v.get(x) for x in ("rule_fired", "trial_number", "refusals", "kl", "candidates_scored")})


if __name__ == "__main__":
    main()
