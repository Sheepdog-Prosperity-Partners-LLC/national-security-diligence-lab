import tempfile
import unittest
from pathlib import Path

from ns_diligence.timeline_builder import build_timeline, infer_posture


class TimelineBuilderTests(unittest.TestCase):
    def test_infer_posture_preserves_allegation_only(self):
        posture = infer_posture(
            {
                "event_type": "civil forfeiture complaint",
                "allegation_status": "complaint allegations not proven",
                "source_note": "allegations are not proven until judgment",
            }
        )

        self.assertEqual(posture, "allegation_only")

    def test_build_timeline_sorts_and_calculates_days(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "input.csv"
            output_path = tmp_path / "output.csv"
            input_path.write_text(
                "event_date,matter_label,event_type,asset_or_amount,amount_usd,statutory_hook,"
                "allegation_status,source_url,source_note\n"
                "2023-01-10,Later order,forfeiture order,asset,100,civil forfeiture,order obtained,"
                "https://example.gov/later,order obtained\n"
                "2023-01-01,Earlier complaint,civil forfeiture complaint,asset,100,civil forfeiture,"
                "complaint allegations not proven,https://example.gov/earlier,not proven\n",
                encoding="utf-8",
            )

            events = build_timeline(input_path, output_path)

            self.assertEqual([event.matter_label for event in events], ["Earlier complaint", "Later order"])
            self.assertEqual(events[0].posture_label, "allegation_only")
            self.assertEqual(events[1].days_since_prior, 9)
            self.assertTrue(output_path.exists())


if __name__ == "__main__":
    unittest.main()
