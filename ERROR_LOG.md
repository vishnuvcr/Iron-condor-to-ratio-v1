# Error Log

| ID | Date | Phase | Error / issue | Impact | Resolution |
|---|---|---|---|---|---|
| E001 | 2026-10-03 | 0 | Target GitHub repository was empty; no prior plan/status/error logs were available. | No inherited research controls or implementation. | Created baseline research-control files and recorded the issue. |
| E002 | 2026-10-03 | 0 | The source strategy requires intraday delta triggers, while NSE public archive pages primarily expose daily/historical report products. | Daily data alone cannot reproduce trigger timing. | Treat intraday option-chain data as a Phase 1 acquisition requirement; do not substitute daily data. |
| E003 | 2026-10-03 | 0 | Video contains discretionary profit-taking/expiry-day decisions and some execution details are not fully deterministic. | A single literal backtest could embed researcher discretion. | Separate deterministic core rules from explicitly tagged discretionary variants. |
| E004 | 2026-10-03 | 0 | Phase 0 literature/data review found public datasets with different coverage, access requirements and licensing; some advertise historical Greeks but full data access is not established. | Risk of using an unverifiable or non-redistributable dataset. | Require provenance, access method, coverage and licensing checks in Phase 1 before primary backtest use. |

| E018 | 2026-10-03 | 0 | Seventh independent tester PASS was not yet synchronized into the main-derived Phase 1 branch at creation time. | Without synchronization, active status could incorrectly keep Phase 1 blocked. | Recorded the tester report/PR #12 approval and activated Phase 1 on `phase-1-data-acquisition-validation`. |
| E019 | 2026-10-03 | 1 | The leading open 1-minute NIFTY option dataset documents OHLCV/OI/strike/type/expiry but not historical bid/ask; a secondary dataset also lacks documented bid/ask. | True historical bid/ask execution cannot be assumed from these sources. | Treat bid/ask as a Phase 1 validation gap; use the frozen literal-core fallback only if no independent quote source is validated, and flag degraded execution data. |
