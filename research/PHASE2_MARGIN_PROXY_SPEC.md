# Phase 2 — Capital and Margin Proxy Specification

Updated: 2026-10-04

## Boundary

The strategy research does not currently possess a complete historical NSE/SPAN margin file synchronized to every option contract and date. It therefore must not present broker margin as historical fact.

The primary capital metric is a deterministic **theoretical expiry-loss capital proxy**.

## Position risk proxy

For every newly established IC or ratio position:

1. Use the actual executed fill prices of the newly opened legs.
2. Compute the net premium cash received/paid by the position.
3. Compute expiry intrinsic payoff for every leg across the piecewise-linear strike grid.
4. Evaluate the grid at:
   - zero;
   - every distinct strike in the position;
   - a sufficiently high underlying bound above the largest strike.
5. Because the source structures have equal total long and short contract count, expiry payoff is bounded at the extremes. The minimum portfolio P&L over the breakpoint grid is the theoretical maximum loss proxy.
6. Capital proxy = max(0, negative minimum expiry P&L).

## Why this is used

The proxy is:
- deterministic;
- based on actual executed premium;
- independent of future path;
- conservative for defined-risk payoff structures;
- reproducible without historical broker margin files.

It is **not** the same as:
- NSE SPAN margin;
- broker exposure margin;
- portfolio margin offsets;
- intraday peak margin requirements.

## Capital utilization

For each cycle:
- report maximum open-position capital proxy;
- report net cycle P&L / maximum capital proxy;
- report aggregate capital occupancy time;
- report peak concurrent proxy capital.

The primary P&L result remains absolute and net of costs. Risk-adjusted capital metrics are secondary and explicitly labelled as proxy-based.

## Future enhancement

When historical daily SPAN/exposure margin files become available, rerun the margin analysis without changing the strategy rules or execution model. Compare proxy capital with actual historical margin requirements.
