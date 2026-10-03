# Operational Conventions — Phase 0 Corrections

## Purpose
The video supplies the strategy logic but does not specify every machine-execution detail. The following conventions are **research implementation conventions**, not claims about what the video author intended. They are fixed before Phase 1 and will be sensitivity-tested rather than changed after seeing performance.

## 1. Canonical delta convention
- Individual option delta is represented as a signed Greek internally.
- For target selection and threshold rules, the canonical magnitude is **absolute delta**.
- For a two-lot short position, the combined short-leg magnitude is:
  `abs(delta_short_1) + abs(delta_short_2)`.
- Therefore the initial 2 × 0.40 short ratio is represented as approximately 0.80 combined short delta.
- Direction is determined separately from option type and the observed underlying move; it is not inferred from the sign of the absolute-delta metric.
- The engine will retain signed delta as an audit field.

**Reason:** the transcript uses positive-looking values such as 0.30, 0.10, 0.80 and 1.20–1.30 operationally for both calls and puts. This convention makes those thresholds mathematically reproducible without claiming that the video specifies the underlying Greek implementation.

## 2. Delta model
Primary implementation:
- Use vendor-observed historical Greeks if the accepted dataset supplies them with documented methodology and timestamp alignment.
- Otherwise reconstruct delta from contemporaneous option prices using an explicitly documented implied-volatility model.
- Primary reconstructed model: Black-Scholes for European index options, with contemporaneous underlying, option price, expiry time, risk-free-rate input and dividend/yield assumption.
- IV is solved per option observation where the price is valid; no future observations are used.
- If IV cannot be solved reliably, that observation is marked invalid for trigger selection rather than backfilled from future data.
- Model, rates, yield source, interpolation and numerical tolerances will be versioned in Phase 1.

The exact model choice is a research convention and will be sensitivity-tested against vendor Greeks where available.

## 3. Trigger sampling
- Canonical sampling frequency: **one-minute observation timestamps**.
- At each valid one-minute observation, calculate/ingest deltas for the currently held contracts.
- A trigger occurs at the **first observed timestamp at which the threshold condition is satisfied**.
- No interpolation is used between observations.
- OHLC high/low is not treated as proof that a delta threshold was crossed.
- If higher-frequency quote data are available, a separate higher-frequency sensitivity test may be run, but it will not replace the pre-registered one-minute core.

## 4. Strike selection
For each target delta:
1. Restrict to the intended expiry and option type.
2. Exclude observations failing minimum data-quality rules.
3. Exclude contracts with invalid/non-solvable delta.
4. Select the contract minimizing `abs(abs(delta) - target_delta)`.
5. Tie-break by smaller absolute delta error, then higher contemporaneous volume, then lower strike distance from the underlying.
6. The canonical maximum allowed delta error is **0.05**. If no contract satisfies it, the target is unavailable and the engine records a failed/rejected adjustment rather than silently selecting a distant strike.
7. Strike selection uses only information available at the decision timestamp.
8. Liquidity thresholds will be explicit data-quality filters in Phase 1; they will not be invented from future performance.

## 5. Entry timing
The source examples show setup on the day before monthly expiry and describe a 5:15 PM AlgoTest setup time. Since 5:15 PM is outside normal NSE equity-derivatives trading, that timestamp cannot be treated as an executable fill.

Canonical implementation convention:
- Identify the monthly expiry contract intended by the source.
- Generate the setup using the **last valid one-minute observation of the prior trading session**.
- Execute the initial four-leg Iron Condor at the **first valid one-minute observation of the next trading session**.
- If the next session does not have all required contracts/quotes, skip that cycle and log the reason.
- This convention is explicitly labelled an implementation assumption and will be sensitivity-tested with same-session entry where data permit.

## 6. Trigger-to-fill sequence / no look-ahead
At each observation:
1. Read the market state available at timestamp t.
2. Evaluate triggers on the currently held position using information timestamped <= t.
3. If triggered, freeze the old-position exit decision at t.
4. Execute the old-position exit using the defined fill model at t or the first executable quote after t, never a quote from before the trigger.
5. Re-read the market only at the execution/new-decision timestamp.
6. Select new strikes from information available at that timestamp.
7. Execute the new structure.
8. Record all fills, quantities, timestamps, prices, costs and trigger reason.

A newly created position cannot itself trigger an additional adjustment using information from the same timestamp unless the execution model explicitly has a second independent quote event. This prevents same-timestamp look-ahead/feedback.

## 7. Fill model
Primary execution hierarchy:
1. Use contemporaneous bid/ask quotes when available.
2. Marketable buys execute at ask and marketable sells at bid.
3. For a multi-leg structure, each leg is independently filled; there is no free portfolio-level midpoint fill.
4. If bid/ask is unavailable but a valid trade/quote price exists, apply a configurable conservative slippage rule and mark the fill as degraded-quality.
5. If neither valid quote nor permitted fallback price exists, the order is not filled and the event is logged.

The research will report gross mark-to-market P&L separately from execution-adjusted P&L.

## 8. Costs
Costs are modeled per executed leg/order and separated into:
- broker brokerage;
- STT as applicable to the exact option transaction;
- exchange transaction charges;
- SEBI charges;
- GST;
- stamp duty;
- other documented regulatory/clearing charges;
- bid/ask spread;
- explicit slippage.

Paytm Money charges will be period-specific. Official Paytm Money documentation shows that brokerage and statutory charges have changed over time; therefore the Phase 1 cost table must map the backtest date to the contemporaneous schedule rather than use one current rate. For example, Paytm Money documents a ₹20/order F&O brokerage schedule for new users from 25 August 2023, while its later materials describe further pricing changes; official documentation also records a 1 October 2024 STT change on option sales. These facts will be independently reconciled against the exact backtest period before production results. 

## 9. Expiry policy for literal core
The literal deterministic core will:
- permit adjustments during the trading session;
- apply no discretionary profit-taking;
- **force-close every open position at the final valid executable observation of the monthly expiry session**;
- if a required quote is unavailable at the final observation, use the last valid executable quote subject to a documented stale-quote rule and log the exception;
- never carry the strategy beyond the selected monthly expiry.

This is a research convention, not a claim that the video specifies a universal forced-close rule. The video's discretionary expiry discussion will be tested separately.

## 10. Profit-taking
The literal core has **no discretionary profit target**.
Profit-taking variants will be pre-registered separately, for example:
- fixed percentage return;
- fixed rupee return per initial lot;
- source-example-inspired threshold bands.

No threshold will be chosen after examining the full backtest outcome.

## 11. State machine
Allowed states:
- FLAT
- IRON_CONDOR
- RATIO_INITIAL
- RATIO_CONTINUATION
- RATIO_REVERSED

Every transition must have:
- timestamp;
- trigger type;
- previous state;
- new state;
- previous quantities;
- new quantities;
- old and new strikes;
- delta observations;
- execution prices;
- costs;
- reason code.

Illegal transitions are test failures.

## 12. Unit-test invariants
Before production data:
1. Initial IC quantities are exactly -1 call short, +1 call hedge, -1 put short, +1 put hedge.
2. Initial ratio quantities are +1 long, -2 short, +1 hedge on the appropriate option side.
3. Continuation ratio quantities are +1 long, -2 short, +1 hedge.
4. Reversal changes the directional option side and does not leave stale old-side ratio quantities.
5. Combined short delta equals the sum of absolute deltas of the two short contracts.
6. Trigger equality and crossing behaviour are deterministic.
7. No position can use a contract that did not exist at the decision timestamp.
8. No fill can use a quote timestamp earlier than its trigger.
9. Forced expiry close leaves net quantity zero.
10. Every cash-flow leg has exactly one cost record.
11. A rejected/failed adjustment cannot silently change the state.
12. Same-timestamp recursive transitions are prohibited unless explicitly generated by a second independent event.

## 13. Sensitivity dimensions
Pre-registered sensitivity axes include:
- 1-minute versus higher-frequency trigger observations where available;
- delta model/vendor Greeks versus reconstructed Greeks;
- delta tolerance;
- nearest-delta selection versus liquidity-constrained selection;
- bid/ask versus conservative slippage;
- entry timing;
- expiry exit convention;
- profit-taking variants.

These are robustness experiments, not optimization targets for the primary result.
