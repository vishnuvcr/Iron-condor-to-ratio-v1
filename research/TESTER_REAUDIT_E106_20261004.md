# Tester Re-audit — E106 exact developer head

## Scope
Independent audit of developer head b75e64d3f6caf9f086a0c063153ccc6315aa5c5a after E106. Tester branch is isolated from developer work.

## Mandatory checks
1. Verify all current control files and gate states.
2. Verify E106 RBI collector actually prioritizes the four known official WSS IDs and retains immutable SHA/provenance checks.
3. Verify strict-prior/no-lookahead semantics and regression coverage.
4. Verify no secondary RBI source has silently entered production.
5. Verify exact-head GitHub Actions evidence exists and checkout SHA equals the audited developer head.
6. Verify any G6 production artifact is bound to the exact audited SHA and contains valid risk_free.csv/dividend_yield.csv inputs.
7. Check mathematical, schema, provenance, duplicate/conflict, coverage, and fail-closed logic.
8. Confirm G5 remains FAIL/WAIVED, G9 PASS, G13/G14 BLOCKED, Phase 2 BLOCKED unless independently justified otherwise.

## Current CI evidence warning
The developer reports no workflow run exposed for the corrected commits. This must be independently verified; absence of exact-head CI is a G6/G12 evidence failure, not a PASS.

## Gate decision
Do not approve G6 without exact-head CI plus artifact/provenance evidence. If defects are found, document them precisely and return a tester PR/report to the developer. Do not modify developer code from this tester branch.

## Handover instruction
Developer must not advance G6 or Phase 2 until this independent report is completed and all tester findings are addressed.

## Independent findings

### E106 implementation
- PASS: the audited source tries candidate IDs from EXPECTED_SHA256 before the fallback archive scan.
- PASS: cached pages require sidecar SHA agreement, expected SHA agreement for bootstrapped IDs, source-ID agreement, and target-series presence.
- PASS: same-day strict-prior regression is present.
- PASS: the specification documents the conservative observation-date eligibility convention and prohibits look-ahead.

### Exact-head CI evidence
- FAIL: commit b75e64d3f6caf9f086a0c063153ccc6315aa5c5a has zero workflow runs exposed by the GitHub Actions evidence API available to the tester.
- Therefore there is no independently verifiable exact-head execution, no exact-head production artifact, and no basis to claim that the E106 collector produced usable risk_free.csv and was consumed by the G6 production audit.
- The earlier long-running run 37171349785 is not accepted as evidence for this head because it predates E106 and never reached downstream evidence.

## Tester gate decision

**G6 = FAIL / OPEN.**

The code-level E106 correction is substantively plausible, but the mandatory exact-head CI/artifact evidence gate is not satisfied. G5 remains FAIL/WAIVED FOR CONTINUED RESEARCH; G9 remains PASS; G13/G14 and Phase 2 remain BLOCKED.

### Required developer actions
1. Obtain an observable Actions execution whose checkout SHA equals the exact corrected developer head.
2. Verify the RBI acquisition actually completes from the known official WSS candidates or fails closed with an explicit diagnostic.
3. Verify the resulting evidence artifact is bound to the exact checkout SHA and contains provenance/coverage/duplicate/conflict/no-lookahead diagnostics.
4. If exact-head CI cannot be dispatched through the available connector, provide a repository-native automatic workflow mechanism that demonstrably triggers on the corrected developer head; do not treat a manual user run as implicit evidence.
5. Re-handover the resulting exact head to a fresh isolated tester branch after corrections.

**Tester instruction to developer:** Do not advance G6, G13/G14, or Phase 2 until exact-head CI and artifact evidence are independently verifiable and this failure is re-audited.
