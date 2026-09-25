#!/usr/bin/env python3
"""Final audit (T0-T9 of the testing plan), kept OUT of analysis.py because that file's sha256 is recorded in the freeze
and must not change after it. Checks: the frozen data files still hash to FREEZE.sha256; DEV and CONF share no semantic
id; the Gemma DEV curve reproduces the iteration-2 anchor (positive control); directions, hooks and templates passed
their gates; judge parse rate; energy and collateral matching of the weight cells; and which fallbacks fired.
Output: results/checks.json."""
from __future__ import annotations

from loguru import logger

import common as C

# iteration-2 exp8 anchor values (second judge, full coverage) for the positive-control replication
ANCHOR = {"gemma|en|0.5": 0.42, "gemma|sl|0.75": 0.21, "gemma|sl|1.0": 0.23, "gemma|sl|0.25": 0.82}
TOL = 0.15


@logger.catch(reraise=True)
def main() -> None:
    C.setup_logging("checks")
    res: dict = {}
    # ---- data freeze still valid
    fr = {}
    for line in (C.CFG / "FREEZE.sha256").read_text().splitlines():
        h, _, path = line.partition("  ")
        fr[path.strip()] = h
    dat = {}
    for k in ("dir", "cal", "idx", "conf", "flores"):
        p = C.DATA / f"items_{k}.jsonl"
        want = fr.get(f"data/items_{k}.jsonl")
        dat[f"items_{k}"] = {"sha256": C.file_sha256(p), "frozen": want, "ok": C.file_sha256(p) == want}
    res["data_freeze"] = {"files": dat, "all_ok": all(v["ok"] for v in dat.values())}
    fp = C.CFG / "frozen_predictions.json"
    res["freeze_enforcement"] = {"frozen_predictions_sha256": C.file_sha256(fp),
                                 "recorded_in_FREEZE": C.file_sha256(fp) in (C.CFG / "FREEZE.sha256").read_text(),
                                 "analysis_py_sha256_now": C.file_sha256(C.CODE / "analysis.py"),
                                 "analysis_py_sha256_frozen": C.jload(fp)["analysis_py_sha256"]}
    res["freeze_enforcement"]["analysis_py_unchanged"] = \
        res["freeze_enforcement"]["analysis_py_sha256_now"] == res["freeze_enforcement"]["analysis_py_sha256_frozen"]
    # ---- split disjointness (no leakage between the set that chose the index and the set that tests it)
    sid = {k: {it["semantic_id"] for it in C.read_jsonl(C.DATA / f"items_{k}.jsonl")} for k in ("dir", "cal", "idx", "conf")}
    res["split_overlap"] = {"dir_vs_idx": sorted(sid["dir"] & sid["idx"]), "dir_vs_conf": sorted(sid["dir"] & sid["conf"]),
                            "idx_vs_conf": sorted(sid["idx"] & sid["conf"]), "cal_subset_of_dir": sid["cal"] <= sid["dir"]}
    res["split_overlap"]["ok"] = not (sid["dir"] & sid["conf"] or sid["idx"] & sid["conf"])
    # ---- T4 positive control vs exp8
    frozen = C.jload(fp)
    pc = {}
    for key, want in ANCHOR.items():
        m, L, k = key.split("|")
        got = frozen["per_model_lang"][f"{m}|{L}"]["curve"].get(k)
        pc[key] = {"exp8": want, "here": got, "abs_diff": abs(got - want) if got is not None else None,
                   "within_tol": bool(got is not None and abs(got - want) <= TOL)}
    res["positive_control_vs_exp8"] = {"points": pc, "tolerance": TOL,
                                       "n_within": sum(v["within_tol"] for v in pc.values()), "n": len(pc),
                                       "note": "items and judge differ from exp8 (JBB half-B only here vs half-B + hoc there, "
                                               "local V2 judge vs exp8's), so the tolerance is deliberately loose"}
    # ---- per-model gates
    pm = {}
    for m in frozen["models"]:
        d = C.jload(C.RES / m / "direction_diagnostics.json")
        li = C.jload(C.RES / m / "load_info.json")
        ht = C.jload(C.RES / m / "hook_tests.json")
        sm = C.jload(C.RES / m / "smoke.json")
        pm[m] = {"T1_template_suffix_ok": li["T1_suffix_ok"], "T1_smoke_lid": sm["lid_ok_of_5"], "T1_smoke_pass": sm["T1_pass"],
                 "T2_hooks": {k: ht[k] for k in ("T2a_pass", "T2b_pass", "post_hook_max_proj_ratio", "c0_max_abs_logprob_diff")},
                 "T3_direction": {"auroc_max_mid": d["auroc_max_mid"], "shuffled_auroc_mean": sum(d["auroc_shuffled"]) / len(d["auroc_shuffled"]),
                                  "T3_pass": d["T3_pass"], "h_star": d["h_star"]},
                 "exp8_direction_recompute_cos": d.get("exp8_recompute_cos"), "exp8_direction_ok": d.get("exp8_recompute_ok")}
        q = C.RES / m / "panel_info.json"
        if q.exists():
            pi = C.jload(q)
            pm[m]["weight_cells"] = {
                "W1_energy": pi["W1"]["energy"], "W1_band": pi["W1"]["band_layers"], "W1_w": pi["W1"]["w"],
                "W2_w": pi["W2"]["w"], "W2_energy": pi["W2"]["energy"], "W2_energy_ratio_vs_W1": pi["W2"]["energy_ratio_vs_W1"],
                "W2_matched_10pct": pi["W2"]["matched_10pct"], "W3_energy": pi["W3"].get("energy"),
                "W3_label": pi["W3"].get("label"), "W3_adapter_sha256": pi["W3"].get("sha256"),
                "W4_matched": pi["W4"]["chosen"].get("matched"), "W4_energy_ratio": pi["W4"]["chosen"].get("energy_ratio"),
                "W4_dnll_ratio": pi["W4"]["chosen"].get("dnll_ratio"), "W4_n_draws": len(pi["W4"]["draws"])}
    res["per_model"] = pm
    # ---- T5 judge parse rate + label coverage
    labs = C.read_jsonl(C.RES / "labels_qwen.jsonl")
    n = len(labs)
    res["judge"] = {"n_labels": n,
                    "unparsed_share": sum(l["label"] == "unparsed" for l in labs) / n if n else None,
                    "wrong_lang_share": sum(bool(l.get("wrong_lang")) for l in labs) / n if n else None,
                    "four_way_counts": {k: sum(l["four"] == k for l in labs) for k in
                                        ("REFUSED", "PARTIAL", "COMPLIED", "INVALID", "INVALID_JUDGE")},
                    "T5_parse_pass": bool(n and sum(l["label"] == "unparsed" for l in labs) / n < 0.02)}
    gens = sum(1 for p in C.RES.glob("*/gens/*.jsonl") for _ in C.read_jsonl(p))
    res["coverage"] = {"n_generations_on_disk": gens, "n_labelled": n, "share_labelled": n / gens if gens else None}
    # ---- fallbacks that fired
    res["fallbacks_fired"] = {
        "F_J_impossible": "G-J1 and the local certification both miss kappa 0.80 and gpt-4.1 was unavailable (run OpenRouter "
                          "budget exhausted before this artifact began), so the planned judge fallback could not fire; the "
                          "Rogan-Gladen sensitivity analysis is reported instead",
        "F_M_fired": [k for k, v in frozen["per_model_lang"].items() if not v["eligible"]],
        "F_R_fired": [m for m in frozen["models"] if (C.RES / m / "panel_info.json").exists()
                      and not C.jload(C.RES / m / "panel_info.json")["W4"]["chosen"].get("matched")],
        "F_C_fired": "see results/analysis.json censoring.F_C_fires",
        "cuts_applied": C.CUTS_APPLIED,
    }
    C.jdump(res, C.RES / "checks.json")
    logger.info(f"data freeze ok={res['data_freeze']['all_ok']} split ok={res['split_overlap']['ok']} "
                f"positive control {res['positive_control_vs_exp8']['n_within']}/{res['positive_control_vs_exp8']['n']} "
                f"judge parse ok={res['judge']['T5_parse_pass']} labelled={res['coverage']['share_labelled']:.2f}")
    for m, v in pm.items():
        logger.info(f"{m}: T1={v['T1_template_suffix_ok']} T2={v['T2_hooks']['T2a_pass'] and v['T2_hooks']['T2b_pass']} "
                    f"T3={v['T3_direction']['T3_pass']} cells={'weight_cells' in v}")


if __name__ == "__main__":
    main()
