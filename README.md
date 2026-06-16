# National-Security Diligence Lab

Prepared by Noah Green CPA CFE.

Applied DD Lab for the SPP National-Security Diligence Stack. In-tree companion to the article series
(matches the sibling Cross-Border Diligence Atlas convention).

This lab teaches reproducible public-data screening methods for US national-security diligence (OFAC,
BIS, CFIUS public actions, forfeiture timelines). It does not make legal findings, sanctions
determinations, export classifications, or CFIUS opinions.

## Guardrails

- Public or synthetic data only.
- No SPP client, target, or private matter data.
- Outputs are leads, not findings.
- A list hit (SDN, Entity List, CSL) is a lead, not a finding; check the official list and restrictions.
- BOI is never treated as a public bulk dataset (confidential and access-limited).
- Export classification is not automated; code only flags screening-list and diligence-request issues.
- Every real dataset must have source URL, access date, terms or license note, and update method in
  `docs/data_sources.md`.
- Dependencies added only after an OSS-first and non-PRC review.

## Starter layout

```text
src/ns_diligence/          reusable helpers
notebooks/                 optional examples; currently only A2_outbound_triage.ipynb exists
data/sample/               tiny public-shape samples
data/synthetic/            synthetic data for demonstrations
data/redacted_outputs/     publishable outputs
docs/                      data sources, limits, update log
tests/                     offline tests
```

## Active modules

- `outbound_triage.py` - A2 synthetic covered-technology and country-nexus keyword triage (leads only).
- `cfius_reports.py` - A1 annual-report trend and funnel table from public Treasury CFIUS figures.
- `fetch_csl.py` - pull and normalize the Trade.gov Consolidated Screening List CSV.
- `fetch_ofac.py` - pull and normalize the OFAC SDN CSV.
- `screen_names.py` - conservative name screening against supplied lists (leads only).
- `ownership_graph.py` - synthetic UBO ownership graph; apply the OFAC 50 Percent Rule.
- `export_list_screen.py` - BIS-related restricted-party screen from CSL rows.
- `data_threshold_checker.py` - bulk-data threshold checker (EO 14117) on synthetic data.
- `timeline_builder.py` - DOJ forfeiture timeline builder from public releases.
- `risk_workflow.py` - integrated synthetic deal-intake workflow that combines regime flags into a
  lead-only triage row.
- `remedy_comparison.py` - D3 publication-approved public case-data remedy-comparison timeline.

## Current lablet map

This repository is module-backed. It is not currently organized as one notebook per article. The only
notebook present is `notebooks/A2_outbound_triage.ipynb`; the supported runnable surfaces are the
standard-library commands below.

- A2: `ns_diligence.outbound_triage` for covered-technology and country-nexus keyword triage on
  synthetic records.
- A1: `ns_diligence.cfius_reports` for annual-report trend and funnel tables from public Treasury CFIUS
  figures.
- C1: `ns_diligence.data_threshold_checker` for bulk-data threshold triage on synthetic records.
- C2: `ns_diligence.timeline_builder` for public DOJ/Treasury forfeiture timeline tables.
- C3: `ns_diligence.award_matrix` for public whistleblower and bounty program comparison.
- D1: `ns_diligence.risk_workflow` for integrated synthetic deal-intake triage.
- D2: `ns_screen.py`, `ns_diligence.export_list_screen`, `ns_diligence.fetch_csl`,
  `ns_diligence.fetch_ofac`, and `ns_diligence.ownership_graph` for lead-only screening and synthetic
  ownership teaching examples.
- D3: `ns_diligence.remedy_comparison` for publication-approved public remedy-comparison rows.

## Quick start

All commands below run from this repository root. They use only the Python standard library. The smoke
commands write to `/tmp/ns-diligence-lab-smoke` so the checked-in sample outputs are not changed.

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'
```

```bash
PYTHONPATH=src python3 -m compileall -q src tests ns_screen.py
```

Prepare a scratch output directory:

```bash
mkdir -p /tmp/ns-diligence-lab-smoke
```

Run the A1 CFIUS annual-report lablet:

```bash
PYTHONPATH=src python3 -m ns_diligence.cfius_reports \
  data/sample/cfius_annual_report_figures.csv \
  /tmp/ns-diligence-lab-smoke/a1_cfius_public_actions_sample.csv
```

Run the A2 synthetic triage lablet:

```bash
PYTHONPATH=src python3 -m ns_diligence.outbound_triage \
  data/synthetic/a2_outbound_targets.csv \
  /tmp/ns-diligence-lab-smoke/a2_outbound_triage_sample.csv
```

Run the C1 synthetic data-threshold lablet:

```bash
PYTHONPATH=src python3 -m ns_diligence.data_threshold_checker \
  data/synthetic/c1_data_assets.csv \
  /tmp/ns-diligence-lab-smoke/c1_data_threshold_sample.csv
```

Run the C2 public-release forfeiture timeline lablet:

```bash
PYTHONPATH=src python3 -m ns_diligence.timeline_builder \
  data/sample/c2_public_forfeiture_events.csv \
  /tmp/ns-diligence-lab-smoke/c2_forfeiture_timeline_sample.csv
```

Run the C3 whistleblower/bounty program matrix lablet:

```bash
PYTHONPATH=src python3 -m ns_diligence.award_matrix \
  data/sample/c3_whistleblower_programs.csv \
  /tmp/ns-diligence-lab-smoke/c3_bounty_program_matrix.csv
```

Run the D1 integrated workflow lablet:

```bash
PYTHONPATH=src python3 -m ns_diligence.risk_workflow \
  data/synthetic/d1_deal_intake_flags.csv \
  /tmp/ns-diligence-lab-smoke/d1_integrated_workflow_sample.csv
```

Run the D2 capstone name screen on synthetic counterparties and a teaching fixture:

```bash
PYTHONPATH=src python3 ns_screen.py \
  data/synthetic/d2_counterparties.csv \
  data/sample/d2_fixture_screening_list.csv \
  /tmp/ns-diligence-lab-smoke/d2_ns_screen_sample.csv \
  --threshold 0.80
```

Run the D2 BIS-related export-list teaching screen against the fixture list:

```bash
PYTHONPATH=src python3 -m ns_diligence.export_list_screen \
  data/synthetic/d2_counterparties.csv \
  data/sample/d2_fixture_screening_list.csv \
  /tmp/ns-diligence-lab-smoke/d2_export_screen_sample.csv \
  --threshold 0.80
```

Run the D2 synthetic ownership teaching graph:

```bash
PYTHONPATH=src python3 -m ns_diligence.ownership_graph \
  data/synthetic/d2_ownership_edges.csv \
  /tmp/ns-diligence-lab-smoke/d2_ownership_graph_sample.csv
```

Run optional D2 live-source commands against official public endpoints:

```bash
PYTHONPATH=src python3 -m ns_diligence.fetch_csl \
  /tmp/ns-diligence-lab-smoke/live_csl_entity_list_sample.csv \
  --source-filter "Entity List" \
  --limit 25
```

```bash
PYTHONPATH=src python3 -m ns_diligence.fetch_ofac \
  /tmp/ns-diligence-lab-smoke/live_ofac_sdn_sample.csv \
  --limit 25
```

Run the optional D2 live-source smoke tests:

```bash
NS_DILIGENCE_LIVE=1 PYTHONPATH=src python3 -m unittest tests/test_live_sources.py
```

The live tests check only that the official endpoints are reachable and parse into the expected public
data shape. They do not certify legal currency, list completeness, or any particular match.

Run the D3 public remedy-comparison lablet:

```bash
PYTHONPATH=src python3 -m ns_diligence.remedy_comparison \
  data/sample/d3_remedy_comparison_events.csv \
  /tmp/ns-diligence-lab-smoke/d3_remedy_comparison_timeline.csv
```

## Current status

Scaffold plus A1, A2, C1, C2, C3, D1, D2, and D3 modules (2026-06-16). The lab uses only the Python
standard library and writes publishable sample outputs. D2 adds official public-list fetchers, a
lead-only name screen, a BIS-related CSL screen, and a synthetic ownership graph. D3 adds a
publication-approved public case-data remedy-comparison timeline sourced from the separate case-data
matter. Article samples remain redacted, synthetic, or publication-approved public case data;
live-source tests are available for source-shape verification only.
