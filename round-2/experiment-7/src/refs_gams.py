#!/usr/bin/env python3
"""Compliance-reference source (ii): GaMS3-12B-Instruct + its iteration-1 core edit (trial 88), rebuilt with
Heretic's Model.abliterate() and checked against the saved adapter. Generates 64 greedy tokens for all 340 S3 JBB
prompts (EN+SL, harmful+benign). The Gemma process judges them later (local judge; the API judge is blocked).
Output: references/gams_core_generations.json (+ sha256)."""
from __future__ import annotations

import json
import sys
import time

sys.argv = ["refs"]
import torch  # noqa: E402
from loguru import logger  # noqa: E402
from safetensors.torch import load_file  # noqa: E402

from common import EXP1, JOURNAL_GAMS, WS, load_items, sha256_file  # noqa: E402

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add(WS / "logs" / "refs_gams.log", rotation="30 MB", level="DEBUG")


@logger.catch(reraise=True)
def main() -> None:
    import optuna
    from heretic.config import Settings
    from heretic.model import AbliterationParameters, Model
    from heretic.utils import Prompt, batchify

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    st = optuna.load_study(study_name="heretic", storage=optuna.storages.JournalStorage(
        optuna.storages.journal.JournalFileBackend(str(JOURNAL_GAMS))))
    settings = Settings.model_validate_json(st.user_attrs["settings"])
    logger.info(f"GaMS settings: {settings.model}@{settings.model_commit} {settings.quantization}")
    torch.cuda.set_per_process_memory_fraction(0.92)
    t0 = time.time()
    model = Model(settings)
    logger.info(f"loaded in {time.time()-t0:.0f}s")
    rd = torch.load(EXP1 / "directions" / "gams" / "directions.pt")
    sel = json.loads((EXP1 / "results" / "selection_gams.json").read_text())
    model.reset_model()
    model.abliterate(rd, sel["direction_index"],
                     {k: AbliterationParameters(**v) for k, v in sel["abliteration_parameters"].items()})
    # rebuild check against the saved adapter
    saved = load_file(str(EXP1 / "adapters" / "gams_selected" / "adapter_model.safetensors"))
    cur = {n: p.detach().float().cpu() for n, p in model.model.named_parameters() if "lora_" in n}
    maxd, nmatch = 0.0, 0
    for k, v in saved.items():
        kk = [c for c in cur if c.endswith(k.replace("base_model.model.", "").replace(".weight", ".default.weight"))]
        if len(kk) == 1:
            maxd = max(maxd, (cur[kk[0]] - v.float()).abs().max().item())
            nmatch += 1
    logger.info(f"GaMS trial-88 rebuild vs saved adapter: {nmatch}/{len(saved)} tensors matched, max|diff|={maxd:.3e}")
    items = load_items()["S3_jbb"]
    prompts = [Prompt(system=settings.system_prompt, user=it["text"]) for it in items]
    outs = []
    for b in batchify(prompts, 64):
        inputs, outputs = model.generate(b, max_new_tokens=64)
        gen = outputs[:, inputs["input_ids"].shape[1]:]
        for row in gen:
            ids = row.tolist()
            outs.append({"ids": ids, "text": model.tokenizer.decode(ids, skip_special_tokens=True)})
    res = {"source": "GaMS3-12B-Instruct@1d0b27af + Heretic trial 88 (iteration-1 core edit), greedy 64 tokens",
           "adapter_sha256_saved": sha256_file(EXP1 / "adapters" / "gams_selected" / "adapter_model.safetensors"),
           "rebuild_check": {"n_matched": nmatch, "n_saved": len(saved), "max_abs_diff": maxd},
           "rows": [{"sid": it["sid"], "lang": it["lang"], "half": it["half"], "role": it["role"], **o}
                    for it, o in zip(items, outs)]}
    p = WS / "references" / "gams_core_generations.json"
    p.write_text(json.dumps(res, ensure_ascii=False, indent=1))
    logger.info(f"saved {len(outs)} generations sha256={sha256_file(p)[:16]} total {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
