#!/usr/bin/env python3
"""Descriptive geometry of the two models' Heretic refusal directions (CPU, from directions/*.pt).

GaMS3-12B-Instruct is a Slovene continued-pretrain of the Gemma-3-12B family: same architecture,
same 262k tokenizer, same residual width, so the two models' residual coordinates are nominally the
same basis (drifted by training) and a per-layer cosine is computable. It is reported as GEOMETRY
ONLY: a cosine between two models' difference-of-means vectors is not evidence of a shared mechanism,
and this artifact's causal statement about transfer comes from the swap test, not from this number.

Also reports, per layer: the norm of each model's harmful-minus-harmless difference before
normalisation (edit "signal size"), the cosine before vs after Heretic's orthogonalisation step, and
the cosine of the harmless means themselves (a baseline for how much of the agreement is just shared
representation drift rather than anything refusal-specific).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import torch
import torch.nn.functional as F
from loguru import logger

WS = Path(__file__).resolve().parent
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")


def load(tag: str) -> dict:
    d = torch.load(WS / "directions" / tag / "residual_means_A.pt")
    good, bad = d["means"][0].double(), d["means"][1].double()
    raw = bad - good
    rd = F.normalize(raw, p=2, dim=1)
    gd = F.normalize(good, p=2, dim=1)
    orth = F.normalize(rd - (rd * gd).sum(1, keepdim=True) * gd, p=2, dim=1)
    return {"good": good, "bad": bad, "raw": raw, "rd": rd, "orth": orth, "gd": gd}


def main() -> None:
    A, B = load("gams"), load("gemma")
    n = A["rd"].shape[0]
    rows = []
    for l in range(n):
        rows.append({
            "row": l, "layer": l - 1,  # row 0 = embeddings; abliterate() uses residual_directions[layer+1]
            "cos_diff_raw": float(F.cosine_similarity(A["rd"][l], B["rd"][l], dim=0)),
            "cos_diff_orthogonalized": float(F.cosine_similarity(A["orth"][l], B["orth"][l], dim=0)),
            "cos_harmless_mean": float(F.cosine_similarity(A["good"][l], B["good"][l], dim=0)),
            "norm_diff_gams": float(A["raw"][l].norm()), "norm_diff_gemma": float(B["raw"][l].norm()),
            "norm_harmless_gams": float(A["good"][l].norm()), "norm_harmless_gemma": float(B["good"][l].norm()),
            "cos_within_gams_raw_vs_orth": float(F.cosine_similarity(A["rd"][l], A["orth"][l], dim=0)),
            "cos_within_gemma_raw_vs_orth": float(F.cosine_similarity(B["rd"][l], B["orth"][l], dim=0)),
        })
    # a random-direction control: cosine between two independent random unit vectors of this width
    g = torch.Generator().manual_seed(0)
    d = A["rd"].shape[1]
    rc = [float(F.cosine_similarity(torch.randn(d, generator=g), torch.randn(d, generator=g), dim=0))
          for _ in range(200)]
    out = {"n_rows": n, "width": d, "per_layer": rows,
           "random_direction_control": {"mean_abs_cos": float(torch.tensor(rc).abs().mean()),
                                        "max_abs_cos": float(torch.tensor(rc).abs().max())},
           "summary": {
               "cos_orth_mean_layers_24_47": float(torch.tensor([r["cos_diff_orthogonalized"]
                                                                for r in rows if 24 <= r["layer"] <= 47]).mean()),
               "cos_orth_mean_all": float(torch.tensor([r["cos_diff_orthogonalized"] for r in rows]).mean()),
               "cos_harmless_mean_all": float(torch.tensor([r["cos_harmless_mean"] for r in rows]).mean()),
           },
           "caveat": ("Cosines are GEOMETRY ONLY. Both models share the Gemma-3 architecture and tokenizer, "
                      "so the coordinates are nominally comparable, but a high cosine between two models' "
                      "difference-of-means vectors is not evidence of a shared causal mechanism, and the "
                      "cos_harmless_mean column shows how much agreement is generic representation overlap.")}
    (WS / "results").mkdir(exist_ok=True)
    (WS / "results" / "direction_geometry.json").write_text(json.dumps(out, indent=1))
    logger.info(json.dumps(out["summary"], indent=1))
    logger.info(f"random-direction control |cos|: mean {out['random_direction_control']['mean_abs_cos']:.4f}")


if __name__ == "__main__":
    main()
