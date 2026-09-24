#!/usr/bin/env python3
"""GATE 5 - an adversarial test of our own discipline: the confirmation entry point must REFUSE to run when the freeze
is missing or has been tampered with. Both cases are exercised on a scratch copy of configs/ (the real freeze is never
touched), and the result is written to results/gate_freeze.json."""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import common as C
from common import jdump

import method


def run_case(name: str, mutate) -> dict:
    """Point common.CFG at a scratch copy, apply `mutate`, and record whether freeze_ok() raises."""
    with tempfile.TemporaryDirectory() as td:
        scratch = Path(td) / "configs"
        shutil.copytree(C.CFG, scratch)
        mutate(scratch)
        orig = C.CFG
        C.CFG = scratch
        try:
            method.freeze_ok()
            out = {"case": name, "raised": False, "error": None}
        except RuntimeError as e:
            out = {"case": name, "raised": True, "error": str(e)[:160]}
        finally:
            C.CFG = orig
    return out


def main() -> None:
    cases = [
        run_case("missing_FREEZE.sha256", lambda p: (p / "FREEZE.sha256").unlink()),
        run_case("corrupted_frozen_predictions",
                 lambda p: (p / "frozen_predictions.json").write_bytes(
                     (p / "frozen_predictions.json").read_bytes()[:-3] + b"0}")),
        run_case("intact_freeze", lambda p: None),
    ]
    out = {"cases": cases,
           "guard_works": bool(cases[0]["raised"] and cases[1]["raised"] and not cases[2]["raised"])}
    jdump(out, C.RES / "gate_freeze.json")
    print(out)


if __name__ == "__main__":
    main()
