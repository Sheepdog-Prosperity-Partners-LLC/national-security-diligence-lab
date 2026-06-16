"""Build a side-by-side remedy timeline from publication-approved public case rows.

This module supports D3. It compares procedural path and remedy type. It does
not determine liability, national-security risk, ownership, or forfeitability.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


TRACK_QUESTIONS = {
    "CFIUS forced-unwind track": "What ownership, control, location, data, or rights fact should have been escalated before close?",
    "Forfeiture recovery track": "What funds-flow, source-of-funds, asset-tracing, or allegation posture should have been preserved?",
}


@dataclass(frozen=True)
class RemedyEvent:
    event_date: date
    track: str
    matter_label: str
    event: str
    regime: str
    remedy: str
    posture: str
    source_url: str
    track_step: int
    diligence_question: str


def _parse_date(value: str) -> date:
    return datetime.strptime(value.strip(), "%Y-%m-%d").date()


def build_comparison(input_path: Path, output_path: Path) -> list[RemedyEvent]:
    with input_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    ordered = sorted(rows, key=lambda row: (row.get("track", ""), _parse_date(row["event_date"])))
    track_counts: dict[str, int] = {}
    events: list[RemedyEvent] = []
    for row in ordered:
        track = row.get("track", "")
        track_counts[track] = track_counts.get(track, 0) + 1
        events.append(
            RemedyEvent(
                event_date=_parse_date(row["event_date"]),
                track=track,
                matter_label=row.get("matter_label", ""),
                event=row.get("event", ""),
                regime=row.get("regime", ""),
                remedy=row.get("remedy", ""),
                posture=row.get("posture", ""),
                source_url=row.get("source_url", ""),
                track_step=track_counts[track],
                diligence_question=TRACK_QUESTIONS.get(track, "What fact should the diligence file preserve?"),
            )
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "track",
                "track_step",
                "event_date",
                "matter_label",
                "event",
                "regime",
                "remedy",
                "posture",
                "diligence_question",
                "source_url",
            ],
        )
        writer.writeheader()
        for event in events:
            writer.writerow(
                {
                    "track": event.track,
                    "track_step": event.track_step,
                    "event_date": event.event_date.isoformat(),
                    "matter_label": event.matter_label,
                    "event": event.event,
                    "regime": event.regime,
                    "remedy": event.remedy,
                    "posture": event.posture,
                    "diligence_question": event.diligence_question,
                    "source_url": event.source_url,
                }
            )
    return events


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a publication-approved public remedy-comparison timeline.")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    args = parser.parse_args()
    events = build_comparison(args.input_csv, args.output_csv)
    counts: dict[str, int] = {}
    for event in events:
        counts[event.track] = counts.get(event.track, 0) + 1
    print("Remedy comparison complete:", counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
