# Independent Tester Report — Phase 0 Second Gate

**Repository:** vishnuvcr/Iron-condor-to-ratio-v1  
**Role:** Tester  
**Branch:** tester/phase-0-second-audit  
**Audit date:** 2026-10-03  
**Target correction PR:** #3 — Phase 0 corrections: deterministic execution specification

## Verdict

**FAIL — second tester gate not approved.**

The correction patch materially addresses most of the first tester's conceptual blockers and correctly distinguishes source-derived strategy rules from researcher-selected implementation conventions. However, the submitted correction is not yet repository-complete or independently reproducible.

The principal blocker is concrete: PR #3 references and links to `research/OPERATIONAL_CONVENTIONS.md`, and `RESEARCH_STATUS.md) says that file was added, but the PR's changed-file list contains no such file and the file is not retrievable from the correction branch. This makes the promised operational specification unavailable as a repository artifact.

Because the strategy specification explicitly says that the full definitions are in that missing file, the corrected specification cannot currently be treated as a complete, auditable implementation contract.

## 1. First-tester blocker recheck

| Previous blocker | Second audit |
|---|---|
| Signed vs absolute delta | **PASS IN STRATEGY_SPEC** — explicitly defined. |
| Combined short-leg delta | **PASS IN STRATEGY_SPEC** — sum of absolute short-leg deltas specified. |
| Trigger sampling | **PASS IN STRATEGY_SPEC** — one-minute observations specified. |
| Strike selection | **PASS IN STRATEGY_SPEC** — nearest absolute delta, 0.05 tolerance and deterministic tie-break requirement specified. |
| Greek source/reconstruction | **PARTIAL** — source hierarchy and Black-Scholes fallback specified, but numerical inputs/solver conventions need full operational specification. |
| Entry timing | **PASS IN STRATEGY_SPEC** — prior-session setup / next-session first valid observation specified. |
| Trigger-to-fill ordering | **PASS IN STRATEGY_SPEC** — explicit sequence and no-look-ahead language present. |
| Execution | **PASS IN STRATEGY_SPEC** — bid/ask, buy-at-ask/sell-at-bid and leg-level execution specified. |
| Slippage fallback | **PARTIAL** — fallback is required but the exact numerical rule is not visible in STRATEGY_SPEC. |
| Literal-core expiry | **PASS WITH TEST CONDITION** — forced final executable observation close is specified, but stale-quote handling must be formally defined. |
| Discretionary profit-taking | **PASS** — explicitly excluded from literal core. |
| State machine | **PASS IN STRATEGY_SPEC** — states and transition logging specified. |
| Unit-test invariants | **PASS IN STRATEGY_SPEC** — invariants listed. |
| Historical Paytm Money costs | **PARTIAL** — date-specific official schedules are required, but actual verified schedules are not yet present. |
| Mandatory second gate | **PASS** — research plan/status explicitly impose the second gate. |

## 2. Critical repository-integrity finding

PR #3's own patch states:

- `research/OPERATIONAL_CONVENTIONS.md` was added;
- README links to it;
- RESEARCH_STATUS says it was added;
- STRATEGY_SPEC says full definitions are in it.

However, the PR changed-file list contains only:

- CONVERSATION_LOG.md
- ERROR_LOG.md
- README.md
- RESEARCH_PLAN.md
- RESEARCH_STATUS.md
- research/STRATEGY_SPEC.md

The referenced operational-conventions file is absent from the PR artifact and cannot be retrieved from the correction branch.

**This is a release-blocking inconsistency.**

It is not sufficient for the information to appear in the patch text of STRATEGY_SPEC if the repository explicitly promises a separate canonical file and that file is missing.

## 3. Remaining methodological gaps

### 3.1 Greek reconstruction is not yet fully reproducible

The correction says to reconstruct Black-Scholes delta from contemporaneous prices, underlying, expiry time, rate and yield.

For independent reproduction, the final operational document must define:

- exact option-pricing convention;
- IV inversion algorithm;
- price used for IV inversion;
- treatment of zero/negative option prices;
- risk-free-rate source;
- dividend/yield source;
- day-count convention;
- trading-calendar/time-to-expiry convention;
- interpolation, if any;
- numerical tolerance and iteration limits;
- behavior when IV cannot be solved.

Otherwise two correct implementations can still generate different deltas.

### 3.2 Slippage fallback is not numerically frozen

The specification says a configurable conservative fallback applies when bid/ask is unavailable.

For the literal core, the fallback must have a fixed pre-registered numerical definition, not merely be configurable. Otherwise the researcher could alter slippage after seeing results.

A recommended structure is to freeze the primary result's fallback before Phase 1 and reserve alternative slippage values for pre-registered sensitivity tests.

### 3.3 Strike-selection tie-breaking needs the exact ordering

"Deterministic tie-breaks and data-quality filters" is directionally correct but not itself deterministic.

The canonical order should specify, for example:

1. valid contract;
2. absolute delta distance;
3. liquidity criterion;
4. strike ordering;
5. contract identifier.

The exact rule must be written, not left as an implementation detail.

### 3.4 Data-quality filters need thresholds

"Data-quality filters" requires exact definitions.

At minimum define treatment of:

- zero bid;
- zero ask;
- bid > ask;
- stale quote;
- missing OI;
- missing volume;
- duplicate timestamps;
- crossed/locked markets;
- abnormal prices;
- missing underlying observation.

### 3.5 Trigger crossing semantics need explicit inequality rules

The source uses approximate thresholds.

The engine should explicitly define whether:

- IC transition is `abs(short_delta) <= 0.10`;
- continuation trigger is `combined_short_delta <= 0.20`;
- reversal trigger is `combined_short_delta >= 1.20` or another boundary;
- the 1.20–1.30 range means a trigger band or an illustrative range.

This is especially important because the correction currently describes "approximately 1.20–1.30" but does not expose the exact machine threshold.

### 3.6 Direction determination requires an exact rule

The source says the directional ratio follows the observed move. The corrected text preserves the source mapping, but the backtest must define exactly how the observed direction is classified at the transition timestamp.

For example, the implementation needs an explicit rule based on the triggering leg and/or underlying movement. It must not infer direction retrospectively.

### 3.7 Monthly expiry identification

The project correctly recognizes that historical contract specifications can change. The literal core therefore needs a historical contract-master source and an explicit rule for identifying the relevant monthly expiry for every observation.

Current exchange specifications must not be substituted for historical metadata.

## 4. Source-vs-convention separation

This part of the correction is **PASS**.

The new STRATEGY_SPEC clearly states that the machine-level semantics are research implementation conventions rather than claims that the YouTube author specified those exact mechanics.

That distinction must remain intact in the final manuscript.

The source-derived rules should be reported separately from:

- execution assumptions;
- Greek reconstruction;
- sampling;
- strike-selection tolerance;
- cost assumptions;
- slippage;
- expiry handling.

## 5. No evidence of prohibited advancement

I found no evidence in PR #3 of:

- historical performance results;
- profitability claims;
- optimization;
- production backtest results;
- Phase 1 data acquisition;
- Phase 2 engine implementation.

The correction remains appropriately gated.

## 6. Required corrections before re-test

The developer should:

1. Add the missing `research/OPERATIONAL_CONVENTIONS.md` to PR #3, or remove the separate-file claim and place the complete specification in one canonical file.
2. Freeze exact Black-Scholes/IV reconstruction inputs and numerical conventions.
3. Freeze the numerical fallback slippage rule for the literal core.
4. Freeze exact strike-selection tie-breaking.
5. Freeze data-quality thresholds and rejection rules.
6. Freeze exact threshold inequalities and the reversal threshold interpretation.
7. Freeze the direction-classification rule.
8. Freeze historical monthly-expiry identification/contract metadata requirements.
9. Update README/status/error/conversation records after these corrections.
10. Re-submit for the second independent tester gate.

## 7. Gate decision

**PHASE 1: BLOCKED.**

The correction work is substantially on the right track, but the second independent tester cannot approve the gate while the canonical operational-conventions artifact is missing and several numerical details remain implementation-dependent.

No performance conclusion, profitability claim, optimization, or trading conclusion is justified.

## 8. Tester conclusion

The first tester's major conceptual objections have largely been acted upon. The remaining issue is now primarily **reproducibility precision and repository integrity**, rather than a fundamental misunderstanding of the source strategy.

Once the operational specification is actually present and the remaining numerical conventions are frozen, the project should return for another independent tester check before Phase 1.
