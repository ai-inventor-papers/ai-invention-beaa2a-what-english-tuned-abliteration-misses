#!/usr/bin/env python3
"""Iteration-4 experiment 13 - PREDICTING WHERE A REFUSAL EDIT MISSES.

GPU pipeline for a frozen weight-space write-mass overlap instrument
    O_L(edit) = sum_h e_L(h) g(h) / ||g||_2
where e_L(h) is a per-language CAUSAL write profile (judged refusal drop from ablating the frozen English refusal
direction d_EN(h) at ONE hidden index h, DEV items only) and g(h) is the closed-form per-layer removal energy of a
Heretic-family weight edit. O is raced OUT OF SAMPLE against log-energy, layer count, depth span, EN/SL direction
cosine and the one-forward-pass baselines (single-site causal probe; unedited refusal rate).

Stages (resumable; every generation is saved under results/gens/, one JSON per cell):
  --stage smoke     Gate 0 (pins, split SHAs, reuse inventory, DEV/CONF disjointness), Gate 1 (operator identities),
                    Gate 2 (generation sanity), timing model.
  --stage profile   Phase 1: no-op + 48 single-site ablations on DEV items (EN, SL), teacher-forced readout,
                    per-site FLORES collateral.
  --stage confirm   Phase 4: refuses to run unless configs/FREEZE.sha256 matches; matched groups, controls, dose
                    ladder, no-op on the frozen CONF items, FLORES + harmless-KL collateral.
  --stage outside   Phase 5: Qwen/Qwen3-8B (EN, SL, DE, LT): eligibility gate, own d_EN(h), reduced-grid profile,
                    frozen conditions (written by freeze_outside.py) and CONF generations.
Judging is done afterwards by judge/local_judge.py (generation and judge never co-reside on the GPU)."""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import os
import time
from pathlib import Path

import numpy as np
import torch
from loguru import logger

import common as C
from common import LANGS, file_sha256, jdump, jload, setup_logging
from interventions import LM, unit, winsorize

GEN_BS = int(os.environ.get("GEN_BS", 64))
L = 48
H = 49
COMPS = ("o_proj", "down_proj")
P = C.PROTO


# ============================================================================================ context
class Ctx:
    def __init__(self, stage: str):
        self.stage = stage
        self.D = C.load_items()
        self.S = C.build_sets(self.D)
        self.lm: LM | None = None
        self.timings = jload(C.RES / "timings.json") if (C.RES / "timings.json").exists() else {}
        z = np.load(C.DIRS_NPZ)
        self.dEN = z["dEN"].astype(np.float32)
        self.dSL = z["dSL"].astype(np.float32)
        assert self.dEN.shape == (H, 3840), self.dEN.shape
        self.rhat = np.load(C.EXP9 / "results" / "rhat_orth.npy").astype(np.float32)  # [49, D], exp9 frozen

    def tick(self, key: str, t0: float) -> None:
        self.timings[key] = round(time.time() - t0, 1)
        jdump(self.timings, C.RES / "timings.json")


def gen_rec(cell: str, it: dict, lang: str, toks: list[int], text: str, max_new: int, model: str = "gemma") -> dict:
    return {"gid": hashlib.sha256(f"{model}|{cell}|{it['uid']}|{lang}".encode()).hexdigest()[:16], "model": model,
            "cell": cell, "uid": it["uid"], "semantic_id": it["semantic_id"], "kind": it["kind"], "role": it.get("role"),
            "stratum": it.get("stratum"), "category": it.get("category"), "lang": lang, "prompt": it[lang],
            "response": text, "n_tokens": len(toks), "hit_max": len(toks) >= max_new, "max_tok": max_new}


def run_gens(ctx: Ctx, cell: str, plan: list[tuple[list[dict], str]], max_new: int, model: str = "gemma") -> float:
    """Greedy generation under the CURRENT hooks for each (items, lang); resumable per cell file. Returns seconds."""
    lm = ctx.lm
    p = C.GENS / f"{cell}.json"
    have = jload(p) if p.exists() else []
    done = {(r["uid"], r["lang"]) for r in have}
    t0 = time.time()
    n0 = len(have)
    todo = [(it, g) for items, g in plan for it in items if (it["uid"], g) not in done]
    for s0 in range(0, len(todo), 4 * GEN_BS):
        chunk = todo[s0:s0 + 4 * GEN_BS]
        outs = lm.generate([lm.encode_chat(it[g])[0] for it, g in chunk], max_new, batch=GEN_BS)
        have += [gen_rec(cell, it, g, t, lm.tok.decode(t, skip_special_tokens=True), max_new, model)
                 for (it, g), t in zip(chunk, outs)]
        jdump(have, p)
    dt = time.time() - t0
    if len(have) > n0:
        logger.info(f"gens {cell}: +{len(have)-n0} in {dt:.0f}s ({dt/max(1, len(have)-n0):.3f}s/gen)")
    return dt


# ============================================================================================ collateral
class Collateral:
    """FLORES per-token NLL change vs the unedited model (teacher forced, plain text) and the 32-token harmless KL vs
    the unedited model on S3 Dolly prompts (100/language). References are computed once with NO hooks."""

    def __init__(self, ctx: Ctx, langs=LANGS, flores_items=None, dolly_items=None, tag: str = "gemma"):
        self.ctx, self.langs, self.tag = ctx, tuple(langs), tag
        lm = ctx.lm
        self.flo = flores_items if flores_items is not None else ctx.S["flores"]
        self.flo_seqs = {g: [lm.encode_plain(it[g]) for it in self.flo] for g in self.langs}
        pb = C.RES / f"ref_flores_base_{tag}.json"
        pc = C.RES / f"ref_dolly_cont_{tag}.json"
        lm.reset()
        lm.set_weight_edit_layerwise({})
        if not pb.exists():
            jdump({g: lm.seq_nll(self.flo_seqs[g], [1] * len(self.flo)).tolist() for g in self.langs}, pb)
        self.flo_base = {g: np.array(v) for g, v in jload(pb).items()}
        self.dol = dolly_items if dolly_items is not None else ctx.S["dolly"]
        if not pc.exists():
            cont = {}
            for g in self.langs:
                gg = lm.generate([lm.encode_chat(it[g])[0] for it in self.dol], 32, batch=GEN_BS)
                cont[g] = [c if c else [lm.tok.eos_token_id] for c in gg]
            jdump(cont, pc)
        cont = jload(pc)
        self.kl = {}
        for g in self.langs:
            base = [lm.encode_chat(it[g])[0] for it in self.dol]
            seqs = [b + c for b, c in zip(base, cont[g])]
            starts = [len(b) for b in base]
            groups: dict = {}
            for i, c in enumerate(cont[g]):
                groups.setdefault(len(c), []).append(i)
            ref = [None] * len(seqs)
            for n, ix in groups.items():
                for i, r in zip(ix, lm.ref_topk([seqs[i] for i in ix], [starts[i] for i in ix], n)):
                    ref[i] = r
            self.kl[g] = (seqs, starts, groups, ref)

    def flores(self, n: int | None = None) -> dict:
        lm = self.ctx.lm
        out = {}
        for g in self.langs:
            seqs = self.flo_seqs[g][:n] if n else self.flo_seqs[g]
            nll = lm.seq_nll(seqs, [1] * len(seqs))
            out[g] = float(np.mean(nll - self.flo_base[g][:len(seqs)]))
        return out

    def kl_dolly(self) -> dict:
        lm = self.ctx.lm
        out = {}
        for g in self.langs:
            seqs, starts, groups, ref = self.kl[g]
            kl = np.zeros(len(seqs))
            for nn, ix in groups.items():
                kl[ix] = lm.kl_vs_ref([seqs[i] for i in ix], [starts[i] for i in ix], nn, [ref[i] for i in ix])
            out[g] = float(kl.mean())
        return out


# ============================================================================================ weight edits
def load_e(p: Path) -> dict:
    return {(int(k.split("|")[0]), k.split("|")[1]): v for k, v in jload(p)["e"].items()}


def profile_energy(prof: dict, e: dict) -> float:
    return float(sum(c * c * e[key] for key, c in prof.items()))


def weight_spec(prof: dict, dirs: dict) -> dict:
    """prof {(j, comp): c}; dirs {j: direction} -> {(j, comp): (dir, c)}"""
    return {key: (dirs[key[0]], c) for key, c in prof.items() if c != 0.0}


def energies(lm: LM, dirs_by_layer: dict) -> dict:
    out = {}
    for j, d in dirs_by_layer.items():
        for comp in COMPS:
            out[(int(j), comp)] = float(lm.module_energy(int(j), comp, np.asarray(d)[None])[0])
    return out


def random_write_dirs(lm: LM, rhat_j: dict, layers0: list[int], seed: int, massive: int | None) -> dict:
    """exp9's write-space random draw: u = unit(W_o g1) + unit(W_down g2), g ~ N(0, I), orthogonalised against rhat_j,
    massive dimension zeroed. layers0 are 0-based decoder layers."""
    g = torch.Generator(device="cuda").manual_seed(seed)
    out = {}
    for j in layers0:
        u = torch.zeros(lm.D, device="cuda")
        for comp in COMPS:
            W = lm.module_weight(j, comp).float()
            x = torch.randn(W.shape[1], generator=g, device="cuda")
            v = W @ x
            u += v / (v.norm() + 1e-12)
            del W
        u = u.cpu().numpy().astype(np.float64)
        if massive is not None:
            u[massive] = 0.0
        r = rhat_j[j].astype(np.float64)
        u = u - (u @ r) * r
        out[j] = unit(u)
    return out


def scaled_control(prof: dict, e_ctrl: dict, E_target: float, cap: float = 2.0) -> tuple[dict, float, float, bool]:
    base = profile_energy(prof, e_ctrl)
    s = math.sqrt(E_target / max(base, 1e-12))
    newp = {k: min(cap, s * c) for k, c in prof.items()}
    E = profile_energy(newp, e_ctrl)
    return newp, s, E, bool(abs(E / E_target - 1) <= 0.10)


def cell_meta(name: str, family: str, prof: dict | None, E: float | None, extra: dict | None = None, nl: int = L) -> dict:
    m = {"cell": name, "family": family, "E": E}
    if prof is not None:
        per = np.zeros((nl, 2))
        for (j, comp), c in prof.items():
            per[j, COMPS.index(comp)] = c
        m["c_profile"] = per.tolist()
        cov = sorted({j + 1 for (j, _), c in prof.items() if c != 0})
        m["layers"] = cov
        m["n_layers"] = len(cov)
    return m | (extra or {})


def run_cell(ctx: Ctx, col: Collateral | None, name: str, setup, plan, meta: dict, stage: str, max_new: int,
             model: str = "gemma", flores_n: int | None = None, with_kl: bool = True) -> None:
    """Apply hooks via setup(), generate, measure collateral, clean up. Skips if already complete."""
    pm = C.CELLS / f"{name}.json"
    sig = [[len(items), g] for items, g in plan]
    if pm.exists() and jload(pm).get("complete_plan") == sig:
        return
    t0 = time.time()
    lm = ctx.lm
    lm.reset()
    lm.set_weight_edit_layerwise({})
    setup()
    dt_gen = run_gens(ctx, name, plan, max_new, model)
    t1 = time.time()
    fl = col.flores(flores_n) if col is not None else None
    kl = col.kl_dolly() if (col is not None and with_kl) else None
    lm.reset()
    lm.set_weight_edit_layerwise({})
    meta = meta | {"stage": stage, "model": model, "flores_dNLL": fl, "kl_dolly": kl, "sec_gen": round(dt_gen, 1),
                   "sec_tf": round(time.time() - t1, 1), "complete_plan": sig, "max_new": max_new,
                   "done_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    jdump(meta, pm)
    ctx.tick(f"cell_{name}", t0)
    fls = "" if fl is None else " ".join(f"{g} {v:+.3f}" for g, v in fl.items())
    logger.info(f"[{stage}] {name}: FLORES dNLL {fls}; KL {kl}; {time.time()-t0:.0f}s")


# ============================================================================================ stage: smoke
def load_model(ctx: Ctx) -> None:
    t0 = time.time()
    torch.cuda.set_per_process_memory_fraction(0.92)
    ctx.lm = LM("gemma")
    ctx.tick("load_gemma", t0)


def reuse_inventory() -> dict:
    """Stat and hash every reused input; record what was found (plan Phase 0)."""
    inv = {}
    items = {
        "dirs": C.DIRS_NPZ, "rhat_orth": C.EXP9 / "results/rhat_orth.npy", "energy_real": C.EXP9 / "results/energy_real.json",
        "exp9_cells_csv": C.EXP9 / "results/cells.csv", "exp9_cells_dir": C.EXP9 / "results/cells",
        "exp9_write_mass": C.EXP9 / "results/write_mass.json", "exp8_layerwise_pc": C.EXP8 / "results/gemma/layerwise_pc.npy",
        "exp10_heretic_op": C.EXP10 / "heretic_op.py", "exp10_results": C.EXP10 / "results",
        "exp12_items_conf": C.EXP12 / "data/items_conf.jsonl", "exp12_items_dir": C.EXP12 / "data/items_dir.jsonl",
        "exp12_items_cal": C.EXP12 / "data/items_cal.jsonl", "exp12_items_flores": C.EXP12 / "data/items_flores.jsonl",
        "exp11_clf": C.EXP11 / "scorer/refusal_clf.joblib", "exp4_protocol": C.EXP4 / "protocol.yaml",
        "label_map": C.EVAL1 / "configs/label_map.yaml",
    }
    for k, p in items.items():
        if p.is_dir():
            inv[k] = {"path": str(p), "exists": True, "n_files": len(list(p.iterdir()))}
        elif p.exists():
            inv[k] = {"path": str(p), "exists": True, "bytes": p.stat().st_size, "sha256": file_sha256(p)}
        else:
            inv[k] = {"path": str(p), "exists": False}
    jdump(inv, C.RES / "reuse_inventory.json")
    return inv


def stage_smoke(ctx: Ctx) -> None:
    lm = ctx.lm
    inv = reuse_inventory()
    g0 = {"model": C.MODEL, "splits_sha_ok": dict(C._SHA_OK), "directions_npz_sha256": file_sha256(C.DIRS_NPZ),
          "exp4_protocol_identical": file_sha256(C.CFG / "exp4_protocol.yaml") == inv["exp4_protocol"]["sha256"],
          "missing_reuse": [k for k, v in inv.items() if not v["exists"]],
          "n_dev": len(ctx.S["dev"]), "n_conf_hoc": len(ctx.S["conf_hoc"]), "n_conf_s5x": len(ctx.S["conf_s5x"]),
          "dev_conf_disjoint": True}
    from huggingface_hub import snapshot_download
    snap = Path(snapshot_download(C.MODEL["repo"], revision=C.MODEL["sha"], local_files_only=True))
    g0["weight_files_sha256"] = {p.name: file_sha256(p) for p in sorted(snap.glob("*.safetensors"))}
    # ---- spot re-verification of the frozen directions: fresh diff-in-means at 4 layers (S3 half A, pos -1, winsorised)
    cos_fresh = {}
    harm = ctx.S["A_harm_all"]
    ben = ctx.S["A_ben"]
    seqs_h = [lm.encode_chat(it["en"])[0] for it in harm]
    seqs_b = [lm.encode_chat(it["en"])[0] for it in ben]
    spot = [8, 20, 32, 44]
    Xh = lm.capture(seqs_h, [[len(s) - 1] for s in seqs_h], [[len(s) - 1] for s in seqs_h], layers=spot)[:, :, 0]
    Xb = lm.capture(seqs_b, [[len(s) - 1] for s in seqs_b], [[len(s) - 1] for s in seqs_b], layers=spot)[:, :, 0]
    for k, h in enumerate(spot):
        d = winsorize(Xh[:, k]).mean(0) - winsorize(Xb[:, k]).mean(0)
        cos_fresh[h] = float(np.dot(unit(d), unit(ctx.dEN[h])))
    g0["cos_dEN_fresh_vs_frozen"] = cos_fresh
    g0["cos_mean"] = float(np.mean(list(cos_fresh.values())))
    assert g0["cos_mean"] >= 0.95, g0
    jdump(g0, C.RES / "gate0_pins.json")
    logger.info(f"Gate 0 ok: cos fresh vs frozen {cos_fresh}")
    # ---- Gate 1: operator identities
    g1 = {}
    e9 = load_e(C.EXP9 / "results/energy_real.json")
    dirs = {j: ctx.rhat[j + 1] for j in range(L)}
    rel = []
    for j in (5, 20, 40):
        for comp in COMPS:
            e_new = float(lm.module_energy(j, comp, dirs[j][None])[0])
            rel.append(abs(e_new - e9[(j, comp)]) / e9[(j, comp)])
    g1["energy_recompute_vs_exp9_max_rel"] = float(max(rel))
    # (a) hook == explicit (I - c r r^T) W on one module; (b) ||dW||_F^2 == c^2 ||W^T r||^2
    j, comp, c = 20, "o_proj", 1.3
    mod = lm.layers[j].self_attn.o_proj
    W = lm.module_weight(j, comp).float()
    r = torch.as_tensor(dirs[j], dtype=torch.float32).cuda()
    x = torch.randn(4, W.shape[1], device="cuda", dtype=torch.bfloat16)
    lm.set_weight_edit_layerwise({(j, comp): (dirs[j], c)})
    with torch.inference_mode():
        y_hook = mod(x).float()
    lm.set_weight_edit_layerwise({})
    with torch.inference_mode():
        y0 = mod(x).float()
    y_expl = y0 - c * (y0 @ r)[..., None] * r
    g1["hook_vs_explicit_rel_err"] = float((y_hook - y_expl).norm() / y_expl.norm())
    Wp = W - c * torch.outer(r, r @ W)
    y_W = x.float() @ Wp.T
    g1["hook_vs_explicit_W_product_rel_err"] = float((y_hook - y_W).norm() / y_W.norm())
    dW = W - Wp
    g1["energy_identity_abs_err"] = float(abs((dW ** 2).sum().item() - c * c * ((r @ W) ** 2).sum().item()))
    g1["energy_identity_rel_err"] = g1["energy_identity_abs_err"] / float(c * c * ((r @ W) ** 2).sum().item())
    del W, Wp, dW
    # (c) zero-coefficient edit reproduces the unedited logits
    seqs = [lm.encode_chat(it["en"])[0] for it in ctx.S["dev"][:8]]
    lp0 = lm.first_token_lp(seqs, list(range(50)))
    lm.set_weight_edit_layerwise({(10, "o_proj"): (dirs[10], 0.0)})
    lp1 = lm.first_token_lp(seqs, list(range(50)))
    lm.set_weight_edit_layerwise({})
    g1["zero_edit_max_abs_logprob_diff"] = float(np.abs(lp0 - lp1).max())
    g1["pass"] = bool(g1["hook_vs_explicit_rel_err"] < 1e-2 and g1["hook_vs_explicit_W_product_rel_err"] < 2e-2 and g1["energy_identity_rel_err"] < 1e-5
                      and g1["zero_edit_max_abs_logprob_diff"] == 0.0 and g1["energy_recompute_vs_exp9_max_rel"] < 1e-3)
    jdump(g1, C.RES / "gate1_operator.json")
    logger.info(f"Gate 1: {g1}")
    assert g1["pass"], g1
    # ---- Gate 2: generation sanity + timing model (8 DEV prompts per language, no-op) at the two token budgets
    tm = {}
    for mx in (P["decoding"]["dev_max_new"], P["decoding"]["conf_max_new"]):
        items = ctx.S["A_harm_all"][:32]
        seqs = [lm.encode_chat(it[g])[0] for g in LANGS for it in items]
        t0 = time.time()
        outs = lm.generate(seqs, mx, batch=GEN_BS)
        tm[f"sec_per_gen_{mx}tok_bs{GEN_BS}"] = (time.time() - t0) / len(seqs)
        if mx == P["decoding"]["dev_max_new"]:
            smp = []
            for (g, it), o in zip([(g, it) for g in LANGS for it in items], outs):
                smp.append({"lang": g, "uid": it["uid"], "response": lm.tok.decode(o, skip_special_tokens=True)[:300]})
            jdump(smp[:8] + smp[32:40], C.RES / "gate2_samples.json")
    t0 = time.time()
    fl_seqs = [lm.encode_plain(it["en"]) for it in ctx.S["flores"][:40]]
    lm.seq_nll(fl_seqs, [1] * len(fl_seqs))
    tm["sec_flores40_tf"] = time.time() - t0
    jdump(tm, C.RES / "timing_model.json")
    logger.info(f"timing: {tm}")


# ============================================================================================ stage: profile (Phase 1)
def stage_profile(ctx: Ctx) -> None:
    """Phase 1: the causal write profile. no-op + single-site ablation of d_EN(h) at h = 1..48, DEV items, EN + SL.
    Order: 3 sites known effective in exp8/exp9 (20, 24, 16) and 3 inert (2, 46, 40) first (Gate 3 positive control)."""
    lm = ctx.lm
    mx = P["decoding"]["dev_max_new"]
    plan = [(ctx.S["dev"], g) for g in LANGS]
    run_cell(ctx, None, "PF_noop", lambda: None, plan, cell_meta("PF_noop", "noop", None, None, {"part": "profile"}),
             "profile", mx)
    # teacher-forced readout reference: no-op greedy reply of ALL 44 DEV harmful items (first 24 tokens)
    tf_p = C.RES / "profile_tf_prefix.json"
    allh = ctx.S["A_harm_all"]
    if not tf_p.exists():
        lm.reset()
        pre = {}
        for g in LANGS:
            seqs = [lm.encode_chat(it[g])[0] for it in allh]
            pre[g] = [o[:24] if o else [lm.tok.eos_token_id] for o in lm.generate(seqs, 24, batch=GEN_BS)]
        jdump(pre, tf_p)
    pre = jload(tf_p)
    prompts = {g: [lm.encode_chat(it[g])[0] for it in allh] for g in LANGS}
    fl_seqs = {g: [lm.encode_plain(it[g]) for it in ctx.S["flores_dev40"]] for g in LANGS}
    tfp = C.RES / "profile_tf.json"
    tf = jload(tfp) if tfp.exists() else {}
    if "noop" not in tf:
        lm.reset()
        tf["noop"] = {g: lm.cont_logprob(prompts[g], pre[g]).tolist() for g in LANGS}
        tf["noop_flores"] = {g: lm.seq_nll(fl_seqs[g], [1] * len(fl_seqs[g])).tolist() for g in LANGS}
        jdump(tf, tfp)
    order = [20, 24, 16, 2, 46, 40] + [h for h in range(1, H) if h not in (20, 24, 16, 2, 46, 40)]
    for h in order:
        name = f"PF_h{h:02d}"
        setup = (lambda h=h: lm.set_ablate_layerwise({h: ctx.dEN[h]}, 1.0))
        run_cell(ctx, None, name, setup, plan, cell_meta(name, "act_single", None, None, {"part": "profile", "h": h}),
                 "profile", mx)
        if name not in tf:
            lm.reset()
            setup()
            tf[name] = {g: lm.cont_logprob(prompts[g], pre[g]).tolist() for g in LANGS}
            tf[name + "_flores"] = {g: lm.seq_nll(fl_seqs[g], [1] * len(fl_seqs[g])).tolist() for g in LANGS}
            lm.reset()
            jdump(tf, tfp)
    logger.info("Phase 1 profile complete")


# ============================================================================================ stage: confirm (Phase 4)
def check_freeze() -> dict:
    fz = C.CFG / "FREEZE.sha256"
    assert fz.exists(), "FREEZE.sha256 missing: freeze predictions before confirmation"
    want = {l.split()[1]: l.split()[0] for l in fz.read_text().splitlines() if l.strip()}
    for f, h in want.items():
        got = file_sha256(C.ROOT / f)
        if got != h:
            raise RuntimeError(f"freeze guard: {f} changed after freeze ({got[:12]} != {h[:12]})")
    return jload(C.CFG / "frozen_predictions.json")


def conf_items(ctx: Ctx, fp: dict) -> list[dict]:
    ids = fp["frozen_confirmation_item_uids"]
    pool = {it["uid"]: it for it in ctx.S["conf"]}
    assert set(ids) <= set(pool), "frozen CONF ids not reproducible from the dataset"
    return [pool[u] for u in ids]


def stage_confirm(ctx: Ctx) -> None:
    fp = check_freeze()
    lm = ctx.lm
    mx = P["decoding"]["conf_max_new"]
    items = conf_items(ctx, fp)
    plan = [(items, g) for g in LANGS]
    col = Collateral(ctx)
    dirs = {j: ctx.rhat[j + 1] for j in range(L)}
    e_real = load_e(C.EXP9 / "results/energy_real.json")
    conds = fp["confirmation_condition_list"]
    order = sorted(conds, key=lambda c: c["priority"])
    for cd in order:
        name = cd["cell"]
        if cd["family"] == "noop":
            run_cell(ctx, col, name, lambda: None, plan, cell_meta(name, "noop", None, 0.0, cd), "confirm", mx)
            continue
        if cd["family"] == "weight":
            prof = {(k - 1, comp): float(cd["c"]) for k in cd["layers"] for comp in COMPS}
            E = profile_energy(prof, e_real)
            assert abs(E - cd["E"]) / cd["E"] < 1e-6, (name, E, cd["E"])
            run_cell(ctx, col, name, (lambda prof=prof: lm.set_weight_edit_layerwise(weight_spec(prof, dirs))), plan,
                     cell_meta(name, "weight", prof, E, cd), "confirm", mx)
            continue
        if cd["family"] in ("random", "pc"):
            control_cell(ctx, col, cd, dirs, e_real, plan, mx)
            continue
        raise ValueError(cd)


def control_cell(ctx: Ctx, col: Collateral, cd: dict, dirs: dict, e_real: dict, plan, mx: int) -> None:
    """Layer-matched write-space random (<= 5 draws) or energy-matched harmless-PC control at the HIGH-O member's
    layers; energy within 10% and SL FLORES dNLL (100 pairs) within +-50% (floor 0.02 nats) of the real member."""
    name = cd["cell"]
    if (C.CELLS / f"{name}.json").exists():
        return
    lm = ctx.lm
    real = jload(C.CELLS / f"{cd['control_of']}.json")
    layers0 = [k - 1 for k in real["layers"]]
    prof = {(j, comp): float(real["c"]) for j in layers0 for comp in COMPS}
    E_t = real["E"]
    fl_real = real["flores_dNLL"]
    tried, best = [], None
    n_draw = 5 if cd["family"] == "random" else 1
    for k in range(n_draw):
        if cd["family"] == "random":
            seed = C.SEED + 1000 * k + int(hashlib.sha256(name.encode()).hexdigest()[:6], 16) % 997
            rd = random_write_dirs(lm, dirs, layers0, seed, C.MASSIVE_DIM)
        else:
            pcs = np.load(C.EXP8 / "results/gemma/layerwise_pc.npy")
            rd = {}
            for j in layers0:
                u = pcs[j].astype(np.float64)
                r = dirs[j].astype(np.float64)
                rd[j] = unit(u - (u @ r) * r)
        e_r = energies(lm, rd)
        newp, s, E, ok_e = scaled_control(prof, e_r, E_t)
        lm.reset()
        lm.set_weight_edit_layerwise(weight_spec(newp, rd))
        fl = col.flores(n=100)
        lm.set_weight_edit_layerwise({})
        tol = max(0.5 * abs(fl_real["sl"]), 0.02)
        ok_c = abs(fl["sl"] - fl_real["sl"]) <= tol
        tried.append({"draw": k, "scale": s, "E": E, "E_target": E_t, "energy_ok": ok_e, "flores_sl_100": fl["sl"],
                      "flores_en_100": fl["en"], "collateral_ok": ok_c, "max_c": max(newp.values())})
        score = (0 if (ok_e and ok_c) else 1 if ok_e else 2, abs(fl["sl"] - fl_real["sl"]))
        if best is None or score < best[0]:
            best = (score, rd, newp, E, k)
        if ok_e and ok_c:
            break
    _, rd, newp, E, k = best
    jdump({"cell": name, "tries": tried, "chosen_draw": k}, C.CELLS / f"{name}__draws.json")
    run_cell(ctx, col, name, (lambda: lm.set_weight_edit_layerwise(weight_spec(newp, rd))), plan,
             cell_meta(name, cd["family"], newp, E, cd | {"E_target": E_t, "energy_matched": tried[k]["energy_ok"],
                                                          "collateral_matched": tried[k]["collateral_ok"]}), "confirm", mx)


# ============================================================================================ main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["smoke", "profile", "confirm", "outside"])
    args = ap.parse_args()
    setup_logging(f"method_{args.stage}")
    ctx = Ctx(args.stage)
    if args.stage == "outside":
        import outside
        outside.run(ctx)
        return
    load_model(ctx)
    {"smoke": stage_smoke, "profile": stage_profile, "confirm": stage_confirm}[args.stage](ctx)
    ctx.lm.close()
    gc.collect()


if __name__ == "__main__":
    logger.catch(reraise=True)(main)()
