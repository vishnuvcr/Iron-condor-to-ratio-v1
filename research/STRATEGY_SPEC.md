# Strategy Specification — Source + Operational Definition

## A. Source-derived strategy rules

### Initial position
- NIFTY monthly options as described in the video.
- Short call approximately 0.30 delta.
- Long call approximately 0.10 delta.
- Short put approximately 0.30 delta.
- Long put approximately 0.10 delta.

The source explicitly states this structure. fileciteturn0file0L292-L307

### Transition
When either short IC leg reaches approximately 0.10 delta, exit the IC and transition to a directional ratio. The source says the strategy remains in the ratio framework rather than returning to the original IC. fileciteturn0file0L328-L370

### Direction mapping
- Downward market move → call-side ratio.
- Upward market move → put-side ratio.

Initial ratio:
- long approximately 0.50 delta;
- short 2 lots approximately 0.40 delta;
- long hedge approximately 0.10 delta.

fileciteturn0file0L375-L415

### Continuation
When combined short-leg delta moves from approximately 0.80 to approximately 0.20, reset in the same direction:
- long approximately 0.40 delta;
- short 2 lots approximately 0.30 delta;
- hedge approximately 0.08 delta.

fileciteturn0file0L427-L501

### Reversal
When combined short-leg delta rises to approximately 1.20–1.30, exit and switch to the opposite directional ratio. fileciteturn0file0L505-L543

## B. Research operational conventions

The video does not define the following machine-level semantics. They are therefore explicitly labelled **research implementation conventions**, not source claims. They are frozen before Phase 1 and will be sensitivity-tested.

1. **Delta convention:** signed delta retained internally; absolute delta used for target matching and threshold calculations. Combined two-short delta = sum of absolute deltas.
2. **Sampling:** one-minute observations; first observed threshold satisfaction triggers. No intra-minute interpolation from OHLC.
3. **Greek source:** vendor historical Greeks where documented; otherwise reconstructed Black-Scholes delta from contemporaneous prices, underlying, expiry time, rate and yield. Invalid IV/delta observations are rejected rather than forward-filled.
4. **Strike selection:** nearest absolute-delta contract within maximum 0.05 delta error, with deterministic tie-breaks and data-quality filters. No valid contract → rejected target and logged event.
5. **Entry:** use the last valid one-minute observation of the prior trading session to determine the setup, then execute at the first valid one-minute observation of the next trading session. This resolves the video's illustrative 5:15 PM setup timestamp, which is outside normal NSE derivatives trading.
6. **Trigger-to-fill:** evaluate using information available at t; exit old position; re-read only at executable decision time; choose new strikes only from information available then; execute new legs. No future data.
7. **Fill:** contemporaneous bid/ask where available; buy at ask and sell at bid; each leg filled independently. Configurable conservative fallback slippage applies when bid/ask is unavailable.
8. **Literal-core expiry:** no discretionary profit-taking; force-close all positions at the final valid executable observation of the monthly expiry session and record any stale-quote exception.
9. **Costs:** model Paytm Money brokerage plus STT, exchange charges, SEBI charges, GST, stamp duty and documented regulatory/clearing charges using date-specific official schedules.
10. **State machine:** FLAT → IRON_CONDOR → RATIO_INITIAL/RATIO_CONTINUATION → RATIO_REVERSED as appropriate; every transition is logged.
11. **No recursive same-timestamp transitions:** a new structure cannot trigger again from the same observation unless a separate independent event exists.
12. **Unit-test invariants:** exact quantities, delta arithmetic, direction mapping, threshold crossing, no future contract use, fill ordering, zero-at-expiry, one cost record per cash-flow leg, and rejection handling.

Full definitions are in the canonical tracked file [research/OPERATIONAL_CONVENTIONS.md](OPERATIONAL_CONVENTIONS.md). The correction branch freezes the exact numerical semantics required for independent reproduction, including IV inversion, quote filters, strike tie-breaking, threshold inequalities, direction classification, fallback slippage, and historical contract metadata.

## C. Explicitly excluded from the literal core
The video discusses discretionary profit-taking and discretionary expiry-day management; it does not provide one universal deterministic threshold. These remain separate, pre-registered sensitivity variants. fileciteturn0file0L895-L943

## D. Research interpretation rule
No performance result may be described as “the video's actual backtest result” unless the data, execution convention and rule configuration exactly match a documented implementation. Source examples are treated as demonstrations, not representative evidence; the video itself states that selected months were shown. fileciteturn0file0L2164-L2209
