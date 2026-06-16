import os
import unittest
from unittest import mock
from urllib.error import URLError

from ns_diligence import fetch_csl, fetch_ofac
from ns_diligence.export_list_screen import filter_bis_rows


class _FakeResponse:
    def __init__(self, text: str):
        self.text = text

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return self.text.encode("utf-8")


class FetchRobustnessTests(unittest.TestCase):
    def test_ofac_default_fetch_tries_canonical_then_legacy(self):
        legacy_text = '123,"Blocked Example Holdings","SDN","SYNTH",-0-,-0-,-0-,-0-,-0-,-0-,-0-,"remarks"\n'
        with mock.patch(
            "ns_diligence.fetch_ofac.urlopen",
            side_effect=[URLError("canonical unavailable"), _FakeResponse(legacy_text)],
        ) as mocked_urlopen:
            self.assertEqual(fetch_ofac.parse_sdn_csv(fetch_ofac.fetch_text())[0]["name"], "Blocked Example Holdings")

        requested_urls = [call.args[0].full_url for call in mocked_urlopen.call_args_list]
        self.assertEqual(
            requested_urls,
            [fetch_ofac.OFAC_SDN_CSV_URL, fetch_ofac.OFAC_SDN_CSV_LEGACY_URL],
        )

    def test_ofac_fetch_network_failure_raises_clean_runtime_error(self):
        with mock.patch("ns_diligence.fetch_ofac.urlopen", side_effect=OSError("network down")):
            with self.assertRaisesRegex(fetch_ofac.OFACSourceUnreachable, "OFAC source unreachable"):
                fetch_ofac.fetch_text()

    def test_csl_fetch_network_failure_raises_clean_runtime_error(self):
        with mock.patch("ns_diligence.fetch_csl.urlopen", side_effect=URLError("network down")):
            with self.assertRaisesRegex(fetch_csl.CSLSourceUnreachable, "CSL source unreachable"):
                fetch_csl.fetch_text()

    def test_parsers_skip_eof_control_rows(self):
        ofac_text = (
            '123,"Blocked Example Holdings","SDN","SYNTH",-0-,-0-,-0-,-0-,-0-,-0-,-0-,"remarks"\n'
            "\x1a\n"
        )
        csl_text = (
            "_id,source,entity_number,type,programs,name,title,addresses,federal_register_notice,"
            "start_date,end_date,source_information_url\n"
            "1,Entity List (EL) - Bureau of Industry and Security,42,Entity,EAR,"
            "Redacted Quantum Trading Limited,,Address,,2026-01-01,,https://example.gov\n"
            "\x1a\n"
        )

        self.assertEqual(len(fetch_ofac.parse_sdn_csv(ofac_text)), 1)
        self.assertEqual(len(fetch_csl.parse_csl_csv(csl_text)), 1)


@unittest.skipUnless(os.environ.get("NS_DILIGENCE_LIVE") == "1", "set NS_DILIGENCE_LIVE=1 for live checks")
class LiveSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.csl_rows = fetch_csl.parse_csl_csv(fetch_csl.fetch_text())
        cls.ofac_rows = fetch_ofac.parse_sdn_csv(fetch_ofac.fetch_text())

    def test_trade_csl_live_has_rows(self):
        self.assertGreaterEqual(len(self.csl_rows), 15000)
        self.assertTrue(any(row["name"] for row in self.csl_rows))

    def test_trade_csl_live_has_bis_entity_or_related_rows(self):
        bis_rows = filter_bis_rows(self.csl_rows)
        self.assertGreaterEqual(len(bis_rows), 2000)
        sources = " | ".join(sorted({row.get("source", "") for row in self.csl_rows}))
        self.assertIn("Entity List (EL) - Bureau of Industry and Security", sources)
        self.assertIn("Denied Persons List (DPL) - Bureau of Industry and Security", sources)
        self.assertIn("Specially Designated Nationals (SDN) - Treasury Department", sources)

    def test_ofac_sdn_live_has_rows(self):
        self.assertGreaterEqual(len(self.ofac_rows), 10000)
        self.assertTrue(any(row["name"] for row in self.ofac_rows))

    def test_ofac_sdn_live_row_count_exceeds_threshold(self):
        self.assertGreaterEqual(len(self.ofac_rows), 10000)
        sources = " ".join(row.get("source", "") for row in self.ofac_rows[:100])
        programs = " ".join(row.get("programs", "") for row in self.ofac_rows[:1000])
        self.assertIn("OFAC SDN", sources)
        self.assertIn("CUBA", programs)
        self.assertTrue(any(row.get("uid", "").isdigit() for row in self.ofac_rows[:100]))


if __name__ == "__main__":
    unittest.main()
