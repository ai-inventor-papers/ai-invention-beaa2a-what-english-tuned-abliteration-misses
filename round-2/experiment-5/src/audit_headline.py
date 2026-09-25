#!/usr/bin/env python3
"""Independent re-derivation of the behaviour / judge / dose headline numbers from RAW files (a different code path from
analyze.py): judge labels parsed from results/judge/raw_calls.jsonl with a fresh regex, keys rebuilt from the generation
files with sha1 (no judge.py import), rates and kappa by plain counting; dose R_seq>0 shares from the per-item arrays;
utility macro deltas from results/utility_items.parquet. Placebos: labels shuffled across checkpoints (orig vs edit refusal
difference must vanish) and kappa with one judge's labels permuted (must be ~0). Writes results/audit_headline.json."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
RES = ROOT / "results"
SEED = 20260923


def kappa(a, b) -> float:
    a, b = np.asarray(a), np.asarray(b)
    cats = sorted(set(a) | set(b))
    po = float(np.mean(a == b))
    pe = sum(float(np.mean(a == c)) * float(np.mean(b == c)) for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def main() -> None:
    raw = {"openai/gpt-4.1": {}, "nvidia/nemotron-3-ultra-550b-a55b:free": {}}
    for line in (RES / "judge" / "raw_calls.jsonl").read_text().splitlines():
        r = json.loads(line)
        if r.get("model") in raw and r.get("out"):
            m = re.search(r'label"\s*:\s*"(\w+)"', r["out"])
            if m:
                raw[r["model"]][r["judge_id"]] = m.group(1)
    rows = []
    for mdl in ("gams", "gemma"):
        for g in json.loads((RES / "gens" / f"{mdl}_gens.json").read_text()):
            key = f"{g['model']}|{g['ckpt']}|{g['kind']}|{g['semantic_id']}|{g['lang']}"
            jid = "j" + hashlib.sha1(f"{SEED}|{key}".encode()).hexdigest()[:10]
            rows.append({"model": mdl, "ckpt": g["ckpt"], "kind": g["kind"], "lang": g["lang"], "sid": g["semantic_id"],
                         "j1": raw["openai/gpt-4.1"].get(jid), "j2": raw["nvidia/nemotron-3-ultra-550b-a55b:free"].get(jid)})
    df = pd.DataFrame(rows)
    out = {"refusal_rates_gpt41": {}, "complied_rates_gpt41": {}}
    h = df[(df.kind == "s4_harmful") & df.j1.notna()]
    for (m, ck, lang), d in h.groupby(["model", "ckpt", "lang"]):
        out["refusal_rates_gpt41"][f"{m}|{ck}|{lang}"] = {"n": int(len(d)), "refused": float((d.j1 == "refused").mean())}
        out["complied_rates_gpt41"][f"{m}|{ck}|{lang}"] = float((d.j1 == "complied").mean())
    # kappa on the items labelled by both judges (the stratified sample)
    both = df[df.j1.notna() & df.j2.notna()]
    out["kappa_6way"] = kappa(both.j1.values, both.j2.values)
    out["kappa_refused"] = kappa((both.j1 == "refused").values, (both.j2 == "refused").values)
    out["n_both"] = int(len(both))
    rng = np.random.default_rng(1)
    out["placebo_kappa_refused_permuted"] = kappa((both.j1 == "refused").values, rng.permutation((both.j2 == "refused").values))
    # placebo: shuffle checkpoint labels within model x language -> orig-edit refusal gap should vanish
    plc = {}
    for (m, lang), d in h.groupby(["model", "lang"]):
        y = (d.j1 == "refused").values
        ck = rng.permutation(d.ckpt.values)
        plc[f"{m}|{lang}"] = {"true_gap": float(y[d.ckpt.values == "orig"].mean() - y[d.ckpt.values == "edit"].mean()),
                              "shuffled_gap": float(y[ck == "orig"].mean() - y[ck == "edit"].mean())}
    out["placebo_ckpt_shuffle"] = plc
    # dose: share of harmful prompts with R_seq > 0 from per-item arrays
    dose = {}
    for m in ("gams", "gemma"):
        d = json.loads((RES / "dose" / f"dose_{m}.json").read_text())
        items = pd.DataFrame(d["items"])
        for f, R in d["items_R_seq"].items():
            R = np.asarray(R)
            for lang in ("en", "sl"):
                mk = ((items.lang == lang) & (items.role == "harmful")).values
                dose[f"{m}|{f}|{lang}"] = float((R[mk] > 0).mean())
    out["dose_Rseq_pos_harmful"] = dose
    # utility macro delta from the per-item parquet (metric per task), plain means
    u = pd.read_parquet(RES / "utility_items.parquet")
    metric = {"arc_challenge": "acc_norm", "hellaswag": "acc_norm", "openbookqa": "acc_norm", "piqa": "acc_norm", "boolq": "acc", "winogrande": "acc"}
    u["score"] = [r[metric[t]] for t, r in zip(u.task, u.to_dict("records"))]
    mac = {}
    for (m, lang), d in u.groupby(["model", "lang"]):
        per = d.groupby(["task", "ckpt"]).score.mean().unstack()
        mac[f"{m}|{lang}"] = float((per["edit"] - per["orig"]).mean())
    out["utility_macro_delta"] = mac
    (RES / "audit_headline.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1)[:3000])


if __name__ == "__main__":
    main()
