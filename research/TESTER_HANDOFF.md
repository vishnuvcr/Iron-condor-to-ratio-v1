# Tester Handoff — Phase 0

## Required independent checks
The tester should independently verify:
1. The repository contains the required project controls.
2. The source-derived strategy rules are faithfully represented.
3. No unsupported profit-taking or expiry-day assumption has been silently promoted into the core rules.
4. The research plan has a clear phase gate.
5. The data plan recognizes the need for intraday option-chain information.
6. Literature claims are attributed and not treated as proof of this strategy.
7. The repository is ready for Phase 1 without hidden dependencies.
8. Branch/phase discipline is documented.
9. Error logging and status updates are present.
10. The developer has not advanced into Phase 1 before tester approval.

## Acceptance
Phase 1 may start only after an independent tester report is available and records a pass or explicitly documents required corrections.


# Phase 1 Tester Handoff — 2026-10-03

## Scope
Independently audit the final Phase 1 branch before any Phase 2 backtest-engine work is permitted.

## Required checks
1. Verify immutable source revision 0f4800e is used consistently in the acquisition manifest and workflow.
2. Verify the exact NIFTY-only acquisition scope and that unrelated underlying files are excluded.
3. Verify structural validation has zero hard failures and zero conflicting duplicate-key groups on the final run.
4. Verify exact duplicate rows are handled only by the deterministic deduplication transform and that source/output row counts and SHA-256 hashes are retained.
5. Verify historical bid/ask absence is explicitly documented and not silently replaced by current NSE data.
6. Verify Greek/IV reconstruction, target-delta availability, timestamp alignment, contract metadata, and cost schedules are either evidenced or remain explicit blockers.
7. Verify the final Phase 1 report does not claim strategy profitability or performance.
8. Verify README, research status, error log, and conversation log match the final branch state.
9. Verify GitHub Actions workflow has manual dispatch, caching, concurrency control, and reproducible source acquisition.
10. Verify all Phase 0 gates remain intact and no phase advancement occurred without tester approval.

## Current known issues to test
- 30,363,281 exact duplicate rows were observed in the source audit; these must be deterministically removed and quantified, not discarded silently.
- Historical bid/ask is not present in the primary source schema.
- Partial/illiquid strike coverage may prevent some target-delta selections; availability must be measured before acceptance.

## Acceptance
Phase 1 can advance only if the independent tester records PASS for the final branch and identifies no unresolved methodological or reproducibility blocker. A PASS is not a profitability claim.