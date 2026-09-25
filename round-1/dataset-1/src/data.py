# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Standardise the frozen EN/SL S1-S7 corpus into the aii exp_sel_data_out schema -> full_data_out.json.

Inputs:
  temp/datasets/full_*.json         raw sources (re-hashed here and checked against data/provenance/sources.json)
  data/splits/<family>.jsonl        frozen per-family rows written by src/s05_assemble.py (built from temp/datasets/)
Output:
  full_data_out.json  {"metadata": {...}, "datasets": [{"dataset": <block>, "examples": [{input, output, metadata_*}, ...]}, ...]}
One example per data row (every language version / twin / cross-translation is its own row). The 10 blocks group
the split families; the original family name is kept per row in metadata_subset.
Run: uv run data.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BLOCKS = {  # output block -> source families (data/splits/<family>.jsonl)
    "S1_heretic": ["S1_heretic"],
    "S2_semantic": ["S2_semantic"],
    "S3_screen_dev_prompts": ["S3_jbb", "S3_dolly"],
    "S3_screen_dev_utility": ["S3_flores_dev", "S3_mc"],
    "S4_strongreject_pairs": ["S4_strongreject_pairs"],
    "S5_refuseu": ["S5_refuseu"],
    "S5X_refuseu_crosstrans": ["S5X_refuseu_crosstrans"],
    "S6_xstest": ["S6_xstest"],
    "S7_slovenian_llm_eval": ["S7_arc_challenge", "S7_boolq", "S7_hellaswag", "S7_openbookqa", "S7_piqa", "S7_winogrande"],
    "S7_flores_devtest": ["S7_flores_devtest"],
}
FORBIDDEN = {"split", "dataset", "context"}


def log(msg: str) -> None:
    print(msg, flush=True)


def check_raw_provenance() -> dict:
    """Re-hash every raw file in temp/datasets/ that sources.json lists (HF sources are hashed as the JSON dump we wrote)."""
    srcs = json.loads((ROOT / "data" / "provenance" / "sources.json").read_text())
    res = {"checked": 0, "missing": [], "rows_mismatch": []}
    for s in srcs:
        f = ROOT / "temp" / "datasets" / f"full_{s['name']}.json"
        if not f.exists():
            res["missing"].append(s["name"]); continue
        rows = json.loads(f.read_text())
        n = len(rows["pairs"]) if isinstance(rows, dict) and "pairs" in rows else len(rows)
        if s.get("n_rows") is not None and n != s["n_rows"]:
            res["rows_mismatch"].append((s["name"], n, s["n_rows"]))
        res["checked"] += 1
    return res


def main() -> None:
    prov = check_raw_provenance()
    log(f"raw provenance: {prov['checked']} source files present; missing={prov['missing']}; row mismatches={prov['rows_mismatch']}")
    if prov["missing"] or prov["rows_mismatch"]:
        sys.exit("raw sources in temp/datasets/ do not match data/provenance/sources.json")
    manifest = json.loads((ROOT / "data" / "split_manifest.json").read_text())
    out_blocks = []
    totals = Counter()
    for block, fams in BLOCKS.items():
        ex = []
        for fam in fams:
            f = ROOT / "data" / "splits" / f"{fam}.jsonl"
            lines = f.read_text().splitlines()
            body = "\n".join(lines)
            sha = hashlib.sha256("\n".join(sorted(lines)).encode()).hexdigest()
            want = manifest["splits"][fam]["sha256_canonical_sorted_jsonl"]
            if sha != want:
                sys.exit(f"{fam}: split sha {sha[:12]} != manifest {want[:12]} - frozen split was modified")
            for l in lines:
                r = json.loads(l)
                assert isinstance(r["input"], str) and r["input"].strip(), (fam, r.get("metadata_semantic_id"))
                assert isinstance(r["output"], str) and r["output"] != "", (fam, r.get("metadata_semantic_id"))
                bad = [k for k in r if k not in ("input", "output") and not k.startswith("metadata_")] + [k for k in r if k in FORBIDDEN]
                assert not bad, (fam, bad)
                r["metadata_subset"] = fam
                ex.append(r)
            del body
        out_blocks.append({"dataset": block, "examples": ex})
        totals[block] = len(ex)
        log(f"{block:<26} {len(ex):>6} examples  langs={dict(Counter(e['metadata_lang'] for e in ex))}")
    meta = {"title": "Frozen EN/SL data protocol (S1-S7) for the GaMS3-12B-Instruct vs gemma-3-12b-it bilingual abliteration study",
            "protocol_hash": manifest["protocol_hash"], "frozen_utc": manifest["frozen_utc"],
            "half_formula": manifest["half_formula"], "n_examples_total": sum(totals.values()),
            "blocks": {b: {"families": f, "n": totals[b]} for b, f in BLOCKS.items()},
            "notes": ["S2 overlaps S1 by construction (DEV only)", "RefusEU EN/SL rows sharing a row_id are NOT translations; see "
                      "metadata_correspondence_grade", "S5X rows are constructed cross-translations, never official RefusEU",
                      "all QC numbers are automated; native review PENDING"]}
    (ROOT / "full_data_out.json").write_text(json.dumps({"metadata": meta, "datasets": out_blocks}, ensure_ascii=False))
    log(f"wrote full_data_out.json: {sum(totals.values())} examples in {len(out_blocks)} dataset blocks "
        f"({(ROOT / 'full_data_out.json').stat().st_size / 1e6:.1f} MB)")
    log("next: aii-json format script --input full_data_out.json -> rename full_full_/mini_full_/preview_full_data_out.json "
        "to full_/mini_/preview_data_out.json (see README)")


if __name__ == "__main__":
    main()
