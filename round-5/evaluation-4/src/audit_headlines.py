#!/usr/bin/env python3
"""Headline self-audit: re-derive this artifact's headline numbers through a DIFFERENT code path (pandas, no helper
shared with rederive_iter5.py / eval.py), and confirm the statistics fail on shuffled input. Writes results/headline_audit.json."""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
LOOP = Path(os.environ.get("AII_LOOP_ROOT", HERE.parents[2]))
rng = np.random.default_rng(7)
out = {}

# 1. defect rate, recounted straight from the per-record verdicts
recs = pd.DataFrame(json.loads((HERE / "results/corrected_numbers.json").read_text())["records"])
fp = recs[recs.pass_provenance.str.startswith("first_pass") & ~recs.verdict.isin(["FIRST_REPORT", "NOT_REDERIVED"])]
out["defect_rate"] = {"k": int(fp.verdict.isin(["MISMATCH", "MISDESCRIBED", "UNTRACEABLE", "SIGN_REVERSED"]).sum()), "n": int(len(fp))}

# 2. lint: every resolved path must exist on disk; count NOT_FOUND
lint = pd.read_csv(HERE / "results/path_lint.csv")
exists = lint.resolved_path_relative_to_3_invention_loop.fillna("").map(lambda p: bool(p) and (LOOP / p).exists())
out["lint"] = {"n": int(len(lint)), "resolved_and_exist": int(exists.sum()), "not_found": int((~exists).sum())}

# 3. exp14 primary rho (SL) via pandas spearman on the parquet
pi = pd.read_parquet(LOOP / "round-4/experiment-14/src/results/per_item.parquet")
cells = pd.read_csv(LOOP / "round-4/experiment-14/src/results/cells.csv").set_index("cell")
h = pi[(pi.split == "confirm") & pi.cls4.isin(["REFUSED", "PARTIAL", "COMPLIED"]) & pi.cell.str.startswith("C_") & (pi.lang == "sl")]
rate = h.assign(r=(h.cls4 == "REFUSED").astype(float)).groupby("cell").r.mean()
df = pd.DataFrame({"r": rate, "O": cells.loc[rate.index, "O_sl"]})
out["exp14_rho_sl"] = float(df.corr(method="spearman").loc["r", "O"])
out["exp14_rho_sl_shuffledO_mean"] = float(np.mean([pd.Series(rng.permutation(df.O.values)).corr(pd.Series(df.r.values), method="spearman") for _ in range(300)]))

# 4. exp4 S5X strict gap and the headline-cell kappa via pandas on the pooled table
pg = pd.read_parquet(LOOP / "round-4/evaluation-2/src/results/pooled_generations.parquet",
                     columns=["source", "cell_id", "prompt_id", "class_4way", "label_gpt41", "gid", "language", "split"])
fs = json.loads((LOOP / "round-2/experiment-4/src/frozen_samples.json").read_text())["s5x_pairs"]
pm = pd.concat([pd.DataFrame({"prompt_id": [p["en_item"] for p in fs], "pair": [p["pair_id"] for p in fs], "side": "en"}),
                pd.DataFrame({"prompt_id": [p["sl_item"] for p in fs], "pair": [p["pair_id"] for p in fs], "side": "sl"})])
g = pg[(pg.source == "exp4") & (pg.cell_id == "gemma_edit") & pg.class_4way.isin(["REFUSED", "PARTIAL", "COMPLIED"])].merge(pm, on="prompt_id")
wide = g.assign(r=(g.class_4way == "REFUSED").astype(float)).pivot_table(index="pair", columns="side", values="r", aggfunc="first").dropna()
out["exp4_s5x_gap_strict"] = float((wide.sl - wide.en).mean())
out["exp4_s5x_gap_strict_sidelabel_shuffled"] = float(np.mean([np.mean(np.where(rng.random(len(wide)) < 0.5, wide.sl - wide.en, wide.en - wide.sl)) for _ in range(300)]))
lab = {}
for fn in ("gpt41_calibration_labels.jsonl", "gpt41_supplement_labels.jsonl"):
    for line in open(LOOP / "round-4/evaluation-2/src/results" / fn):
        x = json.loads(line)
        if x.get("status") == "ok":
            lab[x["gid"]] = str(x.get("cls", "")).upper()
c = pg[(pg.source == "exp4") & (pg.cell_id == "gemma_edit") & (pg.language == "en")].copy()
c["ref"] = c.label_gpt41.fillna(c.gid.map(lab))
c = c[c.ref.isin(["REFUSED", "PARTIAL", "COMPLIED"]) & c.class_4way.isin(["REFUSED", "PARTIAL", "COMPLIED"])]
a, b = (c.class_4way == "REFUSED"), (c.ref == "REFUSED")
ct = pd.crosstab(a, b); n = ct.values.sum(); po = np.trace(ct.values) / n
pe = (ct.sum(1).values * ct.sum(0).values).sum() / n ** 2
out["exp4_gemma_edit_en_kappa"] = {"kappa": float((po - pe) / (1 - pe)), "n": int(n)}
bs = b.sample(frac=1, random_state=3).values
ct2 = pd.crosstab(a.values, bs); po2 = np.trace(ct2.values) / n; pe2 = (ct2.sum(1).values * ct2.sum(0).values).sum() / n ** 2
out["exp4_gemma_edit_en_kappa_shuffled_reference"] = float((po2 - pe2) / (1 - pe2))

# 5. exp11 trial counts straight from the csv
m = pd.read_csv(LOOP / "round-3/experiment-11/src/results/miscalibration_table.csv").set_index("trial")
out["exp11_trial107_judge_refused"] = int(m.loc[107, "judge_refused"]); out["exp11_trial96_judge_refused_partial"] = [int(m.loc[96, "judge_refused"]), int(m.loc[96, "judge_partial"])]

# compare to the pipeline's records
R = recs.set_index("claim_id")
checks = {
    "exp14_rho_sl": (out["exp14_rho_sl"], R.loc["E14.primary_rho_sl", "recomputed_value"]),
    "exp4_s5x_gap_strict": (out["exp4_s5x_gap_strict"], R.loc["E4.S5X_gap.gemma_edit.strict", "recomputed_value"]),
    "exp4_gemma_edit_en_kappa": (out["exp4_gemma_edit_en_kappa"]["kappa"], R.loc["D1.kappa.exp4.gemma_edit.en", "recomputed_value"]),
    "exp11_trial107": (out["exp11_trial107_judge_refused"], R.loc["E11.trial107.judge_refused", "recomputed_value"]),
}
ev = json.loads((HERE / "eval_out.json").read_text())["metrics_agg"]
checks["defect_k"] = (out["defect_rate"]["k"], ev["n_defects_first_pass"]); checks["defect_n"] = (out["defect_rate"]["n"], ev["n_numbers_first_pass_with_draft_value"])
checks["lint_not_found"] = (out["lint"]["not_found"], ev["lint_n_not_found_after_rewrite"])
out["agreement"] = {k: {"audit": float(a_), "pipeline": float(b_), "agree": abs(float(a_) - float(b_)) < 1e-6} for k, (a_, b_) in checks.items()}
out["placebos_fail_as_required"] = {"shuffled_O_rho_near_0": abs(out["exp14_rho_sl_shuffledO_mean"]) < 0.1,
                                    "side_label_shuffled_gap_near_0": abs(out["exp4_s5x_gap_strict_sidelabel_shuffled"]) < 0.05,
                                    "shuffled_reference_kappa_near_0": abs(out["exp4_gemma_edit_en_kappa_shuffled_reference"]) < 0.2}
(HERE / "results/headline_audit.json").write_text(json.dumps(out, indent=1))
print(json.dumps({"agreement": out["agreement"], "placebos": out["placebos_fail_as_required"]}, indent=1))
