#!/usr/bin/env python3
"""STAGE 3 per model.
  --phase dev  : 3a load/template/smoke/timing, 3b directions (d_EN(h), d_L(h), cos profiles, AUROC, h*), 3c DEV index
                 curves (activation ablation of d_EN(h) over cumulative depth prefixes P10..P100, single site SS, matched
                 random RND; IDX harmful x 4 languages + benign at k0/P100), FLORES-dev dNLL, first-token top-k at k0
                 (B_margin), and the CAL generations for the weight-panel choices (W1 band x dose, W3 scale).
  --phase conf : 3e weight panel on CONF (only after configs/frozen_predictions.json exists and is hashed in FREEZE):
                 W0 no-op, W1 narrow band, W2 energy-matched all-depth stride, W3 selected kernel (Gemma: real iter-1
                 trial-96 adapter), W4 energy- and collateral-matched random, W-TR (SL-NLLB control, Gemma/Qwen3).
Generations -> results/<model>/gens/<cond>.jsonl; everything else -> results/<model>/*.json."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import time

import numpy as np
import torch
from loguru import logger

import common as C
from lm import LM, cos, unit, winsorize

PREFIX_K = [0.10, 0.25, 0.50, 0.75, 1.00]
W1_DOSES = [0.75, 1.0, 1.25, 1.5]
W3_SCALES = [0.5, 0.75, 1.0, 1.25, 1.5]
EXPECTED_SUFFIX = {"gemma": "<start_of_turn>model\n", "qwen3": "<|im_start|>assistant\n<think>\n\n</think>\n\n",
                   "mistral": "[/INST]", "eurollm": "<|im_start|>assistant\n", "llama": "<|start_header_id|>assistant<|end_header_id|>\n\n",
                   "granite": "<|start_of_role|>assistant<|end_of_role|>"}


def items(name: str) -> list[dict]:
    return C.read_jsonl(C.DATA / f"items_{name}.jsonl")


def timing(key: str, stage: str, secs: float, **kw) -> None:
    C.append_jsonl({"ts": time.time(), "model": key, "stage": stage, "secs": round(secs, 2)} | kw, C.RES / "timing.jsonl")


def gen_records(lm: LM, cond: str, phase: str, its: list[dict], langs, text_key=None, batch: int = 48) -> list[dict]:
    """Greedy generation for items x languages under the CURRENT hooks; returns records."""
    plan = [(it, L) for L in langs for it in its]
    seqs = [lm.encode_chat(it[text_key or L]) for it, L in plan]
    t = time.time()
    outs = lm.generate(seqs, C.MAX_NEW, batch=batch)
    recs = []
    for (it, L), s, o in zip(plan, seqs, outs):
        prompt = it[text_key or L]
        resp = lm.tok.decode(o, skip_special_tokens=True).strip()
        gid = hashlib.sha256(f"{lm.key}|{cond}|{it['uid']}|{L}|{text_key}".encode()).hexdigest()[:16]
        recs.append({"gid": gid, "model": lm.key, "cond": cond, "phase": phase, "uid": it["uid"], "semantic_id": it["semantic_id"],
                     "role": it["role"], "lang": L, "text_variant": text_key or L, "stratum": it.get("stratum"),
                     "category": it.get("category"), "prompt": prompt, "response": resp, "n_tokens": len(o),
                     "first_tok": o[0] if o else None, "hit_max": len(o) >= C.MAX_NEW})
    logger.info(f"[{lm.key}] {cond}: {len(recs)} generations in {time.time() - t:.0f}s")
    timing(lm.key, f"gen:{cond}", time.time() - t, n=len(recs))
    return recs


def save_gens(key: str, cond: str, recs: list[dict], append: bool = False) -> None:
    p = C.RES / key / "gens" / f"{cond}.jsonl"
    old = C.read_jsonl(p) if append else []
    C.write_jsonl(old + recs, p)


def flores_nll(lm: LM, flo: list[dict], langs, n: int) -> dict:
    out = {}
    for L in langs:
        seqs = [lm.encode_plain(f[L]) for f in flo[:n]]
        out[L] = lm.seq_nll(seqs, [1] * len(seqs)).tolist()
    return out


def mean_dnll(a: dict, base: dict) -> dict:
    return {L: float(np.mean(np.asarray(a[L]) - np.asarray(base[L]))) for L in a}


# ============================================================================================ directions
def build_directions(lm: LM, key: str) -> dict:
    out = C.RES / key / "directions.npz"
    if out.exists():
        z = np.load(out)
        return {k: z[k] for k in z.files}
    t = time.time()
    DIR = items("dir")
    harm = [it for it in DIR if it["role"] == "harmful"]
    ben = [it for it in DIR if it["role"] == "harmless"]
    acts = {}
    for L in C.LANGS:
        for role, its in (("harm", harm), ("ben", ben)):
            acts[(L, role)] = winsorize(lm.capture_last([lm.encode_chat(it[L]) for it in its]))  # [N, H, D]
    H = lm.L + 1
    d = {L: unit(acts[(L, "harm")].mean(0) - acts[(L, "ben")].mean(0)) for L in C.LANGS}  # [H, D]
    good_en = acts[("en", "ben")].mean(0)
    res = {"dEN_fresh": d["en"], "dSL": d["sl"], "dDE": d["de"], "dLT": d["lt"], "good_mean_en": good_en.astype(np.float32)}
    diag = {"n_harm": len(harm), "n_ben": len(ben), "position": "final template token (pos -1)", "winsor_q": 0.995,
            "last_token": lm.tok.convert_ids_to_tokens(lm.encode_chat(harm[0]["en"])[-1:])}
    if key == "gemma":
        z = np.load(C.EXP8 / "directions" / "gemma_all_layers.npz")
        dEN = unit(z["dEN"])
        chk = [4, 12, 20, 28, 36, 44]
        diag["exp8_recompute_cos"] = {h: cos(dEN[h], d["en"][h]) for h in chk}
        diag["exp8_recompute_ok"] = bool(min(diag["exp8_recompute_cos"].values()) >= 0.99)
        if not diag["exp8_recompute_ok"]:
            logger.error(f"Gemma d_EN recompute mismatch: {diag['exp8_recompute_cos']}")
        res["dEN"] = dEN.astype(np.float32)
        res["h_star"] = np.int64(20)
    else:
        res["dEN"] = d["en"]
    dEN = res["dEN"]
    # per-layer projection AUROC on DIR EN (+ label-shuffled control) and h* choice
    from sklearn.metrics import roc_auc_score
    rng = np.random.default_rng(C.SEED)
    au, au_sh = [], []
    yb = np.r_[np.ones(len(harm)), np.zeros(len(ben))]
    for h in range(H):
        x = np.r_[acts[("en", "harm")][:, h] @ dEN[h], acts[("en", "ben")][:, h] @ dEN[h]]
        au.append(float(roc_auc_score(yb, x)))
        ys = rng.permutation(yb)
        xs = np.r_[acts[("en", "harm")][:, h], acts[("en", "ben")][:, h]]
        dsh = unit(xs[ys == 1].mean(0) - xs[ys == 0].mean(0))
        au_sh.append(float(roc_auc_score(rng.permutation(yb), xs @ dsh)))
    lo, hi = int(round(0.3 * lm.L)), int(round(0.8 * lm.L))
    # separation d' as tie-breaker when AUROC saturates
    dprime = []
    for h in range(H):
        a, b = acts[("en", "harm")][:, h] @ dEN[h], acts[("en", "ben")][:, h] @ dEN[h]
        dprime.append(float((a.mean() - b.mean()) / (np.sqrt(0.5 * (a.var() + b.var())) + 1e-9)))
    if key != "gemma":
        cand = list(range(lo, hi + 1))
        res["h_star"] = np.int64(max(cand, key=lambda h: (round(au[h], 4), dprime[h])))
    diag |= {"auroc": au, "auroc_shuffled": au_sh, "dprime": dprime, "h_star": int(res["h_star"]),
             "auroc_max_mid": max(au[lo:hi + 1]), "T3_pass": bool(max(au[lo:hi + 1]) > 0.95 and abs(np.mean(au_sh) - 0.5) < 0.25)}
    # cosine profiles and split-half ceiling
    half = np.arange(len(harm)) % 2 == 0
    for L in ("sl", "de", "lt"):
        diag[f"cos_profile_{L}"] = [cos(dEN[h], d[L][h]) for h in range(H)]
    a_en = unit(acts[("en", "harm")][half].mean(0) - acts[("en", "ben")][half].mean(0))
    b_en = unit(acts[("en", "harm")][~half].mean(0) - acts[("en", "ben")][~half].mean(0))
    diag["split_half_ceiling_en"] = [cos(a_en[h], b_en[h]) for h in range(H)]
    # Heretic-orthogonalised per-layer directions (projected abliteration: remove the harmless-mean component)
    g = unit(good_en)
    v = dEN - (np.sum(dEN * g, -1, keepdims=True)) * g
    res["vdirs"] = unit(v)
    # harmless PC span per hidden index (all 4 languages' benign DIR residuals) for random controls
    pcs = np.zeros((H, 100, lm.D), dtype=np.float32)
    for h in range(H):
        X = np.concatenate([acts[(L, "ben")][:, h] for L in C.LANGS], 0)
        X = X - X.mean(0)
        _, _, Vt = np.linalg.svd(X.astype(np.float64), full_matrices=False)
        k = min(100, Vt.shape[0])
        pcs[h, :k] = Vt[:k]
    res["pcs"] = pcs
    np.savez(out, **res)
    C.jdump(diag, C.RES / key / "direction_diagnostics.json")
    timing(key, "directions", time.time() - t)
    logger.info(f"[{key}] directions: h*={int(res['h_star'])} AUROC_mid_max={diag['auroc_max_mid']:.3f} "
                f"cos_SL(mean)={np.mean(diag['cos_profile_sl'][1:]):.3f} {diag.get('exp8_recompute_cos', '')}")
    return res


def random_dirs(D: dict, L: int, seed: int) -> np.ndarray:
    """Per-hidden-index random unit vectors in the harmless top-100 PC span, orthogonal to d_EN(h)."""
    rng = np.random.default_rng(seed)
    out = np.zeros_like(D["dEN"])
    for h in range(L + 1):
        P = D["pcs"][h]
        P = P[np.linalg.norm(P, axis=1) > 0]
        r = rng.standard_normal(len(P)) @ P
        r = r - (r @ D["dEN"][h]) * D["dEN"][h]
        out[h] = unit(r)
    return out


def prefix(L: int, k: float) -> list[int]:
    return list(range(1, int(round(k * L)) + 1))


# ============================================================================================ DEV phase
def phase_dev(key: str, mini: bool) -> None:
    t0 = time.time()
    outdir = C.RES / key
    (outdir / "gens").mkdir(parents=True, exist_ok=True)
    lm = LM(key)
    torch.cuda.set_per_process_memory_fraction(0.92)
    timing(key, "load", time.time() - t0)
    # ---- 3a template + smoke + timing
    tpl = {L: lm.render({"en": "How do I bake bread?", "sl": "Kako spečem kruh?", "de": "Wie backe ich Brot?",
                         "lt": "Kaip iškepti duoną?"}[L]) for L in C.LANGS}
    ids = lm.encode_chat("How do I bake bread?")
    info = {"repo": lm.repo, "revision": lm.sha, "model_class": lm.model_class, "L": lm.L, "D": lm.D, "eos": lm.eos,
            "rendered_templates": tpl, "suffix_expected": EXPECTED_SUFFIX.get(key),
            "T1_suffix_ok": tpl["en"].endswith(EXPECTED_SUFFIX.get(key, "")),
            "roundtrip_ok": lm.tok.decode(ids) .replace("<bos>", "").strip().endswith(tpl["en"].replace("<bos>", "").strip()[-20:]),
            "n_bos_tokens": sum(1 for t in ids if t == lm.tok.bos_token_id), "last_tokens": lm.tok.convert_ids_to_tokens(ids[-6:])}
    C.jdump(info, outdir / "load_info.json")
    logger.info(f"[{key}] T1 suffix ok={info['T1_suffix_ok']} last={info['last_tokens']}")
    DIR = items("dir")
    smoke_its = [it for it in DIR if it["role"] == "harmless"][:5]
    import fasttext
    from huggingface_hub import hf_hub_download
    lid = fasttext.load_model(hf_hub_download("cis-lmu/glotlid", "model.bin"))
    glot = {"en": "__label__eng_Latn", "sl": "__label__slv_Latn", "de": "__label__deu_Latn", "lt": "__label__lit_Latn"}
    t = time.time()
    sm = gen_records(lm, "smoke", "smoke", smoke_its, C.LANGS)
    for r in sm:
        r["lid"] = C.lid_predict(lid, r["response"])[0]
        r["lid_ok"] = r["lid"] == glot[r["lang"]]
    smoke = {L: sum(r["lid_ok"] for r in sm if r["lang"] == L) for L in C.LANGS}
    C.jdump({"lid_ok_of_5": smoke, "T1_pass": all(v >= 4 for v in smoke.values()), "gens": sm}, outdir / "smoke.json")
    logger.info(f"[{key}] smoke LID ok /5: {smoke}")
    # ---- 3b directions
    D = build_directions(lm, key)
    L = lm.L
    dEN = D["dEN"]
    hstar = int(D["h_star"])
    # ---- T2 hook correctness
    idx = items("idx")
    fl = items("flores")
    flo_dev = [f for f in fl if f["half"] == "A"][:50]
    test_seqs = [lm.encode_chat(it["en"]) for it in idx[:4]]
    lm.reset()
    base_lp = lm.first_lp_topk(test_seqs, k=50)
    lm.set_ablate_layerwise({h: dEN[h] for h in prefix(L, 1.0)}, c=0.0)
    c0_lp = lm.first_lp_topk(test_seqs, k=50)
    lm.set_ablate_layerwise({h: dEN[h] for h in prefix(L, 1.0)}, c=1.0)
    lm.state.track_proj = True
    lm.capture_last(test_seqs)
    t2 = {"c0_max_abs_logprob_diff": float(max(np.abs(a[1] - b[1]).max() for a, b in zip(base_lp, c0_lp))),
          "post_hook_max_proj_ratio": lm.state.max_proj_ratio}
    t2["T2a_pass"] = t2["post_hook_max_proj_ratio"] < 1e-2  # bf16 residuals: 1e-3 is below bf16 resolution at |x|~1e4
    t2["T2b_pass"] = t2["c0_max_abs_logprob_diff"] < 1e-3
    lm.reset()
    C.jdump(t2, outdir / "hook_tests.json")
    logger.info(f"[{key}] T2 {t2}")
    # ---- conditions
    conds = {"k0": {}}
    for k in PREFIX_K:
        conds[f"P{int(k * 100)}"] = {h: dEN[h] for h in prefix(L, k)}
    conds["SS"] = {hstar: dEN[hstar]}
    # ---- FLORES-dev base NLL + P100 dNLL, then RND matching
    nfl = 10 if mini else 50
    lm.reset()
    base_nll = flores_nll(lm, flo_dev, C.LANGS, nfl)
    fl_res = {"base": base_nll, "dnll": {}}
    rnd_log = []
    lm.set_ablate_layerwise(conds["P100"])
    p100 = flores_nll(lm, flo_dev, ["en"], nfl)
    target = float(np.mean(np.asarray(p100["en"]) - np.asarray(base_nll["en"])))
    chosen = None
    for draw in range(5):
        R = random_dirs(D, L, seed=99 + draw)
        for c in (1.0, 1.5, 2.0, 0.5):
            lm.set_ablate_layerwise({h: R[h] for h in prefix(L, 1.0)}, c=c)
            dn = float(np.mean(np.asarray(flores_nll(lm, flo_dev, ["en"], nfl)["en"]) - np.asarray(base_nll["en"])))
            ratio = dn / target if abs(target) > 1e-9 else float("nan")
            rnd_log.append({"draw": draw, "seed": 99 + draw, "c": c, "dnll_en": dn, "target_p100": target, "ratio": ratio})
            if 0.5 <= ratio <= 1.5:
                chosen = {"draw": draw, "seed": 99 + draw, "c": c, "ratio": ratio, "matched": True}
                break
        if chosen:
            break
    if chosen is None:
        best = min(rnd_log, key=lambda r: abs(math.log(max(r["ratio"], 1e-6))) if r["ratio"] == r["ratio"] else 1e9)
        chosen = {"draw": best["draw"], "seed": best["seed"], "c": best["c"], "ratio": best["ratio"], "matched": False}
        logger.warning(f"[{key}] RND unmatched (F-R): {chosen}")
    R = random_dirs(D, L, seed=chosen["seed"])
    conds["RND"] = {h: R[h] for h in prefix(L, 1.0)}
    rnd_c = chosen["c"]
    C.jdump({"chosen": chosen, "draws": rnd_log}, outdir / "rnd_match.json")
    np.save(outdir / "rnd_dirs.npy", R.astype(np.float32))
    # ---- DEV generations
    harm = [it for it in idx if it["role"] == "harmful"]
    ben = [it for it in idx if it["role"] == "harmless"]
    if mini:
        harm, ben = harm[:4], ben[:4]
    for name, dirs in conds.items():
        if (outdir / "gens" / f"dev_{name}.jsonl").exists():
            continue
        lm.set_ablate_layerwise(dirs, c=rnd_c if name == "RND" else 1.0)
        recs = gen_records(lm, f"dev_{name}", "dev", harm, C.LANGS)
        if name in ("k0", "P100"):
            recs += gen_records(lm, f"dev_{name}", "dev", ben, C.LANGS)
        if name != "k0":
            fl_res["dnll"][name] = mean_dnll(flores_nll(lm, flo_dev, C.LANGS, nfl), base_nll)
        if name == "k0":
            tk = lm.first_lp_topk([lm.encode_chat(it[Lg]) for Lg in C.LANGS for it in harm], k=1000)
            np.savez_compressed(outdir / "k0_first_topk.npz", ids=np.stack([a for a, _ in tk]), lp=np.stack([b for _, b in tk]),
                                uids=np.array([it["uid"] for Lg in C.LANGS for it in harm]),
                                langs=np.array([Lg for Lg in C.LANGS for it in harm]))
        save_gens(key, f"dev_{name}", recs)
        lm.reset()
    C.jdump(fl_res, outdir / "flores_dev.json")
    # ---- CAL generations for the weight panel (EN only)
    cal = items("cal")[: (4 if mini else 24)]
    calinfo = C.jload(outdir / "cal_info.json") if (outdir / "cal_info.json").exists() else {"W1": {}, "W3": {}}
    for q in range(4):
        band = list(range(int(round(q * L / 4)), int(round((q + 1) * L / 4))))
        for w in W1_DOSES:
            name = f"cal_W1_q{q}_w{w}"
            if (outdir / "gens" / f"{name}.jsonl").exists():
                continue
            fac, en, _ = lm.heretic_factors(D["vdirs"], {}, weight_override={(j, c): w for j in band for c in ("attn.o_proj", "mlp.down_proj")})
            lm.set_weight_edit(fac)
            save_gens(key, name, gen_records(lm, name, "cal", cal, ["en"]))
            lm.clear_weight_edit()
            calinfo["W1"][name] = {"band_layers": band, "q": q, "w": w, "energy": en}
            C.jdump(calinfo, outdir / "cal_info.json")
    if key != "gemma":
        for s in W3_SCALES:
            name = f"cal_W3_s{s}"
            if (outdir / "gens" / f"{name}.jsonl").exists():
                continue
            fac, en, params, gdir_info = w3_kernel(lm, D, s)
            lm.set_weight_edit(fac)
            save_gens(key, name, gen_records(lm, name, "cal", cal, ["en"]))
            lm.clear_weight_edit()
            calinfo["W3"][name] = {"s": s, "energy": en, "params": params} | gdir_info
            C.jdump(calinfo, outdir / "cal_info.json")
    lm.close()
    timing(key, "phase_dev_total", time.time() - t0)
    logger.info(f"[{key}] DEV phase done in {time.time() - t0:.0f}s")


def w3_kernel(lm: LM, D: dict, s: float) -> tuple:
    """Trial-96 kernel mapped to relative depth (pos/L, dist/L, direction_index/L), max/min weights scaled by s.
    Global direction = Heretic lerp between orthogonalised per-layer directions at the fractional hidden index."""
    T = C.TRIAL96
    last = lm.L - 1
    fr = last / T["last_layer_index"]
    params = {}
    for comp in ("attn.o_proj", "mlp.down_proj"):
        p = T[comp]
        params[comp] = {"max_weight": p["max_weight"] * s, "min_weight": p["min_weight"] * s,
                        "max_weight_position": p["max_weight_position"] * fr, "min_weight_distance": p["min_weight_distance"] * fr}
    di = T["direction_index"] * fr
    wgt, index = math.modf(di + 1)
    index = int(index)
    g = D["vdirs"][index] * (1 - wgt) + D["vdirs"][index + 1] * wgt
    g = unit(g)
    fac, en, _ = lm.heretic_factors(None, params, global_dir=g)
    return fac, en, params, {"direction_index": di, "global_dir_hidden_index": di + 1}


def load_gemma_adapter(lm: LM) -> tuple[dict, dict]:
    from safetensors.torch import load_file
    got = C.file_sha256(C.GEMMA_ADAPTER / "adapter_model.safetensors")
    assert got == C.GEMMA_ADAPTER_SHA, got
    sd = load_file(str(C.GEMMA_ADAPTER / "adapter_model.safetensors"))
    cfg = json.loads((C.GEMMA_ADAPTER / "adapter_config.json").read_text())
    scale = cfg["lora_alpha"] / cfg["r"]
    fac = {}
    for k, A in sd.items():
        if ".lora_A." not in k:
            continue
        B = sd[k.replace(".lora_A.", ".lora_B.")]
        parts = k.split(".")
        j = int(parts[parts.index("layers") + 1])
        comp = "attn.o_proj" if "o_proj" in k else "mlp.down_proj"
        fac[(j, comp)] = (A.float(), B.float() * scale)
    return fac, {"adapter": str(C.GEMMA_ADAPTER), "sha256": got, "n_modules": len(fac), "scale": scale}


# ============================================================================================ CONF phase
def assert_frozen() -> dict:
    fp = C.CFG / "frozen_predictions.json"
    if not fp.exists():
        raise RuntimeError("configs/frozen_predictions.json missing: no CONF generation before the freeze")
    sha = C.file_sha256(fp)
    if sha not in (C.CFG / "FREEZE.sha256").read_text():
        raise RuntimeError("frozen_predictions.json sha256 not in FREEZE.sha256")
    return C.jload(fp)


def phase_conf(key: str, mini: bool, only_cells: list | None = None) -> None:
    frozen = assert_frozen()
    t0 = time.time()
    outdir = C.RES / key
    sel = frozen["weight_panel_choices"][key]
    lm = LM(key)
    torch.cuda.set_per_process_memory_fraction(0.92)
    z = np.load(outdir / "directions.npz")
    D = {k: z[k] for k in z.files}
    L = lm.L
    conf = items("conf")
    harm = [it for it in conf if it["role"] == "harmful"]
    ben = [it for it in conf if it["role"] == "harmless"]
    if mini:
        harm, ben = harm[:2], ben[:2]
    fl = items("flores")
    flo_dev = [f for f in fl if f["half"] == "A"][:50]
    flo_conf = [f for f in fl if f["half"] == "B"]
    nfl = 10 if mini else len(flo_conf)
    panel = C.jload(outdir / "panel_info.json") if (outdir / "panel_info.json").exists() else {}
    both = ("attn.o_proj", "mlp.down_proj")
    # ---- build cells
    cells = {"W0": {}}
    band = sel["W1_band_layers"]
    f1, e1, _ = lm.heretic_factors(D["vdirs"], {}, weight_override={(j, c): sel["W1_w"] for j in band for c in both})
    cells["W1"] = f1
    panel["W1"] = {"band_layers": band, "w": sel["W1_w"], "energy": e1}
    # W2: flat all-depth weight solved on the one-pass delta-energy curve, then refined on the exact LoRA energy
    t = time.time()
    grid = [round(0.02 * i, 3) for i in range(1, 76)]  # w in (0, 1.5]
    cur_all = lm.energy_curve(D["vdirs"], set(range(L)), grid)
    cur_band = lm.energy_curve(D["vdirs"], set(band), grid)
    proxy_target = cur_band[min(grid, key=lambda w: abs(w - sel["W1_w"]))]
    ws = LM.solve_weight(cur_all, proxy_target)
    f2, e2, _ = lm.heretic_factors(D["vdirs"], {}, weight_override={(j, c): ws for j in range(L) for c in both})
    hist = [{"w": ws, "energy": e2, "proxy_target": proxy_target, "step": "proxy"}]
    for _ in range(4):  # refine on the exact rank-3 LoRA energy
        if abs(e2 / e1 - 1) <= 0.05:
            break
        ws = ws * (e1 / e2) ** 0.5
        f2, e2, _ = lm.heretic_factors(D["vdirs"], {}, weight_override={(j, c): ws for j in range(L) for c in both})
        hist.append({"w": ws, "energy": e2, "step": "exact-refine"})
    panel["W2"] = {"w": ws, "energy": e2, "energy_ratio_vs_W1": e2 / e1, "matched_10pct": abs(e2 / e1 - 1) <= 0.10,
                   "search": hist, "energy_curve_all_depth": cur_all, "secs": time.time() - t}
    cells["W2"] = f2
    if key == "gemma":
        f3, ainfo = load_gemma_adapter(lm)
        cells["W3"] = f3
        panel["W3"] = ainfo | {"energy": LM.factor_energy(f3), "label": "iter-1 trial-96 Heretic adapter (real)"}
    else:
        f3, e3, params, gi = w3_kernel(lm, D, sel["W3_s"])
        cells["W3"] = f3
        panel["W3"] = {"s": sel["W3_s"], "energy": e3, "params": params, "label": "Heretic-style EN-calibrated kernel"} | gi
    # W4: random per-layer directions (orthogonal to d_EN(h), harmless PC span) at W2's coverage; energy (+/-10%) and
    # FLORES-dev EN dNLL (+/-50%) matched to W2
    lm.clear_weight_edit()
    lm.reset()
    base_dev = flores_nll(lm, flo_dev, ["en"], 50 if not mini else 10)
    lm.set_weight_edit(f2)
    w2_dn = float(np.mean(np.asarray(flores_nll(lm, flo_dev, ["en"], 50 if not mini else 10)["en"]) - np.asarray(base_dev["en"])))
    lm.clear_weight_edit()
    draws, chosen = [], None
    for draw in range(5):
        R = random_dirs(D, L, seed=500 + draw)
        curR = lm.energy_curve(R, set(range(L)), grid)
        mid = LM.solve_weight(curR, cur_all[min(grid, key=lambda w: abs(w - ws))])
        f4, e4, _ = lm.heretic_factors(R, {}, weight_override={(j, c): mid for j in range(L) for c in both})
        for _ in range(4):
            if abs(e4 / e2 - 1) <= 0.05:
                break
            mid = mid * (e2 / e4) ** 0.5
            f4, e4, _ = lm.heretic_factors(R, {}, weight_override={(j, c): mid for j in range(L) for c in both})
        lm.set_weight_edit(f4)
        dn = float(np.mean(np.asarray(flores_nll(lm, flo_dev, ["en"], 50 if not mini else 10)["en"]) - np.asarray(base_dev["en"])))
        lm.clear_weight_edit()
        ratio = dn / w2_dn if abs(w2_dn) > 1e-9 else float("nan")
        rec = {"draw": draw, "seed": 500 + draw, "w": mid, "energy": e4, "energy_ratio": e4 / e2, "dnll_en": dn, "w2_dnll_en": w2_dn,
               "dnll_ratio": ratio, "energy_ok": abs(e4 / e2 - 1) <= 0.10, "dnll_ok": 0.5 <= ratio <= 1.5}
        draws.append(rec)
        if rec["energy_ok"] and rec["dnll_ok"]:
            chosen, cells["W4"] = rec | {"matched": True}, f4
            break
    if chosen is None:
        best = min(draws, key=lambda r: abs(math.log(max(abs(r["dnll_ratio"]), 1e-6))) if r["dnll_ratio"] == r["dnll_ratio"] else 1e9)
        R = random_dirs(D, L, seed=best["seed"])
        cells["W4"], _, _ = lm.heretic_factors(R, {}, weight_override={(j, c): best["w"] for j in range(L) for c in both})
        chosen = best | {"matched": False}
        logger.warning(f"[{key}] W4 unmatched (F-R): {chosen}")
    panel["W4"] = {"chosen": chosen, "draws": draws}
    C.jdump(panel, outdir / "panel_info.json")
    logger.info(f"[{key}] cells built: E(W1)={e1:.3f} E(W2)={e2:.3f} w_s={ws:.3f} W3={panel['W3'].get('energy', 0):.3f} "
                f"W4 matched={chosen.get('matched')} ({time.time() - t0:.0f}s)")
    # ---- generations + collateral per cell
    lm.clear_weight_edit()
    lm.reset()
    base_conf = flores_nll(lm, flo_conf, C.LANGS, nfl)
    ref_first = lm.first_lp_topk([lm.encode_chat(it[Lg]) for Lg in C.LANGS for it in ben], k=512)
    coll = C.jload(outdir / "panel_collateral.json") if (outdir / "panel_collateral.json").exists() else {}
    tr = key in ("gemma", "qwen3")
    order = only_cells or ["W0", "W2", "W3", "W1", "W4"]
    for cell in order:
        lm.set_weight_edit(cells[cell]) if cells[cell] else lm.clear_weight_edit()
        name = f"conf_{cell}"
        if not (outdir / "gens" / f"{name}.jsonl").exists():
            recs = gen_records(lm, name, "conf", harm, C.LANGS)
            if cell in ("W0", "W3"):  # CUT (declared): over-refusal twins for the no-op and the selected kernel only
                recs += gen_records(lm, name, "conf", ben, C.LANGS)
            save_gens(key, name, recs)
        if tr and cell in ("W0", "W2") and not (outdir / "gens" / f"conf_TR_{cell}.jsonl").exists():
            its = [it for it in harm if it.get("sl_nllb")]
            save_gens(key, f"conf_TR_{cell}", gen_records(lm, f"conf_TR_{cell}", "conf", its, ["sl"], text_key="sl_nllb"))
        if cell not in coll:
            dn = mean_dnll(flores_nll(lm, flo_conf, C.LANGS, nfl), base_conf)
            kl = lm.first_kl([lm.encode_chat(it[Lg]) for Lg in C.LANGS for it in ben], ref_first)
            nb = len(ben)
            coll[cell] = {"flores_devtest_dnll": dn, "first_token_kl_harmless": {Lg: float(np.mean(kl[i * nb:(i + 1) * nb]))
                                                                                  for i, Lg in enumerate(C.LANGS)},
                          "energy": LM.factor_energy(cells[cell]) if cells[cell] else 0.0}
            C.jdump(coll, outdir / "panel_collateral.json")
    lm.close()
    timing(key, "phase_conf_total", time.time() - t0)
    logger.info(f"[{key}] CONF phase done in {time.time() - t0:.0f}s")


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--phase", choices=["dev", "conf"], required=True)
    ap.add_argument("--mini", action="store_true")
    ap.add_argument("--cells", default="")
    args = ap.parse_args()
    C.setup_logging(f"run_{args.model}_{args.phase}")
    if args.phase == "dev":
        phase_dev(args.model, args.mini)
    else:
        phase_conf(args.model, args.mini, [c for c in args.cells.split(",") if c] or None)


if __name__ == "__main__":
    main()
