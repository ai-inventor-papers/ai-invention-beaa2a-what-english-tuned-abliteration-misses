#!/usr/bin/env python3
"""Build arms.json for eval_gen.py from the frozen selections (run AFTER analyze_inloop.py, BEFORE any Step-6 output).
A orig | B keyword-selected (iteration-1 trial 96, checkpoint of record) | C corrected-run selection |
D reselected under the classifier (if != C) | D2 reselected under the Qwen3-14B judge (if distinct) | F dose ladder on B."""
from __future__ import annotations

import json
from pathlib import Path

WS = Path(__file__).resolve().parent
RUN = Path(__file__).resolve().parents[3]
W1 = RUN / "round-1/experiment-1/src"
DOSES = (1.5, 2.0, 3.0)  # 3.0 added before freezing: art_a4VkEvYRquBO dose data suggest {1.5,2} may not reach the corrected EN level


def key(p: dict) -> str:
    return json.dumps(p, sort_keys=True)


def main() -> None:
    ia = json.loads((WS / "results/inloop_analysis.json").read_text())
    s96 = json.loads((WS / "inputs/iter1_selection_gemma.json").read_text())
    arms = [{"arm": "A_orig", "role": "orig", "parameters": None, "direction_index": None, "trial": None}]
    arms.append({"arm": "B_keyword_t96", "role": "keyword", "trial": 96, "source": "iteration-1 keyword run",
                 "parameters": s96["abliteration_parameters"], "direction_index": s96["direction_index"], "dose": 1.0,
                 "check_adapter": str(W1 / "adapters/gemma_selected_path2")})
    seen = {key(s96["abliteration_parameters"]): "B_keyword_t96"}
    notes = []
    cs = ia.get("corrected_selection")
    if cs:
        k = key(cs["abliteration_parameters"])
        arms.append({"arm": "C_corrected", "role": "corrected", "trial": cs["trial_number"], "source": "corrected-objective run",
                     "rule_fired": cs["rule_fired"], "parameters": cs["abliteration_parameters"],
                     "direction_index": cs["direction_index"], "dose": 1.0,
                     "means_src": str(WS / "directions/gemma_corrected/residual_means_A.pt"),
                     "export_adapter": "adapters_corrected"})
        if k in seen:
            notes.append(f"C_corrected has the same parameters as {seen[k]}")
        seen[k] = "C_corrected"
    for col, name in (("classifier_refusals", "D_reselected_clf"), ("judge_refused", "D2_reselected_judge")):
        r = ia.get("reselection", {}).get(col)
        if not r:
            continue
        k = key(r["abliteration_parameters"])
        if k in seen:
            notes.append(f"{name} (iteration-1 trial {r['trial_number']}) == {seen[k]}; not re-generated")
            continue
        arms.append({"arm": name, "role": "reselected", "trial": r["trial_number"], "source": f"post-hoc reselection ({col})",
                     "rule_fired": r["rule_fired"], "parameters": r["abliteration_parameters"],
                     "direction_index": r["direction_index"], "dose": 1.0})
        seen[k] = name
    for f in DOSES:
        arms.append({"arm": f"F_dose{f}", "role": "dose", "trial": 96, "source": "LoRA delta of trial 96 x f",
                     "parameters": s96["abliteration_parameters"], "direction_index": s96["direction_index"], "dose": f})
    (WS / "arms.json").write_text(json.dumps(arms, indent=1))
    (WS / "results/arms_notes.json").write_text(json.dumps(notes, indent=1))
    print(json.dumps([{k: a.get(k) for k in ("arm", "role", "trial", "dose", "rule_fired")} for a in arms], indent=1), notes)


if __name__ == "__main__":
    main()
