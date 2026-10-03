# Research Status

Updated: 2026-10-03

| Phase | Status | Gate |
|---|---|---|
| 0 Specification/audit | **CORRECTIONS IN PROGRESS — SECOND-GATE DEFECTS ADDRESSED FOR RE-TEST** | Independent tester approval required |
| 1 Data | **BLOCKED** | Second tester approval |
| 2 Engine | BLOCKED | Phase 1 |
| 3 Experiments | BLOCKED | Phase 2 |
| 4 Statistics | BLOCKED | Phase 3 |
| 5 Interpretation | BLOCKED | Phase 4 |
| 6 Manuscript/release | BLOCKED | Phase 5 |

## First tester result
Phase 0 received **FAIL / corrections required**. The tester confirmed source fidelity but identified unresolved delta semantics, trigger sampling, strike selection, entry timing, execution/fill sequencing, expiry policy, Paytm Money historical cost verification and unit-test invariants.

## Developer corrections completed on this branch
- Added `research/OPERATIONAL_CONVENTIONS.md`.
- Formalized signed-vs-absolute delta handling and combined short-delta arithmetic.
- Fixed canonical trigger sampling to one-minute observations.
- Defined deterministic target-strike selection and maximum delta error.
- Defined entry timing as prior-session setup with next-session execution for the literal core.
- Defined trigger-to-fill sequencing and no-look-ahead constraints.
- Defined bid/ask leg-by-leg fills with documented fallback slippage.
- Defined literal-core forced expiry close and excluded discretionary profit-taking.
- Added date-specific Paytm Money cost verification requirements.
- Added state-machine and unit-test invariants.
- Updated the research plan with a mandatory second-tester gate.

## Second independent tester result
**FAIL — second gate not approved.** The tester found the canonical operational-conventions artifact missing from PR #3 and identified remaining numerical reproducibility gaps.

## Current developer correction
The branch `phase-0-corrections-v2` now adds the missing tracked artifact and freezes IV/Black-Scholes, slippage, strike selection, data-quality filters, threshold inequalities, direction classification, and historical contract-metadata rules.

## Current conclusion
No performance conclusion exists. Phase 1 remains prohibited until the corrected specification passes independent re-test and approval.

## Third independent tester result
**FAIL — Phase 0 approval not granted.** PR #5 fixed the missing operational-conventions artifact, but the tester found remaining reproducibility blockers: IV solver termination, no-arbitrage bounds, tick rounding, explicit future-quote rejection, and a fallback-slippage wording inconsistency.

## Current gate
Phase 1 remains **BLOCKED**. No historical data acquisition, backtest engine, optimization or performance conclusion may begin until a subsequent tester retest passes.

## Tester branch
`tester/phase-0-third-audit`

## Third tester report
`research/TESTER_REPORT_PHASE0_THIRD.md`
