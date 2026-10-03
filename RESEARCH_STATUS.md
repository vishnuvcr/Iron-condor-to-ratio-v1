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


## 2026-10-03 — Independent tester E046 final-head re-audit
- Final-head CI evidence is independently verified: run `37125656878`, job `111210327724`, head SHA `09c4c2e4b6bc569d42d4743fac5132ad0672f8d8`, artifact `11275311823`, artifact SHA-256 `754a71a1b50f532b49e43be45f24ddc3eab80a4aa56df1f43b23f0030f04aa9c`.
- G12 is therefore independently PASS for the exact final developer head.
- G4 remains FAIL/OPEN under E046: `scripts/phase1_session_reconciliation.py` only iterates observed dates, so a special-session date declared in the control manifest but missing from the observed dataset is never reconciled and cannot fail the run. The implementation also does not perform the session-calendar specification's required one-to-one calendar join for every observed date; unrecognised observed dates can fall through to the generic normal-session rule.
- Phase 1 remains IN PROGRESS. G13 and Phase 2 remain BLOCKED. No backtest engine, optimization, profitability analysis, or trading conclusion has begun.
- Tester report: `research/TESTER_REPORT_PHASE1_G4_FINAL_REAUDIT.md`. Tester branch: `tester/phase-1-g4-final-reaudit`.