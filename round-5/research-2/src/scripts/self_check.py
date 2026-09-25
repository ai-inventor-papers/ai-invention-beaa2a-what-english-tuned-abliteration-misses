"""Self-check + table builder for the iteration-5 positioning artifact.

For every row in scripts/rows_*.py it checks:
  1. quote word count <= 40 (plan's hard rule);
  2. for verified_flag == VERIFIED-QUOTE, the quote occurs VERBATIM (after
     whitespace / dash / quote-character normalisation and PDF hyphenation
     repair) in the named file under results/raw/, which is a grep or fetch of
     the primary source;
  3. every CARRIED row names the dependency file it came from;
  4. required fields are present and non-empty.

It then writes the markdown + JSON mirrors of each table. Run:
    python3 scripts/self_check.py
Exit code 0 means every check passed.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RAW = ROOT / "results" / "raw"
sys.path.insert(0, str(HERE))

import rows_c  # noqa: E402
import rows_m  # noqa: E402
import rows_p  # noqa: E402

ACCESS = "2026-09-24"
FIELDS = [
    "id", "claim_positioned", "citation", "quote", "locator", "url",
    "verified_flag", "establishes", "where_this_run_stops", "raw_file",
]
FLAGS = {"VERIFIED-QUOTE", "PARAPHRASE-ONLY", "NOT VERIFIED", "CARRIED"}


def norm(text: str, mode: str = "join") -> str:
    """Normalise for verbatim comparison without weakening it.

    Unifies unicode dashes/quotes, optionally repairs PDF line-break
    hyphenation ("evalu-\\nators" -> "evaluators"), and collapses whitespace.
    It never deletes or reorders words. All three modes are tried, because a
    line break in extracted PDF text can fall inside a word broken by
    hyphenation ("evalu-\\nators", mode "join"), inside a genuinely hyphenated
    name ("Llama-3.1-70B-\\nInstruct", mode "keep"), or between whole words
    (mode "space").
    """
    t = unicodedata.normalize("NFKC", text)
    for ch in "\u2010\u2011\u2012\u2013\u2014\u2015\u2212":
        t = t.replace(ch, "-")
    for ch in "\u2018\u2019\u02bc\u2032":
        t = t.replace(ch, "'")
    for ch in "\u201c\u201d":
        t = t.replace(ch, '"')
    t = t.replace("\u00a0", " ")
    if mode == "join":
        t = re.sub(r"-\s*\n\s*", "", t)     # word broken by hyphenation
    elif mode == "keep":
        t = re.sub(r"-\s*\n\s*", "-", t)    # genuinely hyphenated name
    t = re.sub(r"\s+", " ", t)
    return t.strip().lower()


def check(rows: list[dict], table: str, problems: list[str]) -> None:
    seen: set[str] = set()
    for row in rows:
        rid = row.get("id", "<no id>")
        where = f"{table}:{rid}"
        for field in FIELDS:
            if not str(row.get(field, "")).strip():
                problems.append(f"{where}: empty field {field}")
        if rid in seen:
            problems.append(f"{where}: duplicate id")
        seen.add(rid)
        flag = row.get("verified_flag")
        if flag not in FLAGS:
            problems.append(f"{where}: bad verified_flag {flag!r}")
        words = len(row.get("quote", "").split())
        row["quote_words"] = words
        if words > 40:
            problems.append(f"{where}: quote is {words} words (> 40)")
        row["access_date"] = ACCESS
        raw_name = row.get("raw_file", "")
        if flag == "VERIFIED-QUOTE":
            path = RAW / raw_name
            if not path.exists():
                problems.append(f"{where}: raw file missing: results/raw/{raw_name}")
                continue
            text = path.read_text(errors="replace")
            modes = ("join", "keep", "space")
            hays = [norm(text, m) for m in modes]
            # " [...] " marks a quote that spans a PDF page-break artifact
            # (e.g. an interposed page number); each fragment is checked alone.
            for frag in row["quote"].split(" [...] "):
                if not any(norm(frag, m) in hays[i] for i, m in enumerate(modes)):
                    problems.append(
                        f"{where}: quote fragment NOT found verbatim in results/raw/{raw_name}: {frag[:60]!r}")
        elif flag == "CARRIED":
            if not raw_name.startswith("(dependency)"):
                problems.append(f"{where}: CARRIED row must name the dependency file")


def to_markdown(rows: list[dict], title: str, intro: str) -> str:
    head = ("| id | claim positioned | citation | verbatim quote (<=40 words) | locator | "
            "url | accessed | flag | what the neighbour establishes | where this run stops | raw file |")
    sep = "|" + "---|" * 11
    lines = [f"# {title}", "", intro, "", head, sep]
    for r in rows:
        cells = [
            r["id"], r["claim_positioned"], r["citation"],
            '"' + r["quote"].replace("|", "\\|") + '"',
            r["locator"], r["url"], r["access_date"], r["verified_flag"],
            r["establishes"], r["where_this_run_stops"], f"`results/raw/{r['raw_file']}`",
        ]
        lines.append("| " + " | ".join(str(c).replace("|", "\\|").replace("\n", " ") for c in cells) + " |")
    return "\n".join(lines) + "\n"


def main() -> int:
    problems: list[str] = []
    tables = [
        ("measurement", rows_m.MEASUREMENT, "neighbour_table_measurement",
         "Neighbour table for the MEASUREMENT / selection-blindness result (M rows)",
         "One row per neighbour. Every quote marked VERIFIED-QUOTE was copied from a grep or fetch of the "
         "primary source, saved under `results/raw/`; `scripts/self_check.py` re-checks each one against that "
         "file. Tags: `establishes` is OBSERVATION, `where_this_run_stops` is INTERPRETATION."),
        ("positive", rows_p.POSITIVE, "neighbour_table_positive_additions",
         "Neighbour table ADDITIONS for the placement positive (P rows)",
         "These are the rows added or re-verified this round; the other 30 rows (N1-N30) are carried unchanged "
         "from the dependency and listed in `results/carried_forward.md`. Tags as above."),
        ("consumers", rows_c.CONSUMERS, "consumers",
         "Named consumers of abliterated checkpoints, and the origin credits (C rows)",
         "C1-C5 are the consumers whose designs this run's evidence bears on; C6-C10 credit the compression-era "
         "origin of the English-proxy principle, which this run does NOT claim. Tags as above."),
    ]
    for _key, rows, stem, title, intro in tables:
        check(rows, stem, problems)
        (ROOT / "results" / f"{stem}.md").write_text(to_markdown(rows, title, intro))
        (ROOT / "results" / f"{stem}.json").write_text(json.dumps(
            {"accessed": ACCESS,
             "method": "search (discover) -> fetch (understand) -> grep (extract the quote); a quote may only "
                       "come from a grep/fetch of the primary source; raw extracts in results/raw/",
             "rows": rows}, indent=1, ensure_ascii=False) + "\n")

    allrows = rows_m.MEASUREMENT + rows_p.POSITIVE + rows_c.CONSUMERS
    counts: dict[str, int] = {}
    for r in allrows:
        counts[r["verified_flag"]] = counts.get(r["verified_flag"], 0) + 1
    print(f"rows checked: {len(allrows)}")
    print("flags: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    print(f"max quote words: {max(r['quote_words'] for r in allrows)}")
    if problems:
        print(f"\nFAILED ({len(problems)} problems):")
        for p in problems:
            print("  -", p)
        return 1
    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
