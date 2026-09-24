#!/usr/bin/env python3
"""STEP 0.3 (EXPLORATORY) - zero-GPU coverage readout: describe every candidate Heretic kernel by where, how
strongly and along which direction it edits.

Kernel (Heretic 3521f864 model.abliterate, reproduced exactly): for component c at layer h,
    w_c(h) = max_w + (|h - pos| / dist) * (min_w_eff - max_w)   if |h - pos| <= dist, else 0,
with min_w_eff = p.min_weight * max_w (p.* stores a FRACTION; abl_params stores the effective value - verified in RUNG 0).
Direction used at layer h: per-layer scope -> r(h) = Heretic's own direction of layer h (row h+1; row 0 = embeddings);
global scope -> normalize(lerp(r[int(i+1)], r[int(i+1)+1], frac(i+1))) at every layer, i = direction_index.
Reference direction d_EN(h): (a) Heretic's own per-layer directions (primary; cos == 1 for per-layer scope),
(b) the frozen art_hmbXDppkPZnR per-layer English refusal directions (dEN, secondary / independent).

Descriptors per component and for the two components summed:
  cov_tau  = #{h : w(h) >= tau}, tau in {.10,.25,.50,.75};  mass = sum w;  energy = sum w^2 ||delta_h||^2
  centroid = sum h w / sum w;  partic = (sum w)^2 / sum w^2  (effective #layers)
  A1 = sum w |cos(v_used(h), d_EN(h))|;  A2 = sum w^2 cos^2 ||delta_h||^2       (ALIGNED coverage)
||delta_h|| = norm of the raw harmful-minus-harmless residual mean difference at layer h (iteration-1 capture).

  python coverage.py            -> results/coverage_descriptors.csv, results/coverage_summary.json
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

WS = Path(__file__).resolve().parent
RUN = Path("/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop")
W1 = RUN / "iter_1/gen_art/gen_art_experiment_1"
W8 = RUN / "iter_2/gen_art/gen_art_experiment_8"
N_LAYERS = 48
COMPS = ("attn.o_proj", "mlp.down_proj")
TAUS = (0.10, 0.25, 0.50, 0.75)
# community edit p-e-w/gemma-3-12b-it-heretic @ e037e6e1, from its own model card (art_m6pglf516e2r copy)
COMMUNITY = {"direction_scope": "per layer", "direction_index": None,
             "parameters": {"attn.o_proj": {"max_weight": 1.48, "max_weight_position": 34.12, "min_weight": 0.94,
                                            "min_weight_distance": 19.48},
                            "mlp.down_proj": {"max_weight": 0.81, "max_weight_position": 35.83, "min_weight": 0.52,
                                              "min_weight_distance": 1.66}}}

_CACHE: dict = {}


def load_dirs() -> dict:
    if _CACHE:
        return _CACHE
    import torch
    m = torch.load(W1 / "directions/gemma/residual_means_A.pt", map_location="cpu")
    g, b = m["means"][0].float().numpy(), m["means"][1].float().numpy()
    raw = b - g
    delta_norm = np.linalg.norm(raw, axis=1)
    r = raw / np.linalg.norm(raw, axis=1, keepdims=True)
    gd = g / np.linalg.norm(g, axis=1, keepdims=True)
    r = r - (r * gd).sum(1, keepdims=True) * gd  # orthogonalize_direction = true (stored settings)
    r = r / np.linalg.norm(r, axis=1, keepdims=True)
    z = np.load(W8 / "directions/gemma_all_layers.npz")
    d8 = z["dEN"].astype(np.float64)
    d8 = d8 / np.maximum(np.linalg.norm(d8, axis=1, keepdims=True), 1e-12)
    _CACHE.update({"r": r, "delta_norm": delta_norm, "d8": d8})
    return _CACHE


def kernel(p: dict) -> np.ndarray:
    h = np.arange(N_LAYERS, dtype=np.float64)
    dist = np.abs(h - p["max_weight_position"])
    w = p["max_weight"] + (dist / p["min_weight_distance"]) * (p["min_weight"] - p["max_weight"])
    return np.where(dist <= p["min_weight_distance"], w, 0.0)


def v_used(direction_index: float | None) -> np.ndarray:
    r = load_dirs()["r"]
    if direction_index is None:
        return r[1:N_LAYERS + 1]
    frac, ip = math.modf(direction_index + 1)
    v = r[int(ip)] * (1 - frac) + r[int(ip) + 1] * frac
    v = v / np.linalg.norm(v)
    return np.tile(v, (N_LAYERS, 1))


def descriptors(parameters: dict, direction_index: float | None) -> dict:
    D = load_dirs()
    V = v_used(direction_index)
    refs = {"": D["r"][1:N_LAYERS + 1], "_x8": D["d8"][1:N_LAYERS + 1]}
    dn = D["delta_norm"][1:N_LAYERS + 1]
    out: dict = {}
    ws = {c: kernel(parameters[c]) for c in COMPS}
    ws["sum"] = ws[COMPS[0]] + ws[COMPS[1]]
    h = np.arange(N_LAYERS)
    for c, w in ws.items():
        tag = {"attn.o_proj": "attn", "mlp.down_proj": "mlp", "sum": "sum"}[c]
        for t in TAUS:
            out[f"{tag}_cov{t:.2f}"] = int((w >= t).sum())
        out[f"{tag}_mass"] = float(w.sum())
        out[f"{tag}_energy"] = float((w ** 2 * dn ** 2).sum())
        out[f"{tag}_centroid"] = float((h * w).sum() / w.sum()) if w.sum() > 0 else float("nan")
        out[f"{tag}_partic"] = float(w.sum() ** 2 / (w ** 2).sum()) if (w ** 2).sum() > 0 else 0.0
        for sfx, R in refs.items():
            cos = np.abs((V * R).sum(1))
            out[f"{tag}_A1{sfx}"] = float((w * cos).sum())
            out[f"{tag}_A2{sfx}"] = float((w ** 2 * cos ** 2 * dn ** 2).sum())
    cos = np.abs((V * refs[""]).sum(1))
    out["mean_cos_in_support"] = float(cos[ws["sum"] > 0].mean()) if (ws["sum"] > 0).any() else float("nan")
    return out


def main() -> None:
    tr = pd.read_csv(W1 / "results/trials_gemma.csv")
    tr = tr[tr["state"] == "COMPLETE"]
    rows = []
    rung0 = []
    for _, t in tr.iterrows():
        ap = json.loads(t["abl_params"])
        di = None if t["p.direction_scope"] == "per layer" else float(t["p.direction_index"])
        for c in COMPS:  # RUNG 0 identity: effective min = fraction * max
            rung0.append(abs(t[f"p.{c}.min_weight"] * max(0.0, t[f"p.{c}.max_weight"]) - ap[c]["min_weight"]))
        d = descriptors(ap, di)
        rows.append({"source": "iter1_keyword_run", "trial": int(t["number"]), "direction_scope": t["p.direction_scope"],
                     "direction_index": di, "keyword_refusals": int(t["refusals"]), "kl": float(t["kl"]), **d})
    comm = descriptors(COMMUNITY["parameters"], None)
    rows.append({"source": "community_ref", "trial": -1, "direction_scope": "per layer", "direction_index": None,
                 "keyword_refusals": 3, "kl": 0.16, **comm})
    # sensitivity: if the card's min_weight were a FRACTION (not the effective value)
    alt = json.loads(json.dumps(COMMUNITY["parameters"]))
    for c in COMPS:
        alt[c]["min_weight"] = alt[c]["min_weight"] * alt[c]["max_weight"]
    rows.append({"source": "community_ref_minw_as_fraction", "trial": -2, "direction_scope": "per layer",
                 "direction_index": None, "keyword_refusals": 3, "kl": 0.16, **descriptors(alt, None)})
    df = pd.DataFrame(rows)
    out = WS / "results/coverage_descriptors.csv"
    df.to_csv(out, index=False)
    it = df[df.source == "iter1_keyword_run"]
    keys = [k for k in df.columns if k.startswith(("sum_", "attn_", "mlp_"))] + ["mean_cos_in_support"]
    corr = {}
    for k in keys:
        a = spearmanr(it[k], it["keyword_refusals"], nan_policy="omit")
        b = spearmanr(it[k], it["kl"], nan_policy="omit")
        corr[k] = {"rho_keyword_refusals": float(a.statistic), "p_kw": float(a.pvalue),
                   "rho_kl": float(b.statistic), "p_kl": float(b.pvalue)}
    t96 = df[(df.source == "iter1_keyword_run") & (df.trial == 96)].iloc[0].to_dict()
    summ = {"label": "EXPLORATORY (post hoc over saved parameters)",
            "rung0_min_weight_identity_max_abs_err": float(max(rung0)),
            "rung0_pass": bool(max(rung0) < 1e-9),
            "trial96": {k: t96[k] for k in ["direction_scope", "direction_index", "sum_mass", "sum_A1", "sum_A1_x8",
                                             "sum_A2", "attn_cov0.10", "mlp_cov0.10", "sum_partic", "sum_centroid",
                                             "mean_cos_in_support"]},
            "community": {k: comm[k] for k in ["sum_mass", "sum_A1", "sum_A1_x8", "sum_A2", "attn_cov0.10",
                                               "mlp_cov0.10", "sum_partic", "sum_centroid", "mean_cos_in_support"]},
            "rung1_checks": {
                "trial96_is_global": t96["direction_scope"] == "global",
                "raw_mass_orders_community_above_t96": bool(comm["sum_mass"] > t96["sum_mass"]),
                "A1_orders_community_above_t96": bool(comm["sum_A1"] > t96["sum_A1"]),
                "A1x8_orders_community_above_t96": bool(comm["sum_A1_x8"] > t96["sum_A1_x8"]),
                "community_mlp_cov0.10": int(comm["mlp_cov0.10"])},
            "spearman_over_116_iter1_trials": corr}
    (WS / "results/coverage_summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps({k: summ[k] for k in ["rung0_pass", "trial96", "community", "rung1_checks"]}, indent=1))


if __name__ == "__main__":
    main()
