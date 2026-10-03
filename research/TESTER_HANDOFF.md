# Phase 1 Tester Handoff — Canonical Gate Contract

Effective: 2026-10-03

The canonical Phase 1 gate IDs are defined only as follows:

| Gate | Meaning |
|---|---|
| G1 | Immutable primary dataset / provenance |
| G2 | Structural schema validation |
| G3 | Duplicate handling |
| G4 | Timestamp and session quality |
| G5 | Underlying/option alignment |
| G6 | Production historical Greeks / IV |
| G7 | Target-delta availability |
| G8 | Historical contract metadata |
| G9 | Historical bid/ask / execution quality |
| G10 | Date-specific transaction costs |
| G11 | Market-context datasets |
| G12 | Repaired CI execution |
| G13 | Independent tester approval |
| G14 | Phase 2 authorization |

This vocabulary is authoritative for all current Phase 1 documents. Older G1–G10 labels in historical evidence are not acceptance IDs.

## E033 normalization
The first independent Phase 1 tester identified ambiguous reuse of G1–G10 between the gate matrix, data specification and acceptance report. Those meanings have now been normalized to the canonical table above.

## Required re-audit
1. Confirm all current Phase 1 documents use the canonical G1–G14 meanings.
2. Confirm the repaired audit has an independently verifiable GitHub Actions run.
3. Confirm G4 session anomalies are reconciled to historical exchange sessions.
4. Confirm G5–G12 are evidenced or remain explicit blockers.
5. Confirm no Phase 2 work or performance claim has been introduced.
6. Record G13 independently; do not infer approval from developer evidence.

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
1. Independently verify successful run 37122686454, job 111201763817, artifact 11274027306 and the reported G1–G12 evidence.
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


## Latest developer evidence package — 2026-10-03
New control artifacts for independent review:
- `research/PHASE1_SESSION_CALENDAR_SPEC.md` — G4 evidence contract.
- `research/PHASE1_CONTRACT_COST_SPEC.md` — G8/G10 evidence contract.
- `research/PHASE1_QUOTE_DATA_PROCUREMENT.md` — G9 procurement and reconstruction contract.
- `data/manifests/phase1_control_sources.json` — source-provenance manifest.
- `scripts/validate_phase1_control_manifests.py` — control-plane manifest validator.

Tester must verify that these additions do not imply data acquisition or gate closure. In particular, G9 remains BLOCKED until historical bid/ask or sufficient order-level data are actually acquired and reconstructed; G12 remains OPEN until the repaired workflow executes successfully in GitHub Actions.


## E035 verification point
- Verify the acceptance report now agrees with the canonical G1 PASS state.
- Verify the market-quality diagnostic contains no hard-coded historical session boundaries; G4 must rely on the date-specific session calendar.
- Treat E035 as a control correction only. G4–G12 remain independently unresolved until production evidence is executed.


## E037 verification point — 2026-10-03
- Independent tester identified a CI command-block defect in `.github/workflows/phase1-data-validation.yml`.
- Corrected commit: `fb5993afa89cfce7fac177d1a62c45e98bddbc27`.
- Required re-audit: verify the syntax-check step contains an explicit multiline `run: |` block and that both `py_compile` and `validate_phase1_control_manifests.py` execute as separate commands in a successful Actions run.
- G12 must remain FAIL/OPEN until that execution is independently verifiable. G13/G14 remain blocked.


- G12 is now supported by successful run 37122686454 / job 111201763817 on commit 68b39d91035bcb79c192cac80f20fd29ed6e709d, with artifact 11274027306. Tester must independently verify the run and artifact before recording G13.


### G12 successful-run verification point — 2026-10-03
- Successful run: 37122686454.
- Job/check: 111201667259 failed only in the earlier E041-superseded execution; final successful job/check: 111201763817.
- Artifact: 11274027306; SHA-256 329eb437e42745f5613e7c41bdf33313977b09d49492513a190d3c1216f01980.
- Tester must independently verify the final run and retain G13 as blocked until its own PASS report is recorded.


## G4 developer-evidence closure — 2026-10-03
- Fresh CI run: `37124047220`; job/check `111205697146`.
- Artifact: `11274239403`; SHA-256 `141abc86ec20be5d34c8c4fcb6735fd04a8da10e4c5e9d7dc15158a5ec7eb48b`.
- Reconciliation result: 1,254 normal eligible dates; 7 documented special-session dates; 1 pre-registered DATA_GAP_EXCLUDED date (2026-06-03); 0 unreconciled dates.
- Normal execution window: 09:15–15:30 Asia/Kolkata. Source observations outside that window are retained for audit but are not eligible for strategy decisions.
- Independent tester must verify the dated special-session references, the 300-timestamp incomplete-session rule, the exclusion of 2026-06-03 from the trading universe, and the zero-unreconciled result before G13 can pass.


## Independent G4/G12 re-audit — 2026-10-03
- Run 37124047220 / job 111205697146 / artifact 11274239403 independently verified successful.
- G4 remains unaccepted because E044 found unresolved_dates in the control manifest that are ignored by the reconciliation script; special-session intervals are not directly validated.
- G12 remains open for final-head acceptance under E045 because the successful run tested dd5447fba974560020084146d6e1101e656a034c, while current branch head is e9fce044ee34f24c3d7ef2422454d57f5af85ab5 and includes later session-control changes.
- G13/G14 remain blocked.
