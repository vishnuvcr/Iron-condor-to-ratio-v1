# Research Status

Updated: 2026-10-03

| Phase | Status | Gate |
|---|---|---|
| 0 Specification/audit | COMPLETE | Seventh independent tester PASS |
| 1 Data | IN PROGRESS | Pinned-source validation and acceptance gates |
| 2 Engine | BLOCKED | Phase 1 independent tester approval |
| 3 Experiments | BLOCKED | Phase 2 |
| 4 Statistics | BLOCKED | Phase 3 |
| 5 Interpretation | BLOCKED | Phase 4 |
| 6 Manuscript/release | BLOCKED | Phase 5 |

## Phase 1 current state
- Primary source: thetrademarkk/india-index-options-1m.
- Source revision is pinned to immutable Hugging Face commit 0f4800e.
- Prior structural acquisition on mutable main downloaded 269 parquet files and passed corrected structural validation; it remains historical evidence only.
- Production workflow now uses the pinned revision and separate cache restore/save steps.
- Historical bid/ask is not documented in the primary source; execution is currently classified as degraded unless an independent historical quote source is validated.
- NSE contract-rule changes and Paytm Money date/cohort-dependent costs have been externally reconciled at source-review level.
- Interim acceptance report: research/PHASE1_ACCEPTANCE_REPORT.md.
- Independent tester PR #25 closed E055 PASS; this does not close G13 because G5–G11 remain incomplete.
- No backtest engine, optimization, or profitability conclusion has started.

## Open Phase 1 gates
1. Re-run structural validation against the pinned revision and record immutable file provenance.
2. Quantify timestamp/coverage gaps, missing bars and stale observations.
3. Quantify underlying/option timestamp alignment.
4. Reconstruct Greeks under the frozen Phase 0 IV/Black-Scholes contract and report solver success/failure.
5. Quantify target-delta strike availability under the frozen ±0.05 tolerance and liquidity rules.
6. Reconcile historical expiry, lot-size and tick-size metadata against effective-date NSE references.
7. Reconcile date-specific Paytm Money brokerage and statutory/exchange charges.
8. Collect and align contextual regime variables: NIFTY, India VIX, FII/FPI, DII, GIFT NIFTY/overnight, global risk/volatility, NSE/BSE and relevant events.
9. Obtain independent tester PASS for the final Phase 1 branch.

## Pinned-source structural audit
- Successful run: 37116400642; job 111183955555; artifact 11271442031.
- Artifact SHA-256: 137396eab20370bbbf2285cbc684f7db1e1693d0b3a88f7c64f77a2e8ea967d0.
- 109,112,358 rows across 269 files were audited; 0 hard-failure files and 0 conflicting duplicate-key groups.
- 30,363,281 exact duplicate rows occurred across 138 files, so deterministic deduplication is now a mandatory production-data step.
- No bid/ask fields were observed in the primary-source schema.
- The acquisition scope has been narrowed from index/*NIFTY*.parquet to index/NIFTY.parquet; a fresh validation run is required.

## Phase 1 evidence
- Prior structural validation commit: 5f701e329c7888e5ccd5cfe70cea0f5c14e452ac.
- Prior successful run: 37116084761; job 111183065244.
- Prior artifact: 11271990517; SHA-256 67fd3898800131d736a5652d1ece3c112c4b5b0489ffe07468f5865fb850d789.
- Current corrected workflow run: 37116328987.

## Latest controls
- Deterministic exact-row deduplication is implemented in scripts/deduplicate_phase1_data.py and is executed in CI after structural validation.
- Conflicting duplicate keys remain fatal.
- Workflow concurrency/cache-save race mitigation was added after E025.
- Phase 1 remains IN PROGRESS. Run 22 failed only because the market-quality audit script contained malformed literal escape sequences (E029); structural validation and deterministic deduplication passed. The script has been repaired in commit 336c8e8ddf5de93f31ef6b114e621747ae956620 and a clean rerun is required.
- No Phase 2 work has started.

- Added `scripts/phase1_market_quality_audit.py` and CI execution for deterministic timestamp-alignment, coverage-gap sampling, and Black-Scholes/IV solver feasibility diagnostics. This does not close G7/G8; production Greeks still require the frozen date-specific r/q and liquidity rules.

- Run 21 completed successfully. Structural validation and deterministic deduplication passed; 77,776,166 option rows remain after key-level deduplication in the market-quality audit, with 99.295% of option rows timestamp-aligned to the NIFTY index. However, NIFTY daily timestamp counts range from 6 to 420, so session outliers must be characterized before acceptance (E028).


## Phase 1 continuation — latest controls
- Run 22 (37118147417) failed at the market-quality audit due to E029; structural validation and deterministic deduplication completed successfully.
- Repair commit: 336c8e8ddf5de93f31ef6b114e621747ae956620.
- Pull request #13 was opened to trigger the pull-request validation path, but no status checks were emitted because repository-token-created events do not retrigger Actions in this environment. The CI workflow remains configured with manual dispatch and PR triggers; no Phase 1 acceptance claim is made from the unexecuted repaired job.
- Official NSE Historical Order & Trade Data is now the preferred quote-source escalation candidate. It is a paid product and remains unacquired.
- Phase 1 remains IN PROGRESS; Phase 2 remains BLOCKED.


- Static syntax verification of the repaired session-outlier block passed locally. Full repository CI execution of the repaired script remains unverified because no new Actions status was emitted from the API-created PR/commits.


## Phase 1 continuation — 2026-10-03
- Run 22 artifact was inspected: structural validation and deterministic deduplication artifacts were produced, but the market-quality audit did not run because of E029.
- Open-source/commercial source search did not identify a public historical NIFTY 1-minute bid/ask dataset satisfying the frozen midpoint requirement. NSE Historical Order & Trade Data is the preferred procurement candidate.
- Phase 1 tester handoff updated with the remaining acceptance checklist and explicit quote-data decision gate.
- Phase 2 remains BLOCKED pending independent tester PASS.


- Date-specific risk-free source: RBI Weekly Statistical Supplement 91-day Treasury-bill primary yield series is validated as an official historical source; complete date-aligned extraction remains an open acquisition task.
- Paytm Money chronology is now supported by official Paytm Money publications: ₹20/order for new users from 25-Aug-2023, flat ₹20 across segments from 15-Jan-2025, and option-sale STT increase from 01-Oct-2024. These are source facts, not yet the complete statutory charge table.
- Historical NIFTY lot/expiry rules are supported by official NSE circulars; production contract metadata must use effective-date rules rather than current specifications.

- Added research/PHASE1_GATE_MATRIX.md with G1–G14 acceptance states; no Phase 2 work is permitted until the independent tester PASSes.


- **E033 normalization:** the independent tester found ambiguous G1–G10 meanings across Phase 1 documents. Canonical G1–G14 definitions are now authoritative in `research/PHASE1_GATE_MATRIX.md`, `research/PHASE1_DATA_SPEC.md`, `research/PHASE1_ACCEPTANCE_REPORT.md`, and `research/TESTER_HANDOFF.md`. Phase 1 remains FAIL/IN PROGRESS; Phase 2 remains BLOCKED.

## 2026-10-03 — Substantive gate progression after E033
- E033 documentation-control defect is closed by independent re-audit.
- G4–G12 are now being treated as substantive evidence gates, not documentation gates.
- Added `research/PHASE1_PRODUCTION_EVIDENCE_PLAN.md` specifying the machine-readable evidence required for each gate.
- External NSE review established that historical F&O session timing must be date-specific; current 15:40 closing time cannot be applied retrospectively. citeturn1search2turn2search0turn2search3
- GitHub Actions evidence for repaired commit 336c8e8 reports zero associated workflow runs, so G12 remains OPEN.
- G4, G5, G6, G7, G8, G9, G10 and G11 remain OPEN/BLOCKED. G13 remains blocked pending independent tester PASS; G14 remains blocked.
\n## 2026-10-03 — Phase 1 control-source formalization\n- Added `research/PHASE1_SESSION_CALENDAR_SPEC.md` defining date-specific NSE session reconciliation for G4. Current 15:40 hours are explicitly reference-only and cannot be projected backward.\n- Added `research/PHASE1_CONTRACT_COST_SPEC.md` defining effective-date NIFTY contract metadata and date/cohort-specific Paytm Money/statutory cost inputs for G8/G10.\n- Added `research/PHASE1_QUOTE_DATA_PROCUREMENT.md` formalizing G9's procurement decision: historical bid/ask or deterministic order-level reconstruction is required; close-price substitution remains rejected.\n- Added `data/manifests/phase1_control_sources.json` and `scripts/validate_phase1_control_manifests.py` for control-plane source validation.\n- Updated Phase 1 CI syntax/control checks to include the new validator.\n- External evidence: NSE's historical order/trade product covers F&O; NSE documents current F&O hours of 09:15–15:40; NIFTY lot size and expiry rules changed by effective-date circulars; RBI publishes 91-day T-bill primary yields; Paytm Money documents brokerage/STT transitions. These close source-identification questions only; production gates remain open.\n- G4–G12 remain OPEN/BLOCKED as previously recorded. No Phase 2 work has started.\n
## 2026-10-03 — E035 control correction
- Synchronized G1 to PASS across the acceptance report and canonical gate matrix.
- Removed unused hard-coded session constants from the market-quality diagnostic; G4 is governed exclusively by date-specific NSE session metadata.
- Logged E035. No Phase 2 work or gate advancement occurred.

## 2026-10-03 — Data-gathering pass
- Added `data/manifests/phase1_data_inventory.json` separating previously CI-acquired primary data from sources still requiring machine-readable acquisition.
- Primary immutable HF source remains revision `0f4800e`; prior NIFTY-only acquisition evidence covers 268 files and 108,625,497 rows, with 30,363,281 exact duplicates and no conflicting duplicate-key groups. No bid/ask fields were present.
- Official NSE historical F&O order/trade data remains identified but not acquired because it is a paid/procurement-controlled product.
- Reopening PR #13 was attempted to obtain a fresh Actions acquisition/audit run; the workflow-run query still returned zero runs. This is recorded as an execution-environment limitation, not a data-validation PASS.
- G4–G12 remain open/blocked and Phase 2 remains blocked.


## 2026-10-03 — Independent tester E037 correction
- Independent tester result: Phase 1 FAIL / IN PROGRESS; Phase 2 BLOCKED.
- E037 identified a workflow command-block defect in the Phase 1 syntax-check step. The second command was not a separate shell command.
- Corrected in commit `fb5993afa89cfce7fac177d1a62c45e98bddbc27` using an explicit multiline `run: |` block.
- G12 remains FAIL/OPEN pending an independently verifiable successful Actions run of the corrected workflow. G13/G14 remain blocked.


## 2026-10-03 — Developer execution attempt after E037
- Attempted to trigger the corrected Phase 1 workflow by committing a workflow-only comment to the active branch (`70baca4a23649ec58cb30e2e91a6747f3f2d8267`).
- GitHub Actions workflow-run lookup returned zero runs for that commit.
- Logged E038. This confirms the current GitHub connector cannot independently cause the required Actions execution in this repository/session.
- G12 remains FAIL/OPEN; G13/G14 remain blocked; no Phase 2 work started.


## 2026-10-03
2026-10-03 — G12 UI correction: The Phase 1 workflow was not present on main, which explains the missing Run workflow control. The workflow was added unchanged to main at commit 25f43daf258add201adf0efc67ea9d58c682ed38. G12 remains unexecuted until a dispatch is actually initiated; no Phase 2 work has begun.


## 2026-10-03 — G12 run #32 diagnosis and correction
- Manual Actions run #32 was visibly started on `main` and failed after 22 seconds.
- Root cause identified from repository layout: `main` contains the dispatch wrapper workflow, while Phase 1 scripts/manifests remain on `phase-1-data-acquisition-validation`.
- Corrected both workflow copies to accept `research_ref` for manual dispatch, defaulting to `phase-1-data-acquisition-validation`, and to checkout that ref. Push events continue to checkout `github.ref`.
- G12 remains OPEN pending an actual successful Phase 1 execution and artifact evidence.


## 2026-10-03 — G12 run 37122653828 / E041
- The corrected branch-targeted CI executed as run `37122653828`, job `111201667259`.
- Dependency installation passed; the syntax-check step failed because `scripts/validate_phase1_control_manifests.py` was missing from the checked-out Phase 1 branch.
- The file existed on `main`; this was a branch synchronization defect.
- Restored the validator unchanged to the Phase 1 branch at commit `68b39d91035bcb79c192cac80f20fd29ed6e709d`.
- G12 remains OPEN pending the next execution.


## 2026-10-03 — Successful Phase 1 CI execution / G12 PASS
- Successful run `37122686454`, job/check `111201763817`, head commit `68b39d91035bcb79c192cac80f20fd29ed6e709d`.
- Artifact `11274027306`, SHA-256 `329eb437e42745f5613e7c41bdf33313977b09d49492513a190d3c1216f01980`.
- Fresh evidence: 268 files, 108,625,497 raw rows, 0 hard failures, 30,363,281 exact duplicates removed deterministically, 77,776,166 option rows after key dedup, 99.2953047% option/NIFTY timestamp alignment, 286 session-count diagnostic outliers among 1,262 dates.
- G12 is now PASS on developer evidence.
- G4 remains OPEN; G5 remains PRELIMINARY; G6–G8, G10–G11 remain OPEN; G9 remains BLOCKED; G13 remains BLOCKED pending independent tester PASS; G14 remains BLOCKED.


## 2026-10-03 — G4 session reconciliation
- Added dated NSE session controls and a pre-registered incomplete-session exclusion rule.
- Successful run `37124047220` / job `111205697146`; artifact `11274239403`.
- Reconciliation result: 1,254 normal eligible dates, 7 documented special sessions, 1 data-gap exclusion on 2026-06-03, 0 unreconciled dates.
- G4 is PASS on developer evidence; independent tester verification remains required.
- G9 remains BLOCKED; G6/G7/G8/G10/G11 remain OPEN; G13/G14 remain blocked.

## 2026-10-03 — E044/E045 correction
- Independent tester re-audit: Phase 1 FAIL / IN PROGRESS; Phase 2 BLOCKED.
- E044 accepted: unresolved-date manifest entries were not consumed and special-session intervals were not actually validated.
- E045 accepted: run 37124047220 was not on the current branch head, so it cannot be final-head CI evidence.
- Replaced unresolved_dates with explicit date_controls and formal special-session execution_intervals + source_observation_intervals.
- Reconciliation now fails on any uncontrolled date, date-control classification mismatch, missing special execution interval coverage, or observation outside documented source windows.
- G4 is back to OPEN pending fresh final-head CI and independent tester review.
- G12 is OPEN for final-head evidence. G13/G14 remain blocked.

## 2026-10-03 — E044 implementation frozen for final-head CI
- Corrected G4 manifest/reconciler/validator now enforce explicit date controls and special-session interval validation.
- Special-session source-observation schedules are pinned to NSE capital-market circulars in addition to F&O execution circulars.
- Prior run 37125014956 successfully exercised the corrected logic on an ancestor commit and produced 1,254 normal eligible dates, 7 reconciled special sessions, 1 data-gap exclusion, and 0 unreconciled dates; this is diagnostic evidence only because E045 requires final-head execution.
- Final-head CI is the next required evidence step; no gate is advanced from the prior run.


## 2026-10-03 — E046
- Independent tester re-audit of final-head CI confirmed G12 PASS for head 09c4c2e4b6bc569d42d4743fac5132ad0672f8d8 (run 37125656878, job 111210327724, artifact 11275311823, SHA-256 754a71a1b50f532b49e43be45f24ddc3eab80a4aa56df1f43b23f0030f04aa9c).
- Tester found the G4 reconciler was not fail-closed for manifest-only dates because it iterated only over observed dates. This violated the repository's one-to-one session-calendar reconciliation contract.
- Resolution: created corrective branch phase-1-e046-bidirectional-reconciliation; refactored reconciliation into a bidirectional manifest/observed-date join, added unique mapping validation and fail-closed unknown-date handling, and added four regression tests.
- Impact: G4 is FAIL/OPEN and G12 must be re-established on the corrective branch head. G13/G14 remain blocked. No Phase 2 work or performance analysis has begun.


## E046/E047 corrective status — 2026-10-03
- E046 bidirectional reconciliation is now exercised on exact corrective head 4099cd1217f072be961f120ab114034578e19197.
- Exact-head Actions run: 37129894485; job 111222750604; artifact 11275819920; artifact SHA-256 57cdcc53ec350fea1ce398f1130d5dd66beb63cdc0b481485e2b0e4fe3d54178.
- Reconciliation artifact reports 1,262 observed dates, 13 manifest control dates, 1,251 normal-eligible dates, 10 special-session dates, 1 data-gap exclusion, 0 unreconciled dates, and 0 missing manifest-session dates.
- E047 recorded the three genuine weekend live-trading dates discovered by the fail-closed exact-head rerun: 2024-01-20, 2025-02-01, and 2026-02-01. They are now explicitly controlled in the session manifest with dated exchange-source references.
- Current Phase 1 status: IN PROGRESS / NOT APPROVED. G4 and G12 have developer evidence on the current corrective head, but G13 is still BLOCKED pending independent tester re-audit. G5–G11 remain as previously stated; Phase 2 remains BLOCKED.


## E048 manual-dispatch safeguard — 2026-10-03
- The user-provided Actions UI showed manual run #52 queued from the `main` workflow entry.
- Inspection of the `main` workflow revealed its manual-dispatch default still pointed to the older acquisition branch and omitted the E046 bidirectional G4 reconciliation step.
- The `main` workflow has now been replaced with the E046-corrected workflow; main workflow commit: 097d29c2816614bc7ba45365454b7f0dc270bc5d.
- Run #52 is not automatically accepted as G12 corrective evidence unless its explicit `research_ref` input selected `phase-1-e046-bidirectional-reconciliation`. The screenshot does not expose that input.
- Current status remains Phase 1 IN PROGRESS / NOT APPROVED; G13 and Phase 2 remain BLOCKED.


## E050 automatic corrective CI execution — 2026-10-03
- CI safeguard commit: `59e025ff0050fb30d2a43928aad02f3a63277a0b`.
- The workflow now fails closed on push if the execution branch is not `phase-1-e046-bidirectional-reconciliation`.
- A protected automatic run is triggered by the workflow change and again by this execution-record commit. The final branch-tip run must be inspected for exact checkout SHA, complete step success, and G4 reconciliation results before G12 is accepted.
- G13 and Phase 2 remain blocked.


## 2026-10-03 — E051 exact-tip CI control
- Repository control files were re-read before continuation; Phase 1 remains IN PROGRESS and Phase 2 remains BLOCKED.
- The prior documentation tip 7a0b43b81d6b69165d745527f639de94ee5a62ad was not itself a workflow-path change, so it is not valid exact-tip CI evidence.
- The workflow was deliberately touched in commit b6e8ff93edfd2d3e5f1797d0d1d2ed186189d512 to force the corrected push trigger while preserving the same validation logic.
- Current branch tip: b6e8ff93edfd2d3e5f1797d0d1d2ed186189d512.
- Current GitHub commit status: pending, zero published statuses. The available repository connector does not expose the push-triggered run list for this commit.
- Therefore G12 is NOT advanced. The required evidence remains an observable Actions run with checkout SHA equal to the exact branch tip, successful G4 reconciliation/artifact, and subsequent independent tester PASS.
- No Phase 2 engine, optimization, profitability analysis, or strategy conclusion has been started.


## E052 — 2026-10-03 — co-commit exact-tip execution control
- To prevent documentation-only commits from moving the research head after a workflow-trigger commit, the final control/documentation update is being co-committed with the workflow marker.
- This commit is intended to be the exact current-head candidate for automatic Phase 1 CI. No G12 PASS is claimed until an observable Actions run proves the checkout SHA and completes all validation steps.


## 2026-10-03 — E053 control-plane synchronization and tester Run #55 result
- Independent tester PR #20 independently verified the immutable Run #55 evidence on exact developer tip `378a130b6d450b288be140655f9b0b75aad840b3`.
- G4 = PASS independently; G12 = PASS independently.
- G13 remains BLOCKED because G5–G11 are not all production-accepted; G9 is specifically BLOCKED pending historical bid/ask or sufficient order-level reconstruction data.
- E053 was identified as stale top-level status text in the README/gate/acceptance/handoff controls. This developer branch synchronizes the canonical current-state sections while retaining historical run-specific evidence as append-only traceability.
- Phase 1 remains IN PROGRESS / NOT APPROVED. Phase 2 remains BLOCKED. No backtest, optimization, profitability result, or strategy conclusion has been introduced.
- Official NSE historical-data specification review confirms that F&O order data are all-order-tick records with transaction time, buy/sell indicator, entry/cancel/modify activity, contract identity, order quantity and limit price; the corresponding F&O trade data include transaction time, contract identity, trade price/quantity and buy/sell order numbers. This makes the NSE order/trade product a technically plausible reconstruction route, but acquisition and validation are still required before G9 can move from BLOCKED. citeturn1view0turn2view0


## 2026-10-03 — E053 control-plane synchronization and tester Run #55 result
- Independent tester PR #20 independently verified the immutable Run #55 evidence on exact developer tip `378a130b6d450b288be140655f9b0b75aad840b3`.
- G4 = PASS independently; G12 = PASS independently.
- G13 remains BLOCKED because G5–G11 are not all production-accepted; G9 is specifically BLOCKED pending historical bid/ask or sufficient order-level reconstruction data.
- E053 was identified as stale top-level status text in the README/gate/acceptance/handoff controls. This developer branch synchronizes the canonical current-state sections while retaining historical run-specific evidence as append-only traceability.
- Phase 1 remains IN PROGRESS / NOT APPROVED. Phase 2 remains BLOCKED. No backtest, optimization, profitability result, or strategy conclusion has been introduced.
- Official NSE historical-data specification review confirms that F&O order data are all-order-tick records with transaction time, buy/sell indicator, entry/cancel/modify activity, contract identity, order quantity and limit price; corresponding F&O trade data include transaction time, contract identity, trade price/quantity and buy/sell order numbers. This makes the NSE order/trade product a technically plausible reconstruction route, but acquisition and validation are still required before G9 can move from BLOCKED. 


## 2026-10-03 — G9 open-data screening extension
- Hugging Face screening found `rissin/nse-options-intraday` and `artist-23/nifty-options-data` as additional NIFTY option datasets. They provide historical/intraday OHLC/IV/OI-type data but do not establish the required historical bid/ask series for the complete study window.
- The public GitHub ecosystem also contains pipelines with bid/ask-shaped schemas or execution modelling, but the underlying historical quote files are not retained/validated for this study.
- These sources are recorded as non-qualifying alternatives. The official NSE historical F&O order/trade product remains the preferred G9 acquisition route.
- G9 remains BLOCKED pending licensed acquisition and deterministic validation/reconstruction.

## 2026-10-03 — E054 README branch provenance correction
- Independent tester PR #22 found the README's current branch identifier was stale relative to developer PR #21.
- Created `phase-1-e054-readme-branch-provenance` from exact audited head `4f7186c4d2478bdd83f86f0bb35547f4c8594fbc`.
- Corrected only the README branch provenance and recorded E054 in the error/status controls.
- No gate result changed: G4/G12 remain independently PASS; G5–G8/G10–G11 remain open/preliminary; G9 remains blocked; G13/G14 and Phase 2 remain blocked.

## 2026-10-03 — E055 E054-audit SHA provenance correction
- Independent tester PR #24 found a malformed SHA in the E054 entry of `CONVERSATION_LOG.md` for the audited PR #21 developer head.
- Corrected SHA: `4f7186c4d2478bdd83f86f0bb35547f4c8594fbc`.
- This is a reproducibility/control correction only; no methodology or gate result changed.
- Current developer branch remains `phase-1-e054-readme-branch-provenance`; the resulting exact developer head is submitted for independent tester re-audit.
- G1–G3 remain PASS; G4/G12 remain independently PASS; G5–G8/G10–G11 remain open/preliminary; G9 remains BLOCKED; G13/G14 and Phase 2 remain BLOCKED. No Phase 2/backtest/optimization/profitability work has started.

## 2026-10-03 — G5–G11 substantive source audit
- Added `research/PHASE1_G5_G11_SOURCE_AUDIT_20261003.md`.
- Re-verified official RBI 91-day Treasury Bill Primary Yield sources, NSE NIFTY contract transitions through 2025, NSE Historical Order & Trade availability/schema/tariff evidence, Paytm Money brokerage/STT chronology, India VIX, NIFTY historical index data, FII/FPI-DII and GIFT NIFTY/NSE IX context.
- Expanded `data/manifests/phase1_control_sources.json` and the G8/G9 control specifications.
- No gate result changed: G5 preliminary/open; G6-G8 open; G9 blocked; G10-G11 open; G13/G14 and Phase 2 remain blocked.
- No backtest, optimization, profitability analysis, or trading conclusion has started.

- New G9 candidate `antony9952/Nifty_option_TBT` exposes bid/ask/depth fields but has a published mixed-schema warning. Added an automated cached candidate-audit workflow with manual dispatch and automatic push/PR triggers. G9 remains BLOCKED until raw-file coverage, NIFTY identity, timestamp quality and quote reconstruction are validated.


## 2026-10-03 — Tester-prescribed G9 free-data salvage
- Tester PR #27 formally handed off the next G9 acquisition order: salvage antony9952/Nifty_option_TBT, investigate ayyararyan/nse-options-pipeline, inspect OptionVault/TickBytes, inspect retained archives from other NSE option collectors, apply one common validator, then use NSE Historical F&O Order & Trade if no free source qualifies.
- Created research/PHASE1_G9_FREE_DATA_SALVAGE.md and expanded data/manifests/phase1_sources.json with the candidate set and acceptance contract.
- Web/source review confirms ayyararyan/nse-options-pipeline documents bid/ask-bearing NSEI-Data files but does not track the raw archive; OptionVault and TickBytes distinguish public samples from licensed full datasets; BarathGB007/nse-options-data-collector has bid/ask-bearing current/sample schemas but does not establish a complete historical archive.
- A local attempt to retrieve the 378 MB antony9952/Nifty_option_TBT archive failed because the runtime could not resolve huggingface.co; this is logged as E058. No inferred quote data were created.
- G9 remains BLOCKED. G13/G14 and Phase 2 remain BLOCKED.

## 2026-10-03 — G9 exact-head CI and raw-file validator hardening
- Developer submission before this continuation: `d2003df53d07a952aa7434c4c706f396067b6080`.
- Exact-head PR workflow lookup returned no run. This is recorded as an execution/connector limitation; it is not evidence against the candidate dataset.
- G9 validator now audits every acquired raw CSV independently and emits an acquisition-failure report rather than losing the diagnostic when network/DNS acquisition fails.
- G9 workflow now uses the current salvage branch, immutable candidate revision in cache keys, PR path coverage, cache restore/save, and unconditional audit-artifact upload.
- G9 remains BLOCKED. No Phase 2/backtest/performance analysis has started.

## 2026-10-03 — E063 bid/ask-free execution methodology proposal
- Developer formally changed the primary methodology to a proxy-execution model rather than requiring historical bid/ask.
- Specification: `research/PHASE1_EXECUTION_PROXY_SPEC.md`.
- Frozen convention: completed 1-minute decision bar -> next eligible 1-minute option-bar open; adverse per-leg slippage at 0/5/10/20/50 bps with date-effective tick floor; date-effective transaction costs; no interpolation or OHLC/LTP-to-bid/ask relabeling.
- This is a methodology change, not a G9 PASS.
- G9 remains BLOCKED pending independent tester approval of the revised methodology and validation of the proxy data/execution controls.
- G13/G14 and Phase 2 remain BLOCKED.

## 2026-10-03 — E064 documentation correction
- Corrected formula rendering in `research/PHASE1_EXECUTION_PROXY_SPEC.md`.
- The slippage methodology itself is unchanged: adverse 0/5/10/20/50-bps scenarios with an effective-date one-tick floor.
- This is a documentation/control correction only. G9 remains blocked pending independent tester approval of the methodology change; Phase 2 remains blocked.

## 2026-10-03 — E065/E066 execution-proxy correction
- Independent tester PR #30 identified two blocking defects in the proposed bid/ask-free methodology: E065 (underspecified missing-next-bar multi-leg state handling) and E066 (sell-side slippage could manufacture a zero-price fill).
- Corrective branch: phase-1-execution-proxy-e065-e066.
- E065 correction: adjustment orders are atomic; any missing/invalid leg causes the entire group to fail, preserves the pre-adjustment state, consumes the trigger, and requires trigger exit/re-entry before another adjustment can be generated. Expiry/session boundaries cannot be crossed to manufacture a fill.
- E066 correction: sell fills are P_base - S(P_base) and are rejected when non-positive; zero-price clipping is prohibited. Buy fills also require positive base/fill prices.
- Added scripts/test_phase1_execution_proxy_rules.py and manual/push/PR CI workflow for regression tests.
- Tester approval has not yet been granted. G9/G13/G14 and Phase 2 remain BLOCKED. No backtest or profitability analysis has started.

## 2026-10-03 — Independent G9 approval
Tester PR #32 independently re-audited developer PR #31 at exact head `8b99cb3b2b537c5b085c09729c27bb3957285ae8`. G9 is now **PASS under the revised bid/ask-free proxy methodology**. E065 and E066 are PASS. Historical bid/ask is not mandatory for the primary backtest and OHLC/LTP is never relabeled as executable quotes. G13/G14 and Phase 2 remain BLOCKED because G5/G6/G7/G8/G10/G11 remain incomplete. No Phase 2 backtest or profitability analysis has started.


## 2026-10-03 — G5 underlying/option alignment step
- Developer continued under the independent-tester gate after G9 PASS; Phase 2 remains BLOCKED.
- Created branch `phase-1-g5-underlying-option-alignment` from the synchronized G9-pass developer head.
- Added `research/PHASE1_G5_ALIGNMENT_SPEC.md`, `scripts/phase1_g5_alignment_audit.py`, and `.github/workflows/phase1-g5-alignment.yml`.
- The G5 validator separates session eligibility from underlying alignment, requires exact timestamp matching to the NIFTY grid, rejects duplicate NIFTY timestamps and invalid option timestamps, reports expiry/day coverage, and never interpolates or forward-fills.
- G5 remains OPEN pending an exact-head Actions run and independent tester re-audit. No Phase 2/backtest/profitability work has started.

- After PR #34 creation, the available GitHub Actions run lookup returned zero PR-triggered runs for exact head `990f450a52e50bb9b62f2444aa015b5989087cf3`; logged E069. This is an execution-observability limitation, not a G5 data result. G5 remains OPEN.


## 2026-10-04 — E071 G5 validator correction
- Static audit found a report-construction defect in the G5 expiry/day coverage section.
- Corrected `in_session` references to the actual `decision_eligible` field at commit `7039818d199566dd18c4d884797d43f3851bfc78`.
- No G5 PASS is claimed; exact-head CI evidence and independent tester review remain required.

## 2026-10-04 — Tester PR #36 and E073 G5 provenance correction
- Independent tester PR #36 returned Phase 1 FAIL / IN PROGRESS.
- G5 exact head `3225d29902a20c958bf8c9803479e8fbe7601dbf` had zero observable workflow runs/statuses; no G5 acceptance was claimed.
- Tester also required manual-dispatch artifact provenance to bind explicitly to the checked-out commit.
- Developer correction branch `phase-1-g5-e071-ci-provenance-hardening` records the checkout SHA inside `phase1_g5_alignment_report.json` and verifies it in CI; manual dispatch accepts an optional exact expected commit SHA.
- G5 remains OPEN. G13/G14 and Phase 2 remain BLOCKED.

## 2026-10-04 — E075 stale G9 wording correction
- Repository control review found superseded G9-blocked wording in the canonical gate matrix after Tester PR #32 had already approved G9.
- Corrected the current/historical control wording without changing the underlying methodology.
- G9 remains PASS under the revised proxy methodology; G5/G6/G7/G8/G10/G11 remain open; G13/G14 and Phase 2 remain blocked.

## 2026-10-04 — Tester PR #39 / developer response
- Tester PR #39 remains controlling: G5/G6 FAIL/OPEN; G9 PASS; G13/G14 and Phase 2 BLOCKED.
- Created correction branch `phase-1-g5-g6-reaudit-corrections-20261004`.
- G5 workflow push trigger now includes the active correction branch; workflow_dispatch default ref now points to the correction branch for explicit testing.
- G6 acquisition now reuses existing retained source files on cache/local hits rather than unconditionally downloading every source; G6 workflow also triggers on the correction branch and supports exact manual expected-commit checking.
- Full G6 r/q production reconstruction and G5 exact-head Actions evidence remain pending independent tester verification.

## 2026-10-04 — Tester PR #40 / G6 cache integrity correction
- Tester PR #40 confirms G5/G6 OPEN, G9 PASS, and Phase 2 BLOCKED.
- G6 correction now rejects cache hits unless an immutable expected SHA-256 is explicitly supplied and matches the cached bytes; mismatches or missing digests fail closed.
- No fabricated or placeholder digest is used as acceptance evidence.
- G6 still requires full date-aligned r/q, no-lookahead validation, production IV/Greek reconstruction, delta distributions, solver diagnostics, target-delta availability and reproducibility checks.

## 2026-10-04 — G6 provenance bootstrap and exact-tip CI evidence
- A one-time non-accepting bootstrap run acquired five registered source pages and produced observed SHA-256 digests; those exact observed digests were committed to `data/manifests/phase1_control_sources.json`.
- The G6 cache-integrity regression tests passed in CI.
- Exact-tip G6 run **37148353717** succeeded at developer commit `e8fca6a6084a463528643b63dd8f310899c0b3bf`; artifact **11282958617**, digest `sha256:bdb21f11285b16535f3ea6338bbf9bff3afe717f6ef727575642f0aaba4d6d11`.
- This is acquisition/provenance evidence only and does not close G6 substantive requirements.
- Exact-tip G5 run **37148384171** is currently executing at commit `001e498bfc099e9f51df9129e1fdc2e9370b2b3a`; no G5 result is claimed until completion and independent review.

## 2026-10-04 — G6 substantive reconstruction implementation started
- Created branch `phase-1-g6-production-greeks-20261004` from paired exact-tip SHA `db668dd2b89bf691a6481affb3cb2a9060c5fe98`.
- Added the fail-closed G6 production Greek specification, implementation script, and dedicated GitHub Actions workflow.
- The specification covers strict no-lookahead r/q selection, Black-Scholes IV, signed/absolute delta, solver diagnostics, target-delta availability, expiry/date coverage and checksums.
- G6 remains OPEN; G13/G14 and Phase 2 remain BLOCKED.


## 2026-10-04 — G6 production continuation
- G6 production branch: phase-1-g6-production-greeks-20261004.
- Corrected E084: reference-data coverage is now measured against unique trading dates observed in production NIFTY option bars, rather than against the q reference table itself.
- Public-source audit confirms the official NSE Indices historical interface exposes daily P/E/P/B/Dividend Yield, and a public technical reference documents the underlying historical valuation endpoint and its 365-day pagination constraint. RBI WSS independently exposes the required 91-Day Treasury Bill (Primary) Yield field. These are acquisition leads only; no substitute q/r values have been accepted.
- G6 remains OPEN; production IV/delta reconstruction is not yet complete and independent tester approval remains mandatory.


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


## 2026-10-04 — Automatic tester handover / E104 correction
- Tester PR #47 independently failed G6/Phase 1 and identified E104: RBI cache reuse was not actually implemented despite the cache path, and availability-date semantics were insufficiently explicit.
- Developer correction committed on the active G6 branch: cache-hit pages now require sidecar SHA-256 validation and known bootstrapped pages additionally require immutable expected SHA-256; retained files without provenance fail closed.
- G6 no-lookahead semantics were clarified: the RBI labelled observation date is a conservative eligibility date, never a claim of exact publication time; strict-prior excludes same-day observations.
- Added regression coverage for same-day exclusion.
- G5 remains FAIL/waived for continued research; G6 remains OPEN pending fresh exact-head CI and independent tester re-audit; G9 remains PASS; G13/G14 and Phase 2 remain BLOCKED.


## 2026-10-04 — E105 bounded RBI acquisition correction
- Exact-head G6 CI run `37171349785` remained in the RBI acquisition step long enough to expose an operational acquisition bottleneck.
- Developer corrected the acquisition bounds/concurrency: WSS IDs 24000–28500, 100 workers, 3-second request timeout.
- No provenance, target-series, duplicate/conflict, or no-lookahead rule was relaxed.
- The prior exact-head run is non-authoritative because downstream evidence was never reached; fresh CI at the corrected head is required.
- G6 remains FAIL/OPEN pending fresh CI and independent tester re-audit. G5 remains FAIL/WAIVED; G9 PASS; G13/G14 and Phase 2 BLOCKED.


## 2026-10-04 — E106 RBI bootstrap-first correction
- The RBI collector now tries the four independently identified official WSS IDs first, using their immutable expected SHA-256 provenance, and invokes the wide archive scan only if those candidates produce no rows.
- This is an execution-performance correction only. G6 remains FAIL/OPEN because the corrected head still requires fresh CI evidence and independent tester approval. G5 remains FAIL/WAIVED, G9 PASS, G13/G14 and Phase 2 BLOCKED.
- The workflow was touched to force exact-head revalidation, but the GitHub connector exposed no new workflow run for the corrected commits 5e90927245283c865c9a9a187fb9a3ec43e52dcd or 68c572e471b78009640d0e3aa3717d6a5d899e01; no CI success is inferred.


## 2026-10-04 — Tester PR #48 / E107
- Fresh isolated tester branch tester/phase-1-g6-reaudit-e106-20261004 independently audited developer head b75e64d3f6caf9f086a0c063153ccc6315aa5c5.
- Tester found E106 code-level controls PASS on inspection, but exact-head Actions evidence absent; **G6 = FAIL/OPEN**.
- G5 remains FAIL/WAIVED FOR CONTINUED RESEARCH; G9 PASS; G13/G14 and Phase 2 BLOCKED. Tester requires observable exact-head CI/artifact evidence and fresh re-handover after correction.
