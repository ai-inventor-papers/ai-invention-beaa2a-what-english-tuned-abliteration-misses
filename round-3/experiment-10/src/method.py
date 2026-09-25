#!/usr/bin/env python3
"""GaMS3-12B-Instruct: does spreading an English-derived refusal edit deeper unlock Slovene?
(iteration 3, gen_art_experiment_10 - depth-coverage x strength factorial + DEV redundancy index)

Stages (each resumable; every cell writes results/cells/<cell>/{gens.json, tf.json, meta.json}):
  --stage A   load NF4 GaMS3 + rank-3 PEFT adapters (Heretic layout) -> GATE 2 smoke checks (template, adapter-delta vs dense,
              no-op reproduction vs exp8 G0, timing) -> half-A residual capture -> GATE d_EN sanity (cos >= .99 vs stored)
              -> layer-matched random / energy-matched PC controls -> PART A activation arms on DEV (S3 half A, 40 harmful
              items x EN/SL) -> GATE 3 operator equivalence vs Heretic's own abliterate() source -> GATE 4 energy checks
              -> per-module energy table -> matched-energy design (configs/design.json), all BEFORE any Part B generation.
  --stage B   PART B weight-edit cells in priority order (configs/priority.json): T1 matched-energy groups (+ random / PC
              controls), T2 anchors (G1 single-site, CORE trial-88 adapter, SWAP_in = Gemma trial-96 kernel on GaMS3),
              T3 coverage grid at c = 1, T4 other strengths. SCREEN = S3 JBB half B (41 harmful x EN/SL, 128 tokens) for
              every cell; CONFIRM = S4 hoc (70 harmful @256 + 70 harmless @128 tokens x EN/SL) for T1+T2 cells, only after
              configs/FREEZE.sha256 holds the frozen index + predictions.
The judge (local Qwen3-14B) runs in a separate process (judge_local.py); analysis in analysis.py."""
from __future__ import annotations

import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")  # shared 48-core host: BLAS oversubscription made a 276x3840 SVD take 35 s

import argparse
import gc
import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np
import torch
from loguru import logger

import common as C
from common import LANGS, jdump, jload, rule_label, setup_logging
from heretic_op import COMPONENTS, Editor, HereticShim, heretic_abliterate_fn, kernel_weights, lora_energy
from interventions import LM, cos, unit, winsorize

GEN_BS = 64
TOK_DEV, TOK_SCREEN, TOK_CONF_H, TOK_CONF_B = 128, 128, 192, 128  # 192 (not 256) on confirmation: GPU budget, logged
W_GRID = np.round(np.arange(0.0, 3.0001, 0.125), 4)  # per-module energy table grid (weights)
C_BOUND = 1.5  # Heretic's max_weight upper bound for the real (d_EN) arms
C_BOUND_CTRL = 3.0  # controls may go further to reach the matched energy (recorded)
DEADLINE = float(__import__("os").environ.get("AII_DEADLINE", "0"))  # unix time after which stage B stops starting cells


# ============================================================================================ loading
def load() -> tuple[LM, Editor]:
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    t0 = time.time()
    repo, sha = C.MODEL["repo"], C.MODEL["sha"]
    tok = AutoTokenizer.from_pretrained(repo, revision=sha)
    bnbc = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_quant_type="nf4",
                              bnb_4bit_use_double_quant=True)
    base = AutoModelForCausalLM.from_pretrained(repo, revision=sha, dtype=torch.bfloat16, quantization_config=bnbc,
                                                device_map="cuda:0", attn_implementation="eager")
    for p in base.parameters():
        p.requires_grad_(False)
    names = sorted(n for n, _ in base.named_modules() if n.endswith("self_attn.o_proj") or n.endswith("mlp.down_proj"))
    cfg = LoraConfig(r=3, target_modules=names, lora_alpha=3, lora_dropout=0, bias="none", task_type="CAUSAL_LM")
    pm = get_peft_model(base, cfg)  # Heretic's _apply_lora (r = full_normalization_lora_rank = 3, alpha = r)
    pm.eval()
    torch.cuda.set_per_process_memory_fraction(0.92)
    lm = LM("gams3", hf_model=pm, tok=tok)
    ed = Editor(pm, lm.layers)
    ed.reset()
    logger.info(f"loaded GaMS3 NF4 + PEFT r=3 on {len(names)} modules in {time.time()-t0:.0f}s; "
                f"VRAM {torch.cuda.memory_allocated()/1e9:.1f} GB")
    return lm, ed


def decode(lm: LM, ids: list[int]) -> str:
    return lm.tok.decode(ids, skip_special_tokens=True)


def gen_rec(cell: str, it: dict, lang: str, text: str, n: int, split: str) -> dict:
    return {"gid": hashlib.sha256(f"gams3|{cell}|{split}|{it['uid']}|{lang}".encode()).hexdigest()[:16], "model": "gams3",
            "cell": cell, "split": split, "uid": it["uid"], "semantic_id": it["semantic_id"], "kind": it["kind"],
            "role": it.get("role"), "source": it.get("source"), "lang": lang, "prompt": it[lang], "response": text,
            "n_tokens": n, "rule_label": rule_label(text)}


# ============================================================================================ cell runner
class Runner:
    def __init__(self, lm: LM, ed: Editor, S: dict):
        self.lm, self.ed, self.S = lm, ed, S
        self.ref = C.RES / "ref"
        self.ref.mkdir(exist_ok=True)
        self.timings = jload(C.RES / "timings.json") if (C.RES / "timings.json").exists() else {}

    def tick(self, k: str, t0: float) -> None:
        self.timings[k] = round(time.time() - t0, 1)
        jdump(self.timings, C.RES / "timings.json")

    def gens(self, cell: str, plan: list[tuple[str, str, str, int]]) -> None:
        """plan = [(split_tag, set_name, lang, max_new)]; generates what is missing under the CURRENT edit."""
        p = C.CELLS / cell / "gens.json"
        have = jload(p) if p.exists() else []
        done = {(r["split"], r["uid"], r["lang"]) for r in have}
        todo_by_tok: dict = {}
        for tag, name, g, mx in plan:
            for it in self.S[name]:
                if (tag, it["uid"], g) not in done:
                    todo_by_tok.setdefault(mx, []).append((tag, it, g))
        t0, n0 = time.time(), len(have)
        for mx, todo in todo_by_tok.items():
            seqs = [self.lm.encode_chat(it[g])[0] for _, it, g in todo]
            outs = self.lm.generate(seqs, mx, batch=GEN_BS)
            have += [gen_rec(cell, it, g, decode(self.lm, o), len(o), tag) for (tag, it, g), o in zip(todo, outs)]
            jdump(have, p)
        if len(have) > n0:
            dt = time.time() - t0
            rr = {f"{t}|{g}": round(float(np.mean([r["rule_label"] == "refused" for r in have if r["split"] == t and r["lang"] == g])), 2)
                  for t in sorted({r["split"] for r in have}) for g in LANGS}
            logger.info(f"[{cell}] +{len(have)-n0} gens in {dt:.0f}s ({dt/(len(have)-n0):.2f}s/gen); rule-refused {rr}")

    # ---------------------------------------------------------------- teacher-forced collateral
    def flores_base(self, name: str) -> dict:
        p = self.ref / f"flores_{name}_base.json"
        if not p.exists():
            assert self.lm.state.mode is None and self.ed.total_energy() == 0.0, "reference must come from the unedited model"
            jdump({g: self.lm.seq_nll([self.lm.encode_plain(it[g]) for it in self.S[name]], [1] * len(self.S[name])).tolist()
                   for g in LANGS}, p)
        return {g: np.array(v) for g, v in jload(p).items()}

    def dolly_ref(self):
        p, pk = self.ref / "dolly_B_cont.json", self.ref / "dolly_B_ref.npz"
        dol = self.S["B_dolly"]
        if not p.exists():
            assert self.lm.state.mode is None and self.ed.total_energy() == 0.0
            cont = {}
            for g in LANGS:
                gg = self.lm.generate([self.lm.encode_chat(it[g])[0] for it in dol], 32, batch=GEN_BS)
                cont[g] = [c if c else [self.lm.tok.eos_token_id] for c in gg]
            jdump(cont, p)
        cont = jload(p)
        refs = np.load(pk, allow_pickle=True)["refs"].item() if pk.exists() else {}
        out = {}
        for g in LANGS:
            base = [self.lm.encode_chat(it[g])[0] for it in dol]
            seqs = [b + c for b, c in zip(base, cont[g])]
            starts = [len(b) for b in base]
            groups: dict = {}
            for i, c in enumerate(cont[g]):
                groups.setdefault(len(c), []).append(i)
            if g not in refs:
                assert self.lm.state.mode is None and self.ed.total_energy() == 0.0
                ref = [None] * len(seqs)
                for n, ix in groups.items():
                    for i, r in zip(ix, self.lm.ref_topk([seqs[i] for i in ix], [starts[i] for i in ix], n)):
                        ref[i] = r
                refs[g] = ref
            out[g] = (seqs, starts, groups, refs[g])
        if not pk.exists():
            np.savez(pk, refs=np.array(refs, dtype=object))
        return out

    def mc_prep(self):
        prep = {}
        for g in LANGS:
            seqs, starts, owner = [], [], []
            for j, it in enumerate(self.S["B_mc"]):
                qi = self.lm.encode_plain(it[g])
                for ci, ch in enumerate(it[f"choices_{g}"]):
                    full = self.lm.encode_plain(it[g] + " " + ch)
                    k = 0
                    while k < min(len(qi), len(full)) and qi[k] == full[k]:
                        k += 1
                    seqs.append(full)
                    starts.append(min(k, len(full) - 1))
                    owner.append((j, ci))
            prep[g] = (seqs, starts, owner)
        return prep

    def tf(self, cell: str, flores_set: str, full: bool) -> None:
        """FLORES dNLL (always); Dolly-B 32-token KL vs the unedited model and MC-B accuracy (full=True)."""
        p = C.CELLS / cell / "tf.json"
        if p.exists():
            return
        t0 = time.time()
        out: dict = {"flores_set": flores_set}
        fb = self.flores_base(flores_set)
        for g in LANGS:
            its = self.S[flores_set]
            n = self.lm.seq_nll([self.lm.encode_plain(it[g]) for it in its], [1] * len(its))
            out[f"flores_{g}"] = {it["semantic_id"]: float(a - b) for it, a, b in zip(its, n, fb[g])}
        if full:
            if not hasattr(self, "_dol"):
                self._dol = self.dolly_ref()
                self._mc = self.mc_prep()
            for g in LANGS:
                seqs, starts, groups, ref = self._dol[g]
                kl = np.zeros(len(seqs))
                for nn, ix in groups.items():
                    kl[ix] = self.lm.kl_vs_ref([seqs[i] for i in ix], [starts[i] for i in ix], nn, [ref[i] for i in ix])
                out[f"kl_{g}"] = {it["semantic_id"]: float(k) for it, k in zip(self.S["B_dolly"], kl)}
                ms, st, owner = self._mc[g]
                nll = self.lm.seq_nll(ms, st)
                by: dict = {}
                for (j, ci), v in zip(owner, nll):
                    by.setdefault(j, {})[ci] = -v
                acc = {}
                for j, it in enumerate(self.S["B_mc"]):
                    lp = by[j]
                    acc[it["semantic_id"]] = float(max(lp, key=lp.get) == it["gold"])
                out[f"mc_{g}"] = acc
        jdump(out, p)
        logger.info(f"[{cell}] TF in {time.time()-t0:.0f}s: FLORES dNLL EN {np.mean(list(out['flores_en'].values())):+.3f} "
                    f"SL {np.mean(list(out['flores_sl'].values())):+.3f}" +
                    (f"; KL SL {np.mean(list(out['kl_sl'].values())):.3f}; MC SL {np.mean(list(out['mc_sl'].values())):.2f}"
                     if full else ""))


# ============================================================================================ STAGE A
def smoke(lm: LM, ed: Editor, S: dict, R: Runner) -> dict:
    p = C.RES / "smoke.json"
    if p.exists():
        return jload(p)
    out: dict = {}
    # (b) template: EN and SL render through the same template (only the user content differs)
    it = S["DEV_H"][0]
    re_, rs = lm.render(it["en"]), lm.render(it["sl"])
    out["template"] = {"en_prefix_equal": re_.split(it["en"])[0] == rs.split(it["sl"])[0],
                       "en_suffix_equal": re_.split(it["en"])[1] == rs.split(it["sl"])[1],
                       "rendered_en": re_, "rendered_sl": rs,
                       "chat_template_sha256": hashlib.sha256((lm.tok.chat_template or "").encode()).hexdigest()}
    assert out["template"]["en_prefix_equal"] and out["template"]["en_suffix_equal"], "template differs by language"
    # (a) adapter-delta test: PEFT LoRA output delta == x @ (B A)^T (alpha/r = 1, Heretic full strength)
    Z = np.load(C.E8 / "directions/gams3_all_layers.npz")
    ed.apply(Z["dEN"], {(20, "attn.o_proj"): 1.0, (20, "mlp.down_proj"): 1.0})
    errs = {}
    for comp in COMPONENTS:
        m = ed.modules[(20, comp)]
        x = torch.randn(4, m.in_features, device="cuda", dtype=torch.bfloat16)
        with torch.inference_mode():
            y1 = m(x).float()
            y0 = m.base_layer(x).float()
        A, B = m.lora_A["default"].weight.detach().float(), m.lora_B["default"].weight.detach().float()
        dd = x.float() @ (B @ A).T
        dy = y1 - y0
        scale = float((dy * dd).sum() / (dd * dd).sum())  # must be 1 (lora_alpha = r -> full strength)
        errs[comp] = {"fitted_scale": scale, "resid_rel_to_output": float((dy - dd).norm() / y0.norm()),
                      "delta_rel_to_output": float(dd.norm() / y0.norm())}
    ed.reset()
    out["adapter_delta"] = errs
    assert all(abs(e["fitted_scale"] - 1) < 0.05 and e["resid_rel_to_output"] < 1e-2 for e in errs.values()), errs
    # (c) no-op reproduction vs exp8 G0 on the overlapping ids (first 60 chars), and (e) timing
    g0 = jload(C.E8 / "results/gams3/gens/G0.json")
    ref = {(r["uid"], r["lang"]): r["response"] for r in g0 if r["kind"] == "jbb_harmful"}
    t0 = time.time()
    its = S["B_harm"][:16]
    seqs = [lm.encode_chat(it[g])[0] for it in its for g in LANGS]
    outs = lm.generate(seqs, TOK_SCREEN, batch=GEN_BS)
    dt = time.time() - t0
    txt = [decode(lm, o) for o in outs]
    keys = [(it["uid"], g) for it in its for g in LANGS]
    match = [txt[i][:60] == ref[k][:60] for i, k in enumerate(keys) if k in ref]
    out["noop_repro_first60"] = {"n": len(match), "rate": float(np.mean(match))}
    out["sec_per_gen_128"] = dt / len(seqs)
    logger.info(f"smoke: template OK; adapter-delta relerr {errs}; no-op reproduction {np.mean(match):.2f} "
                f"(n={len(match)}); {dt/len(seqs):.2f}s/gen @128 (batch {len(seqs)})")
    jdump(out, p)
    return out


def capture_halfA(lm: LM, S: dict) -> tuple[np.ndarray, list[dict]]:
    items = [(it, g) for name in ("A_harm", "A_jbbben", "A_dolly") for it in S[name] for g in LANGS]
    seqs = [lm.encode_chat(it[g])[0] for it, g in items]
    acts = lm.capture(seqs, [[len(s) - 1] for s in seqs], [[len(s) - 1] for s in seqs])[:, :, 0]  # [N, H, D]
    meta = [{"uid": it["uid"], "lang": g, "kind": it["kind"], "role": it["role"]} for it, g in items]
    return acts, meta


def direction_sanity(acts: np.ndarray, meta: list[dict], dEN_stored: np.ndarray) -> dict:
    W = np.stack([winsorize(acts[i]) for i in range(acts.shape[0])])
    lang = np.array([m["lang"] for m in meta])
    kind = np.array([m["kind"] for m in meta])
    dEN = W[(kind == "jbb_harmful") & (lang == "en")].mean(0) - W[(kind == "jbb_benign") & (lang == "en")].mean(0)
    cs = [cos(dEN[h], dEN_stored[h]) for h in range(dEN.shape[0])]
    return {"cos_per_h": cs, "min_cos_h>=1": float(min(cs[1:])), "passed": bool(min(cs[1:]) >= 0.99)}


def massive_dim(acts: np.ndarray) -> int:
    return int(np.argmax(np.abs(acts[:, 24]).mean(0)))


def layerwise_random(dEN_all, acts, hs, mdim: int, seed: int = 99) -> tuple[dict, list]:
    """exp8 method.py layerwise_random, ported: per hidden index a random direction in the half-A residual PC span,
    energy-matched (+-25%) to d_EN(h) on the raw residuals, orthogonal to d_EN(h) and to the massive dimension."""
    rng = np.random.default_rng(seed)
    out, diag = {}, []
    for h in hs:
        Xraw = acts[:, h].astype(np.float64)
        Xw = winsorize(Xraw).astype(np.float64)
        _, sv, Vt = np.linalg.svd(Xw - Xw.mean(0), full_matrices=False)
        V, sv = Vt[:60], sv[:60]
        dh = unit(dEN_all[h]).astype(np.float64)
        e_d = float(np.mean((Xraw @ dh) ** 2))
        best = None
        for k in range(120):
            u = (rng.normal(size=len(sv)) * (sv ** (0.0 if k % 2 else -0.5))) @ V
            u[mdim] = 0.0
            u = unit(u - (u @ dh) * dh).astype(np.float64)
            e_u = float(np.mean((Xraw @ u) ** 2))
            if best is None or abs(e_u / e_d - 1) < best[0]:
                best = (abs(e_u / e_d - 1), u, e_u)
            if best[0] <= 0.25:
                break
        out[h] = best[1]
        diag.append({"h": int(h), "energy_dEN": e_d, "energy_rand": best[2], "ratio": best[2] / e_d, "matched": bool(best[0] <= 0.25)})
    return out, diag


def layerwise_pc(dEN_all, acts, hs, mdim: int) -> tuple[dict, list]:
    """exp8 method.py layerwise_pc, ported: per hidden index the half-A residual principal component whose raw projection
    energy best matches d_EN(h) (after removing d_EN(h) and the massive dimension)."""
    out, diag = {}, []
    for h in hs:
        Xraw = acts[:, h].astype(np.float64)
        Xw = winsorize(Xraw).astype(np.float64)
        _, _, Vt = np.linalg.svd(Xw - Xw.mean(0), full_matrices=False)
        dh = unit(dEN_all[h]).astype(np.float64)
        e_d = float(np.mean((Xraw @ dh) ** 2))
        best = None
        for k in range(min(40, Vt.shape[0])):
            u = Vt[k].astype(np.float64).copy()
            u[mdim] = 0.0
            u = unit(u - (u @ dh) * dh).astype(np.float64)
            e_u = float(np.mean((Xraw @ u) ** 2))
            if best is None or abs(e_u / e_d - 1) < best[0]:
                best = (abs(e_u / e_d - 1), u, e_u, k)
        out[h] = best[1]
        diag.append({"h": int(h), "pc": best[3], "energy_dEN": e_d, "energy_pc": best[2], "ratio": best[2] / e_d,
                     "matched": bool(best[0] <= 0.25)})
    return out, diag


def coverage_family(H: int) -> dict:
    fam = {f"P{k}": list(range(1, k + 1)) for k in range(4, 49, 4)}
    fam |= {f"S{k}": list(range(H - k, H)) for k in (12, 24, 36)}
    ALL = list(range(1, H))
    for a, b in ((1, 12), (13, 24), (25, 36), (37, 48)):
        fam[f"LOBO_{a}_{b}"] = [h for h in ALL if not (a <= h <= b)]
    return fam


def stage_A(args) -> None:
    S = C.build_sets(C.load_items())
    if args.mini:
        S = {k: v[:6] for k, v in S.items()}
    lm, ed = load()
    R = Runner(lm, ed, S)
    sm = smoke(lm, ed, S, R)
    Z = np.load(C.E8 / "directions/gams3_all_layers.npz")
    dEN_all = Z["dEN"].astype(np.float32)
    H = dEN_all.shape[0]
    ALL = list(range(1, H))
    # ---------------------------------------------------------------- half-A capture, direction sanity, controls
    pctl = C.RES / "controls"
    pctl.mkdir(exist_ok=True)
    if not (pctl / "layerwise_pc.npy").exists():
        t0 = time.time()
        acts, meta = capture_halfA(lm, C.build_sets(C.load_items()))  # always full half A (mini only trims outcomes)
        san = direction_sanity(acts, meta, dEN_all)
        md = massive_dim(acts)
        jdump(san | {"massive_dim": md, "n_items": len(meta)}, C.RES / "direction_sanity.json")
        logger.info(f"d_EN sanity: min cos (h>=1) {san['min_cos_h>=1']:.4f}; massive dim {md}")
        if not san["passed"]:
            raise RuntimeError("GATE: recomputed d_EN(h) disagrees with the stored frozen vectors (cos < .99) - STOP")
        rnd, drnd = layerwise_random(dEN_all, acts, ALL, md)
        pcs, dpc = layerwise_pc(dEN_all, acts, ALL, md)
        np.save(pctl / "layerwise_random.npy", np.stack([np.zeros(dEN_all.shape[1])] + [rnd[h] for h in ALL]).astype(np.float32))
        np.save(pctl / "layerwise_pc.npy", np.stack([np.zeros(dEN_all.shape[1])] + [pcs[h] for h in ALL]).astype(np.float32))
        jdump({"random": drnd, "pc": dpc, "n_random_matched": sum(d["matched"] for d in drnd),
               "n_pc_matched": sum(d["matched"] for d in dpc)}, pctl / "match.json")
        logger.info(f"controls: random matched {sum(d['matched'] for d in drnd)}/48, PC matched {sum(d['matched'] for d in dpc)}/48")
        del acts
        gc.collect()
        R.tick("halfA_capture_controls", t0)
    rnd_all = np.load(pctl / "layerwise_random.npy")
    pc_all = np.load(pctl / "layerwise_pc.npy")
    # ---------------------------------------------------------------- GATE 3 / 4, energy table, matched-energy design
    design_stage(lm, ed, R, dEN_all, rnd_all, pc_all)
    # ---------------------------------------------------------------- PART A: DEV redundancy index arms
    jdump({"DEV_H": [it["uid"] for it in S["DEV_H"]], "DEV_B": [it["uid"] for it in S["DEV_B"]],
           "flores": [it["uid"] for it in S["A_flores"][:40]], "seed": C.SEED}, C.CFG / "dev_items.json")
    S["A_flores40"] = S["A_flores"][:40]
    fam = coverage_family(H)
    arms = [("A0", None)] + [(k, v) for k, v in fam.items()] + [("X3_rand_all", "rnd"), ("X5_pc_all", "pc")]
    with_ben = {"A0", "P12", "P24", "P48", "LOBO_25_36", "X3_rand_all", "X5_pc_all"}
    t0 = time.time()
    for name, lay in arms:
        cell = f"dev_{name}"
        ta = time.time()
        ed.reset()
        if lay is None:
            lm.reset()
        elif lay == "rnd":
            lm.set_ablate_layerwise({h: rnd_all[h] for h in ALL}, 1.0)
        elif lay == "pc":
            lm.set_ablate_layerwise({h: pc_all[h] for h in ALL}, 1.0)
        else:
            lm.set_ablate_layerwise({h: unit(dEN_all[h]) for h in lay}, 1.0)
        plan = [("dev", "DEV_H", g, TOK_DEV) for g in LANGS]
        if name in with_ben:
            plan += [("dev_ben", "DEV_B", g, TOK_DEV) for g in LANGS]
        if name == "A0":  # the flores reference must be built by the unedited model first
            R.flores_base("A_flores40")
        R.gens(cell, plan)
        R.tf(cell, "A_flores40", full=False)
        jdump({"cell": cell, "part": "A", "kind": "activation_layerwise", "hidden_indices": lay if isinstance(lay, list) else
               (ALL if lay else []), "control": lay if isinstance(lay, str) else None, "c": 1.0}, C.CELLS / cell / "meta.json")
        lm.reset()
        R.tick(cell, ta)
    R.tick("partA_total", t0)
    lm.close()


# ============================================================================================ operator + energy
def journal_params(path: Path, trial: int) -> dict:
    tid, ua = -1, {}
    for line in path.read_text().splitlines():
        x = json.loads(line)
        if x["op_code"] == 4:
            tid += 1
        elif x["op_code"] == 8:
            ua.setdefault(x["trial_id"], {}).update(x["user_attr"])
    return ua[trial]


def coverage_sets(L: int = 48) -> dict:
    return {"B1": list(range(0, 12)), "B2": list(range(12, 24)), "B3": list(range(24, 36)), "B4": list(range(36, 48)),
            "C24": list(range(0, 24)), "C36": list(range(0, 36)), "STR2": list(range(0, L, 2)), "STR4": list(range(0, L, 4)),
            "ALL": list(range(0, L))}


def flat_weights(layers: list[int], c: float) -> dict:
    return {(l, comp): c for l in layers for comp in COMPONENTS}


def her88_weights(c: float, L: int = 48) -> tuple[dict, list]:
    p = journal_params(C.E1 / "checkpoints/gams/cjvt--GaMS3-12B-Instruct.jsonl", 88)["parameters"]
    k = kernel_weights(p, L)
    clips = []
    out = {}
    for key, w in k.items():
        ww = c * w
        if ww > C_BOUND:
            clips.append([key[0], key[1], ww])
            ww = C_BOUND
        out[key] = ww
    return out, clips


def swap_in_weights(L: int = 48) -> dict:
    """Gemma trial 96's triangular KERNEL (its own direction was global, index 26.07, a Gemma quantity); on GaMS3 the kernel
    is applied to the panel's frozen per-layer d_EN(h) family so SWAP_in differs from the panel only in its kernel."""
    ua = journal_params(C.E1 / "checkpoints/gemma/google--gemma-3-12b-it.jsonl", 96)
    return kernel_weights(ua["parameters"], L)


def energy_of(table: dict, weights: dict) -> float:
    """Total energy from the per-module table {(l, comp): e(w) on W_GRID} by linear interpolation."""
    return float(sum(np.interp(w, W_GRID, table[k]) for k, w in weights.items() if w != 0))


def build_table(ed: Editor, dirs: np.ndarray) -> dict:
    from heretic_op import delta_factors

    d = torch.as_tensor(np.asarray(dirs, np.float32)).cuda()
    tab = {}
    for key, m in ed.modules.items():
        W = ed.W(key)
        v = torch.nn.functional.normalize(d[key[0] + 1], p=2, dim=0)
        tab[key] = np.array([0.0] + [lora_energy(*delta_factors(W, v, float(w))) for w in W_GRID[1:]])
        del W
    torch.cuda.empty_cache()
    return tab


def prod_relerr(ref: tuple, other: tuple) -> float:
    """||B1A1 - B2A2||_F / ||B1A1||_F via r x r Gram algebra (never materialises the dense d_out x d_in products)."""
    (A1, B1), (A2, B2) = ref, other
    A1, B1, A2, B2 = A1.double(), B1.double(), A2.double(), B2.double()
    n11 = torch.trace((B1.T @ B1) @ (A1 @ A1.T))
    n22 = torch.trace((B2.T @ B2) @ (A2 @ A2.T))
    n12 = torch.trace((B1.T @ B2) @ (A2 @ A1.T))
    return float(torch.sqrt((n11 + n22 - 2 * n12).clamp_min(0)) / torch.sqrt(n11))


def design_stage(lm: LM, ed: Editor, R: Runner, dEN_all, rnd_all, pc_all) -> None:
    pdz = C.CFG / "design.json"
    if pdz.exists():
        return
    t0 = time.time()
    gates: dict = {}
    # GATE 3a: Heretic's own abliterate() source vs abliterate_custom (Editor.apply) - trial-88 kernel, per-layer d_EN
    fn, src_sha = heretic_abliterate_fn()
    from heretic_op import AbliterationParameters

    p88 = journal_params(C.E1 / "checkpoints/gams/cjvt--GaMS3-12B-Instruct.jsonl", 88)
    shim = HereticShim(ed)
    ed.reset()
    fn(shim, torch.nn.functional.normalize(torch.as_tensor(dEN_all).cuda(), p=2, dim=1), None, {c: AbliterationParameters(**v) for c, v in p88["parameters"].items()})
    fh = {k: (A.clone(), B.clone()) for k, (A, B) in ed.factors().items() if float(B.abs().sum()) > 0}
    ed.apply(dEN_all, kernel_weights(p88["parameters"], ed.L))
    fc = {k: (A.clone(), B.clone()) for k, (A, B) in ed.factors().items() if float(B.abs().sum()) > 0}
    assert set(fh) == set(fc), (len(fh), len(fc))
    rel = max(prod_relerr(fh[k], fc[k]) for k in fh)
    gates["G3_operator_equivalence"] = {"heretic_source_sha256": src_sha, "n_modules": len(fh), "max_rel_err_BA": rel,
                                        "passed": rel <= 1e-5}
    logger.info(f"GATE 3a operator equivalence: {len(fh)} modules, max rel err {rel:.2e}")
    del fh, fc
    # GATE 3b: rebuild the iteration-1 trial-88 adapter from Heretic's own GaMS3 directions (global index 22.30)
    try:
        rd = torch.load(C.E1 / "directions/gams/directions.pt", map_location="cuda").float()
        wgt, idx = math.modf(p88["direction_index"] + 1)
        v = torch.nn.functional.normalize(rd[int(idx)].lerp(rd[int(idx) + 1], wgt), p=2, dim=0)
        ed.apply(v.cpu().numpy(), kernel_weights(p88["parameters"], ed.L), per_layer=False)
        mine = {k: (A.clone(), B.clone()) for k, (A, B) in ed.factors().items() if float(B.abs().sum()) > 0}
        n = ed.load_adapter(C.E1 / "adapters/gams_selected_path2/adapter_model.safetensors")
        theirs = {k: (A.clone(), B.clone()) for k, (A, B) in ed.factors().items() if float(B.abs().sum()) > 0}
        common_k = set(mine) & set(theirs)
        errs = [prod_relerr(theirs[k], mine[k]) for k in common_k]
        gates["G3_trial88_rebuild"] = {"n_adapter_tensors": n, "n_modules_mine": len(mine), "n_modules_adapter": len(theirs),
                                       "median_rel_err_BA": float(np.median(errs)), "max_rel_err_BA": float(np.max(errs)),
                                       "energy_mine": float(sum(lora_energy(*x) for x in mine.values())),
                                       "energy_adapter": float(sum(lora_energy(*x) for x in theirs.values()))}
        logger.info(f"GATE 3b trial-88 rebuild vs adapter: {gates['G3_trial88_rebuild']}")
        del mine, theirs
    except (FileNotFoundError, RuntimeError, AssertionError) as e:
        logger.error(f"trial-88 rebuild check failed: {e!r}")
        gates["G3_trial88_rebuild"] = {"error": repr(e)}
    ed.reset()
    # GATE 4: energy identity, monotonicity, ALL > B2
    ed.apply(dEN_all, flat_weights([10, 30], 1.0))
    g4 = []
    for k in [(10, "attn.o_proj"), (30, "mlp.down_proj")]:
        A, B = ed.factors()[k]
        g4.append(abs(lora_energy(A, B) - float((B @ A).pow(2).sum())) / float((B @ A).pow(2).sum()))
    ed.reset()
    tabs = {}
    for fam_name, dirs in (("dEN", dEN_all), ("rnd", rnd_all), ("pc", pc_all)):
        ta = time.time()
        tabs[fam_name] = build_table(ed, dirs)
        logger.info(f"energy table {fam_name}: {time.time()-ta:.0f}s")
    np.savez(C.RES / "energy_table.npz", w_grid=W_GRID,
             **{f"{f}|{l}|{c}": v for f, t in tabs.items() for (l, c), v in t.items()})
    cs = coverage_sets(ed.L)
    mono = {}
    for sname in ("B2", "ALL"):
        e = [energy_of(tabs["dEN"], flat_weights(cs[sname], c)) for c in (0.25, 0.5, 0.75, 1.0, 1.5)]
        mono[sname] = {"E": e, "monotone": bool(np.all(np.diff(e) > 0))}
    gates["G4_energy"] = {"trace_vs_dense_relerr": g4, "monotone": mono,
                          "ALL_gt_B2": bool(energy_of(tabs["dEN"], flat_weights(cs["ALL"], 1.0)) >
                                            energy_of(tabs["dEN"], flat_weights(cs["B2"], 1.0)))}
    assert max(g4) < 1e-4 and all(m["monotone"] for m in mono.values()), gates["G4_energy"]
    # ---------------------------------------------------------------- design: matched-energy groups by bisection
    def solve_c(fam: str, layers: list[int], target: float, hi: float) -> tuple[float, float]:
        lo_c, hi_c = 0.0, hi
        if energy_of(tabs[fam], flat_weights(layers, hi_c)) < target:
            return hi_c, energy_of(tabs[fam], flat_weights(layers, hi_c))
        for _ in range(40):
            mid = (lo_c + hi_c) / 2
            if energy_of(tabs[fam], flat_weights(layers, mid)) < target:
                lo_c = mid
            else:
                hi_c = mid
        c = (lo_c + hi_c) / 2
        return c, energy_of(tabs[fam], flat_weights(layers, c))

    narrow = ["B2", "B3"]
    e_hi = 0.9 * min(energy_of(tabs["dEN"], flat_weights(cs[s], C_BOUND)) for s in narrow)
    targets = {"E1": e_hi / 4, "E2": e_hi / 2, "E3": e_hi}
    groups = {}
    for gname, tgt in targets.items():
        mem = {}
        for s in ("B2", "B3", "STR4", "STR2", "ALL"):
            c, e = solve_c("dEN", cs[s], tgt, C_BOUND)
            mem[s] = {"family": "dEN", "layers": cs[s], "c": c, "E_table": e, "rel_dev": e / tgt - 1}
        for fam, lab in (("rnd", "RND_ALL"), ("pc", "PC_ALL")):
            c, e = solve_c(fam, cs["ALL"], tgt, C_BOUND_CTRL)
            mem[lab] = {"family": fam, "layers": cs["ALL"], "c": c, "E_table": e, "rel_dev": e / tgt - 1}
        groups[gname] = {"target_E": tgt, "members": mem,
                         "all_within_10pct": bool(all(abs(m["rel_dev"]) <= 0.10 for m in mem.values()))}
        logger.info(f"group {gname} E*={tgt:.1f}: " + ", ".join(f"{k} c={m['c']:.3f} dev={m['rel_dev']:+.2f}" for k, m in mem.items()))
    grid = {}
    for s, lay in cs.items():
        for c in (0.25, 0.5, 1.0, 1.5):
            grid[f"{s}_c{c}"] = {"family": "dEN", "layers": lay, "c": c, "E_table": energy_of(tabs["dEN"], flat_weights(lay, c))}
    her = {}
    for c in (0.25, 0.5, 1.0, 1.5):
        w, clips = her88_weights(c, ed.L)
        her[f"HER88_c{c}"] = {"family": "dEN", "kernel": "trial88", "c": c, "E_table": energy_of(tabs["dEN"], w),
                              "n_clipped": len(clips), "layers": sorted({l for l, _ in w})}
    sw = swap_in_weights(ed.L)
    design = {"declared_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "gates": gates, "targets": targets,
              "groups": groups, "grid": grid | her, "swap_in": {"E_table": energy_of(tabs["dEN"], sw),
                                                                "layers": sorted({l for l, _ in sw}), "kernel": "gemma trial 96"},
              "c_bound": C_BOUND, "c_bound_controls": C_BOUND_CTRL, "narrow_members": narrow,
              "broad_members": ["STR2", "ALL"], "count_matched_spread_member": "STR4",
              "layer_numbering": "Heretic layer l (0..47) edits o_proj/down_proj of decoder layer l with d_EN(hidden index l+1)"}
    jdump(design, pdz)
    R.tick("design_stage", t0)


# ============================================================================================ STAGE B
def weights_for(spec: dict, L: int = 48) -> dict:
    if spec.get("kernel") == "trial88":
        return her88_weights(spec["c"], L)[0]
    return flat_weights(spec["layers"], spec["c"])


def priority_list(design: dict) -> list[dict]:
    cells = [{"cell": "NOOP", "tier": "T1", "type": "noop", "confirm": True}]
    for g, grp in design["groups"].items():
        for m, spec in grp["members"].items():
            cells.append({"cell": f"{g}_{m}", "tier": "T1", "type": "weight", "spec": spec, "group": g, "member": m, "confirm": True})
    cells += [{"cell": "G1_single_site", "tier": "T2", "type": "activation_single", "confirm": True},
              {"cell": "CORE_trial88", "tier": "T2", "type": "adapter", "confirm": True},
              {"cell": "SWAP_in_trial96", "tier": "T2", "type": "swap_in", "confirm": True}]
    for c in (1.0, 0.5, 1.5, 0.25):   # T5 levels run only if the GPU deadline leaves room
        tier = {1.0: "T3", 0.5: "T4"}.get(c, "T5")
        for name, spec in design["grid"].items():
            if name.endswith(f"_c{c}"):
                cells.append({"cell": f"GRID_{name}", "tier": tier, "type": "weight", "spec": spec, "confirm": False})
    return cells


def stage_B(args) -> None:
    S = C.build_sets(C.load_items())
    if args.mini:
        S = {k: v[:6] for k, v in S.items()}
    design = jload(C.CFG / "design.json")
    cells = priority_list(design)
    jdump([{k: v for k, v in c.items() if k != "spec"} for c in cells], C.CFG / "priority.json")
    freeze_ok = (C.CFG / "FREEZE.sha256").exists() and all(
        f in (C.CFG / "FREEZE.sha256").read_text() for f in ("redundancy_index.json", "frozen_predictions.json"))
    if not freeze_ok:
        logger.warning("FREEZE not present: confirmation generations are DISABLED for this run")
    lm, ed = load()
    R = Runner(lm, ed, S)
    Z = np.load(C.E8 / "directions/gams3_all_layers.npz")
    dEN_all = Z["dEN"].astype(np.float32)
    fams = {"dEN": dEN_all, "rnd": np.load(C.RES / "controls/layerwise_random.npy"), "pc": np.load(C.RES / "controls/layerwise_pc.npy")}
    dEN_single = np.load(C.E8 / "directions/gams3_dEN.npy").astype(np.float32)
    ed.reset()
    lm.reset()
    R.flores_base("B_flores")
    R._dol = R.dolly_ref()
    R._mc = R.mc_prep()
    for spec in cells:
        cell = spec["cell"]
        if args.tiers and spec["tier"] not in args.tiers:
            continue
        if DEADLINE and time.time() > DEADLINE:
            logger.warning(f"deadline reached; stopping before {cell}")
            break
        ta = time.time()
        ed.reset()
        lm.reset()
        meta = {"cell": cell, "tier": spec["tier"], "type": spec["type"], "part": "B"}
        if spec["type"] == "weight":
            w = weights_for(spec["spec"], ed.L)
            en = ed.apply(fams[spec["spec"]["family"]], w)
            meta |= {"family": spec["spec"]["family"], "c": spec["spec"]["c"], "group": spec.get("group"), "member": spec.get("member"),
                     "kernel": spec["spec"].get("kernel", "flat"), "layers": sorted({l for l, _ in w}),
                     "weights": {f"{l}|{c}": v for (l, c), v in w.items()}, "E_table": spec["spec"]["E_table"]}
        elif spec["type"] == "adapter":
            n = ed.load_adapter(C.E1 / "adapters/gams_selected_path2/adapter_model.safetensors")
            meta |= {"adapter_tensors": n, "adapter_sha256": C.file_sha256(C.E1 / "adapters/gams_selected_path2/adapter_model.safetensors")}
        elif spec["type"] == "swap_in":
            w = swap_in_weights(ed.L)
            ed.apply(dEN_all, w)
            meta |= {"family": "dEN", "kernel": "gemma_trial96", "layers": sorted({l for l, _ in w}),
                     "weights": {f"{l}|{c}": v for (l, c), v in w.items()}}
        elif spec["type"] == "activation_single":
            lm.set_ablate(dEN_single, 1.0)
            meta |= {"h_star": C.H_STAR, "note": "exp8 G1: single-site d_EN ablated at every hidden index, all positions"}
        per_mod = {f"{l}|{c}": lora_energy(A, B) for (l, c), (A, B) in ed.factors().items()}
        meta["E_exact"] = float(sum(per_mod.values()))
        meta["E_per_layer"] = [sum(v for k, v in per_mod.items() if int(k.split("|")[0]) == l) for l in range(ed.L)]
        jdump(meta, C.CELLS / cell / "meta.json")
        plan = [("screen", "B_harm", g, TOK_SCREEN) for g in LANGS]
        if spec["confirm"] and freeze_ok:
            plan += [("confirm", "hoc_harm", g, TOK_CONF_H) for g in LANGS] + [("confirm_ben", "hoc_ben40", g, TOK_CONF_B) for g in LANGS]
        R.gens(cell, plan)
        R.tf(cell, "B_flores", full=spec["tier"] in ("T1", "T2"))  # KL + MC only where the utility gate is reported
        R.tick(cell, ta)
        logger.info(f"[{cell}] done in {time.time()-ta:.0f}s (E_exact {meta['E_exact']:.1f})")
    ed.reset()
    lm.close()


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["A", "B"], required=True)
    ap.add_argument("--mini", action="store_true")
    ap.add_argument("--tiers", nargs="*", default=None)
    args = ap.parse_args()
    if args.mini and not C.MINI:  # the mini tree is selected by AII_MINI so every script agrees on the paths
        raise SystemExit("run mini with AII_MINI=1 in the environment")
    setup_logging(f"method_{args.stage}{'_mini' if args.mini else ''}")
    torch.manual_seed(C.SEED)
    if args.stage == "A":
        stage_A(args)
    else:
        stage_B(args)


if __name__ == "__main__":
    main()
