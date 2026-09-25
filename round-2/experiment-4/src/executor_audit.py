#!/usr/bin/env python3
"""Stage F executor audit (EXECUTOR CHECK, not human review): 30 EN FINAL items stratified across the primary judge's
classes (all checkpoints pooled), read by the executing agent BLIND to the judge label and to the checkpoint.

  python executor_audit.py sample   -> results/executor_audit_sample.json   (item_id, prompt, response; no labels/ckpt)
  python executor_audit.py score    <- results/executor_audit_labels.json   ({item_id: {"cls": ..., "unsafe": bool}})
                                    -> results/executor_audit.json          (agreement with gpt-4.1)"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict

import numpy as np

from common import ALL_CKPTS, WS, read_jsonl
from stats_lib import cohen_kappa

SAMPLE = WS / "results/executor_audit_sample.json"
KEY = WS / "results/executor_audit_key.json"
LABELS = WS / "results/executor_audit_labels.json"
N = 30


def sample() -> None:
    frozen = json.loads((WS / "frozen_samples.json").read_text())
    items = {it["item_key"]: it for it in frozen["items"]}
    strata = defaultdict(list)
    gen = {}
    for ck in ALL_CKPTS:
        p = WS / "results/gen" / f"{ck}.jsonl"
        if p.exists():
            gen |= {(ck, r["item_key"]): r for r in read_jsonl(p)}
        p = WS / "results/judge" / f"{ck}.jsonl"
        if p.exists():
            for r in read_jsonl(p):
                if not r.get("judge_fail") and items[r["item_key"]]["lang"] == "en" and r["cls"] != "empty":
                    strata[r["cls"]].append((ck, r["item_key"]))
    rng = np.random.default_rng(20260928)
    classes = sorted(strata)
    quota = {c: N // len(classes) for c in classes}
    for c in sorted(classes, key=lambda c: -len(strata[c]))[: N - sum(quota.values())]:
        quota[c] += 1
    pick = []
    for c in classes:
        pool = sorted(set(strata[c]))
        n = min(quota[c], len(pool))
        pick += [pool[i] for i in rng.choice(len(pool), size=n, replace=False)]
    if len(pick) < N:  # fill from the biggest classes
        rest = sorted({x for c in classes for x in strata[c]} - set(pick))
        pick += [rest[i] for i in rng.choice(len(rest), size=N - len(pick), replace=False)]
    rng.shuffle(pick)
    samp, key = [], {}
    for i, (ck, ik) in enumerate(pick):
        iid = f"ea{i:02d}"
        g = gen[(ck, ik)]
        samp.append({"item_id": iid, "set": items[ik]["set"], "prompt": items[ik]["prompt"],
                     "response": g["response_text"] + ("\n[TRUNCATED AT 256 TOKENS]" if g["hit_max"] else "")})
        key[iid] = {"ckpt": ck, "item_key": ik}
    SAMPLE.write_text(json.dumps(samp, indent=1, ensure_ascii=False))
    KEY.write_text(json.dumps(key, indent=1))
    print(f"wrote {len(samp)} items; class quota {quota}")


def score() -> None:
    key = json.loads(KEY.read_text())
    mine = json.loads(LABELS.read_text())
    J = {}
    for ck in ALL_CKPTS:
        p = WS / "results/judge" / f"{ck}.jsonl"
        if p.exists():
            J |= {(ck, r["item_key"]): r for r in read_jsonl(p) if not r.get("judge_fail")}
    rows = []
    for iid, k in key.items():
        j = J[(k["ckpt"], k["item_key"])]
        m = mine[iid]
        rows.append({"item_id": iid, "ckpt": k["ckpt"], "item_key": k["item_key"], "judge_cls": j["cls"], "exec_cls": m["cls"],
                     "judge_unsafe": j["safety"] == "unsafe", "exec_unsafe": bool(m["unsafe"]), "exec_note": m.get("note", "")})
    ref = lambda c: c == "refused"  # noqa: E731
    out = {"label": "EXECUTOR CHECK (the executing agent, blind to judge label and checkpoint) - NOT human review",
           "n": len(rows),
           "agreement_5way": float(np.mean([r["judge_cls"] == r["exec_cls"] for r in rows])),
           "kappa_5way": cohen_kappa([r["judge_cls"] for r in rows], [r["exec_cls"] for r in rows]),
           "agreement_refused_vs_not": float(np.mean([ref(r["judge_cls"]) == ref(r["exec_cls"]) for r in rows])),
           "agreement_safe_unsafe": float(np.mean([r["judge_unsafe"] == r["exec_unsafe"] for r in rows])),
           "judge_class_counts": dict(Counter(r["judge_cls"] for r in rows)),
           "disagreements": [r for r in rows if r["judge_cls"] != r["exec_cls"] or r["judge_unsafe"] != r["exec_unsafe"]],
           "rows": rows}
    (WS / "results/executor_audit.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(json.dumps({k: out[k] for k in ("n", "agreement_5way", "kappa_5way", "agreement_refused_vs_not", "agreement_safe_unsafe")}))


if __name__ == "__main__":
    {"sample": sample, "score": score}[sys.argv[1]]()
