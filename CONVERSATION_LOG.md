# Conversation Log

This file records user-visible project instructions and work decisions, not hidden chain-of-thought.

## 2026-10-03 — Developer initiation
- User requested a backtest of the uploaded YouTube strategy and supplied the video URL.
- User selected Developer role.
- Uploaded transcript was used as the primary strategy specification.
- Repository vishnuvcr/Iron-condor-to-ratio-v1 was inspected and found empty.
- Phase 0 controls were established.
- A tester gate was recorded because the project instructions require a tester report before the developer advances.

## Source
YouTube URL supplied by user: https://youtu.be/T4gvTshMEyA
Uploaded transcript: What If the Iron Condor Starts Trending Ratio Spread Strategy.txt

## 2026-10-03 — Seventh independent tester PASS and Phase 1 start
- User reported the seventh independent tester gate as **PASS** for PR #11 / `phase-0-corrections-v6`.
- The tester independently verified B9/B10, exact CI provenance, numerical/IV conventions, execution semantics, cost policy, source/convention separation, state-machine invariants and phase discipline.
- Tester report: `research/TESTER_REPORT_PHASE0_SEVENTH.md`; tester PR #12.
- Developer created `phase-1-data-acquisition-validation` from main.
- Phase 1 is now active and limited initially to data acquisition, validation, provenance, historical contract metadata and date-specific costs. No backtest engine or performance analysis has begun.

## 2026-10-03 — Phase 1 source sweep
- Primary open candidate identified: `thetrademarkk/india-index-options-1m`, with documented 1-minute NIFTY option OHLCV/OI/strike/type/expiry data across approximately 2021–2026.
- Secondary candidate identified: `rissin/nse-options-intraday`, combining NSE daily EOD and Upstox 1-minute intraday data from 2024 onward.
- Neither candidate documents historical bid/ask; this is recorded as E019 and remains a validation gap.
- Official NSE sources were registered for contract metadata, daily reference data, India VIX, FII/DII, corporate actions and reconciliation. Paytm Money brokerage/cost sources were registered with date/cohort-specific treatment.
- Added Phase 1 acquisition manifests, validator, automated GitHub Actions workflow and market-context registry.
