"""Lead-only forfeiture timeline builder from public DOJ/Treasury releases.

This module supports the C2 Applied DD Lab. It turns a curated public-release
CSV into a chronological diligence timeline. It does not determine ownership,
traceability, forfeitability, sanctions status, or the truth of allegations.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


POSTURE_TERMS = {
    "allegation_only": ["alleged", "allegation", "complaint", "not proven"],
    "court_order_or_return": ["forfeiture order", "order obtained", "repatriated", "returned"],
    "seizure_or_freeze": ["seizure", "seized", "warrant", "blocked", "frozen", "immobilized"],
    "program_context": ["task force", "program", "reporting requirement"],
}


@dataclass(frozen=True)
class TimelineEvent:
    """One public-release event converted into diligence timeline output."""

    event_date: date
    matter_label: str
    event_type: str
    asset_or_amount: str
    amount_usd: int
    statutory_hook: str
    source_url: str
    posture_label: str
    days_since_prior: int | str
    diligence_note: str


def _parse_date(value: str) -> date:
    return datetime.strptime(value.strip(), "%Y-%m-%d").date()


def _to_int(value: str) -> int:
    cleaned = value.replace(",", "").strip()
    if not cleaned:
        return 0
    try:
        return int(float(cleaned))
    except ValueError:
        return 0


def infer_posture(row: dict[str, str]) -> str:
    """Infer a conservative event posture from curated public-release text."""

    text = " ".join(
        [
            row.get("event_type", ""),
            row.get("allegation_status", ""),
            row.get("source_note", ""),
        ]
    ).lower()
    for posture, terms in POSTURE_TERMS.items():
        if any(term in text for term in terms):
            return posture
    return "source_review"


def _note_for(posture: str, row: dict[str, str]) -> str:
    matter = row.get("matter_label", "matter")
    if posture == "allegation_only":
        return f"Treat {matter} as allegation posture unless a later court order or settlement is sourced."
    if posture == "court_order_or_return":
        return f"Treat {matter} as a sourced order, return, or repatriation event, limited to the cited release."
    if posture == "seizure_or_freeze":
        return f"Treat {matter} as custody, freeze, warrant, or immobilization posture, not final forfeiture."
    if posture == "program_context":
        return f"Treat {matter} as program context, not an asset-specific forfeiture outcome."
    return f"Review the cited source before using {matter} in a risk memo."


def build_timeline(input_path: Path, output_path: Path) -> list[TimelineEvent]:
    """Build a chronological public-release timeline and write output CSV."""

    with input_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    ordered = sorted(rows, key=lambda row: _parse_date(row["event_date"]))
    events: list[TimelineEvent] = []
    prior_date: date | None = None
    for row in ordered:
        event_date = _parse_date(row["event_date"])
        posture = infer_posture(row)
        delta: int | str = "" if prior_date is None else (event_date - prior_date).days
        prior_date = event_date
        events.append(
            TimelineEvent(
                event_date=event_date,
                matter_label=row.get("matter_label", ""),
                event_type=row.get("event_type", ""),
                asset_or_amount=row.get("asset_or_amount", ""),
                amount_usd=_to_int(row.get("amount_usd", "")),
                statutory_hook=row.get("statutory_hook", ""),
                source_url=row.get("source_url", ""),
                posture_label=posture,
                days_since_prior=delta,
                diligence_note=_note_for(posture, row),
            )
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "event_date",
                "matter_label",
                "event_type",
                "asset_or_amount",
                "amount_usd",
                "statutory_hook",
                "source_url",
                "posture_label",
                "days_since_prior",
                "diligence_note",
            ],
        )
        writer.writeheader()
        for event in events:
            writer.writerow(
                {
                    "event_date": event.event_date.isoformat(),
                    "matter_label": event.matter_label,
                    "event_type": event.event_type,
                    "asset_or_amount": event.asset_or_amount,
                    "amount_usd": event.amount_usd,
                    "statutory_hook": event.statutory_hook,
                    "source_url": event.source_url,
                    "posture_label": event.posture_label,
                    "days_since_prior": event.days_since_prior,
                    "diligence_note": event.diligence_note,
                }
            )
    return events


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a lead-only forfeiture public-release timeline.")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    args = parser.parse_args()
    events = build_timeline(args.input_csv, args.output_csv)
    counts: dict[str, int] = {}
    for event in events:
        counts[event.posture_label] = counts.get(event.posture_label, 0) + 1
    print("Forfeiture timeline build complete:", counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
