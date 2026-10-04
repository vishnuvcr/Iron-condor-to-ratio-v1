# Independent Tester Audit — Phase 2 E151 Final Audit v2
Date: 2026-10-04
Developer head: `66e2a06850eb75f4b9eebca4bf994ba592a59ff7`

## Verdict
**FAIL / PRODUCTION GATE BLOCKED.**

E151's intended interval-membership logic is conceptually correct, and the horizon control is present. However, the implementation contains a material timezone-type defect that invalidates both the contract-master expiry-close predicate and the E150/E151 impact scan.

## Critical finding E152 — aware/naive expiry comparison

`timestamp` is normalized as timezone-aware Asia/Kolkata. In both the builder and impact scan, `expiry` is produced with `pd.to_datetime(...).dt.normalize()`, which is timezone-naive.

The predicate effectively performs:
`timestamp.normalize() == expiry`
where the left side is Asia/Kolkata-aware and the right side is naive. These values are not equal.

Consequences:
- `expiry_timestamp_is_executable()` can reject valid expiry-day observations.
- `timestamp_in_execution_interval()` can reject valid expiry-day observations.
- `update_expiry_close_ts()` may fail to populate `expiry_close_ts` for otherwise valid data.
- the corrected impact scan's `executable()` can classify valid observations as non-executable.
- a reported zero affected-group result cannot be interpreted as evidence of zero materiality.

This is a **material chronology/data-validity defect**, not a cosmetic issue.

## Impact-scan secondary defect

The impact scan only records a group as affected when both `old_close` and `corrected_close` are non-null and differ. If old semantics produce a close from a gap/post-session observation but corrected semantics produce no qualifying observation, the group is omitted rather than reported as affected.

Required affected condition should include at least:
- old close differs from corrected close; OR
- old close exists while corrected close is missing; OR
- corrected close exists while old close is missing.

Such groups must be fail-closed and included in the impact report.

## E151 interval-membership assessment

The intended `any(start <= timestamp <= end)` interval membership is correct for disjoint special sessions once timestamp timezone normalization is fixed.

The added gap regression is directionally appropriate, but the test itself should be independently executed after the timezone representation is made consistent. As currently written, the same aware/naive mismatch can make the valid timestamp assertion fail.

## Horizon assessment

The contract-master builder now derives the study horizon from `phase1_session_rules.json` and rejects dates beyond it. The impact scan similarly bounds its source rows. This is structurally appropriate.

However, horizon correctness cannot compensate for the invalid timezone predicate.

## E150/E151 materiality

**UNRESOLVED.** No zero-impact conclusion is accepted from this implementation. Affected expiry groups must be recomputed after timezone normalization and after the missing-corrected-close case is treated as affected.

## E146–E150
- E146: closed at source-inspection level.
- E147: closed at source-inspection level.
- E148: candidate deterministic reconstruction remains subject to production evidence.
- E149: exact-head Actions execution remains unobservable.
- E150: ordinary post-session boundary logic is conceptually corrected, but final materiality remains unresolved.

## Production workflow gate

The workflow correctly attempts to fail closed on a nonzero `affected_contract_groups` result before production normalization/backtesting. However, because the impact scan itself is defective, the workflow cannot currently establish that zero is meaningful.

Also, the workflow invokes the E150/E151 impact scan twice. This duplication is not itself a scientific defect, but should be removed or explicitly justified to avoid inconsistent artifacts and unnecessary work.

## Required remediation
1. Normalize expiry dates to Asia/Kolkata before every expiry-date comparison, or compare local calendar dates explicitly.
2. Add tests proving an aware 15:30 timestamp is executable for a naive input expiry after normalization, plus the 15:31 rejection.
3. Fix the impact scan to classify old-close-present/corrected-close-missing groups as affected.
4. Regenerate the impact scan over the pinned source.
5. Independently inspect the resulting affected-group count and examples.
6. If affected groups > 0, rerun affected production scenarios.
7. If zero, retain the machine-readable zero-impact artifact and independently verify its exact source hashes and coverage.
8. Obtain exact-head CI evidence where possible; no existing artifact may be relabelled.

## Tester conclusion
**Do not grant E150 non-material status, Phase 2 production acceptance, Phase 3 statistical execution, or a profitability/trading-strategy conclusion at this gate.**

### Tester → Developer instruction
Correct E152 and the impact-scan missing-close logic, rerun the chronology tests and impact scan, then hand the exact new head to a fresh tester gate. Preserve the fail-closed rule.

### Developer → Tester instruction for the next gate
Independently verify timezone-consistent expiry predicates, all impact-scan categories including corrected-close-missing cases, source coverage/hashes, exact SHA, and any resulting affected-group reruns before accepting E150.