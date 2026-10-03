# Phase 1 — Historical NSE Session Calendar Specification

Updated: 2026-10-03

## Purpose

Close the evidence design for G4 (timestamp/session quality) without assuming that today's NSE hours apply retrospectively.

## Source basis

NSE currently documents equity-derivatives normal-market hours as 09:15–15:40. Historical NSE F&O circulars also document sessions with different close times, including a 2024 mock session at 15:30. Therefore the validator must use date-specific exchange/session metadata rather than a single hard-coded market close. [NSE Market Timings](https://www.nseindia.com/static/market-data/market-timings); [NSE Circular 100/2024](https://nsearchives.nseindia.com/content/circulars/FAOP63427.pdf).

## Required canonical fields

Each calendar row must contain:

- `trade_date` — Asia/Kolkata calendar date.
- `segment` — F&O.
- `session_type` — NORMAL, SPECIAL, BUDGET, MUHURAT, MOCK, or OTHER.
- `market_open` — local timestamp.
- `market_close` — local timestamp.
- `trade_modification_end` when applicable.
- `source_url`.
- `source_reference`.
- `effective_from` and `effective_to` when the rule is interval-based.
- `exception_reason` for special sessions.
- `source_hash` when a downloaded source file is retained.

## Reconciliation algorithm

1. Convert source timestamps to Asia/Kolkata.
2. Deduplicate the primary NIFTY index by timestamp before diagnostics.
3. For every observed date, join to exactly one canonical session row.
4. If no session row exists, classify the date as `UNRECONCILED`; do not silently exclude it.
5. Compare observed first/last timestamps and observed minute set against the session window.
6. Report:
   - expected minute count;
   - observed count;
   - missing expected minutes;
   - extra/out-of-session minutes;
   - first/last observed minute;
   - duplicate timestamp count before dedup;
   - null/non-finite price count.
7. Special sessions are retained and flagged, not discarded automatically.
8. A pre-registered exclusion or repair rule must be applied only after reconciliation.

## Acceptance thresholds

These are diagnostics, not an assumption that every session must have exactly 376/391 observations:

- G4 cannot PASS with any `UNRECONCILED` trading date.
- Missing minutes inside an expected session window must be quantified by date.
- Out-of-session observations must be quantified and traced to source/session conventions.
- No date is excluded solely because its count differs from another date.
- Any repair must preserve the original rows and record a deterministic transformation and reason.

## Current evidence status

**OPEN.** The machine-readable calendar itself has not yet been acquired and independently executed against all 1,262 observed dates.

## Important non-substitution rule

The current 15:40 close is reference information only. It must not be projected backward across 2021–2026.

## Primary references

- NSE Market Timings: https://www.nseindia.com/static/market-data/market-timings
- NSE Market Timings & Holidays: https://www.nseindia.com/resources/exchange-communication-holidays
- NSE historical F&O order/trade data: https://betanseapi.nseindia.com/static/market-data/eod-historical-data-subscription
