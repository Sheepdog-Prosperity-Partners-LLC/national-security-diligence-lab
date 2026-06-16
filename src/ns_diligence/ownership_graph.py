"""Synthetic ownership aggregation for OFAC 50 Percent Rule teaching."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def load_edges(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def aggregate_flagged_ownership(edges: list[dict[str, str]], target: str) -> float:
    """Aggregate direct synthetic ownership by owners marked flagged=yes.

    This intentionally demonstrates the aggregation idea only. It does not
    resolve indirect ownership, control, trusts, voting rights, or legal status.
    """

    total = 0.0
    for edge in edges:
        if edge.get("owned", "").strip() != target:
            continue
        if edge.get("flagged_owner", "").strip().lower() == "yes":
            total += float(edge.get("percent", "0") or 0)
    return round(total, 4)


def summarize_targets(edges: list[dict[str, str]]) -> list[dict[str, str]]:
    targets = sorted({edge.get("owned", "").strip() for edge in edges if edge.get("owned", "").strip()})
    out: list[dict[str, str]] = []
    owners_by_target: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        if edge.get("owned", "").strip():
            owners_by_target[edge["owned"].strip()].append(edge.get("owner", "").strip())
    for target in targets:
        pct = aggregate_flagged_ownership(edges, target)
        out.append(
            {
                "target": target,
                "flagged_owner_percent": f"{pct:.2f}",
                "ofac_50_percent_teaching_signal": "review" if pct >= 50 else "below_synthetic_threshold",
                "owners_seen": "; ".join(owners_by_target[target]),
                "posture": "synthetic_lead_only",
            }
        )
    return out


def write_summary(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "target",
                "flagged_owner_percent",
                "ofac_50_percent_teaching_signal",
                "owners_seen",
                "posture",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize synthetic flagged ownership percentages.")
    parser.add_argument("ownership_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    args = parser.parse_args()
    rows = summarize_targets(load_edges(args.ownership_csv))
    write_summary(rows, args.output_csv)
    print("Ownership graph complete:", {"rows": len(rows), "output": str(args.output_csv)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
