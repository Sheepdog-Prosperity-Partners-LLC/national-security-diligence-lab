"""CFIUS annual-report lablet for the A1 Applied DD Lab.

This module turns a source-located Treasury annual-report fixture into a small
public-actions table. It is aggregate context only; it does not classify a deal,
predict a CFIUS outcome, or make a filing recommendation.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


SOURCE_LOCATOR_FIELDS = ("source_title", "source_url", "source_locator")

A1_2024_FUNNEL_KEYS = [
    "declarations_assessed",
    "notices_reviewed",
    "notices_investigated",
    "notices_withdrawn_after_investigation_began",
    "withdrawn_notices_refiled",
    "notices_rejected",
    "presidential_decisions",
    "notices_with_mitigation_measures_or_conditions",
    "notices_concluded_through_mitigation_agreement",
]

A1_NON_NOTIFIED_KEYS = [
    "potential_non_notified_transactions_considered",
    "non_notified_transactions_investigated",
    "official_inquiries_opened",
    "filing_requests",
    "voluntary_filings_after_outreach",
    "prohibited_by_presidential_order",
]

OUTPUT_FIELDNAMES = [
    "section",
    "year",
    "metric_key",
    "metric_label",
    "value",
    "value_text",
    "unit",
    "diligence_use",
    "source_title",
    "source_url",
    "source_locator",
    "source_note",
]


@dataclass(frozen=True)
class AnnualReportFigure:
    """One source-located annual-report number or report phrase."""

    record_id: str
    article_unit: str
    scope: str
    year: int
    metric_key: str
    metric_label: str
    value: int | None
    value_text: str
    unit: str
    source_title: str
    source_url: str
    source_locator: str
    source_note: str

    @property
    def display_value(self) -> int | str:
        """Return the numeric value when present otherwise the report phrase."""

        if self.value is not None:
            return self.value
        return self.value_text


def _to_int(value: str, field_name: str, row_number: int) -> int | None:
    cleaned = value.replace(",", "").strip()
    if not cleaned:
        return None
    try:
        return int(cleaned)
    except ValueError as exc:
        raise ValueError(f"Row {row_number} has non-integer {field_name}: {value!r}") from exc


def _require(row: dict[str, str], field_name: str, row_number: int) -> str:
    value = row.get(field_name, "").strip()
    if not value:
        raise ValueError(f"Row {row_number} is missing {field_name}")
    return value


def _row_to_figure(row: dict[str, str], row_number: int) -> AnnualReportFigure:
    for field_name in SOURCE_LOCATOR_FIELDS:
        _require(row, field_name, row_number)

    value = _to_int(row.get("value", ""), "value", row_number)
    value_text = row.get("value_text", "").strip()
    if value is None and not value_text:
        raise ValueError(f"Row {row_number} must include value or value_text")

    return AnnualReportFigure(
        record_id=_require(row, "record_id", row_number),
        article_unit=_require(row, "article_unit", row_number),
        scope=_require(row, "scope", row_number),
        year=_to_int(_require(row, "year", row_number), "year", row_number) or 0,
        metric_key=_require(row, "metric_key", row_number),
        metric_label=_require(row, "metric_label", row_number),
        value=value,
        value_text=value_text,
        unit=_require(row, "unit", row_number),
        source_title=_require(row, "source_title", row_number),
        source_url=_require(row, "source_url", row_number),
        source_locator=_require(row, "source_locator", row_number),
        source_note=row.get("source_note", "").strip(),
    )


def load_figures(input_path: Path) -> list[AnnualReportFigure]:
    """Load source-located CFIUS annual-report fixture rows."""

    with input_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [_row_to_figure(row, index) for index, row in enumerate(rows, start=2)]


def declaration_trend(
    figures: list[AnnualReportFigure],
    start_year: int = 2019,
    end_year: int = 2024,
) -> dict[int, int]:
    """Return the declaration count trend for the requested inclusive years."""

    trend = {
        figure.year: figure.value
        for figure in figures
        if figure.scope == "declaration_trend"
        and figure.metric_key == "declarations_assessed"
        and start_year <= figure.year <= end_year
        and figure.value is not None
    }
    return dict(sorted(trend.items()))


def _value_map(
    figures: list[AnnualReportFigure],
    metric_keys: list[str],
    year: int,
) -> dict[str, int | str]:
    by_key = {
        figure.metric_key: figure.display_value
        for figure in figures
        if figure.year == year and figure.metric_key in metric_keys
    }
    missing = [metric_key for metric_key in metric_keys if metric_key not in by_key]
    if missing:
        raise ValueError(f"Missing CFIUS annual-report metrics for {year}: {', '.join(missing)}")
    return {metric_key: by_key[metric_key] for metric_key in metric_keys}


def cfius_2024_funnel(figures: list[AnnualReportFigure]) -> dict[str, int | str]:
    """Return the A1 2024 declarations and notices funnel."""

    return _value_map(figures, A1_2024_FUNNEL_KEYS, 2024)


def non_notified_2024_summary(figures: list[AnnualReportFigure]) -> dict[str, int | str]:
    """Return the A1 2024 non-notified transaction summary."""

    return _value_map(figures, A1_NON_NOTIFIED_KEYS, 2024)


def _diligence_use(scope: str) -> str:
    if scope == "declaration_trend":
        return "Aggregate declaration trend for memo context only; not deal-specific diligence."
    if scope == "filing_funnel":
        return "Aggregate review and remedy base-rate context only; not an outcome prediction."
    if scope == "non_notified":
        return "Aggregate non-notified activity context only; not proof about any target."
    return "Aggregate annual-report context only; verify source before memo use."


def build_public_actions_sample(input_path: Path, output_path: Path) -> list[AnnualReportFigure]:
    """Write the A1 public-actions sample from the annual-report fixture."""

    figures = load_figures(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDNAMES)
        writer.writeheader()
        for figure in figures:
            writer.writerow(
                {
                    "section": figure.scope,
                    "year": figure.year,
                    "metric_key": figure.metric_key,
                    "metric_label": figure.metric_label,
                    "value": "" if figure.value is None else figure.value,
                    "value_text": figure.value_text,
                    "unit": figure.unit,
                    "diligence_use": _diligence_use(figure.scope),
                    "source_title": figure.source_title,
                    "source_url": figure.source_url,
                    "source_locator": figure.source_locator,
                    "source_note": figure.source_note,
                }
            )
    return figures


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the A1 CFIUS annual-report lablet output.")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    args = parser.parse_args()
    figures = build_public_actions_sample(args.input_csv, args.output_csv)
    print(
        "CFIUS annual-report lablet complete:",
        {
            "rows": len(figures),
            "declaration_trend_years": len(declaration_trend(figures)),
            "funnel_metrics": len(cfius_2024_funnel(figures)),
            "non_notified_metrics": len(non_notified_2024_summary(figures)),
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
