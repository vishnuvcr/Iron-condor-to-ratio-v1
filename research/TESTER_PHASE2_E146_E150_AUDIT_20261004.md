# Independent Tester Audit — E146–E149 Final Phase 2 Check — 2026-10-04

## Verdict

**CONDITIONAL PASS FOR CONTINUED PHASE 2 DEVELOPMENT — PRODUCTION ACCEPTANCE DEFERRED**

Developer head audited:

`923c50a32af703b46158e1ab2a882dc2e47235d4`

The previous E146/E147 workflow findings are closed in source. The reconstructed historical monthly lot-size chronology is substantially improved and has boundary tests. However, the exact-head production workflow still has no observable GitHub Actions run, so no production result exists and no profitability claim can be accepted.

A further material E148 issue was found: the reconstruction script derives `expiry_close_ts` from the maximum raw timestamp observed on expiry day. Earlier Phase 1 evidence explicitly documents that raw source files can contain pre/post-window observations. Therefore the reconstructed expiry-close timestamp is not guaranteed to represent the historical F&O execution close. The expiry-close metadata must be derived from the dated session/F&O execution controls (or another authoritative expiry-close source), not simply the raw-file maximum timestamp.

## Findings

### E146 — CLOSED

The workflow now uses valid GitHub Actions expression syntax for checkout/ref selection and exact-head assertions.

### E147 — CLOSED

The five matrix scenarios are consistently named:

- 0 bps
- 5 bps
- 10 bps
- 20 bps
- 50 bps

The analysis stage downloads `phase2-backtest-*-bps` and explicitly asserts that all five scenario directories exist before analysis.

### E148 — PARTIALLY CLOSED

The reconstruction correctly:
- selects monthly expiries from the observed option dataset;
- encodes tested historical lot-size boundaries;
- retains source references and source-file hashes;
- produces deterministic contract IDs;
- validates required metadata;
- merges the reconstructed master into normalized bars;
- rejects unmatched contract metadata;
- enforces contract lifecycle intervals.

The boundary tests cover 75 → 50, 50 → 25, 25 → 75 and 75 → 65 transitions.

**Residual material issue:** `build_phase2_contract_master.py` sets `expiry_close_ts` to the latest raw observation timestamp on expiry day. Because the project's own Phase 1 audit records raw observations outside the F&O execution window, this can be later than the true strategy execution close. The production engine uses this field for expiry cut-off logic.

Required correction: derive expiry-close from the applicable date-specific F&O execution interval/session control, using the latest eligible observation within that interval, and retain the source/control provenance. If an authoritative exchange expiry-close timestamp is available, prefer it. Add a regression test proving post-session raw observations cannot move `expiry_close_ts` later.

### Contract lifecycle

The reconstruction's contract_start/end are observed-data lifecycle bounds rather than recovery of original exchange member contract-file bytes. This is appropriately disclosed and is acceptable as a deterministic reconstruction **provided expiry-close is corrected as above**.

### Cost/slippage

The frozen cost architecture and 0/5/10/20/50 bps adverse slippage model remain consistent with the previously audited design. The E141 unit conversion correction remains explicitly tested.

### State machine / chronology

The previously audited state machine remains coherent: completed-bar decisions, strict next-bar execution, atomic groups, explicit trigger crossings, re-arm semantics, and forced-close state transitions are present. No new mathematical contradiction was found in this pass.

### Exact-head evidence

GitHub reports zero workflow runs for exact head:

`923c50a32af703b46158e1ab2a882dc2e47235d4`

Therefore:
- no five-scenario production ledger is accepted;
- no statistical analysis is accepted;
- no prior artifact is relabelled as evidence for this head;
- no profitability conclusion is accepted.

## E150 — Expiry-close reconstruction can include post-session observations

**Severity:** MATERIAL PRE-PRODUCTION CHRONOLOGY DEFECT.

The contract-master reconstruction uses the maximum raw timestamp observed on expiry day as `expiry_close_ts`. Raw source observations are known to include timestamps outside the strategy's F&O execution window.

**Impact:** expiry-close metadata can be later than the actual F&O execution close, affecting forced-close timing and potentially terminal-position handling.

**Required resolution:** derive expiry-close from the date-specific F&O execution/session control interval or an authoritative exchange close source; add a regression test preventing post-session observations from changing expiry-close.

No production P&L has been generated from this defect.

## Tester → Developer instructions

Correct E150, add the regression test, regenerate the contract master, and then obtain a genuinely reproducible exact-head production Actions run. After the five scenario ledgers and statistical artifacts exist, hand them back for consolidated independent audit.

The owner-approved lenient gate policy remains in effect: this finding does not require abandoning Phase 2; it only prevents production-result acceptance until corrected.
