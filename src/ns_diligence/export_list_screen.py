"""Lead-only export restricted-party screen using normalized CSL rows."""

from __future__ import annotations

import argparse
from pathlib import Path

from ns_diligence.fetch_csl import parse_csl_csv
from ns_diligence.screen_names import load_names, screen_rows, write_results


BIS_SOURCE_TERMS = ("Entity List", "Denied Persons", "Unverified List", "Military End User")


def filter_bis_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    filtered: list[dict[str, str]] = []
    for row in rows:
        source = row.get("source", "")
        if any(term.lower() in source.lower() for term in BIS_SOURCE_TERMS):
            filtered.append(row)
    return filtered


def screen_against_csl_text(query_csv: Path, csl_text: str, output_csv: Path, threshold: float = 0.86) -> int:
    bis_rows = filter_bis_rows(parse_csl_csv(csl_text))
    results = screen_rows(load_names(query_csv), bis_rows, threshold)
    write_results(results, output_csv)
    return len(results)


def main() -> int:
    parser = argparse.ArgumentParser(description="Lead-only export restricted-party screen from CSL CSV.")
    parser.add_argument("query_csv", type=Path)
    parser.add_argument("csl_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("--threshold", type=float, default=0.86)
    args = parser.parse_args()
    count = screen_against_csl_text(args.query_csv, args.csl_csv.read_text(encoding="utf-8"), args.output_csv, args.threshold)
    print("Export list screen complete:", {"rows": count, "output": str(args.output_csv)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
