# Dependency Review

Prepared by Noah Green CPA CFE.

This lab is public-release staged as a standard-library Python project. No third-party dependency is
required for the current module-backed lablets, offline tests, live-source smoke tests, or sample-output
regeneration.

| Candidate | Proposed use | Origin review | License review | Maintenance review | Verdict | Rationale |
|---|---|---|---|---|---|---|
| Python standard library | CSV parsing, URL fetches, command-line interfaces, tests, hashing, JSON manifests | CPython is maintained by the Python Software Foundation and is not PRC-origin tooling. | Python Software Foundation License, permissive. | Actively maintained. | BUILD-FRESH | The current lab can meet the reader-facing requirements without external dependencies. |
| matplotlib | Optional future charts for notebook-style presentation | Not adopted in this release. A fresh review is required before use. | Not reviewed for adoption in this release. | Not reviewed for adoption in this release. | deferred | Text and CSV trend tables are sufficient for this release, so charting is not added. |
| pandas | Optional future dataframe convenience | Not adopted in this release. A fresh review is required before use. | Not reviewed for adoption in this release. | Not reviewed for adoption in this release. | deferred | The project keeps CSV handling in the standard library to stay clone-and-run friendly. |
| networkx | Optional future graph convenience | Not adopted in this release. A fresh review is required before use. | Not reviewed for adoption in this release. | Not reviewed for adoption in this release. | deferred | The current synthetic ownership example does not need an external graph library. |
| requests | Optional future HTTP convenience | Not adopted in this release. A fresh review is required before use. | Not reviewed for adoption in this release. | Not reviewed for adoption in this release. | deferred | URL fetching currently uses `urllib.request` from the standard library. |

## Release Decision

- Current dependency posture: standard library only.
- Public-release action: do not add dependencies before owner approval and a fresh dependency review.
- Reader impact: every documented command can run with Python 3.10 or later and the standard library.
