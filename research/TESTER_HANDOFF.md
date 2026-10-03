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

## Phase 1 tester handoff — latest evidence
### What is independently reproducible
- Pinned primary source revision: 0f4800e.
- Structural validation: 108,625,497 raw rows; 0 hard-failure files; 0 conflicting duplicate-key groups.
- Exact duplicate rows: 30,363,281; deterministic deduplication is required and implemented.
- Prior successful diagnostic run: 596,005 IV/Greek solver observations with r=q=0; this is solver smoke testing only.
### Outstanding acceptance items
1. Execute the repaired Phase 1 CI workflow and verify the new syntax gate, market-quality audit, and session-outlier characterization on the pinned source.
2. Verify date-specific r/q reconstruction and production delta target availability under the frozen rules.
3. Verify historical contract/lot/tick metadata against effective-date NSE sources.
4. Verify date-specific Paytm Money brokerage/statutory cost schedules.
5. Decide the historical quote-data route. The primary source has no bid/ask; NSE's official historical order/trade product is the strongest identified route, but is paid and not yet acquired.
6. Confirm contextual data alignment (NIFTY, India VIX, FII/FPI, DII, GIFT NIFTY/overnight, global volatility/equity, BSE, corporate actions/news where applicable).
7. Review all Phase 1 errors E020–E030 and confirm controls prevent recurrence.
8. Issue an independent PASS/FAIL report before any Phase 2 work.
### Gate rule
Phase 2 remains BLOCKED until an independent tester explicitly approves the completed Phase 1 branch. A methodology/data-quality pass is not a profitability claim.


### Newly closed source-validation items
- **Risk-free rate:** official RBI Weekly Statistical Supplement series confirmed as a historical source for 91-day Treasury-bill primary yields. Complete date-aligned extraction remains open.
- **Paytm Money:** official publications confirm the major brokerage/STT transition dates; the complete statutory/exchange charge schedule remains open.
- **NIFTY contracts:** official NSE circulars confirm effective-date lot-size and expiry changes; production contract metadata remains to be reconciled from effective-date contract files.
- **Quote data:** remains the principal unresolved data-source issue. NSE historical order/trade data is the preferred procurement candidate.
