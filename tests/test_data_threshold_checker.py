import tempfile
import unittest
from pathlib import Path

from ns_diligence.data_threshold_checker import screen_asset, screen_csv


class DataThresholdCheckerTests(unittest.TestCase):
    def test_screen_asset_flags_bulk_threshold_exceeded(self):
        result = screen_asset(
            {
                "asset_id": "C1",
                "asset_label": "Synthetic genomic file",
                "data_category": "human_genomic_data",
                "us_persons": "125",
                "us_devices": "0",
                "foreign_access_path": "foreign collaborator",
            }
        )

        self.assertEqual(result.threshold_status, "bulk_threshold_exceeded")
        self.assertEqual(result.threshold, 100)
        self.assertIn("foreign collaborator", result.diligence_note)

    def test_screen_asset_flags_near_threshold(self):
        result = screen_asset(
            {
                "asset_id": "C2",
                "asset_label": "Synthetic location SDK",
                "data_category": "precise_geolocation_data",
                "us_persons": "0",
                "us_devices": "920",
                "foreign_access_path": "",
            }
        )

        self.assertEqual(result.threshold_status, "near_threshold")
        self.assertEqual(result.count_basis, "us_devices")

    def test_screen_csv_writes_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "input.csv"
            output_path = tmp_path / "output.csv"
            input_path.write_text(
                "asset_id,asset_label,data_category,us_persons,us_devices,foreign_access_path\n"
                "C1,Synthetic patient portal,personal_health_data,18500,0,offshore vendor\n",
                encoding="utf-8",
            )

            results = screen_csv(input_path, output_path)

            self.assertEqual(len(results), 1)
            self.assertTrue(output_path.exists())
            self.assertIn("bulk_threshold_exceeded", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
