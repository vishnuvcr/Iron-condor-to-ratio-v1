# Strategy Specification — Source-Derived

## Core deterministic rules extracted from the uploaded transcript

### Initial position
- Instrument: NIFTY monthly options as described in the video.
- Short call: approximately 0.30 delta.
- Long call hedge: approximately 0.10 delta.
- Short put: approximately 0.30 delta.
- Long put hedge: approximately 0.10 delta.

The source explicitly states this initial structure. fileciteturn0file0L292-L307

### Transition trigger
When either short Iron Condor leg reaches approximately 0.10 delta, exit the entire Iron Condor and transition to a ratio spread aligned with the observed direction. The source says the strategy does not return to the original Iron Condor after transition. fileciteturn0file0L328-L370

### Downward move
Create a call-side ratio:
- long call around 0.50 delta
- short 2 calls around 0.40 delta
- long hedge call around 0.10 delta

### Upward move
Create a put-side ratio:
- long put around 0.50 delta
- short 2 puts around 0.40 delta
- long hedge put around 0.10 delta

These directional constructions are explicitly described by the source. fileciteturn0file0L375-L415

### Same-direction continuation
When the combined delta of the two short option positions moves from about 0.80 to about 0.20, exit the whole ratio and reset in the same direction:
- long around 0.40 delta
- short 2 around 0.30 delta
- hedge around 0.08 delta

The source explicitly gives this trigger and construction. fileciteturn0file0L427-L501

### Reversal
When the combined short-leg delta rises to roughly 1.20–1.30, exit the ratio and switch to the opposite directional ratio. fileciteturn0file0L505-L543

## Rules requiring explicit operational definitions before Phase 1
1. Whether delta means signed Black-Scholes delta, absolute delta, or platform-displayed delta.
2. How “approximately” is implemented when exact delta is unavailable.
3. Whether the trigger is checked continuously, every minute, or at another frequency.
4. Whether fills occur at bid/ask, LTP, midpoint, or another execution rule.
5. What happens if the target delta strike changes between observations.
6. What happens when no contract is sufficiently close to the requested delta.
7. Exact entry time and whether the first position is established one trading day before monthly expiry, as shown in the video examples, or under a broader rule.
8. Profit-taking threshold. The video gives examples such as exiting after substantial profit, but does not provide one universal deterministic threshold. fileciteturn0file0L895-L943
9. Exact expiry-day policy. The video sometimes recommends exiting before expiry and sometimes demonstrates discretionary expiry-day management. fileciteturn0file0L943-L1088
10. Whether all adjustments are made immediately when the trigger is crossed or only after confirmation.
11. Exact brokerage/cost assumptions. These will be a separate configurable execution layer.

## Backtest principle
The first production backtest will have a **literal-core mode** containing only rules that can be made deterministic without inventing an unstated trading preference. Any discretionary rule will be a separately labeled variant and will not be mixed into the core result.
