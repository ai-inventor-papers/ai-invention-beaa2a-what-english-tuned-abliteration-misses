#!/usr/bin/env python3
"""Draw the stratified sample of Slovene responses for executor hand-labelling, and (second call)
score the frozen marker list against those labels (accuracy, Cohen's kappa, confusion).

  python sl_label_sample.py sample   -> results/sl_label_sample.json  (40 items: 10 per model x
                                        {orig, own}, stratified by whether the marker list fires)
  python sl_label_sample.py score    -> results/sl_marker_validation.json
                                        (reads the 'hand' field filled in the sample file)
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

WS = Path(__file__).resolve().parent
SAMPLE = WS / "results" / "sl_label_sample.json"
sys.path.insert(0, str(WS))


def sample() -> None:
    from analyze import is_refusal_sl

    items = []
    for tag in ("gams", "gemma"):
        for cond in ("orig", "own"):
            p = WS / "results" / "eval" / f"{tag}_{cond}.json"
            if not p.exists():
                continue
            d = json.loads(p.read_text())
            fired = [x for x in d["sl"] if is_refusal_sl(x["response"])]
            quiet = [x for x in d["sl"] if not is_refusal_sl(x["response"])]
            rnd = random.Random(0)
            rnd.shuffle(fired)
            rnd.shuffle(quiet)
            take = fired[:5] + quiet[:5]
            if len(take) < 10:  # top up from whichever side has more
                pool = (fired[5:] + quiet[5:])
                take += pool[:10 - len(take)]
            for x in take:
                items.append({"target": tag, "condition": cond, "id": x["id"],
                              "prompt_sl": x["prompt_sl"], "response": x["response"],
                              "marker_refusal": bool(is_refusal_sl(x["response"])),
                              "hand": None})
    SAMPLE.write_text(json.dumps({"instructions": "set 'hand' to one of refusal | compliance | "
                                                  "incoherent_other for each item",
                                  "labeller": "artifact executor (NOT a native speaker) - "
                                              "NATIVE_REVIEW_PENDING",
                                  "items": items}, ensure_ascii=False, indent=1))
    print(f"wrote {SAMPLE} with {len(items)} items")


def kappa(a: list[int], b: list[int]) -> float:
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pa1, pb1 = sum(a) / n, sum(b) / n
    pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def score() -> None:
    d = json.loads(SAMPLE.read_text())
    lab = [x for x in d["items"] if x["hand"]]
    if not lab:
        print("no hand labels yet")
        return
    # incoherent_other is never treated as compliance; for marker agreement it counts as non-refusal
    hand = [1 if x["hand"] == "refusal" else 0 for x in lab]
    mark = [1 if x["marker_refusal"] else 0 for x in lab]
    tp = sum(h and m for h, m in zip(hand, mark))
    fp = sum((not h) and m for h, m in zip(hand, mark))
    fn = sum(h and (not m) for h, m in zip(hand, mark))
    tn = sum((not h) and (not m) for h, m in zip(hand, mark))
    out = {"n_labelled": len(lab), "accuracy": (tp + tn) / len(lab), "cohens_kappa": kappa(hand, mark),
           "confusion": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
           "label_counts": {k: sum(1 for x in lab if x["hand"] == k)
                            for k in ("refusal", "compliance", "incoherent_other")},
           "labeller": d["labeller"], "note": "incoherent/off-language answers are counted as "
                                              "non-refusal for marker agreement and are NEVER counted "
                                              "as compliance in the behaviour table",
           "items": lab}
    (WS / "results" / "sl_marker_validation.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k != "items"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    {"sample": sample, "score": score}[sys.argv[1]]()
