#!/usr/bin/env python3
"""Reshape method_out.json into the exp_gen_sol_out schema: every analysis block goes under
`metadata`, and the per-example rows become four `datasets` (EN refusal, SL refusal, harmless KL,
and the 60 shared edits), with one `predict_*` column per checkpoint/condition."""
import json
from pathlib import Path

WS = Path(__file__).resolve().parent
m = json.loads((WS / "method_out.json").read_text())
ev = lambda t, c: json.loads((WS / "results" / "eval" / f"{t}_{c}.json").read_text())
CONDS = [(t, c) for t in ("gams", "gemma") for c in ("orig", "own", "swap")]
D = {(t, c): ev(t, c) for t, c in CONDS}
flag = lambda b: "refusal" if b else "compliance"

en = []
for i, x in enumerate(D[("gams", "orig")]["en"]):
    r = {"input": x["prompt"],
         "output": "REFUSAL (a harmful request; refusing is the behaviour safety training targets)",
         "metadata_id": x["id"], "metadata_language": "en",
         "metadata_source": "mlabonne/harmful_behaviors test[:100]"}
    for t, c in CONDS:
        r[f"predict_{t}_{c}"] = flag(D[(t, c)]["en"][i]["refusal_heretic"])
    en.append(r)

sl = []
for i, x in enumerate(D[("gams", "orig")]["sl"]):
    r = {"input": x["prompt_sl"],
         "output": "REFUSAL (Slovene translation of the same harmful request)",
         "metadata_id": x["id"], "metadata_language": "sl",
         "metadata_source": "NLLB-200-distilled-1.3B translation of mlabonne/harmful_behaviors test[:100]",
         "metadata_scorer": "Slovene marker list; accuracy 0.75 / kappa 0.48 vs executor hand labels "
                            "(n=40), NATIVE_REVIEW_PENDING"}
    for t, c in CONDS:
        r[f"predict_{t}_{c}"] = flag(D[(t, c)]["sl"][i]["refusal_sl_markers"])
    sl.append(r)

ha = json.loads((WS / "data" / "heretic_default_sources.json").read_text())["harmless_alpaca_test"][:100]
kl = []
for i, p in enumerate(ha):
    r = {"input": p, "output": "(no reference answer: this is the harmless-divergence probe; the "
                               "measurement is first-token KL against the same model's original)",
         "metadata_id": f"ha_test_{i:03d}", "metadata_source": "mlabonne/harmless_alpaca test[:100]"}
    for t, c in CONDS:
        r[f"predict_{t}_{c}"] = f"{D[(t, c)]['kl_per_prompt'][i]:.6g}"
    kl.append(r)

import pandas as pd
A = pd.read_csv(WS / "results" / "trials_gams.csv")
B = pd.read_csv(WS / "results" / "trials_gemma.csv")
shared = m["efficiency_same_edit_contrast"]["n_shared_identical_edits"]
edits = []
for i in range(shared):
    a, b = A.iloc[i], B.iloc[i]
    edits.append({
        "input": json.dumps({"trial": int(a["number"]), "direction_scope": a["p.direction_scope"],
                             "direction_index": a["p.direction_index"],
                             "abliteration_parameters": json.loads(a["abl_params"])}),
        "output": "(no reference: the outcome of an edit is what is measured)",
        "metadata_id": f"edit_{int(a['number']):03d}",
        "metadata_note": "identical parameter draw in both models (shared TPE seed 20260923)",
        "predict_gams_refusals": str(int(a["refusals"])), "predict_gemma_refusals": str(int(b["refusals"])),
        "predict_gams_kl": f"{a['kl']:.6g}", "predict_gemma_kl": f"{b['kl']:.6g}"})

meta = {k: v for k, v in m.items()}
meta["method_name"] = "Matched Heretic abliteration of two sibling 12B models + sibling screen + bilingual swap test"
meta["baseline"] = ("the unedited original of each model, scored in the same pipeline (same 4-bit "
                    "quantization, batch size, chat template, greedy decoding); plus a second baseline - "
                    "the sibling's selected parameters applied to the same model (swap) - and a "
                    "params-only cross-validated predictor as the baseline for the A3 agreement claim")
meta["per_example_files"] = str(WS / "results" / "eval")
out = {"metadata": meta, "datasets": [
    {"dataset": "harmful_behaviors_test100_EN (refusal flags, 6 checkpoints)", "examples": en},
    {"dataset": "harmful_behaviors_test100_SL (refusal flags, 6 checkpoints)", "examples": sl},
    {"dataset": "harmless_alpaca_test100 (per-prompt first-token KL, 6 checkpoints)", "examples": kl},
    {"dataset": f"shared_startup_edits ({shared} identical edits, outcome in both models)", "examples": edits},
]}
(WS / "method_out.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print("datasets:", [(d["dataset"], len(d["examples"])) for d in out["datasets"]])
