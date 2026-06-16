"""Simple lead-only name screening helpers.

This module intentionally uses conservative standard-library matching. It is a
teaching aid, not a sanctions screening system.
"""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path


WORD_RE = re.compile(r"[^a-z0-9]+")


def normalize_name(name: str) -> str:
    lowered = name.lower().strip()
    normalized = WORD_RE.sub(" ", lowered)
    return " ".join(normalized.split())


def score_name(query: str, candidate: str) -> float:
    q = normalize_name(query)
    c = normalize_name(candidate)
    if not q or not c:
        return 0.0
    if q == c:
        return 1.0
    if q in c or c in q:
        return 0.92
    return SequenceMatcher(None, q, c).ratio()


@dataclass(frozen=True)
class ScreenResult:
    query_name: str
    candidate_name: str
    source: str
    score: float
    posture: str


def load_names(path: Path, name_field: str = "name") -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def screen_rows(
    query_rows: list[dict[str, str]],
    list_rows: list[dict[str, str]],
    threshold: float = 0.86,
) -> list[ScreenResult]:
    results: list[ScreenResult] = []
    for query in query_rows:
        query_name = (query.get("name") or "").strip()
        best: ScreenResult | None = None
        for row in list_rows:
            candidate_name = (row.get("name") or "").strip()
            score = score_name(query_name, candidate_name)
            if score >= threshold and (best is None or score > best.score):
                best = ScreenResult(
                    query_name=query_name,
                    candidate_name=candidate_name,
                    source=(row.get("source") or "").strip(),
                    score=round(score, 4),
                    posture="lead_only",
                )
        if best:
            results.append(best)
        else:
            results.append(
                ScreenResult(
                    query_name=query_name,
                    candidate_name="",
                    source="",
                    score=0.0,
                    posture="no_current_signal_from_supplied_list",
                )
            )
    return results


def write_results(results: list[ScreenResult], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["query_name", "candidate_name", "source", "score", "posture"],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "query_name": result.query_name,
                    "candidate_name": result.candidate_name,
                    "source": result.source,
                    "score": f"{result.score:.4f}",
                    "posture": result.posture,
                }
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Lead-only name screen against a normalized CSV list.")
    parser.add_argument("query_csv", type=Path)
    parser.add_argument("list_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("--threshold", type=float, default=0.86)
    args = parser.parse_args()
    results = screen_rows(load_names(args.query_csv), load_names(args.list_csv), args.threshold)
    write_results(results, args.output_csv)
    print("Name screen complete:", {"rows": len(results), "output": str(args.output_csv)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
