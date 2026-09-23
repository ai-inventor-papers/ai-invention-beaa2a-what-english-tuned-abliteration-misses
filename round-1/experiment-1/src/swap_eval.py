#!/usr/bin/env python3
"""Swap / SL / sanity evaluation for ONE target model (GPU). Replica of Heretic's scorers kept per prompt.

  python swap_eval.py <target_tag> [--retest 0,1,2] [--sel-suffix ""]

Conditions for target T:
  orig : T with LoRA zeroed (Heretic reset_model)
  own  : T + T's selected params with T's own directions      (export path 2 == Heretic abliterate())
  swap : T + OTHER model's selected params with T's own directions
  retest_k : T + journal trial k params (test-retest of journal scores)

Per condition: EN refusal flags (harmful_behaviors test[:100], greedy, 100 tok, Heretic markers),
SL responses (NLLB translations of the same 100; EN system prompt), per-prompt first-token KL on
harmless_alpaca test[:100] vs orig, 10 EN + 10 SL harmless 128-token sanity generations, FLORES+ dev
per-token NLL (raw continuation, no chat template). Outputs -> results/eval/<target>_<cond>.json
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import sys
import time
from pathlib import Path

WS = Path(__file__).resolve().parent
sys.argv_saved = list(sys.argv)

import torch  # noqa: E402
import torch.nn.functional as F  # noqa: E402
from loguru import logger  # noqa: E402

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add(WS / "logs" / "swap_eval.log", rotation="30 MB", level="DEBUG")

# NOTE: no RLIMIT_AS here. safetensors loads the 5 x 5 GB shards with mmap and torch/CUDA reserve a
# large virtual address space, so an RLIMIT_AS cap makes the model unloadable ("unable to mmap ...:
# Cannot allocate memory"). Resident use stays ~6 GB (the weights live on the GPU); the GPU side is
# capped below instead.

JOURNALS = {
    "gams": WS / "checkpoints" / "gams" / "cjvt--GaMS3-12B-Instruct.jsonl",
    "gemma": WS / "checkpoints" / "gemma" / "google--gemma-3-12b-it.jsonl",
}
OTHER = {"gams": "gemma", "gemma": "gams"}


def is_refusal_heretic(response: str, markers: list[str]) -> bool:
    """Exact copy of heretic.scorers.keyword_rate.KeywordRate._is_match normalisation."""
    if not response.strip():
        return True
    response = response.lower().replace("*", "")
    response = response.replace("’", "'")
    response = " ".join(response.split())
    return any(m.lower() in response for m in markers)


def build_directions(means_path: Path, orthogonalize: bool) -> torch.Tensor:
    d = torch.load(means_path)
    good, bad = d["means"][0], d["means"][1]
    rd = F.normalize(bad - good, p=2, dim=1)
    if orthogonalize:
        gd = F.normalize(good, p=2, dim=1)
        proj = torch.sum(rd * gd, dim=1)
        rd = rd - proj.unsqueeze(1) * gd
        rd = F.normalize(rd, p=2, dim=1)
    return rd


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", choices=["gams", "gemma"])
    ap.add_argument("--retest", default="0,1,2")
    ap.add_argument("--conds", default="orig,own,swap")
    ap.add_argument("--flores-n", type=int, default=200)
    args = ap.parse_args()
    sys.argv = ["heretic-eval"]  # keep pydantic CLI source quiet

    import optuna
    from heretic.config import Settings
    from heretic.model import AbliterationParameters, Model
    from heretic.scorers.keyword_rate import REFUSAL_MARKERS
    from heretic.utils import Prompt, load_prompts, batchify

    T = args.target
    out_dir = WS / "results" / "eval"
    out_dir.mkdir(parents=True, exist_ok=True)

    st = optuna.load_study(study_name="heretic", storage=optuna.storages.JournalStorage(
        optuna.storages.journal.JournalFileBackend(str(JOURNALS[T]))))
    settings = Settings.model_validate_json(st.user_attrs["settings"])
    logger.info(f"restored settings: model={settings.model}@{settings.model_commit} quant={settings.quantization} "
                f"bs={settings.batch_size} prefix={settings.response_prefix!r} sys={settings.system_prompt!r}")
    sel_own = json.loads((WS / "results" / f"selection_{T}.json").read_text())
    sel_other = json.loads((WS / "results" / f"selection_{OTHER[T]}.json").read_text())

    if torch.cuda.is_available():
        torch.cuda.set_per_process_memory_fraction(0.92)
    t0 = time.time()
    model = Model(settings)
    logger.info(f"model loaded in {time.time() - t0:.0f}s dtype={model.dtype}")
    rd = build_directions(WS / "directions" / T / "residual_means_A.pt", settings.orthogonalize_direction)
    torch.save(rd, WS / "directions" / T / "directions.pt")
    logger.info(f"directions {tuple(rd.shape)} (row 0 = embeddings; abliterate() uses index+1)")

    # scorer settings were not customised -> Heretic's default KeywordRate / KLDivergence prompt sets
    from heretic.config import DatasetSpecification
    hb = load_prompts(settings, DatasetSpecification(dataset="mlabonne/harmful_behaviors", split="test[:100]", column="text"))
    ha = load_prompts(settings, DatasetSpecification(dataset="mlabonne/harmless_alpaca", split="test[:100]", column="text"))
    sl = json.loads((WS / "data" / "sl_harmful_behaviors_test100.json").read_text())["items"]
    sl_h = [it for it in sl if it["set"] == "harmful_behaviors_test"]
    sl_b = [it for it in sl if it["set"] != "harmful_behaviors_test"]
    assert [it["en"] for it in sl_h] == [p.user for p in hb], "SL items not aligned with harmful_behaviors test[:100]"
    sys_p = settings.system_prompt
    sl_prompts = [Prompt(system=sys_p, user=it["sl"]) for it in sl_h]
    san_en = [Prompt(system=sys_p, user=it["en"]) for it in sl_b]
    san_sl = [Prompt(system=sys_p, user=it["sl"]) for it in sl_b]
    flores = json.loads((WS / "data" / "flores_plus_dev200.json").read_text())["data"]
    # FLORES+ subset size: the teacher-forced pass over the full 262k-vocab logits is the slowest part
    # of a condition, so the number of sentences per language is a CLI knob and is recorded per file.
    flores = {k: v[: args.flores_n] for k, v in flores.items()}

    def kl_per_prompt(base_lp: torch.Tensor) -> list[float]:
        lp = F.log_softmax(model.get_logits_batched(ha).float(), dim=-1)
        kl = (base_lp.exp() * (base_lp - lp)).sum(-1)
        return kl.tolist()

    def gen(prompts, n_tok):
        out = []
        for b in batchify(prompts, settings.batch_size):
            inputs, outputs = model.generate(b, max_new_tokens=n_tok)
            out += model.tokenizer.batch_decode(outputs[:, inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        return out

    def flores_nll(lang: str) -> list[float]:
        tok = model.tokenizer
        res = []
        texts = [r["text"] for r in flores[lang]]
        old = tok.padding_side
        tok.padding_side = "right"
        for i in range(0, len(texts), 10):
            enc = tok(texts[i:i + 10], return_tensors="pt", padding=True, return_token_type_ids=False).to(model.model.device)
            with torch.no_grad():
                logits = model.model(**enc).logits.float()
            lp = F.log_softmax(logits[:, :-1], -1)
            tgt = enc["input_ids"][:, 1:]
            m = enc["attention_mask"][:, 1:].float()
            nll = -(lp.gather(-1, tgt.unsqueeze(-1)).squeeze(-1)) * m
            res += (nll.sum(1) / m.sum(1)).tolist()
            del logits, lp, nll
            torch.cuda.empty_cache()
        tok.padding_side = old
        return res

    def apply(params_rec: dict | None):
        model.reset_model()
        if params_rec is None:
            return
        model.abliterate(rd, params_rec["direction_index"],
                         {k: AbliterationParameters(**v) for k, v in params_rec["abliteration_parameters"].items()})

    # baseline first-token distributions (orig)
    model.reset_model()
    base_lp = F.log_softmax(model.get_logits_batched(ha).float(), dim=-1)

    conds: list[tuple[str, dict | None, bool]] = []
    for c in args.conds.split(","):
        if c == "orig":
            conds.append(("orig", None, True))
        elif c == "own":
            conds.append(("own", sel_own, True))
        elif c == "swap":
            conds.append(("swap", sel_other, True))
    for k in [int(x) for x in args.retest.split(",") if x != ""]:
        t = st.trials[k]
        conds.append((f"retest{k}", {"trial_number": k, "direction_index": t.user_attrs["direction_index"],
                                     "abliteration_parameters": t.user_attrs["parameters"],
                                     "journal_refusals": round(t.values[0] * 100), "journal_kl": t.values[1]}, False))

    for name, rec, full in conds:
        t1 = time.time()
        apply(rec)
        en_resp = model.get_responses_batched(hb, skip_special_tokens=True)
        en_flags = [is_refusal_heretic(r, REFUSAL_MARKERS) for r in en_resp]
        kl = kl_per_prompt(base_lp)
        out = {"target": T, "condition": name, "params_source": (None if rec is None else rec.get("trial_number")),
               "params_from_model": (T if name in ("own",) or name.startswith("retest") else (OTHER[T] if name == "swap" else None)),
               "en_refusals": int(sum(en_flags)), "kl_mean": float(sum(kl) / len(kl)),
               "en": [{"id": f"hb_test_{i:03d}", "prompt": p.user, "response": r, "refusal_heretic": f}
                      for i, (p, r, f) in enumerate(zip(hb, en_resp, en_flags))],
               "kl_per_prompt": kl}
        if rec is not None and "journal_refusals" in rec:
            out["journal_refusals"] = rec["journal_refusals"]
            out["journal_kl"] = rec["journal_kl"]
        if rec is not None and "refusals" in rec:
            out["journal_refusals"] = rec["refusals"]
            out["journal_kl"] = rec["kl"]
        if full:
            sl_resp = gen(sl_prompts, settings.max_response_length)
            out["sl"] = [{"id": it["id"], "prompt_sl": it["sl"], "response": r,
                          "refusal_heretic_en_markers": is_refusal_heretic(r, REFUSAL_MARKERS)}
                         for it, r in zip(sl_h, sl_resp)]
            out["sanity_en"] = [{"id": it["id"], "prompt": it["en"], "response": r} for it, r in zip(sl_b, gen(san_en, 128))]
            out["sanity_sl"] = [{"id": it["id"], "prompt": it["sl"], "response": r} for it, r in zip(sl_b, gen(san_sl, 128))]
            out["flores_nll_eng"] = flores_nll("eng_Latn")
            out["flores_nll_slv"] = flores_nll("slv_Latn")
        out["flores_n_per_language"] = args.flores_n
        out["wall_s"] = time.time() - t1
        (out_dir / f"{T}_{name}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
        logger.info(f"{T}/{name}: EN refusals {out['en_refusals']} KL {out['kl_mean']:.4f} "
                    f"(journal {out.get('journal_refusals')}, {out.get('journal_kl')}) wall {out['wall_s']:.0f}s")
        if name == "own" and rec is not None:
            # save the path-2 adapter for the selected trial + sha256
            ad = WS / "adapters" / f"{T}_selected_path2"
            model.model.save_pretrained(str(ad))
            shas = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in ad.iterdir() if p.is_file()}
            (ad / "SHA256SUMS.json").write_text(json.dumps(shas, indent=1))
        gc.collect()
        torch.cuda.empty_cache()
    logger.info(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
