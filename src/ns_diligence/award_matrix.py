"""Lead-only whistleblower and bounty program comparison matrix.

This module supports the C3 Applied DD Lab. It turns a curated public-authority
CSV into a program comparison table. It does not advise a whistleblower, make an
eligibility determination, or decide disclosure strategy.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AwardProgram:
    """One whistleblower or bounty program comparison row."""

    program_id: str
    program_name: str
    lead_agency: str
    primary_authority: str
    covered_conduct: str
    award_trigger: str
    award_range: str
    filing_or_claim_path: str
    disclosure_timing_issue: str
    diligence_use: str
    escalation_note: str


def classify_program(row: dict[str, str]) -> AwardProgram:
    """Normalize one curated award-program row for comparison output."""

    timing = row.get("disclosure_timing_issue", "").strip()
    escalation = row.get("escalation_note", "").strip()
    if not escalation:
        escalation = "Escalate to counsel before any filing, disclosure, or strategy decision."
    if timing and "120" in timing:
        escalation += " Track the 120-day timing issue."

    return AwardProgram(
        program_id=row.get("program_id", "").strip(),
        program_name=row.get("program_name", "").strip(),
        lead_agency=row.get("lead_agency", "").strip(),
        primary_authority=row.get("primary_authority", "").strip(),
        covered_conduct=row.get("covered_conduct", "").strip(),
        award_trigger=row.get("award_trigger", "").strip(),
        award_range=row.get("award_range", "").strip(),
        filing_or_claim_path=row.get("filing_or_claim_path", "").strip(),
        disclosure_timing_issue=timing,
        diligence_use=row.get("diligence_use", "").strip(),
        escalation_note=escalation,
    )


def build_matrix(input_path: Path, output_path: Path) -> list[AwardProgram]:
    """Build a normalized award-program comparison matrix."""

    with input_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    programs = [classify_program(row) for row in rows]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "program_id",
                "program_name",
                "lead_agency",
                "primary_authority",
                "covered_conduct",
                "award_trigger",
                "award_range",
                "filing_or_claim_path",
                "disclosure_timing_issue",
                "diligence_use",
                "escalation_note",
            ],
        )
        writer.writeheader()
        for program in programs:
            writer.writerow(
                {
                    "program_id": program.program_id,
                    "program_name": program.program_name,
                    "lead_agency": program.lead_agency,
                    "primary_authority": program.primary_authority,
                    "covered_conduct": program.covered_conduct,
                    "award_trigger": program.award_trigger,
                    "award_range": program.award_range,
                    "filing_or_claim_path": program.filing_or_claim_path,
                    "disclosure_timing_issue": program.disclosure_timing_issue,
                    "diligence_use": program.diligence_use,
                    "escalation_note": program.escalation_note,
                }
            )
    return programs


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a lead-only whistleblower program matrix.")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    args = parser.parse_args()
    programs = build_matrix(args.input_csv, args.output_csv)
    print("Award-program matrix complete:", {"programs": len(programs)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
