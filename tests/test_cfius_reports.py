import csv
import tempfile
import unittest
from pathlib import Path

from ns_diligence.cfius_reports import (
    build_public_actions_sample,
    cfius_2024_funnel,
    declaration_trend,
    load_figures,
    non_notified_2024_summary,
)


LAB_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = LAB_ROOT / "data" / "sample" / "cfius_annual_report_figures.csv"


class CfiusReportsTests(unittest.TestCase):
    def test_fixture_reproduces_a1_declaration_trend(self):
        figures = load_figures(FIXTURE)

        self.assertEqual(
            declaration_trend(figures),
            {
                2019: 94,
                2020: 126,
                2021: 164,
                2022: 154,
                2023: 109,
                2024: 116,
            },
        )

    def test_fixture_reproduces_a1_2024_funnel(self):
        figures = load_figures(FIXTURE)

        self.assertEqual(
            cfius_2024_funnel(figures),
            {
                "declarations_assessed": 116,
                "notices_reviewed": 209,
                "notices_investigated": 116,
                "notices_withdrawn_after_investigation_began": 49,
                "withdrawn_notices_refiled": 42,
                "notices_rejected": 1,
                "presidential_decisions": 2,
                "notices_with_mitigation_measures_or_conditions": 25,
                "notices_concluded_through_mitigation_agreement": 16,
            },
        )

    def test_fixture_reproduces_a1_non_notified_summary(self):
        figures = load_figures(FIXTURE)

        self.assertEqual(
            non_notified_2024_summary(figures),
            {
                "potential_non_notified_transactions_considered": "thousands",
                "non_notified_transactions_investigated": 98,
                "official_inquiries_opened": 76,
                "filing_requests": 12,
                "voluntary_filings_after_outreach": 5,
                "prohibited_by_presidential_order": 1,
            },
        )

    def test_each_fixture_row_has_source_locator_fields(self):
        figures = load_figures(FIXTURE)

        self.assertGreater(len(figures), 0)
        for figure in figures:
            self.assertTrue(figure.source_title)
            self.assertTrue(figure.source_url)
            self.assertTrue(figure.source_locator)

    def test_build_public_actions_sample_preserves_source_locators(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "a1_cfius_public_actions_sample.csv"

            figures = build_public_actions_sample(FIXTURE, output_path)

            self.assertEqual(len(figures), 20)
            with output_path.open(newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 20)
            self.assertEqual(rows[0]["metric_key"], "declarations_assessed")
            self.assertEqual(rows[0]["value"], "94")
            self.assertTrue(rows[0]["source_title"])
            self.assertTrue(rows[0]["source_url"])
            self.assertTrue(rows[0]["source_locator"])


if __name__ == "__main__":
    unittest.main()
