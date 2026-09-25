#!/usr/bin/env python3
"""Build the 24-token R_seq references per (model, S4 item, language) from generations + labels (spec):
  ref_refuse(i,l) = first 24 tokens of THIS model's ORIGINAL gen if labelled 'refused', else the per-(model, language)
                    canonical refusal opener (most frequent 8-token prefix among this model's refused ORIGINAL outputs,
                    extended to 24 tokens with the first output that has it); fallback: pooled over languages
  ref_comply(i,l) = first 24 tokens of the GaMS CORE EDIT gen on item i if labelled 'complied' (spec: used for BOTH
                    models; identical tokenizer.json sha256), else THIS model's ORIGINAL gen if 'complied' (fallback 1),
                    else the per-language canonical compliance opener mined from GaMS-edit 'complied' outputs (fallback 2)
Label source = judge (gpt-4.1) when judged labels exist, else Heretic+SL keyword markers ('markers', flagged unjudged).
Usage: .venv/bin/python readouts.py --source judge|markers"""
from __future__ import annotations

import argparse
import json
from collections import Counter

from loguru import logger

import common as C
from common import jdump, jload, setup_logging

N_REF = C.GEN["ref_tokens"]
LABEL_STATS: dict = {}


def labels_for(source: str, root=C.RES) -> dict:
    """(model, ckpt, kind, semantic_id, lang) -> label."""
    lab = {}
    if source == "judge":
        lab = labels_for("markers", root)  # unjudged items (e.g. priority-4 harmless) keep their marker label (counted)
        judged = 0
        for o in jload(root / "judge" / "judged_generations.json"):
            if o["label"] not in ("NOT_JUDGED", "unparsed"):
                m, ck, kind, sid, lang = o["key"].split("|")
                lab[(m, ck, kind, sid, lang)] = o["label"]
                judged += 1
        LABEL_STATS["judged"], LABEL_STATS["marker_fallback"] = judged, len(lab) - judged
    else:
        for m in C.MODELS:
            p = root / "gens" / f"{m}_gens.json"
            if not p.exists():
                continue
            for g in jload(p):
                t = g["response"]
                l = "empty" if not t.strip() else ("malformed" if C.malformed_rule(t) else ("refused" if C.keyword_refusal(t) else "complied"))
                lab[(m, g["ckpt"], g["kind"], g["semantic_id"], g["lang"])] = l
    return lab


def canonical(outputs: list[list[int]]) -> list[int] | None:
    outs = [o for o in outputs if len(o) >= N_REF]
    if not outs:
        return None
    c = Counter(tuple(o[:8]) for o in outs).most_common(1)[0][0]
    return next(o[:N_REF] for o in outs if tuple(o[:8]) == c)


def build(source: str, root=C.RES) -> None:
    lab = labels_for(source, root)
    gens = {m: jload(root / "gens" / f"{m}_gens.json") for m in C.MODELS if (root / "gens" / f"{m}_gens.json").exists()}
    assert "gams" in gens, "GaMS generations are required (compliance references come from the GaMS core edit)"
    G = {m: {(g["ckpt"], g["kind"], g["semantic_id"], g["lang"]): g for g in gl} for m, gl in gens.items()}
    # canonical compliance per language from GaMS edit 'complied' outputs (both roles)
    can_comply = {}
    for lang in C.LANGS:
        outs = [g["gen_ids"] for g in gens["gams"] if g["ckpt"] == "edit" and g["kind"].startswith("s4") and g["lang"] == lang
                and lab.get(("gams", "edit", g["kind"], g["semantic_id"], lang)) == "complied"]
        can_comply[lang] = canonical(outs)
    for m, gl in gens.items():
        can_refuse = {}
        for lang in C.LANGS:
            outs = [g["gen_ids"] for g in gl if g["ckpt"] == "orig" and g["lang"] == lang
                    and lab.get((m, "orig", g["kind"], g["semantic_id"], lang)) == "refused"]
            can_refuse[lang] = canonical(outs)
        pooled_ref = canonical([g["gen_ids"] for g in gl if g["ckpt"] == "orig" and lab.get((m, "orig", g["kind"], g["semantic_id"], g["lang"])) == "refused"])
        pooled_comp = canonical([g["gen_ids"] for g in gens["gams"] if g["ckpt"] == "edit" and lab.get(("gams", "edit", g["kind"], g["semantic_id"], g["lang"])) == "complied"])
        rows, use = [], Counter()
        for (ck, kind, sid, lang), g in sorted(G[m].items()):
            if ck != "orig" or not kind.startswith("s4"):
                continue
            role = g["role"]
            own = g["gen_ids"]
            if lab.get((m, "orig", kind, sid, lang)) == "refused" and len(own) >= N_REF:
                rr, src_r = own[:N_REF], "own_orig"
            elif can_refuse[lang] is not None:
                rr, src_r = can_refuse[lang], "canonical_lang"
            else:
                rr, src_r = pooled_ref, "canonical_pooled"
            ge = G["gams"].get(("edit", kind, sid, lang))
            if ge is not None and lab.get(("gams", "edit", kind, sid, lang)) == "complied" and len(ge["gen_ids"]) >= N_REF:
                rc, src_c = ge["gen_ids"][:N_REF], "gams_edit"
            elif lab.get((m, "orig", kind, sid, lang)) == "complied" and len(own) >= N_REF:
                rc, src_c = own[:N_REF], "fallback1_own_orig"
            elif can_comply[lang] is not None:
                rc, src_c = can_comply[lang], "fallback2_canonical_lang"
            else:
                rc, src_c = pooled_comp, "fallback3_canonical_pooled"
            assert rr is not None and rc is not None and len(rr) == N_REF and len(rc) == N_REF
            use[(lang, role, "refuse", src_r)] += 1
            use[(lang, role, "comply", src_c)] += 1
            rows.append({"semantic_id": sid, "lang": lang, "role": role, "ref_refuse": rr, "ref_comply": rc, "src_refuse": src_r, "src_comply": src_c})
        p = root / "refs" / f"refs_{m}.jsonl"
        txt = "\n".join(json.dumps(r) for r in rows)
        p.write_text(txt)
        meta = {"label_source": source, "label_stats": dict(LABEL_STATS), "sha256": C.text_sha256(txt), "n": len(rows), "n_tokens": N_REF,
                "fallback_counts": {"|".join(k): v for k, v in sorted(use.items())},
                "canonical_refusal_text": {l: None if can_refuse[l] is None else _dec(can_refuse[l]) for l in C.LANGS},
                "canonical_compliance_text": {l: None if can_comply[l] is None else _dec(can_comply[l]) for l in C.LANGS}}
        jdump(meta, root / "refs" / f"refs_{m}.meta.json")
        logger.info(f"refs {m} ({source}): {len(rows)} rows; fallbacks {dict(use)}")


_TOK = None


def _dec(ids: list[int]) -> str:
    global _TOK
    if _TOK is None:
        from transformers import AutoTokenizer

        _TOK = AutoTokenizer.from_pretrained(C.MODELS["gams"]["repo"], revision=C.MODELS["gams"]["sha"])
    return _TOK.decode(ids)


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["judge", "markers"], required=True)
    args = ap.parse_args()
    setup_logging("readouts")
    build(args.source)


if __name__ == "__main__":
    main()
