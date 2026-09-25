#!/usr/bin/env python3
"""STAGE 5 (priority 2): Heretic bridge. Uses Heretic @3521f864's own Model class (bnb_4bit, LoRA abliteration,
orthogonalize_direction=true, row_normalization='full') and its refusal directions computed from S1
(mlabonne/harmful_behaviors + harmless_alpaca train[:400], English), then applies Heretic startup draws 1-20
(TPESampler seed 20260923; draws 61-200 are RESERVED) and measures rho_SL - rho_EN per edit, plus u_SL activation
ablation on top of the 5 strongest edits.

  uv run heretic_bridge.py --model gams3 [--n-edits 20]"""
from __future__ import annotations

import argparse
import sys
import time

import numpy as np
import optuna
import torch
import torch.nn.functional as F
from loguru import logger

import common as C
from common import LANGS, MODELS, SEED, jdump, jload, setup_logging
from interventions import LM, cos, refusal_scores


def heretic_params(trial, n_layers: int, components: list[str]):
    """Verbatim copy of the suggest_* calls of heretic main.py objective() @3521f864 (same order, names, ranges)."""
    from heretic.model import AbliterationParameters

    direction_scope = trial.suggest_categorical("direction_scope", ["global", "per layer"])
    last_layer_index = n_layers - 1
    direction_index = trial.suggest_float("direction_index", 0.4 * last_layer_index, 0.9 * last_layer_index)
    if direction_scope == "per layer":
        direction_index = None
    parameters = {}
    for component in components:
        max_weight_lower_bound = -0.25 if component == "mlp.down_proj" else 0.8
        max_weight = max(0.0, trial.suggest_float(f"{component}.max_weight", max_weight_lower_bound, 1.5))
        max_weight_position = trial.suggest_float(f"{component}.max_weight_position", 0.6 * last_layer_index, 1.0 * last_layer_index)
        min_weight = trial.suggest_float(f"{component}.min_weight", 0.0, 1.0)
        min_weight_distance = trial.suggest_float(f"{component}.min_weight_distance", 1.0, max(0.6 * last_layer_index, 1.0))
        parameters[component] = AbliterationParameters(max_weight=max_weight, max_weight_position=max_weight_position,
                                                       min_weight=(min_weight * max_weight), min_weight_distance=min_weight_distance)
    return direction_index, parameters


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=list(MODELS))
    ap.add_argument("--n-edits", type=int, default=20)
    args = ap.parse_args()
    setup_logging(f"heretic_bridge_{args.model}")
    out = C.RES / args.model
    t0 = time.time()
    sys.argv = ["heretic"]  # Heretic's Settings parses the CLI; give it none
    from heretic.config import Settings
    from heretic.model import Model
    from heretic.utils import Prompt

    settings = Settings(model=MODELS[args.model]["repo"], model_commit=MODELS[args.model]["sha"], quantization="bnb_4bit",
                        seed=SEED, batch_size=32)
    hm = Model(settings)
    logger.info(f"Heretic model loaded ({time.time()-t0:.0f}s); orthogonalize_direction={settings.orthogonalize_direction} "
                f"row_normalization={settings.row_normalization}")
    items = jload(C.DATA / "screen_dev.json")
    s1h = [it["en"] for it in items if it["kind"] == "s1_harmful"]
    s1b = [it["en"] for it in items if it["kind"] == "s1_harmless"]
    sysmsg = settings.system_prompt
    good = [Prompt(system=sysmsg, user=t) for t in s1b]
    bad = [Prompt(system=sysmsg, user=t) for t in s1h]
    with torch.inference_mode():
        good_means = hm.get_residuals_mean(good)
        bad_means = hm.get_residuals_mean(bad)
    rd = F.normalize(bad_means - good_means, p=2, dim=1)
    if settings.orthogonalize_direction:
        gd = F.normalize(good_means, p=2, dim=1)
        rd = F.normalize(rd - torch.sum(rd * gd, dim=1).unsqueeze(1) * gd, p=2, dim=1)
    torch.save(rd.cpu(), out / "heretic_directions.pt")
    dirs = np.load(out / "frozen_directions.npz")
    proto = jload(C.CFG / f"frozen_protocol_{args.model}.json")
    h = proto["h_star"]
    cos_h = {"cos_heretic_dEN_at_hstar": cos(rd[h].cpu().numpy(), dirs["dEN"]), "cos_heretic_dSL_at_hstar": cos(rd[h].cpu().numpy(), dirs["dSL"]),
             "cos_heretic_uSL_at_hstar": cos(rd[h].cpu().numpy(), dirs["uSL"]),
             "note": "Heretic direction index h = hidden_states[h] = our hidden index h (0 = embeddings); Heretic uses the last prompt position (pos -1) with left padding"}
    logger.info(f"cosines {cos_h}")
    # startup draws 1..n (allowed); identical across models by construction
    n_layers = len(hm.get_layers())
    comps = hm.get_abliterable_components()
    study = optuna.create_study(sampler=optuna.samplers.TPESampler(n_startup_trials=60, n_ei_candidates=128, multivariate=True, seed=SEED),
                                directions=["minimize", "minimize"])
    draws = []
    for k in range(args.n_edits):
        tr = study.ask()
        di, params = heretic_params(tr, n_layers, comps)
        draws.append({"trial": k + 1, "raw_params": tr.params, "direction_index": di,
                      "parameters": {c: vars(p) for c, p in params.items()}})
        study.tell(tr, [0.0, 0.0])  # dummy values; startup draws are independent of history
    jdump(draws, out / "startup_params.json")
    # evaluation wrapper on Heretic's own (PeftModel) model
    lm = LM(args.model, hf_model=hm.model, tok=hm.tokenizer)
    sets = jload(C.CFG / f"prefix_sets_{args.model}.json")
    from method import Scorer

    sc = Scorer(lm, sets)
    harm = [it for it in items if it["kind"] == "jbb_harmful" and it["half"] == 1]
    ben = [it for it in items if it["kind"] == "jbb_benign" and it["half"] == 1]
    dol = [it for it in items if it["kind"] == "dolly" and it["half"] == 1][:12]
    cont = jload(out / "dolly_B_continuations.json")
    dol_ids = [it["semantic_id"] for it in items if it["kind"] == "dolly" and it["half"] == 1]
    kl_seqs, kl_starts, kl_n = [], [], []
    for lang in LANGS:
        for it in dol:
            b = lm.encode_chat(it[lang])[0]
            c = cont[lang][dol_ids.index(it["semantic_id"])]
            kl_seqs.append(b + c)
            kl_starts.append(len(b))
            kl_n.append(len(c))
    hm.reset_model()
    lm.reset()
    refs = [lm.ref_topk([s], [st], n)[0] for s, st, n in zip(kl_seqs, kl_starts, kl_n)]

    def evaluate(tag: str) -> dict:
        r = {}
        for lang in LANGS:
            r[f"R_harm_{lang}"] = sc.R(harm, lang)[0]
            r[f"R_ben_{lang}"] = sc.R(ben, lang)[0]
        kls = []
        for s, st, n, ref in zip(kl_seqs, kl_starts, kl_n, refs):
            kls.append(lm.kl_vs_ref([s], [st], n, [ref])[0])
        r["KL_en"] = float(np.mean(kls[:len(dol)]))
        r["KL_sl"] = float(np.mean(kls[len(dol):]))
        return r
    base = evaluate("base")
    Rb0 = {l: float(base[f"R_ben_{l}"].mean()) for l in LANGS}
    R0 = {l: float(base[f"R_harm_{l}"].mean()) for l in LANGS}

    def rho(v, l):
        return (float(np.mean(v)) - Rb0[l]) / (R0[l] - Rb0[l])
    edits = []
    for d in draws:
        te = time.time()
        from heretic.model import AbliterationParameters

        params = {c: AbliterationParameters(**p) for c, p in d["parameters"].items()}
        hm.reset_model()
        hm.abliterate(rd, d["direction_index"], params)
        lm.reset()
        r = evaluate(f"edit{d['trial']}")
        rec = {"trial": d["trial"], "rho_en": rho(r["R_harm_en"], "en"), "rho_sl": rho(r["R_harm_sl"], "sl"),
               "meanR_harm_en": float(r["R_harm_en"].mean()), "meanR_harm_sl": float(r["R_harm_sl"].mean()),
               "meanR_ben_en": float(r["R_ben_en"].mean()), "meanR_ben_sl": float(r["R_ben_sl"].mean()),
               "KL_en": r["KL_en"], "KL_sl": r["KL_sl"], "per_item_R_harm_en": r["R_harm_en"].tolist(), "per_item_R_harm_sl": r["R_harm_sl"].tolist()}
        rec["gap"] = rec["rho_sl"] - rec["rho_en"]
        edits.append(rec)
        logger.info(f"edit {d['trial']}: rho_en={rec['rho_en']:.3f} rho_sl={rec['rho_sl']:.3f} gap={rec['gap']:.3f} "
                    f"KL_en={rec['KL_en']:.3f} ({time.time()-te:.0f}s)")
    # u_SL activation ablation on top of the 5 edits with the lowest rho_EN
    top = sorted(edits, key=lambda e: e["rho_en"])[:5]
    for e in top:
        d = draws[e["trial"] - 1]
        params = {c: AbliterationParameters(**p) for c, p in d["parameters"].items()}
        hm.reset_model()
        hm.abliterate(rd, d["direction_index"], params)
        lm.set_ablate(dirs["uSL"])
        rs = sc.R(harm, "sl")[0]
        re_ = sc.R(harm, "en")[0]
        lm.set_ablate(dirs["Q1"])
        rq = sc.R(harm, "sl")[0]
        lm.reset()
        e["uSL_on_top"] = {"rho_sl": rho(rs, "sl"), "rho_en": rho(re_, "en"), "extra_SL_drop_R": float(e["meanR_harm_sl"] - rs.mean()),
                           "extra_SL_drop_R_randomQ1": float(e["meanR_harm_sl"] - rq.mean())}
    hm.reset_model()
    gaps = np.array([e["gap"] for e in edits])
    bi = np.random.default_rng(0).integers(0, len(gaps), (2000, len(gaps)))
    ren = np.array([e["rho_en"] for e in edits])
    rsl = np.array([e["rho_sl"] for e in edits])
    slope, icpt = np.polyfit(ren, rsl, 1)
    res = {"model": args.model, "n_edits": len(edits), "settings": {"quantization": "bnb_4bit", "seed": SEED,
           "orthogonalize_direction": settings.orthogonalize_direction, "row_normalization": str(settings.row_normalization),
           "full_normalization_lora_rank": settings.full_normalization_lora_rank, "components": comps},
           "cosines": cos_h, "baseline": {"R0": R0, "Rb0": Rb0}, "mean_gap": float(gaps.mean()),
           "mean_gap_ci95": [float(np.percentile(gaps[bi].mean(1), 2.5)), float(np.percentile(gaps[bi].mean(1), 97.5))],
           "regression_rho_sl_on_rho_en": {"slope": float(slope), "intercept": float(icpt)}, "edits": edits,
           "unit_of_uncertainty": "edit-bootstrap over the 20 startup draws (not item-level)", "runtime_s": time.time() - t0}
    jdump(res, out / "heretic_bridge.json")
    logger.info(f"bridge done: mean gap {res['mean_gap']:.3f} CI {res['mean_gap_ci95']}")


if __name__ == "__main__":
    main()
