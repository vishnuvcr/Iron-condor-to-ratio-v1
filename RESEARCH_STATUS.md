# Research Status

Updated: 2026-10-03

| Phase | Status | Gate |
|---|---|---|
| 0 Specification/audit | **CORRECTIONS IN PROGRESS — FOURTH-GATE DEFECTS ADDRESSED FOR RE-TEST** | Current independent tester approval required |
| 1 Data | **BLOCKED** | Current independent tester approval for Phase 0 |
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
**FAIL — Phase 0 approval not granted.** The third audit confirmed the canonical operational artifact exists, but found five remaining deterministic gaps: IV solver termination, no-arbitrage bounds, tick rounding, explicit future-quote rejection, and strategy-spec/slippage inconsistency.

## Third correction pass
The branch `phase-0-corrections-v3` resolved B1–B5 and added the Phase 0 GitHub Actions integrity workflow. A fourth independent tester then failed B6 because the live plan/status/README records still contained stale gate wording and the Phase 2 slippage wording did not explicitly restrict configurability to sensitivity variants.

## Gate
**Phase 1 remains BLOCKED.** Independent tester approval is required before any historical data acquisition or backtest work.

## Fourth independent tester result
**FAIL — Phase 0 approval not granted.** B1–B5 were confirmed resolved. B6 identified stale/inconsistent active gate records and ambiguous Phase 2 slippage wording. Phase 1 remains prohibited.

## Fourth correction pass
The branch `phase-0-corrections-v4` synchronizes the active gate to the current independent tester approval model, makes the literal-core slippage assumption fixed while restricting alternatives to pre-registered sensitivity variants, updates the active branch/state references, and strengthens the Phase 0 integrity checks. Another independent tester gate is required before Phase 1.

## Current gate
**Phase 1 remains BLOCKED.** The current Phase 0 correction pass must receive independent tester approval before any historical data acquisition, backtesting, optimization or performance assessment begins.

## Current developer correction PR
PR #9 / `phase-0-corrections-v4` is the active developer correction pass for B6. The repository integrity workflow has passed on this branch. A fresh independent tester approval is still required before Phase 1.

## Fifth independent tester result
**FAIL — Phase 0 approval not granted.** PR #9 resolves the fourth gate's active-record and slippage-language defects, and B1–B5 remain substantively resolved. The fifth audit found B7: the Phase 0 integrity workflow's multiline stale-v2 grep assertion is ineffective under standard grep, and B8: the claimed v4 workflow pass is not independently auditable from the available commit status/check evidence. Phase 1 remains blocked.

## Fifth tester gate artifact
The complete independent report is `research/TESTER_REPORT_PHASE0_FIFTH.md` on branch `tester/phase-0-fifth-audit`. Required corrections are to fix the stale-branch assertion, rerun the integrity workflow on the exact resulting commit, persist an auditable workflow/check reference, and submit the corrected pass for another independent tester review.
