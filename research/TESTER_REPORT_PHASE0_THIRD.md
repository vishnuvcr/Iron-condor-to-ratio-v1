# Tester Report — Phase 0 Third Independent Gate (PR #5)

**Date:** 2026-10-03  
**Role:** Tester  
**PR under test:** #5 — Phase 0 v2 corrections: freeze reproducibility contract  
**Developer branch:** phase-0-corrections-v2  
**Tester branch:** tester/phase-0-third-audit

## Verdict

**FAIL — Phase 0 approval is not granted. Phase 1 remains BLOCKED.**

PR #5 resolves the principal defects from the second gate: research/OPERATIONAL_CONVENTIONS.md is now a tracked file on the correction branch, and the requested major conventions are substantially frozen.

However, several machine-level details remain implementation-dependent or internally inconsistent. These are sufficient to prevent an independent implementation from being guaranteed to produce the same literal-core event/price stream.

## What passed

1. Canonical operational-conventions artifact exists on phase-0-corrections-v2.
2. Delta sign/absolute-value semantics are explicit.
3. Literal-core threshold inequalities are explicit: <= 0.10, <= 0.20, >= 1.20, with equality triggering.
4. One-minute event sampling and no intraminute interpolation are explicit.
5. Black-Scholes model equations, inputs, IV bracket, maximum iterations, and post-solve price-error check are substantially specified.
6. Strike eligibility and deterministic selection ordering are substantially specified.
7. Direction classification for single/both simultaneous IC triggers is explicit and does not use future observations.
8. Trigger-to-fill ordering and no-look-ahead requirements are explicit.
9. Primary bid/ask leg execution and a fixed fallback slippage formula are explicit.
10. Historical expiry/lot-size/tick-size sourcing is explicitly historical rather than retroactively using current specifications.
11. Literal-core expiry treatment excludes discretionary profit-taking.
12. Costs explicitly include Paytm Money plus statutory/exchange/regulatory components, with date-specific historical schedules required.
13. State-machine states and minimum unit-test invariants are listed.
14. Source-derived rules remain separated from research implementation conventions.

## Remaining blockers

### B1 — IV solver is not fully reproduction-frozen

The document specifies Brent bracketing, an initial/maximum volatility bracket, a pricing tolerance and maximum iterations, but does not specify numerical root-solver tolerance/termination parameters or an exact implementation/library/version.

Two conforming implementations can therefore stop at different volatility estimates while both satisfying the stated price-error test. Because strike selection depends on delta proximity, this can change the selected contract near a target/tolerance boundary.

**Required:** freeze solver implementation semantics, including root tolerance(s), relative tolerance if applicable, termination rule, and either exact algorithm/version-independent pseudocode or a pinned library/version.

### B2 — No-arbitrage bounds are referenced but not mathematically frozen

The specification says to reject prices outside no-arbitrage bounds with one historical tick of rounding tolerance, but does not state the exact call/put lower and upper bound equations, nor exactly how the one-tick tolerance is applied.

**Required:** write the exact bounds and inequality semantics for calls and puts, including the precise tick-based tolerance operation.

### B3 — Tick rounding direction is not algorithmically frozen

“Rounded away from the trader” is economically understandable but leaves implementation choices. The literal core needs an exact rule such as buy prices rounded upward to the next valid tick and sell prices rounded downward to the prior valid tick, with explicit handling when the unrounded price is already on-grid.

**Required:** freeze exact ceil/floor semantics and decimal/tick arithmetic.

### B4 — Future-dated quotes are not explicitly rejected by the generic quote-quality filter

The freshness rule says a quote “may not be more than 120 seconds older,” which does not explicitly state that a quote timestamp later than the decision timestamp is invalid. Other sections imply no future data, but the executable quote eligibility rule should itself be explicit.

**Required:** add quote_timestamp <= decision_timestamp (or an explicitly defined execution-time exception) to the executable/Greek quote rule.

### B5 — Internal inconsistency remains in STRATEGY_SPEC.md

The operational conventions freeze the literal-core fallback slippage to max(2*tick_size, 0.005*reference_price), but research/STRATEGY_SPEC.md still describes the fallback as “configurable conservative fallback slippage.”

That wording is inconsistent with the canonical literal-core contract and can cause an independent implementer to believe the core parameter is free.

**Required:** change the strategy specification to say the literal-core fallback is the frozen formula and that configurable alternatives are sensitivity variants only.

## Non-gating repository-control observation

The correction branch contains no .github/workflows directory. This is not a reason to invent Phase 1 work, but the standing project requirements call for automated/manual GitHub Actions workflows and automatic execution. These should be explicitly scheduled as a repository-control deliverable before the corresponding phases begin, with no manual user-run dependency.

## Gate decision

Because B1–B5 affect deterministic implementation/reproduction, **Phase 0 is not approved**.

No data acquisition, backtest engine, optimization, performance result, profitability claim or trading conclusion should begin.

## Retest requirements

A passing retest requires:
- B1–B5 resolved;
- canonical operational file and strategy specification mutually consistent;
- updated README/status/error/conversation records;
- a new tester review against the resulting branch/PR;
- no Phase 1 advancement before that approval.

The prior second-gate defect concerning the missing operational artifact is considered **resolved** on PR #5.
