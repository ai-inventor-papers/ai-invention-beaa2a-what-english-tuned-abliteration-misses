#!/usr/bin/env bash
# The exact chain this artifact was produced with (each stage resumable; PID-based management, never by name).
set -e
PY=.venv/bin/python
$PY method.py --stage smoke                     # gates 0/1/3/4, controls, energy table, timing model
$PY method.py --stage profile                   # the 48 single-layer DEV write probes (+ the strength pilot)
$PY judge_local.py --root results/cells         # blind local Qwen3-14B labels for everything generated so far
$PY freeze.py                                   # e_L(h) -> O -> confirmation cells -> configs/FREEZE.sha256
$PY method.py --stage reuse                     # re-label (never regenerate) the iteration-3 anchors A1, A2, no-op, G1
$PY screen.py                                   # zero-GPU screen on 57 GaMS3 + 122 sibling cells
$PY method.py --stage confirm                   # the frozen confirmation panel, controls and the A3/A4 twins
$PY judge_local.py --root results/cells         # label the confirmation generations
$PY cert_pool.py                                # free certification against the gpt-4.1 labels already on disk
$PY certify.py --n 600                          # gpt-4.1 stratified certification of the local judge (cap $3)
$PY gate_freeze_test.py                         # GATE 5: the freeze guard, tested adversarially
$PY third_channel.py                            # the free third label channel on this pod's own generations
$PY analysis.py && $PY rederive.py              # analysis + the independent re-derivation and placebos
$PY make_deviations.py && $PY report_tables.py && $PY figures.py && $PY build_output.py
$PY make_cells_csv.py && $PY make_readme.py
