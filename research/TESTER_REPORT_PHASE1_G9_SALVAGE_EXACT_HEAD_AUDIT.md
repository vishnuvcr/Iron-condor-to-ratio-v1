# Tester Report — Phase 1 G9 Free-Data Salvage Exact-Head Audit

Updated: 2026-10-03

## Role and scope
Role: Independent Tester.
Developer exact head audited: 4698fa62b45fc62ae6c543c168bccdfd3de1d5fc
Developer PR: #28
Tester branch: tester/phase-1-g9-salvage-exact-head-audit

This audit is limited to the Phase 1 G9 free-data salvage implementation at the exact developer head. It does not authorize Phase 2, backtesting, optimization, profitability analysis, or a trading conclusion.

The controlling state remains: G9 BLOCKED; G13 BLOCKED; G14 BLOCKED; Phase 2 BLOCKED.

## Control-file review
Before evaluating the implementation, the tester re-read the active README, research plan, research status, error log, conversation log, Phase 1 gate matrix, Phase 1 acceptance report, tester handoff, quote-data procurement decision, G9 salvage protocol, and G9 source manifest at the audited head.

The control documents consistently state that G9 requires historical bid/ask or deterministic order-level reconstruction and prohibits OHLC/LTP substitution. The salvage protocol also requires raw-file hashes, schema classification, timestamps, contract identity, quote validity, coverage, licensing, and deterministic no-leakage execution evidence.

## Exact-head provenance
The audited developer commit is exactly 4698fa62b45fc62ae6c543c168bccdfd3de1d5fc.
The developer branch is phase-1-g9-free-data-salvage.
PR #28 remains open. No associated PR-triggered Actions run for the current exact head was observable through the available GitHub interface. This is retained as an execution-evidence limitation, not as evidence that the candidate dataset is absent or invalid.

## Finding E060 — G9 workflow does not prove execution against the PR head SHA

### Evidence
The workflow uses actions/checkout@v4 without an explicit ref bound to the pull-request head SHA.
For a pull-request event, checkout normally resolves to the PR merge/test ref unless an explicit head SHA/ref is supplied. The workflow contains no post-checkout assertion of the checked-out commit SHA.
Therefore a successful PR-triggered run, if later observed, would not by itself prove that the validator ran against developer head 4698fa62b45fc62ae6c543c168bccdfd3de1d5fc.

### Impact
This is a reproducibility/control-plane defect and recreates the class of exact-tip evidence problem previously recorded as E045/E051/E052.

### Required correction
Explicitly checkout the PR head SHA for pull_request events and the triggering SHA for push/manual execution, or use an equivalent deterministic strategy. Emit and assert the actual checkout SHA in the machine-readable audit report, failing closed on mismatch.
Disposition: OPEN.

## Finding E061 — Raw-file diagnostics are not yet a production acceptance validator

The validator now performs useful per-file diagnostics: SHA-256, bytes, columns, schema class, row counts, bid/ask counts, quantity presence, timestamp parsing, naive timestamp counts, min/max timestamp, duplicate-row counts, out-of-order counts, contract-identity diagnostics, crossed/negative quote diagnostics, and instrument inventory.

However, it does not convert the G9 acceptance contract into fail-closed tests. Missing controls include:
1. Cross-file schema policy and explicit mixed-schema acceptance/rejection.
2. Timezone/session semantics; naive timestamps are counted but not rejected or normalized.
3. Study-window coverage against an expected date/session set.
4. NIFTY identity and deterministic contract-master mapping.
5. Contract-identity completeness as an acceptance condition.
6. Duplicate event/quote-key conflicts; only exact duplicate rows are counted.
7. Full quote validity including malformed numeric values, quantity validity, spread sanity, and locked/crossed-book policy.
8. Quote-age/staleness at decision timestamps.
9. Depth-level continuity/uniqueness and best-level reconstruction semantics.
10. Deterministic no-future-leakage decision-time reconstruction.
11. Machine-readable licensing/permission evidence.
12. Coverage by contract/expiry/CE-PE; only a global observed-date union is emitted.
13. A final ACCEPT/REJECT/INSUFFICIENT_COVERAGE determination after a completed audit.

The report safely keeps production_acceptance=BLOCKED, but a RAW_FILE_AUDIT_COMPLETE result could still be mistaken for production validation because the acceptance contract is not mechanically tested.
Disposition: OPEN.

## Finding E062 — Current candidate remains unverified at the raw-file level
The pinned candidate is antony9952/Nifty_option_TBT revision 643b48383839947b5fe3ed9483c9f7c0f167e865.
The repository records that the public dataset builder reports incompatible schemas and that local acquisition failed because this environment could not resolve Hugging Face. The hardened workflow now retains an UNEXECUTED_ACQUISITION report when acquisition itself cannot run.
This behavior is correct and must be preserved. However, because no independently observable exact-head CI run/artifact is available, there is currently no raw-file inventory, file hash set, coverage result, or quote-quality result from the salvage workflow that the tester can accept.
This is an evidence gap, not a finding that the candidate data are invalid.
Disposition: BLOCKED / awaiting exact-head CI evidence.

## Positive controls verified
1. G9 remains explicitly blocked.
2. The candidate is pinned to immutable revision 643b48383839947b5fe3ed9483c9f7c0f167e865.
3. Per-file SHA-256 is implemented.
4. Acquisition failure is represented as UNEXECUTED_ACQUISITION rather than dataset rejection.
5. OHLC/LTP is not relabeled as bid/ask.
6. The workflow includes cache restore/save and an immutable revision-derived cache key.
7. Audit artifact upload uses if: always().
8. The workflow exposes workflow_dispatch.
9. The salvage protocol requires the NSE licensed historical F&O Order & Trade route if no free source qualifies.
10. No Phase 2/backtesting/optimization/profitability code or conclusion was introduced by this G9 salvage step.

## Gate determination
| Gate | Tester determination |
|---|---|
| G9 | BLOCKED |
| G13 | BLOCKED |
| G14 | BLOCKED |
| Phase 2 | BLOCKED |

No G9 PASS is issued.

## Required next developer actions
1. Correct exact-head checkout and assert the checked-out SHA in the G9 artifact.
2. Convert the G9 acceptance contract into fail-closed machine-readable validation.
3. Preserve UNEXECUTED_ACQUISITION for network/runtime failures.
4. Obtain an independently observable Actions run at the corrected exact head.
5. Inspect every retained raw CSV, not the Hugging Face viewer alone.
6. Require complete study-window/date/contract/CE-PE coverage accounting.
7. Validate timezone, timestamp ordering, duplicates/conflicts, quote validity, spread, quote age, depth semantics and decision-time no-leakage reconstruction.
8. Retain raw-file SHA-256 and licensing/provenance evidence.
9. Only after a complete free-data candidate passes the common G9 contract should the tester reconsider G9; otherwise continue to the licensed NSE Historical F&O Order & Trade route.
10. Do not start Phase 2 before G13/G14 authorization.

## Tester conclusion
PR #28 is not acceptable for G9 closure at exact head 4698fa62b45fc62ae6c543c168bccdfd3de1d5fc.
The developer hardening is directionally correct and improves the audit substantially, but the current implementation has an exact-head CI provenance defect and lacks several fail-closed production acceptance tests. No candidate-data validity conclusion can be drawn until those controls are corrected and an independently observable exact-head run produces inspectable raw-file evidence.