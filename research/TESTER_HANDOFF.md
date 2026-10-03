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
Phase 1 may start only after the **current independent tester gate** records a pass for the latest Phase 0 correction pass. Historical labels such as first/second/third/fourth tester are audit history only and do not define the active gate. A FAIL requires corrections on a new developer correction pass and another independent re-test before Phase 1 can start.

## Current gate state
The current developer correction branch is `phase-0-corrections-v4`. The fourth tester report (PR #8) failed B6 repository-control synchronization. Phase 1 remains blocked pending independent approval of the v4 correction pass.
