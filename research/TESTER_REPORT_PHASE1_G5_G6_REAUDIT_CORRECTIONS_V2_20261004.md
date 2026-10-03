# Independent Tester Report — G5/G6 Re-audit Corrections v2 — 2026-10-04

## Disposition

**Phase 1: FAIL / IN PROGRESS**

- G5: **OPEN — exact-head Actions evidence not independently established**
- G6: **OPEN — cache reuse implementation improved but provenance validation remains insufficient; substantive production evidence absent**
- G9: **PASS remains valid under Tester PR #32**
- G13: **BLOCKED**
- G14: **BLOCKED**
- Phase 2: **BLOCKED**

## G5

The correction branch workflow now correctly includes:
- `phase-1-g5-g6-reaudit-corrections-20261004` in the automatic push branch filter;
- manual dispatch defaulting to that correction branch;
- optional exact expected-SHA checking;
- artifact checkout-SHA verification.

These are accepted as implementation corrections.

However, independent tester evidence still does not include an observable successful Actions run/artifact tied to the correction branch's actual tip. The GitHub connector available to the tester does not expose a branch-tip SHA directly, and no independently verifiable exact-head run was found. Therefore G5 cannot be promoted to PASS.

**G5 remains OPEN.**

## G6

### Positive correction

The acquisition script now has a local reuse path:

`CACHE_HIT_LOCAL` is emitted when the retained destination exists, is a file, and is non-empty.

The workflow also includes the correction branch in its automatic push filter, has manual dispatch, performs checkout-SHA checking, and restores/saves the source cache.

### G6-1 — cached-file provenance is not actually validated

The function named `acquire_one` claims:

> "Reuse an existing validated byte-identical source"

but its condition only checks:

- file exists;
- regular file;
- size > 0.

It then reads the bytes and computes a SHA-256, but **does not compare that hash against an expected immutable source hash from the manifest or another frozen provenance record** before declaring `CACHE_HIT_LOCAL`.

Therefore a corrupted, stale, wrong-content, or manually replaced non-empty file can be accepted as a cache hit. The computed hash is merely recorded after acceptance.

This is not sufficient for the project's reproducibility requirement. Cache reuse must be conditional on validation against an expected immutable digest/provenance identity; otherwise the cache can bypass the source acquisition integrity check.

### G6-2 — exact-head CI evidence still not independently established

No independently observable successful Actions run/artifact tied to the correction branch's actual tip has been established by the tester.

### G6-3 — substantive G6 evidence remains incomplete

The implementation remains source acquisition/provenance only. It does not yet provide the complete study-period date-aligned:

- risk-free rate series;
- dividend/yield series;
- no-lookahead production validation;
- Black-Scholes IV reconstruction;
- signed/absolute delta reconstruction;
- solver residual/iteration/boundary/failure distributions;
- target-delta availability evidence;
- production checksum/evidence package.

Therefore G6 cannot pass even if the acquisition workflow becomes green.

**G6 remains OPEN.**

## G9

Tester PR #32 remains the independent approval basis. G9 remains **PASS under the revised proxy-execution methodology**. The current correction branch's G9 synchronization is consistent with that approval.

No G9 regression or withdrawal is warranted.

## Project controls

`PROJECT_INSTRUCTIONS.md` now contains the Developer/Tester response-end controls:

- Developer → Instructions to Tester
- Tester → Instructions to Developer
- communication text is explicitly non-authorizing.

This control is now independently verified on the correction branch.

## Required developer actions

1. Produce observable successful exact-head G5 CI evidence tied to the actual correction-branch tip, including artifact SHA binding.
2. Produce observable successful exact-head G6 CI evidence tied to the actual correction-branch tip.
3. Make G6 cache reuse cryptographically/provenance safe: a cache hit must verify the cached bytes against an expected immutable source digest/version before `CACHE_HIT_LOCAL` is accepted; mismatch must fail closed and reacquire only through the pinned source path.
4. Complete the substantive G6 date-aligned r/q and production IV/Greek evidence.
5. Preserve G9 PASS wording and its Tester PR #32 provenance.
6. Keep G13/G14/Phase 2 blocked until independent tester approval.

## Final tester decision

**G5 OPEN. G6 OPEN. G9 PASS. G13/G14/Phase 2 BLOCKED.**

This report does not authorize any Phase 2 implementation or backtest.
