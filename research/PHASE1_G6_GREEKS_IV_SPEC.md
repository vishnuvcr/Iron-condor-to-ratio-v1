# Phase 1 G6 — Historical Greeks / IV Acceptance Specification

Updated: 2026-10-03

## Purpose

G6 establishes whether every option observation needed for deterministic target-delta selection can be assigned a reproducible implied volatility and signed/absolute Black-Scholes delta using only information available by the decision timestamp.

G6 is a production-data gate. It does not authorize the backtest engine or produce profitability results.

## Source inputs

### Risk-free rate

Primary source: Reserve Bank of India Weekly Statistical Supplement, field **91-Day Treasury Bill (Primary) Yield**.

Examples of official WSS pages exposing the field:
- https://www.rbi.org.in/scripts/WSSView.aspx?Id=26722
- https://www.rbi.org.in/scripts/WSSView.aspx?Id=26962
- https://www.rbi.org.in/scripts/WSSView.aspx?Id=27637
- https://www.rbi.org.in/scripts/WSSView.aspx?Id=27727

The WSS series is treated as a historical source, not a current-rate substitute.

### Dividend/yield input

Primary source: NSE Indices Historical Data / P-E, P-B and Dividend Yield reports:
- https://www.niftyindices.com/reports
- NSE NIFTY 50 underlying information: https://www.nseindia.com/static/products-services/equity-derivatives-underlying-information-nifty-50

NSE's underlying-information page identifies daily NIFTY P/E and annual dividend yield, while the NSE Indices historical reports interface explicitly provides P/E, P/B and Dividend Yield fields.

## No-look-ahead timing rule

For an option observation at timestamp t:
- use the most recent risk-free observation whose source observation/publication date is strictly before the trading date containing t;
- use the most recent NIFTY dividend-yield observation dated strictly before that trading date;
- never use a value first published/observed after t;
- no future interpolation;
- every source input must retain its source date and provenance.

If no valid historical input exists under this rule, the option observation is **G6-invalid**, not backfilled.

## IV solver

For European index options:
- Black-Scholes pricing model;
- contemporaneous NIFTY underlying value;
- option strike;
- time to contractual expiry;
- date-aligned risk-free rate;
- date-aligned dividend yield;
- observed option premium from the primary OHLC dataset only for diagnostic/model reconstruction, never as historical bid/ask.

The solver must:
1. reject non-positive or malformed inputs;
2. enforce exact Phase 0 no-arbitrage bounds;
3. use the frozen Brent-Dekker/root-termination tolerances from Phase 0;
4. record convergence iterations and residual;
5. reject non-convergent observations;
6. never forward-fill an IV;
7. retain solver-failure reason codes.

## Delta

For a solved IV, compute signed Black-Scholes delta and retain absolute delta for target selection.

Target-selection convention remains the Phase 0 rule:
- minimize abs(abs(delta) - target_delta);
- maximum permitted target error: 0.05;
- no eligible contract means target unavailable;
- all decisions are timestamp-local and cannot use future observations.

## Production acceptance evidence

The G6 report must contain:
- source hashes/revisions and acquisition timestamps;
- coverage of the full study period;
- counts of observations with valid r and q;
- IV solver success/failure/boundary-rejection counts;
- residual and iteration distributions;
- delta distributions by option type;
- failures by date, expiry and reason;
- evidence that no future-dated r/q/IV input was used;
- a reproducibility checksum for the resulting production Greek dataset.

## Acceptance rule

G6 may become a PASS candidate only when the complete date-aligned r/q inputs and production IV/Greek reconstruction execute successfully over the full required option dataset under the frozen Phase 0 numerical rules.

Diagnostic samples are not sufficient for G6 acceptance.

## Important limitation

The public NSE option-chain page exposes live bid/ask/IV fields, but current live values cannot be used retrospectively. NSE describes India VIX as being based on best bid/ask NIFTY option quotes, which confirms the exchange's quote-based volatility framework but does not supply the historical quote series needed for this study.

G6 therefore remains separate from G9's approved proxy execution methodology.
