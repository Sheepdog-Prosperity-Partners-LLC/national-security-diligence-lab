import tempfile
import unittest
from pathlib import Path

from ns_diligence.award_matrix import build_matrix, classify_program


class AwardMatrixTests(unittest.TestCase):
    def test_classify_program_adds_timing_escalation(self):
        result = classify_program(
            {
                "program_id": "DOJ",
                "program_name": "DOJ pilot",
                "lead_agency": "DOJ",
                "primary_authority": "28 U.S.C. 524(c)",
                "covered_conduct": "corporate sanctions offenses",
                "award_trigger": "forfeiture",
                "award_range": "up to 30 percent",
                "filing_or_claim_path": "intake",
                "disclosure_timing_issue": "120-day issue",
                "diligence_use": "routing",
                "escalation_note": "Escalate.",
            }
        )

        self.assertIn("120-day", result.escalation_note)

    def test_build_matrix_writes_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "input.csv"
            output_path = tmp_path / "output.csv"
            input_path.write_text(
                "program_id,program_name,lead_agency,primary_authority,covered_conduct,award_trigger,"
                "award_range,filing_or_claim_path,disclosure_timing_issue,diligence_use,escalation_note\n"
                "AML,FinCEN AML,FinCEN,31 U.S.C. 5323,BSA,monetary sanctions,10 to 30 percent,"
                "FinCEN process,final rule pending,routing,\n",
                encoding="utf-8",
            )

            programs = build_matrix(input_path, output_path)

            self.assertEqual(len(programs), 1)
            self.assertTrue(output_path.exists())
            self.assertIn("FinCEN AML", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
