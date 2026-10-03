# Conversation Log

This file records user-visible project instructions and work decisions, not hidden chain-of-thought.

## 2026-10-03 — Developer initiation
- User requested a backtest of the uploaded YouTube strategy and supplied the video URL.
- User selected Developer role.
- Uploaded transcript was used as the primary strategy specification.
- Repository vishnuvcr/Iron-condor-to-ratio-v1 was inspected and found empty.
- Phase 0 controls were established.
- First tester gate recorded.

## 2026-10-03 — First tester result
- Independent tester reported **Phase 0 FAIL / corrections required**.
- Tester confirmed the source strategy was substantially transcribed correctly.
- Tester blockers: delta convention; trigger sampling; strike selection; entry timing; fill/execution; trigger-to-fill ordering; expiry handling; Paytm Money historical cost verification; unit-test invariants.
- Developer accepted the gate and did not advance Phase 1.

## 2026-10-03 — Correction pass
- Added `research/OPERATIONAL_CONVENTIONS.md`.
- Updated `research/STRATEGY_SPEC.md` with explicit source-vs-operational separation.
- Updated research plan to require second independent tester approval.
- Defined a one-minute deterministic literal-core implementation convention, no-look-ahead execution sequencing, leg-by-leg bid/ask fills, date-specific cost verification, and forced expiry close.
- Phase 1 remains blocked pending second tester approval.

## Source
YouTube URL supplied by user: https://youtu.be/T4gvTshMEyA
Uploaded transcript: What If the Iron Condor Starts Trending Ratio Spread Strategy.txt

## 2026-10-03 — Second independent tester result and developer response
- User reported the second independent tester gate as **FAIL** and instructed the developer to proceed with corrections.
- Developer verified PR #4 and the tester branch directly.
- The missing `research/OPERATIONAL_CONVENTIONS.md` artifact was confirmed absent from PR #3.
- Developer created `phase-0-corrections-v2` from the correction branch and added the canonical operational artifact.
- Exact numerical semantics were frozen for IV/Black-Scholes reconstruction, slippage, strike selection, data quality, thresholds, direction classification, and historical contract metadata.
- README, status, plan and error records were updated.
- Phase 1 remains blocked pending independent re-test and approval.

## 2026-10-03 — Third independent tester result and correction pass
- User reported the third independent tester gate as **FAIL** and instructed the developer to proceed.
- Developer verified PR #6 and the third tester report directly.
- Developer created `phase-0-corrections-v3`.
- B1: froze Brent-Dekker root tolerances, termination and binary64 semantics.
- B2: froze exact Black-Scholes no-arbitrage bounds and one-tick tolerance handling.
- B3: froze integer tick ceil/floor rounding and on-grid behavior.
- B4: explicitly rejected future-dated quotes.
- B5: aligned STRATEGY_SPEC.md with the fixed literal-core fallback slippage formula.
- Added a Phase 0 GitHub Actions integrity workflow with automatic push/PR triggers and manual dispatch.
- Phase 1 remains blocked pending another independent tester approval.
