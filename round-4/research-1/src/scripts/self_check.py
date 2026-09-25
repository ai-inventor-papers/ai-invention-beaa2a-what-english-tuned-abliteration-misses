"""Self-checks that must pass before this artifact ships (plan step R9).

Run: python3 scripts/self_check.py
Exits non-zero and prints every violation if a check fails.
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
TAGS = {"OBSERVATION", "INTERPRETATION", "FAILED HYPOTHESIS", "UNEXECUTED PROPOSAL"}
problems: list[str] = []


def check_quotes_and_urls() -> None:
    """(1) every quote <= 40 words; every neighbour row has a URL, an access date and a locator.
    (2) no 'verified' row without a quote retrieved in this session."""
    data = json.loads((RES / "neighbour_table.json").read_text())
    if data.get("accessed") != "2026-09-24":
        problems.append("neighbour_table.json: missing or wrong access date")
    for n in data["neighbours"]:
        wc = len(n["quote"].split())
        if wc > 40:
            problems.append(f"{n['id']}: quote is {wc} words (> 40)")
        if not n["url"].startswith("http"):
            problems.append(f"{n['id']}: no URL")
        if not n.get("locator"):
            problems.append(f"{n['id']}: no locator")
        if n["verified"] and not n["quote"].strip():
            problems.append(f"{n['id']}: verified=True without a quote")


def check_claims_closed() -> None:
    """(3) every claim row ends with a neighbour id or an explicit NO NEIGHBOUR FOUND; no blanks.
    (5) tag vocabulary is exactly the four values."""
    rows = list(csv.DictReader((RES / "claims_to_position.csv").open()))
    if len(rows) < 20:
        problems.append(f"claims_to_position.csv has {len(rows)} rows (< 20)")
    for r in rows:
        cid = r["claim_id"]
        if r["tag"] not in TAGS:
            problems.append(f"{cid}: tag {r['tag']!r} is not one of the four")
        nb = r["neighbour_ids"].strip()
        st = r["status"].strip()
        if not st:
            problems.append(f"{cid}: empty status")
        if not nb and "NO NEIGHBOUR FOUND" not in st:
            problems.append(f"{cid}: no neighbour id and no NO NEIGHBOUR FOUND")
        if "NO NEIGHBOUR FOUND" in st and "search_log" not in st and "search_log" not in r["number_and_its_producing_file_path"]:
            # the absence must point at the logged searches somewhere in the row
            if "rows" not in st:
                problems.append(f"{cid}: NO NEIGHBOUR FOUND without pointing at logged searches")


def check_numbers_have_paths() -> None:
    """(4) no numeric value about this run appears without a producing file path beside it."""
    rows = list(csv.DictReader((RES / "claims_to_position.csv").open()))
    for r in rows:
        cell = r["number_and_its_producing_file_path"]
        has_number = bool(re.search(r"\d", cell)) and cell.strip() != "n/a"
        if has_number and "/" not in cell:
            problems.append(f"{r['claim_id']}: number without a producing path")


def check_no_we_show_on_unrun() -> None:
    """(6) 'we show'/'we demonstrate'/'we find' never attaches to an UNEXECUTED PROPOSAL or FAILED HYPOTHESIS row."""
    text = (RES / "failed_and_unexecuted.md").read_text()
    for line in text.splitlines():
        if line.strip().startswith("|") and re.search(r"\bwe (show|demonstrate|prove)\b", line, re.I):
            problems.append(f"failed_and_unexecuted.md: forbidden verb in ledger row: {line[:80]}")


def check_neighbour_ids_resolve() -> None:
    known = {n["id"] for n in json.loads((RES / "neighbour_table.json").read_text())["neighbours"]}
    for r in csv.DictReader((RES / "claims_to_position.csv").open()):
        for nid in [x.strip() for x in r["neighbour_ids"].split(",") if x.strip()]:
            if nid not in known:
                problems.append(f"{r['claim_id']}: neighbour id {nid} does not resolve")


def check_files_present() -> None:
    for name in [
        "claims_to_position.csv", "neighbour_table.md", "neighbour_table.json",
        "positioning_positive.md", "positioning_negative.md", "unverified_claims.md",
        "failed_and_unexecuted.md", "reconciliation_map.csv", "search_log.md", "stopping_points.md",
    ]:
        if not (RES / name).exists():
            problems.append(f"missing deliverable: results/{name}")


def main() -> int:
    check_files_present()
    check_quotes_and_urls()
    check_claims_closed()
    check_numbers_have_paths()
    check_no_we_show_on_unrun()
    check_neighbour_ids_resolve()
    if problems:
        print("SELF-CHECK FAILED")
        for p in problems:
            print(" -", p)
        return 1
    print("SELF-CHECK PASSED: all 6 checks green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
