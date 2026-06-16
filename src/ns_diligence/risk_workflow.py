"""Lead-only integrated national-security diligence workflow.

This module supports the D1 Applied DD Lab. It consumes synthetic deal-intake
flags and returns a triage row showing which national-security diligence screens
need review. It does not make legal findings or replace counsel.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


TECH_KEYWORDS = (
    "semiconductor",
    "microelectronics",
    "quantum",
    "artificial intelligence",
    "ai model",
    "advanced computing",
    "encryption",
    "aerospace",
    "defense",
)


def truthy(value: str) -> bool:
    """Return true for simple synthetic yes/no fields."""

    return value.strip().lower() in {"yes", "y", "true", "1"}


def contains_covered_technology(text: str) -> bool:
    """Keyword triage only, not a legal technology determination."""

    lowered = text.lower()
    return any(keyword in lowered for keyword in TECH_KEYWORDS)


@dataclass(frozen=True)
class WorkflowResult:
    """One integrated deal triage output row."""

    deal_id: str
    synthetic_deal_type: str
    risk_tier: str
    triggered_screens: str
    counsel_escalations: str
    immediate_requests: str
    memo_warning: str


def classify_deal(row: dict[str, str]) -> WorkflowResult:
    """Classify one synthetic deal-intake row into lead-only workflow outputs."""

    screens: list[str] = []
    counsel: list[str] = []
    requests: list[str] = []
    severe_flags = 0

    tech_signal = contains_covered_technology(row.get("covered_technology_text", ""))
    country_signal = truthy(row.get("country_of_concern_nexus", ""))

    if truthy(row.get("foreign_buyer", "")) or truthy(row.get("foreign_lp_control_rights", "")):
        screens.append("CFIUS inbound")
        counsel.append("CFIUS counsel")
        requests.append("foreign ownership and governance-rights chart")

    if truthy(row.get("outbound_investment", "")) and (country_signal or tech_signal):
        screens.append("Outbound investment")
        counsel.append("outbound investment counsel")
        requests.append("covered technology and country-nexus memo")

    if truthy(row.get("sanctioned_party_signal", "")):
        screens.append("OFAC sanctions")
        counsel.append("sanctions counsel")
        requests.append("current party list screen and beneficial-ownership support")
        severe_flags += 1

    if truthy(row.get("export_control_signal", "")) or tech_signal:
        screens.append("Export controls")
        counsel.append("export-control counsel")
        requests.append("ECCN, end-use, end-user, and foreign-national access request")

    if truthy(row.get("aml_regulated_target", "")) or truthy(row.get("boi_access_needed", "")):
        screens.append("BSA/AML and BOI")
        counsel.append("AML counsel")
        requests.append("AML program, CDD, source-of-funds, and BOI access posture")

    if truthy(row.get("bulk_sensitive_data", "")) and (
        truthy(row.get("foreign_data_access", "")) or country_signal
    ):
        screens.append("DOJ Data Security Program")
        counsel.append("data-security counsel")
        requests.append("data inventory, bulk-threshold count, and foreign-access map")
        severe_flags += 1

    if truthy(row.get("tainted_capital_signal", "")):
        screens.append("Asset forfeiture")
        counsel.append("forfeiture or white-collar counsel")
        requests.append("source-of-funds trace and asset-proceeds timeline")
        severe_flags += 1

    if truthy(row.get("internal_whistleblower_report", "")):
        screens.append("Whistleblower or bounty routing")
        counsel.append("white-collar and employment counsel")
        requests.append("internal report date, recipient, investigation status, and legal-hold posture")
        severe_flags += 1

    if not screens:
        screens.append("No current national-security screen from supplied synthetic flags")
        requests.append("document no-hit limits and re-screen when identifiers change")

    unique_counsel = sorted(set(counsel))
    unique_requests = list(dict.fromkeys(requests))

    if severe_flags >= 2 or truthy(row.get("sanctioned_party_signal", "")) and truthy(
        row.get("tainted_capital_signal", "")
    ):
        risk_tier = "critical"
    elif len(set(screens)) >= 3 or severe_flags == 1:
        risk_tier = "high"
    elif len(set(screens)) >= 1 and screens[0].startswith("No current") is False:
        risk_tier = "elevated"
    else:
        risk_tier = "baseline"

    return WorkflowResult(
        deal_id=row.get("deal_id", "").strip(),
        synthetic_deal_type=row.get("synthetic_deal_type", "").strip(),
        risk_tier=risk_tier,
        triggered_screens="; ".join(screens),
        counsel_escalations="; ".join(unique_counsel) if unique_counsel else "none from supplied flags",
        immediate_requests="; ".join(unique_requests),
        memo_warning=(
            "Lead-only triage from synthetic flags; verify against source documents and escalate "
            "before any filing, disclosure, classification, sanctions, CFIUS, privacy, or forfeiture conclusion."
        ),
    )


def build_workflow(input_path: Path, output_path: Path) -> list[WorkflowResult]:
    """Build an integrated workflow output from synthetic intake rows."""

    with input_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    results = [classify_deal(row) for row in rows]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "deal_id",
                "synthetic_deal_type",
                "risk_tier",
                "triggered_screens",
                "counsel_escalations",
                "immediate_requests",
                "memo_warning",
            ],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "deal_id": result.deal_id,
                    "synthetic_deal_type": result.synthetic_deal_type,
                    "risk_tier": result.risk_tier,
                    "triggered_screens": result.triggered_screens,
                    "counsel_escalations": result.counsel_escalations,
                    "immediate_requests": result.immediate_requests,
                    "memo_warning": result.memo_warning,
                }
            )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a lead-only integrated diligence triage output.")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    args = parser.parse_args()
    results = build_workflow(args.input_csv, args.output_csv)
    summary: dict[str, int] = {}
    for result in results:
        summary[result.risk_tier] = summary.get(result.risk_tier, 0) + 1
    print("Integrated workflow complete:", summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
