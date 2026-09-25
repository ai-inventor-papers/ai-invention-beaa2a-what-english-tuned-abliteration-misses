#!/usr/bin/env python3
"""Host-offset check for the K trait (CPU only, no model).

The panel was scored on two RTX 4090 hosts (host 1: E0_000..E0_050; host 2: every later edit) against an original-model
reference cached on host 1. repro_check.py re-scored three edits on a third GPU type (RTX 2000 Ada) and found per-item KL
differences of 17-26% of the mean for weak edits, so this script tests whether host 2 shifted K relative to host 1:
OLS of log KL_en on [1, log lora_fro, log lora_fro^2, host2] over all panel edits (and within E0 only).
Writes the block `host1_vs_host2_K_offset_check` into results/repro_check.json.

  uv run host_check.py
"""
from __future__ import annotations

import json

import numpy as np
from loguru import logger

from common import RES, jdump, jload, setup_logging


@logger.catch(reraise=True)
def main() -> None:
    setup_logging("host_check")
    rows = [json.loads(l) for l in (RES / "panel_edits.jsonl").read_text().splitlines() if l.strip()]
    host2 = np.array([not (r["set"] == "E0" and r["edit_id"] <= "E0_050") for r in rows], float)
    x = np.log(np.array([r["lora_fro_attn"] + r["lora_fro_mlp"] for r in rows]) + 1e-9)
    e0 = np.array([r["set"] == "E0" for r in rows])
    out = {"method": "OLS of log KL_<lang> on [1, log lora_fro, log lora_fro^2, host2] (host 1 = E0_000..E0_050, host 2 = the rest; both RTX 4090)"}
    for lang in ("en", "sl"):
        y = np.log(np.array([r[f"KL_{lang}"] for r in rows]))
        A = np.c_[np.ones_like(x), x, x ** 2, host2]
        b = np.linalg.lstsq(A, y, rcond=None)[0]
        b0 = np.linalg.lstsq(A[e0], y[e0], rcond=None)[0]
        k = np.array([r[f"KL_{lang}"] for r in rows])
        out[lang] = {"host2_offset_log_units": float(b[3]), "residual_sd_log_units": float(np.std(y - A @ b)),
                     "within_E0_only_offset": float(b0[3]), "n_host2_in_E0": int(host2[e0].sum()),
                     "host1_min5_KL": np.sort(k[host2 == 0])[:5].tolist(), "host2_min5_KL": np.sort(k[host2 == 1])[:5].tolist()}
    big = max(abs(out[l]["host2_offset_log_units"]) for l in ("en", "sl"))
    out["conclusion"] = (f"max |host-2 offset| = {big:.3f} log units vs residual SD ~{out['en']['residual_sd_log_units']:.2f}: "
                         + ("no detectable host offset in K between the two RTX 4090 hosts" if big < 0.1 else "HOST OFFSET DETECTED"))
    p = RES / "repro_check.json"
    d = jload(p) if p.exists() else {}
    d["host1_vs_host2_K_offset_check"] = out
    jdump(d, p)
    logger.info(json.dumps(out)[:600])


if __name__ == "__main__":
    main()
