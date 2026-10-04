# Independent Tester Audit — Phase 2 E150 Final Audit
Date: 2026-10-04
Developer head audited: a60c785215558f90eab32be5babde2af9a55ff31
Tester branch: tester/phase-2-e150-final-audit-20261004

## Verdict

**CONDITIONAL PASS FOR CONTINUED DEVELOPMENT — PRODUCTION ACCEPTANCE DEFERRED.**

E150's normal-session 15:30/15:31 contamination mechanism is correctly blocked by the new cutoff logic and regression test. However, the audit cannot establish that E150 is non-material for the historical tested window because the pinned raw option partitions/results are not available through the repository content surface for independent inspection, and no fresh exact-head production workflow artifact is observable through the available GitHub Actions connector.

A final profitability/trading-strategy conclusion remains prohibited.

## 1. Exact-head identity and reproducibility

- Developer head: a60c785215558f90eab32be5babde2af9a55ff31.
- Commit title: Phase 3: link pre-results manuscript framework.
- Compared with prior audited developer head 923c50a32af703b46158e1ab2a882dc2e47235d4: 12 commits ahead, 0 behind.
- The exact-head Actions lookup available to the tester returned zero workflow runs.
- No previous artifact is relabelled as evidence for this head.

**Finding:** exact-head production reproducibility remains unproven.

## 2. E150 implementation audit

The corrected builder now loads phase1_session_rules.json, resolves a date-specific execution-session endpoint, accepts an expiry-day observation only when it is on the expiry date and at or before that endpoint, retains the latest qualifying observation, and fails closed if no qualifying expiry-day observation exists.

The regression fixture creates a valid expiry close at 15:30 IST and a post-session observation at 15:31 IST, and verifies that the 15:31 observation cannot move the stored close beyond 15:30.

**Result:** PASS for the ordinary regular-session boundary tested by the fixture.

## 3. E150 materiality mechanism

The engine's _expiry_cutoff() takes the minimum expiry_close_ts across the position and subtracts the configured one-minute force-close interval. _should_force_close() then triggers when the session timestamp reaches that cutoff.

Therefore an erroneous expiry close can directly change the forced-close decision timestamp, next eligible option-bar execution, fill prices and slippage, transaction costs, terminal cash/P&L, and potentially whether a cycle closes successfully.

This establishes **potential materiality**, not measured materiality.

The current repository content surface does not expose the raw pinned option partitions needed to count post-session expiry observations or compare old/new affected cycles. The tester therefore cannot honestly certify that E150 is non-material without a rerun or an equivalent deterministic impact scan over the affected source data.

## 4. Additional chronology finding — special-session interval membership

A residual logic issue remains in expiry_execution_close_ts(). For a special session with multiple disjoint execution intervals, the implementation selects the maximum interval endpoint and then accepts any expiry-day observation satisfying timestamp <= cutoff.

That is not equivalent to membership in one of the permitted execution intervals. An observation in a non-trading gap between two special execution intervals could therefore become the expiry close.

This does not currently establish a historical impact on the study's monthly-expiry sample, because the audited repository materials do not provide a qualifying affected expiry-day observation. It is nevertheless a correctness defect in the generic chronology control and should be corrected before production acceptance.

Recommended correction: expose a date-specific execution-timestamp predicate; require the timestamp to belong to an allowed execution interval, not merely precede the latest interval endpoint; add a regression fixture for a multi-interval day containing an in-gap observation.

## 5. Session-rule horizon consistency

The contract-master builder declares a study end of 2026-09-30, while the inspected session manifest declares its study data end as 2026-07-02.

For dates beyond the session-manifest horizon, the current builder can fall back to the regular session endpoint rather than failing on an out-of-coverage date.

This should be reconciled before any production result claims coverage beyond the session-rule evidence horizon. If the actual pinned data end is 2026-07-02, the contract-master study end should be aligned or explicitly bounded to that date.

## 6. E146/E147/E148/E149

### E146 — CLOSED
The production workflow uses valid GitHub Actions expression syntax.

### E147 — CLOSED
The five scenario artifact names and analysis download pattern are aligned, and the workflow asserts all five registered scenarios: 0/5/10/20/50 bps.

### E148 — PARTIALLY CLOSED
The monthly contract-master reconstruction is deterministic and provenance-aware, with official lot-size chronology and lifecycle reconstruction. It remains a reconstruction rather than original NSE member-file bytes. Independent exact-result manifest validation and production execution evidence remain outstanding.

### E149 — OPEN
Exact-head Actions execution is not independently observable through the available connector. No production result is accepted on this basis.

## 7. State-machine / execution / cost audit

Source inspection confirms completed-bar decision chronology, strict bisect_right next-bar execution, atomic multi-leg execution staging, adverse slippage with tick-size floor, date-effective charge resolution, cost calculation from the completed fill ledger, static IC comparator mode, and separation of the theoretical expiry-loss/margin proxy from historical SPAN.

No new mathematical or sign error was identified in these inspected paths during this audit.

The absence of fresh production ledgers means these are code-level findings, not production-result validation.

## 8. Statistical/manuscript lock

The pre-results statistical plan and manuscript framework correctly prohibit final profitability inference, parameter selection from provisional results, result-bearing manuscript sections before immutable audited production ledgers, and treating E150-dependent analyses as final.

This control is appropriate and is retained.

## 9. Required next actions

1. Correct special-session interval membership, or document and independently demonstrate that no affected expiry dates exist in the study sample.
2. Reconcile the contract-master study horizon with the session-rule evidence horizon.
3. Regenerate the contract master after chronology corrections.
4. Obtain an independently observable exact-head five-scenario workflow execution.
5. Independently audit all five ledgers, manifests, checksums, costs, slippage, look-ahead controls and paired static-IC results.
6. Quantify E150 impact using either a deterministic old-vs-corrected expiry-close impact scan over the pinned source data, or the required affected production rerun.
7. Only then unlock final statistical inference and the trading-strategy conclusion.

## Tester conclusion

The developer's ordinary 15:30/15:31 E150 correction is valid, but **E150 cannot yet be classified as non-material**. The correct scientific disposition is therefore:

**Continue research and manuscript preparation under the lenient gate; do not finalize profitability, tradability, or a recommended strategy.**

### Tester → Developer instruction

Fix the multi-interval session predicate and session-horizon consistency, regenerate the contract-master candidate, then obtain exact-head production evidence. If the raw data demonstrate any E150-affected expiry cycle, rerun the affected scenarios before final inference. Do not relabel historical artifacts as corrected-head results.

### Developer → Tester instruction for the next gate

After the developer remediation, independently verify the corrected session predicate, contract-master manifest, exact Git SHA, five-scenario workflow artifacts, and E150 impact scan. Reject any profitability conclusion until the affected-data question is quantitatively closed.