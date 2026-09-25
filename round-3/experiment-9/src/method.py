#!/usr/bin/env python3
"""How deep must an edit go to stop Slovene refusal? (iteration 3, experiment 9; google/gemma-3-12b-it, NF4)

GPU pipeline. Every stage is resumable per cell (results/gens/<cell>.json + results/cells/<cell>.json).

  --stage smoke    Gate 0/1/2/4: pins + SHAs + direction file, operator unit tests, closed-form energy check, harmless
                   means + orthogonalised per-layer directions, per-module edit energies, FLORES/Dolly references,
                   anchor smoke cells on 20+20 items/language, timing model.
  --stage partA    PART A (DEV = S3 JBB half A): activation-only cumulative prefix / suffix / leave-one-band-out
                   ablation of layer-matched d_EN(h) -> the depth-redundancy index (judged later). Part G write-mass.
  --stage screen   PART B screen (S3 JBB half B): matched-energy groups (narrow-and-strong vs broad-and-weak) with
                   layer-matched random (energy + collateral matched) and energy-matched PC controls, anchors
                   (L20 c=1, L20 c=2, all-48 activation, W0/W3/W4 on the trial-96 Heretic LoRA, Heretic-exact K96g),
                   then the coverage x strength factorial.
  --stage confirm  CONFIRMATION (S4 StrongREJECT hoc + ind, S6 over-refusal subsample, S7 utility) on the frozen
                   priority subset; refuses to run unless results/FREEZE.sha256 lists the frozen predictions.
  --stage s5x      FINAL second touch: S5X paired items for <= 2 cells named in configs/s5x_cells.json.

Baselines/controls: no-op (unedited model, same decoding/items), layer-matched random (same sites, same energy,
collateral-matched), energy-matched harmless-PC direction, the Arditi full-depth ceiling (ALL48), the frozen single
site (L20, exp8 A1/X4), the real Heretic trial-96 adapter (W0) and its repairs (W3/W4)."""
from __future__ import annotations

import argparse
import gc
import hashlib
import math
import os
import time
from pathlib import Path

import numpy as np
import torch
from loguru import logger

import common as C
from common import GEN_TOK, LANGS, file_sha256, jdump, jload, setup_logging
from interventions import LM, unit, winsorize

GEN_BS = int(os.environ.get("GEN_BS", 96))
L = 48
H = 49
COMPS = ("o_proj", "down_proj")
STRENGTHS = (0.25, 0.5, 1.0, 1.5)  # c = 2.0 of the plan is clipped at Heretic's max_weight = 1.5
COVERAGE = {  # 1-based layer numbers k (decoder layer j = k-1 writes into hidden index h = k)
    "B1": list(range(1, 13)), "B2": list(range(13, 25)), "B3": list(range(25, 37)), "B4": list(range(37, 49)),
    "C24": list(range(1, 25)), "C36": list(range(1, 37)), "S2": list(range(1, 49, 2)), "S4": list(range(1, 49, 4)),
    "ALL48": list(range(1, 49)),
}
GROUPS = {  # matched-energy groups: (narrow set, narrow c, broad set); broad c solved in closed form
    "G1": ("B3", 1.0, "S4"), "G2": ("B2", 1.0, "S2"), "G3": ("B4", 1.5, "C36"), "G4": ("B3", 1.5, "ALL48"),
}
SCREEN_PLAN = [("B_harm", "en"), ("B_harm", "sl"), ("B_ben", "en"), ("B_ben", "sl")]
PARTA_PLAN = [("A_harm", "en"), ("A_harm", "sl"), ("A_ben", "en"), ("A_ben", "sl")]
CONF_PLAN = [(s, g) for s in ("hoc_harm", "hoc_ben", "ind_harm", "ind_ben", "s6") for g in LANGS]


# ============================================================================================ context
class Ctx:
    def __init__(self, stage: str):
        self.stage = stage
        self.D = C.load_items(with_final=(stage == "s5x"))
        self.S = C.build_sets(self.D)
        self.lm: LM | None = None
        self.timings = jload(C.RES / "timings.json") if (C.RES / "timings.json").exists() else {}
        z = np.load(C.DIRS_NPZ)
        self.dEN = z["dEN"].astype(np.float32)
        self.dSL = z["dSL"].astype(np.float32)
        assert self.dEN.shape == (H, 3840), self.dEN.shape

    def tick(self, key: str, t0: float) -> None:
        self.timings[key] = round(time.time() - t0, 1)
        jdump(self.timings, C.RES / "timings.json")


def enc(lm: LM, items: list[dict], lang: str) -> list[list[int]]:
    return [lm.encode_chat(it[lang])[0] for it in items]


def decode(lm: LM, toks: list[int]) -> str:
    return lm.tok.decode(toks, skip_special_tokens=True)


def gen_rec(cell: str, it: dict, lang: str, toks: list[int], text: str, max_new: int) -> dict:
    return {"gid": hashlib.sha256(f"{cell}|{it['uid']}|{lang}".encode()).hexdigest()[:16], "cell": cell, "uid": it["uid"],
            "semantic_id": it["semantic_id"], "kind": it["kind"], "role": it.get("role"), "stratum": it.get("stratum"),
            "lang": lang, "prompt": it[lang], "response": text, "n_tokens": len(toks), "hit_max": len(toks) >= max_new}


def run_gens(ctx: Ctx, cell: str, plan: list[tuple[str, str]], max_new: int = GEN_TOK) -> float:
    """Greedy generation under the CURRENT hooks for each (set, lang); resumable per cell file. Returns seconds."""
    lm = ctx.lm
    p = C.GENS / f"{cell}.json"
    have = jload(p) if p.exists() else []
    done = {(r["uid"], r["lang"]) for r in have}
    t0 = time.time()
    n0 = len(have)
    # one pooled, length-sorted schedule over every (set, lang) of the plan: identical for every cell with this plan
    todo = [(it, g) for name, g in plan for it in ctx.S[name] if (it["uid"], g) not in done]
    for s0 in range(0, len(todo), 8 * GEN_BS):  # checkpoint to disk every <= 8 batches
        chunk = todo[s0:s0 + 8 * GEN_BS]
        outs = lm.generate([lm.encode_chat(it[g])[0] for it, g in chunk], max_new, batch=GEN_BS)
        have += [gen_rec(cell, it, g, t, decode(lm, t), max_new) for (it, g), t in zip(chunk, outs)]
        jdump(have, p)
    dt = time.time() - t0
    if len(have) > n0:
        logger.info(f"gens {cell}: +{len(have)-n0} in {dt:.0f}s ({dt/max(1, len(have)-n0):.3f}s/gen)")
    return dt


# ============================================================================================ references + collateral
class Collateral:
    """FLORES per-token NLL change vs the unedited model (S3_flores_dev, 200 pairs/language) and the 32-token harmless
    KL vs the unedited model on S3_dolly (100 prompts/language), both teacher forced."""

    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        lm = ctx.lm
        self.flo = ctx.S["flores"]
        self.flo_seqs = {g: [lm.encode_plain(it[g]) for it in self.flo] for g in LANGS}
        pb = C.RES / "ref_flores_base.json"
        pc = C.RES / "ref_dolly_cont.json"
        pk = C.RES / "ref_dolly_topk.npz"
        lm.reset()
        lm.set_weight_edit_layerwise({})
        if not pb.exists():
            jdump({g: lm.seq_nll(self.flo_seqs[g], [1] * len(self.flo)).tolist() for g in LANGS}, pb)
        self.flo_base = {g: np.array(v) for g, v in jload(pb).items()}
        self.dol = ctx.S["dolly"]
        if not pc.exists():
            cont = {}
            for g in LANGS:
                gg = lm.generate(enc(lm, self.dol, g), 32, batch=GEN_BS)
                cont[g] = [c if c else [lm.tok.eos_token_id] for c in gg]
            jdump(cont, pc)
        cont = jload(pc)
        refs = np.load(pk, allow_pickle=True)["refs"].item() if pk.exists() else {}
        self.kl = {}
        for g in LANGS:
            base = enc(lm, self.dol, g)
            seqs = [b + c for b, c in zip(base, cont[g])]
            starts = [len(b) for b in base]
            groups: dict = {}
            for i, c in enumerate(cont[g]):
                groups.setdefault(len(c), []).append(i)
            if g not in refs:
                ref = [None] * len(seqs)
                for n, ix in groups.items():
                    for i, r in zip(ix, lm.ref_topk([seqs[i] for i in ix], [starts[i] for i in ix], n)):
                        ref[i] = r
                refs[g] = ref
            self.kl[g] = (seqs, starts, groups, refs[g])
        if not pk.exists():
            np.savez(pk, refs=np.array(refs, dtype=object))

    def flores(self, n: int | None = None) -> dict:
        lm = self.ctx.lm
        out = {}
        for g in LANGS:
            seqs = self.flo_seqs[g][:n] if n else self.flo_seqs[g]
            nll = lm.seq_nll(seqs, [1] * len(seqs))
            out[g] = float(np.mean(nll - self.flo_base[g][:len(seqs)]))
        return out

    def kl_dolly(self) -> dict:
        lm = self.ctx.lm
        out = {}
        for g in LANGS:
            seqs, starts, groups, ref = self.kl[g]
            kl = np.zeros(len(seqs))
            for nn, ix in groups.items():
                kl[ix] = lm.kl_vs_ref([seqs[i] for i in ix], [starts[i] for i in ix], nn, [ref[i] for i in ix])
            out[g] = float(kl.mean())
        return out


# ============================================================================================ directions + energy
def harmless_means(ctx: Ctx) -> np.ndarray:
    """Per-hidden-index mean of winsorised pos -1 residuals of ENGLISH DEV harmless prompts (JBB-benign half A + Dolly
    half A), the 'good mean' Heretic orthogonalises its refusal direction against (orthogonalize_direction=true)."""
    p = C.RES / "harmless_mean_en.npy"
    if p.exists():
        return np.load(p)
    lm = ctx.lm
    its = ctx.S["A_ben"] + ctx.S["A_dolly"]
    seqs, content = [], []
    for it in its:
        s, c = lm.encode_chat(it["en"])
        seqs.append(s)
        content.append(c if c else [len(s) - 1])
    X = lm.capture(seqs, [[len(s) - 1] for s in seqs], content)  # [N, H, 2, D]
    m = winsorize(X[:, :, 0]).mean(0)  # [H, D]
    np.save(p, m.astype(np.float32))
    return m


def orth_dirs(ctx: Ctx, gm: np.ndarray) -> np.ndarray:
    """rhat_h = unit(d_EN(h) - (d_EN(h).g_h) g_h), g_h = unit(harmless mean at h)."""
    R = np.zeros_like(ctx.dEN)
    for h in range(H):
        d = ctx.dEN[h].astype(np.float64)
        g = gm[h].astype(np.float64)
        g = g / (np.linalg.norm(g) + 1e-12)
        R[h] = unit(d - (d @ g) * g)
    np.save(C.RES / "rhat_orth.npy", R)
    return R


def energies(ctx: Ctx, dirs_by_layer: dict) -> dict:
    """e[(j, comp)] = ||W^T rhat_j||^2 for decoder layer j (0-based), module comp."""
    lm = ctx.lm
    out = {}
    for j, d in dirs_by_layer.items():
        for comp in COMPS:
            out[(int(j), comp)] = float(lm.module_energy(int(j), comp, d[None])[0])
    return out


def kernel_profile() -> dict:
    """Heretic Model.abliterate() per-layer weight schedule for trial 96 (exp7 heretic_params.kernel_weights)."""
    from heretic_params import kernel_weights

    params = {"attn.o_proj": C.TRIAL96["attn.o_proj"], "mlp.down_proj": C.TRIAL96["mlp.down_proj"]}
    kw = kernel_weights(C.TRIAL96["direction_index"], params)
    return {"o_proj": kw["attn.o_proj"], "down_proj": kw["mlp.down_proj"]}


# ============================================================================================ cells
def uniform_profile(layers: list[int], c: float) -> dict:
    """{(j, comp): c} for 1-based layer numbers."""
    return {(k - 1, comp): float(c) for k in layers for comp in COMPS}


def profile_energy(prof: dict, e: dict) -> float:
    return float(sum(c * c * e[key] for key, c in prof.items()))


def weight_spec(prof: dict, dirs: dict) -> dict:
    """dirs: {j: direction}. -> {(j, comp): (dir, c)}"""
    return {key: (dirs[key[0]], c) for key, c in prof.items() if c != 0.0}


def cell_meta(name: str, family: str, prof: dict | None, E: float | None, extra: dict | None = None) -> dict:
    m = {"cell": name, "family": family, "E": E}
    if prof is not None:
        per = np.zeros((L, 2))
        for (j, comp), c in prof.items():
            per[j, COMPS.index(comp)] = c
        m["c_profile"] = per.tolist()
        cov = sorted({j + 1 for (j, _), c in prof.items() if c != 0})
        m["layers"] = cov
        m["n_layers"] = len(cov)
    return m | (extra or {})


def run_cell(ctx: Ctx, col: Collateral, name: str, setup, plan, meta: dict, stage: str) -> None:
    """Apply hooks via setup(), generate, measure collateral, clean up. Skips if already complete."""
    pm = C.CELLS / f"{name}.json"
    if pm.exists() and jload(pm).get("complete_plan") == [list(x) for x in plan]:
        return
    t0 = time.time()
    lm = ctx.lm
    lm.reset()
    lm.set_weight_edit_layerwise({})
    setup()
    dt_gen = run_gens(ctx, name, plan)
    t1 = time.time()
    fl = col.flores()
    kl = col.kl_dolly()
    lm.reset()
    lm.set_weight_edit_layerwise({})
    meta = meta | {"stage": stage, "flores_dNLL": fl, "kl_dolly": kl, "sec_gen": round(dt_gen, 1),
                   "sec_tf": round(time.time() - t1, 1), "complete_plan": [list(x) for x in plan],
                   "done_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    jdump(meta, pm)
    ctx.tick(f"cell_{name}", t0)
    logger.info(f"[{stage}] {name}: FLORES dNLL EN {fl['en']:+.3f} SL {fl['sl']:+.3f}; KL EN {kl['en']:.3f} SL {kl['sl']:.3f}; "
                f"{time.time()-t0:.0f}s")


# ============================================================================================ controls
def random_write_dirs(lm: LM, rhat: dict, layers: list[int], seed: int) -> dict:
    """One random direction per covered decoder layer, drawn from that layer's WRITE space (u = W_o g1 + W_down g2 with
    Gaussian g, i.e. the output of the two write modules on random inputs), orthogonalised against rhat_j and with the
    massive dimension zeroed. Write-space draws reach d_EN-like edit energy far more often than isotropic draws, which
    exp8 found could match d_EN(h)'s energy at only 15/48 layers."""
    g = torch.Generator(device="cuda").manual_seed(seed)
    out = {}
    for k in layers:
        j = k - 1
        u = torch.zeros(3840, device="cuda")
        for comp in COMPS:
            W = lm.module_weight(j, comp).float()
            x = torch.randn(W.shape[1], generator=g, device="cuda")
            v = W @ x
            u += v / (v.norm() + 1e-12)
            del W
        u = u.cpu().numpy().astype(np.float64)
        u[C.MASSIVE_DIM] = 0.0
        r = rhat[j].astype(np.float64)
        u = u - (u @ r) * r
        out[j] = unit(u)
    return out


def scaled_control(prof: dict, e_ctrl: dict, E_target: float, cap: float = 2.0) -> tuple[dict, float, float, bool]:
    """Scale the real cell's per-(layer, module) coefficient profile by one scalar s so the control reaches E_target.
    Coefficients are capped at `cap` (c = 2 is a Householder reflection; beyond it the edit amplifies)."""
    base = profile_energy(prof, e_ctrl)
    s = math.sqrt(E_target / max(base, 1e-12))
    newp = {k: min(cap, s * c) for k, c in prof.items()}
    E = profile_energy(newp, e_ctrl)
    return newp, s, E, bool(abs(E / E_target - 1) <= 0.10)


def setup_weight(ctx: Ctx, prof: dict, dirs: dict):
    return lambda: ctx.lm.set_weight_edit_layerwise(weight_spec(prof, dirs))


def solve_groups(e_real: dict) -> dict:
    """Closed-form matched-energy pairs: c_broad = c_narrow * sqrt(E_narrow(1) / E_broad(1)); if c_broad > 1.5, shift the
    narrow c down (x0.8) and re-solve."""
    out = {}
    for gname, (nset, cn, bset) in GROUPS.items():
        En1 = profile_energy(uniform_profile(COVERAGE[nset], 1.0), e_real)
        Eb1 = profile_energy(uniform_profile(COVERAGE[bset], 1.0), e_real)
        c_n = cn
        shifted = False
        while True:
            c_b = c_n * math.sqrt(En1 / Eb1)
            if c_b <= C.HERETIC_MAX_WEIGHT:
                break
            c_n *= 0.8
            shifted = True
        out[gname] = {"narrow": nset, "c_narrow": c_n, "broad": bset, "c_broad": c_b, "E_narrow": c_n ** 2 * En1,
                      "E_broad": c_b ** 2 * Eb1, "narrow_shifted": shifted,
                      "narrow_cell": f"W_{nset}_c{c_n:g}" if not shifted else f"W_{nset}_c{c_n:.3f}",
                      "broad_cell": f"W_{bset}_c{c_b:.3f}_{gname}"}
    return out


# ============================================================================================ stages
def load_model(ctx: Ctx) -> None:
    t0 = time.time()
    torch.cuda.set_per_process_memory_fraction(0.92)
    ctx.lm = LM("gemma")
    ctx.tick("load", t0)


def stage_smoke(ctx: Ctx) -> None:
    lm = ctx.lm
    # ---- Gate 0: pins, SHAs, direction file
    g0 = {"model": C.MODEL, "splits_sha_ok": dict(C._SHA_OK), "directions_npz_sha256": file_sha256(C.DIRS_NPZ),
          "dEN_shape": list(ctx.dEN.shape)}
    d20 = np.load(C.DEN_L20).astype(np.float64).ravel()
    g0["cos_dEN_L20_vs_saved"] = float(ctx.dEN[C.L_R] @ d20 / (np.linalg.norm(ctx.dEN[C.L_R]) * np.linalg.norm(d20)))
    assert g0["cos_dEN_L20_vs_saved"] > 0.99, g0
    from huggingface_hub import snapshot_download
    snap = Path(snapshot_download(C.MODEL["repo"], revision=C.MODEL["sha"], local_files_only=True))
    g0["weight_files_sha256"] = {p.name: file_sha256(p) for p in sorted(snap.glob("*.safetensors"))}
    g0["rendered_en"] = lm.render(ctx.S["B_harm"][0]["en"])
    g0["rendered_sl"] = lm.render(ctx.S["B_harm"][0]["sl"])
    e8 = [r for r in jload(C.EXP8 / "results/gemma/gens/A0.json") if r["uid"] == ctx.S["B_harm"][0]["uid"]]
    g0["exp8_prompt_identical"] = bool(e8) and all(r["prompt"] == ctx.S["B_harm"][0][r["lang"]] for r in e8)
    jdump(g0, C.RES / "gate0_pins.json")
    logger.info(f"Gate 0: cos(dEN L20, saved)={g0['cos_dEN_L20_vs_saved']:.5f}; exp8 prompt identical={g0['exp8_prompt_identical']}")

    # ---- Gate 1: operator unit tests
    g1 = {}
    x = torch.randn(64, 3840, device="cuda")
    r = torch.nn.functional.normalize(torch.randn(3840, device="cuda"), dim=0)
    for c in (1.0, 0.5, 0.25):
        y = x - c * (x @ r)[:, None] * r
        g1[f"hook_proj_ratio_c{c}"] = float(((y @ r) / (x @ r)).mean())
    g1["hook_residual_c1"] = float(((x - (x @ r)[:, None] * r) @ r).abs().max() / x.norm(dim=1).max())
    # hook on a real module equals the explicit (I - c r r^T) W product on a slice
    j, comp = 20, "o_proj"
    W = lm.module_weight(j, comp).float()
    rr = torch.as_tensor(unit(ctx.dEN[j + 1]), device="cuda")
    Ws = W[:, :512]
    dW = 1.0 * torch.outer(rr, rr @ Ws)
    g1["energy_explicit_slice"] = float((dW ** 2).sum())
    g1["energy_closed_slice"] = float(((Ws.T @ rr) ** 2).sum())
    g1["energy_rel_err"] = abs(g1["energy_explicit_slice"] - g1["energy_closed_slice"]) / g1["energy_closed_slice"]
    del W, Ws, dW
    # layerwise activation hook touches only its indices
    its = ctx.S["A_harm"][:3]
    seqs = [lm.encode_chat(it["en"])[0] for it in its]
    lm.reset()
    base = lm.capture(seqs, [[len(s) - 1] for s in seqs], [[len(s) - 1] for s in seqs], layers=[5, 30])
    lm.set_ablate_layerwise({30: ctx.dEN[30]}, 1.0)
    abl = lm.capture(seqs, [[len(s) - 1] for s in seqs], [[len(s) - 1] for s in seqs], layers=[5, 30])
    lm.reset()
    g1["untouched_index_identical"] = bool(np.array_equal(base[:, 0], abl[:, 0]))
    g1["touched_index_changed"] = bool(not np.array_equal(base[:, 1], abl[:, 1]))
    # weight hook on real module: output projection removed
    lm.set_weight_edit_layerwise({(j, comp): (ctx.dEN[j + 1], 1.0)})
    store = {}
    hd = lm.layers[j].self_attn.o_proj.register_forward_hook(lambda m, i, o: store.__setitem__("o", o.float()))
    lm._forward(seqs)
    hd.remove()
    lm.set_weight_edit_layerwise({})
    o = store["o"]  # hook order: our edit hook registered first -> store sees edited output
    g1["weight_hook_max_proj_ratio"] = float(((o @ rr).abs() / o.norm(dim=-1).clamp_min(1e-6)).max())
    g1["pass"] = bool(abs(g1["hook_proj_ratio_c0.5"] - 0.5) < 1e-4 and abs(g1["hook_proj_ratio_c0.25"] - 0.75) < 1e-4
                      and g1["energy_rel_err"] < 1e-3 and g1["untouched_index_identical"] and g1["touched_index_changed"]
                      and g1["weight_hook_max_proj_ratio"] < 2e-2)
    jdump(g1, C.RES / "gate1_unit_tests.json")
    logger.info(f"Gate 1: {g1}")
    assert g1["pass"], g1

    # ---- directions, energies, references
    prepare(ctx)
    col = Collateral(ctx)
    # ---- Gate 2 anchor smoke on 20+20 items per language (+ Gate 4 timing)
    sm = {"sm_harm": ctx.S["B_harm"][:20], "sm_ben": ctx.S["B_ben"][:20]}
    ctx.S.update(sm)
    plan = [("sm_harm", "en"), ("sm_harm", "sl"), ("sm_ben", "en"), ("sm_ben", "sl")]
    dirs = ctx_dirs(ctx)
    cells = [("SMK_noop", lambda: None, "noop"),
             ("SMK_A1_L20_c1", lambda: lm.set_ablate(ctx.dEN[C.L_R], 1.0), "act"),
             ("SMK_X4_L20_c2", lambda: lm.set_ablate(ctx.dEN[C.L_R], 2.0), "act"),
             ("SMK_X1_all48", lambda: lm.set_ablate_layerwise({h: ctx.dEN[h] for h in range(1, H)}, 1.0), "act"),
             ("SMK_W_4layer", setup_weight(ctx, uniform_profile([25, 28, 31, 34], 1.0), dirs), "weight")]
    for name, setup, fam in cells:
        run_cell(ctx, col, name, setup, plan, cell_meta(name, fam, None, None, {"smoke": True}), "smoke")
    tm = {k: v for k, v in ctx.timings.items() if k.startswith("cell_SMK")}
    per_gen = float(np.mean([jload(C.CELLS / f"{n}.json")["sec_gen"] / 80 for n, _, _ in cells]))
    per_tf = float(np.mean([jload(C.CELLS / f"{n}.json")["sec_tf"] for n, _, _ in cells]))
    jdump({"sec_per_gen_128tok": per_gen, "sec_tf_per_cell": per_tf, "gen_bs": GEN_BS, "cells": tm,
           "screen_cell_164_gens_s": 164 * per_gen + per_tf, "partA_cell_176_gens_s": 176 * per_gen + per_tf,
           "confirm_cell_680_gens_s": 680 * per_gen + per_tf}, C.RES / "timing_model.json")


def ctx_dirs(ctx: Ctx) -> dict:
    """{decoder layer j: rhat_{j+1}} orthogonalised per-layer d_EN directions used by every weight cell."""
    R = np.load(C.RES / "rhat_orth.npy")
    return {j: R[j + 1] for j in range(L)}


def prepare(ctx: Ctx) -> None:
    """Harmless means, orthogonalised directions, per-module energies of the real directions."""
    t0 = time.time()
    gm = harmless_means(ctx)
    R = orth_dirs(ctx, gm)
    pe = C.RES / "energy_real.json"
    if not pe.exists():
        e = energies(ctx, {j: R[j + 1] for j in range(L)})
        cos_orth = [float(np.dot(unit(ctx.dEN[h]), R[h])) for h in range(H)]
        jdump({"e": {f"{j}|{c}": v for (j, c), v in e.items()}, "cos_rhat_vs_dEN": cos_orth}, pe)
    ctx.tick("prepare", t0)


def load_e(p: Path) -> dict:
    return {(int(k.split("|")[0]), k.split("|")[1]): v for k, v in jload(p)["e"].items()}


def stage_partA(ctx: Ctx) -> None:
    lm = ctx.lm
    prepare(ctx)
    col = Collateral(ctx)
    sets = {}
    for k in range(4, 49, 4):
        sets[f"PA_prefix_{k:02d}"] = list(range(1, k + 1))
    for k in range(4, 49, 4):
        sets[f"PA_suffix_{k:02d}"] = list(range(49 - k, 49))
    for a, b in ((1, 12), (13, 24), (25, 36), (37, 48)):
        sets[f"PA_lobo_{a:02d}_{b:02d}"] = [h for h in range(1, 49) if not a <= h <= b]
    jdump({"sets": sets, "declared_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "items": "S3 JBB half A: 44 harmful + 44 harmless per language (DEV)", "gen_tokens": GEN_TOK,
           "operator": "layer-matched activation ablation of unit(d_EN(h)) at hidden indices in the set, all positions, c=1"},
          C.CFG / "partA_sets.json")
    run_cell(ctx, col, "PA_noop", lambda: None, PARTA_PLAN, cell_meta("PA_noop", "noop", None, None, {"part": "A"}), "partA")
    order = [n for n in sets if "prefix" in n] + [n for n in sets if "lobo" in n] + [n for n in sets if "suffix" in n]
    for name in order:
        lay = sets[name]
        run_cell(ctx, col, name, (lambda lay=lay: lm.set_ablate_layerwise({h: ctx.dEN[h] for h in lay}, 1.0)), PARTA_PLAN,
                 cell_meta(name, "act", None, None, {"part": "A", "layers": lay, "n_layers": len(lay)}), "partA")
    part_G(ctx)


def part_G(ctx: Ctx) -> None:
    """EXPLORATORY write-mass: per layer, the component of that layer's residual CONTRIBUTION (x_h - x_{h-1}) along
    unit(d_EN(h)) at the pre-response position, harmful minus harmless, per language (S3 half A)."""
    p = C.RES / "write_mass.json"
    if p.exists():
        return
    lm = ctx.lm
    lm.reset()
    lm.set_weight_edit_layerwise({})
    out = {}
    for g in LANGS:
        proj = {}
        for role, key in (("harmful", "A_harm"), ("harmless", "A_ben")):
            seqs = [lm.encode_chat(it[g])[0] for it in ctx.S[key]]
            X = lm.capture(seqs, [[len(s) - 1] for s in seqs], [[len(s) - 1] for s in seqs])[:, :, 0]  # [N, H, D]
            dX = X[:, 1:] - X[:, :-1]  # contribution of decoder layer j into hidden j+1
            U = np.stack([unit(ctx.dEN[h]) for h in range(1, H)])  # [48, D]
            proj[role] = np.einsum("nhd,hd->nh", dX.astype(np.float64), U.astype(np.float64))  # [N, 48]
            del X, dX
        diff = proj["harmful"].mean(0) - proj["harmless"].mean(0)
        out[g] = {"harm_minus_harmless_write": diff.tolist(), "harmful_write": proj["harmful"].mean(0).tolist(),
                  "harmless_write": proj["harmless"].mean(0).tolist()}
    jdump(out, p)
    gc.collect()


def stage_screen(ctx: Ctx) -> None:
    lm = ctx.lm
    prepare(ctx)
    col = Collateral(ctx)
    dirs = ctx_dirs(ctx)
    e_real = load_e(C.RES / "energy_real.json")
    groups = solve_groups(e_real)
    jdump(groups, C.CFG / "matched_groups.json")
    S = SCREEN_PLAN

    def wcell(name, prof, extra=None, d=dirs, e=e_real, fam="weight"):
        E = profile_energy(prof, e)
        run_cell(ctx, col, name, setup_weight(ctx, prof, d), S, cell_meta(name, fam, prof, E, extra), "screen")

    # ---- step 4: the matched-energy groups WITH their controls (decisive contrast first)
    run_cell(ctx, col, "noop", lambda: None, S, cell_meta("noop", "noop", None, 0.0), "screen")
    for gname, G in groups.items():
        for side in ("narrow", "broad"):
            cname = G[f"{side}_cell"]
            prof = uniform_profile(COVERAGE[G[side]], G[f"c_{side}"])
            wcell(cname, prof, {"group": gname, "side": side, "coverage": G[side], "c": G[f"c_{side}"]})
    for gname, G in groups.items():
        for side in ("narrow", "broad"):
            real = G[f"{side}_cell"]
            prof = uniform_profile(COVERAGE[G[side]], G[f"c_{side}"])
            E_t = profile_energy(prof, e_real)
            fl_real = jload(C.CELLS / f"{real}.json")["flores_dNLL"]
            random_control(ctx, col, f"R_{real}", prof, E_t, fl_real, COVERAGE[G[side]], dirs, gname, side)
            pc_control(ctx, col, f"P_{real}", prof, E_t, COVERAGE[G[side]], dirs, gname, side)
    # ---- step 5: anchors
    run_cell(ctx, col, "A1_L20_c1", lambda: lm.set_ablate(ctx.dEN[C.L_R], 1.0), S,
             cell_meta("A1_L20_c1", "act", None, None, {"anchor": "exp8 A1"}), "screen")
    run_cell(ctx, col, "X4_L20_c2", lambda: lm.set_ablate(ctx.dEN[C.L_R], 2.0), S,
             cell_meta("X4_L20_c2", "act", None, None, {"anchor": "exp8 X4"}), "screen")
    run_cell(ctx, col, "X1_act_all48", lambda: lm.set_ablate_layerwise({h: ctx.dEN[h] for h in range(1, H)}, 1.0), S,
             cell_meta("X1_act_all48", "act", None, None, {"anchor": "exp8 X1", "layers": list(range(1, 49)), "n_layers": 48}),
             "screen")
    # Heretic-exact operator of trial 96 on base weights: global interpolated direction + kernel profile
    kp = kernel_profile()
    di = C.TRIAL96["direction_index"]
    lo = int(math.floor(di + 1))
    fr = di + 1 - lo
    dglob = unit((1 - fr) * ctx.dEN[lo] + fr * ctx.dEN[lo + 1])
    gm = np.load(C.RES / "harmless_mean_en.npy")
    kprof = {(j, comp): float(kp[comp][j]) for j in range(L) for comp in COMPS if kp[comp][j] > 0}
    jdump({"kernel": kp, "support_layers_1based": sorted({j + 1 for (j, _) in kprof}), "direction_index": di}, C.CFG / "k96_kernel.json")
    e_glob = energies(ctx, {j: dglob for j in range(L)})
    wcell("K96g_heretic_exact", kprof, {"anchor": "trial-96 operator (global dir, kernel profile), no LoRA norm-preservation"},
          d={j: dglob for j in range(L)}, e=e_glob)
    for mult in (0.5, 1.0):
        prof = {k: v * mult for k, v in kprof.items()}
        wcell(f"K96k_x{mult:g}", prof, {"coverage": "K96", "kernel_mult": mult})
    fac_order = [(cov, c) for c in (1.0, 0.5, 1.5, 0.25) for cov in COVERAGE]
    # ---- core-edit anchors (LoRA) are attached LAST in this process: W0, W3, W4 (+ fill factorial first)
    # ---- step 6: remaining coverage cells at c=1, then the strength sweep
    for cov, c in fac_order:
        wcell(f"W_{cov}_c{c:g}", uniform_profile(COVERAGE[cov], c), {"coverage": cov, "c": c})
    k96_support = sorted({j + 1 for (j, _) in kprof})
    for c in STRENGTHS:
        wcell(f"W_K96_c{c:g}", uniform_profile(k96_support, c), {"coverage": "K96", "c": c})
    anchors_lora(ctx, col)


def anchors_lora(ctx: Ctx, col: Collateral, plan=None, prefix: str = "") -> None:
    from peft import PeftModel

    lm = ctx.lm
    plan = plan or SCREEN_PLAN
    names = [f"{prefix}W0_core", f"{prefix}W3_core_plus_act_all48", f"{prefix}W4_core_plus_act_random"]
    if all((C.CELLS / f"{n}.json").exists() and jload(C.CELLS / f"{n}.json").get("complete_plan") == [list(x) for x in plan]
           for n in names):
        return
    got = file_sha256(C.ADAPTER["dir"] / "adapter_model.safetensors")
    assert got == C.ADAPTER["sha"], got
    if not getattr(lm, "_lora", False):
        PeftModel.from_pretrained(lm.model, str(C.ADAPTER["dir"]))
        lm.model.eval()
        lm._lora = True
    rnd = np.load(C.EXP8 / "results/gemma/layerwise_random.npy")  # exp8 X3/W4 draws, h = 1..48
    info = {"adapter_sha256": got, "trial": 96}
    run_cell(ctx, col, names[0], lambda: None, plan, cell_meta(names[0], "lora", None, None, info | {"anchor": "exp8 W0"}), ctx.stage)
    run_cell(ctx, col, names[1], lambda: lm.set_ablate_layerwise({h: ctx.dEN[h] for h in range(1, H)}, 1.0), plan,
             cell_meta(names[1], "lora+act", None, None, info | {"anchor": "exp8 W3"}), ctx.stage)
    run_cell(ctx, col, names[2], lambda: lm.set_ablate_layerwise({h: rnd[h - 1] for h in range(1, H)}, 1.0), plan,
             cell_meta(names[2], "lora+act", None, None, info | {"anchor": "exp8 W4"}), ctx.stage)


def random_control(ctx: Ctx, col: Collateral, name: str, prof: dict, E_t: float, fl_real: dict, layers: list[int],
                   dirs: dict, gname: str, side: str) -> None:
    """Up to 5 write-space random draws at the SAME layers; each is scaled to the real cell's energy (single scalar,
    c capped at 2) and accepted if energy is within 10% AND its SL FLORES dNLL (100 pairs) is within +-50% of the real
    cell's (absolute floor 0.02 nats). The accepted draw closest in collateral is generated; shortfalls are recorded."""
    pm = C.CELLS / f"{name}.json"
    if pm.exists():
        return
    lm = ctx.lm
    tried = []
    best = None
    for k in range(5):
        rd = random_write_dirs(lm, dirs, layers, seed=C.SEED + 1000 * k + int(hashlib.sha256(name.encode()).hexdigest()[:6], 16) % 997)
        e_r = energies(ctx, rd)
        newp, s, E, ok_e = scaled_control(prof, e_r, E_t)
        lm.reset()
        lm.set_weight_edit_layerwise(weight_spec(newp, rd))
        fl = col.flores(n=100)
        lm.set_weight_edit_layerwise({})
        tol = max(0.5 * abs(fl_real["sl"]), 0.02)
        ok_c = abs(fl["sl"] - fl_real["sl"]) <= tol
        per_layer_short = {j + 1: e_r[(j, "o_proj")] + e_r[(j, "down_proj")] for j in rd}
        tried.append({"draw": k, "scale": s, "E": E, "E_target": E_t, "energy_ok": ok_e, "flores_sl_100": fl["sl"],
                      "flores_en_100": fl["en"], "collateral_ok": ok_c, "max_c": max(newp.values()),
                      "e_rand_per_layer": per_layer_short})
        score = (0 if (ok_e and ok_c) else 1 if ok_e else 2, abs(fl["sl"] - fl_real["sl"]))
        if best is None or score < best[0]:
            best = (score, rd, newp, E, k)
        if ok_e and ok_c:
            break
    _, rd, newp, E, k = best
    jdump({"cell": name, "tries": tried, "chosen_draw": k, "n_matched": sum(t["energy_ok"] and t["collateral_ok"] for t in tried)},
          C.CELLS / f"{name}__draws.json")
    run_cell(ctx, col, name, setup_weight(ctx, newp, rd), SCREEN_PLAN,
             cell_meta(name, "random", newp, E, {"group": gname, "side": side, "control_of": name[2:], "E_target": E_t,
                                                 "matched": tried[k]["energy_ok"] and tried[k]["collateral_ok"],
                                                 "energy_matched": tried[k]["energy_ok"], "collateral_matched": tried[k]["collateral_ok"]}),
             "screen")


def pc_control(ctx: Ctx, col: Collateral, name: str, prof: dict, E_t: float, layers: list[int], dirs: dict,
               gname: str, side: str) -> None:
    """Energy-matched harmless-PC control: exp8's per-layer energy-matched top harmless principal component
    (results/gemma/layerwise_pc.npy, h = 1..48), orthogonalised against rhat_j, scaled to the real cell's energy."""
    if (C.CELLS / f"{name}.json").exists():
        return
    pcs = np.load(C.EXP8 / "results/gemma/layerwise_pc.npy")
    pd_ = {}
    for k in layers:
        j = k - 1
        u = pcs[k - 1].astype(np.float64)
        r = dirs[j].astype(np.float64)
        pd_[j] = unit(u - (u @ r) * r)
    e_p = energies(ctx, pd_)
    newp, s, E, ok = scaled_control(prof, e_p, E_t)
    run_cell(ctx, col, name, setup_weight(ctx, newp, pd_), SCREEN_PLAN,
             cell_meta(name, "pc", newp, E, {"group": gname, "side": side, "control_of": name[2:], "E_target": E_t,
                                             "scale": s, "energy_matched": ok}), "screen")


def stage_confirm(ctx: Ctx) -> None:
    """Gate 5: refuse to run unless the frozen predictions + redundancy index are hashed in results/FREEZE.sha256."""
    fz = C.RES / "FREEZE.sha256"
    assert fz.exists(), "FREEZE.sha256 missing: freeze predictions before confirmation"
    txt = fz.read_text()
    for f in ("frozen_predictions.json", "redundancy_index.json"):
        assert f in txt, f"{f} not frozen"
        assert file_sha256(C.RES / f) in txt, f"{f} changed after freeze"
    fp = jload(C.RES / "frozen_predictions.json")
    cells = fp["confirmation_cells"]
    lm = ctx.lm
    prepare(ctx)
    col = Collateral(ctx)
    dirs = ctx_dirs(ctx)
    ctx.S["s6_sl"] = ctx.S["s6"]
    for c in cells:
        m = jload(C.CELLS / f"{c}.json")
        name = f"CF_{c}"
        if m["family"] == "noop":
            setup = lambda: None
        elif m["family"] in ("weight",):
            prof = {(j, COMPS[i]): v for j, row in enumerate(m["c_profile"]) for i, v in enumerate(row) if v != 0}
            if c.startswith("K96g"):
                continue  # global-direction anchor: screen only
            setup = setup_weight(ctx, prof, dirs)
        elif c == "X1_act_all48":
            setup = lambda: lm.set_ablate_layerwise({h: ctx.dEN[h] for h in range(1, H)}, 1.0)
        elif m["family"].startswith("lora"):
            continue  # handled below after all base-model cells
        else:
            raise ValueError(f"unsupported confirmation cell {c} ({m['family']})")
        run_cell(ctx, col, name, setup, CONF_PLAN, m | {"cell": name, "screen_cell": c}, "confirm")
        utility(ctx, name, setup)
    if any(jload(C.CELLS / f"{c}.json")["family"].startswith("lora") for c in cells):
        anchors_lora(ctx, col, plan=CONF_PLAN, prefix="CF_")
        for n in ("CF_W0_core", "CF_W3_core_plus_act_all48"):
            if n[3:] in cells:
                setup = (lambda: None) if n == "CF_W0_core" else (lambda: lm.set_ablate_layerwise({h: ctx.dEN[h] for h in range(1, H)}, 1.0))
                utility(ctx, n, setup)


def utility(ctx: Ctx, name: str, setup) -> None:
    """S7 utility: 100 items/task x 6 tasks per language; choice = argmax mean per-token log-prob of ' ' + choice after
    the query (plain, no chat template, as exp8's MC check). Per-item correctness saved for paired bootstraps."""
    p = C.CELLS / f"{name}__utility.json"
    if p.exists():
        return
    lm = ctx.lm
    lm.reset()
    lm.set_weight_edit_layerwise({})
    setup()
    t0 = time.time()
    out = {}
    for g in LANGS:
        for task in ("arc_challenge", "boolq", "hellaswag", "openbookqa", "piqa", "winogrande"):
            its = ctx.S[f"s7_{task}"]
            seqs, starts, owner = [], [], []
            for jj, it in enumerate(its):
                q = it[g]
                qi = lm.encode_plain(q)
                for ci, ch in enumerate(it[f"choices_{g}"]):
                    full = lm.encode_plain(q + " " + ch)
                    k = 0
                    while k < min(len(qi), len(full)) and qi[k] == full[k]:
                        k += 1
                    seqs.append(full)
                    starts.append(min(k, len(full) - 1))
                    owner.append((jj, ci))
            nll = lm.seq_nll(seqs, starts)
            by: dict = {}
            for (jj, ci), v in zip(owner, nll):
                by.setdefault(jj, {})[ci] = -v
            out[f"{g}|{task}"] = {it["semantic_id"]: int(max(by[jj], key=by[jj].get) == it["gold"]) for jj, it in enumerate(its)}
    lm.reset()
    lm.set_weight_edit_layerwise({})
    jdump(out, p)
    logger.info(f"utility {name}: " + ", ".join(f"{k}={np.mean(list(v.values())):.2f}" for k, v in out.items()) +
                f" ({time.time()-t0:.0f}s)")


def stage_s5x(ctx: Ctx) -> None:
    sel = jload(C.CFG / "s5x_cells.json")
    lm = ctx.lm
    prepare(ctx)
    col = Collateral(ctx)
    dirs = ctx_dirs(ctx)
    # S5X verified basis: exp4's 100 frozen S5X pairs if available, else the first 100 qc-passing pairs (seeded)
    ids = sel.get("s5x_semantic_ids")
    its = [it for it in ctx.S["s5x"] if it["semantic_id"] in set(ids)] if ids else ctx.S["s5x"][:100]
    ctx.S["s5x_sel"] = its
    plan = [("s5x_sel", "en"), ("s5x_sel", "sl")]
    for c in ["noop"] + sel["cells"]:
        m = jload(C.CELLS / f"{c}.json")
        if m["family"] == "noop":
            setup = lambda: None
        elif m["family"] == "weight":
            prof = {(j, COMPS[i]): v for j, row in enumerate(m["c_profile"]) for i, v in enumerate(row) if v != 0}
            setup = setup_weight(ctx, prof, dirs)
        elif c == "X1_act_all48":
            setup = lambda: lm.set_ablate_layerwise({h: ctx.dEN[h] for h in range(1, H)}, 1.0)
        else:
            raise ValueError(c)
        run_cell(ctx, col, f"S5X_{c}", setup, plan, m | {"cell": f"S5X_{c}", "screen_cell": c}, "s5x")


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["smoke", "partA", "screen", "partA+screen", "confirm", "s5x"])
    args = ap.parse_args()
    setup_logging(f"method_{args.stage}")
    ctx = Ctx(args.stage)
    load_model(ctx)
    if args.stage == "smoke":
        stage_smoke(ctx)
    elif args.stage == "partA":
        stage_partA(ctx)
    elif args.stage == "screen":
        stage_screen(ctx)
    elif args.stage == "partA+screen":
        stage_partA(ctx)
        stage_screen(ctx)
    elif args.stage == "confirm":
        stage_confirm(ctx)
    elif args.stage == "s5x":
        stage_s5x(ctx)
    ctx.lm.close()
    logger.info(f"stage {args.stage} done")


if __name__ == "__main__":
    main()
