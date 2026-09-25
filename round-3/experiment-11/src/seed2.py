#!/usr/bin/env python3
"""cut_2 executed: the SECOND optimiser seed (20260926) of the corrected-objective run, identical in every other
respect. Answers the question prompt-level CIs cannot: is the corrected run's selection one draw of TPE noise?
-> results/seed2_analysis.json"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from analyze_inloop import load_study
from coverage import descriptors
from select_rule import apply_rule_rows

WS = Path(__file__).resolve().parent
J2 = WS / "checkpoints/gemma_corrected_s2/google--gemma-3-12b-it.jsonl"


def summarize(journal: Path, name: str) -> dict:
    st = {n: t for n, t in load_study(journal).items() if t["state"] == "COMPLETE"}
    sel = apply_rule_rows([(n, round(t["values"][0] * 100), float(t["values"][1])) for n, t in st.items()])
    t = st[sel["trial_number"]]
    di = None if t["params"]["direction_scope"] == "per layer" else t["direction_index"]
    d = descriptors(t["parameters"], di)
    rows = [{"trial": n, "refusals": round(x["values"][0] * 100), "kl": x["values"][1],
             "per_layer": x["params"]["direction_scope"] == "per layer"} for n, x in st.items()]
    df = pd.DataFrame(rows)
    return {"run": name, "n_complete": len(st), "selection": sel | {"direction_scope": t["params"]["direction_scope"],
            "direction_index": di, "abliteration_parameters": t["parameters"]},
            "selected_coverage": {k: d[k] for k in ("sum_A1", "sum_mass", "sum_partic", "sum_centroid", "sum_cov0.10")},
            "n_trials_under_rule1_threshold": int((df.refusals <= 10).sum()),
            "median_refusals": float(df.refusals.median()), "median_kl": float(df.kl.median()),
            "per_layer_share": float(df.per_layer.mean()),
            "best_kl_among_qualifying": float(df[df.refusals <= 10].kl.min()) if (df.refusals <= 10).any() else None}


def main() -> None:
    out = {"label": "cut_2 EXECUTED (the plan's first declared cut): a second optimiser seed for the corrected objective",
           "held_constant": "everything except optuna/TPE seed (20260923 -> 20260926)"}
    out["seed_20260923"] = summarize(WS / "checkpoints/gemma_corrected/google--gemma-3-12b-it.jsonl", "corrected seed 1")
    if J2.exists():
        out["seed_20260926"] = summarize(J2, "corrected seed 2")
        a, b = out["seed_20260923"], out["seed_20260926"]
        out["comparison"] = {
            "same_rule_branch": a["selection"]["rule_fired"] == b["selection"]["rule_fired"],
            "rule_fired": [a["selection"]["rule_fired"], b["selection"]["rule_fired"]],
            "selected_trials": [a["selection"]["trial_number"], b["selection"]["trial_number"]],
            "selected_refusals": [a["selection"]["refusals"], b["selection"]["refusals"]],
            "selected_kl": [a["selection"]["kl"], b["selection"]["kl"]],
            "selected_scope": [a["selection"]["direction_scope"], b["selection"]["direction_scope"]],
            "selected_A1": [a["selected_coverage"]["sum_A1"], b["selected_coverage"]["sum_A1"]],
            "A1_of_keyword_selection_trial96": 26.01157247479183,
            "n_qualifying_draws": [a["n_trials_under_rule1_threshold"], b["n_trials_under_rule1_threshold"]],
            "verdict": ("BOTH seeds fire the primary rule and select a broader, higher-aligned-coverage kernel than "
                        "the keyword run's trial 96" if (a["selection"]["rule_fired"] == b["selection"]["rule_fired"]
                        and min(a["selected_coverage"]["sum_A1"], b["selected_coverage"]["sum_A1"]) > 26.012)
                        else "the two seeds DISAGREE - the selection difference may be optimiser noise")}
    (WS / "results/seed2_analysis.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(out.get("comparison", out), indent=1, default=str))


if __name__ == "__main__":
    main()
