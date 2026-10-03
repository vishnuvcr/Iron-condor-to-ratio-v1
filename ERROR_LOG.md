# Error Log

| ID | Date | Phase | Error / issue | Impact | Resolution |
|---|---|---|---|---|---|
| E001 | 2026-10-03 | 0 | Target GitHub repository was empty; no prior plan/status/error logs were available. | No inherited research controls or implementation. | Created baseline research-control files and recorded the issue. |
| E002 | 2026-10-03 | 0 | The source strategy requires intraday delta triggers, while NSE public archive pages primarily expose daily/historical report products. | Daily data alone cannot reproduce trigger timing. | Treat intraday option-chain data as a Phase 1 acquisition requirement; do not substitute daily data. |
| E003 | 2026-10-03 | 0 | Video contains discretionary profit-taking/expiry-day decisions and some execution details are not fully deterministic. | A single literal backtest could embed researcher discretion. | Separate deterministic core rules from explicitly tagged discretionary variants. |
