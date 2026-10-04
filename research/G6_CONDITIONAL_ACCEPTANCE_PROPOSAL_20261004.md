# G6 Conditional Acceptance Proposal — 2026-10-04

## Purpose

This proposal asks the independent tester to determine whether the existing completed G6 production scan may be accepted as a CONDITIONAL PASS without rerunning the full 32-shard numerical scan.

This is not Developer approval and does not change the canonical gate state until the independent tester issues an explicit verdict.

## Existing computational evidence

- 32 exhaustive shards completed successfully.
- 267/267 option files were covered.
- strict-prior r coverage: 1262/1262.
- strict-prior q coverage: 1262/1262.
- IV converged: 102,759,697 records.
- IV non-convergence: 0.
- target-selected records: 8,016,434.
- maximum target-delta error: <= 0.05.
- shard/aggregate reconciliation passed.
- aggregate artifact SHA-256: 80512999956437e2acfdbcea2d4a6a6ebfb659267691ef033dcf7b19f55c3ae6.

The tester PR #49 did not identify a mathematical contradiction in these results. It identified evidence-completeness deficiencies.

## Outstanding evidence deficiencies

### D1 — IV convergence evidence retention

The production computation did not retain machine-readable per-record iteration/residual evidence required by the strict G6 evidence contract.

### D2 — Explicit expiry/date coverage

Expiry validity was used internally but the aggregate did not expose sufficiently specific expiry/date coverage counters. The broad invalid-model-input category was insufficient for independent diagnosis.

### D3 — Explicit no-lookahead evidence

The implementation used strict-prior selection, but the aggregate did not retain explicit machine-readable same-day/future-input audit counters.

## Proposed classification

If the tester agrees:

- Numerical computation: ACCEPTED
- Production result: CONDITIONALLY ACCEPTED
- G6 formal status: CONDITIONAL PASS
- D1-D3: documented evidence limitations
- No claim is made that D1-D3 were satisfied by the old artifact.
- The corrected evidence implementation remains the intended production evidence implementation for future reruns.

## Conditions for proceeding

1. D1-D3 remain explicit limitations in the final manuscript.
2. No claim is made that the old artifact contained evidence it did not contain.
3. The corrected evidence implementation remains in the repository.
4. A later reproducibility release should rerun the corrected G6 evidence path when CI execution is available.
5. G7 and later gates must independently validate their own evidence; this conditional acceptance does not waive unrelated gates.
6. G13 cannot be declared final PASS until the tester has independently accepted all required Phase 1 gates.

## Tester decision required

The tester must issue exactly one of:

- PASS — conditional acceptance is acceptable and G6 may proceed under the documented limitations.
- FAIL — missing evidence is scientifically material and a corrected fresh G6 run is mandatory.
- CONDITIONAL PASS WITH CONDITIONS — proceed only with additional explicit restrictions.

This proposal itself is not approval.
