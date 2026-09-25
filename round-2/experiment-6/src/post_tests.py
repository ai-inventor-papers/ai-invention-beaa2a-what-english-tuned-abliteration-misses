#!/usr/bin/env python3
"""Unit tests that were not run in stage0b, run on a second model instance: U4 (cached-exposure formula vs the PEFT
LoRA path on the same cached inputs, plus realized-vs-cached exposure on X_SET under the edit), U5 (truncated top-256 +
tail KL vs full-vocab KL on 20 Dolly items for 1 edit), and a U7 diagnostic separating attention-mask errors from
bf16/NF4 batch-shape numerics (same-length batches with NO padding vs batch size 1; batched pass repeated twice).

  uv run post_tests.py
"""
from __future__ import annotations

import time

import numpy as np
import torch
from loguru import logger

from common import CACHE, DATA, EXP1, LANGS, RES, jdump, jload, setup_logging
from engine import Engine, red_full_kl, red_kl_nll, red_target, red_topk


@logger.catch(reraise=True)
def main() -> None:
    setup_logging("post_tests")
    torch.cuda.set_per_process_memory_fraction(0.92)  # run alone on host 3 (RTX 2000 Ada 16 GB), after the local judge
    eng = Engine(token_budget=4096)
    dirs = torch.load(EXP1 / "directions" / "gams" / "directions.pt").float()
    man = jload(RES / "edits_manifest.json")
    core = man["core"]
    out = {}
    # ---------------- U4
    eng.apply_edit(core["direction_index"], core["parameters"], dirs)
    fac = eng.lora_factors()
    X = torch.load(CACHE / "x_acts_en.pt")
    rel = []
    for k in list(fac)[::7]:
        l, c = k
        A, B = fac[k]
        if float(B.abs().max()) == 0:
            continue
        x = X[f"{l}|{c}"].cuda()
        z = x.float() @ A.T
        e_formula = ((z @ (B.T @ B)) * z).sum(1)
        m = eng.modules[k]
        with torch.inference_mode():
            y = m.lora_B["default"](m.lora_A["default"](x.to(m.lora_A["default"].weight.dtype)))
        e_peft = y.float().pow(2).sum(1)
        rel.append(float(((e_formula - e_peft).abs().sum() / e_peft.abs().sum()).item()))
    out["U4_formula_vs_peft_path"] = {"n_modules": len(rel), "max_rel_diff": max(rel), "pass": max(rel) <= 1e-3}
    # realized (edited forward on X_SET response tokens) vs cached exposure
    xs = jload(DATA / "x_set.json")["rows"]
    meta = jload(CACHE / "x_acts_meta.json")
    real = {}
    for lang in LANGS:
        ps = [eng.encode_chat(r[lang]) for r in xs]
        eng.reset()
        gg = eng.generate(ps, 48, batch=32, mode="bucket")
        eng.apply_edit(core["direction_index"], core["parameters"], dirs)
        full = [a + b for a, b in zip(ps, gg)]
        em = [list(range(len(a), len(a) + len(b))) for a, b in zip(ps, gg)]
        pos = [[len(s) - 2] for s in full]
        tg = {(i, 0): full[i][-1] for i in range(len(full))}
        o = eng.run(full, pos, red_target(tg), energy_masks=em)
        n = sum(len(b) for b in gg)
        real[lang] = float(np.nansum(o["energy"]) / n)
    rec = [json_line for json_line in (RES / "panel_edits.jsonl").read_text().splitlines() if f'"{core["edit_id"]}"' in json_line]
    import json

    cached = json.loads(rec[0]) if rec else None
    out["U4_realized_vs_cached_core"] = {"realized_E_en_xset": real["en"], "realized_E_sl_xset": real["sl"],
                                         "cached_E_en": cached["E_en"] if cached else None, "cached_E_sl": cached["E_sl"] if cached else None,
                                         "note": "cached exposure uses ORIGINAL-model module inputs; the realized value uses the edited "
                                                 "model's own inputs (upstream edits shift them), so equality is not expected - ratio reported"}
    # ---------------- U5
    kc = torch.load(CACHE / "k_cache.pt", weights_only=False)
    d = kc["en"]
    items = {it["sid"]: it for it in jload(DATA / "s3_items.json")["items"] if it["kind"] == "dolly"}
    sids = d["sids"][:20]
    seqs, pos = [], []
    for j, s in enumerate(sids):
        p = eng.encode_chat(items[s]["en"])
        c = d["cont"][j]
        seqs.append(p + c)
        pos.append(list(range(len(p) - 1, len(p) - 1 + len(c))))
    eng.reset()
    full_ref = eng.run(seqs, pos, lambda lp, meta: lp.half())["out"]
    e1 = man["E0"][2]
    eng.apply_edit(e1["direction_index"], e1["parameters"], dirs)
    rf = {(i, k): torch.as_tensor(full_ref[i][k]).float().cuda() for i in range(len(seqs)) for k in range(len(pos[i]))}
    fk = eng.run(seqs, pos, red_full_kl(rf))["out"]
    ri = {(i, k): torch.as_tensor(d["top_idx"][j][k]).cuda() for i, j in enumerate(range(20)) for k in range(len(pos[i]))}
    rl = {(i, k): torch.as_tensor(d["top_lp"][j][k]).cuda() for i, j in enumerate(range(20)) for k in range(len(pos[i]))}
    tg = {(i, k): seqs[i][p + 1] for i in range(len(seqs)) for k, p in enumerate(pos[i])}
    tk = eng.run(seqs, pos, red_kl_nll(ri, rl, tg))["out"]
    full_kl = np.array([x[:, 0].mean() for x in fk])
    tr_kl = np.array([x[:, 0].mean() for x in tk])
    out["U5_truncated_vs_full_KL"] = {"edit": e1["edit_id"], "mean_full": float(full_kl.mean()), "mean_trunc": float(tr_kl.mean()),
                                      "ratio_trunc_over_full": float(tr_kl.mean() / full_kl.mean()), "pass": bool(tr_kl.mean() / full_kl.mean() >= 0.95),
                                      "note": "truncated reference from the stage0d cache (batched); full reference recomputed here "
                                              "(different batch shapes add bf16 noise to both)"}
    # ---------------- U7 diagnostic
    eng.reset()
    fl = [it for it in jload(DATA / "s3_items.json")["items"] if it["kind"] == "flores"]
    enc = [eng.encode_plain(it["en"]) for it in fl]
    by = {}
    for i, s in enumerate(enc):
        by.setdefault(len(s), []).append(i)
    same = max(by.values(), key=len)[:8]
    S = [enc[i] for i in same]
    P = [list(range(0, len(s) - 1)) for s in S]
    T = {(i, k): S[i][p + 1] for i in range(len(S)) for k, p in enumerate(P[i])}
    a = eng.run(S, P, red_target(T))["out"]
    a2 = eng.run(S, P, red_target(T))["out"]
    tb = eng.token_budget
    eng.token_budget = 1
    b1 = eng.run(S, P, red_target(T))["out"]
    eng.token_budget = tb
    mixed = [enc[i] for i in range(0, 40)]
    Pm = [list(range(0, len(s) - 1)) for s in mixed]
    Tm = {(i, k): mixed[i][p + 1] for i in range(len(mixed)) for k, p in enumerate(Pm[i])}
    am = eng.run(mixed, Pm, red_target(Tm))["out"]
    eng.token_budget = 1
    bm = eng.run(mixed, Pm, red_target(Tm))["out"]
    eng.token_budget = tb
    dm = np.concatenate([np.abs(x - y).ravel() for x, y in zip(am, bm)])
    ds = np.concatenate([np.abs(x - y).ravel() for x, y in zip(a, b1)])
    out["U7_diagnostic"] = {
        "same_length_no_padding_vs_bs1": {"n_seq": len(S), "max_abs": float(ds.max()), "mean_abs": float(ds.mean())},
        "padded_mixed_vs_bs1": {"n_seq": len(mixed), "max_abs": float(dm.max()), "mean_abs": float(dm.mean()),
                                "per_seq_mean_nll_max_abs_diff": float(max(abs(x.mean() - y.mean()) for x, y in zip(am, bm)))},
        "batched_repeat_bit_identical": bool(all(np.array_equal(x, y) for x, y in zip(a, a2))),
        "interpretation": "if unpadded same-length batches differ from batch size 1 by the same magnitude as padded batches, the "
                          "difference is batch-shape numerics (bf16 / NF4 GEMM tiling), not an attention-mask error"}
    out["t"] = time.time()
    jdump(out, RES / "post_tests.json")
    logger.info(f"post tests: {out}")


if __name__ == "__main__":
    main()
