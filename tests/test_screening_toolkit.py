import tempfile
import unittest
from pathlib import Path

from ns_diligence.export_list_screen import filter_bis_rows, screen_against_csl_text
from ns_diligence.fetch_csl import parse_csl_csv
from ns_diligence.fetch_ofac import parse_sdn_csv
from ns_diligence.ownership_graph import aggregate_flagged_ownership, summarize_targets
from ns_diligence.screen_names import normalize_name, score_name, screen_rows


class ScreeningToolkitTests(unittest.TestCase):
    def test_parse_ofac_sdn_csv(self):
        text = '123,"Blocked Example Holdings","SDN","SYNTH",-0-,-0-,-0-,-0-,-0-,-0-,-0-,"remarks"\r\n'
        rows = parse_sdn_csv(text)

        self.assertEqual(rows[0]["name"], "Blocked Example Holdings")
        self.assertEqual(rows[0]["source"], "OFAC SDN")

    def test_parse_csl_and_filter_bis_rows(self):
        text = (
            "_id,source,entity_number,type,programs,name,title,addresses,federal_register_notice,"
            "start_date,end_date,source_information_url\n"
            "1,Entity List,42,Entity,EAR,Redacted Quantum Trading Limited,,Address,,2026-01-01,,https://example.gov\n"
            "2,OFAC SDN,43,Entity,SDN,Blocked Example Holdings,,Address,,2026-01-01,,https://example.gov\n"
        )
        rows = parse_csl_csv(text)
        bis = filter_bis_rows(rows)

        self.assertEqual(len(rows), 2)
        self.assertEqual(len(bis), 1)
        self.assertEqual(bis[0]["name"], "Redacted Quantum Trading Limited")

    def test_screen_rows_exact_and_near_match(self):
        query_rows = [{"name": "Redacted Quantum Trading Ltd"}, {"name": "No Hit LLC"}]
        list_rows = [{"name": "Redacted Quantum Trading Limited", "source": "Fixture BIS Entity List"}]
        results = screen_rows(query_rows, list_rows, threshold=0.80)

        self.assertEqual(results[0].posture, "lead_only")
        self.assertEqual(results[1].posture, "no_current_signal_from_supplied_list")
        self.assertEqual(normalize_name("Redacted, Quantum!"), "redacted quantum")
        self.assertGreater(score_name("Blocked Example Holdings", "Blocked Example Holdings"), 0.99)

    def test_export_list_screen_from_csl_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            query = tmp_path / "query.csv"
            output = tmp_path / "output.csv"
            query.write_text("name\nRedacted Quantum Trading Limited\n", encoding="utf-8")
            csl_text = (
                "_id,source,entity_number,type,programs,name,title,addresses,federal_register_notice,"
                "start_date,end_date,source_information_url\n"
                "1,Entity List,42,Entity,EAR,Redacted Quantum Trading Limited,,Address,,2026-01-01,,https://example.gov\n"
            )

            count = screen_against_csl_text(query, csl_text, output)

            self.assertEqual(count, 1)
            self.assertIn("lead_only", output.read_text(encoding="utf-8"))

    def test_ownership_graph_synthetic_signal(self):
        edges = [
            {"owner": "Blocked A", "owned": "Target", "percent": "30", "flagged_owner": "yes"},
            {"owner": "Blocked B", "owned": "Target", "percent": "25", "flagged_owner": "yes"},
            {"owner": "Ordinary", "owned": "Target", "percent": "45", "flagged_owner": "no"},
        ]

        self.assertEqual(aggregate_flagged_ownership(edges, "Target"), 55.0)
        rows = summarize_targets(edges)
        self.assertEqual(rows[0]["ofac_50_percent_teaching_signal"], "review")


if __name__ == "__main__":
    unittest.main()
