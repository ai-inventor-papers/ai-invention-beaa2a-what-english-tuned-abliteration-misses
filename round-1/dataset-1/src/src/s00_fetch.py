#!/usr/bin/env python3
"""STEP 0: download every raw source (HF datasets pinned to commit SHA + ungated GitHub CSVs) into temp/datasets/.

Writes temp/datasets/full_<name>.json (list of row dicts) and data/provenance/sources.json
(repo, config, split, revision SHA, row count, file SHA256)."""
from __future__ import annotations

import csv
import io
import json
import os
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from datasets import load_dataset
from huggingface_hub import HfApi, hf_hub_download
from loguru import logger

from common import OUT, RAW, setup_logging, sha256_text, write_json

setup_logging("s00_fetch")
API = HfApi()

HF_JOBS = [  # name, repo, config, split
    ("mlhb_train", "mlabonne/harmful_behaviors", None, "train"),
    ("mlhb_test", "mlabonne/harmful_behaviors", None, "test"),
    ("mlha_train", "mlabonne/harmless_alpaca", None, "train"),
    ("mlha_test", "mlabonne/harmless_alpaca", None, "test"),
    ("semharmful", "heretic-org/Semantic-Harmful", None, "train"),
    ("semharmless", "heretic-org/Semantic-Harmless", None, "train"),
    ("jbb_harmful", "JailbreakBench/JBB-Behaviors", "behaviors", "harmful"),
    ("jbb_benign", "JailbreakBench/JBB-Behaviors", "behaviors", "benign"),
    ("dolly", "databricks/databricks-dolly-15k", None, "train"),
    ("flores_eng_dev", "openlanguagedata/flores_plus", "eng_Latn", "dev"),
    ("flores_slv_dev", "openlanguagedata/flores_plus", "slv_Latn", "dev"),
    ("flores_eng_devtest", "openlanguagedata/flores_plus", "eng_Latn", "devtest"),
    ("flores_slv_devtest", "openlanguagedata/flores_plus", "slv_Latn", "devtest"),
    ("sleval_arc_challenge", "cjvt/slovenian-llm-eval", "arc_challenge", "test"),
    ("sleval_boolq", "cjvt/slovenian-llm-eval", "boolq", "test"),
    ("sleval_hellaswag", "cjvt/slovenian-llm-eval", "hellaswag", "test"),
    ("sleval_openbookqa", "cjvt/slovenian-llm-eval", "openbookqa", "test"),
    ("sleval_piqa", "cjvt/slovenian-llm-eval", "piqa", "test"),
    ("sleval_winogrande", "cjvt/slovenian-llm-eval", "winogrande", "test"),
    ("en_arc_challenge", "allenai/ai2_arc", "ARC-Challenge", "test"),
    ("en_boolq", "google/boolq", None, "validation"),
    ("en_hellaswag", "Rowan/hellaswag", None, "validation"),
    ("en_openbookqa", "allenai/openbookqa", "main", "test"),
    ("en_piqa", "baber/piqa", None, "validation"),
    ("en_winogrande", "allenai/winogrande", "winogrande_xl", "validation"),
    ("refuseu_eval", "NASK-PIB/RefusEU", "evaluation", "eval"),
    ("refuseu_pref_en_test", "NASK-PIB/RefusEU", "lang_en", "test"),
    ("refuseu_pref_sl_test", "NASK-PIB/RefusEU", "lang_sl", "test"),
    ("maliciousinstruct", "walledai/MaliciousInstruct", None, "train"),
]
GH_JOBS = [  # name, owner/repo, path
    ("strongreject", "alexandrasouly/strongreject", "strongreject_dataset/strongreject_dataset.csv"),
    ("xstest", "paul-rottger/xstest", "xstest_prompts.csv"),
    ("advbench", "llm-attacks/llm-attacks", "data/advbench/harmful_behaviors.csv"),
    ("harmbench", "centerforaisafety/HarmBench", "data/behavior_datasets/harmbench_behaviors_text_all.csv"),
]


def _jsonable(v):
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    if isinstance(v, dict):
        return {k: _jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    return str(v)


def fetch_hf(job: tuple) -> dict:
    name, repo, cfg, split = job
    sha = API.dataset_info(repo).sha
    ds = load_dataset(repo, cfg, split=split, revision=sha)
    if name == "refuseu_eval":
        ds = ds.filter(lambda r: r["lang"] in ("en", "sl"))
    rows = [_jsonable(r) for r in ds]
    txt = json.dumps(rows, ensure_ascii=False)
    (RAW / f"full_{name}.json").write_text(txt)
    logger.info(f"{name}: {repo}/{cfg}/{split} @ {sha[:10]} -> {len(rows)} rows")
    return {"name": name, "repo": repo, "config": cfg, "split": split, "revision": sha, "n_rows": len(rows),
            "sha256": sha256_text(txt), "columns": list(rows[0].keys()) if rows else []}


def fetch_gh(job: tuple) -> dict:
    name, repo, path = job
    commit = None
    try:
        api = f"https://api.github.com/repos/{repo}/commits?path={path}&per_page=1"
        commit = json.load(urllib.request.urlopen(api, timeout=60))[0]["sha"]
    except Exception as e:  # noqa: BLE001 - GitHub API rate limits; fall back to main
        logger.warning(f"{name}: commit lookup failed ({e}); using main")
    ref = commit or "main"
    raw = urllib.request.urlopen(f"https://raw.githubusercontent.com/{repo}/{ref}/{path}", timeout=120).read().decode("utf-8")
    rows = list(csv.DictReader(io.StringIO(raw)))
    (RAW / f"full_{name}.json").write_text(json.dumps(rows, ensure_ascii=False))
    logger.info(f"{name}: github {repo}/{path} @ {ref[:10]} -> {len(rows)} rows")
    return {"name": name, "repo": f"github:{repo}", "path": path, "revision": ref, "n_rows": len(rows),
            "sha256": sha256_text(raw), "columns": list(rows[0].keys()) if rows else []}


@logger.catch(reraise=True)
def main() -> None:
    with ThreadPoolExecutor(8) as ex:
        hf = list(ex.map(fetch_hf, HF_JOBS))
        gh = list(ex.map(fetch_gh, GH_JOBS))
    # Semantic-Harmful pairing metadata (harmful_index / harmless_index)
    sha = API.dataset_info("heretic-org/Semantic-Harmful").sha
    p = hf_hub_download("heretic-org/Semantic-Harmful", "metadata/matched_pairs.json", repo_type="dataset", revision=sha)
    meta = json.loads(open(p).read())
    (RAW / "full_semantic_matched_pairs.json").write_text(json.dumps(meta, ensure_ascii=False))
    extra = {"name": "semantic_matched_pairs", "repo": "heretic-org/Semantic-Harmful", "path": "metadata/matched_pairs.json",
             "revision": sha, "n_rows": len(meta) if isinstance(meta, list) else None}
    write_json(OUT / "provenance" / "sources.json", hf + gh + [extra])
    logger.info("fetch complete")


if __name__ == "__main__":
    main()
