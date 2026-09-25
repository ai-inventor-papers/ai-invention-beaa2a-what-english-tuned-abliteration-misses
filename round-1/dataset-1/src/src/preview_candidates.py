#!/usr/bin/env python3
"""Preview candidate datasets via the HF datasets-server (splits, sizes, first rows) + hub metadata."""
import json, os, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
TOK = os.environ.get("HF_TOKEN", "")
CANDS = ["mlabonne/harmful_behaviors","mlabonne/harmless_alpaca","heretic-org/Semantic-Harmful","heretic-org/Semantic-Harmless",
 "JailbreakBench/JBB-Behaviors","databricks/databricks-dolly-15k","openlanguagedata/flores_plus","cjvt/slovenian-llm-eval",
 "allenai/ai2_arc","google/boolq","Rowan/hellaswag","allenai/openbookqa","baber/piqa","allenai/winogrande","walledai/StrongREJECT",
 "walledai/XSTest","NASK-PIB/RefusEU","sorry-bench/sorry-bench-202406","walledai/MaliciousInstruct","bench-llm/or-bench",
 "DAMO-NLP-SG/MultiJail","CohereLabs/aya_redteaming","walledai/AdvBench","walledai/HarmBench","LibrAI/do-not-answer"]
def get(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOK}"})
    return json.load(urllib.request.urlopen(req, timeout=60))
def one(rid):
    out = {"id": rid}
    try:
        h = get(f"https://huggingface.co/api/datasets/{rid}")
        out.update(sha=h.get("sha"), downloads=h.get("downloads"), likes=h.get("likes"), gated=h.get("gated"),
                   license=[t for t in h.get("tags", []) if t.startswith("license:")], cardData_present=bool(h.get("cardData")))
    except Exception as e:
        out["hub_error"] = str(e)[:120]
    try:
        s = get(f"https://datasets-server.huggingface.co/splits?dataset={urllib.parse.quote(rid)}")
        out["splits"] = [(x["config"], x["split"]) for x in s.get("splits", [])][:40]
        cfg, spl = out["splits"][0]
        if rid == "openlanguagedata/flores_plus":
            cfg, spl = "slv_Latn", "dev"
        if rid == "cjvt/slovenian-llm-eval":
            cfg, spl = "arc_challenge", "test"
        if rid == "NASK-PIB/RefusEU":
            cfg, spl = "evaluation", "eval"
        fr = get(f"https://datasets-server.huggingface.co/first-rows?dataset={urllib.parse.quote(rid)}&config={urllib.parse.quote(cfg)}&split={spl}")
        out["preview_cfg"] = (cfg, spl)
        out["columns"] = [f["name"] for f in fr.get("features", [])]
        out["rows"] = [{k: (str(v)[:160]) for k, v in r["row"].items()} for r in fr.get("rows", [])[:3]]
        sz = get(f"https://datasets-server.huggingface.co/size?dataset={urllib.parse.quote(rid)}")
        out["num_rows_total"] = sz.get("size", {}).get("dataset", {}).get("num_rows")
        out["bytes_parquet"] = sz.get("size", {}).get("dataset", {}).get("num_bytes_parquet_files")
    except Exception as e:
        out["ds_error"] = str(e)[:160]
    return out
with ThreadPoolExecutor(16) as ex:
    res = list(ex.map(one, CANDS))
Path("temp/candidates_preview.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
for r in res:
    print(f"{r['id']:<36} dl={r.get('downloads')} gated={r.get('gated')} rows={r.get('num_rows_total')} MB={round((r.get('bytes_parquet') or 0)/1e6,1)} cols={r.get('columns')} err={r.get('ds_error','')[:60]}")
