"""Build the v2 positioning paragraphs by EDITING the dependency's text.

The v2 files are the dependency's paragraphs character-for-character except the
edits enumerated here, each of which is also written into
results/positioning_diff.md. Every replacement anchor must occur exactly once in
the source, or the build fails rather than silently changing the wrong text.

Run: python3 scripts/make_v2.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"

E14 = "round-4/experiment-14/src/results"
E13 = "round-4/experiment-13/src/results"

KEPT_DELTA = (
    "**What this work adds is the consequence of that asymmetry for a persistent weight edit of bounded "
    "size: at matched total removal energy AND matched layer count, WHERE in depth a Heretic-family "
    "English-derived weight edit deposits its removal energy orders how much refusal survives — in English "
    "and in Slovene, in two sibling checkpoints, and in an outside family — while doubling the dose of the "
    "badly placed edit does not buy what the well-placed edit buys at half the energy.** This is an ordering "
    "result on matched contrasts, not a band prescription: the specific layer indices are properties of these "
    "checkpoints at this depth budget, the panels are 2 sibling checkpoints of one architecture plus 1 outside "
    "family, 1–2 optimiser seeds, NF4 with a single bf16 control, and Slovene machine-translated with native "
    "review PENDING."
)

NEW_NEIGHBOUR_SENTENCE = (
    " In weight space the closest published statement is stronger than the draft assumed: a small set of "
    "\"contiguous layers in the middle of the model\" is already reported as safety-critical, located by "
    "layer-wise input-vector analysis and then refined by *scaling the parameter weights of the layers within "
    "the range* and reading an over-rejection count, over four aligned LLMs (Li et al., 2025, arXiv 2408.17003, "
    "ICLR 2025, abstract and §3.4) [OBSERVATION]. That prior work therefore already compares layer RANGES by "
    "editing their weights; what it does not hold fixed is the total removal energy and the layer count, it "
    "amplifies rather than removes, and it is English-only [INTERPRETATION]."
)

EDITS = [
    dict(
        id="E1",
        file="positive",
        anchor=(
            "**What this work adds is the consequence of that asymmetry for a persistent weight edit of bounded "
            "size: holding total removal energy AND the number of edited layers fixed, which contiguous band "
            "carries the energy decides how much refusal survives, and it decides it differently per language "
            "and differently between two sibling checkpoints.**"
        ),
        new=KEPT_DELTA,
        reason=(
            "STRIKES the sibling-difference qualifier and the per-language qualifier, and inserts the "
            "replacement kept-delta sentence plus the stopping sentence. Falsified by this run's own placebos: "
            "art_bxpIbe7-nSvR's DEV argmax named band 25-36 and LOST at matched energy at both levels "
            "(E2: B2 0.50 < B3 0.59; E3: 0.30 < 0.53), the GaMS3 profile predicts Gemma's 50 weight cells at "
            "rho -0.442, no worse than it predicts its own iteration-3 panel (-0.278 screen / -0.111 confirm), "
            "and the A1-A4 ladder shows the two production kernels are indistinguishable once dose is matched "
            "(placement at fixed high E -0.029 [-0.129, +0.071], p 0.774; at fixed low E 0.000 "
            "[-0.086, +0.086], p 1.000)."
        ),
        evidence=f"{E14}/analysis_summary.json; {E14}/report_tables.md (Tables 4, 6, 6b)",
    ),
    dict(
        id="E2",
        file="positive",
        anchor=(
            "| the effective region DIFFERS between two sibling checkpoints of the same architecture | "
            "no neighbour found (search log row 24) | **kept**, and kept descriptive (n = 2) |"
        ),
        new=(
            "| ~~the effective region DIFFERS between two sibling checkpoints of the same architecture~~ | "
            "no neighbour found (search log row 24) — but the qualifier is no longer available | "
            "**DROPPED (falsified by this run's own evidence)**: the DEV-named band LOST at matched energy at "
            "both levels, the sibling's profile predicts the anchor's cells no worse than its own, and the two "
            "production kernels are indistinguishable at matched dose "
            f"(`{E14}/report_tables.md`, Tables 4, 6, 6b, 7) |"
        ),
        reason="Same falsification as E1; the struck row is shown struck rather than deleted.",
        evidence=f"{E14}/report_tables.md (Tables 4, 6, 6b, 7)",
    ),
    dict(
        id="E3",
        file="positive",
        anchor=(
            "**Delta sentence for the abstract:** at matched total removal energy and matched layer count, the "
            "depth band an English-derived refusal edit acts on determines how much refusal survives — "
            "differently per language and differently between two sibling checkpoints — a placement contrast "
            "that the all-layer default of the single-direction literature and the per-language depth "
            "observations of the multilingual-safety literature both leave untested."
        ),
        new=(
            "**Delta sentence for the abstract (v2):** at matched total removal energy and matched layer count, "
            "where in depth an English-derived refusal edit deposits that energy orders how much refusal "
            "survives — in both languages, in two sibling checkpoints and in an outside family, and not "
            "recoverable by doubling the dose of a badly placed edit — a matched-budget placement contrast that "
            "the all-layer default of the single-direction literature, the safety-layer localisation line "
            "(arXiv 2408.17003) and the selection-criterion comparison of the abliteration literature "
            "(arXiv 2607.02714) each leave untested.\n\n"
            "**Language, stated correctly (v2):** the BAND is shared, the RESIDUAL is not. The English causal "
            "write profile predicts the Slovene residual at rho -0.94, so the language-label placebo does not "
            f"collapse (`{E13}/analysis.json`, `language_swapped_O_spearman` = -0.941); what differs by "
            "language is how much refusal is left at the same placement and energy (strict refusal EN 0.07 vs "
            f"SL 0.27 in group G3, `{E13}/report_tables.md`)."
        ),
        reason=(
            "STRIKES the language-conditioned reading of the BAND (falsified by the language-label placebo at "
            "rho -0.94, which does not collapse) while keeping the residual-refusal difference, which is real; "
            "adds the two neighbours that narrow the delta."
        ),
        evidence=f"{E13}/analysis.json; {E13}/report_tables.md",
    ),
    dict(
        id="E4",
        file="positive",
        anchor="| the contrast is at MATCHED total edit size AND MATCHED layer count |",
        new=(
            "| a failed DOSE rival at matched placement: 1.5x and 2x the energy of the badly placed edit do not "
            "reach what the well-placed edit reaches at 1x (SL 0.93 / 0.92 vs 0.27; EN 0.88 / 0.88 vs 0.07; "
            f"`{E13}/report_tables.md`, 'Dose rival (G3)') | no neighbour found by these queries (rows 37, 38, "
            "39, 43); closest is an iso-effect dose-response study under quantisation, not placement "
            "(arXiv 2609.06473) | **kept** |\n"
            "| an outside-family replication (Qwen3-8B; EN, SL, DE) | no neighbour found by these queries "
            "(rows 39, 40); the multi-model abliteration studies compare tools or selection criteria, not "
            f"matched-budget placement (arXiv 2512.13655, 2607.02714) | **kept** (`{E13}/report_tables.md`, "
            "'Outside family') |\n"
            "| the contrast is at MATCHED total edit size AND MATCHED layer count |"
        ),
        reason=(
            "ADDS the two new qualifier rows the round introduced, with their neighbour verdicts filled from "
            "the adversarial searches; both survive as **kept** because no neighbour was found by those queries."
        ),
        evidence=f"{E13}/report_tables.md; results/search_log_iter5.md rows 37-43",
    ),
    dict(
        id="E5",
        file="positive",
        anchor=(
            "For refusal specifically, a 24-model abliteration study reports that uniformly spread layer "
            "selection"
        ),
        new=(
            "For refusal specifically, a 24-model abliteration study reports that uniformly spread layer "
            "selection"
        ),
        after_sentence_insert=NEW_NEIGHBOUR_SENTENCE,
        reason=(
            "ADDS the neighbour that most narrows the positive (arXiv 2408.17003, ICLR 2025: contiguous middle "
            "safety layers, located by a weight-scaling range comparison). Omitting it would be the first thing "
            "a reviewer named. Inserted after the 2608.11583 sentence so the carried text is otherwise untouched."
        ),
        evidence="results/neighbour_table_positive_additions.md rows P1, P2",
    ),
    dict(
        id="E6",
        file="negative",
        anchor=(
            "The closest neighbour on the SELECTION side is AdvPrefix, which shows that a misspecified "
            "objective inside an optimiser produces low loss without the intended behaviour and that repairing "
            "it changes what the search finds (Zhu et al., 2024, §1) [OBSERVATION]."
        ),
        new=(
            "The closest neighbour on the SELECTION side is AdvPrefix, which shows that a misspecified "
            "objective inside an optimiser produces low loss without the intended behaviour and that repairing "
            "it changes what the search finds (Zhu et al., 2024, §1) [OBSERVATION]. **AdvPrefix is the "
            "neighbour for this SELECTION-BLINDNESS companion, not for the placement result; the iteration-4 "
            "draft cites it against the depth finding, and that placement is corrected here** [OBSERVATION]. "
            "Three further neighbours narrow this companion and must be cited beside it: for abliterated models "
            "specifically, \"regex tends to overestimate refusals by flagging templated disclaimers in "
            "otherwise harmless answers\" is already reported over 20 original-and-abliterated systems (arXiv "
            "2510.02768, §4.2), the tool-comparison literature already states the caveat that marker matching "
            "\"can produce false positives (responses that mention safety language while still providing "
            "actionable content)\" (arXiv 2512.13655, §3), and judge reliability under exactly this kind of "
            "distribution shift is the subject of its own audit, which finds that \"attacks distort output "
            "patterns\" and drive judge performance \"to degrade to near random chance\" over 6,642 "
            "human-verified labels (arXiv 2603.06594, abstract) [OBSERVATION]. What remains is narrower and "
            "must be written narrowly: the STRUCTURAL form of the blindness (the keyword floor sits above the "
            "rule's own 10/100 threshold in BOTH searches, so the threshold-blind fraction is 1.00 twice), the "
            "calibration difference between the two searches (K-on-C slope 0.31 vs 0.74, floor 72 vs 16), and "
            "the within-edited agreement collapse of the counter on held-out harm categories (kappa 0.02 EN, "
            "0.00 SL, against a distilled classifier at 0.48 EN / 0.73 SL) "
            "(`iter_4/gen_art/gen_art_experiment_15/results/analysis.json`) [OBSERVATION]. The pre-registered "
            "primary prediction that Gemma's objective is BLINDER than GaMS3's was FALSIFIED (+0.006 "
            "[0.000, 0.019], CI includes zero; judge-referenced the sign reverses to -0.029 [-0.060, -0.005]), "
            "so the paper must not write that selection blindness explains the divergent search outcomes "
            "(same file, `paired_headline`) [FAILED HYPOTHESIS]."
        ),
        reason=(
            "RE-AIMS AdvPrefix at the companion result, adds the three neighbours that narrow it (two of them "
            "on abliterated models specifically), and states the falsified primary prediction beside the "
            "structural finding that survived, so no 'this explains the divergence' reading is available."
        ),
        evidence="iter_4/gen_art/gen_art_experiment_15/results/analysis.json; results/neighbour_table_measurement.md rows M3, M4, M8, M9",
    ),
    dict(
        id="E7",
        file="positive",
        anchor=(
            "| the contrast is at MATCHED total edit size AND MATCHED layer count | no neighbour found running "
            "this construction (search log rows 21, 22) | **kept** — this is the load-bearing qualifier |"
        ),
        new=(
            "| the contrast is at MATCHED total edit size AND MATCHED layer count | no neighbour found running "
            "this construction — not found by these queries (rows 21, 22, 39, 40, 41) — but NARROWED this "
            "round: arXiv 2408.17003 (ICLR 2025) already compares layer RANGES by scaling their weights and "
            "already localises a contiguous mid-depth safety band, without matching energy or layer count, "
            "without a removal edit, and English-only | **kept, narrowed** — it remains the load-bearing "
            "qualifier, but the claim is now only the matched-budget contrast, not the depth localisation |"
        ),
        reason=(
            "The load-bearing qualifier survives but is narrowed by P1/P2; rule 3 requires the narrowing to be "
            "stated in the row rather than argued away."
        ),
        evidence="results/neighbour_table_positive_additions.md rows P1, P2; results/evidenced_absence.md A1",
    ),
    dict(
        id="E8",
        file="negative",
        anchor=(
            "what we could not find stated after the searches logged in `results/search_log.md` "
            "(rows 2, 4, 8, 11, 13, 18, 20, 21)"
        ),
        new=(
            "what we could not find stated after the searches logged in the dependency's log "
            "(`results/_dep_search_log.md`, rows 2, 4, 8, 11, 13, 18, 20, 21) and re-checked in this round's log "
            "(`results/search_log_iter5.md`, rows 42, 43)"
        ),
        reason=(
            "PATH REPAIR plus one coverage statement: the carried text pointed at `results/search_log.md`, which is "
            "the dependency's filename and does not exist in this workspace (it is copied in as "
            "`results/_dep_search_log.md`). The two re-check rows run this round are named so the reader can see "
            "that the absence was probed again, not merely inherited."
        ),
        evidence="results/search_log_iter5.md rows 42, 43; results/evidenced_absence.md A3",
    ),
    dict(
        id="E9",
        file="negative",
        anchor="(engine and date per row in `results/search_log.md`).",
        new="(engine and date per row in `results/_dep_search_log.md`, the dependency's log copied into this workspace).",
        reason="PATH REPAIR: same filename change as E8, in the 'why the absence claim is credible' section.",
        evidence="results/_dep_search_log.md",
    ),
]


def apply_edits(text: str, edits: list[dict]) -> str:
    for e in edits:
        anchor = e["anchor"]
        n = text.count(anchor)
        if n != 1:
            raise SystemExit(f"{e['id']}: anchor occurs {n} times, expected exactly 1:\n{anchor[:110]}")
        if "after_sentence_insert" in e:
            # insert the new sentence at the end of the sentence that ends the
            # paragraph's 2608.11583 clause, i.e. after the next "[OBSERVATION]."
            start = text.index(anchor)
            marker = "[OBSERVATION]."
            end = text.index(marker, start) + len(marker)
            text = text[:end] + e["after_sentence_insert"] + text[end:]
        else:
            text = text.replace(anchor, e["new"], 1)
    return text


def main() -> None:
    out = []
    for which, src, dst in (("positive", "_dep_positive.md", "positioning_positive_v2.md"),
                            ("negative", "_dep_negative.md", "positioning_negative_v2.md")):
        text = (RES / src).read_text()
        edits = [e for e in EDITS if e["file"] == which]
        text = apply_edits(text, edits)
        header = (
            f"<!-- v2. Carried CHARACTER-FOR-CHARACTER from the dependency "
            f"({'art_sZ5w0yoY9o6L results/positioning_' + which + '.md'}) except the edits listed in "
            f"results/positioning_diff.md ({', '.join(e['id'] for e in edits)}). "
            f"Built by scripts/make_v2.py; do not hand-edit. -->\n\n"
        )
        (RES / dst).write_text(header + text)
        out.append(f"{dst}: {len(edits)} edits applied")

    lines = [
        "# Diff: what changed between the dependency's positioning and v2",
        "",
        "Nothing else changed. `scripts/make_v2.py` asserts that each anchor below occurs exactly once in the "
        "dependency file, so a silent edit is impossible; re-running it rebuilds both v2 files from the "
        "dependency text.",
        "",
        "| edit | file | old text (verbatim) | new text (verbatim) | reason | evidence path |",
        "|---|---|---|---|---|---|",
    ]
    for e in EDITS:
        new = e.get("new") if "after_sentence_insert" not in e else e["after_sentence_insert"]
        old = e["anchor"] if "after_sentence_insert" not in e else "(insertion point: end of the sentence beginning \"" + e["anchor"][:60] + "…\")"
        cells = [e["id"], e["file"], old, new, e["reason"], "`" + e["evidence"] + "`"]
        lines.append("| " + " | ".join(str(c).replace("|", "\\|").replace("\n", " ") for c in cells) + " |")
    (RES / "positioning_diff.md").write_text("\n".join(lines) + "\n")
    print("\n".join(out))
    print("positioning_diff.md: %d edits documented" % len(EDITS))


if __name__ == "__main__":
    main()
