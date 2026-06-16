import tempfile
import unittest
from pathlib import Path

from ns_diligence.remedy_comparison import build_comparison


class RemedyComparisonTests(unittest.TestCase):
    def test_build_comparison_sorts_within_track_and_counts_steps(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "input.csv"
            output_path = tmp_path / "output.csv"
            input_path.write_text(
                "track,matter_label,event_date,event,regime,remedy,posture,source_url\n"
                "Forfeiture recovery track,Case B,2024-01-10,later event,Forfeiture,forfeiture,order,https://example.gov/b\n"
                "CFIUS forced-unwind track,Case A,2012-01-10,second event,CFIUS,forced_unwind,order,https://example.gov/a2\n"
                "CFIUS forced-unwind track,Case A,2012-01-01,first event,CFIUS,mitigation,order,https://example.gov/a1\n",
                encoding="utf-8",
            )

            events = build_comparison(input_path, output_path)

            cfius = [event for event in events if event.track == "CFIUS forced-unwind track"]
            self.assertEqual([event.track_step for event in cfius], [1, 2])
            self.assertEqual(cfius[0].event, "first event")
            self.assertTrue(output_path.exists())


if __name__ == "__main__":
    unittest.main()
