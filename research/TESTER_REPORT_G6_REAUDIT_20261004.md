# Tester G6 Re-audit — 2026-10-04

## Independence
- Tester branch: `tester/phase-1-g6-reaudit-20261004`
- Developer head audited: `15f14b590ffd3c2947102f2ae7f6ad32ff04e6b8`
- This branch is isolated from developer changes.

## Preliminary decision
**G6: FAIL / OPEN pending exact-head CI evidence.**

## Static checks
1. Explicit dividend coverage is now emitted by the production report.
2. Aggregation now fails closed when dividend coverage evidence is absent.
3. Aggregate workflow changes are included in automatic push/PR trigger paths.
4. Exact-head exhaustive production artifact is still required.
5. No Phase 2 advancement is authorized.

## Mandatory evidence still pending
- Complete 8-shard exact-head execution.
- Aggregate artifact tied to the exact developer SHA.
- Artifact checksum/provenance.
- Full option-file coverage and row accounting.
- Independent verification of Black-Scholes/IV/delta mathematics.
- Strict-prior r/q no-lookahead verification.
- Underlying exact timestamp alignment.
- Target-selection determinism.
- Cache/provenance and workflow reproducibility.
- Consistency with G5 waiver, G9 PASS, and G13/G14 BLOCKED state.

This report must be updated to a final PASS or FAIL after the exact-head aggregate artifact is available.
