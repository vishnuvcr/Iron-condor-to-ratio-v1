# Phase 1 Gate Matrix

Updated: 2026-10-03 — E053 synchronized current-state control

This matrix is the Phase 1 acceptance checklist. A source-validation PASS does not equal production-data acceptance. The table below is the **current canonical state**. Historical sections later in this file are append-only evidence and must not override this table.

| Gate | Requirement | Current state | Evidence / blocker |
|---|---|---|---|
| G1 | Immutable primary dataset / provenance | PASS | HF revision 0f4800e; pinned manifest; prior structural evidence retained |
| G2 | Structural schema validation | PASS | 108,625,497 raw rows; 0 hard failures |
| G3 | Duplicate handling | PASS | 30,363,281 exact duplicates; 0 conflicting duplicate groups; deterministic deduplication |
| G4 | Timestamp/session quality | **PASS — independently verified** | Exact tip 378a130b6d450b288be140655f9b0b75aad840b3; Run 37135122966; artifact 11278418088; 1,262 observed dates; 13 controls; 10 special sessions; 1 data-gap exclusion; 0 unreconciled; 0 missing manifest-session dates; four E046 regressions passed |
| G5 | Underlying/option alignment | **OPEN — exact-head CI pending** | Dedicated validator now separates session eligibility from exact NIFTY timestamp alignment and reports expiry/day coverage; no interpolation/forward-fill. Independent tester approval still required |
| G6 | Production historical Greeks / IV | OPEN | Date-aligned r/q and production IV/Greek validation remain incomplete |
| G7 | Target-delta availability | OPEN | Frozen delta tolerance plus quote/volume/OI availability must be measured on production data |
| G8 | Historical contract metadata | OPEN | Effective-date NIFTY lot/expiry/contract metadata reconciliation remains incomplete |
| G9 | Historical bid/ask / execution quality | **PASS — revised proxy methodology independently approved** | Tester PR #32 independently approved the bid/ask-free proxy at developer head 8b99cb3b2b537c5b085c09729c27bb3957285ae8; E065/E066 PASS. Historical bid/ask is not mandatory for the primary backtest. OHLC/LTP is never relabeled as bid/ask. Accepted proxy: completed-bar decision, first eligible next-bar open, atomic multi-leg failure, trigger consumption/re-arm, 0/5/10/20/50-bps adverse slippage with historical tick floor, date-effective costs. |
| G10 | Date-specific transaction costs | OPEN | Complete date-specific Paytm Money/statutory/exchange cost schedule remains incomplete |
| G11 | Market-context datasets | OPEN | Required aligned context datasets remain incomplete |
| G12 | Repaired CI execution | **PASS — independently verified** | Exact tip 378a130b6d450b288be140655f9b0b75aad840b3; Run 37135122966; job 111238039571; artifact 11278418088; digest de60c50a047357d7f89d5602ea42fd832158855779e34169fec2b9beeb02159; all substantive workflow steps succeeded |
| G13 | Independent tester approval | **BLOCKED** | G9 is now independently PASS via Tester PR #32, but G5/G6/G7/G8/G10/G11 remain incomplete. |
| G14 | Phase 2 authorization | **BLOCKED** | Cannot begin until G1–G13 are accepted and tester explicitly authorizes Phase 2 |

## Current decision

**Phase 1 remains IN PROGRESS / NOT APPROVED. Phase 2 remains BLOCKED.**

The independent tester has closed the specific E046 technical defect and independently verified G4/G12. G9 is also independently PASS under the revised bid/ask-free proxy methodology. This does **not** constitute Phase 1 approval because G5, G6, G7, G8, G10 and G11 remain incomplete.

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
- G9: **PASS — revised proxy methodology independently approved by Tester PR #32**
- G13: **BLOCKED**
- G14: **BLOCKED**
- Phase 2: **BLOCKED**

The proxy model does not relabel OHLC/LTP as bid/ask. It uses completed-bar decisions, next eligible option-bar open fills, adverse 0/5/10/20/50-bps per-leg slippage with an effective-date tick floor, and date-effective transaction costs. This methodology must be independently reviewed before Phase 2 can be authorized.

## 2026-10-03 — E065/E066 correction pending re-audit
Tester PR #30 identified two defects in the proposed bid/ask-free methodology. The developer correction addresses both without changing the 0/5/10/20/50-bps sensitivity schedule: E065 is resolved in the specification by atomic multi-leg fail-closed execution and explicit trigger/state re-arm rules; E066 is resolved by rejecting non-positive adjusted fills rather than clipping sells to zero. These are **developer-side corrections only**. G9 remains **BLOCKED pending independent tester approval** of the corrected exact head; G13/G14 and Phase 2 remain blocked.

## 2026-10-03 — G9 PASS under revised execution methodology
Tester PR #32 independently re-audited developer PR #31 exact head `8b99cb3b2b537c5b085c09729c27bb3957285ae8`. E065 and E066 are PASS and G9 is PASS under the revised bid/ask-free proxy methodology. This does not authorize Phase 2. G13/G14 remain blocked by G5/G6/G7/G8/G10/G11.
