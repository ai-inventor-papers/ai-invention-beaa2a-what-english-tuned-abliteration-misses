#!/usr/bin/env python3
"""PHASE 2 - FREEZE. Reads ONLY the Phase-1 DEV profile generations + their judge labels (and the teacher-forced
readout), computes the causal write profiles e_EN(h), e_SL(h) with item-bootstrap bands and split-half stability,
applies the pre-declared primary-variant rule (configs/protocol.yaml), builds the matched-energy / matched-count
confirmation groups from the frozen profile and exp9's closed-form per-module energies, writes every prediction, the
frozen CONF item ids and the MDE to configs/frozen_predictions.json, and hashes it (+ protocol, stats code, method.py)
into configs/FREEZE.sha256. Refuses to run if any confirmation generation already exists."""
from __future__ import annotations

import itertools
import time

import numpy as np
from loguru import logger

import alib as A
import common as C
from common import jdump, jload

L, H = 48, 49
COMPS = ("o_proj", "down_proj")
P = C.PROTO
BANDS = {"1-12": range(1, 13), "13-24": range(13, 25), "25-36": range(25, 37), "37-48": range(37, 49)}


def per_layer_energy() -> np.ndarray:
    """E1[h-1] = sum_comp ||W_comp(j=h-1)^T rhat_h||^2 (exp9 energy_real.json, NF4-dequantised, c = 1)."""
    e = jload(C.EXP9 / "results/energy_real.json")["e"]
    return np.array([e[f"{j}|o_proj"] + e[f"{j}|down_proj"] for j in range(L)])


def judged_profile(df) -> dict:
    """e_raw_L(h) = mean over DEV items judged in BOTH the no-op and the ablate-h cell of [refused(no-op) - refused(h)]
    (pairwise per layer, so a judge parse failure removes one pair, not the item from every layer); item bootstrap."""
    out = {}
    cells = ["PF_noop"] + [f"PF_h{h:02d}" for h in range(1, H)]
    for g in C.LANGS:
        d = df[(df["model"] == "gemma") & (df["lang"] == g) & df["cell"].isin(cells)]
        ref = d.assign(y=np.where(d["judged"], (d["cls4"] == "REFUSED").astype(float), np.nan)).pivot_table(
            index="uid", columns="cell", values="y", aggfunc="first", dropna=False).reindex(columns=cells)
        inv = d.assign(y=np.where(d["judged"], (d["cls4"] == "INVALID").astype(float), np.nan)).pivot_table(
            index="uid", columns="cell", values="y", aggfunc="first", dropna=False).reindex(columns=cells)
        ids = sorted(ref.index)
        M = ref.loc[ids].values.T  # [49, n] with NaN = no label
        D = M[0][None, :] - M[1:]  # [48, n] paired drops (NaN where either side unlabelled)
        n = len(ids)

        def e_of(cols):
            return np.nanmean(D[:, cols], axis=1)
        e_raw = e_of(np.arange(n))
        bi = A.boot_idx(n)
        eb = np.stack([e_of(b) for b in bi])
        half = n // 2
        e1, e2 = e_of(np.arange(half)), e_of(np.arange(half, n))
        sh = float(np.corrcoef(e1, e2)[0, 1]) if np.nanstd(e1) > 0 and np.nanstd(e2) > 0 else float("nan")
        invr = np.nanmean(inv.loc[ids].values.T[1:], axis=1)
        out[g] = {"n_items": n, "item_uids": ids, "n_pairs_per_layer": np.isfinite(D).sum(1).tolist(),
                  "noop_refusal": float(np.nanmean(M[0])), "e_raw": e_raw.tolist(),
                  "e_ci_lo": np.nanpercentile(eb, 2.5, 0).tolist(), "e_ci_hi": np.nanpercentile(eb, 97.5, 0).tolist(),
                  "split_half_r": sh, "invalid_rate": invr.tolist(), "flagged_layers": [h for h in range(1, H) if invr[h - 1] > 0.10],
                  "ablated_refusal": np.nanmean(M[1:], axis=1).tolist()}
    return out


def tf_profile() -> dict:
    """e_tf_L(h) = mean over the 44 DEV harmful items of [lp_noop - lp_ablate(h)] of the no-op refusal prefix."""
    tf = jload(C.RES / "profile_tf.json")
    out = {}
    for g in C.LANGS:
        base = np.array(tf["noop"][g])
        D = np.stack([base - np.array(tf[f"PF_h{h:02d}"][g]) for h in range(1, H)])  # [48, n]
        n = D.shape[1]
        half = n // 2
        e1, e2 = D[:, :half].mean(1), D[:, half:].mean(1)
        bi = A.boot_idx(n)
        eb = np.stack([D[:, b].mean(1) for b in bi])
        fl = np.array([np.mean(np.array(tf[f"PF_h{h:02d}_flores"][g]) - np.array(tf["noop_flores"][g])) for h in range(1, H)])
        out[g] = {"n_items": n, "e_raw": D.mean(1).tolist(), "e_ci_lo": np.percentile(eb, 2.5, 0).tolist(),
                  "e_ci_hi": np.percentile(eb, 97.5, 0).tolist(), "split_half_r": float(np.corrcoef(e1, e2)[0, 1]),
                  "flores_dNLL_dev40": fl.tolist()}
    return out


def normalise(e_raw) -> np.ndarray | None:
    e = np.clip(np.asarray(e_raw, float), 0, None)
    return None if e.sum() <= 0 else e / e.sum()


def O_of(e: np.ndarray, g: np.ndarray) -> float:
    return float((e * g).sum() / np.sqrt((g ** 2).sum()))


def window_sets(k: int) -> list[list[int]]:
    return [list(range(s, s + k)) for s in range(1, L - k + 2)]


def descriptors(layers: list[int], c: float, E1: np.ndarray, cosL: np.ndarray, eprof: dict, e_raw: dict) -> dict:
    """Per-condition predictors: O_L, energy, count, span, g-weighted EN/SL cosine, peak-site probe."""
    g = np.zeros(L)
    for k in layers:
        g[k - 1] = c * c * E1[k - 1]
    d = {"E": float(g.sum()), "log_energy": float(np.log(g.sum())), "layer_count": len(layers),
         "depth_span": int(max(layers) - min(layers) + 1), "en_sl_cosine": float((g * cosL).sum() / g.sum()),
         "h_peak": int(np.argmax(g) + 1), "g_profile": g.tolist()}
    for lang, e in eprof.items():
        d[f"O_{lang}"] = O_of(e, g)
        d[f"B_site_{lang}"] = float(e_raw[lang][int(np.argmax(g))])
    return d


def build_groups(E1: np.ndarray, eprof: dict, cosL: np.ndarray, e_raw: dict) -> list[dict]:
    """Matched groups per protocol.yaml: identical count k, identical energy (closed-form c), non-overlapping members,
    chosen to span O_SL (max-vs-min or 75th-vs-25th percentile)."""
    spec = [("G1", 8, "extreme", 1.0), ("G2", 12, "extreme", 1.0), ("G3", 16, "extreme", 1.0),
            ("G4", 12, "quartile", 0.6), ("G5", 8, "quartile", 0.6), ("G6", 16, "quartile", 0.6), ("G7", 10, "extreme", 1.0),
            ("G8", 6, "extreme", 1.0)]
    groups = []
    for gname, k, mode, f in spec:
        wins = window_sets(k)
        o = np.array([O_of(eprof["sl"], np.where(np.isin(np.arange(1, L + 1), w), E1, 0.0)) for w in wins])
        order = np.argsort(o)
        if mode == "extreme":
            hi_i = int(order[-1])
            cand = sorted((int(i) for i in order), key=lambda i: (len(set(wins[i]) & set(wins[hi_i])), o[i]))
            lo_i = cand[0]
        else:
            q75, q25 = np.percentile(o, 75), np.percentile(o, 25)
            hi_i = int(np.argmin(np.abs(o - q75)))
            cand = sorted((int(i) for i in range(len(wins)) if i != hi_i),
                          key=lambda i: (len(set(wins[i]) & set(wins[hi_i])), abs(o[i] - q25)))
            lo_i = cand[0]
        hi, lo = wins[hi_i], wins[lo_i]
        E1h, E1l = E1[np.array(hi) - 1].sum(), E1[np.array(lo) - 1].sum()
        E_t = f * C.HERETIC_MAX_WEIGHT ** 2 * min(E1h, E1l)
        mem = []
        for side, lay, e1 in (("hiO", hi, E1h), ("loO", lo, E1l)):
            c = float(np.sqrt(E_t / e1))
            assert c <= C.HERETIC_MAX_WEIGHT + 1e-9
            dsc = descriptors(lay, c, E1, cosL, eprof, e_raw)
            mem.append({"cell": f"CF_{gname}_{side}_L{lay[0]:02d}-{lay[-1]:02d}", "family": "weight", "group": gname,
                        "side": side, "layers": lay, "c": c} | dsc)
        assert abs(mem[0]["E"] - mem[1]["E"]) / mem[0]["E"] < 0.02 and mem[0]["layer_count"] == mem[1]["layer_count"]
        groups.append({"group": gname, "k": k, "mode": mode, "overlap": len(set(hi) & set(lo)), "energy_fraction": f, "E_target": E_t, "members": mem,
                       "O_SL_gap": mem[0]["O_sl"] - mem[1]["O_sl"], "O_EN_gap": mem[0]["O_en"] - mem[1]["O_en"],
                       "window_O_SL_range": [float(o.min()), float(o.max())]})
    return groups


def main() -> None:
    C.setup_logging("freeze")
    assert not list(C.GENS.glob("CF_*.json")), "confirmation generations already exist: refusing to (re)freeze"
    D = C.load_items()
    S = C.build_sets(D)
    df = A.gens_frame(("PF_",), with_lid=False)
    assert df["judged"].mean() > 0.95, f"profile not judged: {df['judged'].mean():.3f}"
    jp = judged_profile(df)
    tp = tf_profile()
    rule_j = all(np.isfinite(jp[g]["split_half_r"]) and jp[g]["split_half_r"] >= 0.5 for g in C.LANGS)
    rule_t = all(np.isfinite(tp[g]["split_half_r"]) and tp[g]["split_half_r"] >= 0.5 for g in C.LANGS)
    if rule_j and all(normalise(jp[g]["e_raw"]) is not None for g in C.LANGS):
        primary, status = "judged", "PRIMARY"
    elif rule_t and all(normalise(tp[g]["e_raw"]) is not None for g in C.LANGS):
        primary, status = "teacher_forced", "PRIMARY (judged profile failed the split-half rule; teacher-forced promoted by the pre-declared rule)"
    else:
        primary, status = ("judged" if all(normalise(jp[g]["e_raw"]) is not None for g in C.LANGS) else "teacher_forced"), "EXPLORATORY"
    src = jp if primary == "judged" else tp
    eprof = {g: normalise(src[g]["e_raw"]) for g in C.LANGS}
    eprof_alt = {g: normalise((tp if primary == "judged" else jp)[g]["e_raw"]) for g in C.LANGS}
    e_raw_j = {g: jp[g]["e_raw"] for g in C.LANGS}
    z = np.load(C.DIRS_NPZ)
    dEN, dSL = z["dEN"].astype(np.float64), z["dSL"].astype(np.float64)
    cosL = np.array([dEN[h] @ dSL[h] / (np.linalg.norm(dEN[h]) * np.linalg.norm(dSL[h])) for h in range(1, H)])
    probe_mass = {g: (np.linalg.norm((dEN if g == "en" else dSL)[1:], axis=1)) for g in C.LANGS}
    probe_mass = {g: (v / v.sum()).tolist() for g, v in probe_mass.items()}
    E1 = per_layer_energy()
    groups = build_groups(E1, eprof, cosL, e_raw_j)
    conds, prio = [], 0
    conds.append({"cell": "CF_noop", "family": "noop", "priority": prio, "layers": [], "E": 0.0})
    for G in groups[:3]:
        for m in G["members"]:
            prio += 1
            conds.append(m | {"priority": prio})
    for G in groups[:3]:  # controls of the core groups right after the core contrast
        hi = G["members"][0]
        for fam in ("random", "pc"):
            prio += 1
            conds.append({"cell": f"CF_{G['group']}_{fam}", "family": fam, "control_of": hi["cell"], "group": G["group"],
                          "priority": prio, "layers": hi["layers"]})
    lo3 = groups[2]["members"][1]
    for mult in (1.5, 2.0):  # dose ladder of G3's low-O member (energy multiplier)
        prio += 1
        c = lo3["c"] * np.sqrt(mult)
        conds.append({"cell": f"CF_dose_G3loO_x{mult:g}", "family": "weight", "group": "G3dose", "side": f"x{mult:g}",
                      "layers": lo3["layers"], "c": float(c), "priority": prio, "dose_of": lo3["cell"], "energy_multiplier": mult}
                     | descriptors(lo3["layers"], float(c), E1, cosL, eprof, e_raw_j))
    for G in groups[3:5]:
        for m in G["members"]:
            prio += 1
            conds.append(m | {"priority": prio})
        hi = G["members"][0]
        for fam in ("random", "pc"):
            prio += 1
            conds.append({"cell": f"CF_{G['group']}_{fam}", "family": fam, "control_of": hi["cell"], "group": G["group"],
                          "priority": prio, "layers": hi["layers"]})
    for G in groups[5:]:  # extra groups (no controls)
        for m in G["members"]:
            prio += 1
            conds.append(m | {"priority": prio})
    for cd in conds:  # alternative-profile O (the variant NOT chosen), reported beside O, never used for the verdict
        if cd["family"] == "weight":
            g = np.array(cd["g_profile"])
            for lang in C.LANGS:
                cd[f"O_alt_{lang}"] = O_of(eprof_alt[lang], g) if eprof_alt[lang] is not None else None
    wcells = [c for c in conds if c["family"] == "weight"]
    pred_rank = {g: [c["cell"] for c in sorted(wcells, key=lambda c: -c[f"O_{g}"])] for g in C.LANGS}
    band_of = lambda h: next(b for b, r in BANDS.items() if h in r)  # noqa: E731
    argmax_pred = {g: {"argmax_h": int(np.argmax(eprof[g]) + 1), "band": band_of(int(np.argmax(eprof[g]) + 1))} for g in C.LANGS}
    n_fit = len(wcells)
    fp = {
        "frozen_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "primary_profile": primary, "O_status": status,
        "rule": P["profile"]["primary_variant_rule"],
        "e_EN": eprof["en"].tolist(), "e_SL": eprof["sl"].tolist(),
        "e_alt_EN": None if eprof_alt["en"] is None else eprof_alt["en"].tolist(),
        "e_alt_SL": None if eprof_alt["sl"] is None else eprof_alt["sl"].tolist(),
        "judged_profile": jp, "tf_profile": tp, "probe_mass_read_profile": probe_mass,
        "spearman_e_vs_probe_mass": {g: A.spearman(eprof[g], probe_mass[g]) for g in C.LANGS},
        "spearman_e_EN_vs_e_SL": A.spearman(eprof["en"], eprof["sl"]),
        "en_sl_cosine_per_layer": cosL.tolist(), "per_layer_energy_c1": E1.tolist(),
        "O_definition": P["instrument"]["O_definition"], "g_definition": "closed-form per-layer removal energy (exp9 energy_real.json)",
        "nuisance_stack": P["instrument"]["nuisance_stack"], "cheap_baselines": P["instrument"]["cheap_baselines"],
        "single_site_transfer_rate_hstar20": (jp["sl"]["e_raw"][C.L_R - 1] / jp["en"]["e_raw"][C.L_R - 1]
                                              if jp["en"]["e_raw"][C.L_R - 1] != 0 else None),
        "primary_thresholds": P["instrument"]["primary_thresholds"],
        "groups": groups, "confirmation_condition_list": conds,
        "predicted_rank_order_of_conditions_per_language": pred_rank,
        "frozen_confirmation_item_uids": [it["uid"] for it in S["conf"]],
        "conf_item_composition": {"hoc": len(S["conf_hoc"]), "s5x": len(S["conf_s5x"])},
        "argmax_band_prediction": argmax_pred,
        "prediction_matched_contrast": "within every group, residual SL refusal of the high-O member < low-O member",
        "placebos_that_must_collapse": ["cell_label_perm_within_language", "language_label_perm", "energy_shuffled_g"],
        "MDE": {"n_weight_cells_per_language": n_fit, "spearman_mde_per_language": A.mde_spearman(n_fit),
                "spearman_mde_pooled_2lang": A.mde_spearman(2 * n_fit),
                "dR2_mde_per_language_base4": A.mde_dr2(n_fit, 4, 1), "dR2_mde_pooled_base4": A.mde_dr2(2 * n_fit, 4, 1),
                "matched_contrast_item_mde_approx": float(2.8 * np.sqrt(2 * 0.25 / len(S["conf"])))},
        "verdict_rule": P["verdict_rule"],
    }
    jdump(fp, C.CFG / "frozen_predictions.json")
    files = ["configs/frozen_predictions.json", "configs/protocol.yaml", "alib.py", "freeze.py", "method.py", "common.py",
             "interventions.py", "judge/local_judge.py"]
    (C.CFG / "FREEZE.sha256").write_text("".join(f"{C.file_sha256(C.ROOT / f)}  {f}\n" for f in files))
    logger.info(f"FROZEN: primary={primary} ({status}); split-half judged EN {jp['en']['split_half_r']:.2f} SL "
                f"{jp['sl']['split_half_r']:.2f}; tf EN {tp['en']['split_half_r']:.2f} SL {tp['sl']['split_half_r']:.2f}")
    for G in groups:
        m = G["members"]
        logger.info(f"{G['group']}: {m[0]['cell']} O_SL {m[0]['O_sl']:.3f} vs {m[1]['cell']} O_SL {m[1]['O_sl']:.3f}; "
                    f"E {m[0]['E']:.1f}/{m[1]['E']:.1f}; c {m[0]['c']:.2f}/{m[1]['c']:.2f}")


if __name__ == "__main__":
    logger.catch(reraise=True)(main)()
