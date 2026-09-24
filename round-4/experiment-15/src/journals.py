#!/usr/bin/env python3
"""STAGE S1 - parse BOTH iteration-1 Optuna journals two ways and run GATE G1 (paired startup draws).

Path 1: the JournalStorage log is parsed DIRECTLY as jsonl (op 4 = create trial, 5 = set param, 6 = set state/values,
        8 = set trial user attr, 2 = set study user attr).
Path 2: optuna.storages.JournalStorage opens a COPY of the same file; (trial -> params, values) must be identical.

Outputs: results/journal_trials.csv, results/journal_settings_{gams,gemma}.json, results/s1_journals.json
"""
from __future__ import annotations

import json
import math
import shutil

import pandas as pd
from loguru import logger

from common import J_GAMS, J_GEMMA, N_STARTUP, RESULTS, WS, setup_logging, write_json

MUST_AGREE = ["seed", "n_startup_trials", "batch_size", "max_response_length", "response_prefix", "quantization",
              "orthogonalize_direction", "row_normalization", "full_normalization_lora_rank", "winsorization_quantile",
              "system_prompt", "good_prompts", "bad_prompts", "scorers", "dtypes"]


def parse_raw(path) -> tuple[dict, dict]:
    """Returns (settings dict, {trial_number: {...}}) by reading the journal ops directly."""
    settings = None
    trials: dict[int, dict] = {}
    tid2num: dict[int, int] = {}
    for line in open(path):
        d = json.loads(line)
        op = d["op_code"]
        if op == 2 and "settings" in (d.get("user_attr") or {}):
            settings = json.loads(d["user_attr"]["settings"])
        elif op == 4:
            num = len(tid2num)
            tid2num[num] = num  # trial_id == creation order in a single-study journal
            trials[num] = {"number": num, "params": {}, "values": None, "state": None, "user_attrs": {}}
        elif op == 5:
            t = trials[tid2num[d["trial_id"]]]
            dist = json.loads(d["distribution"])
            v = d["param_value_internal"]
            if dist["name"] == "CategoricalDistribution":
                v = dist["attributes"]["choices"][int(v)]
            elif dist["name"] == "IntDistribution":
                v = int(v)
            t["params"][d["param_name"]] = v
        elif op == 6:
            t = trials[tid2num[d["trial_id"]]]
            t["state"] = {0: "RUNNING", 1: "COMPLETE", 2: "PRUNED", 3: "FAIL", 4: "WAITING"}[d["state"]]
            if d.get("values") is not None:
                t["values"] = list(d["values"])
        elif op == 8:
            trials[tid2num[d["trial_id"]]]["user_attrs"].update(d["user_attr"])
    return settings, trials


def parse_optuna(path) -> dict | None:
    try:
        import optuna
        from optuna.storages import JournalStorage
        from optuna.storages.journal import JournalFileBackend
    except ImportError:
        logger.warning("optuna not importable - optuna cross-check skipped")
        return None
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    cp = WS / "inputs" / ("optuna_copy_" + path.name)
    cp.parent.mkdir(exist_ok=True)
    shutil.copy2(path, cp)
    st = optuna.load_study(study_name="heretic", storage=JournalStorage(JournalFileBackend(str(cp))))
    out = {t.number: {"params": dict(t.params), "values": list(t.values) if t.values else None,
                      "state": t.state.name} for t in st.trials}
    cp.unlink()
    lock = cp.with_suffix(cp.suffix + ".lock")
    if lock.exists():
        lock.unlink()
    return out


def close(a, b, rtol=1e-9) -> bool:
    if isinstance(a, float) or isinstance(b, float):
        return math.isclose(float(a), float(b), rel_tol=rtol, abs_tol=1e-12)
    return a == b


@logger.catch(reraise=True)
def main() -> None:
    setup_logging("s1_journals")
    rows, report = [], {"stage": "S1"}
    parsed = {}
    for tag, path in (("gams", J_GAMS), ("gemma", J_GEMMA)):
        settings, trials = parse_raw(path)
        parsed[tag] = (settings, trials)
        write_json(RESULTS / f"journal_settings_{tag}.json", settings)
        n_complete = sum(t["state"] == "COMPLETE" for t in trials.values())
        # objective_0 * 100 must be an integer count
        bad_int = [n for n, t in trials.items() if t["values"] and abs(t["values"][0] * 100 - round(t["values"][0] * 100)) > 1e-6]
        opt = parse_optuna(path)
        agree = None
        if opt is not None:
            agree = all(opt[n]["params"] == trials[n]["params"] and opt[n]["values"] == trials[n]["values"]
                        and opt[n]["state"] == trials[n]["state"] for n in trials) and set(opt) == set(trials)
        report[tag] = {"journal": str(path.relative_to(WS.parents[2])), "n_trials": len(trials),
                       "n_complete": n_complete, "non_integer_counts": bad_int,
                       "raw_vs_optuna_identical": agree, "model": settings["model"],
                       "model_commit": settings.get("model_commit")}
        logger.info(f"{tag}: {len(trials)} trials, {n_complete} complete, raw==optuna: {agree}, non-int counts: {bad_int}")
        for n, t in sorted(trials.items()):
            if t["state"] != "COMPLETE":
                continue
            rows.append({"model": tag, "trial": n, "phase": "startup" if n < N_STARTUP else "tpe",
                         "keyword_count": int(round(t["values"][0] * 100)), "kl": float(t["values"][1]),
                         "direction_scope": t["params"].get("direction_scope"),
                         "direction_index": t["user_attrs"].get("direction_index"),
                         "params_json": json.dumps(t["params"], sort_keys=True),
                         "abl_params_json": json.dumps(t["user_attrs"].get("parameters"), sort_keys=True)})
    # settings agreement
    sg, se = parsed["gams"][0], parsed["gemma"][0]
    diffs = {k: (sg.get(k), se.get(k)) for k in MUST_AGREE if sg.get(k) != se.get(k)}
    report["settings_disagreements"] = diffs
    report["settings_expected"] = {"seed": sg["seed"] == 20260923, "n_startup_trials": sg["n_startup_trials"] == 60,
                                   "max_response_length": sg["max_response_length"] == 100,
                                   "bad_prompts": sg["bad_prompts"]["dataset"] == "mlabonne/harmful_behaviors"
                                   and sg["bad_prompts"]["commit"].startswith("01cead01")}
    # GATE G1
    tg, te = parsed["gams"][1], parsed["gemma"][1]
    ident, per = [], []
    for n in range(N_STARTUP):
        pg, pe = tg[n]["params"], te[n]["params"]
        ok = set(pg) == set(pe) and all(close(pg[k], pe[k]) for k in pg)
        ag, ae = tg[n]["user_attrs"].get("parameters"), te[n]["user_attrs"].get("parameters")
        per.append({"trial": n, "params_identical": ok, "abl_params_identical": ag == ae})
        if ok:
            ident.append(n)
    n_id = len(ident)
    design = "paired_60" if n_id == 60 else ("paired_subset" if n_id >= 50 else "unpaired_116")
    report["G1"] = {"n_identical_startup_param_vectors": n_id, "rtol": 1e-9, "identical_trials": ident,
                    "n_abl_params_identical": sum(p["abl_params_identical"] for p in per),
                    "design": design, "pass": n_id == 60}
    # TPE draws must differ (sanity: the two searches diverge after startup)
    report["tpe_param_vectors_identical"] = sum(
        1 for n in range(N_STARTUP, 116) if n in tg and n in te and tg[n]["params"] == te[n]["params"])
    logger.info(f"G1: {n_id}/60 identical startup parameter vectors -> design {design}; "
                f"TPE identical: {report['tpe_param_vectors_identical']}")
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / "journal_trials.csv", index=False)
    for tag in ("gams", "gemma"):
        d = df[df.model == tag]
        report[tag]["keyword_count_range"] = [int(d.keyword_count.min()), int(d.keyword_count.max())]
        report[tag]["keyword_count_range_startup"] = [int(d[d.phase == "startup"].keyword_count.min()),
                                                      int(d[d.phase == "startup"].keyword_count.max())]
    write_json(RESULTS / "s1_journals.json", report)
    logger.info(json.dumps({k: report[k] for k in ("G1", "settings_disagreements")}, default=str)[:800])


if __name__ == "__main__":
    main()
