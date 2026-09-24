#!/usr/bin/env python3
"""results/data_usage.json: every block of the dependency dataset (art_qdUCJWbc5kHh), what this artifact does with it, and
- for the blocks it does NOT open - why. The S5/S6/S7 families are the run's reserved FINAL-evaluation sets; opening them
here would burn them for the evaluation artifact, so common.load_split refuses them and this audit reads only their row
counts from the dataset's own manifest, never their contents."""
from __future__ import annotations

import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import json

from loguru import logger

import common as C
from common import jdump, jload, setup_logging

ROLE = {
    "S1_heretic": ("indirect", "Heretic 3521f864's own direction data. Not opened here: the per-layer directions this "
                               "artifact edits along were built from S3 half A in iteration 2 and are reused frozen; the "
                               "iteration-1 trial-88 adapter that anchors the panel was optimised on S1 by Heretic itself."),
    "S2_semantic": ("not used", "Semantic-Harmful/Harmless. DEV-only in this run and known to overlap Heretic's own S1 "
                                "sources, so it cannot serve as independent validation; iteration 2 already used it for the "
                                "r_prior stability rebuild, which this artifact does not repeat."),
    "S3_jbb": ("PRIMARY", "half A -> the DEV redundancy index (40 harmful + 40 harmless items per language) and the half-A "
                          "residual capture behind the matched random / PC controls; half B harmful (41 pairs) -> the SCREEN "
                          "outcome of every Part B cell."),
    "S3_dolly": ("PRIMARY", "half A -> harmless collateral during control construction; half B -> the 32-token KL of every "
                            "T1/T2 cell against the unedited model."),
    "S3_flores_dev": ("PRIMARY", "half A (first 40 pairs) -> the fluency readout of every Part A arm; half B (83 pairs) -> "
                                 "the FLORES delta-NLL of every Part B cell."),
    "S3_mc": ("PRIMARY", "half B (64 items x EN/SL) -> the teacher-forced multiple-choice utility readout of every T1/T2 "
                         "cell. Half A is unused."),
    "S4_strongreject_pairs": ("PRIMARY", "stratum 'hoc' (held-out Llama-Guard categories) -> the CONFIRMATION outcome: 70 "
                                         "harmful pairs + a frozen 40-item harmless subsample per language, generated only "
                                         "after configs/FREEZE.sha256 was written. Stratum 'ind' was NOT generated (GPU "
                                         "budget) and is reported as not reached."),
    "S5_refuseu": ("RESERVED", "official RefusEU evaluation rows: reserved for the final-evaluation artifact. Never opened "
                               "(common.load_split raises on the S5 prefix)."),
    "S5X_refuseu_crosstrans": ("RESERVED", "the cross-translated RefusEU core for paired cross-language claims: reserved; "
                                           "the plan's optional 'second touch' on the two best cells was NOT taken."),
    "S6_xstest": ("RESERVED", "XSTest over-refusal: reserved. Over-refusal here is measured on the S3/S4 harmless twins "
                              "instead, which are part of the same frozen screen/confirmation sets."),
    "S7_arc_challenge": ("RESERVED", "Slovenian-LLM-Eval utility task: reserved for the final-evaluation artifact."),
    "S7_boolq": ("RESERVED", "Slovenian-LLM-Eval utility task: reserved."),
    "S7_hellaswag": ("RESERVED", "Slovenian-LLM-Eval utility task: reserved."),
    "S7_openbookqa": ("RESERVED", "Slovenian-LLM-Eval utility task: reserved."),
    "S7_piqa": ("RESERVED", "Slovenian-LLM-Eval utility task: reserved."),
    "S7_winogrande": ("RESERVED", "Slovenian-LLM-Eval utility task: reserved. Utility here is the S3 half-B MC readout, "
                                  "flagged in every table as the weaker measure."),
    "S7_flores_devtest": ("RESERVED", "reserved; fluency here uses the S3 FLORES dev split."),
}


def main() -> None:
    setup_logging("data_usage")
    man = jload(C.MANIFEST)
    out = {"dataset": "art_qdUCJWbc5kHh", "workspace": str(C.DATASET),
           "protocol_hash": man.get("protocol_hash"), "blocks": {}}
    for fam, meta in man["splits"].items():
        role, why = ROLE.get(fam, ("not used", "not part of this artifact's protocol"))
        out["blocks"][fam] = {"role": role, "why": why, "n_rows": meta.get("n_rows") or meta.get("n"),
                              "sha256_canonical_sorted_jsonl": meta.get("sha256_canonical_sorted_jsonl"),
                              "verified_this_run": role in ("PRIMARY",)}
    S = C.build_sets(C.load_items())
    out["item_counts_used"] = {k: len(v) for k, v in S.items()}
    out["reserved_guard"] = ("common.load_split asserts the family is in USED_SPLITS and refuses anything starting with "
                             "S5/S6/S7; no row of a reserved block was read by any script in this repository.")
    jdump(out, C.RES / "data_usage.json")
    logger.info(f"data usage written: {sum(1 for b in out['blocks'].values() if b['role'] == 'PRIMARY')} primary blocks, "
                f"{sum(1 for b in out['blocks'].values() if b['role'] == 'RESERVED')} reserved")


if __name__ == "__main__":
    main()
