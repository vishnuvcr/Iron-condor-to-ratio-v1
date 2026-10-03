# G6 Production Historical Greeks / IV Evidence Specification

## Purpose

This gate converts the accepted G6 source-provenance work into production evidence for historical Black-Scholes reconstruction. It does **not** authorize Phase 2.

## Required inputs

1. Deduplicated NIFTY option bars from the pinned primary dataset.
2. Exact contemporaneous NIFTY underlying values at each option timestamp.
3. Historical risk-free observations containing:
   - observation date,
   - publication/availability date when known,
   - 91-Day Treasury Bill (Primary) Yield.
4. Historical NIFTY dividend-yield observations containing:
   - observation date,
   - dividend yield percentage.
5. Effective expiry/contract metadata from the Phase 1 contract rules.

## No-lookahead rule

For every option valuation timestamp (t), select the latest valid risk-free and dividend-yield observation whose **observation/availability date is strictly earlier than the trading date**. No future observation, interpolation, forward-fill across a missing source history, or same-day value is permitted.

If no eligible observation exists, the valuation is a hard failure with a reason code.

## Black-Scholes reconstruction

European index-option pricing is used:

- Call: (C=S e^{-qT}N(d_1)-K e^{-rT}N(d_2))
- Put: (P=K e^{-rT}N(-d_2)-S e^{-qT}N(-d_1))
- (d_1=[\ln(S/K)+(r-q+\sigma^2/2)T]/(\sigma\sqrt T))
- (d_2=d_1-\sigma\sqrt T)

Expiry time and time-to-expiry must use the effective contract convention. Non-positive (S,K,T), malformed premiums, or invalid rates are rejected.

## IV solver

1. Check exact European no-arbitrage bounds before solving.
2. Solve for volatility only within a deterministic bounded interval.
3. Use a frozen Brent-style tolerance and maximum iteration count.
4. Record:
   - convergence flag,
   - iterations,
   - residual,
   - lower/upper boundary,
   - boundary rejection,
   - failure reason.
5. No IV forward-fill is permitted.

## Delta

Retain signed Black-Scholes delta:

- call: (e^{-qT}N(d_1))
- put: (-e^{-qT}N(-d_1))

Use absolute delta only for target-delta contract selection. Report both distributions separately.

## Target availability

For each required target (0.30, 0.10, 0.50, 0.40, 0.08), select only contracts available at that timestamp and within the frozen absolute-delta tolerance of ±0.05. Apply the deterministic tie-break from the operational conventions. Missing target availability is a hard evidence failure for the affected decision universe.

## Acceptance criteria

G6 production PASS requires all of:

- complete date-aligned r coverage for the study window;
- complete date-aligned q coverage for the study window;
- zero future-dated inputs;
- zero silent interpolation/forward-fill;
- documented IV success/failure/boundary distributions;
- signed and absolute delta distributions;
- target-delta availability statistics;
- expiry/date coverage;
- deterministic failure-reason counts;
- production dataset/evidence checksums;
- exact checkout SHA recorded in the evidence artifact.

Any missing mandatory evidence leaves G6 OPEN.

## Evidence boundary

A successful workflow run proves only that the implementation produced the reported evidence from its exact checkout. G6 becomes PASS only after independent tester review of the substantive evidence package.


## 2026-10-04 source-method audit update

The public NSE Indices historical-data interface explicitly exposes daily P/E, P/B and dividend-yield reports. An independently documented public reverse-engineering reference records the underlying historical valuation endpoint, with a maximum 365-day request window and multi-year pagination requirements. This is a procurement/implementation lead, not yet production data acceptance. The public documentation is linked in the project research record.

RBI public WSS pages independently expose the required 91-Day Treasury Bill (Primary) Yield field. RBI's DBIE documentation also states that government-securities datasets are available through its public data API, but the study's frozen G6 rule remains tied to the specified 91-day primary-yield series and strict no-lookahead handling; no alternate rate series is silently substituted.
