# Phase 1 Production Evidence Execution Plan

Updated: 2026-10-03

This file defines the evidence required to close the substantive Phase 1 gates after E033. It does not change the research plan or promote any gate to PASS.

| Gate | Required evidence | Current blocker |
|---|---|---|
| G4 | Machine-readable NSE F&O trading-session calendar covering every observed date; observed first/last minute, count and missing-minute diagnostics reconciled against that calendar; explicit exclusion/repair rule pre-registered before production use | Calendar dataset not yet acquired; prior 1,262-date count range remains unreconciled |
| G5 | Full one-minute option-to-NIFTY timestamp join after deterministic dedup, with missing-index and duplicate-key diagnostics; decision-time coverage by expiry/date | Requires fresh pinned-source execution |
| G6 | Date-aligned RBI r and NSE NIFTY q series; production IV solver using exact Phase 0 tolerances; success/failure/boundary rejection statistics; no forward-filled failed IV | Historical machine-readable r/q series not yet assembled |
| G7 | Every decision timestamp evaluated for each required target delta under frozen liquidity/quote-quality rules; coverage by leg, expiry, date and regime; no sampled-only acceptance | Requires G6 plus execution-quality data |
| G8 | Historical contract master/effective-date map containing expiry, lot size, tick size and applicable contract rules; every source contract reconciled to one historical rule set | Machine-readable historical contract master not yet assembled |
| G9 | Historical bid/ask or order-level reconstruction sufficient to reproduce midpoint execution; timestamp/age/spread validation and quote-quality rejection report | Primary source has no bid/ask; NSE historical order/trade procurement not completed |
| G10 | Date-indexed brokerage, STT, exchange transaction, IPFT, SEBI, GST, stamp duty and applicable clearing/regulatory schedules; deterministic charge calculation tests | Complete machine-readable historical schedule not yet assembled |
| G11 | Date-aligned NIFTY benchmark, India VIX, FII/FPI, DII, GIFT NIFTY/overnight/global risk indicators, NSE/BSE context and event/corporate-action calendars with provenance | Full aligned context package not yet assembled |
| G12 | GitHub Actions run whose commit SHA is the repaired audit code (or a later commit containing it), with successful syntax, acquisition, validation, dedup, market-quality and session-audit steps and retained artifacts | GitHub connector can inspect runs but cannot dispatch workflows; commit 336c8e8 has zero associated workflow runs |
| G13 | Independent tester report explicitly marking G4–G12 and G13 PASS, with no unresolved acceptance blocker | Depends on G4–G12 |
| G14 | Formal authorization record after G13 PASS | Blocked |

## Historical session evidence already verified externally

NSE currently documents F&O regular trading as 09:15–15:40, while historical NSE F&O circulars demonstrate 09:15–15:30 schedules during the study period (for example, 2024 mock/live-session documentation and the February 2025 Budget session). Therefore current market hours must not be projected backward over the complete 2021–2026 sample. citeturn1search2turn2search0turn2search3

The production session calendar must be date-specific and sourced from NSE holiday/session circulars, including special sessions such as the Budget session and Muhurat/special trading days.

## Acceptance rule

No gate becomes PASS merely because a source has been identified. A gate becomes PASS only when its specified machine-readable evidence is generated, reproducible, retained and independently reviewed.
