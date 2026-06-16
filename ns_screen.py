#!/usr/bin/env python3
"""Capstone lead-only screen for the National-Security Diligence Lab."""

from __future__ import annotations

import argparse
from pathlib import Path

from ns_diligence.screen_names import load_names, screen_rows, write_results


def main() -> int:
    parser = argparse.ArgumentParser(description="Lead-only name screen against a supplied public or fixture list.")
    parser.add_argument("query_csv", type=Path)
    parser.add_argument("list_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("--threshold", type=float, default=0.86)
    args = parser.parse_args()
    results = screen_rows(load_names(args.query_csv), load_names(args.list_csv), args.threshold)
    write_results(results, args.output_csv)
    print("NS screen complete:", {"rows": len(results), "output": str(args.output_csv)})
    print("Reminder: outputs are leads only, not findings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
