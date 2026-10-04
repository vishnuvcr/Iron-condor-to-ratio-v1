# Independent Tester Handover Report — 2026-10-04

## Handover
Developer branch: `phase-1-g6-production-greeks-20261004`  
Developer head audited: `2dd4506e5173052c58573a94f9a3368f1a7d3190`  
Tester branch: `tester/phase-1-g6-handover-20261004`

This branch was created automatically from the exact developer head. The tester audit is isolated from developer implementation work.

## Determination

**PHASE 1: FAIL / IN PROGRESS**  
**G5: FAIL / WAIVED FOR CONTINUED RESEARCH**  
**G6: FAIL / OPEN**  
**G9: PASS under the independently approved bid/ask-free proxy methodology**  
**G13/G14: BLOCKED**  
**PHASE 2: BLOCKED**

No backtest, optimization, profitability conclusion, or Phase 2 authorization is permitted.

## Independent checks performed

### 1. Control-state consistency — PASS
The canonical gate matrix, research plan/status, G6 specification, and error log consistently state that G6 is open and Phase 2 is blocked. G5 is not relabelled as a pass.

### 2. G6 fail-closed production scanner — PASS
The production scanner requires both `risk_free.csv` and `dividend_yield.csv`, validates schemas/dates/duplicates, requires strict-prior coverage, uses exact underlying timestamp joins, and fails closed when mandatory inputs are absent.

The Black-Scholes implementation records solver outcomes, signed and absolute delta distributions, target-delta availability, checksums, and exact checkout SHA.

### 3. Strict-prior implementation — PASS WITH DOCUMENTATION LIMIT
The implementation uses `merge_asof(..., direction="backward", allow_exact_matches=False)`, which correctly rejects same-day equality at the date-key level.

However, the required G6 specification distinguishes **observation/availability date** from observation date. The current `risk_free.csv` schema contains only `date,yield_pct`, and the acquisition script does not preserve a publication/availability date. Therefore the tester cannot certify the stronger real-world no-lookahead requirement until the source-date semantics are explicitly established and preserved.

### 4. RBI primary acquisition — FAIL / BLOCKER
The documented final primary acquisition returned zero parseable 91-Day Treasury Bill (Primary) Yield rows. This correctly leaves G6 open. No primary-data acceptance is claimed.

### 5. Cache/reuse requirement — FAIL / REGRESSION
The workflow restores `data/raw/g6_sources` and `data/processed/g6`, but `scripts/acquire_g6_rbi_risk_free.py` does not inspect or reuse retained source pages before submitting the complete WSS ID scan. The current script defines the retained `RAW` directory and writes provenance files, but `fetch_one()` always performs network requests.

This contradicts the repository requirement that important data be cached/kept and reused rather than downloaded every workflow run, and it conflicts with the earlier E077/E079 correction history claiming cache reuse and immutable byte validation.

**Required correction:** implement explicit cache-hit handling for each retained source page, with expected SHA-256 validation; fail closed on missing/mismatched expected provenance rather than silently trusting a non-empty file. Cache reuse must be tested in CI.

### 6. Tester-branch CI isolation — observation
The G6 workflow's automatic push trigger is restricted to the developer branch `phase-1-g6-production-greeks-20261004`. It does not automatically execute on this tester branch. That is acceptable only if the tester performs independent static/repository verification and does not represent the branch as having fresh CI evidence. Any CI evidence used for gate approval must be tied to the exact developer checkout SHA.

## Required developer actions before re-handover

1. Correct the G6 RBI acquisition cache/reuse regression without relaxing provenance checks.
2. Preserve and validate immutable expected SHA-256 values for cached RBI source pages.
3. Define/preserve the availability-date semantics needed by the G6 strict-prior rule, or explicitly prove that the retained RBI observation date is the valid availability key for this source.
4. Add deterministic regression tests for cache hit, cache SHA mismatch, and no-lookahead date semantics.
5. Run the G6 workflow at the exact corrected developer head and retain the complete artifact.
6. Re-handover automatically to a **new isolated tester branch** from that exact developer SHA.
7. Do not merge this tester branch as a substitute for tester approval; this report is a FAIL / request-for-correction.

## Gate consequence

G6 remains **FAIL / OPEN**. G13/G14 and Phase 2 remain **BLOCKED**. G5's independently established exact-timestamp limitation remains disclosed and waived only for continued exploratory research; it is not a PASS.

## Tester instruction to developer

Rectify the identified G6 cache/provenance and no-lookahead semantics defects, update the error log and status records, then automatically create a fresh isolated tester branch from the corrected developer head and submit the new evidence for re-audit. Do not advance the research phase before that tester report.
