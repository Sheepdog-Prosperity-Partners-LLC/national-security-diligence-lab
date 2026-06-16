import csv
import tempfile
import unittest
from pathlib import Path

from ns_diligence.outbound_triage import screen_csv, screen_record


class OutboundTriageTests(unittest.TestCase):
    def test_screen_record_escalates_when_tech_and_country_nexus_present(self):
        result = screen_record(
            {
                "record_id": "T1",
                "entity_name": "Synthetic AI Company",
                "description": "Develops artificial intelligence model training tools.",
                "country_nexus": "Hong Kong subsidiary.",
                "ownership_notes": "",
            }
        )

        self.assertEqual(result.triage_result, "escalate")
        self.assertTrue(result.country_nexus_flag)
        self.assertIn("artificial_intelligence", result.technology_flags)

    def test_screen_record_reviews_when_only_tech_present(self):
        result = screen_record(
            {
                "record_id": "T2",
                "entity_name": "Synthetic Packaging Company",
                "description": "Advanced packaging for integrated circuit assembly.",
                "country_nexus": "No country nexus.",
                "ownership_notes": "",
            }
        )

        self.assertEqual(result.triage_result, "review")
        self.assertFalse(result.country_nexus_flag)

    def test_screen_record_marks_no_trigger_when_screen_has_no_hits(self):
        result = screen_record(
            {
                "record_id": "T3",
                "entity_name": "Synthetic Logistics Company",
                "description": "Runs marketplace software for grocery wholesalers.",
                "country_nexus": "Argentina and Brazil sales offices only.",
                "ownership_notes": "Synthetic founder-owned company.",
            }
        )

        self.assertEqual(result.triage_result, "no_trigger")
        self.assertIn("No obvious public triage trigger", result.rationale)

    def test_screen_csv_writes_allowed_outcomes_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "input.csv"
            output_path = tmp_path / "output.csv"
            input_path.write_text(
                "record_id,entity_name,description,country_nexus,ownership_notes\n"
                "T1,Synthetic AI,artificial intelligence tools,Hong Kong office,\n"
                "T2,Synthetic Logistics,marketplace software,Argentina sales office,\n",
                encoding="utf-8",
            )

            results = screen_csv(input_path, output_path)

            self.assertEqual(len(results), 2)
            self.assertTrue(output_path.exists())
            with output_path.open(newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            emitted_outcomes = {row["triage_result"] for row in rows}
            self.assertEqual(emitted_outcomes, {"escalate", "no_trigger"})
            self.assertLessEqual(emitted_outcomes, {"no_trigger", "review", "escalate"})


if __name__ == "__main__":
    unittest.main()
