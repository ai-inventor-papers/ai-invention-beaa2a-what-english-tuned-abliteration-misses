#!/usr/bin/env python3
"""PHASE 3 - THE SCREEN (zero GPU). The frozen overlap statistic O is computed for cells that already exist on this
run's volume and were produced for a DIFFERENT question, so O was never fitted on them:
  * 57 GaMS3 cells (iteration-3 gen_art_experiment_10), scored on their S3 JBB half-B screen split;
  * 122 sibling-checkpoint (gemma-3-12b-it) cells (iteration-3 gen_art_experiment_9), scored from their cells.csv -
    a deliberate MIS-SPECIFICATION arm: it applies the GaMS3 write profile to another checkpoint's edits, so if O
    predicts there just as well, the profile is not model-specific and the instrument means less than it looks.
This is a SCREEN. No headline rests on it; the confirmation panel is the test."""
from __future__ import annotations

import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import csv

import numpy as np
from loguru import logger
from scipy.stats import spearmanr

import alib as A
import common as C
import labels as LB
from judge_local import JUDGE_LOCAL
from common import LANGS, jdump, jload, setup_logging

GEMMA_COV = {"B1": list(range(1, 13)), "B2": list(range(13, 25)), "B3": list(range(25, 37)), "B4": list(range(37, 49)),
             "C24": list(range(1, 25)), "C36": list(range(1, 37)), "S2": list(range(1, 49, 2)),
             "S4": list(range(1, 49, 4)), "ALL48": list(range(1, 49))}


def main() -> None:
    setup_logging("screen")
    F = jload(C.CFG / "frozen_predictions.json")
    e = {g: np.array(F[f"e_{g}"]) for g in LANGS}
    cos_h = np.array(F.get("cos_h", [0.0] * 49))
    out: dict = {"note": "SCREEN ONLY - cells produced for a different question; O was never fitted on them"}

    # ------------------------------------------------------------------ 1. the GaMS3 panel
    cache = A.judge_cache()
    rows = []
    for p in sorted((C.E10 / "results/cells").glob("*/gens.json")):
        cell = p.parent.name
        meta = jload(p.parent / "meta.json")
        g = meta.get("E_per_layer")
        if not g or sum(g) <= 0 or cell.startswith("dev_"):
            continue
        recs = LB.attach_labels(jload(p), cache, JUDGE_LOCAL)
        r = {"cell": cell, "E": float(sum(g)), "n_layers": int(sum(x > 0 for x in g)),
             "span": int(max(i for i, x in enumerate(g) if x > 0) - min(i for i, x in enumerate(g) if x > 0)),
             "mean_depth": float(np.average(range(48), weights=g)), "family": meta.get("family", meta.get("type")),
             "O_en": A.overlap(e["en"], g), "O_sl": A.overlap(e["sl"], g),
             "O_cos": A.overlap(cos_h, g) if cos_h.any() else float("nan")}
        for lang in LANGS:
            for split in ("screen", "confirm"):
                rr = A.rates(A.subset(recs, lang, split))
                r[f"{lang}_{split}_strict"] = rr["strict"]
                r[f"{lang}_{split}_broad"] = rr["broad"]
                r[f"{lang}_{split}_n"] = rr["n"]
        rows.append(r)
    out["gams3"] = {"n_cells": len(rows), "rows": rows}
    for lang in LANGS:
        for split in ("screen", "confirm"):
            v = [(x[f"O_{lang}"], x[f"{lang}_{split}_strict"]) for x in rows if x[f"{lang}_{split}_n"] >= 20]
            if len(v) >= 6:
                st = spearmanr([a for a, _ in v], [b for _, b in v])
                out["gams3"][f"rho_O_{lang}_{split}"] = {"n": len(v), "rho": float(st.statistic), "p": float(st.pvalue)}
                for comp in ("E", "n_layers", "span", "mean_depth"):
                    w = [(x[comp], x[f"{lang}_{split}_strict"]) for x in rows if x[f"{lang}_{split}_n"] >= 20]
                    s2 = spearmanr([np.log(a) if comp == "E" else a for a, _ in w], [b for _, b in w])
                    out["gams3"][f"rho_{comp}_{lang}_{split}"] = {"n": len(w), "rho": float(s2.statistic)}
    logger.info(f"GaMS3 screen: {len(rows)} cells; " + ", ".join(
        f"{k} {v['rho']:+.3f}" for k, v in out["gams3"].items() if k.startswith("rho_O")))

    # ------------------------------------------------------------------ 2. the sibling-checkpoint mis-specification arm
    try:
        er = jload(C.E9 / "results/energy_real.json")["e"]
        gem = []
        for x in csv.DictReader(open(C.E9 / "results/cells.csv")):
            cov = x["coverage"]
            if x["family"] != "weight" or cov not in GEMMA_COV or not x["sl_harm_refused"]:
                continue
            g = [0.0] * 48
            for k in GEMMA_COV[cov]:
                g[k - 1] = float(er.get(f"{k-1}|o_proj", 0.0)) + float(er.get(f"{k-1}|down_proj", 0.0))
            gem.append({"cell": x["cell"], "coverage": cov, "c": float(x["c"] or 1.0), "E": float(x["E"] or "nan"),
                        "O_en": A.overlap(e["en"], g), "O_sl": A.overlap(e["sl"], g),
                        "sl_strict": float(x["sl_harm_refused"]), "en_strict": float(x["en_harm_refused"]),
                        "stage": x["stage"], "n_layers": len(GEMMA_COV[cov])})
        out["gemma_misspec"] = {"n_cells": len(gem), "rows": gem,
                                "note": "the GaMS3 write profile applied to the sibling checkpoint's cells: a HIGH rho "
                                        "here would mean the profile is not model-specific"}
        for lang in LANGS:
            v = [(x[f"O_{lang}"], x[f"{lang}_strict"]) for x in gem]
            st = spearmanr([a for a, _ in v], [b for _, b in v])
            out["gemma_misspec"][f"rho_O_{lang}"] = {"n": len(v), "rho": float(st.statistic), "p": float(st.pvalue)}
        logger.info(f"sibling mis-specification screen: {len(gem)} cells; "
                    f"rho_sl {out['gemma_misspec']['rho_O_sl']['rho']:+.3f}")
    except (FileNotFoundError, KeyError, ValueError) as exc:
        logger.error(f"sibling screen unavailable: {exc!r}")
        out["gemma_misspec"] = {"error": repr(exc)}

    jdump(out, C.RES / "screen.json")


if __name__ == "__main__":
    main()
