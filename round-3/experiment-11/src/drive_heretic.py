#!/usr/bin/env python3
"""Non-interactive driver around Heretic @ 3521f864 (the real Heretic code path, not a reimplementation).

Usage:
  python drive_heretic.py <tag> <phase> [--deadline-epoch T] [--batch-size N] [--n-trials N]

  tag   : gams | gemma | smoke        (model + pinned revision from MODELS)
  phase : A      -> fresh study, --n-trials 60 (restart only if checkpoint dir empty)
          B      -> continue finished study, run n_additional_trials (=140, stored in phase-A settings),
                    then apply the frozen selection rule (protocol_selection.json) and export the
                    selected trial as a LoRA adapter through Heretic's own save menu (export path 1).
          RESUME -> continue an interrupted (unfinished) study to its stored n_trials, then select+export.

What the driver adds around heretic.main.run():
  (a) wraps Model.get_residuals_mean -> saves [good_mean, bad_mean] to directions/<tag>/residual_means.pt
  (b) replaces heretic.main.questionary with a scripted stub; each prompt/answer is logged to
      logs/interactive_<tag>_<phase>.jsonl; an unscripted prompt exits with code 3 (never guesses)
  (c) injects an Optuna callback that logs per-trial wall time + peak VRAM and stops the study
      cleanly (study.stop(), no pruned trial) once --deadline-epoch has passed.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

WS = Path(__file__).resolve().parent
MODELS = {
    "gams": ("cjvt/GaMS3-12B-Instruct", "1d0b27af5748784482600d24779409e7e1dc9adc"),
    "gemma": ("google/gemma-3-12b-it", "96b6f1eccf38110c56df3a15bffe176da04bfd80"),
    "smoke": ("google/gemma-3-1b-it", "dcc83ea841ab6100d6b47a070329e1ba4cf78752"),
    # iteration 3 (C3): the corrected-objective run - same model/revision as "gemma"; the objective comes from
    # config.toml in the working directory (runs/corrected_gemma/config.toml), nothing else differs.
    "gemma_corrected": ("google/gemma-3-12b-it", "96b6f1eccf38110c56df3a15bffe176da04bfd80"),
    "gemma_corrected_s2": ("google/gemma-3-12b-it", "96b6f1eccf38110c56df3a15bffe176da04bfd80"),  # second seed (cut_2, run because the clock allowed)
    "smoke_corrected": ("google/gemma-3-1b-it", "dcc83ea841ab6100d6b47a070329e1ba4cf78752"),
}
SEED = 20260923
N_STARTUP = 60
N_ADDITIONAL = 140


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("tag", choices=list(MODELS))
    ap.add_argument("phase", choices=["A", "B", "RESUME"])
    ap.add_argument("--deadline-epoch", type=float, default=float("inf"))
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--n-trials", type=int, default=N_STARTUP)
    ap.add_argument("--n-additional", type=int, default=N_ADDITIONAL)
    ap.add_argument("--ckpt-root", default=str(WS / "checkpoints"))
    ap.add_argument("--no-export", action="store_true")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--stop-at-trials", type=int, default=0,
                    help="stop the study cleanly once this many COMPLETE trials exist (0 = no cap). "
                         "Used to give both siblings an identical trial budget when Heretic's restored "
                         "settings override the CLI n_additional_trials.")
    args = ap.parse_args()

    import optuna
    import torch
    import heretic.main as hm
    import heretic.model as hmod
    from heretic.config import ExportStrategy

    tag, phase = args.tag, args.phase
    repo, sha = MODELS[tag]
    ckpt_dir = Path(args.ckpt_root) / tag
    dir_out = WS / "directions" / tag
    dir_out.mkdir(parents=True, exist_ok=True)
    (WS / "logs").mkdir(exist_ok=True)
    ilog = WS / "logs" / f"interactive_{tag}_{phase}.jsonl"
    tlog = WS / "logs" / f"trials_{tag}.jsonl"
    journal = ckpt_dir / ("".join(c if (c.isalnum() or c in "_-") else "--" for c in repo) + ".jsonl")

    def log_i(rec: dict) -> None:
        rec["t"] = time.time()
        with ilog.open("a") as f:
            f.write(json.dumps(rec, default=str) + "\n")

    # ---------------- (a) residual-mean capture ----------------
    _orig = hmod.Model.get_residuals_mean
    calls: list = []

    def wrapped(self, prompts):
        m = _orig(self, prompts)
        calls.append(m.detach().cpu().clone())
        torch.save({"means": calls, "order": ["good(harmless_alpaca train[:400])", "bad(harmful_behaviors train[:400])"][: len(calls)],
                    "n_prompts": len(prompts), "model": repo, "revision": sha},
                   dir_out / f"residual_means_{phase}.pt")
        log_i({"event": "residual_mean", "call": len(calls), "shape": list(m.shape), "n_prompts": len(prompts)})
        return m

    hmod.Model.get_residuals_mean = wrapped

    # ---------------- (c) trial callback ----------------
    _orig_opt = optuna.study.Study.optimize

    def cb(study, trial):
        rec = {"tag": tag, "phase": phase, "number": trial.number, "state": str(trial.state),
               "values": trial.values, "datetime_start": str(trial.datetime_start),
               "datetime_complete": str(trial.datetime_complete),
               "duration_s": (trial.duration.total_seconds() if trial.duration else None),
               "peak_vram_gb": torch.cuda.max_memory_allocated() / 1e9 if torch.cuda.is_available() else None}
        with tlog.open("a") as f:
            f.write(json.dumps(rec) + "\n")
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
        if time.time() > args.deadline_epoch:
            log_i({"event": "deadline_stop", "after_trial": trial.number})
            study.stop()
        if args.stop_at_trials:
            n_done = sum(1 for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE)
            if n_done >= args.stop_at_trials:
                log_i({"event": "trial_cap_stop", "after_trial": trial.number, "n_complete": n_done})
                study.stop()

    def opt_wrapper(self, func, n_trials=None, **kw):
        kw["callbacks"] = list(kw.get("callbacks") or []) + [cb]
        return _orig_opt(self, func, n_trials=n_trials, **kw)

    optuna.study.Study.optimize = opt_wrapper

    # (d) iteration 3: tell the PartialAwareRefusal scorer which trial it is scoring (Heretic's objective() calls
    #     trial.set_user_attr("index", ...) before abliterate(), so this tags every in-loop log row with its trial).
    import heretic.scorers.partial_aware_refusal as _par
    _orig_sua = optuna.trial.Trial.set_user_attr

    def _sua(self, key, value):
        if key == "index":
            _par.CURRENT_TRIAL.clear()
            _par.CURRENT_TRIAL.update({"trial": self.number, "tag": f"{tag}_{phase}"})
        return _orig_sua(self, key, value)

    optuna.trial.Trial.set_user_attr = _sua

    # ---------------- (b) scripted questionary ----------------
    state = {"trial_menu_calls": 0, "action_menu_calls": 0}
    selection = {}

    def pick_selected_trial(choices):
        """Apply the frozen selection rule (protocol_selection.json) to ALL complete trials."""
        from select_rule import apply_rule
        st = optuna.load_study(study_name="heretic", storage=optuna.storages.JournalStorage(
            optuna.storages.journal.JournalFileBackend(str(journal))))
        res = apply_rule(st)
        selection.update(res)
        target = res["trial_number"]
        for ch in choices:
            v = getattr(ch, "value", None)
            if hasattr(v, "number") and v.number == target:
                return v
        selection["not_on_front"] = True
        return ""

    class Q:
        def __init__(self, kind, message, choices=None, **kw):
            self.kind, self.message, self.choices = kind, message, choices or []

        def _answer(self):
            msg = self.message
            titles = [getattr(c, "title", str(c)) for c in self.choices]
            ans = None
            if msg.startswith("Which trial do you want to use?"):
                state["trial_menu_calls"] += 1
                k = state["trial_menu_calls"]
                if phase == "A":
                    ans = ""
                elif phase == "B" and k == 1:
                    ans = "continue"
                elif (phase == "B" and k == 2) or (phase == "RESUME" and k == 1):
                    ans = "" if args.no_export else pick_selected_trial(self.choices)
                else:
                    ans = ""
            elif msg.startswith("What do you want to do with the decensored model?"):
                state["action_menu_calls"] += 1
                ans = "save" if state["action_menu_calls"] == 1 else ""
            elif msg.startswith("Path to the folder"):
                ans = str(WS / "adapters" / f"{tag}_selected")
            elif msg.startswith("How do you want to export the model?"):
                ans = ExportStrategy.ADAPTER
            elif msg.startswith("How many additional trials"):
                ans = str(args.n_additional)
            if ans is None:
                log_i({"event": "UNSCRIPTED", "kind": self.kind, "message": msg, "choices": titles})
                print(f"UNSCRIPTED PROMPT: {msg}", flush=True)
                sys.exit(3)
            shown = ans.number if hasattr(ans, "number") else ans
            log_i({"event": "prompt", "kind": self.kind, "message": msg, "choices": titles[:50], "answer": shown})
            return ans

        def ask(self, *a, **k):
            return self._answer()

        def unsafe_ask(self, *a, **k):
            return self._answer()

    class QStub:
        def select(self, message, choices=None, **kw):
            return Q("select", message, choices)

        def text(self, message, **kw):
            return Q("text", message)

        def path(self, message, **kw):
            return Q("path", message)

        def password(self, message, **kw):
            return Q("password", message)

        def confirm(self, message, **kw):
            return Q("confirm", message)

        def checkbox(self, message, choices=None, **kw):
            return Q("checkbox", message, choices)

    hm.questionary = QStub()

    # ---------------- argv ----------------
    base = ["heretic", "--model", repo, "--model-commit", sha, "--quantization", "bnb_4bit",
            "--seed", str(args.seed), "--batch-size", str(args.batch_size),
            "--study-checkpoint-dir", str(ckpt_dir)]
    if phase == "A":
        if journal.exists() and journal.stat().st_size > 0:
            print(f"REFUSING phase A: journal exists {journal}", flush=True)
            sys.exit(2)
        ckpt_dir.mkdir(parents=True, exist_ok=True)
        argv = base + ["--n-trials", str(args.n_trials), "--n-additional-trials", str(args.n_additional)]
    else:
        argv = base + ["--checkpoint-action", "continue"]
    log_i({"event": "launch", "argv": argv, "deadline_epoch": args.deadline_epoch})
    sys.argv = argv
    t0 = time.time()
    hm.main()
    log_i({"event": "finished", "wall_s": time.time() - t0, "selection": selection})
    if selection:
        (WS / "results").mkdir(exist_ok=True)
        (WS / "results" / f"selection_{tag}.json").write_text(json.dumps(selection, indent=2, default=str))
    print("DRIVER_DONE", json.dumps(selection, default=str), flush=True)


if __name__ == "__main__":
    main()
