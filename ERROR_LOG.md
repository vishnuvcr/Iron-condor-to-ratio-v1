# Error Log

| ID | Date | Phase | Error / issue | Impact | Resolution |
|---|---|---|---|---|---|
| E001 | 2026-10-03 | 0 | Target GitHub repository was empty; no prior plan/status/error logs were available. | No inherited research controls or implementation. | Created baseline research-control files and recorded the issue. |
| E002 | 2026-10-03 | 0 | The source strategy requires intraday delta triggers, while NSE public archive pages primarily expose daily/historical report products. | Daily data alone cannot reproduce trigger timing. | Treat intraday option-chain data as a Phase 1 acquisition requirement; do not substitute daily data. |
| E003 | 2026-10-03 | 0 | Video contains discretionary profit-taking/expiry-day decisions and some execution details are not fully deterministic. | A single literal backtest could embed researcher discretion. | Separate deterministic core rules from explicitly tagged discretionary variants. |
| E004 | 2026-10-03 | 0 | Phase 0 literature/data review found public datasets with different coverage, access requirements and licensing; some advertise historical Greeks but full data access is not established. | Risk of using an unverifiable or non-redistributable dataset. | Require provenance, access method, coverage and licensing checks in Phase 1 before primary backtest use. |
| E005 | 2026-10-03 | 0 | First independent tester failed Phase 0 because execution-critical semantics were still unspecified. | Phase 1 was blocked. | Added explicit operational conventions, unit-test invariants and a second-tester gate; no Phase 1 work started. |
| E006 | 2026-10-03 | 0 | Paytm Money brokerage and statutory charges vary by date/user plan and regulatory changes. | A single generic cost rate could distort net P&L. | Require date-specific official Paytm Money/regulatory cost schedules before the production backtest. |

| E007 | 2026-10-03 | 0 | Second independent tester failed the gate because the promised canonical operational-conventions artifact was absent from PR #3 and several numerical semantics remained implementation-dependent. | Phase 1 remained blocked; independent reproduction from PR #3 was not possible. | Added the missing tracked artifact and froze the requested numerical conventions on `phase-0-corrections-v2`; independent re-test required. |
