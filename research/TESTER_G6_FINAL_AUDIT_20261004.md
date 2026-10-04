# Independent Tester Report — G6 Final Audit — 2026-10-04

## Verdict
**G6 FAIL / OPEN — evidence-completeness defects remain.**

The frozen developer CI run `37191768801` at exact checkout `1a9eab7389b972c05362271ee9fb23092aa7354d` completed its exhaustive 32-shard production scan and aggregate with no CI job failures. The aggregate artifact is SHA-256 `80512999956437e2acfdbcea2d4a6a6ebfb659267691ef033dcf7b19f55c3ae6`.

The independent tester verified:
- 32 shard artifacts exist, indexed 0–31, all tied to the exact frozen developer SHA.
- Aggregate status is `PRODUCTION_SCAN_COMPLETE`.
- Aggregate declares `shards=32` and `complete_file_partition=true`.
- 267/267 option files were processed.
- Strict-prior r coverage is 1262/1262 underlying days; q coverage is 1262/1262.
- IV converged for 102,759,697 observations; non-convergence is zero.
- Signed-delta and absolute-delta histogram totals each equal the IV-converged count.
- Target-selection counts reconcile exactly to `target_selected_records` (8,016,434).
- Every target's reported maximum delta-selection error is <= 0.05.
- Production checksums and exact checkout SHA are present.
- The production implementation uses strict-prior r/q selection, exact timestamp underlying joins, no interpolation/forward-fill, deterministic Brent solving, and the documented target tie-break.

## Blocking defects
### D1 — Required IV iteration/residual evidence is not emitted
The G6 specification requires recording convergence flag, iterations, residual, lower/upper boundary, boundary rejection, and failure reason. The production scanner computes `iters` and `residual` internally but discards them after the solve. The aggregate report therefore contains only convergence/failure counts and solver configuration, not iteration/residual distributions or summary evidence.

### D2 — Explicit expiry/date coverage evidence is absent
The G6 acceptance criteria require expiry/date coverage. The scanner derives `expiry_close` and uses time-to-expiry, but the report does not explicitly quantify valid/invalid expiry observations, expiry coverage, or expiry-date coverage by the study window. `invalid_model_input` is not a sufficient substitute because it conflates expiry failures with underlying/r/q/model-input failures.

### D3 — Explicit future-input audit is absent from the evidence artifact
The implementation's strict-prior join is conservative and the code audit found no same-day/future join path. However, the acceptance specification requires zero future-dated inputs as a G6 acceptance criterion; the aggregate does not emit an explicit future-input count/check result. This should be surfaced as machine-readable evidence rather than inferred solely from code review.

## Gate disposition
G6 is **not approved**. The mathematical/data-path checks above are encouraging, but the mandatory evidence package is incomplete. G13/G14 and Phase 2 remain blocked.

## Required developer remediation
1. Preserve and summarize IV iteration counts and residuals for converged solves; report deterministic boundary/bracket diagnostics separately.
2. Add explicit expiry validity/coverage counters and study-window expiry-date coverage.
3. Add explicit future-input/no-lookahead counters/checks for r and q at valuation timestamps.
4. Extend aggregate validation to require these fields consistently across all 32 shards.
5. Re-run the complete exact-head G6 workflow after the code change.
6. Create a fresh isolated tester branch from the new developer head and repeat the independent audit. Do not reuse this FAIL report as approval.

This report does not authorize G7 or Phase 2.
