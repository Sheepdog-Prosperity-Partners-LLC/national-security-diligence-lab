# Limitations

Prepared by Noah Green CPA CFE.

- Lab outputs are diligence leads, not findings. A name or list hit is a starting point for verification,
  not proof of wrongdoing.
- Screening lists change. Re-pull before relying on any result; record the access date.
- Name matching is imperfect. Transliteration, aliases, and identifier gaps cause false positives and
  false negatives. A no-hit result is not a clean bill of health unless coverage and identifier quality
  support it.
- The OFAC 50 Percent Rule examples use synthetic ownership graphs; real ownership tracing requires
  source documents and, where exposure is live, counsel.
- BOI is confidential and access-limited; it is never used as a bulk dataset here.
- Export classification (ECCN) is not automated; the lab only flags screening-list and diligence-request
  issues.
- The A2 outbound triage lablet is keyword-based. It does not understand legal negation, technical
  thresholds, ownership thresholds, exceptions, or the prohibited-versus-notifiable line. A hit means
  "review," not "covered," and a no-hit means only that the supplied text did not contain the configured
  terms.
- The C1 threshold checker uses synthetic counts and rule categories. It does not determine whether a
  real transaction is data brokerage, a vendor agreement, an employment agreement, an investment
  agreement, exempt, licensed, prohibited, restricted, or compliant with CISA security requirements.
- The C2 timeline builder uses manually curated public DOJ/Treasury releases. It does not verify
  ownership, trace tainted funds, determine forfeitability, update docket posture, or convert complaint
  allegations into findings. A "seizure_or_freeze" row is not final forfeiture, and an
  "allegation_only" row must stay allegation-only unless a later sourced order changes the posture.
- The C3 award matrix is a program-routing aid only. It does not determine eligibility, advise a
  whistleblower, recommend a filing, calculate an award, resolve privilege, decide company
  self-disclosure strategy, or determine whether a person can both report internally and receive an
  award. Each program has its own rules and counsel-escalation path.
- The D1 integrated workflow lablet uses synthetic flags. It does not verify whether a real deal
  triggers CFIUS, outbound investment, OFAC, BIS, BSA/AML, BOI, DOJ Data Security Program, forfeiture,
  or whistleblower rules. It is a memo-structure and escalation exercise, not an approval tool.
- The D2 capstone screen is a teaching aid. It uses simple standard-library name normalization and
  scoring, not a commercial sanctions-screening engine, transliteration model, alias-resolution system,
  or legal review workflow.
- D2 live-source tests check endpoint reachability and parse shape only. They do not certify that a
  downloaded list is complete, current for a particular legal question, or sufficient for a real
  diligence file.
- D2 export-list screening filters BIS-related CSL source labels. It does not classify items,
  technology, software, source code, deemed exports, end uses, foreign direct product rule exposure, or
  license requirements.
- D2 ownership graph outputs use synthetic direct ownership rows. Real OFAC 50 Percent Rule work
  requires legal-entity documents, aggregation across blocked persons, control and indirect-ownership
  review, and counsel escalation when exposure is live.
- The D3 remedy-comparison lablet uses publication-approved public case-data rows to compare procedural paths. It
  does not determine liability, national-security risk, ownership, forfeitability, due-process
  sufficiency, or whether a different buyer would have received the same remedy. Ralls is used as the
  primary public CFIUS forced-unwind anchor because the presidential order and appellate opinion are
  public; Grindr/Kunlun is caveated unless a public CFIUS order is located in a later pass.
- Escalate to sanctions, export-control, CFIUS, or privacy counsel for any legal interpretation.
