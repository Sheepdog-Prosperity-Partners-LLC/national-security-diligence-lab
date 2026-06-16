"""Lead-only EO 14117 / 28 CFR Part 202 threshold checker.

This module supports the C1 Applied DD Lab. It uses synthetic or public data
asset inventories to flag data categories that meet or approach the bulk
thresholds in 28 CFR 202.205. It does not determine legal coverage,
exemptions, licensing, prohibited status, restricted status, or compliance with
CISA security requirements.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


THRESHOLDS = {
    "human_genomic_data": ("us_persons", 100),
    "human_omic_data": ("us_persons", 1000),
    "biometric_identifiers": ("us_persons", 1000),
    "precise_geolocation_data": ("us_devices", 1000),
    "personal_health_data": ("us_persons", 10000),
    "personal_financial_data": ("us_persons", 10000),
    "covered_personal_identifiers": ("us_persons", 100000),
}


@dataclass(frozen=True)
class ThresholdResult:
    """One data-asset threshold result."""

    asset_id: str
    asset_label: str
    data_category: str
    count_basis: str
    count_value: int
    threshold: int
    threshold_status: str
    foreign_access_path: str
    diligence_note: str


def _to_int(value: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def screen_asset(row: dict[str, str], near_threshold_ratio: float = 0.8) -> ThresholdResult:
    """Classify one synthetic data asset against the configured threshold."""

    category = row.get("data_category", "").strip()
    basis, threshold = THRESHOLDS.get(category, ("unknown", 0))
    count_value = _to_int(row.get(basis, "0")) if basis != "unknown" else 0
    foreign_access = row.get("foreign_access_path", "").strip()

    if threshold == 0:
        status = "unknown_category"
        note = "Data category is not configured; map it to a 28 CFR 202.205 category before relying on it."
    elif count_value > threshold:
        status = "bulk_threshold_exceeded"
        note = "Count is above the bulk threshold; evaluate covered-data-transaction elements and escalate."
    elif count_value >= int(threshold * near_threshold_ratio):
        status = "near_threshold"
        note = "Count is near the bulk threshold; confirm measurement method and update before signing."
    else:
        status = "below_threshold"
        note = "Count is below this threshold in the supplied synthetic record; re-check if counts change."

    if foreign_access:
        note += " Foreign-access path supplied: " + foreign_access + "."

    return ThresholdResult(
        asset_id=row.get("asset_id", ""),
        asset_label=row.get("asset_label", ""),
        data_category=category,
        count_basis=basis,
        count_value=count_value,
        threshold=threshold,
        threshold_status=status,
        foreign_access_path=foreign_access,
        diligence_note=note,
    )


def screen_csv(input_path: Path, output_path: Path) -> list[ThresholdResult]:
    """Screen a CSV of synthetic data assets and write lead-only output."""

    with input_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    results = [screen_asset(row) for row in rows]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "asset_id",
                "asset_label",
                "data_category",
                "count_basis",
                "count_value",
                "threshold",
                "threshold_status",
                "foreign_access_path",
                "diligence_note",
            ],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "asset_id": result.asset_id,
                    "asset_label": result.asset_label,
                    "data_category": result.data_category,
                    "count_basis": result.count_basis,
                    "count_value": result.count_value,
                    "threshold": result.threshold,
                    "threshold_status": result.threshold_status,
                    "foreign_access_path": result.foreign_access_path,
                    "diligence_note": result.diligence_note,
                }
            )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Run lead-only EO 14117 threshold triage.")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    args = parser.parse_args()
    results = screen_csv(args.input_csv, args.output_csv)
    counts: dict[str, int] = {}
    for result in results:
        counts[result.threshold_status] = counts.get(result.threshold_status, 0) + 1
    print("Data-threshold triage complete:", counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
