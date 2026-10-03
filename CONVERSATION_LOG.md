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
