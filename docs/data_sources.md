# Data Sources

Prepared by Noah Green CPA CFE.

Every real dataset used by a lab module or notebook is recorded here before use. Synthetic data is
labeled synthetic and needs no source.

Record per dataset: name; official source URL; access date; terms or license note; update method;
identifiers/fields; lab use; no-hit interpretation.

## Public lists and federal datasets

- OFAC SDN CSV: https://www.treasury.gov/ofac/downloads/sdn.csv. Access date: 2026-06-16. Terms or
  license note: public United States Treasury dataset; users must verify current list status and
  restrictions on official OFAC pages before relying on any hit. Update method: re-pull before each
  live screening exercise and record access date. Lab use: demonstrate lead-only sanctions list
  screening. No-hit interpretation: no current signal from the supplied list snapshot only.
- OFAC Sanctions List Service SDN export:
  https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV. Access date:
  2026-06-16. Terms or license note: public United States Treasury sanctions-list export. Update method:
  use as a service-backed alternative if the legacy SDN CSV endpoint changes. Lab use: source
  availability cross-check, not article sample output.
- Trade.gov Consolidated Screening List CSV:
  https://data.trade.gov/downloadable_consolidated_screening_list/v1/consolidated.csv. Access date:
  2026-06-16. Terms or license note: public International Trade Administration dataset; Trade.gov
  describes CSL as a screening aid, and users still need to check official source lists and restriction
  details. Update method: re-pull before live-source tests and quarterly maintenance. Lab use:
  demonstrate screening-list aggregation and BIS-related restricted-party filtering. No-hit
  interpretation: no current signal from the supplied CSL snapshot only.
- Trade.gov Consolidated Screening List landing page:
  https://www.trade.gov/consolidated-screening-list. Access date: 2026-06-16. Terms or license note:
  official source-description page for the CSL. Update method: re-check page text and download links
  during quarterly maintenance. Lab use: source authority and limitation note.
- BIS Entity List legal source:
  https://www.ecfr.gov/current/title-15/subtitle-B/chapter-VII/subchapter-C/part-744/appendix-Supplement%20No.%204%20to%20Part%20744.
  Access date: 2026-06-16. Terms or license note: official eCFR text. Update method: verify current
  eCFR version and Federal Register amendments before publication or quarterly refresh. Lab use:
  authority for explaining that a CSL/BIS hit is not export classification.
- BIS Part 744 official page: https://www.bis.gov/regulations/ear/744. Access date: 2026-06-16. Terms
  or license note: official BIS regulatory page. Update method: verify for current BIS guidance and
  links during quarterly maintenance. Lab use: regulatory context for Entity List and related party
  restrictions.
- USAspending / SAM.gov: public procurement and exclusions sources. Access date: not used by the D2
  capstone code sample. Terms or license note: add before any future enrichment module. Lab use:
  candidate enrichment source for procurement and exclusion history only.
- `data/sample/cfius_annual_report_figures.csv`: Treasury CFIUS Annual Report to Congress for CY 2024
  figures, with source locator fields carried row by row. Source URL:
  https://home.treasury.gov/system/files/206/2024-CFIUS-Annual-Report.pdf. Access date: 2026-06-16.
  Terms or license note: public United States Treasury report. Update method: re-check the current
  Treasury CFIUS reports page and annual-report PDF before publication or quarterly refresh. Lab use:
  reproduce the A1 aggregate trend and funnel table. No-hit interpretation: not applicable, this is an
  aggregate report fixture.

## Curated public-release datasets

- `data/sample/c2_public_forfeiture_events.csv`: curated public DOJ/Treasury release timeline for the
  C2 forfeiture lablet. Official source URLs are stored row by row in the CSV. Access date: 2026-06-15.
  Terms or license note: United States Government public web releases; verify current page status before
  reuse. Update method: re-check DOJ/Treasury release URLs and add later orders, settlements,
  repatriations, or corrected amounts during quarterly refresh. Lab use: demonstrate chronology,
  allegation-versus-order posture, and freeze/seizure/forfeiture distinction. No-hit interpretation:
  absence from the curated CSV means only that the event was not manually selected for the teaching
  sample.
- `data/sample/c3_whistleblower_programs.csv`: curated public authority matrix for FCA, SEC, CFTC,
  FinCEN AML, and DOJ Corporate Whistleblower Awards Pilot Program. Official source authorities are
  stored by program row. Access date: 2026-06-15. Terms or license note: federal public authority and
  public program pages; verify current program pages before reuse. Update method: re-check DOJ pilot
  guidance, FinCEN final-rule status, SEC/CFTC program pages, and U.S. Code rows during quarterly
  refresh. Lab use: demonstrate program-routing questions, not eligibility.
- `data/sample/d3_remedy_comparison_events.csv`: publication-approved public case-data sample for D3,
  built from the separate `case_data_matter/` source logs. Access date: 2026-06-16. Terms or license note: public
  federal sources and SEC filings; Ralls and 1MDB rows are primary-source anchors; Grindr/Kunlun remains
  caveated where no public CFIUS divestiture order was located. Update method: recheck the case-data
  matter, DOJ 1MDB releases, Ralls sources, SEC filings, and publication-approval log before reuse.
  Lab use: demonstrate remedy-path comparison, not liability.

## Synthetic datasets

- `data/synthetic/a2_outbound_targets.csv`: synthetic outbound-investment triage records for the A2
  lablet. No real company names, client data, target data, private records, or allegations. Created
  2026-06-15. Update method: edit synthetic examples when the A2 article or Part 850 vocabulary changes.
  Lab use: demonstrate lead-only covered-technology and country-nexus keyword triage.
- `data/synthetic/c1_data_assets.csv`: synthetic data-asset inventory for the C1 Data Security Program
  lablet. No real company names, client data, target data, private records, or allegations. Created
  2026-06-15. Update method: edit synthetic rows when 28 CFR Part 202 data categories or thresholds
  change. Lab use: demonstrate threshold triage for bulk US sensitive personal data under EO 14117.
- `data/synthetic/d1_deal_intake_flags.csv`: synthetic deal-intake flags for the D1 integrated workflow
  lablet. No real company names, client data, target data, private records, or allegations. Created
  2026-06-16. Update method: edit synthetic flags when the regime-trigger matrix or article workflow
  changes. Lab use: demonstrate how a diligence team can turn intake facts into counsel escalations,
  immediate evidence requests, and risk-memo warnings.
- `data/synthetic/d2_counterparties.csv`: synthetic counterparties for the D2 capstone name-screen
  demonstration. No real company names, client data, target data, private records, or allegations.
  Created 2026-06-16. Update method: edit synthetic rows when the D2 article or fixture vocabulary
  changes. Lab use: demonstrate exact match, near match, and no-current-signal output posture.
- `data/synthetic/d2_ownership_edges.csv`: synthetic ownership edges for the D2 OFAC 50 Percent Rule
  teaching graph. No real company names, client data, target data, private records, or allegations.
  Created 2026-06-16. Update method: edit synthetic rows when the B1 or D2 ownership-tracing explanation
  changes. Lab use: demonstrate aggregated flagged ownership as a teaching signal only.

## Teaching fixtures

- `data/sample/d2_fixture_screening_list.csv`: synthetic screening-list fixture shaped like normalized
  list data. No real company names, client data, target data, private records, or allegations. Created
  2026-06-16. Update method: edit when D2 parser fields change. Lab use: deterministic offline tests and
  publishable D2 sample output.

## Non-public / access-limited (named, NOT in the automated screen)

- FinCEN BOI: confidential and access-limited (https://www.fincen.gov/boi). Not a bulk dataset; the
  article explains lawful diligence use only.
