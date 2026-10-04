# Independent Tester Audit — Phase 2 Final Freeze — 2026-10-04

## Verdict

**CONDITIONAL PASS FOR PHASE 2 MILESTONE / NOT YET PRODUCTION-READY**

The frozen developer head `374704bf544cde75f051b816bfdba47a799db615` contains a coherent deterministic engine and substantial pre-production hardening. The core state-machine design, chronology, atomic multi-leg execution, cost-layer architecture, static-IC comparator design, normalization controls, and fail-closed historical contract-master requirement are acceptable for continued research.

However, the production workflow at this exact head has two concrete reproducibility/orchestration defects:

1. GitHub Actions expression interpolation is malformed in several places (for example `ref: ${inputs.expected_commit_sha ...}` rather than GitHub expression syntax `${{ ... }}`). This must be corrected before relying on the workflow for production execution.
2. The analysis job downloads artifacts using pattern `slippage-*-bps`, while the run matrix uploads artifacts named `phase2-backtest-<bps>bps`. Therefore the analysis stage cannot reliably consume the intended scenario artifacts.

These are **workflow defects**, not evidence of a mathematical error in the backtest engine itself. The owner-authorized lenient gate policy permits the Phase 2 research to continue, but production P&L generation must remain deferred until these workflow defects and the historical contract master are resolved.

## Exact-head provenance

- Developer head audited: `374704bf544cde75f051b816bfdba47a799db615`
- Developer branch: `phase-2-backtest-engine-20261004`
- Tester branch: `tester/phase-2-final-freeze-20261004`
- Exact-head GitHub Actions workflow runs observable: **0**
- No CI pass is claimed from the absence of runs.

## Independent findings

### 1. State machine — acceptable for milestone

The implementation has explicit states FLAT, IRON_CONDOR and RATIO; first monthly entry is consumed once; transitions use threshold crossings; failed multi-leg groups do not partially commit; trigger consumption/re-arm state is explicit; forced close is represented as a separate event.

The implementation correctly uses a completed decision timestamp and searches strictly after it for the next execution-eligible bar.

### 2. Atomic execution — acceptable

`_execute_group` stages all intended fills before committing them to the fill ledger and cash state. If any leg lacks an eligible next bar or has invalid fill inputs, the group fails without committing staged fills.

This matches the frozen atomic multi-leg requirement.

### 3. Chronology / timezone — corrected and acceptable

The tester confirms the Phase 2 implementation explicitly handles timezone-naive G6 timestamps as Asia/Kolkata and converts timezone-aware values to Asia/Kolkata. The dedicated regression test covers this behavior.

The next-execution lookup uses a strict `bisect_right` after the decision timestamp, preventing same-bar execution.

### 4. Trigger semantics — acceptable with documented source interpretation

The IC transition uses a crossing from prior delta > 0.10 to current delta <= 0.10. Ratio continuation uses a downward crossing through 0.20; reversal uses an upward crossing through 1.20.

The source's discretionary profit-taking remains excluded from the literal core, as required.

### 5. Slippage — acceptable as a proxy

The fill model applies adverse proportional slippage with a historical tick-size floor. The configured scenarios are 0/5/10/20/50 bps.

This is correctly described as proxy execution rather than historical bid/ask reconstruction.

### 6. Costs — architecture acceptable; no production result yet

The cost layer resolves date-effective brokerage and statutory charges and calculates monthly NSE slab charges from the completed fill ledger. Unit-conversion tests and date/side coverage validation are present.

The earlier E141 conversion defect was material but was corrected before production use and explicitly regression-tested.

### 7. Static IC benchmark — acceptable design

The benchmark uses the same engine with transitions disabled and therefore shares the same execution, cost, expiry and slippage conventions. This is appropriate for paired comparison.

### 8. Historical contract master — correctly fail-closed

The engine requires authoritative historical contract metadata for lot size, tick size, lifecycle and expiry-close treatment. The specification correctly prevents projection of current contract rules backward.

This remains the principal scientific/data dependency before historical-contract-correct production results.

### 9. Margin proxy — acceptable with proper labeling

The theoretical expiry-loss capital proxy is appropriately distinguished from NSE SPAN, broker exposure margin and historical peak-margin requirements. It must remain labelled as a proxy in all results.

### 10. Production workflow — correction required

The workflow source at the audited SHA contains malformed expression interpolation in checkout and related steps. In addition, the analysis artifact-selection pattern does not match the artifact names emitted by the matrix run.

These defects mean the frozen workflow cannot yet be treated as a reproducibly executable production pipeline.

## Newly recorded tester defects

### E146 — Phase 2 workflow expression interpolation defect
Several GitHub Actions expressions in `.github/workflows/phase2-production-backtest.yml` use single-brace interpolation such as `${inputs.expected_commit_sha ...}` rather than GitHub Actions' required `${{ ... }}` expression syntax.

**Impact:** checkout/ref selection and related workflow expressions may be interpreted literally or otherwise fail, preventing reliable exact-head production execution.

**Required resolution:** correct every affected GitHub Actions expression and independently inspect the resulting workflow before production execution.

### E147 — Phase 2 analysis artifact-pattern mismatch
The matrix job uploads artifacts named `phase2-backtest-0bps`, `phase2-backtest-5bps`, etc., while the analysis job requests download pattern `slippage-*-bps`.

**Impact:** the analysis stage may receive zero intended scenario artifacts, preventing the planned combined analysis from operating on the production outputs.

**Required resolution:** make upload/download artifact naming and pattern exactly consistent, then add a fail-closed assertion that all five registered scenarios are present before analysis.

## Milestone disposition

**PASS for continued Phase 2 research development, CONDITIONAL for production execution.**

The owner-authorized lenient gate policy is applied. The tester therefore does not block further methodology/documentation work solely because exact-head CI is currently unobservable.

The following remain mandatory before any production profitability claim:

1. authoritative historical NIFTY contract master;
2. corrected production workflow expressions;
3. corrected analysis artifact matching with fail-closed scenario-count check;
4. reproducible production execution;
5. independent final audit of the resulting trade/fill/cost/statistics ledgers.

No P&L, Sharpe, drawdown, CAGR, or trading-strategy conclusion is accepted by this tester at this milestone.

## Tester → Developer instructions

Proceed to correct E146/E147 and acquire/validate the historical contract master. Then run the production workflow through all five slippage scenarios and retain immutable artifacts. Do not report profitability until the resulting ledgers and statistical outputs have been independently audited.

The tester will perform the consolidated audit after production artifacts are available.
