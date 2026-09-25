"""PHASE 5 - OUTSIDE FAMILY: Qwen/Qwen3-8B (NF4, thinking disabled) in EN, SL, DE, LT.

Phase A (no frozen_outside.json yet): pre-registered eligibility gate on DEV (exp12 items_cal, 24 JBB half-A harmful
items per language; no-op refusal >= 0.60 AND INVALID <= 0.20, judged later), a spot re-verification of exp12's frozen
Qwen3 directions, per-module closed-form energies of the orthogonalised directions, and the reduced-resolution causal
profile (single-site ablation of d_EN(h) at every 3rd hidden index, same DEV items, 96 tokens).
Phase B (after judge + freeze_outside.py): the frozen matched-energy / matched-count conditions + no-op + random control
on exp12 items_conf (S4 StrongREJECT harmful, 40 per language), 128 tokens, eligible languages only."""
from __future__ import annotations

import json
import time

import numpy as np
import torch
from loguru import logger

import common as C
from common import jdump, jload
from interventions import LM, unit, winsorize

KEY = "qwen3"
LANGS4 = ("en", "sl", "de", "lt")
DIRS = C.EXP12 / "results/qwen3/directions.npz"
OUT = C.RES / "outside"
OUT.mkdir(parents=True, exist_ok=True)
COMPS = ("o_proj", "down_proj")


def ex12(name: str) -> list[dict]:
    rows = [json.loads(l) for l in (C.EXP12 / "data" / f"items_{name}.jsonl").read_text().splitlines() if l.strip()]
    for r in rows:  # exp12 rows carry no 'kind' / 'stratum'; add them so generation records share one format
        r.setdefault("kind", f"{r.get('source', name)}_{r.get('role', 'na')}")
        r.setdefault("stratum", f"exp12_{name}")
        r.setdefault("semantic_id", r["uid"])
    return sorted(rows, key=lambda r: r["uid"])


def run(ctx) -> None:
    import method as M

    from huggingface_hub import snapshot_download
    snap = snapshot_download(C.OUTSIDE["repo"], local_files_only=True)
    sha = snap.rstrip("/").split("/")[-1]
    t0 = time.time()
    torch.cuda.set_per_process_memory_fraction(0.92)
    lm = LM(KEY, repo=C.OUTSIDE["repo"], sha=sha)
    ctx.lm = lm
    ctx.tick("load_qwen3", t0)
    z = np.load(DIRS)
    dEN = z["dEN"].astype(np.float32)
    vd = z["vdirs"].astype(np.float32)  # Heretic-orthogonalised (harmless-mean removed) per-hidden-index directions
    Lq = lm.L
    cal = ex12("cal")
    dirh = ex12("dir")
    frozen = OUT / "frozen_outside.json"
    if not frozen.exists():
        info = {"repo": C.OUTSIDE["repo"], "revision": sha, "L": Lq, "D": lm.D, "directions_npz": str(DIRS),
                "directions_sha256": C.file_sha256(DIRS)}
        # spot re-verification of exp12's frozen direction (EN, 2 layers)
        harm = [it for it in dirh if it["role"] == "harmful"]
        ben = [it for it in dirh if it["role"] == "harmless"]
        spot = [Lq // 3, 2 * Lq // 3]
        sh = [lm.encode_chat(it["en"])[0] for it in harm]
        sb = [lm.encode_chat(it["en"])[0] for it in ben]
        Xh = lm.capture(sh, [[len(s) - 1] for s in sh], [[len(s) - 1] for s in sh], layers=spot)[:, :, 0]
        Xb = lm.capture(sb, [[len(s) - 1] for s in sb], [[len(s) - 1] for s in sb], layers=spot)[:, :, 0]
        info["cos_fresh_vs_frozen"] = {int(h): float(np.dot(unit(winsorize(Xh[:, k]).mean(0) - winsorize(Xb[:, k]).mean(0)),
                                                           unit(dEN[h]))) for k, h in enumerate(spot)}
        e = {}
        for j in range(Lq):
            for comp in COMPS:
                e[f"{j}|{comp}"] = float(lm.module_energy(j, comp, vd[j + 1][None])[0])
        info["energy"] = e
        jdump(info, OUT / "phaseA_info.json")
        logger.info(f"[qwen3] cos fresh vs frozen {info['cos_fresh_vs_frozen']}")
        plan = [(cal, g) for g in LANGS4]
        mx = C.PROTO["decoding"]["dev_max_new"]
        M.run_cell(ctx, None, "QPF_noop", lambda: None, plan, M.cell_meta("QPF_noop", "noop", None, None, {"part": "outside_profile"}),
                   "outside_profile", mx, model=KEY)
        for h in range(3, Lq + 1, 3):
            name = f"QPF_h{h:02d}"
            M.run_cell(ctx, None, name, (lambda h=h: lm.set_ablate_layerwise({h: dEN[h]}, 1.0)), plan,
                       M.cell_meta(name, "act_single", None, None, {"part": "outside_profile", "h": h}), "outside_profile", mx,
                       model=KEY)
        logger.info("[qwen3] phase A complete (judge, then freeze_outside.py)")
        lm.close()
        return
    fz = jload(frozen)
    assert C.file_sha256(frozen) == (OUT / "FREEZE_outside.sha256").read_text().split()[0], "outside freeze changed"
    conf = [it for it in ex12("conf") if it["uid"] in set(fz["conf_item_uids"])]
    langs = fz["eligible_langs"]
    plan = [(conf, g) for g in langs]
    mx = C.PROTO["decoding"]["conf_max_new"]
    flo = ex12("flores")[:100]
    col = M.Collateral(ctx, langs=langs, flores_items=flo, dolly_items=None, tag=KEY) if False else None
    dirs = {j: vd[j + 1] for j in range(Lq)}
    for cd in sorted(fz["conditions"], key=lambda c: c["priority"]):
        name = cd["cell"]
        if cd["family"] == "noop":
            setup = (lambda: None)
        elif cd["family"] == "weight":
            prof = {(k - 1, comp): float(cd["c"]) for k in cd["layers"] for comp in COMPS}
            setup = (lambda prof=prof: lm.set_weight_edit_layerwise(M.weight_spec(prof, dirs)))
        elif cd["family"] == "random":
            rd = M.random_write_dirs(lm, dirs, [k - 1 for k in cd["layers"]], C.SEED + 77, None)
            e_r = M.energies(lm, rd)
            prof = {(k - 1, comp): float(cd["c"]) for k in cd["layers"] for comp in COMPS}
            newp, s, E, ok = M.scaled_control(prof, e_r, cd["E_target"])
            cd = cd | {"E": E, "energy_matched": ok, "scale": s}
            setup = (lambda newp=newp, rd=rd: lm.set_weight_edit_layerwise(M.weight_spec(newp, rd)))
        else:
            raise ValueError(cd)
        M.run_cell(ctx, col, name, setup, plan, M.cell_meta(name, cd["family"], None, cd.get("E"), cd, nl=Lq), "outside_conf",
                   mx, model=KEY)
    # FLORES collateral (100 pairs/language, teacher forced) for every outside condition, measured after generation
    flo_seqs = {g: [lm.encode_plain(it[g]) for it in flo] for g in langs}
    lm.reset()
    lm.set_weight_edit_layerwise({})
    base = {g: lm.seq_nll(flo_seqs[g], [1] * len(flo)) for g in langs}
    colres = {}
    for cd in sorted(fz["conditions"], key=lambda c: c["priority"]):
        if cd["family"] != "weight":
            continue
        prof = {(k - 1, comp): float(cd["c"]) for k in cd["layers"] for comp in COMPS}
        lm.set_weight_edit_layerwise(M.weight_spec(prof, dirs))
        colres[cd["cell"]] = {g: float(np.mean(lm.seq_nll(flo_seqs[g], [1] * len(flo)) - base[g])) for g in langs}
        lm.set_weight_edit_layerwise({})
    jdump(colres, OUT / "outside_flores_dNLL.json")
    logger.info("[qwen3] phase B complete")
    lm.close()
