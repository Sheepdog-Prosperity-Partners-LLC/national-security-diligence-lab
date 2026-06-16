"""Synthetic outbound-investment triage helper.

This module supports the A2 Applied DD Lab. It does not classify a transaction
under 31 CFR Part 850. It flags public or synthetic descriptions that deserve
the full outbound-investment diligence workflow.

Triage outcomes are limited to "no_trigger", "review", and "escalate".
"no_trigger" means no obvious public triage trigger appeared in the supplied
public or synthetic text; it is not a legal determination.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


TECH_KEYWORDS = {
    "semiconductors_microelectronics": [
        "advanced packaging",
        "chip",
        "dram",
        "eda",
        "extreme ultraviolet",
        "integrated circuit",
        "microelectronics",
        "nand",
        "semiconductor",
        "supercomputer",
    ],
    "quantum": [
        "dilution refrigerator",
        "quantum",
        "quantum communication",
        "quantum computer",
        "quantum key distribution",
        "quantum sensing",
    ],
    "artificial_intelligence": [
        "ai",
        "artificial intelligence",
        "computer vision",
        "foundation model",
        "large language model",
        "machine learning",
        "mass surveillance",
        "model training",
    ],
}

COUNTRY_OF_CONCERN_TERMS = [
    "china",
    "chinese",
    "hong kong",
    "macau",
    "prc",
    "people's republic of china",
]


@dataclass(frozen=True)
class TriageResult:
    """One row of triage output."""

    record_id: str
    entity_name: str
    technology_flags: str
    country_nexus_flag: bool
    triage_result: str
    rationale: str


def _contains_any(text: str, terms: list[str]) -> list[str]:
    haystack = text.lower()
    return [term for term in terms if term in haystack]


def screen_record(row: dict[str, str]) -> TriageResult:
    """Screen one synthetic/public description for outbound triage flags."""

    description = " ".join(
        [
            row.get("entity_name", ""),
            row.get("description", ""),
            row.get("country_nexus", ""),
            row.get("ownership_notes", ""),
        ]
    )
    flags: list[str] = []
    matched_terms: list[str] = []
    for category, terms in TECH_KEYWORDS.items():
        hits = _contains_any(description, terms)
        if hits:
            flags.append(category)
            matched_terms.extend(hits)

    country_hits = _contains_any(description, COUNTRY_OF_CONCERN_TERMS)
    country_flag = bool(country_hits)

    if flags and country_flag:
        triage = "escalate"
        rationale = "Covered-technology terms and country-of-concern nexus both appeared."
    elif flags or country_flag:
        triage = "review"
        rationale = "One side of the outbound screen appeared; complete the four-question analysis."
    else:
        triage = "no_trigger"
        rationale = "No obvious public triage trigger appeared in the supplied text."

    if matched_terms or country_hits:
        rationale += " Matched terms: " + ", ".join(sorted(set(matched_terms + country_hits))) + "."

    return TriageResult(
        record_id=row.get("record_id", ""),
        entity_name=row.get("entity_name", ""),
        technology_flags=";".join(flags),
        country_nexus_flag=country_flag,
        triage_result=triage,
        rationale=rationale,
    )


def screen_csv(input_path: Path, output_path: Path) -> list[TriageResult]:
    """Screen a CSV and write a lead-only triage output CSV."""

    with input_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    results = [screen_record(row) for row in rows]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "record_id",
                "entity_name",
                "technology_flags",
                "country_nexus_flag",
                "triage_result",
                "rationale",
            ],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "record_id": result.record_id,
                    "entity_name": result.entity_name,
                    "technology_flags": result.technology_flags,
                    "country_nexus_flag": str(result.country_nexus_flag).lower(),
                    "triage_result": result.triage_result,
                    "rationale": result.rationale,
                }
            )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Run lead-only outbound-investment triage.")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    args = parser.parse_args()
    results = screen_csv(args.input_csv, args.output_csv)
    counts: dict[str, int] = {}
    for result in results:
        counts[result.triage_result] = counts.get(result.triage_result, 0) + 1
    print("Outbound triage complete:", counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
