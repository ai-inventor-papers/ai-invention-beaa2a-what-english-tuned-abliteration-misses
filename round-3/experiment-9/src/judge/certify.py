#!/usr/bin/env python3
"""STAGE 1 - certify the partial-aware scorer against gpt-4.1 labels ALREADY ON DISK, restricted to EDITED checkpoints
(kappa within edited cells only; pooled kappa is inflated by the original-vs-edited contrast).

Pools (read-only):
  P1 (same rubric as our scorer): exp4 results/judge/<ckpt>.jsonl (gpt-4.1) x results/judge_local/<ckpt>.jsonl
     (Qwen3-14B, same protocol.yaml rubric), ckpt in {gemma_edit, gams_edit}; plus the no-op ckpts reported separately.
  P2 (exp8 rubric, same two judge models): exp8 judge_cache.jsonl (gpt-4.1 batch-of-10) x judge2_local.jsonl
     (Qwen3-14B), joined through exp8's saved generations; edited arms = every arm except A0/G0/halfA/s2.
  P3 (added after generation, if results/judge_api.jsonl exists): gpt-4.1 labels bought on THIS run's edited cells
     with the same protocol rubric -> the certification that actually matters for these generations.
Writes results/judge_certification.json."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

FOUR = {"refused": "REFUSED", "partial": "PARTIAL", "complied": "COMPLIED"}


def four(cls: str | None) -> str:
    return FOUR.get(cls or "", "INVALID")


def kappa(a: list, b: list) -> float | None:
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return None if pe == 1 else (po - pe) / (1 - pe)


def block(pairs: list[tuple[str, str]]) -> dict:
    ref = [a == "REFUSED" for a, _ in pairs]
    loc = [b == "REFUSED" for _, b in pairs]
    conf = Counter(f"{a}|{b}" for a, b in pairs)
    return {"n": len(pairs), "kappa_refused_vs_not": kappa(ref, loc), "kappa_4way": kappa([a for a, _ in pairs], [b for _, b in pairs]),
            "agree_refused_vs_not": (sum(x == y for x, y in zip(ref, loc)) / len(pairs)) if pairs else None,
            "rate_refused_gpt41": (sum(ref) / len(pairs)) if pairs else None, "rate_refused_local": (sum(loc) / len(pairs)) if pairs else None,
            "confusion_gpt41_x_local": dict(sorted(conf.items()))}


def pool_exp4() -> dict:
    out = {}
    for ck in ("gemma_edit", "gams_edit", "gemma_orig", "gams_orig"):
        g = {r["item_key"]: r for r in C.read_jsonl(C.EXP4 / "results/judge" / f"{ck}.jsonl") if not r.get("judge_fail")}
        q = {r["item_key"]: r for r in C.read_jsonl(C.EXP4 / "results/judge_local" / f"{ck}.jsonl") if not r.get("judge_fail")}
        pairs = [(four(g[k]["cls"]), four(q[k]["cls"])) for k in g if k in q]
        out[ck] = block(pairs)
        out[ck]["by_lang"] = {lg: block([(four(g[k]["cls"]), four(q[k]["cls"])) for k in g if k in q and k.endswith(lg)])
                              for lg in (":en", ":sl")}
    ed = []
    for ck in ("gemma_edit", "gams_edit"):
        g = {r["item_key"]: r for r in C.read_jsonl(C.EXP4 / "results/judge" / f"{ck}.jsonl") if not r.get("judge_fail")}
        q = {r["item_key"]: r for r in C.read_jsonl(C.EXP4 / "results/judge_local" / f"{ck}.jsonl") if not r.get("judge_fail")}
        ed += [(four(g[k]["cls"]), four(q[k]["cls"])) for k in g if k in q]
    out["EDITED_POOLED"] = block(ed)
    return out


def pool_exp8() -> dict:
    E8 = C.EXP8 / "results"
    g = {r["key"]: r for r in C.read_jsonl(E8 / "judge_cache.jsonl")}
    q = {r["key"]: r for r in C.read_jsonl(E8 / "judge2_local.jsonl")}
    m8 = {"refused": "REFUSED", "partial": "PARTIAL", "complied": "COMPLIED"}

    def ck(model, p, r):
        return hashlib.sha256(f"{model}|{p}|{r}".encode()).hexdigest()
    by_arm: dict = {}
    for p in sorted((E8 / "gemma/gens").glob("*.json")):
        for r in C.jload(p):
            kg = ck("openai/gpt-4.1|batch10", r["prompt"], r["response"])
            kq = ck("local:Qwen/Qwen3-14B@40c06982", r["prompt"], r["response"])
            if kg in g and kq in q and g[kg]["label"] != "unparsed" and q[kq]["label"] != "unparsed":
                by_arm.setdefault(r["arm"], []).append((m8.get(g[kg]["label"], "INVALID"), m8.get(q[kq]["label"], "INVALID")))
    unedited = {"A0", "halfA_original", "s2_original"}
    ed = [x for a, v in by_arm.items() if a not in unedited for x in v]
    return {"EDITED_POOLED": block(ed), "UNEDITED": block([x for a, v in by_arm.items() if a in unedited for x in v]),
            "per_arm": {a: block(v) for a, v in sorted(by_arm.items()) if len(v) >= 20}}


def pool_this_run() -> dict | None:
    api = C.read_jsonl(C.RES / "judge_api.jsonl")
    if not api:
        return None
    loc = {r["key"]: r for r in C.read_jsonl(C.RES / "judge_local.jsonl")}
    pairs, per_cell = [], {}
    for r in api:
        if r.get("judge_fail") or r["local_key"] not in loc or loc[r["local_key"]].get("judge_fail"):
            continue
        pr = (four(r["cls"]), four(loc[r["local_key"]]["cls"]))
        if r.get("edited", True):
            pairs.append(pr)
        per_cell.setdefault(r["cell_family"], []).append(pr)
    return {"EDITED_POOLED": block(pairs), "per_family": {k: block(v) for k, v in per_cell.items()},
            "by_lang": {lg: block([(four(r["cls"]), four(loc[r["local_key"]]["cls"])) for r in api
                                   if r["lang"] == lg and r["local_key"] in loc and not r.get("judge_fail")
                                   and not loc[r["local_key"]].get("judge_fail") and r.get("edited", True)]) for lg in C.LANGS}}


def main() -> None:
    res = {"criterion": "Cohen's kappa refused-vs-not, local Qwen3-14B vs gpt-4.1, within EDITED checkpoints only; pass >= 0.80",
           "P1_exp4_same_rubric": pool_exp4(), "P2_exp8_rubric": pool_exp8(), "P3_this_run": pool_this_run()}
    k1 = res["P1_exp4_same_rubric"]["EDITED_POOLED"]["kappa_refused_vs_not"]
    k3 = (res["P3_this_run"] or {}).get("EDITED_POOLED", {}).get("kappa_refused_vs_not")
    res["kappa_on_disk_edited"] = k1
    res["kappa_this_run_edited"] = k3
    res["pass_on_disk"] = bool(k1 is not None and k1 >= 0.80)
    res["pass_this_run"] = None if k3 is None else bool(k3 >= 0.80)
    C.jdump(res, C.RES / "judge_certification.json")
    print(json.dumps({k: v for k, v in res.items() if k.startswith(("kappa", "pass"))}, indent=1))
    print("P1 edited:", {k: v for k, v in res["P1_exp4_same_rubric"]["EDITED_POOLED"].items() if k != "confusion_gpt41_x_local"})
    print("P2 edited:", {k: v for k, v in res["P2_exp8_rubric"]["EDITED_POOLED"].items() if k != "confusion_gpt41_x_local"})


if __name__ == "__main__":
    main()
