# Iron Condor to Ratio v1

Research project to reproduce and independently backtest the YouTube strategy “What If the Iron Condor Starts Trending? Ratio Spread Strategy”.

## Current role
Developer (remediation branch). Independent tester PR #49 failed G6 evidence completeness; developer remediation is isolated here and requires a fresh tester handoff.
## Current phase
**Phase 1 — data acquisition and validation: IN PROGRESS. Phase 0 is APPROVED.**

## Gate
Phase 1 is **IN PROGRESS / NOT APPROVED**. G6 exact-head CI completed on the prior developer head, but tester PR #49 returned **G6 FAIL / OPEN** for missing IV iteration/residual, expiry/date coverage, and explicit no-lookahead evidence. G13/G14 and Phase 2 remain BLOCKED.

### Latest independently verified evidence
- Developer exact tip audited: `378a130b6d450b288be140655f9b0b75aad840b3`
- GitHub Actions run #55: `37135122966`
- Job: `111238039571`
- Artifact: `11278418088`
- Artifact SHA-256: `de60c50a047357d7f89d5602ea42fd832158855779e34169fec2b9beeb02159`
- G4: **PASS — independently verified**
- G12: **PASS — independently verified**
- G9: **PASS — independently approved under revised proxy methodology** (Tester PR #32). Historical bid/ask is not mandatory for the primary backtest; OHLC/LTP is never relabeled as bid/ask.
- G13/G14: **BLOCKED**
- No backtest engine, optimization, profitability result, or trading-strategy conclusion has been introduced.
- Historical evidence sections below are append-only records; the gate table above is the current control state.


## Research files
- [Research plan](RESEARCH_PLAN.md)
- [Research status](RESEARCH_STATUS.md)
- [Phase 1 acceptance report](research/PHASE1_ACCEPTANCE_REPORT.md)
- [Source-derived strategy specification](research/STRATEGY_SPEC.md)
- [Literature and data review](research/LITERATURE_AND_DATA_REVIEW.md)
- [Tester handoff](research/TESTER_HANDOFF.md)
- [Error log](ERROR_LOG.md)
- [Conversation log](CONVERSATION_LOG.md)
- [Project instructions](PROJECT_INSTRUCTIONS.md)

## Phase 1 data decision
Primary candidate: thetrademarkk/india-index-options-1m, pinned to Hugging Face revision 0f4800e. Documentation describes 1-minute OHLCV(+OI), IST timestamps, strike/type/expiry fields, and partial coverage of illiquid/far strikes. Historical bid/ask is not documented.

NSE current option-chain pages provide bid/ask, OI, volume and reference IV, but the historical intraday archive needed for this study is not established from that interface. Current NSE data are treated as reconciliation/reference data rather than silently substituted for historical quote history.

## Historical contract and cost controls
NSE Circular 128/2024 changed NIFTY lot size from 25 to 75 for new index derivatives introduced from 20 November 2024. The 2025 NSE expiry-day transition changed newly introduced NIFTY contracts to Tuesday expiry, with explicit treatment for already introduced contracts. Historical contract masters must be applied by effective date.

Paytm Money materials document cohort/date-dependent brokerage and a 1 October 2024 option-sale STT change. The final cost engine will use contemporaneous date-specific brokerage, STT, exchange/IPFT, SEBI, GST, stamp duty and other applicable charges.

## Structural validation evidence
A prior acquisition on mutable main downloaded 269 parquet files and passed structural validation on commit 5f701e329c7888e5ccd5cfe70cea0f5c14e452ac (run 37116084761, job 111183065244, artifact 11271990517, SHA-256 67fd3898800131d736a5652d1ece3c112c4b5b0489ffe07468f5865fb850d789). Because the source was mutable, that run is not the production acceptance run.

The current workflow pins the source to 0f4800e and uses separate cache restore/save steps. Pinned-source audit run 37116400642 completed successfully: 109,112,358 rows across 269 files, with 0 hard structural failures but 30,363,281 exact duplicate rows across 138 files. Deterministic deduplication is now mandatory before production use. The acquisition scope has since been narrowed to index/NIFTY.parquet, so a fresh validation run is required.

## Open Phase 1 gates
- G5 underlying/option alignment — automated exact-timestamp acceptance audit pending CI;
- G6 production historical Greeks/IV;
- G7 target-delta availability;
- G8 historical contract metadata;
- G10 date-specific transaction costs;
- G11 market-context datasets;
- independent Phase 1 tester PASS.

## G5 alignment step — 2026-10-03
A dedicated fail-closed G5 validator and GitHub Actions workflow were added. The validator separates date-specific session eligibility from exact NIFTY timestamp matching, rejects duplicate underlying timestamps and invalid option timestamps, reports expiry/day coverage, and never interpolates missing underlying observations. The workflow uses the pinned source revision `0f4800e`, cache restore/save, automatic push/PR triggers, manual dispatch, and retained evidence artifacts. G5 is **OPEN pending exact-head CI evidence and independent tester review**.

Open Phase 1 gates — detailed:
- pinned-source validation and file provenance;
- timestamp/missing/stale coverage;
- underlying alignment;
- Greek reconstruction and IV-solver audit;
- target-delta strike availability;
- historical NSE contract metadata reconciliation;
- date-specific Paytm Money/statutory costs;
- market-regime/context datasets;
- independent Phase 1 tester PASS.

**No performance conclusion is justified yet. No backtest engine or optimization has begun.**

## Latest Phase 1 CI incident
The latest run passed structural validation but initially failed at deterministic deduplication because the referenced script was missing from the committed tree (E026). The missing `scripts/deduplicate_phase1_data.py` has now been added. Phase 1 remains open pending a fresh CI run and the remaining data-quality, execution, cost, context, and independent-tester gates.

### Latest data-quality finding
Run 21 completed the structural, deterministic-deduplication, and diagnostic market-quality stages. Option timestamps matched NIFTY timestamps for 99.2953% of post-key-dedup option rows. However, NIFTY daily timestamp counts range from 6 to 420 across 1,262 dates; these session outliers are now an explicit acceptance blocker (E028) and will be characterized before production use.

## Branch
`phase-1-g5-underlying-option-alignment` (current developer G5 evidence branch).

## Latest Phase 1 controls
- Deterministic exact-row deduplication: `scripts/deduplicate_phase1_data.py`.
- Conflicting duplicate keys remain fatal.
- GitHub Actions concurrency/cache-save race mitigation added after E025.

### Phase 1 latest execution
- Run 22 (37118147417) completed with structural validation and deterministic deduplication successful, but the market-quality audit failed due to malformed escaped-newline Python source (E029).
- E029 was repaired in commit 336c8e8ddf5de93f31ef6b114e621747ae956620; a clean Phase 1 rerun is required.
- Historical bid/ask remains an explicit data-source gap. The primary historical dataset exposes OHLCV/OI but not documented bid/ask, while the current NSE option-chain page exposes bid/ask for live snapshots. No close-price substitution has been accepted for the frozen literal-core midpoint rule.

- Phase 1 quote-data escalation: official NSE Historical Order & Trade Data is registered as the preferred procurement candidate for historical order-level quote reconstruction; access is paid and not yet acquired.
- PR #13 was opened for the repaired CI path, but no new Actions status was emitted in this environment; therefore Phase 1 acceptance remains blocked and no repaired-run result is claimed.

- E029 control improvement: Phase 1 CI now performs a fail-fast Python syntax check before data acquisition.

- Phase 1 evidence search expanded to GitHub/open-source and commercial NIFTY archives; reviewed alternatives also lack historical bid/ask. NSE Historical Order & Trade Data remains the preferred quote-source procurement route.
- Tester handoff updated with the remaining acceptance gates; Phase 2 remains blocked.

- Official RBI, NSE and Paytm Money source validation advanced the rate/cost/contract metadata gates; complete historical extraction remains open.
- Phase 1 tester handoff now separates closed source-identification work from remaining production-acquisition gates.

- Added research/PHASE1_GATE_MATRIX.md as the explicit acceptance matrix for the tester; it separates source identification from production acquisition and keeps Phase 2 blocked.


- **Independent tester result:** Phase 1 FAIL. PR #13's repaired audit still lacks independently verifiable Actions execution, and session/Greek/contract/quote/cost/context gates remain open.
- **E033 resolved at the documentation-control level:** canonical G1–G14 meanings are now defined consistently across Phase 1 control documents. This does not itself make any data gate PASS.
- [Phase 1 gate matrix](research/PHASE1_GATE_MATRIX.md) now serves as the canonical gate vocabulary.
- Added [Phase 1 production evidence plan](research/PHASE1_PRODUCTION_EVIDENCE_PLAN.md), defining machine-readable evidence required for G4–G12 after E033 closure.
- External NSE evidence confirms historical session timing cannot be inferred from today's 15:40 F&O close; date-specific session metadata is required.
- G12 remains open: GitHub Actions reports zero workflow runs for repaired audit commit 336c8e8ddf5de93f31ef6b114e621747ae956620.
- E034 records that local execution cannot substitute for CI because this environment has no outbound network resolution.

## Phase 1 control-source specifications
- [Historical NSE session calendar specification](research/PHASE1_SESSION_CALENDAR_SPEC.md) — date-specific session reconciliation; no retrospective use of current 15:40 hours.
- [Historical contract and cost specification](research/PHASE1_CONTRACT_COST_SPEC.md) — effective-date NIFTY lot/expiry controls and date/cohort-specific Paytm Money/statutory charges.
- [Historical quote-data procurement decision](research/PHASE1_QUOTE_DATA_PROCUREMENT.md) — G9 requires bid/ask or deterministic order-level reconstruction; close-price substitution remains disallowed.
- [Phase 1 control-source manifest](data/manifests/phase1_control_sources.json) — provenance register for session, contract, risk-free, broker-cost and volatility-context sources.

### Latest Phase 1 evidence step — 2026-10-03
The developer formalized the remaining production evidence requirements without promoting any gate to PASS. Official NSE documentation confirms a paid F&O historical order/trade product suitable for quote/execution reconstruction. Official NSE circulars confirm that NIFTY lot size and expiry rules changed during the sample, so historical contract metadata must be effective-date based. RBI provides historical 91-day T-bill primary yields, and Paytm Money documents brokerage/STT changes by date and user cohort. G4–G12 remain open/blocked pending machine-readable acquisition, execution and independent review.

### E035 control correction — 2026-10-03
The Phase 1 acceptance report was synchronized with the canonical G1 PASS state, and unused hard-coded session-bound constants were removed from the diagnostic audit. Historical session acceptance remains date-specific and G4 remains OPEN. No Phase 2 work has begun.


### Independent tester E037 — 2026-10-03
The independent Phase 1 tester recorded **FAIL / IN PROGRESS** and kept Phase 2 **BLOCKED**. E037 identified a CI correctness defect: the syntax-check step used a plain `run:` scalar, so its second command was folded into the first command rather than executed separately. The workflow was corrected in commit `fb5993afa89cfce7fac177d1a62c45e98bddbc27` using an explicit multiline command block. G12 remains FAIL/OPEN until the corrected workflow has an independently verifiable Actions run. No backtest, optimization, profitability result, or trading conclusion has been introduced.


### G12 autonomous execution attempt — 2026-10-03
The corrected workflow was committed with an execution-trigger marker (`70baca4a23649ec58cb30e2e91a6747f3f2d8267`) to test whether a repository-side push could initiate Actions. GitHub returned zero workflow runs for that commit. G12 therefore remains FAIL/OPEN; no Phase 2 advancement is permitted.


## 2026-10-03
2026-10-03 — G12 UI correction: The Phase 1 workflow was added unchanged to the default branch so GitHub can expose the manual workflow-dispatch control. This does not merge the Phase 1 research branch or authorize Phase 2. Actual G12 execution remains pending dispatch.


### G12 run #32 — branch-target correction
Manual run #32 was dispatched on `main` and failed after 22 seconds. The dispatch workflow has now been corrected so manual execution defaults to `phase-1-data-acquisition-validation`, where the Phase 1 scripts and manifests reside. G12 remains unaccepted until a real run succeeds and produces verifiable artifacts.


### G12 execution evidence — E041
Run `37122653828` reached the Phase 1 branch but failed in syntax/control-manifest validation because `scripts/validate_phase1_control_manifests.py` was missing from that branch. The validator has been restored unchanged at commit `68b39d91035bcb79c192cac80f20fd29ed6e709d`. G12 remains open pending the next execution.


### Latest Phase 1 execution — G12 PASS on developer evidence
Successful run `37122686454` on `phase-1-data-acquisition-validation` completed all Phase 1 workflow steps. Artifact `11274027306` was verified. Fresh data evidence: 108,625,497 raw rows, 0 hard-failure files, 30,363,281 exact duplicates removed, 77,776,166 option rows after key dedup, 99.2953% option/NIFTY timestamp alignment, and 286 session-count diagnostic outliers. G12 is now PASS on developer evidence; G13/G14 remain blocked.


### G4 session reconciliation — PASS on developer evidence
Fresh CI run `37124047220` reconciled the NIFTY observation dates against dated session controls: 1,254 normal eligible dates, 7 documented special sessions, and one pre-registered data-gap exclusion (2026-06-03), with zero unreconciled dates. Strategy execution will use only the regular 09:15–15:30 IST F&O window except explicitly documented special sessions; excluded raw dates remain retained for audit. G4 still requires independent tester verification.

## Independent tester E044/E045 — 2026-10-03
The independent tester found two substantive blockers. E044: the previous G4 manifest still contained unresolved-date entries that the reconciliation code ignored, and special-session labels did not validate actual documented intervals. E045: the successful run was on an older commit, not the current final Phase 1 head. Both findings are accepted.

The G4 implementation has now been corrected: explicit date controls replace the unresolved-date escape hatch; every special session has documented F&O execution intervals and source-observation intervals; the reconciler checks interval coverage, source-observation containment, controlled anomalies, and uncontrolled dates. A fresh workflow run on the resulting final Phase 1 head is required. No Phase 2 work has started.

### E044 correction frozen — final-head CI pending
The G4 correction is implemented and has successfully executed on an ancestor commit. The independent tester's E045 requirement is being honored: that run is not being treated as final evidence. The next CI execution will be tied to the final Phase 1 branch head after all methodology/control changes are frozen.
undefined

## Current Phase 1 status — 2026-10-03
- Phase 1: IN PROGRESS / NOT APPROVED.
- Corrective head: 4099cd1217f072be961f120ab114034578e19197.
- Exact-head CI: run 37129894485, job 111222750604, all steps successful.
- Validation artifact: 11275819920; SHA-256 57cdcc53ec350fea1ce398f1130d5dd66beb63cdc0b481485e2b0e4fe3d54178.
- G4 reconciliation: 1,262 observed dates; 13 manifest controls; 10 special sessions reconciled; 1 data-gap exclusion; 0 unreconciled; 0 missing manifest-session dates.
- G4/G12: developer-evidence PASS on the corrective head; G13: BLOCKED pending independent tester re-audit; Phase 2: BLOCKED.
- E047 added dated controls for the documented weekend live-trading sessions 2024-01-20, 2025-02-01 and 2026-02-01 after the fail-closed exact-head rerun identified them.

See research/PHASE1_GATE_MATRIX.md, research/PHASE1_ACCEPTANCE_REPORT.md, research/TESTER_HANDOFF.md, and ERROR_LOG.md.


## E048 manual-dispatch safeguard — 2026-10-03
The default-branch Actions workflow was updated to expose the E046-corrected Phase 1 workflow for manual dispatch. Main workflow commit: `097d29c2816614bc7ba45365454b7f0dc270bc5d`. Manual run #52 shown in the user screenshot is not accepted as corrective evidence unless its explicit `research_ref` selected the E046 branch.


## E051 — exact-tip CI evidence remains pending
The corrective branch now points to b6e8ff93edfd2d3e5f1797d0d1d2ed186189d512. The workflow file was touched only to force a push-path execution after documentation commits had advanced the branch beyond the previously verified run 37129894485 on commit 4099cd1217f072be961f120ab114034578e19197.

The current commit-status endpoint reports pending with zero published statuses, and the available repository connector does not expose the push-triggered run list. Accordingly, no current-head G12 PASS is claimed. Phase 2 remains BLOCKED until an observable Actions run proves the exact checkout SHA and the independent tester records G13 PASS.


## E052 — 2026-10-03 — co-commit exact-tip execution control
- To prevent documentation-only commits from moving the research head after a workflow-trigger commit, the final control/documentation update is being co-committed with the workflow marker.
- This commit is intended to be the exact current-head candidate for automatic Phase 1 CI. No G12 PASS is claimed until an observable Actions run proves the checkout SHA and completes all validation steps.


## E053 control-plane synchronization — 2026-10-03
The independent tester's Run #55 re-audit identified stale top-level Phase 1 status text. This developer branch synchronizes the canonical current-state sections while retaining older run-specific evidence as historical records. The developer role remains correctly identified as Developer on this branch; tester status is represented by the independent tester report/PR rather than by changing the developer branch's role label.

- **2026-10-03 substantive G5–G11 source audit:** added [G5–G11 source audit](research/PHASE1_G5_G11_SOURCE_AUDIT_20261003.md), expanded the official contract/cost/source manifests, and re-verified the NSE F&O Historical Order & Trade procurement route. These are evidence/provenance advances only; G5–G8/G10–G11 remain open and G9 remains blocked. No Phase 2 work has started.

- **G9 candidate discovery:** a public Hugging Face NIFTY TBT dataset with bid/ask/depth fields was identified and registered as a candidate. Its published dataset currently reports incompatible schemas, so it is not accepted. An automated cached CI audit workflow has been added; G9 remains BLOCKED pending validation.


### G9 free-data salvage — current step
The independent tester's PR #27 prescribed a fixed acquisition order for G9. The developer has created the G9 free-data salvage protocol at research/PHASE1_G9_FREE_DATA_SALVAGE.md and expanded the source manifest. Current candidates include the pinned Hugging Face TBT archive, the ayyararyan/nse-options-pipeline raw-data lead, OptionVault/TickBytes samples, and retained-data investigation for the NSE options collector. **G9 remains BLOCKED** until one common validator demonstrates complete, reproducible historical execution-quality coverage. Candle close/OHLC remains prohibited as a bid/ask or midpoint substitute.

## G9 salvage continuation — 2026-10-03
The exact developer submission `d2003df53d07a952aa7434c4c706f396067b6080` was checked for associated PR-triggered Actions; none was observed through the available GitHub connector, so no CI result is claimed. The G9 workflow and validator were then hardened: raw CSVs are classified independently with immutable-file SHA-256, schema, timestamp, contract-identity, duplicate/order, and bid/ask validity diagnostics; acquisition failures produce a retained machine-readable report; OHLC/LTP is never substituted for bid/ask; cache keys are pinned to the candidate revision; and the workflow uploads the audit report even when acquisition fails. G9 remains **BLOCKED** and Phase 2 remains **BLOCKED** pending independently reproducible raw-data evidence and tester approval.

## 2026-10-03 — E063 execution-methodology change
The primary backtest methodology has been explicitly changed so historical bid/ask is no longer mandatory. See [Phase 1 Execution Proxy Specification](research/PHASE1_EXECUTION_PROXY_SPEC.md).

The frozen model uses completed 1-minute decision bars and fills at the next eligible option bar open, with adverse per-leg slippage scenarios of 0/5/10/20/50 bps and an effective-date tick-size floor. Brokerage and statutory/exchange costs remain date-effective and separate. Missing execution bars are not interpolated, and OHLC/LTP are never relabeled as bid/ask.

This changes the interpretation of the research from historical executable-fill validation to **proxy-execution backtesting under explicit sensitivity assumptions**. G9 is **BLOCKED pending independent tester approval of the methodology**; G13/G14 and Phase 2 remain BLOCKED.

### E064 — execution-proxy specification documentation correction
The execution-proxy specification initially rendered mathematical escape sequences incorrectly. The equations were corrected without changing the frozen slippage parameters or execution convention. See `research/PHASE1_EXECUTION_PROXY_SPEC.md`. This correction does not advance any gate.

## Latest execution-proxy correction — 2026-10-03
Independent tester PR #30 identified E065 and E066 in the proposed bid/ask-free execution methodology. The developer correction now defines atomic multi-leg failure handling: if any required next-bar leg is missing or invalid, no leg fills, the prior state is retained, the triggering event is consumed, and a fresh trigger requires exit/re-entry. Sell-side slippage no longer clips to zero; non-positive fills are rejected explicitly, matching the invalid-price rule. Regression tests and a dedicated GitHub Actions workflow were added. **Tester approval is still pending; G9/G13/G14 and Phase 2 remain BLOCKED.**

## G9 status update — 2026-10-03
**G9 = PASS under the revised proxy-execution methodology**, independently approved in Tester PR #32 after re-audit of developer head `8b99cb3b2b537c5b085c09729c27bb3957285ae8`. Historical bid/ask is not required for the primary backtest. The accepted model uses completed-bar decisions, the first eligible next-bar option open, atomic multi-leg execution, fail-closed missing-leg handling, trigger consumption/re-arm, historical tick-size floor, 0/5/10/20/50-bps adverse slippage and date-effective transaction costs. OHLC/LTP is never called bid/ask/midpoint/executable price. **G13/G14 and Phase 2 remain BLOCKED** pending G5/G6/G7/G8/G10/G11.


### 2026-10-04 — E071 G5 validator correction
The G5 validator had a report-construction field-reference defect found before execution. It was corrected to use the actual `decision_eligible` field. No G5 PASS is claimed; exact-head CI and tester review remain required.

## Current developer status — 2026-10-04
- Independent tester PR #36: **Phase 1 FAIL / IN PROGRESS**.
- G5 remains **OPEN** because exact developer head `3225d29902a20c958bf8c9803479e8fbe7601dbf` had no observable Actions run/status, and tester required explicit artifact-to-checkout SHA binding.
- G5 correction PR #37 adds exact checkout SHA to the evidence artifact and CI verification; manual dispatch can require an expected commit SHA.
- G6 remains **OPEN**. Correction PR #38 adds cache restore/save to the official-source acquisition workflow; complete r/q and IV/Greek production reconstruction remain pending.
- G13/G14 and Phase 2 remain **BLOCKED**.
- No backtest, optimization, profitability analysis, or strategy conclusion has been introduced.

## 2026-10-04 — Tester PR #39 corrective response
Tester PR #39 confirms **G5 FAIL/OPEN, G6 FAIL/OPEN, G9 PASS, G13/G14 and Phase 2 BLOCKED**. The Developer created `phase-1-g5-g6-reaudit-corrections-20261004` and corrected the two identified workflow/reuse defects. G5 push triggers now include the active correction branch. G6 source acquisition reuses retained source files rather than unconditionally redownloading them, while preserving provenance checks. No Phase 2 work has started.

## 2026-10-04 — Tester PR #40 corrective response
Tester PR #40 found a G6 cache-integrity defect. The developer corrected the cache path to fail closed on missing or mismatched immutable SHA-256 provenance. G5/G6 remain OPEN and G9 remains PASS; no Phase 2 work has started.

## 2026-10-04 — Latest CI evidence
- G6 source provenance bootstrap produced real observed SHA-256 values, which are now committed to the manifest; no placeholder digests remain.
- G6 exact-tip CI run **37148353717** succeeded at commit `e8fca6a6084a463528643b63dd8f310899c0b3bf`, with artifact **11282958617**. This does not constitute G6 PASS because substantive r/q and IV/Greek reconstruction remain incomplete.
- G5 exact-tip CI run **37148384171** is executing at commit `001e498bfc099e9f51df9129e1fdc2e9370b2b3a`; G5 remains OPEN pending completion and tester re-audit.

## 2026-10-04 — G6 substantive production reconstruction implementation
- New branch: `phase-1-g6-production-greeks-20261004` from paired SHA `db668dd2b89bf691a6481affb3cb2a9060c5fe98`.
- Added the fail-closed G6 production Greek specification, production audit script, and GitHub Actions workflow.
- The pipeline requires historical r/q inputs and refuses to manufacture missing coverage, future data, interpolation, or proxy values.
- A local official-NSE q-data acquisition attempt was blocked by environment DNS isolation and logged as E082; this is not treated as research evidence.
- G6 remains OPEN; G5 remains independently tracked on its exact-tip submission; G13/G14 and Phase 2 remain BLOCKED.


## 2026-10-04 — G6 production branch update
The G6 production branch now includes a fail-closed production Greek evidence scaffold and corrected E084 coverage logic. Coverage is derived from actual NIFTY option-bar dates rather than the reference q table. Official-source acquisition leads have been documented, but no substitute rate/dividend data have been accepted and G6 remains OPEN. The paired G5 exact-tip audit on run 37148487963 is still executing independently.


## 2026-10-04 — E089 G6 production correction
- Independent tester PR #45 determined G6 FAIL / OPEN on developer head c5f28327c13efd9b93bd4ca5a809dfc39b447c3d. E088 is accepted without reinterpretation.
- The previous implementation was a scaffold rather than a completed historical Greek reconstruction.
- The correction now performs timestamp-level production reconstruction with exact contemporaneous NIFTY joins, strictly-prior r/q selection, study-window enforcement, 15:30 IST expiry timing, deterministic Brent IV solving, signed/absolute deltas, target-delta diagnostics, populated failure counters, checksums and exact-checkout provenance.
- G6 remains FAIL / OPEN because complete historical risk_free.csv and dividend_yield.csv inputs are not yet accepted and independent tester approval is still required.
- G5 remains FAIL / WAIVED FOR CONTINUED RESEARCH; G13/G14 and Phase 2 remain BLOCKED.


## 2026-10-04 — E090 CI harness correction
- Exact-tip G6 run 37156880805 failed during test collection because the test imported scripts.phase1_g6_production_greeks while scripts is not a package.
- Corrected the test import path and logged E090. No G6 gate advancement occurred.
- A fresh push-triggered exact-head run is required before any substantive production-scan conclusion.


## 2026-10-04 — E091 pandas datetime compatibility correction
- Exact-tip run 37156932044 passed 6/7 G6 tests and failed only the strict-prior regression because pandas 3.x used different datetime units on the two merge keys.
- Both sides are now normalized to datetime64[ns]. E091 is logged. No gate advancement occurred.


## 2026-10-04 — G6 evidence completeness refinement
- The production scan now requires option volume in the production schema and performs deterministic target-delta contract selection using minimum delta error, then higher volume, then lower strike distance as the frozen tie-break.
- The scan also records signed-delta, absolute-delta and IV histograms in the evidence artifact.
- This is an evidence-completeness correction only. G6 remains FAIL / OPEN because historical r/q production inputs are still missing.


## 2026-10-04 — Exact-head G6 production evidence attempt
- Exact developer head: 02702ff384596dd270ca12946e613eeda53d4236.
- Actions run 37157070947 completed with unit tests passing and the production audit failing closed because data/processed/g6/risk_free.csv and data/processed/g6/dividend_yield.csv are absent.
- Evidence artifact 11285937357 was produced and is bound to the exact checkout SHA; artifact digest sha256:c9d3748f22da9f83525f7aa4594dafbb69364370764230dae374a487d9f7d78c.
- This is substantive evidence that the corrected production scanner is reached and fails closed on missing mandatory inputs. It is not G6 PASS evidence.


## 2026-10-04 — G6 official r/q acquisition implementation
- Added `scripts/acquire_g6_rbi_risk_free.py` to enumerate the official RBI WSS archive, retain/hash source pages containing the 91-day Treasury-bill primary yield, extract dated observations, reject conflicting duplicates, and emit `data/processed/g6/risk_free.csv`.
- Extended the G6 workflow to execute the existing official NSE Indices NIFTY 50 P/E/P/B/dividend-yield acquisition and convert its double-parsed response into `data/processed/g6/dividend_yield.csv` before the production scan.
- The production pipeline therefore now has a concrete primary-source acquisition path for both mandatory r and q inputs. No secondary proxy has been substituted.
- G6 remains FAIL / OPEN pending exact-head CI acquisition results and independent tester review.


## 2026-10-04 — E092 workflow wiring correction
- Run 37157227269 executed head e76c40a but did not contain the intended r/q acquisition steps because the earlier workflow edit changed only the trigger path list.
- No acquisition was attempted in that run; the production scan therefore failed on the already-known missing r/q inputs.
- Corrected the workflow at head 7177aa7dfeecc667cb3dd9471347d3538ba9a467 to execute both official acquisition scripts before the production scan, install requests/lxml, and cache the retained official-source material.
- No gate advancement occurred; a fresh exact-head run is required.


## 2026-10-04 — E093 NSE q response parsing correction
- Exact-head run 37157292177 reached the official NSE dividend-yield acquisition successfully, but the conversion step failed because the retained response wrapper used Python-style single quotes and was parsed with `json.loads`.
- Corrected the workflow to use `ast.literal_eval` for the trusted, locally retained response wrapper, then JSON-decode only the endpoint's inner `d` payload.
- No data values were changed and no gate advanced. A fresh exact-head run is required.


## 2026-10-04 — E094 NSE endpoint-response correction
- Exact-head run 37157347960 reached the NSE acquisition but the endpoint returned an HTML page rather than the expected JSON payload. The stored HTML was then incorrectly treated as JSON.
- Corrected the official NSE request to the documented single-quoted `cinfo` form with browser-style headers and added an explicit HTML-response failure check. The downstream parser is restored to JSON decoding because the corrected acquisition now requires a valid JSON response.
- No secondary q source was substituted and no gate advanced.


## 2026-10-04 — E095 NSE q access-layer hardening
- Exact-head run 37157416345 still received HTML from the NSE dividend-yield endpoint despite the corrected payload.
- The acquisition client is now hardened with an initial historical-data page GET for session cookies, browser-style headers, the current `/Backpage.aspx/...` endpoint and the legacy `/BackPage/...` fallback, with explicit JSON-vs-HTML validation.
- No q data have been substituted and G6 remains FAIL / OPEN.


## 2026-10-04 — E096 NSE q response-shape correction
- Exact-head run 37157488655 reached the NSE endpoint and received structured JSON, but the response was a top-level list rather than the legacy `{d: ...}` wrapper.
- Corrected the converter to accept both documented/current response shapes without changing source bytes or values.
- No gate advancement; the next exact-head run must establish complete q coverage and then exercise RBI acquisition and production Greeks.


## 2026-10-04 — E097 RBI acquisition performance correction
- The exact-head RBI acquisition in run 37157538662 was serially probing 3,000 archive IDs and did not complete within the acceptable research execution window.
- Replaced the serial scan with bounded parallel retrieval (20 workers), expanded the lower bound to ID 24000 to avoid an unverified 2021 coverage cutoff, and retained per-page SHA-256 provenance for every page containing the target series.
- No values or acceptance criteria were relaxed. G6 remains FAIL / OPEN.


## 2026-10-04 — E098 RBI acquisition entry-point defect
- Exact-head run 37157862634 reported the RBI acquisition step successful, but the production artifact still lacked `risk_free.csv`.
- Inspection of exact-head source showed `main()` was defined but never invoked, so the step was a no-op and the CI success status was misleading.
- Added the explicit module entry point. No gate advancement; the next run must prove actual RBI row extraction, coverage, provenance and production consumption.


## 2026-10-04 — E099 RBI entry-point escaping correction
- Exact-head run 37157954305 failed because the E098 entry-point was committed with literal `\\n` text, causing a Python syntax error.
- Corrected the file to contain actual newline characters and preserved the intended explicit `main()` invocation.
- No gate advancement; a fresh exact-head run is required.


## 2026-10-04 — E100 duplicate RBI entry-point text correction
- Exact-head run 37158026784 still failed because the previous correction left both literal escaped and real `main()` entry-point blocks in the file.
- Removed the literal duplicate and verified the exact file tail contains one valid module entry point.
- No gate advancement; next exact-head run must establish actual RBI extraction.


## 2026-10-04 — E101 RBI non-target page handling correction
- Exact-head run 37158125363 executed the RBI scan but failed because non-target/404 pages returned `None`, while the concurrent collector expected every future result to be a `(record, rows)` tuple.
- Corrected non-target pages to return an explicit empty-result tuple with provenance status `NO_TARGET`.
- No data acceptance or gate change occurred.


## 2026-10-04 — E102 final RBI primary-host fallback
- The runner reached the RBI acquisition but produced zero target rows from the initial official host. A final bounded attempt now probes the canonical `www.rbi.org.in`, apex `rbi.org.in`, and `wss.rbi.org.in` WSS hosts for the same archive IDs.
- If no primary rows are obtained, the script writes a failure diagnostic with per-page status counts and stops. No secondary RBI mirror is substituted into production.
- This is the final planned primary-host acquisition attempt for G6; repeated blind retries are prohibited.


## 2026-10-04 — Final G6 primary r acquisition result
- Exact developer head: `fcba8794002b9f129a20dd1e4d19f32c3a97bab5`.
- Final Actions run: `37158613890`; job `111307127681`.
- Official NSE NIFTY 50 dividend-yield acquisition completed successfully with **1,425 rows**.
- RBI acquisition executed across three official hostnames (`www.rbi.org.in`, `rbi.org.in`, `wss.rbi.org.in`) over the bounded WSS ID range and returned **zero parseable 91-Day Treasury Bill (Primary) Yield observations** to the runner. The step therefore failed closed with `RBI_NO_91D_TBILL_ROWS`.
- RBI public WSS/DBIE availability is independently corroborated externally, but the machine-readable primary series could not be retrieved by this CI execution environment. No secondary mirror has been substituted into production.
- **G6 remains FAIL / OPEN.** This is the final planned blind primary-host retry. A secondary RBI mirror may be investigated only as a separately labelled cross-check/provisional source and cannot silently convert G6 to PASS.
- G5 remains FAIL / WAIVED FOR CONTINUED RESEARCH; G13/G14 and Phase 2 remain BLOCKED.


## 2026-10-04 — Tester PR #46 secondary RBI cross-check
- Tester branch `tester/phase-1-g6-secondary-r-crosscheck-20261004` independently reviewed the provisional Dataful RBI-derived cross-check.
- Tester determination: **G6 FAIL / OPEN**. The source is not accepted as a production r input without immutable full-file provenance, coverage/duplicate audit, and reconciliation to primary RBI WSS observations.
- No Phase 2 authorization. G5 remains FAIL / WAIVED FOR CONTINUED RESEARCH.
- Tester report: `research/TESTER_REPORT_G6_SECONDARY_R_CROSSCHECK_20261004.md`; PR #46 targets this developer branch and is intentionally not merged as a gate-advancement mechanism.


## 2026-10-04 — automatic tester handover and E104 correction
The developer branch automatically handed exact head 2dd4506e5173052c58573a94f9a3368f1a7d3190 to isolated tester branch tester/phase-1-g6-handover-20261004 (PR #47). The tester correctly returned G6 FAIL/OPEN and identified E104: the RBI cache path existed but the acquisition script did not actually reuse retained pages, and availability-date semantics were insufficiently explicit. The developer corrected the acquisition with fail-closed sidecar SHA-256 cache validation, immutable expected hashes for bootstrapped RBI pages, rejection of unproven retained files, and an explicit conservative observation-date eligibility convention with strict-prior same-day exclusion. A regression test was added. G5 remains FAIL/waived for continued research; G9 remains PASS; G13/G14 and Phase 2 remain blocked. Fresh exact-head CI and automatic tester re-handover are required.


## 2026-10-04 — E105 acquisition-runtime correction
The exact-head G6 validation run `37171349785` remained in official RBI acquisition without reaching tests/evidence. The developer identified the operational cause (broad WSS scan, 20 workers, 10-second timeout) and tightened it to IDs 24000–28500, 100 workers, 3-second timeout. No data-integrity or no-lookahead safeguards were relaxed. G6 remains OPEN/FAIL pending fresh exact-head CI and independent tester re-audit; G5 remains FAIL/waived, G9 PASS, G13/G14 and Phase 2 BLOCKED.


## 2026-10-04 — Current G6 execution status after E106
- E106 corrected RBI acquisition runtime by trying the four known official WSS candidates before the wide fallback scan; immutable SHA/provenance and strict-prior controls remain unchanged.
- Fresh exact-head CI is still required. The connector currently exposes no new Actions run for the corrected head, so G6 is FAIL/OPEN and Phase 2 remains BLOCKED.


## 2026-10-04 — Tester PR #48 current status
- Automatic isolated tester re-audit of developer head b75e64d3f6caf9f086a0c063153ccc6315aa5c5 returned **G6 FAIL/OPEN**.
- E106 code-level controls were independently found sound, but exact-head Actions/artifact evidence is absent. G5 remains FAIL/WAIVED, G9 PASS, G13/G14 and Phase 2 BLOCKED.
- Required next step: make exact-head CI observable through repository-native automation, verify artifact binding, then automatically hand the corrected exact head to a fresh tester branch.


## 2026-10-04 — E106 structured RBI risk-free source
G6 production risk-free acquisition has been redesigned around RBI Bulletin Table 26: the 91-day Government of India Treasury-bill implicit auction yield. The source is pinned to immutable Reserve Bank Innovation Hub commit `0db4ddb88c3119347e809af78c93beb4d1c874d4` / Git blob SHA-1 `ff603b132a2aa2aee8b1bc08d0d1e68879af2ea7`, with cache/provenance validation and conservative auction-date strict-prior semantics. RBI WSS remains a reconciliation/control source. G6 remains OPEN/FAIL pending exact-head CI and independent tester re-audit; G5 remains FAIL/waived, G9 PASS, G13/G14 and Phase 2 BLOCKED.


## 2026-10-04 — E107/E108 source-verifier correction
The first RBI Bulletin provenance validation failed because the Git blob verifier itself encoded the header incorrectly. The developer corrected the NUL-byte construction and verified the committed source line directly. The pinned RBI Bulletin commit/blob identity is unchanged. G6 remains OPEN/FAIL pending fresh exact-head CI and independent tester re-audit; no gate was advanced.


## 2026-10-04 — E109 RBI Bulletin parser correction
Immutable RBI Bulletin provenance validation passed, after which CI exposed a blank-cell/`NaT` parser edge case. The date parser was hardened to coerce invalid cells to missing and skip them. G6 remains OPEN/FAIL pending fresh exact-head CI and independent tester re-audit.


## 2026-10-04 — E110/E111 G6 underlying materialization
The G6 production artifact correctly failed closed because the contemporaneous NIFTY underlying parquet was missing from the workflow workspace. The developer added pinned acquisition of the independently audited HF NIFTY file (revision `92e0288`, SHA-256 `613864738250107807354c17c7092986960220ac3062b830c65cc5f9ec16fcf7`), cache validation, HF_TOKEN support, and corrected workflow cache/path triggers. G6 remains OPEN/FAIL pending fresh exact-head CI and independent tester re-audit.


## 2026-10-04 — E112/E113 G6 option-input materialization
The G6 production scan now has pinned acquisition for the required NIFTY option-chain parquet files from the audited HF dataset, with per-file SHA-256 validation, provenance manifest, HF_TOKEN support, and cache persistence. The prior artifact had failed closed solely because option inputs were absent. G6 remains OPEN/FAIL pending fresh exact-head CI and independent tester re-audit.


## 2026-10-04 — E114 HF option-listing correction
The pinned NIFTY option acquisition initially failed at Hugging Face file listing due to an unsupported tree API parameter combination. The listing call was corrected to the documented recursive form; per-file SHA-256 validation remains mandatory. G6 remains OPEN/FAIL pending fresh exact-head CI.


## 2026-10-04 — E115 target-key correction
G6 production now reaches Greek selection with all required data inputs, but the latest scan exposed a target-delta diagnostic key-format bug (`0.3` versus `0.30`). The developer standardized the keys and added regression coverage. G6 remains OPEN/FAIL pending fresh exact-head CI and independent tester re-audit.


## 2026-10-04 — E115 G6 target-key correction
The complete G6 scan reached valid input/coverage state but failed on an internal diagnostic key mismatch (`0.3` versus `0.30`). This was corrected without changing the Greek solver or selection rules. G6 remains OPEN/FAIL pending fresh exact-head CI and tester re-audit.


## 2026-10-04 — E116 G6 runtime bound
The complete G6 production audit became an unbounded CI bottleneck. A 30-minute workflow timeout was added to the production-evidence step; timeout is fail-closed, not success. G6 remains OPEN/FAIL pending fresh bounded execution and independent tester re-audit.


## 2026-10-04 — E117 G6 deterministic-test correction
The bounded G6 run failed deterministic testing because one regression test referenced a stale loader and undefined vectorized-delta function. The production module now exposes a deterministic vectorized delta primitive and the test calls the actual module API. G6 remains OPEN/FAIL pending fresh exact-head CI.


## 2026-10-04 — E118 G6 IV solver performance correction
The G6 production scan was computationally dominated by serial independent IV roots. The exact same Brent equations, bounds, tolerances and fail-closed rules are now executed with Numba parallel row-level scheduling. No sampling or approximation was introduced. G6 remains OPEN/FAIL pending fresh exact-head CI.


## 2026-10-04 — E119 exact chunked G6 reconstruction
The production G6 scan now processes every pinned option row in exact 250,000-row Arrow batches instead of loading each file wholesale. This is an execution/memory correction only: no sampling, row omission, interpolation, or mathematical shortcut was introduced. G6 remains OPEN/FAIL pending fresh exact-head CI.


## 2026-10-04 — E120 exhaustive G6 sharding
The single-job G6 scan was computationally impractical despite exact batching and parallel IV roots. The production evidence path is now 8 deterministic, exhaustive option-file shards plus a fail-closed aggregator. Every row remains included exactly once; no sampling or approximation is introduced. G6 remains OPEN/FAIL pending fresh exact-head CI and independent tester re-audit.


## 2026-10-04 — E121 G6 shard configuration correction
The first E120 sharded execution failed because the production module referenced undefined shard configuration variables. The developer added validated `G6_SHARD_INDEX`/`G6_SHARD_COUNT` configuration, shard-specific evidence filenames, and regression coverage. No mathematical/data rule changed. G6 remains OPEN/FAIL pending fresh exact-head CI and independent tester re-audit; G5 remains FAIL/waived, G9 PASS, G13/G14 and Phase 2 BLOCKED.


### Latest G6 status — E121
- **G6: OPEN / IN PROGRESS.** E120's exhaustive 8-shard implementation failed closed before production scanning because shard variables were undefined. E121 corrected this; exact-head CI revalidation is required before tester handover.
- G5 remains **FAIL / WAIVED FOR CONTINUED RESEARCH** and G9 remains **PASS**. G13/G14 and Phase 2 remain blocked.


## 2026-10-04 — E131 G6 aggregation alignment
The 32-shard exhaustive scan completed without shard failures, but developer audit found the aggregate job was still configured for 8 shards. E131 corrected the aggregator to consume all 32 shards. The preceding scan is not accepted as G6 evidence; fresh exact-head CI and independent tester audit remain mandatory.


## 2026-10-04 — G6 evidence remediation
- Tester PR #49: G6 **FAIL / OPEN** on exact head `1a9eab7389b972c05362271ee9fb23092aa7354d`.
- Remediation branch: `phase-1-g6-evidence-remediation-20261004`.
- Scientific model unchanged; evidence now records IV iteration/residual distributions, expiry/date coverage, and explicit strict-prior/future-input audit results.
- Fresh exact-head CI and independent tester re-audit are required before G6 approval.
- [Tester G6 audit report](research/TESTER_G6_FINAL_AUDIT_20261004.md) is retained on the isolated tester branch/PR #49.


## 2026-10-04 — E137 execution-environment status
- The remediation workflow explicitly includes this branch in its push trigger, but the GitHub connector exposes no workflow-dispatch operation and reports no Actions run for corrected heads `e43acf88e10b4af13af54fe11d0c0a3cec5295ec` or `33fd3c798faa6104987f9440ba1d38a75e38eba3`.
- The previous G6 run is **not** reused for the corrected code.
- G6 remains **FAIL / OPEN** from tester PR #49; G13/G14 and Phase 2 remain blocked until a fresh exact-head run and independent tester re-audit.


## 2026-10-04 — G6 conditional-acceptance assessment
- The completed 32-shard G6 numerical scan is retained as immutable computational evidence, but PR #49 identified D1-D3 evidence-retention deficiencies.
- A formal conditional-acceptance proposal is now recorded at `research/G6_CONDITIONAL_ACCEPTANCE_PROPOSAL_20261004.md`.
- Independent tester branch `tester/phase-1-g6-conditional-acceptance-20261004` was created from developer remediation SHA `e9d319e7f2e902f77696fc4dbd029fa93cbbce7f`.
- **G6 remains FAIL/OPEN pending the tester verdict; G13/G14 and Phase 2 remain blocked.** No stale artifact is being silently upgraded to a full PASS.


## 2026-10-04 — Research progression waiver and Phase 2

The project owner accepted the historical G6 aggregate for research progression with deferred audit. G6 D1–D3 remain explicit limitations and are not retroactively claimed as satisfied. Intermediate evidence-completeness gates may be audited at milestone/final review, while material mathematical, look-ahead, data-quality, cost/slippage, logical and reproducibility failures remain blocking.

Phase 2 deterministic engine work is now active. [Research plan](RESEARCH_PLAN.md) · [Status](RESEARCH_STATUS.md) · [Tester handoff](research/TESTER_HANDOFF.md) · [Literature review](research/LITERATURE_REVIEW.md) · [Error log](ERROR_LOG.md).


## 2026-10-04 — Phase 2 engine milestone

Phase 2 is active on `phase-2-backtest-engine-20261004`. PR #53 contains the deterministic engine, proxy execution, cost resolution, event/fill ledgers and regression suite. See [Phase 2 specification](research/PHASE2_ENGINE_SPEC.md), [data contract](research/PHASE2_DATA_CONTRACT.md), and [literature review](research/LITERATURE_REVIEW.md).

The Phase 2 validation workflow is configured with PR and manual triggers, but no exact-head Actions status is observable through the current GitHub connector. No CI pass is claimed.

## 2026-10-04 — Phase 2 cost-model milestone

The engine now uses a dated, fail-closed cost layer with historical NSE option slabs, Paytm Money brokerage cohort assumptions, STT, SEBI, stamp duty and GST. The initial rate-conversion defect was caught before production results and corrected with unit tests; see ERROR_LOG.md E141.

Phase 3 preparation is documented in research/PHASE3_STATISTICAL_ANALYSIS_PLAN.md and market-context requirements in research/PHASE2_CONTEXT_DATA_SPEC.md. These are analysis preparations, not performance results.

## 2026-10-04 — Phase 2 integration control

Phase 2 has an exact end-to-end workflow, but **no production strategy result is being asserted yet**. The remaining hard input is the authoritative historical NIFTY contract master needed for lot-size, tick-size and contract-lifecycle reconciliation. See [contract-master specification](research/PHASE2_CONTRACT_MASTER_SPEC.md), [production run specification](research/PHASE2_PRODUCTION_RUN_SPEC.md), [statistical analysis plan](research/PHASE3_STATISTICAL_ANALYSIS_PLAN.md), and [context-data specification](research/PHASE2_CONTEXT_DATA_SPEC.md).

## 2026-10-04 — Final Phase 2 milestone snapshot

Phase 2 engineering is complete for milestone review at developer head `3d5c41f13269618b5d742527df973f405974c762`. See the [Phase 2 milestone report](research/PHASE2_MILESTONE_REPORT_20261004.md), [contract-master controls](research/PHASE2_CONTRACT_MASTER_SPEC.md), [production run specification](research/PHASE2_PRODUCTION_RUN_SPEC.md), [margin proxy](research/PHASE2_MARGIN_PROXY_SPEC.md), and [Phase 3 statistical plan](research/PHASE3_STATISTICAL_ANALYSIS_PLAN.md).

No production P&L or profitability claim has been made yet. The remaining material data dependency is the authoritative historical NIFTY contract master; independent tester review is also pending.

## 2026-10-04 — E146/E147 corrected; historical contract reconstruction added

The Phase 2 production workflow now has valid GitHub Actions expressions, matching scenario artifact names, and a fail-closed assertion for all five slippage scenarios. Historical monthly NIFTY contract metadata is reconstructed deterministically from the pinned expiry-partitioned option source plus official NSE lot-size chronology. See [contract-master provenance](research/PHASE2_CONTRACT_MASTER_PROVENANCE.md).

No production P&L is claimed until the exact-head workflow succeeds and the independent tester audits the resulting artifacts.

## 2026-10-04 — Exact-head production execution pending

Developer head `9e08a2882715b144cfe815f3c7d1382e848c9d18` contains the E146/E147 workflow corrections and E148 historical monthly contract reconstruction. Repository inspection is clean, but the available GitHub connector currently exposes zero Actions runs for this exact head. Consequently, no production P&L or profitability result is reported. See [Phase 2 contract provenance](research/PHASE2_CONTRACT_MASTER_PROVENANCE.md) and [Phase 2 milestone report](research/PHASE2_MILESTONE_REPORT_20261004.md).


## 2026-10-04 — E150 expiry-close control

E150 corrected a chronology defect in the reconstructed contract master: post-session observations could previously extend expiry_close_ts. The builder now bounds expiry_close_ts by the date-specific F&O execution-session close, with a regression test proving a 15:31 observation cannot extend a normal 15:30 close.

Under the authorized lenient-gate policy, the full five-scenario backtest is **not rerun at this stage**. Research/statistical/manuscript work may continue as non-final evidence, but no profitability/trading-strategy conclusion is final until the consolidated audit determines whether E150 could materially affect the tested window. See [contract-master specification](research/PHASE2_CONTRACT_MASTER_SPEC.md) and [error log](ERROR_LOG.md).


## 2026-10-04 — Statistical/manuscript preparation

Under the owner-authorized lenient gate, Phase 3 methodology and manuscript structure are being prepared without treating provisional production evidence as final. See [statistical analysis plan](research/PHASE3_STATISTICAL_ANALYSIS_PLAN.md) and [manuscript framework](research/MANUSCRIPT_FRAMEWORK.md). E150-dependent expiry-day results remain locked pending the consolidated audit.


## 2026-10-04 — E151 chronology remediation

E151 has been corrected: expiry-day timestamps must belong to an allowed execution interval, including on disjoint special-session days. The contract-master horizon is now tied to the documented session-data horizon of 2026-07-02.

An automated E150/E151 impact scan is included in the production workflow. No production P&L is relabelled or finalized; final inference remains blocked until the impact question is quantitatively closed and independently audited.


## 2026-10-04 — E151 remediation

The independent E150 audit found a second chronology defect: special sessions with disjoint execution intervals were being treated as a single endpoint rather than explicit interval membership. The remediation now rejects timestamps inside non-trading gaps and fails closed beyond the session-rule evidence horizon of 2026-07-02.

A deterministic old-vs-corrected E150/E151 impact scan is now part of the production workflow. Any affected contract group blocks production inference and requires affected scenario reruns. No profitability/trading-strategy conclusion is final.
