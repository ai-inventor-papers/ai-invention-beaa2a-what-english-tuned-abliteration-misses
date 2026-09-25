#!/usr/bin/env python3
"""Slim the direction archives once every phase that needs them has run.
`results/<m>/directions.npz` is ~80 MB, almost all of it `pcs`: the top-100 harmless principal-component basis per hidden
index, used only to draw the matched random control directions. It is a construction detail, it is fully regenerable from
the DEV captures, and it would otherwise dominate the published repository. This script moves it to
`results/<m>/harmless_pcs.npy` (declared `delete: regenerable` in .aii/manifest.yaml) and rewrites `directions.npz` with
just the vectors the paper and any later round actually read: d_EN(h), d_SL/d_DE/d_LT(h), the Heretic-orthogonalised
v(h), the harmless mean and h*.
Safe to re-run: if `pcs` is already absent, nothing happens."""
from __future__ import annotations

import numpy as np
from loguru import logger

import common as C


def main() -> None:
    C.setup_logging("cleanup")
    out = {}
    for m in sorted(p.name for p in C.RES.iterdir() if (p / "directions.npz").exists()):
        p = C.RES / m / "directions.npz"
        z = np.load(p)
        keys = list(z.files)
        if "pcs" not in keys:
            out[m] = {"already_slim": True, "size_mb": round(p.stat().st_size / 1e6, 1)}
            continue
        before = p.stat().st_size
        np.save(C.RES / m / "harmless_pcs.npy", z["pcs"])
        np.savez(p, **{k: z[k] for k in keys if k != "pcs"})
        out[m] = {"size_mb_before": round(before / 1e6, 1), "size_mb_after": round(p.stat().st_size / 1e6, 1),
                  "pcs_moved_to": f"results/{m}/harmless_pcs.npy",
                  "pcs_mb": round((C.RES / m / "harmless_pcs.npy").stat().st_size / 1e6, 1), "kept_keys": [k for k in keys if k != "pcs"]}
        logger.info(f"{m}: directions.npz {out[m]['size_mb_before']} -> {out[m]['size_mb_after']} MB")
    C.jdump({"note": "pcs = top-100 harmless PC basis per hidden index; used only to draw matched random controls; "
                     "regenerable with `uv run code/run_model.py --model <m> --phase dev` (build_directions)",
             "models": out}, C.RES / "cleanup.json")


if __name__ == "__main__":
    main()
