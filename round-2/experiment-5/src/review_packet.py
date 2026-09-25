#!/usr/bin/env python3
"""Blinded EN/SL native-review packet (120 rows, status PENDING) + per-item utility export.

Packet: stratified over model x checkpoint x language x role (S4 generations), 7-8 rows per cell, neutral ids, rows
shuffled; the model/checkpoint key and the gpt-4.1 labels live in a SEPARATE key file (never shown to reviewers).
Also writes results/utility_items.parquet (one row per item x task x checkpoint x language x model) and
results/judged_generations.jsonl (one judged generation per line).
Usage: .venv/bin/python review_packet.py"""
from __future__ import annotations

import csv
import hashlib
import json

import numpy as np
import pandas as pd
from loguru import logger

import common as C
from common import MODELS, jload, setup_logging

N_PACKET = 120


def packet() -> None:
    jp = C.RES / "judge" / "judged_generations.json"
    judged = {o["key"]: o for o in jload(jp)} if jp.exists() else {}
    cells: dict = {}
    for m in MODELS:
        p = C.RES / "gens" / f"{m}_gens.json"
        if not p.exists():
            continue
        for g in jload(p):
            if not g["kind"].startswith("s4"):
                continue
            cells.setdefault((m, g["ckpt"], g["lang"], g["role"]), []).append(g)
    keys = sorted(cells)
    per = int(np.ceil(N_PACKET / max(len(keys), 1)))
    rng = np.random.default_rng(C.SEED)
    rows = []
    for k in keys:
        gl = sorted(cells[k], key=lambda g: g["semantic_id"])
        for i in rng.choice(len(gl), size=min(per, len(gl)), replace=False):
            rows.append(gl[int(i)])
    rows = [rows[i] for i in rng.permutation(len(rows))][:N_PACKET]
    pk, key = [], []
    for g in rows:
        full = f"{g['model']}|{g['ckpt']}|{g['kind']}|{g['semantic_id']}|{g['lang']}"
        rid = "r" + hashlib.sha1(f"review|{full}".encode()).hexdigest()[:8]
        pk.append({"review_id": rid, "language": g["lang"], "request": g["prompt"], "reply": g["response"],
                   "reviewer_label(refused|complied|partial|irrelevant|malformed|empty)": "", "reply_language_ok(y/n)": "",
                   "translation_of_request_faithful(y/n/NA)": "", "notes": "", "status": "PENDING"})
        j = judged.get(full, {})
        key.append({"review_id": rid, "key": full, "gpt41_label": j.get("label", "NOT_JUDGED"), "marker_refusal": C.keyword_refusal(g["response"])})
    out = C.RES / "native_review_packet_c1u.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(pk[0]))
        w.writeheader()
        w.writerows(pk)
    with open(C.RES / "native_review_packet_c1u_KEY.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(key[0]))
        w.writeheader()
        w.writerows(key)
    logger.info(f"review packet: {len(pk)} rows ({per}/cell over {len(keys)} cells), status PENDING")


def utility_items() -> None:
    rows = []
    for m in MODELS:
        for ck in ("orig", "edit"):
            p = C.RES / m / f"utility_{ck}.json"
            if not p.exists():
                continue
            for r in jload(p):
                rows.append({"model": m, "ckpt": ck, "task": r["task"], "lang": r["lang"], "semantic_id": r["semantic_id"],
                             "gold": int(r["gold"]), "acc": int(r["acc"]), "acc_norm": int(r["acc_norm"]),
                             "pred_acc": int(r["pred_acc"]), "pred_acc_norm": int(r["pred_acc_norm"]),
                             "ll": json.dumps([float(x) for x in r["ll"]]), "norm_len": json.dumps(r.get("norm_len"))})
    if rows:
        pd.DataFrame(rows).to_parquet(C.RES / "utility_items.parquet")
        logger.info(f"utility_items.parquet: {len(rows)} rows")


def judged_jsonl() -> None:
    jp = C.RES / "judge" / "judged_generations.json"
    if not jp.exists():
        return
    with open(C.RES / "judged_generations.jsonl", "w") as f:
        for o in jload(jp):
            f.write(json.dumps(o, ensure_ascii=False) + "\n")


@logger.catch(reraise=True)
def main() -> None:
    setup_logging("review_packet")
    packet()
    utility_items()
    judged_jsonl()


if __name__ == "__main__":
    main()
