# Operational Conventions — Frozen Phase 0 Contract

**Status:** Phase 0 correction candidate; frozen for independent tester review.  
**Scope:** These are research implementation conventions, not claims about what the YouTube source explicitly specified. They define the machine-level semantics required for independent reproduction.

## 1. Delta semantics

- Store signed option delta internally.
- Use absolute delta for all target matching and threshold tests.
- For two short option legs, define:
  `combined_short_delta = abs(delta_short_1) + abs(delta_short_2)`.
- Direction is a separate state variable and is never inferred retrospectively from the eventual trade outcome.
- Equality counts as threshold satisfaction.

### Thresholds frozen for the literal core

- Iron-condor transition: `abs(short_call_delta) <= 0.10` OR `abs(short_put_delta) <= 0.10`.
- Continuation reset: `combined_short_delta <= 0.20`.
- Reversal: `combined_short_delta >= 1.20`.
- The source's 1.20–1.30 wording is treated as an illustrative range; the machine threshold is exactly 1.20.
- No interpolation between observations is permitted.

## 2. Observation frequency and timestamp rules

- Canonical event grid: one-minute observations.
- A threshold is triggered at the first observed one-minute timestamp satisfying the relevant inequality.
- OHLC high/low values cannot establish an intraminute delta crossing.
- Each observation must have a timestamp in Asia/Kolkata and a source-quality flag.
- Data are sorted by timestamp before state evaluation.
- Duplicate contract/timestamp observations are rejected unless the source provides an explicit sequence/order identifier.

## 3. Black-Scholes/IV reconstruction

Historical vendor Greeks are preferred only when their calculation methodology and timestamp provenance are documented. Otherwise use the following deterministic fallback.

### Pricing model

- European option.
- Continuous dividend yield formulation.
- Call:
  `C = S*exp(-qT)*N(d1) - K*exp(-rT)*N(d2)`.
- Put:
  `P = K*exp(-rT)*N(-d2) - S*exp(-qT)*N(-d1)`.
- `d1 = [ln(S/K) + (r-q+0.5*sigma^2)T] / (sigma*sqrt(T))`.
- `d2 = d1 - sigma*sqrt(T)`.
- Delta:
  - call = `exp(-qT)*N(d1)`;
  - put = `-exp(-qT)*N(-d1)`.

NSE documentation also describes Black-Scholes as the theoretical pricing basis for index-option base prices. This project uses the model solely as a documented Greek-reconstruction convention, not as evidence of profitability.

### Inputs

- `S`: NIFTY 50 index level from the same one-minute observation used for the option quote. If a one-minute index observation is unavailable, that observation is invalid for Greek reconstruction.
- `K`: exact contract strike from historical contract metadata.
- Option premium for IV inversion: arithmetic midpoint `(bid + ask)/2`, only after quote-quality checks in Section 5.
- `T`: exact elapsed seconds from observation timestamp to the exchange-defined expiry timestamp, divided by 365 days. If `T <= 0`, reconstruction is invalid.
- `r`: latest available 91-day Indian Treasury-bill primary-market yield published by RBI on or before the observation date, expressed as a continuously compounded annual rate via `ln(1+y)`.
- `q`: latest available NSE NIFTY 50 dividend-yield observation published on or before the observation date, expressed as a decimal annual yield. If no historical NSE dividend-yield observation exists for the date, the observation is invalid rather than forward-filled from an arbitrary external source.

### IV solver

- Solve for positive volatility using Brent's bracketing method.
- Initial bracket: `[1e-6, 5.0]` annualized volatility.
- If the pricing error does not change sign over that bracket, expand the upper bound by doubling it until 10.0; do not exceed 10.0.
- If no sign change exists at 10.0, reject the observation.
- Absolute pricing tolerance: `1e-8` option-price units.
- Maximum iterations: 100.
- Do not forward-fill failed IVs.
- After solving IV, recompute model premium and require absolute model-vs-input error <= 1e-6. Otherwise reject.
- Reject non-finite values and option prices outside the no-arbitrage bounds, allowing at most one historical tick of numerical rounding tolerance.
- IV must be strictly positive and finite.

### Delta fallback

Once IV is solved, compute Black-Scholes delta from the same `S,K,T,r,q,sigma` inputs. Do not mix an IV from one timestamp with a delta input from another timestamp.

## 4. Strike selection

For each requested target delta, first construct the eligible contract set for the required underlying, expiry, option type and decision timestamp.

A contract is eligible only if:
1. it exists in the historical exchange contract metadata for that date;
2. it is the intended monthly expiry;
3. the option type matches;
4. quote-quality tests in Section 5 pass;
5. a valid signed/absolute delta is available;
6. `abs(abs(delta)-target_delta) <= 0.05`;
7. one-minute volume >= 1 contract OR open interest >= 1 contract.

Selection is lexicographically deterministic in this exact order:
1. smallest absolute delta error;
2. highest one-minute traded volume;
3. highest open interest;
4. smallest `abs(strike - underlying)`;
5. lowest strike price;
6. lexicographically smallest exchange contract identifier, if needed to resolve a final duplicate.

No information after the decision timestamp may be used.

If no eligible contract exists, the requested adjustment is rejected and the state does not silently change.

## 5. Data-quality filters

For a quote used for execution or IV reconstruction:
- bid and ask must both be finite and strictly positive;
- ask must be >= bid;
- midpoint must be strictly positive;
- relative spread `(ask-bid)/mid <= 0.25`;
- quote timestamp may not be more than 120 seconds older than the decision timestamp;
- crossed or otherwise invalid quote records are rejected;
- missing underlying observation rejects the corresponding Greek reconstruction;
- missing expiry/strike/option type/contract identifier rejects the contract;
- duplicate records at the same contract/timestamp are rejected unless a documented sequence number permits deterministic ordering.

For an execution fill, a quote failing these conditions is not executable.

## 6. Direction classification at the IC transition

The source maps a downward move to a call-side ratio and an upward move to a put-side ratio.

Machine rule:
- If exactly one short IC leg satisfies `abs(delta) <= 0.10`, use that triggering leg:
  - short call triggers -> downward classification -> call-side ratio;
  - short put triggers -> upward classification -> put-side ratio.
- If both short legs satisfy the threshold at the same timestamp, compute the one-minute NIFTY return from the immediately preceding valid observation:
  - return < 0 -> downward -> call-side ratio;
  - return > 0 -> upward -> put-side ratio;
  - return = 0 -> transition is rejected as directionally ambiguous and the existing position is retained.
- Never use subsequent observations to classify the direction.

## 7. Trigger-to-fill sequence

At timestamp `t`:
1. read only information available at `t`;
2. evaluate the current-state trigger;
3. freeze the exit decision;
4. submit/record exit fills at `t` or the first later executable quote;
5. at the actual executable/new-decision timestamp, re-read market state;
6. select new contracts using only information available then;
7. execute new legs independently;
8. record timestamp, contract, side, quantity, price, quote source, slippage/cost and reason.

A new structure cannot recursively trigger at the same timestamp merely because its entry-state delta already satisfies another rule. A separate later observation is required.

## 8. Execution and fallback slippage

Primary execution:
- buy = contemporaneous ask;
- sell = contemporaneous bid;
- each leg is priced independently;
- no portfolio-level midpoint fill.

If a valid traded price exists but no executable bid/ask exists, the literal-core fallback is fixed as:
`fallback_slippage = max(2 * tick_size, 0.005 * reference_price)`.

- `reference_price` is the latest valid trade price available at or before the decision timestamp, subject to the 120-second freshness rule.
- Buy fill = reference price + fallback slippage.
- Sell fill = max(tick_size, reference price - fallback slippage).
- Prices are rounded away from the trader to the contract tick size.
- If no valid bid/ask and no fresh reference trade exist, no fill occurs and the event is logged as unfilled.
- The fallback is a pre-registered literal-core convention; alternative slippage assumptions are sensitivity variants and cannot be selected after observing results.

The historical tick size must come from the applicable contract specification/master rather than assuming today's tick size.

## 9. Expiry and stale-quote handling

- Literal core has no discretionary profit target.
- No position is carried beyond the selected monthly expiry.
- All open legs are force-closed at the final valid executable one-minute observation of the monthly expiry trading session.
- If no valid bid/ask exists at that observation but a fresh reference trade exists within 120 seconds, apply the Section 8 fallback.
- If neither exists, use the most recent valid executable quote/trade within 120 seconds; if none exists, the position cannot be marked executable and the run is flagged as an expiry-data exception rather than silently assigning a price.
- No settlement-price substitution is permitted for the primary execution-adjusted result.
- A separate settlement-value sensitivity may be reported only if pre-registered.

## 10. Historical monthly-expiry identification

Historical contract metadata is authoritative.

For every candidate contract:
- use an exchange-provided historical contract master when available;
- verify symbol, instrument type, option type, strike, expiry date, lot size and applicable tick size;
- identify the monthly contract using explicit exchange metadata when the metadata provides the monthly designation;
- where the master lacks an explicit monthly flag, use the contemporaneous NSE contract specification/circular defining the monthly expiry cycle for that period;
- if neither source resolves the monthly designation unambiguously, exclude that period from the literal-core run and log the reason.

Current expiry rules must never be retroactively applied to historical observations. NSE's historical master documentation demonstrates that contract masters encode expiry and option-type information and that historical contract specifications must be respected.

## 11. Lot size and contract identity

- Lot size is taken from the historical NSE permitted-lot-size/contract-master record applicable to the contract date.
- Quantities are represented both in lots and underlying option units.
- Every fill records the immutable contract identifier, expiry, strike, option type, lot size and source metadata.
- A contract cannot be traded before its exchange-defined introduction date.

## 12. Costs

The literal-core P&L includes:
- Paytm Money brokerage;
- securities transaction tax;
- exchange transaction charges;
- SEBI charges;
- GST;
- stamp duty;
- documented clearing/regulatory charges;
- bid/ask spread;
- explicit fallback slippage where used.

Historical Paytm Money schedules must be selected by effective date for the eventual backtest period. The current Paytm Money page is not sufficient evidence for historical periods.

No cost is applied twice. Every cash-flow leg receives exactly one applicable cost record.

## 13. State machine

Allowed states:
- FLAT
- IRON_CONDOR
- RATIO_INITIAL
- RATIO_CONTINUATION
- RATIO_REVERSED

Every transition records:
- decision timestamp;
- previous and new state;
- triggering rule;
- relevant deltas;
- direction;
- strikes;
- quantities;
- fill timestamps/prices;
- costs;
- rejection/unfilled reason if applicable.

## 14. Unit-test invariants

The engine must test at minimum:
- exact initial IC quantities;
- exact initial ratio quantities;
- exact continuation quantities;
- reversal removes the prior directional structure;
- combined short delta equals the sum of absolute short-leg deltas;
- equality at each threshold triggers deterministically;
- no contract can be used before its introduction;
- no fill can occur before its trigger;
- forced expiry close leaves zero net quantity when executable data exist;
- exactly one cost record per executed cash-flow leg;
- a rejected adjustment cannot silently mutate state;
- same-timestamp recursive transitions are prohibited;
- ambiguous simultaneous IC triggers with zero underlying return are rejected;
- invalid IV observations cannot be forward-filled.

## 15. Pre-registration and sensitivity policy

The literal core uses the values in this document.

Sensitivity variants may vary only dimensions named in the research plan, including:
- observation frequency;
- vendor Greeks versus reconstructed Greeks;
- delta tolerance;
- quote-quality thresholds;
- slippage;
- entry timing;
- expiry treatment;
- pre-registered profit-taking rules.

Variants must be defined before looking at their performance results. No parameter may be selected because it produces a preferred outcome.

## 16. Source references for numerical inputs

- NSE equity-derivatives contract specifications and historical contract information: https://www.nseindia.com/static/products-services/equity-derivatives-contract-specifications and https://www.nseindia.com/static/products-services/equity-derivatives-contract-information
- NSE historical reports include NIFTY 50 history and historical NIFTY 50 dividend-yield observations: https://www.nseindia.com/all-reports
- RBI publishes Treasury-bill auction yields in its bulletins/press releases: https://www.rbi.org.in/
- NSE historical master-data documentation identifies expiry date, option type and contract metadata fields: https://archives.nseindia.com/content/press/Data_Details_F_n_O.pdf
- Paytm Money historical fee schedules must be verified by effective date from official Paytm Money publications before Phase 1 cost configuration.

## 17. Reproducibility rule

This document is the canonical operational convention for the literal-core research run. If a future change alters any numerical rule, this document, the research plan, status, error log and tester handoff must be updated and the changed phase must return through the appropriate independent tester gate before downstream research resumes.
