# Independent Tester Report — Phase 1 G5/G6 Audit
Updated: 2026-10-04

## Role and scope

Role: **Tester only**.

This report independently audits developer PR #34 (G5) and PR #35 (G6) without advancing either gate or authorizing Phase 2.

Audited developer heads:
- PR #34 G5: `3225d29902a20c958bf8c9803479e8fbe7601dbf`
- PR #35 G6: `d52aa06c9d3efee71cae513e8aacf09955dbdb53`

## Repository control state checked

The repository control documents were checked before audit, including README.md, RESEARCH_STATUS.md, ERROR_LOG.md, CONVERSATION_LOG.md, RESEARCH_PLAN.md, and research/PHASE1_GATE_MATRIX.md where available on the audited developer branch.

Canonical state remains:
- G1 PASS
- G2 PASS
- G3 PASS
- G4 PASS independently
- G5 OPEN
- G6 OPEN
- G7 OPEN
- G8 OPEN
- G9 PASS under the independently approved proxy-execution methodology
- G10 OPEN
- G11 OPEN
- G12 PASS independently
- G13 BLOCKED
- G14 BLOCKED
- Phase 2 BLOCKED

No backtest or profitability authorization is granted by this report.

## G5 audit

### Finding G5-1 — exact-head CI evidence absent

The developer PR identifies exact head `3225d29902a20c958bf8c9803479e8fbe7601dbf` as the current G5 head.

Independent GitHub status inspection for that SHA returned:
- state: pending
- total statuses: 0

Independent workflow-run inspection for `phase1-g5-alignment.yml` at that exact SHA returned:
- workflow runs: 0

Therefore there is no independently observable Actions execution proving that the G5 validator actually ran against the exact audited developer head.

**Disposition:** BLOCKING. G5 cannot be PASSed.

### Finding G5-2 — manual-dispatch provenance is not self-authenticating

The G5 workflow accepts a free-form `research_ref` input for manual execution and checks only that the validator file exists after checkout. The workflow prints the resulting Git SHA, but the produced JSON evidence report does not itself retain the checkout SHA.

This is not evidence of an actual wrong checkout, but it leaves a reproducibility/control gap for manual evidence. A production acceptance artifact should bind the report to the exact commit SHA, or the workflow should assert the intended SHA explicitly.

**Disposition:** CONTROL DEFECT. Must be corrected before manual-dispatch evidence can be treated as equivalent exact-head evidence.

### G5 implementation review

The validator correctly:
- parses timestamps with explicit UTC conversion;
- retains Asia/Kolkata session classification;
- rejects duplicate NIFTY timestamps;
- rejects unparseable timestamps;
- separates session eligibility from timestamp alignment;
- requires exact timestamp membership in the NIFTY grid;
- performs no interpolation or forward-fill;
- reports expiry/day coverage;
- fails closed when the aggregate alignment condition is not satisfied.

No additional mathematical defect was identified in the inspected G5 implementation that would justify a separate rejection at this stage.

### G5 disposition

**FAIL / OPEN — not production accepted.**

Reason: the required exact-head execution evidence is absent, and the manual-evidence provenance control should be hardened.

## G6 audit

### Finding G6-1 — source acquisition is not G6 production evidence

The G6 specification correctly states that source acquisition alone is insufficient. The submitted workflow only downloads/hashes the registered source pages and explicitly does not claim G6 PASS.

The current implementation does not provide:
- a complete date-aligned risk-free series for the full study period;
- a complete historical dividend-yield series for the full study period;
- production option-by-option IV reconstruction;
- frozen Brent-Dekker numerical execution over the production dataset;
- solver success/failure/boundary counts;
- residual and iteration distributions;
- signed/absolute delta distributions;
- failure breakdown by date/expiry/reason;
- no-look-ahead validation over the complete production dataset;
- a reproducibility checksum for the resulting production Greek dataset.

**Disposition:** BLOCKING. G6 remains OPEN.

### Finding G6-2 — workflow caching requirement not implemented

The G6 source-acquisition workflow has no cache restore/save mechanism. The project-level research controls require important data to be cached/retained and reused rather than downloaded on every workflow execution.

Because the workflow is only a preliminary acquisition/provenance step, this does not change the already-open G6 gate, but it is a workflow-control defect that should be corrected before repeated production acquisition.

**Disposition:** CONTROL DEFECT.

### G6 implementation review

The no-look-ahead rule in the specification is appropriately conservative: source observations must precede the trading date, and missing historical inputs are invalid rather than forward-filled.

The acquisition script correctly records acquisition status, bytes and SHA-256 for successfully fetched source pages and retains failure diagnostics. It does not overclaim production acceptance.

However, registering a small number of RBI WSS pages and a dynamic NSE reports page is not equivalent to assembling a complete historical time series. That distinction is correctly recognized by the developer and remains a substantive open gate.

### G6 disposition

**FAIL / OPEN — not production accepted.**

## Phase 1 authorization decision

**G13: BLOCKED.**

G5 and G6 are not accepted. G7, G8, G10 and G11 are also not production-accepted.

**G14: BLOCKED.**

**Phase 2: BLOCKED.**

No Phase 2 engine execution, optimization, profitability result, trading-strategy conclusion, or performance inference is authorized by this tester report.

## Required developer actions before re-audit

1. Obtain an independently observable G5 Actions run whose checked-out SHA equals the exact developer head being submitted for review.
2. Bind G5 evidence artifacts to the checkout commit SHA, especially for manual dispatch.
3. Re-submit the exact G5 head and its retained artifact for independent tester review.
4. Build the complete date-aligned historical risk-free and dividend-yield inputs required by G6.
5. Implement and execute the production IV/Greek reconstruction under the frozen Phase 0 numerical contract.
6. Retain complete G6 diagnostics and a deterministic production-dataset checksum.
7. Add cache restore/save to the G6 acquisition workflow before treating repeated acquisition as production workflow evidence.
8. Do not begin Phase 2 until all Phase 1 gates are independently accepted and G14 is explicitly authorized by the tester.

## Overall tester result

**PHASE 1: FAIL / IN PROGRESS**

The repository demonstrates substantial control hardening and correctly keeps Phase 2 blocked. The present submissions do not provide sufficient evidence to close G5 or G6, and no authorization to proceed to Phase 2 is given.
