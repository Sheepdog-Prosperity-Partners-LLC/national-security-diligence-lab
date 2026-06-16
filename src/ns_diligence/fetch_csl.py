"""Fetch and normalize the Trade.gov Consolidated Screening List.

The Consolidated Screening List is an official public data aid. A hit is a
lead, not a finding, and users must check the official list and restrictions.
"""

from __future__ import annotations

import argparse
import csv
import sys
import urllib.error
from pathlib import Path
from urllib.request import Request, urlopen


CSL_CSV_URL = "https://data.trade.gov/downloadable_consolidated_screening_list/v1/consolidated.csv"


class CSLSourceUnreachable(RuntimeError):
    """Raised when the CSL endpoint cannot be reached."""


def fetch_text(url: str = CSL_CSV_URL, timeout: int = 30) -> str:
    req = Request(url, headers={"User-Agent": "ns-diligence-lab/0.1"})
    try:
        with urlopen(req, timeout=timeout) as response:
            return response.read().decode("utf-8-sig", errors="replace")
    except (urllib.error.URLError, OSError) as exc:
        raise CSLSourceUnreachable("CSL source unreachable; try again later") from exc


def _has_visible_text(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, list):
        return any(_has_visible_text(item) for item in value)
    return bool("".join(ch for ch in str(value) if ch.isprintable()).strip())


def _is_control_row(row: dict[str | None, object]) -> bool:
    return not any(_has_visible_text(value) for value in row.values())


def parse_csl_csv(text: str, source_filter: str | None = None, limit: int | None = None) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for row in csv.DictReader(text.splitlines()):
        if _is_control_row(row):
            continue
        source = (row.get("source") or "").strip()
        if source_filter and source_filter.lower() not in source.lower():
            continue
        normalized.append(
            {
                "source": source,
                "name": (row.get("name") or "").strip(),
                "type": (row.get("type") or "").strip(),
                "programs": (row.get("programs") or "").strip(),
                "addresses": (row.get("addresses") or "").strip(),
                "source_information_url": (row.get("source_information_url") or "").strip(),
                "federal_register_notice": (row.get("federal_register_notice") or "").strip(),
            }
        )
        if limit is not None and len(normalized) >= limit:
            break
    return normalized


def write_rows(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "source",
        "name",
        "type",
        "programs",
        "addresses",
        "source_information_url",
        "federal_register_notice",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch and normalize the Trade.gov CSL CSV.")
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("--url", default=CSL_CSV_URL)
    parser.add_argument("--source-filter", default=None)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    try:
        text = fetch_text(args.url)
    except CSLSourceUnreachable as exc:
        print(exc, file=sys.stderr)
        return 1
    rows = parse_csl_csv(text, args.source_filter, args.limit)
    write_rows(rows, args.output_csv)
    print("CSL rows written:", {"rows": len(rows), "output": str(args.output_csv)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
