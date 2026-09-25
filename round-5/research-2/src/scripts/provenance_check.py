"""Check that every declared URL matches the URL the quote was actually taken from.

For each row in scripts/rows_*.py and each supporting passage in the structured
output, the quote must occur in a file under results/raw/ whose header records
the SAME url that the row or source declares. This catches the failure mode that
the output verifier caught once: a quote lifted from an arXiv abs page (where a
sentence runs continuously) while the entry cites the PDF (where the same
sentence is broken across lines).

Run: python3 scripts/provenance_check.py
Exit code 0 means every quote's URL matches its extract's URL.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RAW = ROOT / "results" / "raw"
OUT = ROOT / ".terminal_claude_agent_struct_out.json"
sys.path.insert(0, str(HERE))

import rows_c  # noqa: E402
import rows_m  # noqa: E402
import rows_p  # noqa: E402


def raw_index() -> dict[Path, tuple[str, str]]:
    index = {}
    for path in sorted(RAW.glob("*.txt")):
        text = path.read_text(errors="replace")
        m = re.match(r"# (?:grep|fetch) (\S+)", text)
        index[path] = (m.group(1) if m else "", text)
    return index


def main() -> int:
    index = raw_index()
    problems: list[str] = []

    for label, rows in (("rows_m", rows_m.MEASUREMENT),
                        ("rows_p", rows_p.POSITIVE),
                        ("rows_c", rows_c.CONSUMERS)):
        for row in rows:
            if row["verified_flag"] != "VERIFIED-QUOTE":
                continue
            path = RAW / row["raw_file"]
            if path not in index:
                problems.append(f"{label}:{row['id']}: missing raw file {row['raw_file']}")
                continue
            url, _ = index[path]
            if url != row["url"]:
                problems.append(
                    f"{label}:{row['id']}: declares {row['url']} but the extract came from {url}")

    if OUT.exists():
        data = json.loads(OUT.read_text())
        for source in data.get("sources", []):
            for passage in source.get("supporting_passages", []):
                urls = {url for url, text in index.values() if passage["quote"] in text}
                if not urls:
                    problems.append(
                        f"source [{source['index']}]: quote not found in any saved extract")
                elif source["url"] not in urls:
                    problems.append(
                        f"source [{source['index']}]: declares {source['url']} but the quote is in "
                        f"an extract of {sorted(urls)[0]}")

    print(f"raw extracts indexed: {len(index)}")
    if problems:
        print(f"FAILED ({len(problems)} problems):")
        for p in problems:
            print("  -", p)
        return 1
    print("ALL URLS MATCH THEIR EXTRACTS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
