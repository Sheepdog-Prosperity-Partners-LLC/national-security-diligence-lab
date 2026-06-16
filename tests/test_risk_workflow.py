import tempfile
import unittest
from pathlib import Path

from ns_diligence.risk_workflow import build_workflow, classify_deal, contains_covered_technology


class RiskWorkflowTests(unittest.TestCase):
    def test_technology_keyword_detection(self):
        self.assertTrue(contains_covered_technology("quantum sensing module"))
        self.assertFalse(contains_covered_technology("ordinary billing workflow"))

    def test_classify_deal_combines_screens(self):
        result = classify_deal(
            {
                "deal_id": "D1-X",
                "synthetic_deal_type": "foreign buyer data target",
                "foreign_buyer": "yes",
                "foreign_lp_control_rights": "no",
                "country_of_concern_nexus": "yes",
                "outbound_investment": "no",
                "covered_technology_text": "personal health data",
                "sanctioned_party_signal": "no",
                "export_control_signal": "no",
                "aml_regulated_target": "no",
                "boi_access_needed": "yes",
                "bulk_sensitive_data": "yes",
                "foreign_data_access": "yes",
                "tainted_capital_signal": "no",
                "internal_whistleblower_report": "no",
            }
        )

        self.assertIn("CFIUS inbound", result.triggered_screens)
        self.assertIn("DOJ Data Security Program", result.triggered_screens)
        self.assertEqual(result.risk_tier, "high")

    def test_build_workflow_writes_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "input.csv"
            output_path = tmp_path / "output.csv"
            input_path.write_text(
                "deal_id,synthetic_deal_type,foreign_buyer,foreign_lp_control_rights,"
                "country_of_concern_nexus,outbound_investment,covered_technology_text,"
                "sanctioned_party_signal,export_control_signal,aml_regulated_target,boi_access_needed,"
                "bulk_sensitive_data,foreign_data_access,tainted_capital_signal,"
                "internal_whistleblower_report\n"
                "D1-TEST,ordinary domestic,no,no,no,no,workflow software,no,no,no,no,no,no,no,no\n",
                encoding="utf-8",
            )

            results = build_workflow(input_path, output_path)

            self.assertEqual(len(results), 1)
            self.assertTrue(output_path.exists())
            self.assertIn("baseline", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
