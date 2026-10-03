# Phase 1 G5 — Underlying/Option Alignment Acceptance Specification

Updated: 2026-10-03

## Purpose

G5 establishes that the primary NIFTY option observations can be joined to the NIFTY underlying on the exact one-minute timestamp grid used for strategy decisions, after deterministic contract-key deduplication and date-specific session filtering.

This gate is a data-integrity gate only. It does not compute strategy P&L, optimize parameters, or authorize Phase 2.

## Source and provenance

Primary market source:
- Hugging Face dataset: `thetrademarkk/india-index-options-1m`
- immutable revision: `0f4800e`
- selected structures: `index/NIFTY.parquet` and `options/NIFTY/*.parquet`
- source timestamps documented as Asia/Kolkata.

Official NSE reference sources:
- Historical Index Data: https://www.nseindia.com/reports-indices-historical-index-data
- NIFTY 50 F&O: https://www.nseindia.com/static/products-services/equity-derivatives-nifty50
- Contract Specifications: https://www.nseindia.com/static/products-services/equity-derivatives-contract-specifications

NSE's published historical/contract interfaces confirm that NIFTY derivative records are identified by underlying, expiry, option type and strike, while the historical index interface provides the benchmark index series used for timestamp alignment.

## Deterministic procedure

1. Read the immutable primary source.
2. Parse timestamps as UTC while retaining Asia/Kolkata for session classification.
3. Reject any unparseable option or index timestamp.
4. Require unique NIFTY underlying timestamps; duplicate underlying timestamps are fatal.
5. Treat option contract identity as `timestamp + expiry + strike + option_type`.
6. Observe and report exact duplicates and key duplicates; production deduplication remains deterministic and fail-closed for conflicting key groups.
7. Define decision-eligible option timestamps using the date-specific session rules already independently reconciled under G4.
8. Separately test whether every decision-eligible option timestamp exists exactly in the NIFTY timestamp grid.
9. Do not interpolate, forward-fill, nearest-match, or otherwise manufacture an underlying observation.
10. Produce complete counts plus bounded examples of decision-eligible option timestamps lacking an underlying match.
11. Produce expiry-by-date coverage so a high aggregate match fraction cannot conceal a missing contract/day segment.

## Acceptance rule

G5 is a PASS candidate only when:
- zero invalid option timestamps;
- zero duplicate NIFTY timestamps;
- every decision-eligible option observation has an exact NIFTY timestamp match;
- expiry/day coverage is reported for the complete production source;
- no interpolation or forward-fill is used.

The validator fails closed if any acceptance condition is not satisfied.

## Interpretation boundary

A high aggregate alignment percentage is not sufficient. The production gate requires complete decision-time alignment. Out-of-session option observations remain retained and reported but are not treated as strategy decision observations.

G5 does not establish:
- historical executable bid/ask;
- valid historical Greeks;
- target-delta availability;
- contract-rule validity;
- transaction-cost completeness;
- strategy profitability.

Those remain separate gates.

## Automated evidence

Workflow:
`.github/workflows/phase1-g5-alignment.yml`

Validator:
`scripts/phase1_g5_alignment_audit.py`

Evidence artifact:
`data/validation/phase1_g5_alignment_report.json`

The workflow supports push, pull-request and manual `workflow_dispatch`, restores the pinned-source cache, and retains the G5 evidence artifact even on failure.
