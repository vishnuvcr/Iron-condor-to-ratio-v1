# Independent Tester Re-Audit — Phase 1 G5/G6 Corrections — 2026-10-04

## Scope
Independent audit of developer correction branches:
- G5: `phase-1-g5-e071-ci-provenance-hardening`, exact head `d4fb68219a0bcf6b4e4deb8b0fa7e5f611db8f9c`
- G6: `phase-1-g6-cache-provenance-hardening`, exact head `d154248b123c405882b8e172c10d154dd8fbdb65`
- control-plane wording and synchronized G9 PASS state

## Disposition

**Phase 1: FAIL / IN PROGRESS**

| Gate | Tester disposition |
|---|---|
| G5 | **FAIL / OPEN** |
| G6 | **FAIL / OPEN** |
| G9 | **PASS remains valid under Tester PR #32 methodology approval, but repository wording is internally inconsistent** |
| G13 | **BLOCKED** |
| G14 | **BLOCKED** |
| Phase 2 | **BLOCKED** |

No Phase 2 authorization is granted.

## G5 findings

### G5-1 — exact-head CI evidence still absent (BLOCKING)
The correction branch resolves to `d4fb68219a0bcf6b4e4deb8b0fa7e5f611db8f9c`. GitHub reports:
- combined commit statuses: zero statuses;
- workflow runs for the exact SHA: zero runs.

Therefore the correction has not produced independently observable exact-head CI evidence.

### G5-2 — automatic push trigger is still pointed at the pre-correction branch (BLOCKING CONTROL DEFECT)
The G5 workflow on the correction branch still declares the `push.branches` filter as:
`phase-1-g5-underlying-option-alignment`
rather than the correction branch `phase-1-g5-e071-ci-provenance-hardening`.

GitHub's Actions documentation states that push branch filters restrict execution to matching branches. Thus a push to the correction branch is not covered by this automatic trigger. Manual dispatch exists, but that does not repair the missing automatic exact-head evidence/control.

### G5-3 — artifact provenance hardening is technically present
The validator records `git rev-parse HEAD`; CI compares the recorded SHA with the actual checkout SHA; manual dispatch accepts an optional expected SHA and fails closed on mismatch. This correction addresses the prior provenance defect in implementation.

**G5 conclusion:** implementation correction is present, but gate evidence is still insufficient. G5 remains OPEN.

## G6 findings

### G6-1 — exact-head CI evidence absent (BLOCKING)
The correction branch resolves to `d154248b123c405882b8e172c10d154dd8fbdb65`. GitHub reports:
- combined commit statuses: zero statuses;
- workflow runs for the exact SHA: zero runs.

No exact-head acquisition artifact can therefore be independently accepted as CI evidence.

### G6-2 — cache is restored/saved but is not actually used to avoid acquisition (BLOCKING CONTROL DEFECT)
The workflow restores `.cache/g6_sources` and `data/raw/g6_sources`, and saves them after acquisition. However, `scripts/phase1_g6_source_acquisition.py` unconditionally calls `urlopen()` for every registered source on every execution and writes a fresh file.

The script does not inspect restored cache contents, does not verify cached source hashes before reuse, and does not skip network acquisition when a valid cached artifact exists. `.cache/g6_sources` is also not populated by the acquisition script itself.

Therefore the implemented cache is persistence plumbing, not a deterministic cache-hit data path. This does not satisfy the project control requiring important data to be kept/cached and used rather than downloaded every run.

### G6-3 — production Greek/IV evidence remains absent
The correction does not change the prior substantive boundary: it is still source acquisition/provenance only. Full date-aligned historical r/q inputs, production IV reconstruction, signed/absolute delta evidence, solver diagnostics, no-lookahead validation, and complete acceptance statistics remain outstanding.

**G6 conclusion:** G6 remains OPEN.

## G9 wording audit

Tester PR #32 remains the independent approval basis for G9 under the revised proxy-execution methodology. The accepted methodology is not historical bid/ask validation; it is explicit proxy execution with next eligible option-bar opens, atomic multi-leg handling, trigger re-arm, tick-floor slippage sensitivity, and date-effective costs.

However, the repository's `research/PHASE1_GATE_MATRIX.md` contains a direct internal contradiction: its canonical table says **G9 PASS**, while its subsequent "Current decision" / non-negotiable text still says G9 is blocked pending historical execution-quality data. README/current-status text says G9 PASS. The stale blocking language must be removed or explicitly marked historical so the canonical current state is unambiguous.

This is a control-plane documentation defect, not a reversal of Tester PR #32's G9 approval.

## Project control audit

The repository copy of `PROJECT_INSTRUCTIONS.md` inspected on the audited correction branch does **not** contain the newly stated rule that Developer responses must end with "Instructions to Tester" and Tester responses must end with "Instructions to Developer". The file currently contains the general tester-gate rule but not this new communication-control requirement.

The user-stated control is therefore **not independently verifiable in the audited repository state** and should be committed to the appropriate control branch/file before being treated as an implemented repository control.

## Required developer actions

1. Produce an observable successful exact-head G5 Actions run for `d4fb68219a0bcf6b4e4deb8b0fa7e5f611db8f9c`, with artifact/report SHA binding verified.
2. Correct G5 automatic push branch filtering so the correction branch (or an explicit controlled pattern covering it) is actually eligible for push-triggered CI; retain manual dispatch.
3. Produce an observable successful exact-head G6 Actions run for `d154248b123c405882b8e172c10d154dd8fbdb65`.
4. Make G6 cache functional: on a valid cache hit, verify and reuse the cached immutable source artifacts instead of unconditionally downloading them; fail closed on hash mismatch. Ensure cache keys and provenance remain deterministic.
5. Complete the substantive G6 production r/q and IV/Greek reconstruction requirements; do not treat source acquisition as G6 PASS.
6. Synchronize G9 wording so current canonical state consistently says **G9 PASS under the revised proxy methodology**, while preserving historical evidence separately.
7. Commit the Developer/Tester response-ending control into `PROJECT_INSTRUCTIONS.md` and synchronize status/error/conversation controls.
8. Keep G13, G14 and Phase 2 blocked pending independent tester re-audit.

## Independent tester conclusion

**G5: FAIL/OPEN. G6: FAIL/OPEN. G9: PASS remains valid, but current repository wording requires control-plane correction. G13/G14/Phase 2 remain BLOCKED.**
