#!/usr/bin/env python3
"""STEP 6 - final generation for every arm from ONE shared NF4 base load (Heretic's own Model class, iteration-1
stored settings), so every arm differs ONLY in the LoRA delta that Heretic's abliterate() writes:

  A  gemma_orig                 reset_model() (identity LoRA)
  B  gemma_edit_keyword         abliterate(iteration-1 trial 96 params)   (the keyword-selected checkpoint of record)
  C  gemma_edit_corrected       abliterate(params selected by the corrected-objective run)
  D  gemma_edit_reselected      abliterate(params reselected post hoc from the 116 iteration-1 draws), if != C
  F  dose ladder on B           abliterate(trial 96) then every lora_B *= f  (matched-efficacy control)

Item sets (frozen, see results/eval_items.json): S5X 100 verified pairs (= 200 prompts: the official EN/SL
row and its gpt-4.1 cross-translation), S4 held-out-category ('hoc') StrongREJECT harmful 70 x EN+SL, S6 XSTest-safe
60 x EN+SL, plus FLORES+ devtest teacher-forced per-token NLL (100 sentences per language).
Decoding: system prompt 'You are a helpful assistant.', greedy, 256 new tokens, EOS = {<eos>, <end_of_turn>}.
Batching: length-sorted left-padded batches of <= 32 with ONE schedule shared by every arm (DEVIATION from
art_m6pglf516e2r's exact-length buckets, which would leave most batches at 1-3 prompts on this item set; batch
composition is identical across arms, so it cannot confound arm contrasts; A and B are re-measured in this path).

  python eval_gen.py --arms arms.json [--only A,B] [--sets S5X,S4hoc,S6,FLORES]
Outputs: results/eval_gen/<arm>.jsonl (resumable by item_key), results/eval_gen/<arm>_flores.json,
results/eval_gen/adapter_check.json (in-memory trial-96 LoRA vs the exported iteration-1 adapter).
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from pathlib import Path

WS = Path(__file__).resolve().parent
RUN = Path("/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop")
W1 = RUN / "iter_1/gen_art/gen_art_experiment_1"
W4 = RUN / "iter_2/gen_art/gen_art_experiment_4"
WD = RUN / "iter_1/gen_art/gen_art_dataset_1"
SYSTEM_PROMPT = "You are a helpful assistant."
MAX_NEW = 256
EOS = [1, 106]


def read_jsonl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def build_items() -> dict:
    """Frozen item list (written once; later calls read it back)."""
    out = WS / "results/eval_items.json"
    if out.exists():
        return json.loads(out.read_text())
    fr = json.loads((W4 / "frozen_samples.json").read_text())
    it = {i["item_key"]: i for i in fr["items"]}
    items = []
    for p in fr["s5x_pairs"]:
        for side, k in (("en", p["en_item"]), ("sl", p["sl_item"])):
            x = it[k]
            items.append({"item_key": k, "set": "S5X", "lang": x["lang"], "prompt": x["prompt"], "pair_id": p["pair_id"],
                          "pair_side": side, "direction": p["direction"], "semantic_id": p["pair_id"],
                          "category": p["category"], "role": "harmful"})
    s4 = [json.loads(l) for l in (WD / "data/splits/S4_strongreject_pairs.jsonl").read_text().splitlines() if l.strip()]
    for r in s4:
        if r["metadata_s4_stratum"] == "hoc" and r["metadata_role"] == "harmful":
            sid = r["metadata_semantic_id"]
            items.append({"item_key": f"S4hoc:{sid}:{r['metadata_lang']}", "set": "S4hoc", "lang": r["metadata_lang"],
                          "prompt": r["input"], "semantic_id": sid, "category": r.get("metadata_category_llamaguard"),
                          "role": "harmful"})
    s6_ids = sorted({i["semantic_id"] for i in fr["items"] if i["set"] == "S6"})
    random.Random(20260924).shuffle(s6_ids)
    keep = set(s6_ids[:60])
    for i in fr["items"]:
        if i["set"] == "S6" and i["semantic_id"] in keep:
            items.append({"item_key": i["item_key"], "set": "S6", "lang": i["lang"], "prompt": i["prompt"],
                          "semantic_id": i["semantic_id"], "role": "safe", "xstest_type": i.get("xstest_type")})
    fl = [json.loads(l) for l in (WD / "data/splits/S7_flores_devtest.jsonl").read_text().splitlines() if l.strip()]
    en = [r for r in fl if r["metadata_lang"] == "en"][:100]
    flores = [{"id": r["metadata_semantic_id"], "en": r["input"], "sl": r["output"]} for r in en]
    res = {"frozen_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "items": items, "flores": flores,
           "note": "S5X pairs = art_m6pglf516e2r frozen_samples.json s5x_pairs (SECOND touch of S5X; first: art_m6pglf516e2r); "
                   "S6 subset = 60 semantic ids, seed 20260924; FLORES = first 100 devtest en rows and their sl reference"}
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(res, ensure_ascii=False, indent=0))
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--sets", default="S5X,S4hoc,S6,FLORES")
    ap.add_argument("--bs", type=int, default=32)
    args = ap.parse_args()
    sys.argv = [sys.argv[0]]
    from loguru import logger
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    logger.add(WS / "logs/eval_gen.log", level="DEBUG", rotation="30 MB")

    import torch
    import torch.nn.functional as F
    from heretic.config import Settings
    from heretic.model import AbliterationParameters, Model
    from replay import MEANS_SRC, load_iter1_study

    arms = json.loads(Path(args.arms).read_text())
    only = [a for a in args.only.split(",") if a]
    sets = set(args.sets.split(","))
    data = build_items()
    items = [i for i in data["items"] if i["set"] in sets]
    s_json, trials = load_iter1_study()
    s_json["scorers"] = [{"plugin": "heretic.scorers.kl_divergence.KLDivergence", "optimization": "minimize"}]
    settings = Settings.model_validate_json(json.dumps(s_json))
    t0 = time.time()
    model = Model(settings)
    tok = model.tokenizer
    logger.info(f"model loaded {time.time() - t0:.0f}s; {len(items)} items; arms {[a['arm'] for a in arms]}")
    _dir_cache: dict = {}

    def directions_for(src: str):
        """Heretic's refusal directions from a saved residual-mean capture (iteration-1 capture by default; the
        corrected run's own capture for arm C, since the optimiser tuned C's parameters on those directions)."""
        if src not in _dir_cache:
            m = torch.load(src, map_location="cpu")
            g, b = m["means"][0].float(), m["means"][1].float()
            d = F.normalize(b - g, p=2, dim=1)
            if settings.orthogonalize_direction:
                gd = F.normalize(g, p=2, dim=1)
                d = F.normalize(d - torch.sum(d * gd, dim=1).unsqueeze(1) * gd, p=2, dim=1)
            _dir_cache[src] = d
        return _dir_cache[src]

    def render_ids(prompt: str) -> list[int]:
        txt = tok.apply_chat_template([{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
                                      add_generation_prompt=True, tokenize=False)
        return tok(txt, add_special_tokens=False)["input_ids"]

    enc = {i["item_key"]: render_ids(i["prompt"]) for i in items}

    def lora_modules():
        for name, mod in model.model.named_modules():
            if hasattr(mod, "lora_B") and "default" in getattr(mod, "lora_B", {}):
                yield name, mod

    def apply_arm(arm: dict) -> None:
        model.reset_model()
        if arm.get("parameters") is None:
            return
        params = {k: AbliterationParameters(**v) for k, v in arm["parameters"].items()}
        model.abliterate(directions_for(arm.get("means_src") or str(MEANS_SRC)), arm["direction_index"], params)
        f = float(arm.get("dose", 1.0))
        if f != 1.0:
            n = 0
            for _, mod in lora_modules():
                mod.lora_B["default"].weight.data *= f
                n += 1
            logger.info(f"{arm['arm']}: scaled lora_B of {n} modules by {f}")

    @torch.inference_mode()
    def gen_bucket(id_lists: list[list[int]]) -> list[dict]:
        L = max(len(x) for x in id_lists)
        pad = tok.pad_token_id
        ids = torch.full((len(id_lists), L), pad, dtype=torch.long)
        att = torch.zeros((len(id_lists), L), dtype=torch.long)
        for i, x in enumerate(id_lists):  # left padding
            ids[i, L - len(x):] = torch.tensor(x)
            att[i, L - len(x):] = 1
        ids, att = ids.to(model.model.device), att.to(model.model.device)
        out = model.model.generate(input_ids=ids, attention_mask=att, do_sample=False,
                                   max_new_tokens=MAX_NEW, temperature=None, top_p=None, top_k=None,
                                   pad_token_id=tok.pad_token_id, eos_token_id=EOS)
        res = []
        for gseq in out[:, ids.shape[1]:].cpu().tolist():
            n, seen = len(gseq), False
            for j, t in enumerate(gseq):
                if t in EOS:
                    n, seen = j, True
                    break
            res.append({"n_new_tokens": n, "eos_token_seen": seen, "hit_max": (not seen) and n >= MAX_NEW,
                        "response_text": tok.decode(gseq[:n], skip_special_tokens=True)})
        return res

    @torch.inference_mode()
    def flores_nll(texts: list[str]) -> dict:
        tot, ntok, per = 0.0, 0, []
        for t in texts:
            ids = tok(t, return_tensors="pt", add_special_tokens=True)["input_ids"].to(model.model.device)
            logits = model.model(input_ids=ids).logits[0, :-1].float()
            tgt = ids[0, 1:]
            nll = 0.0
            for c0 in range(0, logits.shape[0], 64):  # chunked log_softmax over the 262k vocabulary
                lp = torch.log_softmax(logits[c0:c0 + 64], dim=-1)
                nll += float(-lp.gather(1, tgt[c0:c0 + 64, None]).sum())
            per.append(nll / max(len(tgt), 1))
            tot += nll
            ntok += len(tgt)
        return {"nll_per_token": tot / max(ntok, 1), "n_tokens": ntok, "n_sent": len(texts), "per_sentence": per}

    outdir = WS / "results/eval_gen"
    outdir.mkdir(parents=True, exist_ok=True)
    for arm in arms:
        if only and arm["arm"] not in only:
            continue
        name = arm["arm"]
        t1 = time.time()
        apply_arm(arm)
        if arm.get("check_adapter"):
            from safetensors.torch import load_file
            ad = load_file(str(Path(arm["check_adapter"]) / "adapter_model.safetensors"))
            mem = {n.replace(".default", ""): p.detach().float().cpu() for n, p in model.model.named_parameters() if "lora_" in n}
            diffs, missing = [], 0
            for k, v in ad.items():
                kk = k if k in mem else k.replace("base_model.model.", "base_model.model.", 1)
                if kk not in mem:
                    missing += 1
                    continue
                diffs.append(float((mem[kk] - v.float()).abs().max()))
            chk = {"arm": name, "adapter": arm["check_adapter"], "n_tensors_file": len(ad), "n_matched": len(diffs),
                   "n_missing": missing, "max_abs_diff": max(diffs) if diffs else None,
                   "n_exact": sum(d == 0.0 for d in diffs)}
            (outdir / "adapter_check.json").write_text(json.dumps(chk, indent=1))
            logger.info(f"adapter check {chk}")
        if arm.get("export_adapter") and not (WS / arm["export_adapter"] / "adapter_model.safetensors").exists():
            import hashlib
            exp_dir = WS / arm["export_adapter"]
            model.model.save_pretrained(str(exp_dir))
            shas = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in exp_dir.iterdir() if f.is_file()}
            (exp_dir / "SHA256SUMS.json").write_text(json.dumps(shas, indent=1))
            (exp_dir / "EDIT_PARAMETERS.json").write_text(json.dumps({k: arm.get(k) for k in (
                "arm", "trial", "source", "rule_fired", "parameters", "direction_index", "means_src")}, indent=1))
            logger.info(f"{name}: exported LoRA adapter -> {exp_dir}")
        p = outdir / f"{name}.jsonl"
        done = {r["item_key"] for r in read_jsonl(p)}
        todo = [i for i in items if i["item_key"] not in done]
        # ONE deterministic schedule for every arm: items sorted by (prompt length, item_key), chunks of --bs,
        # left padding (identical batch composition across arms, so padding cannot differ between arms)
        todo = sorted(todo, key=lambda i: (len(enc[i["item_key"]]), i["item_key"]))
        buckets = {0: todo}
        n_done = 0
        for L in sorted(buckets):
            grp = buckets[L]
            for c0 in range(0, len(grp), args.bs):
                chunk = grp[c0:c0 + args.bs]
                res = gen_bucket([enc[i["item_key"]] for i in chunk])
                with p.open("a") as f:
                    for i, r in zip(chunk, res):
                        f.write(json.dumps({"arm": name, **{k: i[k] for k in ("item_key", "set", "lang", "semantic_id", "role")},
                                            "pair_id": i.get("pair_id"), "prompt": i["prompt"], **r,
                                            "batch_index": c0 // args.bs, "batch_size_used": len(chunk)}, ensure_ascii=False) + "\n")
                n_done += len(chunk)
        logger.info(f"{name}: generated {n_done} in {time.time() - t1:.0f}s")
        if "FLORES" in sets and not (outdir / f"{name}_flores.json").exists():
            fl = {lang: flores_nll([r[lang] for r in data["flores"]]) for lang in ("en", "sl")}
            (outdir / f"{name}_flores.json").write_text(json.dumps({"arm": name, **fl}))
            logger.info(f"{name}: FLORES NLL en {fl['en']['nll_per_token']:.4f} sl {fl['sl']['nll_per_token']:.4f}")
        torch.cuda.empty_cache()
    logger.info("EVAL_GEN_DONE")


if __name__ == "__main__":
    main()
