# Phase 2 — Deterministic Backtest Engine Specification

Updated: 2026-10-04

## Objective

Implement the source-derived Iron Condor → directional ratio strategy as a deterministic state machine using the frozen bid/ask-free proxy execution model. The engine is not an optimizer and does not introduce discretionary profit-taking rules into the literal core.

## Canonical input contract

The engine consumes a normalized one-minute option table with one row per contract/bar and these required columns:

- `timestamp`: timezone-aware or parseable timestamp
- `expiry`: contract expiry date
- `strike`: strike
- `option_type`: CE/CALL/C or PE/PUT/P
- `open`: next-bar execution candidate
- `close`: decision/marking price
- `volume`: tie-break liquidity field
- `underlying`: contemporaneous NIFTY level
- `abs_delta`: contemporaneous absolute Black-Scholes delta from the Phase 1 Greek pipeline
- `tick_size`: effective historical option tick size
- `lot_size`: effective historical contract lot size
- `session_eligible`: date-specific session eligibility
- `execution_eligible`: whether the bar is eligible as a next-bar proxy execution observation
- `expiry_close_ts`: date-specific expiry-session close timestamp used for expiry boundaries

A deterministic `contract_id` is formed from expiry + strike + option type unless supplied.

## Source-derived literal core

### Initial Iron Condor

At the first eligible entry opportunity for a monthly cycle:
- sell CE at approximately 0.30 absolute delta;
- buy CE at approximately 0.10;
- sell PE at approximately 0.30;
- buy PE at approximately 0.10.

### Transition

If either short IC leg crosses from above 0.10 to <= 0.10:
- call-side short reaches threshold → directional CALL ratio (downward move);
- put-side short reaches threshold → directional PUT ratio (upward move).

The entire old position is closed and the new ratio opened as one atomic multi-leg adjustment group.

### Initial directional ratio

For downward/call direction:
- +1 lot CALL near 0.50 delta;
- -2 lots CALL near 0.40 delta;
- +1 lot CALL hedge near 0.10 delta.

For upward/put direction:
- +1 lot PUT near 0.50 delta;
- -2 lots PUT near 0.40 delta;
- +1 lot PUT hedge near 0.10 delta.

### Continuation

When the combined absolute delta of the two short ratio legs crosses downward from >0.20 to <=0.20:
- close the old ratio;
- reset in the same direction to +1 near 0.40, -2 near 0.30, +1 near 0.08.

### Reversal

When the combined absolute delta of the two short ratio legs crosses upward from <1.20 to >=1.20:
- close the old ratio;
- switch to the opposite directional ratio using the initial 0.50 / 0.40×2 / 0.10 construction.

The source describes a reversal zone around 1.20–1.30; the literal core freezes the lower boundary (>=1.20) as the first deterministic trigger. The 1.30 upper boundary is retained for sensitivity analysis and is not silently ignored.

## Operational assumptions that are not fully specified by the source

These are isolated from the source-derived rules and must be disclosed:

1. **Entry timing:** first decision-eligible minute of each calendar month for which a valid expiry is available.
2. **Expiry selection:** nearest available expiry at least 20 calendar days after the entry date, restricted to the latest listed expiry date in each calendar month. This uses the observed contract expiry field rather than projecting a weekday rule backward. The 20-day floor is an operational convention, not a claim about the source video.
3. **Target selection:** absolute-delta error <= 0.05; ties broken by higher volume, then smaller strike distance, then lower strike.
4. **Trigger frequency:** every completed eligible one-minute bar.
5. **Forced expiry exit:** the engine creates a close event on the last decision minute before the date-specific `expiry_close_ts` cutoff supplied in the normalized data; no hard-coded historical close is projected backward and no settlement payoff is synthesized.
6. **Profit taking:** excluded from the literal core because the source is discretionary. A separate variant may be tested later.
7. **Execution:** frozen Phase 1 next-eligible-open proxy with adverse slippage and atomic group execution.
8. **Multi-leg position units:** quantities are whole lots; short two-lot ratio legs are two lots of the selected contract.
9. **Missing delta/bar:** no interpolation. Missing observations suppress a trigger until a valid observation returns.
10. **Failed adjustment:** state is preserved, the trigger is consumed, and the trigger must leave and re-enter its trigger region before a new adjustment is eligible.

## Atomic execution

For every order group:
- all legs must have a valid next eligible bar strictly after the decision timestamp;
- the contract must not be expired at the execution timestamp;
- base open and tick size must be positive;
- adverse slippage is applied per leg;
- every dated cost rule required by the cost schedule must resolve.

Any failed leg causes the entire group to be `FAILED_INCOMPLETE_EXECUTION`. No partial fill is recorded.

## Cost model

The engine requires a complete date-indexed charge schedule for:
- Paytm Money brokerage;
- STT;
- NSE transaction charges;
- IPFT;
- SEBI turnover fee;
- GST;
- stamp duty;
- other documented regulatory/clearing charges where applicable.

The engine fails closed when a required rule is missing. It does not infer a current rate for historical dates.

## Outputs

The production run must create:
- deterministic trade ledger;
- event/state-transition ledger;
- per-leg fill ledger;
- per-group execution result;
- cost breakdown;
- slippage breakdown;
- missing/failed-execution log;
- provenance manifest with input file hashes and exact Git SHA;
- reproducible configuration snapshot.

## Validation hierarchy

1. Mathematical/unit tests.
2. Synthetic state-machine tests for every trigger and failure path.
3. Property tests for atomicity, no partial fills, no future-bar execution, and trigger re-arm.
4. Exact-data integration run when normalized Phase 1 inputs and dated cost schedules are available.
5. Milestone tester audit before final strategy acceptance.

## Interpretation boundary

This engine supports research under the declared proxy execution model. It does not establish historical live fills, and it does not turn the source video's discretionary rules into facts.
