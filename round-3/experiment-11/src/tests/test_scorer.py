#!/usr/bin/env python3
"""STEP 3.2 - harness test on saved text (no GPU): the plugin's per-item verdicts must equal the frozen classifier's,
and the plugin's keyword replica must equal Heretic's own KeywordRate._is_match on the same 40 texts, i.e. the
harness is right and ONLY the objective changed. Also runs the plugin's get_score() through a fake Context.
Writes results/test_scorer.json; exit code 1 on any failure."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import pandas as pd

WS = Path(__file__).resolve().parent.parent


def main() -> int:
    from heretic.config import Settings as HS
    from heretic.plugin import Context
    from heretic.scorers.keyword_rate import KeywordRate, Settings as KWS
    from heretic.scorers.partial_aware_refusal import PartialAwareRefusal, Settings, keyword_is_match
    from heretic.utils import Prompt

    pool = pd.read_parquet(WS / "results/label_pool.parquet")
    pool = pool[(pool.source == "exp4") & (pool.judge_model == "openai/gpt-4.1") & pool.is_edited & pool.y.notna()]
    pool = pool.sample(40, random_state=0)
    texts = pool["text"].tolist() + [""]  # + one empty response (must count as refusal)
    b = joblib.load(WS / "scorer/refusal_clf.joblib")
    ref = [(not t.strip()) or p >= b["threshold"] for t, p in zip(texts, b["pipeline"].predict_proba(texts)[:, 1])]

    sys.argv = [sys.argv[0]]
    hs = HS.model_validate({"model": "dummy"})
    sc = PartialAwareRefusal(heretic_settings=hs, settings=Settings(model_path=str(WS / "scorer/refusal_clf.joblib"),
                                                                     log_dir=str(WS / "logs/test_scorer")))

    class FakeCtx(Context):
        def __init__(self):
            self._responses_cache = {}

        def load_prompts(self, spec):
            return [Prompt(system="You are a helpful assistant.", user=f"q{i}") for i in range(len(texts))]

        def get_responses(self, prompts):
            return texts

    ctx = FakeCtx()
    sc.init(ctx)
    probs, matches = sc.score_texts(texts)
    score = sc.get_score(ctx)
    kw_plugin = [keyword_is_match(t) for t in texts]
    kwr = KeywordRate(heretic_settings=hs, settings=KWS())
    kw_heretic = [kwr._is_match(t) for t in texts]
    y = pool["y"].astype(int).tolist()
    res = {"n": len(texts), "plugin_equals_frozen_classifier": matches == ref,
           "keyword_replica_equals_heretic": kw_plugin == kw_heretic,
           "empty_counts_as_refusal": bool(matches[-1]),
           "score_value": score.value, "score_equals_mean": abs(score.value - sum(matches) / len(texts)) < 1e-12,
           "on_gpt41_labelled_edited_items": {
               "judged_refusal": sum(y), "classifier_refusal": sum(matches[:-1]), "keyword_refusal": sum(kw_heretic[:-1])}}
    res["pass"] = all([res["plugin_equals_frozen_classifier"], res["keyword_replica_equals_heretic"],
                       res["empty_counts_as_refusal"], res["score_equals_mean"]])
    (WS / "results/test_scorer.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
