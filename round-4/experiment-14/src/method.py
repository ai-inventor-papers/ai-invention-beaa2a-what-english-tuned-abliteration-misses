#!/usr/bin/env python3
"""WHERE A REFUSAL EDIT MUST LAND IN GaMS3 - iteration-4 slot-2 pod (boundary and confound).

The object: a per-language CAUSAL WRITE PROFILE e_L(h) measured in WEIGHT-EDIT space - the judged drop in harmful
refusal caused by applying Heretic's own abliteration operator at ONE decoder layer (both write components) with the
frozen English refusal direction d_EN(h), on DEV items only. From it, a frozen overlap statistic

    O_L(edit) = sum_h e_L(h) g(h) / ||g||_2 ,   g(h) = closed-form per-layer removal energy of the edit

and a sharp out-of-sample prediction (which matched-energy 12-layer region wins on held-out harm categories).

Stages (resumable; every cell writes results/cells/<cell>/{gens.json, tf.json, meta.json}):
  --stage smoke    Gate 0 pins + input inventory, Gate 1 operator unit tests (Heretic-source equivalence, energy
                   identity, c -> k^2 energy rescaling, trial-88 adapter rebuild), Gate 3 anchor reproduction against
                   the iteration-3 panel's stored generations, Gate 4 baseline sanity, the dEN energy table, the
                   half-A capture and the layer-matched RANDOM / energy-matched PC control direction families.
  --stage profile  Phase 1: DEV no-op + a c-selection pilot + 48 single-layer weight edits on DEV harmful (EN, SL).
  --stage confirm  Phase 4/5: refuses to start unless configs/FREEZE.sha256 matches configs/frozen_predictions.json;
                   runs the frozen confirmation cells, the energy- and collateral-matched controls, and the
                   dissociation ladder A3/A4 (A1/A2 are re-labelled from the iteration-3 panel, never regenerated).
Judging happens in a separate process (judge_local.py) so the judge and the model never co-reside on the GPU."""
from __future__ import annotations

import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")  # shared 48-core host: BLAS oversubscription made a 276x3840 SVD take 35 s

import argparse
import gc
import hashlib
import json
import math
import resource
import shutil
import time
from pathlib import Path

import numpy as np
import torch
from loguru import logger

import common as C
from common import LANGS, jdump, jload, rule_label, setup_logging
from heretic_op import COMPONENTS, Editor, HereticShim, delta_factors, heretic_abliterate_fn, kernel_weights, lora_energy
from interventions import LM, cos, unit, winsorize

GEN_BS = 64                                   # frozen bucket schedule: identical for every cell including the no-op
TOK_DEV, TOK_CONF_H, TOK_CONF_B = 128, 192, 128   # identical to the iteration-3 panel so the two panels pool
W_GRID = np.round(np.arange(0.0, 3.0001, 0.125), 4)
C_BOUND_REPORT = 1.5                          # Heretic's own max_weight bound: cells above it are flagged, not hidden
DEADLINE = float(os.environ.get("AII_DEADLINE", "0"))
RAM_BUDGET = 60 * 1024 ** 3                   # 503 GB host, 48 cores shared: fail fast instead of OOM-killing the box


def guard_resources() -> None:
    """CUDA reserves an enormous virtual address space, so RLIMIT_AS is only safe on the CPU-only paths; the GPU is
    capped with the allocator fraction instead (both raise a catchable error rather than OOM-killing the container)."""
    if torch.cuda.is_available():
        torch.cuda.set_per_process_memory_fraction(0.92)
    else:
        resource.setrlimit(resource.RLIMIT_AS, (RAM_BUDGET, RAM_BUDGET))


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


def gen_rec(cell: str, it: dict, lang: str, text: str, n: int, split: str) -> dict:
    return {"gid": hashlib.sha256(f"gams3|{cell}|{split}|{it['uid']}|{lang}".encode()).hexdigest()[:16], "model": "gams3",
            "cell": cell, "split": split, "uid": it["uid"], "semantic_id": it["semantic_id"], "kind": it["kind"],
            "role": it.get("role"), "source": it.get("source"), "lang": lang, "prompt": it[lang], "response": text,
            "n_tokens": n, "rule_label": rule_label(text)}


# ============================================================================================ cell runner
class Runner:
    """Generation + teacher-forced collateral for one edit state, with per-cell incremental files."""

    def __init__(self, lm: LM, ed: Editor, S: dict):
        self.lm, self.ed, self.S = lm, ed, S
        self.ref = C.RES / "ref"
        self.ref.mkdir(exist_ok=True)
        self.timings = jload(C.RES / "timings.json") if (C.RES / "timings.json").exists() else {}

    def tick(self, k: str, t0: float) -> None:
        self.timings[k] = round(time.time() - t0, 1)
        jdump(self.timings, C.RES / "timings.json")

    def gens(self, cell: str, plan: list[tuple[str, str, str, int]]) -> int:
        """plan = [(split_tag, set_name, lang, max_new)]; generates what is missing under the CURRENT edit state."""
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
            have += [gen_rec(cell, it, g, self.lm.tok.decode(o, skip_special_tokens=True), len(o), tag)
                     for (tag, it, g), o in zip(todo, outs)]
            jdump(have, p)
        n = len(have) - n0
        if n:
            dt = time.time() - t0
            rr = {g: round(float(np.mean([r["rule_label"] == "refused" for r in have if r["lang"] == g])), 2) for g in LANGS}
            logger.info(f"[{cell}] +{n} gens in {dt:.0f}s ({dt/n:.2f}s/gen); rule-refused {rr}")
        return n

    # ---------------------------------------------------------------- teacher-forced collateral
    def flores_base(self, name: str) -> dict:
        p = self.ref / f"flores_{name}_base.json"
        if not p.exists():
            assert self.lm.state.mode is None and self.ed.total_energy() == 0.0, "reference must come from the unedited model"
            jdump({g: self.lm.seq_nll([self.lm.encode_plain(it[g]) for it in self.S[name]], [1] * len(self.S[name])).tolist()
                   for g in LANGS}, p)
        return {g: np.array(v) for g, v in jload(p).items()}

    def dolly_ref(self):
        """Unedited 32-token harmless continuations + their top-512 reference distributions (for the harmless KL)."""
        p, pk = self.ref / "dolly_cont.json", self.ref / "dolly_ref.npz"
        dol = self.S["KL_dolly"]
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

    def tf(self, cell: str, flores_set: str, kl: bool) -> None:
        p = C.CELLS / cell / "tf.json"
        if p.exists():
            return
        t0 = time.time()
        out: dict = {"flores_set": flores_set}
        fb = self.flores_base(flores_set)
        its = self.S[flores_set]
        for g in LANGS:
            n = self.lm.seq_nll([self.lm.encode_plain(it[g]) for it in its], [1] * len(its))
            out[f"flores_{g}"] = {it["semantic_id"]: float(a - b) for it, a, b in zip(its, n, fb[g])}
        if kl:
            if not hasattr(self, "_dol"):
                self._dol = self.dolly_ref()
            for g in LANGS:
                seqs, starts, groups, ref = self._dol[g]
                k = np.zeros(len(seqs))
                for nn, ix in groups.items():
                    k[ix] = self.lm.kl_vs_ref([seqs[i] for i in ix], [starts[i] for i in ix], nn, [ref[i] for i in ix])
                out[f"kl_{g}"] = {it["semantic_id"]: float(v) for it, v in zip(self.S["KL_dolly"], k)}
        jdump(out, p)
        logger.info(f"[{cell}] TF in {time.time()-t0:.0f}s: FLORES dNLL EN {np.mean(list(out['flores_en'].values())):+.3f} "
                    f"SL {np.mean(list(out['flores_sl'].values())):+.3f}"
                    + (f"; KL SL {np.mean(list(out['kl_sl'].values())):.3f}" if kl else ""))


# ============================================================================================ item sets
def sets(mini: bool = False) -> dict:
    """DEV (S3 JBB half A, used for the profile only) and CONFIRM (S4 held-out-category pairs) item sets."""
    S = C.build_sets(C.load_items())
    D = C.load_items()
    out = {
        "DEV_H": S["DEV_H"],                       # 40 harmful DEV items (frozen in iteration 3, reused verbatim)
        "DEV_B": S["DEV_B"],                       # 40 harmless DEV twins
        "CONF_H": S["hoc_harm"],                   # 70 held-out-category StrongREJECT harmful pairs
        "CONF_B": S["hoc_ben40"],                  # 40 held-out-category harmless twins (over-refusal)
        "FLORES": S["A_flores"][:40],              # FLORES dev, half A (DEV collateral, 40 semantic items)
        "KL_dolly": [it for it in D["dolly"] if it["half"] == "B"][:60],
    }
    if mini:
        out = {k: v[:4] for k, v in out.items()}
    return out


# ============================================================================================ energy helpers
def flat_weights(layers: list[int], c: float) -> dict:
    return {(l, comp): float(c) for l in layers for comp in COMPONENTS}


def build_table(ed: Editor, dirs: np.ndarray, layers: list[int] | None = None) -> dict:
    """Per-module removal energy on W_GRID for a direction family (row h = hidden index h; layer l uses row l+1)."""
    d = torch.as_tensor(np.asarray(dirs, np.float32)).cuda()
    tab = {}
    keys = [k for k in ed.modules if layers is None or k[0] in layers]
    for key in keys:
        W = ed.W(key)
        v = torch.nn.functional.normalize(d[key[0] + 1], p=2, dim=0)
        tab[key] = np.array([0.0] + [lora_energy(*delta_factors(W, v, float(w))) for w in W_GRID[1:]])
        del W
    torch.cuda.empty_cache()
    return tab


def energy_of(table: dict, weights: dict) -> float:
    return float(sum(np.interp(w, W_GRID, table[k]) for k, w in weights.items() if w != 0))


def solve_c(table: dict, layers: list[int], target: float, hi: float = 3.0) -> tuple[float, float]:
    """Closed-form matched-energy solution: the weight c whose total removal energy equals `target`."""
    lo_c, hi_c = 0.0, hi
    if energy_of(table, flat_weights(layers, hi_c)) < target:
        return hi_c, energy_of(table, flat_weights(layers, hi_c))
    for _ in range(50):
        mid = (lo_c + hi_c) / 2
        if energy_of(table, flat_weights(layers, mid)) < target:
            lo_c = mid
        else:
            hi_c = mid
    c = (lo_c + hi_c) / 2
    return c, energy_of(table, flat_weights(layers, c))


def save_table(tabs: dict, path: Path) -> None:
    np.savez(path, w_grid=W_GRID, **{f"{f}|{l}|{c}": v for f, t in tabs.items() for (l, c), v in t.items()})


def load_table(path: Path, fam: str) -> dict:
    z = np.load(path)
    return {(int(k.split("|")[1]), k.split("|")[2]): z[k] for k in z.files if k.startswith(f"{fam}|")}


# ============================================================================================ control directions
def capture_halfA(lm: LM, S_full: dict) -> tuple[np.ndarray, list[dict]]:
    items = [(it, g) for name in ("A_harm", "A_jbbben", "A_dolly") for it in S_full[name] for g in LANGS]
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
    return {"cos_per_h": cs, "min_cos_h_ge_1": float(min(cs[1:])), "passed": bool(min(cs[1:]) >= 0.99)}


def layerwise_random(dEN_all, acts, hs, mdim: int, seed: int) -> tuple[np.ndarray, list]:
    """Per hidden index a random direction in the half-A residual PC span, energy-matched (+-25%) to d_EN(h) on the
    raw residuals, orthogonal to d_EN(h) and to the massive dimension (iteration-2 construction, ported verbatim)."""
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
        diag.append({"h": int(h), "energy_dEN": e_d, "energy_rand": best[2], "ratio": best[2] / e_d,
                     "matched": bool(best[0] <= 0.25)})
    M = np.zeros((acts.shape[1], acts.shape[2]), dtype=np.float32)
    for h in hs:
        M[h] = out[h]
    return M, diag


def layerwise_pc(dEN_all, acts, hs, mdim: int, rank: int) -> tuple[np.ndarray, list]:
    """Per hidden index the `rank`-th best energy-matching harmless-activation principal component (rank 0 = best)."""
    out, diag = {}, []
    for h in hs:
        Xraw = acts[:, h].astype(np.float64)
        Xw = winsorize(Xraw).astype(np.float64)
        _, _, Vt = np.linalg.svd(Xw - Xw.mean(0), full_matrices=False)
        dh = unit(dEN_all[h]).astype(np.float64)
        e_d = float(np.mean((Xraw @ dh) ** 2))
        cand = []
        for k in range(min(40, Vt.shape[0])):
            u = Vt[k].astype(np.float64).copy()
            u[mdim] = 0.0
            u = unit(u - (u @ dh) * dh).astype(np.float64)
            e_u = float(np.mean((Xraw @ u) ** 2))
            cand.append((abs(e_u / e_d - 1), u, e_u, k))
        cand.sort(key=lambda t: t[0])
        pick = cand[min(rank, len(cand) - 1)]
        out[h] = pick[1]
        diag.append({"h": int(h), "pc": pick[3], "energy_dEN": e_d, "energy_pc": pick[2], "ratio": pick[2] / e_d,
                     "matched": bool(pick[0] <= 0.25)})
    M = np.zeros((acts.shape[1], acts.shape[2]), dtype=np.float32)
    for h in hs:
        M[h] = out[h]
    return M, diag


# ============================================================================================ Heretic parameter rows
def journal_params(path: Path, trial: int) -> dict:
    tid, ua = -1, {}
    for line in path.read_text().splitlines():
        x = json.loads(line)
        if x["op_code"] == 4:
            tid += 1
        elif x["op_code"] == 8:
            ua.setdefault(x["trial_id"], {}).update(x["user_attr"])
    return ua[trial]


def her88_weights(c: float, L: int = 48) -> dict:
    """The shipped GaMS3 edit's own triangular kernel (Optuna trial 88), scaled by c. No clipping: the dose ladder
    needs the exact k^2 energy law, and any weight above Heretic's own 1.5 bound is flagged in the cell meta."""
    p = journal_params(C.E1 / "checkpoints/gams/cjvt--GaMS3-12B-Instruct.jsonl", 88)["parameters"]
    return {k: c * w for k, w in kernel_weights(p, L).items()}


def swap_weights(c: float = 1.0, L: int = 48) -> dict:
    """The sibling checkpoint's selected kernel (Gemma Optuna trial 96) applied to GaMS3's own d_EN(h) family."""
    ua = journal_params(C.E1 / "checkpoints/gemma/google--gemma-3-12b-it.jsonl", 96)
    return {k: c * w for k, w in kernel_weights(ua["parameters"], L).items()}


# ============================================================================================ STAGE smoke
def stage_smoke(args) -> None:
    import bitsandbytes, peft, transformers

    S = sets(args.mini)
    t_all = time.time()
    # ---------------------------------------------------------------- GATE 0: pins and inputs
    inputs = {
        "E1_adapter": C.E1 / "adapters/gams_selected_path2/adapter_model.safetensors",
        "E1_journal_gams": C.E1 / "checkpoints/gams/cjvt--GaMS3-12B-Instruct.jsonl",
        "E1_journal_gemma": C.E1 / "checkpoints/gemma/google--gemma-3-12b-it.jsonl",
        "E8_directions": C.E8 / "directions/gams3_all_layers.npz",
        "E8_dEN_single": C.E8 / "directions/gams3_dEN.npy",
        "E6_heretic_model_py": C.HERETIC_MODEL_PY,
        "E10_judge_cache": C.E10 / "results/judge_local.jsonl",
        "E10_cells": C.E10 / "results/cells",
        "E9_cells_csv": C.E9 / "results/cells.csv",
        "E9_energy_real": C.E9 / "results/energy_real.json",
        "E12_frozen": C.E12 / "configs/frozen_predictions.json",
        "dataset_manifest": C.MANIFEST,
    }
    inv = {}
    for k, p in inputs.items():
        p = Path(p)
        inv[k] = {"path": C.relpath(p), "exists": p.exists(),
                  "sha256": (C.file_sha256(p) if (p.exists() and p.is_file() and p.stat().st_size < 3e8) else None),
                  "recovery": RECOVERY.get(k, "")}
    jdump(inv, C.RES / "inputs_manifest.json")
    missing = [k for k, v in inv.items() if not v["exists"]]
    if missing:
        logger.error(f"MISSING INPUTS (recovery paths in results/inputs_manifest.json): {missing}")
    lm, ed = load()
    tokh = hashlib.sha256((lm.tok.chat_template or "").encode()).hexdigest()
    pins = {"model": C.MODEL, "tokenizer_chat_template_sha256": tokh, "torch": torch.__version__,
            "transformers": transformers.__version__, "peft": peft.__version__, "bitsandbytes": bitsandbytes.__version__,
            "gpu": torch.cuda.get_device_name(0), "cuda": torch.version.cuda, "seed": C.SEED,
            "heretic_op_sha256": C.file_sha256(Path(__file__).parent / "heretic_op.py"),
            "method_sha256": C.file_sha256(Path(__file__)), "gen_bs": GEN_BS,
            "tokens": {"dev": TOK_DEV, "confirm_harmful": TOK_CONF_H, "confirm_benign": TOK_CONF_B},
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    jdump(pins, C.RES / "gate0_pins.json")
    logger.info(f"GATE 0 pins written; chat-template sha {tokh[:12]}")

    Z = np.load(C.E8 / "directions/gams3_all_layers.npz")
    dEN_all = Z["dEN"].astype(np.float32)
    H = dEN_all.shape[0]                       # 49 rows: row h is hidden index h (layer l uses row l+1)
    ALL = list(range(1, H))
    R = Runner(lm, ed, S)

    # ---------------------------------------------------------------- GATE 1: operator unit tests
    g1p = C.RES / "gate1_unit_tests.json"
    if not g1p.exists():
        g1: dict = {}
        it = S["DEV_H"][0]
        re_, rs = lm.render(it["en"]), lm.render(it["sl"])
        g1["template"] = {"prefix_equal": re_.split(it["en"])[0] == rs.split(it["sl"])[0],
                          "suffix_equal": re_.split(it["en"])[1] == rs.split(it["sl"])[1], "rendered_en": re_}
        assert g1["template"]["prefix_equal"] and g1["template"]["suffix_equal"], "chat template differs by language"
        # (a) adapter-disabled == no-op: the identity adapter must leave logits bitwise unchanged
        ed.reset()
        seqs = [lm.encode_chat(S["DEV_H"][i]["en"])[0] for i in range(min(4, len(S["DEV_H"])))]
        base_lp = lm.seq_nll(seqs, [1] * len(seqs))
        ed.apply(dEN_all, flat_weights([20], 1.0))
        ed.reset()
        after_lp = lm.seq_nll(seqs, [1] * len(seqs))
        g1["adapter_disabled_equals_noop"] = {"max_abs_diff": float(np.max(np.abs(base_lp - after_lp))),
                                              "passed": bool(np.max(np.abs(base_lp - after_lp)) == 0.0)}
        # (b) Heretic's OWN abliterate() source vs our generalised operator, trial-88 kernel, per-layer d_EN
        fn, src_sha = heretic_abliterate_fn()
        from heretic_op import AbliterationParameters
        p88 = journal_params(C.E1 / "checkpoints/gams/cjvt--GaMS3-12B-Instruct.jsonl", 88)
        ed.reset()
        fn(HereticShim(ed), torch.nn.functional.normalize(torch.as_tensor(dEN_all).cuda(), p=2, dim=1), None,
           {c: AbliterationParameters(**v) for c, v in p88["parameters"].items()})
        fh = {k: (A.clone(), B.clone()) for k, (A, B) in ed.factors().items() if float(B.abs().sum()) > 0}
        ed.apply(dEN_all, kernel_weights(p88["parameters"], ed.L))
        fc = {k: (A.clone(), B.clone()) for k, (A, B) in ed.factors().items() if float(B.abs().sum()) > 0}
        rel = max(prod_relerr(fh[k], fc[k]) for k in fh)
        g1["operator_equivalence"] = {"heretic_source_sha256": src_sha, "n_modules": len(fh), "max_rel_err": rel,
                                      "passed": bool(rel <= 1e-5)}
        del fh, fc
        # (c) energy identity: the r x r trace form equals the dense ||BA||_F^2
        ed.apply(dEN_all, flat_weights([10, 30], 1.0))
        ids = []
        for k in [(10, "attn.o_proj"), (30, "mlp.down_proj")]:
            A, B = ed.factors()[k]
            ids.append(abs(lora_energy(A, B) - float((B @ A).pow(2).sum())) / float((B @ A).pow(2).sum()))
        g1["energy_identity"] = {"rel_err": ids, "passed": bool(max(ids) < 1e-4)}
        # (d) rescaling law: scaling every weight by k scales the total removal energy by k^2
        resc = []
        for k in (0.5, 0.75, 1.25):
            ed.apply(dEN_all, flat_weights([24, 25, 26], 1.0))
            e1 = ed.total_energy()
            ed.apply(dEN_all, flat_weights([24, 25, 26], k))
            resc.append({"k": k, "ratio": ed.total_energy() / e1, "k2": k * k})
        g1["energy_rescaling"] = {"rows": resc, "max_rel_dev": max(abs(r["ratio"] / r["k2"] - 1) for r in resc)}
        # (e) the shipped trial-88 adapter rebuilt from its journal row
        try:
            rd = torch.load(C.E1 / "directions/gams/directions.pt", map_location="cuda").float()
            wgt, idx = math.modf(p88["direction_index"] + 1)
            v = torch.nn.functional.normalize(rd[int(idx)].lerp(rd[int(idx) + 1], wgt), p=2, dim=0)
            ed.apply(v.cpu().numpy(), kernel_weights(p88["parameters"], ed.L), per_layer=False)
            mine = {k: (A.clone(), B.clone()) for k, (A, B) in ed.factors().items() if float(B.abs().sum()) > 0}
            n = ed.load_adapter(C.E1 / "adapters/gams_selected_path2/adapter_model.safetensors")
            theirs = {k: (A.clone(), B.clone()) for k, (A, B) in ed.factors().items() if float(B.abs().sum()) > 0}
            errs = [prod_relerr(theirs[k], mine[k]) for k in set(mine) & set(theirs)]
            g1["trial88_rebuild"] = {"n_tensors": n, "median_rel_err": float(np.median(errs)),
                                     "max_rel_err": float(np.max(errs)),
                                     "energy_rebuild": float(sum(lora_energy(*x) for x in mine.values())),
                                     "energy_adapter": float(sum(lora_energy(*x) for x in theirs.values()))}
            del mine, theirs
        except (FileNotFoundError, RuntimeError, AssertionError, KeyError) as e:
            logger.error(f"trial-88 rebuild failed: {e!r}")
            g1["trial88_rebuild"] = {"error": repr(e)}
        ed.reset()
        jdump(g1, g1p)
        logger.info(f"GATE 1: operator equivalence {g1['operator_equivalence']['max_rel_err']:.2e}; "
                    f"energy identity {max(g1['energy_identity']['rel_err']):.2e}; "
                    f"k^2 rescaling dev {g1['energy_rescaling']['max_rel_dev']:.2e}; "
                    f"adapter-disabled == no-op {g1['adapter_disabled_equals_noop']['passed']}")
        if not (g1["operator_equivalence"]["passed"] and g1["energy_identity"]["passed"]):
            raise RuntimeError("GATE 1 FAILED - the operator is wrong; every downstream number would be invalid")

    # ---------------------------------------------------------------- GATE 3: anchor reproduction
    g3p = C.RES / "gate3_anchor.json"
    if not g3p.exists():
        anchors = {}
        ref_cells = {"NOOP": None, "GRID_B3_c1.0": list(range(24, 36))}
        for cell, layers in ref_cells.items():
            src = C.E10 / f"results/cells/{cell}/gens.json"
            if not src.exists():
                continue
            ref = {(r["uid"], r["lang"]): r["response"] for r in jload(src) if r["split"] == "screen"}
            ed.reset()
            if layers is not None:
                ed.apply(dEN_all, flat_weights(layers, 1.0))
            its = C.build_sets(C.load_items())["B_harm"][:12]
            sq = [lm.encode_chat(it[g])[0] for it in its for g in LANGS]
            outs = lm.generate(sq, 128, batch=GEN_BS)
            keys = [(it["uid"], g) for it in its for g in LANGS]
            txt = [lm.tok.decode(o, skip_special_tokens=True) for o in outs]
            m = [txt[i][:60] == ref[k][:60] for i, k in enumerate(keys) if k in ref]
            anchors[cell] = {"n": len(m), "first60_match_rate": float(np.mean(m)) if m else None}
            logger.info(f"GATE 3 anchor {cell}: first-60-char reproduction {anchors[cell]}")
        ed.reset()
        jdump(anchors, g3p)

    # ---------------------------------------------------------------- half-A capture, direction sanity, controls
    ctl = C.RES / "controls"
    ctl.mkdir(exist_ok=True)
    if not (ctl / "pc_r0.npy").exists():
        t0 = time.time()
        acts, meta = capture_halfA(lm, C.build_sets(C.load_items()))
        san = direction_sanity(acts, meta, dEN_all)
        mdim = int(np.argmax(np.abs(acts[:, 24]).mean(0)))
        jdump(san | {"massive_dim": mdim, "n_items": len(meta)}, C.RES / "direction_sanity.json")
        logger.info(f"d_EN sanity: min cos (h>=1) {san['min_cos_h_ge_1']:.4f}; massive dim {mdim}")
        if not san["passed"]:
            raise RuntimeError("GATE: recomputed d_EN(h) disagrees with the stored frozen vectors (cos < .99)")
        diag = {}
        for d in range(3):
            M, dg = layerwise_random(dEN_all, acts, ALL, mdim, seed=99 + d)
            np.save(ctl / f"rnd_d{d}.npy", M)
            diag[f"rnd_d{d}"] = dg
        for r in range(3):
            M, dg = layerwise_pc(dEN_all, acts, ALL, mdim, rank=r)
            np.save(ctl / f"pc_r{r}.npy", M)
            diag[f"pc_r{r}"] = dg
        jdump({k: {"n_matched": sum(x["matched"] for x in v), "rows": v} for k, v in diag.items()}, ctl / "match.json")
        logger.info("controls: " + ", ".join(f"{k} {sum(x['matched'] for x in v)}/{len(v)} energy-matched"
                                             for k, v in diag.items()))
        del acts
        gc.collect()
        R.tick("halfA_capture_controls", t0)

    # ---------------------------------------------------------------- dEN energy table (needed by the freeze)
    tp = C.RES / "energy_table.npz"
    if not tp.exists():
        t0 = time.time()
        save_table({"dEN": build_table(ed, dEN_all)}, tp)
        R.tick("energy_table_dEN", t0)
        logger.info(f"dEN energy table built in {time.time()-t0:.0f}s")

    # ---------------------------------------------------------------- GATE 4: baseline sanity + timing model
    t0 = time.time()
    ed.reset()
    lm.reset()
    R.flores_base("FLORES")
    R.gens("dev_NOOP", [("dev", "DEV_H", g, TOK_DEV) for g in LANGS] + [("dev_ben", "DEV_B", g, TOK_DEV) for g in LANGS])
    jdump({"cell": "dev_NOOP", "stage": "profile", "type": "noop", "layers": [], "c": 0.0, "E_exact": 0.0,
           "E_per_layer": [0.0] * ed.L}, C.CELLS / "dev_NOOP" / "meta.json")
    R.tf("dev_NOOP", "FLORES", kl=False)
    R.tick("dev_NOOP", t0)
    # one single-layer profile cell end-to-end, for the extrapolation the scale-up rule demands
    t0 = time.time()
    ed.reset()
    ed.apply(dEN_all, flat_weights([33], 1.0))
    R.gens("dev_L34_c1.0", [("dev", "DEV_H", g, TOK_DEV) for g in LANGS])
    per_mod = {f"{l}|{c}": lora_energy(A, B) for (l, c), (A, B) in ed.factors().items()}
    jdump({"cell": "dev_L34_c1.0", "stage": "profile", "type": "single_layer", "h": 34, "layers": [33], "c": 1.0,
           "E_exact": float(sum(per_mod.values())),
           "E_per_layer": [sum(v for k, v in per_mod.items() if int(k.split("|")[0]) == l) for l in range(ed.L)]},
          C.CELLS / "dev_L34_c1.0" / "meta.json")
    dt = time.time() - t0
    R.tick("dev_L34_c1.0", t0)
    R.timings["profile_cell_seconds"] = round(dt, 1)
    R.timings["profile_48_extrapolated_min"] = round(dt * 48 / 60, 1)
    jdump(R.timings, C.RES / "timings.json")
    logger.info(f"TIMING MODEL: one profile cell {dt:.0f}s -> 48 layers ~= {dt*48/60:.0f} min of generation")
    ed.reset()
    lm.close()
    logger.info(f"stage smoke finished in {(time.time()-t_all)/60:.1f} min")


RECOVERY = {
    "E1_adapter": "rebuild from the trial-88 journal row through heretic_op.kernel_weights + Editor.apply",
    "E8_directions": "recompute difference-in-means d_EN(h) on S3 JBB half A under the same position convention",
    "E6_heretic_model_py": "re-clone Heretic at SHA 3521f864 and re-run the operator-equivalence unit test",
    "E10_judge_cache": "re-judge the reused anchor generations with judge_local.py (GPU cost, no information loss)",
    "E10_cells": "the screen shrinks to the cells that are recoverable; declared in results/deviations.json",
    "E9_cells_csv": "the cross-checkpoint mis-specification screen is dropped and declared",
}


def prod_relerr(ref: tuple, other: tuple) -> float:
    """||B1A1 - B2A2||_F / ||B1A1||_F via r x r Gram algebra (never materialises the dense product)."""
    (A1, B1), (A2, B2) = ref, other
    A1, B1, A2, B2 = A1.double(), B1.double(), A2.double(), B2.double()
    n11 = torch.trace((B1.T @ B1) @ (A1 @ A1.T))
    n22 = torch.trace((B2.T @ B2) @ (A2 @ A2.T))
    n12 = torch.trace((B1.T @ B2) @ (A2 @ A1.T))
    return float(torch.sqrt((n11 + n22 - 2 * n12).clamp_min(0)) / torch.sqrt(n11))


# ============================================================================================ STAGE profile
def stage_profile(args) -> None:
    S = sets(args.mini)
    lm, ed = load()
    R = Runner(lm, ed, S)
    dEN_all = np.load(C.E8 / "directions/gams3_all_layers.npz")["dEN"].astype(np.float32)
    ALL = list(range(1, dEN_all.shape[0]))
    ed.reset()
    lm.reset()
    R.flores_base("FLORES")
    R.gens("dev_NOOP", [("dev", "DEV_H", g, TOK_DEV) for g in LANGS] + [("dev_ben", "DEV_B", g, TOK_DEV) for g in LANGS])

    # ---- c selection on DEV, decided BEFORE the freeze with the cheap opener rule (never a reported outcome)
    cp = C.CFG / "profile_c.json"
    if cp.exists():
        sel = jload(cp)
    else:
        noop = jload(C.CELLS / "dev_NOOP" / "gens.json")
        base = {g: float(np.mean([r["rule_label"] == "refused" for r in noop if r["lang"] == g and r["split"] == "dev"]))
                for g in LANGS}
        pilot, rows, sel = [4, 16, 28, 40], [], None
        # DECLARED PRE-FREEZE SEARCH (DEV items, cheap opener-rule instrument, never a reported outcome):
        # the smallest single-layer strength whose pilot max refusal drop reaches 0.15 with degenerate output <= 0.10;
        # if no strength in the grid qualifies, a 3-layer sliding window at the largest strength is used instead
        # (fallback_plan: "pick the smallest c at which the profile has non-degenerate variance").
        for width, c in [(1, 1.0), (1, 1.5), (1, 2.5), (1, 3.5), (3, 2.5)]:
            drops, degen = [], []
            for h in pilot:
                lay = [x - 1 for x in range(h - width // 2, h + width // 2 + 1) if 1 <= x <= 48]
                cell = f"dev_L{h:02d}_c{c}" if width == 1 else f"dev_W{width}L{h:02d}_c{c}"
                ed.reset()
                ed.apply(dEN_all, flat_weights(lay, c))
                R.gens(cell, [("dev", "DEV_H", g, TOK_DEV) for g in LANGS])
                recs = jload(C.CELLS / cell / "gens.json")
                drops.append({g: base[g] - float(np.mean([r["rule_label"] == "refused" for r in recs if r["lang"] == g]))
                              for g in LANGS})
                degen.append(float(np.mean([r["rule_label"] in ("empty", "malformed") for r in recs])))
            spread = max(max(d[g] for g in LANGS) for d in drops)
            rows.append({"c": c, "width": width, "pilot_h": pilot, "drops": drops, "max_drop": spread,
                         "degenerate": float(np.mean(degen))})
            logger.info(f"c-pilot width={width} c={c}: max rule-based refusal drop {spread:+.2f}, "
                        f"degenerate {np.mean(degen):.2f}")
            if spread >= 0.15 and np.mean(degen) <= 0.10:
                sel = {"c_star": c, "width": width}
                break
        if sel is None:
            ok = [r for r in rows if r["degenerate"] <= 0.10]
            best = max(ok or rows, key=lambda r: r["max_drop"])
            sel = {"c_star": best["c"], "width": best["width"], "grid_exhausted": True}
            logger.warning(f"no strength reached the 0.15 pilot threshold; using the largest usable one: {sel}")
        sel |= {"rule": "smallest single-layer strength with pilot max rule-based drop >= 0.15 and degenerate <= 0.10; "
                        "otherwise the largest usable grid point (3-layer window allowed); DEV only, pre-freeze",
                "rows": rows, "noop_rule_refusal": base}
        jdump(sel, cp)
    c_star, width = sel["c_star"], sel.get("width", 1)
    logger.info(f"profile strength c* = {c_star}, window width = {width}")

    # ---- the 48 single-layer conditions
    t0 = time.time()
    for h in ALL:
        if DEADLINE and time.time() > DEADLINE:
            logger.warning(f"deadline reached; stopping the profile before h={h}")
            break
        lay = [x - 1 for x in range(h - width // 2, h + width // 2 + 1) if 1 <= x <= 48]
        cell = (f"dev_L{h:02d}_c{c_star}" if width == 1 else f"dev_W{width}L{h:02d}_c{c_star}")
        ta = time.time()
        ed.reset()
        ed.apply(dEN_all, flat_weights(lay, c_star))
        n = R.gens(cell, [("dev", "DEV_H", g, TOK_DEV) for g in LANGS])
        per_mod = {f"{l}|{c}": lora_energy(A, B) for (l, c), (A, B) in ed.factors().items()}
        jdump({"cell": cell, "stage": "profile", "type": "single_layer" if width == 1 else "window", "h": h,
               "layers": lay, "c": c_star, "width": width,
               "E_exact": float(sum(per_mod.values())),
               "E_per_layer": [sum(v for k, v in per_mod.items() if int(k.split("|")[0]) == l) for l in range(ed.L)]},
              C.CELLS / cell / "meta.json")
        if h in (4, 12, 20, 28, 36, 44):   # collateral spot-checks along the profile (GPU budget)
            R.tf(cell, "FLORES", kl=False)
        if n:
            R.tick(cell, ta)
    R.tick("profile_total", t0)
    ed.reset()
    lm.close()


def solve_c_exact(ed: Editor, dirs: np.ndarray, wfn, target: float, tol: float = 0.005) -> tuple[float, float]:
    """Solve the weight scale whose EXACT total removal energy hits `target`, using the verified k^2 energy law
    (GATE 1 measured it to 1.1e-3) with Newton corrections against the exact energy of the applied factors."""
    ed.apply(dirs, wfn(1.0))
    e1 = ed.total_energy()
    c = math.sqrt(target / e1)
    for _ in range(6):
        ed.apply(dirs, wfn(c))
        e = ed.total_energy()
        if abs(e / target - 1) <= tol:
            break
        c *= math.sqrt(target / e)
    return c, e


# ============================================================================================ STAGE confirm
def freeze_ok() -> dict:
    fz, sh = C.CFG / "frozen_predictions.json", C.CFG / "FREEZE.sha256"
    if not (fz.exists() and sh.exists()):
        raise RuntimeError("FREEZE GUARD: configs/FREEZE.sha256 and configs/frozen_predictions.json must both exist "
                           "before any confirmation generation - run freeze.py first")
    want = {parts[1]: parts[0] for parts in (l.split() for l in sh.read_text().splitlines()) if len(parts) == 2}
    got = C.file_sha256(fz)
    key = [k for k in want if k.endswith("frozen_predictions.json")]
    if not key or want[key[0]] != got:
        raise RuntimeError(f"FREEZE GUARD: frozen_predictions.json hash {got[:12]} does not match FREEZE.sha256")
    if fz.stat().st_mtime > sh.stat().st_mtime + 5:
        raise RuntimeError("FREEZE GUARD: the predictions file is newer than its hash file")
    return jload(fz)


def stage_confirm(args) -> None:
    F = freeze_ok()
    logger.info(f"FREEZE verified ({len(F['cells'])} frozen cells, declared {F['declared_utc']})")
    S = sets(args.mini)
    lm, ed = load()
    R = Runner(lm, ed, S)
    dEN_all = np.load(C.E8 / "directions/gams3_all_layers.npz")["dEN"].astype(np.float32)
    fams = {"dEN": dEN_all}
    for d in range(3):
        fams[f"rnd_d{d}"] = np.load(C.RES / f"controls/rnd_d{d}.npy")
    for r in range(3):
        fams[f"pc_r{r}"] = np.load(C.RES / f"controls/pc_r{r}.npy")
    ed.reset()
    lm.reset()
    R.flores_base("FLORES")
    R._dol = R.dolly_ref()
    extra = jload(C.CFG / "post_freeze_cells.json")["cells"] if (C.CFG / "post_freeze_cells.json").exists() else []
    if extra:
        logger.warning(f"{len(extra)} POST-FREEZE EXPLORATORY cells appended (configs/post_freeze_cells.json); they "
                       f"are never part of the pre-registered family")
    order = sorted(F["cells"] + extra, key=lambda c: (c["priority"], c["cell"]))
    for spec in order:
        cell = spec["cell"]
        if (C.CELLS / cell / "tf.json").exists() and (C.CELLS / cell / "gens.json").exists():
            recs = jload(C.CELLS / cell / "gens.json")
            if len({(r["split"], r["uid"], r["lang"]) for r in recs}) >= spec["n_expected"]:
                continue
        if DEADLINE and time.time() > DEADLINE:
            logger.warning(f"deadline reached; stopping before {cell} (cut order applies)")
            break
        ta = time.time()
        ed.reset()
        lm.reset()
        meta = {k: v for k, v in spec.items() if k != "n_expected"}
        if spec["type"] == "weight":
            c = spec["c"]
            if c is None:      # energy-matched control draw: solve its scale against the exact energy identity
                c, e_got = solve_c_exact(ed, fams[spec["family"]], lambda x: flat_weights(spec["layers"], x),
                                         spec["E_target"])
                meta["c"] = c
                logger.info(f"[{cell}] control scale solved: c = {c:.4f} -> E {e_got:.2f} (target {spec['E_target']:.2f})")
            w = flat_weights(spec["layers"], c)
            ed.apply(fams[spec["family"]], w)
        elif spec["type"] == "kernel":
            wfn = her88_weights if spec["kernel"] == "trial88" else swap_weights
            c = spec["c"]
            if c is None:
                c, e_got = solve_c_exact(ed, dEN_all, wfn, spec["E_target"])
                meta["c"] = c
                logger.info(f"[{cell}] kernel scale solved: c = {c:.4f} -> E {e_got:.2f} (target {spec['E_target']:.2f})")
            w = wfn(c)
            ed.apply(dEN_all, w)
            meta["layers"] = sorted({l for l, _ in w})
            meta["max_weight"] = max(w.values())
            meta["above_heretic_bound"] = bool(max(w.values()) > C_BOUND_REPORT)
        elif spec["type"] == "adapter":
            ed.load_adapter(C.E1 / "adapters/gams_selected_path2/adapter_model.safetensors")
        elif spec["type"] != "noop":
            raise ValueError(spec["type"])
        per_mod = {f"{l}|{c}": lora_energy(A, B) for (l, c), (A, B) in ed.factors().items()}
        meta["E_exact"] = float(sum(per_mod.values()))
        meta["E_per_layer"] = [sum(v for k, v in per_mod.items() if int(k.split("|")[0]) == l) for l in range(ed.L)]
        if spec.get("E_target"):
            meta["E_rel_dev"] = meta["E_exact"] / spec["E_target"] - 1
            if abs(meta["E_rel_dev"]) > 0.02:
                logger.warning(f"[{cell}] energy match {meta['E_rel_dev']:+.3f} outside the declared 2% window")
        jdump(meta, C.CELLS / cell / "meta.json")
        plan = [("confirm", "CONF_H", g, TOK_CONF_H) for g in LANGS]
        if spec["benign"]:
            plan += [("confirm_ben", "CONF_B", g, TOK_CONF_B) for g in LANGS]
        R.gens(cell, plan)
        R.tf(cell, "FLORES", kl=spec["kl"])
        R.tick(cell, ta)
        logger.info(f"[{cell}] done in {time.time()-ta:.0f}s (E_exact {meta['E_exact']:.1f})")
    ed.reset()
    lm.close()


# ============================================================================================ reuse of stored cells
REUSE = {                     # iteration-3 panel cells on the SAME items, tokens, model, quantisation and schedule
    "A1_ship": "CORE_trial88",            # the shipped GaMS3 edit (Optuna trial 88)
    "A2_swap": "SWAP_in_trial96",         # the sibling checkpoint's kernel, as-is
    "R_NOOP": "NOOP",                     # the unedited model on the confirmation items
    "R_G1_single_site": "G1_single_site",  # the single-site causal probe (cheap baseline 1)
    "R_B1_c1": "GRID_B1_c1.0", "R_B2_c1": "GRID_B2_c1.0", "R_B3_c1": "GRID_B3_c1.0", "R_B4_c1": "GRID_B4_c1.0",
    "R_STR4_c1": "GRID_STR4_c1.0", "R_STR2_c1": "GRID_STR2_c1.0", "R_ALL_c1": "GRID_ALL_c1.0",
    "R_HER88_c1": "GRID_HER88_c1.0",
}


def stage_reuse(args) -> None:
    """Copy the iteration-3 panel cells this pod re-reads (generations + metas) into results/cells/, re-labelled here
    by THIS pod's judge run. No GPU: the stored generations are the anchors, not new measurements."""
    out = {}
    for new, old in REUSE.items():
        src = C.E10 / f"results/cells/{old}"
        if not src.exists():
            logger.error(f"reuse source missing: {src}")
            continue
        dst = C.CELLS / new
        dst.mkdir(parents=True, exist_ok=True)
        recs = [r | {"cell": new} for r in jload(src / "gens.json")]
        jdump(recs, dst / "gens.json")
        meta = jload(src / "meta.json") | {"cell": new, "reused_from": C.relpath(src), "stage": "reused",
                                           "reuse_sha256_gens": C.file_sha256(src / "gens.json")}
        jdump(meta, dst / "meta.json")
        if (src / "tf.json").exists():
            shutil.copy(src / "tf.json", dst / "tf.json")
        out[new] = {"source": C.relpath(src), "n_gens": len(recs), "splits": sorted({r["split"] for r in recs})}
        logger.info(f"reused {old} -> {new}: {len(recs)} generations")
    jdump(out, C.RES / "reused_cells.json")


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["smoke", "profile", "confirm", "reuse"], required=True)
    ap.add_argument("--mini", action="store_true")
    args = ap.parse_args()
    if args.mini and not C.MINI:
        raise SystemExit("run mini with AII_MINI=1 in the environment")
    setup_logging(f"method_{args.stage}{'_mini' if args.mini else ''}")
    guard_resources()
    torch.manual_seed(C.SEED)
    np.random.seed(C.SEED)
    {"smoke": stage_smoke, "profile": stage_profile, "confirm": stage_confirm, "reuse": stage_reuse}[args.stage](args)


if __name__ == "__main__":
    main()
