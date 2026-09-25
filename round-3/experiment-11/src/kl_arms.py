#!/usr/bin/env python3
"""Harmless first-token KL (Heretic's own KLDivergence scorer, mlabonne/harmless_alpaca test[:100]) and in-loop
keyword/classifier refusal counts for EVERY evaluation arm incl. the dose ladder, in Heretic's own loop, so the dose
arms get the same divergence measure as the optimiser's candidates. One model load; same code path as replay.py.
-> results/kl_arms.json"""
from __future__ import annotations

import json
import sys
from pathlib import Path

WS = Path(__file__).resolve().parent


def main() -> None:
    sys.argv = [sys.argv[0]]
    import torch
    import torch.nn.functional as F
    from heretic.config import Settings
    from heretic.evaluator import Evaluator
    from heretic.model import AbliterationParameters, Model
    import heretic.scorers.partial_aware_refusal as par
    from replay import MEANS_SRC, load_iter1_study

    arms = json.loads((WS / "arms.json").read_text())
    s_json, _ = load_iter1_study()
    s_json["scorers"] = [{"plugin": "heretic.scorers.keyword_rate.KeywordRate", "optimization": "minimize"},
                         {"plugin": "heretic.scorers.kl_divergence.KLDivergence", "optimization": "minimize"},
                         {"plugin": "heretic.scorers.partial_aware_refusal.PartialAwareRefusal", "optimization": "none"}]
    s_json["scorer"] = {"PartialAwareRefusal": {"model_path": str(WS / "scorer/refusal_clf.joblib"),
                                                "log_dir": str(WS / "logs/inloop_scores/kl_arms")}}
    settings = Settings.model_validate_json(json.dumps(s_json))
    model = Model(settings)
    cache = {}

    def dirs_for(src: str):
        if src not in cache:
            m = torch.load(src, map_location="cpu")
            g, b = m["means"][0].float(), m["means"][1].float()
            d = F.normalize(b - g, p=2, dim=1)
            gd = F.normalize(g, p=2, dim=1)
            cache[src] = F.normalize(d - torch.sum(d * gd, dim=1).unsqueeze(1) * gd, p=2, dim=1)
        return cache[src]

    par.CURRENT_TRIAL.update({"trial": -1, "tag": "kl_arms_baseline"})
    ev = Evaluator(settings, model)
    out = {}
    for a in arms:
        par.CURRENT_TRIAL.clear()
        par.CURRENT_TRIAL.update({"trial": a.get("trial"), "tag": a["arm"]})
        model.reset_model()
        if a.get("parameters"):
            model.abliterate(dirs_for(a.get("means_src") or str(MEANS_SRC)), a["direction_index"],
                             {k: AbliterationParameters(**v) for k, v in a["parameters"].items()})
            f = float(a.get("dose", 1.0))
            if f != 1.0:
                for _, mod in model.model.named_modules():
                    if hasattr(mod, "lora_B") and "default" in getattr(mod, "lora_B", {}):
                        mod.lora_B["default"].weight.data *= f
        sc = {n: s.value for n, s in ev.get_scores()}
        out[a["arm"]] = {"harmless_kl": sc["KL divergence"], "inloop_keyword_refusals": round(sc["Refusals"] * 100),
                         "inloop_classifier_refusals": round(sc["Refusals (partial-aware)"] * 100)}
        print(a["arm"], out[a["arm"]], flush=True)
    (WS / "results/kl_arms.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
