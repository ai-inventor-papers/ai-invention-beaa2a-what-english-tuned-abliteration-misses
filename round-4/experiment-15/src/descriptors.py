#!/usr/bin/env python3
"""STAGE S5 (descriptors) - closed-form, zero-GPU kernel descriptors of every candidate, both searches.

art_xLy2vVlI7OEL/heretic_op.py is NOT a declared dependency; if absent, the closed form recorded in
art_0XmNBGkzsJc_/coverage.py is replicated here (Heretic 3521f864 abliterate kernel):
    w_c(h) = max_w + (|h-pos|/dist) * (min_w_eff - max_w)  if |h-pos| <= dist else 0
Direction used at layer h: per-layer scope -> Heretic's own direction r(h) (row h+1); global scope ->
normalize(lerp(r[int(i+1)], r[int(i+1)+1], frac(i+1))) at every layer. Reference d(h) = Heretic's own per-layer
direction of THAT model (the primary reference of art_0XmNBGkzsJc_; its secondary x8 reference exists only for Gemma).
Descriptors (per component and summed): cov@{.10,.25,.50,.75}, mass, energy = sum w^2 ||delta_h||^2, centroid,
participation, aligned coverage A1 = sum w |cos(v_used, d)|, A2.

VALIDATION: the Gemma rows of art_0XmNBGkzsJc_/results/coverage_descriptors.csv must be reproduced to < 1e-6
(relative) before the same code is applied to GaMS3.
  python descriptors.py -> results/candidate_descriptors.csv, results/descriptors_validation.json
"""
from __future__ import annotations

import json
import math

import numpy as np
import pandas as pd
from loguru import logger

from common import A1, A10, A11, RESULTS, setup_logging, write_json

COMPS = ("attn.o_proj", "mlp.down_proj")
TAUS = (0.10, 0.25, 0.50, 0.75)


def load_dirs(model: str) -> dict:
    import torch
    m = torch.load(A1 / f"directions/{model}/residual_means_A.pt", map_location="cpu")
    g, b = m["means"][0].float().numpy().astype(np.float64), m["means"][1].float().numpy().astype(np.float64)
    raw = b - g
    delta_norm = np.linalg.norm(raw, axis=1)
    r = raw / np.linalg.norm(raw, axis=1, keepdims=True)
    gd = g / np.linalg.norm(g, axis=1, keepdims=True)
    r = r - (r * gd).sum(1, keepdims=True) * gd
    r = r / np.linalg.norm(r, axis=1, keepdims=True)
    return {"r": r, "delta_norm": delta_norm, "n_layers": r.shape[0] - 1}


def kernel(p: dict, n_layers: int) -> np.ndarray:
    h = np.arange(n_layers, dtype=np.float64)
    dist = np.abs(h - p["max_weight_position"])
    w = p["max_weight"] + (dist / p["min_weight_distance"]) * (p["min_weight"] - p["max_weight"])
    return np.where(dist <= p["min_weight_distance"], w, 0.0)


def v_used(D: dict, direction_index: float | None) -> np.ndarray:
    r, L = D["r"], D["n_layers"]
    if direction_index is None:
        return r[1:L + 1]
    frac, ip = math.modf(direction_index + 1)
    v = r[int(ip)] * (1 - frac) + r[int(ip) + 1] * frac
    v = v / np.linalg.norm(v)
    return np.tile(v, (L, 1))


def descriptors(D: dict, parameters: dict, direction_index: float | None) -> dict:
    L = D["n_layers"]
    V = v_used(D, direction_index)
    R = D["r"][1:L + 1]
    dn = D["delta_norm"][1:L + 1]
    out: dict = {}
    ws = {c: kernel(parameters[c], L) for c in COMPS}
    ws["sum"] = ws[COMPS[0]] + ws[COMPS[1]]
    h = np.arange(L)
    cos = np.abs((V * R).sum(1))
    for c, w in ws.items():
        tag = {"attn.o_proj": "attn", "mlp.down_proj": "mlp", "sum": "sum"}[c]
        for t in TAUS:
            out[f"{tag}_cov{t:.2f}"] = int((w >= t).sum())
        out[f"{tag}_mass"] = float(w.sum())
        out[f"{tag}_energy"] = float((w ** 2 * dn ** 2).sum())
        out[f"{tag}_centroid"] = float((h * w).sum() / w.sum()) if w.sum() > 0 else float("nan")
        out[f"{tag}_partic"] = float(w.sum() ** 2 / (w ** 2).sum()) if (w ** 2).sum() > 0 else 0.0
        out[f"{tag}_A1"] = float((w * cos).sum())
        out[f"{tag}_A2"] = float((w ** 2 * cos ** 2 * dn ** 2).sum())
    out["mean_cos_in_support"] = float(cos[ws["sum"] > 0].mean()) if (ws["sum"] > 0).any() else float("nan")
    return out


@logger.catch(reraise=True)
def main() -> None:
    setup_logging("descriptors")
    jt = pd.read_csv(RESULTS / "journal_trials.csv")
    rows = []
    for model in ("gemma", "gams"):
        D = load_dirs(model)
        for t in jt[jt.model == model].itertuples():
            ap = json.loads(t.abl_params_json)
            di = None if t.direction_scope == "per layer" else float(json.loads(t.params_json)["direction_index"])
            rows.append({"model": model, "trial": int(t.trial), **descriptors(D, ap, di)})
    df = pd.DataFrame(rows)
    # validation on Gemma against art_0XmNBGkzsJc_
    ref = pd.read_csv(A11 / "results/coverage_descriptors.csv")
    ref = ref[ref.source == "iter1_keyword_run"].set_index("trial")
    mine = df[df.model == "gemma"].set_index("trial")
    cols = [c for c in mine.columns if c in ref.columns and c not in ("model",)]
    rel = []
    for c in cols:
        a, b = mine[c].astype(float), ref.loc[mine.index, c].astype(float)
        rel.append(float(np.nanmax(np.abs(a - b) / np.maximum(np.abs(b), 1e-9))))
    val = {"heretic_op_present": (A10 / "heretic_op.py").exists(),
           "substitution": "closed form replicated from art_0XmNBGkzsJc_/coverage.py (heretic_op.py not a declared dependency)",
           "n_columns_compared": len(cols), "max_rel_err": max(rel), "pass": max(rel) < 1e-6,
           "worst_column": cols[int(np.argmax(rel))]}
    write_json(RESULTS / "descriptors_validation.json", val)
    logger.info(f"descriptor validation vs A11 (Gemma, 116 rows x {len(cols)} cols): max rel err {val['max_rel_err']:.2e} pass {val['pass']}")
    if not val["pass"]:
        raise SystemExit("descriptor validation failed - not applying to GaMS3")
    df.to_csv(RESULTS / "candidate_descriptors.csv", index=False)
    logger.info(f"wrote {len(df)} descriptor rows")


if __name__ == "__main__":
    main()
