# Phase 1 Gate Matrix

Updated: 2026-10-03 — E053 synchronized current-state control

This matrix is the Phase 1 acceptance checklist. A source-validation PASS does not equal production-data acceptance. The table below is the **current canonical state**. Historical sections later in this file are append-only evidence and must not override this table.

| Gate | Requirement | Current state | Evidence / blocker |
|---|---|---|---|
| G1 | Immutable primary dataset / provenance | PASS | HF revision 0f4800e; pinned manifest; prior structural evidence retained |
| G2 | Structural schema validation | PASS | 108,625,497 raw rows; 0 hard failures |
| G3 | Duplicate handling | PASS | 30,363,281 exact duplicates; 0 conflicting duplicate groups; deterministic deduplication |
| G4 | Timestamp/session quality | **PASS — independently verified** | Exact tip 378a130b6d450b288be140655f9b0b75aad840b3; Run 37135122966; artifact 11278418088; 1,262 observed dates; 13 controls; 10 special sessions; 1 data-gap exclusion; 0 unreconciled; 0 missing manifest-session dates; four E046 regressions passed |
| G5 | Underlying/option alignment | PRELIMINARY / OPEN | 99.2953% diagnostic timestamp alignment is not production acceptance; decision-time alignment and missingness controls remain open |
| G6 | Production historical Greeks / IV | OPEN | Date-aligned r/q and production IV/Greek validation remain incomplete |
| G7 | Target-delta availability | OPEN | Frozen delta tolerance plus quote/volume/OI availability must be measured on production data |
| G8 | Historical contract metadata | OPEN | Effective-date NIFTY lot/expiry/contract metadata reconciliation remains incomplete |
| G9 | Historical bid/ask / execution quality | **BLOCKED** | Primary HF source has no documented historical bid/ask; NSE historical F&O order/trade data is the preferred acquisition/reconstruction route and is not yet acquired/validated |
| G10 | Date-specific transaction costs | OPEN | Complete date-specific Paytm Money/statutory/exchange cost schedule remains incomplete |
| G11 | Market-context datasets | OPEN | Required aligned context datasets remain incomplete |
| G12 | Repaired CI execution | **PASS — independently verified** | Exact tip 378a130b6d450b288be140655f9b0b75aad840b3; Run 37135122966; job 111238039571; artifact 11278418088; digest de60c50a047357d7f89d5602ea42fd832158855779e34169fec2b9beeb02159; all substantive workflow steps succeeded |
| G13 | Independent tester approval | **BLOCKED** | Tester PR #25 closed E055 PASS, while G13 remains BLOCKED because G5–G11 are not yet production-accepted |
| G14 | Phase 2 authorization | **BLOCKED** | Cannot begin until G1–G13 are accepted and tester explicitly authorizes Phase 2 |

## Current decision

**Phase 1 remains IN PROGRESS / NOT APPROVED. Phase 2 remains BLOCKED.**

The independent tester has closed the specific E046 technical defect and independently verified G4/G12. This does **not** constitute Phase 1 approval because G5–G11 remain incomplete, with G9 specifically blocked pending historical execution-quality data acquisition/validation.

## Non-negotiable acceptance rules

1. No close-price substitution for the frozen historical bid/ask midpoint rule without an explicit pre-registered methodology change.
2. No contemporary risk-free rate or current cost schedule may be applied retrospectively.
3. Historical lot size, expiry day and tick/contract rules must use effective-date metadata.
4. No Phase 2 engine, optimization, profitability result or strategy conclusion may be accepted before the independent tester PASS.
5. Any future methodology change must update RESEARCH_PLAN.md only if the planned research itself changes; ordinary execution errors belong in ERROR_LOG.md.
6. Historical evidence below is append-only and must not be interpreted as the current gate state when it conflicts with the canonical table above.

## E053 resolution

The previous top-level table incorrectly exposed superseded E044/E045/E046 states. Those historical entries are retained below for traceability, while this top table is now synchronized to the independently verified Run #55 result.

## Historical evidence

- Evidence update: `research/PHASE1_G5_G11_SOURCE_AUDIT_20261003.md` records the 2026-10-03 official-source audit. G8 contract-rule evidence now includes the 2025 lot-size and expiry transitions; G9's official NSE Historical Order & Trade route is better specified. These additions do not close G5–G11.


## 2026-10-03 — E058 / Tester PR #27 G9 free-data salvage continuation
The tester handoff PR #27 is now the controlling next-step evidence for G9. Free-data candidates are being investigated in the prescribed order; no candidate is production-accepted yet. G9 remains **BLOCKED**. The local Hugging Face download attempt failed due to DNS/network isolation and was logged as E058; no inferred quote data were created. Phase 2 remains blocked.

## 2026-10-03 — explicit execution-proxy methodology change
The developer has formally proposed replacing the mandatory historical bid/ask requirement for the primary backtest with the frozen proxy-execution model in `research/PHASE1_EXECUTION_PROXY_SPEC.md`.

**Current gate state remains unchanged pending tester approval:**
- G9: **BLOCKED — methodology change pending independent tester review**
- G13: **BLOCKED**
- G14: **BLOCKED**
- Phase 2: **BLOCKED**

The proxy model does not relabel OHLC/LTP as bid/ask. It uses completed-bar decisions, next eligible option-bar open fills, adverse 0/5/10/20/50-bps per-leg slippage with an effective-date tick floor, and date-effective transaction costs. This methodology must be independently reviewed before Phase 2 can be authorized.
