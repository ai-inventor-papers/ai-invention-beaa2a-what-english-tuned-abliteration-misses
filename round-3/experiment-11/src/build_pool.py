#!/usr/bin/env python3
"""STEP 1.1 - harvest every existing judge label (prior iterations) into one table: results/label_pool.parquet.

Sources (all READ-ONLY, prior artifacts of this run):
  exp4 (art_m6pglf516e2r): results/gen/<ckpt>.jsonl text + results/judge/*.jsonl (gpt-4.1, 716) +
                           results/judge_local/*.jsonl (Qwen3-14B, 4,800) - same frozen rubric as this artifact.
  exp5 (art_a4VkEvYRquBO): results/judged_generations.jsonl (gpt-4.1 'label', 1,072 judged rows).
  exp8 (art_hmbXDppkPZnR): results/<model>/gens/*.json text + results/per_item.parquet labels with
                           label_source == 'gpt-4.1' (activation-steered arms; the 'rule' labels are NOT used).
One row per (source, generation, judge). Columns: uid, source, judge_model, ckpt, is_edited, semantic_id, lang,
prompt, text, n_chars, cls, y (1 = refused, 0 = partial/complied/irrelevant, NaN = invalid/empty/malformed).
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import pandas as pd
from loguru import logger

WS = Path(__file__).resolve().parent
RUN = Path(__file__).resolve().parents[3]
W4 = RUN / "round-2/experiment-4/src"
W5 = RUN / "round-2/experiment-5/src"
W8 = RUN / "round-2/experiment-8/src"


def read_jsonl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def y_of(cls: str | None) -> float:
    if cls == "refused":
        return 1.0
    if cls in ("partial", "complied", "irrelevant"):
        return 0.0
    return float("nan")


def exp4_rows() -> list[dict]:
    frozen = json.loads((W4 / "frozen_samples.json").read_text())
    prompts = {it["item_key"]: it["prompt"] for it in frozen["items"]}
    rows = []
    for gp in sorted((W4 / "results/gen").glob("*.jsonl")):
        ck = gp.stem
        gen = {r["item_key"]: r for r in read_jsonl(gp)}
        for jdir, jname in (("judge", "openai/gpt-4.1"), ("judge_local", "Qwen/Qwen3-14B")):
            jp = W4 / "results" / jdir / f"{ck}.jsonl"
            if not jp.exists():
                continue
            last = {}
            for r in read_jsonl(jp):
                last[r["item_key"]] = r  # later rows (retries) supersede
            for k, j in last.items():
                if j.get("judge_fail") or k not in gen:
                    continue
                g = gen[k]
                rows.append({"uid": f"exp4|{ck}|{k}", "source": "exp4", "judge_model": jname, "ckpt": ck,
                             "is_edited": ck.endswith("edit") or ck == "community_ref",
                             "model": ck.split("_")[0], "semantic_id": g.get("semantic_id", k), "lang": g["lang"],
                             "set": g.get("set"), "prompt": prompts.get(k, ""), "text": g["response_text"],
                             "hit_max": bool(g.get("hit_max")), "cls": j["cls"]})
    return rows


def exp5_rows() -> list[dict]:
    rows = []
    for r in read_jsonl(W5 / "results/judged_generations.jsonl"):
        if r.get("label") in (None, "NOT_JUDGED"):
            continue
        sem = r["key"].split("|")[3] if r["key"].count("|") >= 4 else r["key"]
        rows.append({"uid": f"exp5|{r['key']}", "source": "exp5", "judge_model": "openai/gpt-4.1",
                     "ckpt": f"{r['model']}_{r['ckpt']}", "is_edited": r["ckpt"] != "orig", "model": r["model"],
                     "semantic_id": sem, "lang": r["lang"], "set": r["kind"], "prompt": r["prompt"],
                     "text": r["response"], "hit_max": None, "cls": r["label"]})
    return rows


def exp8_rows() -> list[dict]:
    lab = pd.read_parquet(W8 / "results/per_item.parquet")
    lab = lab[lab["label_source"] == "gpt-4.1"].set_index("gid")
    rows = []
    for f in sorted(glob.glob(str(W8 / "results/*/gens/*.json"))):
        for g in json.loads(Path(f).read_text()):
            gid = g.get("gid")
            if gid not in lab.index:
                continue
            L = lab.loc[gid]
            if isinstance(L, pd.DataFrame):
                L = L.iloc[0]
            arm = g.get("arm", "")
            orig = ("original" in arm) or arm in ("A0", "G0", "C0", "W0")
            rows.append({"uid": f"exp8|{gid}", "source": "exp8", "judge_model": "openai/gpt-4.1",
                         "ckpt": f"{g['model']}_{arm}", "is_edited": not orig, "model": g["model"],
                         "semantic_id": g.get("semantic_id", gid), "lang": g["lang"], "set": g.get("kind"),
                         "prompt": g.get("prompt", ""), "text": g.get("response", ""), "hit_max": None,
                         "cls": L["label"]})
    return rows


def main() -> None:
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    parts = []
    for fn in (exp4_rows, exp5_rows, exp8_rows):
        try:
            r = fn()
            logger.info(f"{fn.__name__}: {len(r)} labelled rows")
            parts += r
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            logger.error(f"{fn.__name__} failed: {e!r}")
            raise
    df = pd.DataFrame(parts)
    df["text"] = df["text"].fillna("")
    df["y"] = df["cls"].map(y_of)
    df["n_chars"] = df["text"].str.len()
    out = WS / "results/label_pool.parquet"
    out.parent.mkdir(exist_ok=True)
    df.to_parquet(out, index=False)
    logger.info(f"pool: {len(df)} rows -> {out}")
    logger.info("\n" + df.groupby(["source", "judge_model", "is_edited"])["y"].agg(["size", "mean"]).to_string())
    logger.info("\n" + df["cls"].value_counts().to_string())


if __name__ == "__main__":
    main()
