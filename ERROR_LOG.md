# Error Log

| ID | Date | Phase | Error / issue | Impact | Resolution |
|---|---|---|---|---|---|
| E001 | 2026-10-03 | 0 | Target GitHub repository was empty; no prior plan/status/error logs were available. | No inherited research controls or implementation. | Created baseline research-control files and recorded the issue. |
| E002 | 2026-10-03 | 0 | The source strategy requires intraday delta triggers, while NSE public archive pages primarily expose daily/historical report products. | Daily data alone cannot reproduce trigger timing. | Treat intraday option-chain data as a Phase 1 acquisition requirement; do not substitute daily data. |
| E003 | 2026-10-03 | 0 | Video contains discretionary profit-taking/expiry-day decisions and some execution details are not fully deterministic. | A single literal backtest could embed researcher discretion. | Separate deterministic core rules from explicitly tagged discretionary variants. |
| E004 | 2026-10-03 | 0 | Phase 0 literature/data review found public datasets with different coverage, access requirements and licensing; some advertise historical Greeks but full data access is not established. | Risk of using an unverifiable or non-redistributable dataset. | Require provenance, access method, coverage and licensing checks in Phase 1 before primary backtest use. |

| E018 | 2026-10-03 | 0 | Seventh independent tester PASS was not yet synchronized into the main-derived Phase 1 branch at creation time. | Without synchronization, active status could incorrectly keep Phase 1 blocked. | Recorded the tester report/PR #12 approval and activated Phase 1 on `phase-1-data-acquisition-validation`. |
| E019 | 2026-10-03 | 1 | The leading open 1-minute NIFTY option dataset documents OHLCV/OI/strike/type/expiry but not historical bid/ask; a secondary dataset also lacks documented bid/ask. | True historical bid/ask execution cannot be assumed from these sources. | Treat bid/ask as a Phase 1 validation gap; use the frozen literal-core fallback only if no independent quote source is validated, and flag degraded execution data. |

| E020 | 2026-10-03 | 1 | Initial Phase 1 validator incorrectly treated index files as option files and treated all exact duplicate rows as fatal. | The first validation run failed despite successful acquisition, obscuring whether duplicates were exact repeats or conflicting observations. | Rewrote validator with separate index/option schemas and a duplicate-key conflict test; exact duplicates are quality flags, conflicting duplicate keys remain fatal. Corrected validation passed in run 37116084761. |

| E021 | 2026-10-03 | 1 | Primary Hugging Face acquisition used mutable `main` instead of an immutable revision. | A rerun could silently change the production dataset. | Pinned the primary source to Hugging Face revision `0f4800e` and changed the acquisition workflow to use that revision. |
| E022 | 2026-10-03 | 1 | While modernizing the cache workflow, the first edit placed the cache-save step before acquisition. | The intended post-acquisition cache persistence would not occur in that run. | Moved `actions/cache/save@v4` to immediately before validation, after acquisition; the corrected commit is 57a7fa060977d239edf3ea1a1a86c30975c0a25b. |

| E023 | 2026-10-03 | 1 | Pinned-source audit found 30,363,281 exact duplicate option rows across 138 of 267 option files (109,112,358 total rows); no conflicting duplicate keys were found. | The duplicate volume is material and must not be treated as an insignificant quality flag. | Require deterministic exact-row deduplication before production backtest use; preserve original counts and dedup counts in the data audit. |
| E024 | 2026-10-03 | 1 | Acquisition pattern index/*NIFTY*.parquet also downloaded BANKNIFTY.parquet, although this study uses NIFTY. | Added unnecessary data and obscured the exact intended source set. | Narrowed both acquisition manifest and workflow to index/NIFTY.parquet. |

| E025 | 2026-10-03 | 1 | Multiple rapid Phase 1 pushes attempted to save the same Hugging Face cache key concurrently; one cache save reported a reservation conflict. | Concurrent runs create avoidable cache races and can waste acquisition time. | Added a workflow concurrency group and conditional cache-save behavior so only the cache-miss run saves the key. |

| E026 | 2026-10-03 | 1 | The Phase 1 CI workflow invoked scripts/deduplicate_phase1_data.py, but that script was absent from the committed branch, so the structural validation passed and deterministic deduplication failed. | Phase 1 production-data preparation could not complete. | Added the missing deterministic deduplication script and re-triggered Phase 1 CI; no data was accepted or backtested during the failed run. |

| E027 | 2026-10-03 | 1 | The first market-quality/Greek feasibility audit design must not be mistaken for production Greek acceptance; it uses r=q=0 solely as a solver/data-path diagnostic. | A naive diagnostic could falsely imply target-delta coverage or production Greek validity. | Explicitly labeled the audit diagnostic-only and retained production G7/G8 as open until date-specific r/q, liquidity, and full decision-timestamp calculations are validated. |

| E028 | 2026-10-03 | 1 | Pinned-source market-quality audit found NIFTY daily timestamp counts ranging from 6 to 420 across 1,262 dates (median 378). | Uniform one-minute session coverage cannot yet be assumed; anomalous dates could bias trigger/entry availability if silently retained or removed. | Added explicit session-count outlier reporting (<300 or >390 timestamps/day). Phase 1 acceptance remains blocked until anomalous dates are characterized and an exclusion/repair rule is pre-registered. |

| E029 | 2026-10-03 | 1 | Phase 1 market-quality audit failed in run 37118147417 because a code-generation edit inserted literal \\n escape sequences into Python source, causing a SyntaxError before the audit and session-outlier characterization steps. | The structural validator and deterministic dedup passed, but the diagnostic audit did not execute and session outlier results were not produced in that run. | Repaired scripts/phase1_market_quality_audit.py in commit 336c8e8ddf5de93f31ef6b114e621747ae956620 and scheduled a clean rerun; no data acceptance or backtest was performed. |

| E030 | 2026-10-03 | 1 | GitHub API-created repair commits/PR did not emit a new Actions status in this environment because workflow events generated by repository-token operations are not retriggered. | The repaired Phase 1 audit could not be re-executed in GitHub Actions from this chat session; relying on an old successful run would not test the repaired code. | Opened PR #13 as the normal pull-request trigger path, recorded the absence of emitted checks, and kept Phase 1 acceptance blocked. No manual user run was assumed. |

| E031 | 2026-10-03 | 1 | Broader historical-data search found additional NIFTY 1-minute OHLCV/OI archives, but the reviewed public/commercial descriptions also explicitly lack bid/ask. | These sources do not resolve the frozen quote-based execution requirement. | Registered them as non-qualifying alternatives and elevated official NSE Historical Order & Trade Data to the preferred quote-source procurement candidate. |

| E032 | 2026-10-03 | 1 | Historical rate/cost sources are available from official RBI/NSE/Paytm Money publications, but a complete machine-readable date-aligned series has not yet been assembled. | Production Greeks and net P&L costs could otherwise be approximated with contemporary values, introducing look-ahead or cost-model bias. | Registered official source chronology and kept production acceptance open until the complete historical series is acquired and validated. |


| E033 | 2026-10-03 | 1 | Phase 1 documents reused G1–G10 for different requirements, making gate statements ambiguous. | Tester results could be interpreted against the wrong acceptance criterion, undermining reproducibility and independent approval. | Established one canonical G1–G14 vocabulary and propagated it through the Phase 1 specification, acceptance report, gate matrix and tester handoff. A fresh independent audit is required before Phase 1 approval. |
| E034 | 2026-10-03 | 1 | The model execution environment has no outbound network resolution, so a local clone/execution of the repository could not be performed from this session. | Local execution cannot substitute for independently verifiable GitHub Actions evidence and must not be presented as CI validation. | Recorded the limitation; used repository-native source inspection and GitHub Actions evidence APIs only. G12 remains open because commit 336c8e8 has zero associated workflow runs. |

| E035 | 2026-10-03 | 1 | Phase 1 acceptance report retained G1 as PARTIAL while the canonical gate matrix recorded G1 PASS. The market-quality diagnostic also contained unused hard-coded 09:15–15:30 session constants. | Inconsistent gate state and unused session constants could confuse independent review or be mistaken for historical session assumptions. | Synchronized G1 to PASS and removed the unused session-bound constants. G4 remains governed only by the date-specific session-calendar specification; no gate was advanced. |

| E036 | 2026-10-03 | 1 | Reopening PR #13 did not emit a new GitHub Actions workflow run for the repaired Phase 1 acquisition/audit path. | A fresh bulk acquisition/audit cannot be claimed from the connector session even though the workflow contains the required triggers. | Recorded the absence of a run in the data inventory; retained prior CI acquisition evidence as historical evidence only and kept G12 open. |

| E037 | 2026-10-03 | 1 | Independent tester found the Phase 1 workflow syntax-check step used a plain `run:` scalar with a second indented command, so the control-manifest validator was folded into the py_compile command rather than executed separately. | G12 CI correctness was invalid; the repaired workflow could not be independently accepted. | Changed the step to a block scalar `run: |` with two explicit commands. Independent CI execution is still required; no gate was advanced. |

| E038 | 2026-10-03 | 1 | Developer attempted a repository-side push trigger by committing a workflow-only comment to the corrected Phase 1 workflow, but GitHub exposed zero workflow runs for the resulting commit. | G12 still cannot be independently executed from this connector session. | Retain the corrected workflow; record the trigger attempt as non-executing evidence and keep G12 FAIL/OPEN. No phase advancement. |

| E039 | 2026-10-03 | 1 | GitHub Actions manual Run workflow control was absent because the Phase 1 workflow was not present on the default branch. The workflow was copied unchanged to main with workflow_dispatch retained. This is a CI discoverability issue, not a Phase 1 methodological change. | Refresh Actions after the main-branch workflow is indexed and dispatch the Phase 1 workflow against the feature branch. | G12 remains FAIL/OPEN until a real run and evidence exist. |

| E040 | 2026-10-03 | 1 | Manual Actions run #32 was dispatched against `main`, but Phase 1 executable scripts/manifests live on `phase-1-data-acquisition-validation`; the run failed after 22 seconds. | Workflow now accepts a `research_ref` input defaulting to `phase-1-data-acquisition-validation` and checks out that ref for manual dispatch. Push-triggered branch runs continue to use `github.ref`. | Await a real Phase 1 execution on the research branch before G12 acceptance. |

| E041 | 2026-10-03 | 1 | G12 CI run 37122653828 reached the research branch but failed because `scripts/validate_phase1_control_manifests.py` was missing there, although the workflow invoked it and the file existed on main. | Restored the exact control-manifest validator to `phase-1-data-acquisition-validation` at commit `68b39d91035bcb79c192cac80f20fd29ed6e709d`. | Trigger/observe the next branch execution; G12 remains OPEN. |

| E042 | 2026-10-03 | 1 | Final corrected Phase 1 Actions execution completed successfully after E041. | None; this is a resolved CI execution correction. | G12 is now PASS on developer evidence; independent tester must verify before G13/G14. |

| E043 | 2026-10-03 | 1 | The initial 286 session-count outliers were heterogeneous: regular sessions contained pre/post-window source observations, seven dates were documented special sessions, and one date was materially incomplete. Treating all outliers as one defect would risk either data loss or false session timing. | Added dated NSE special-session controls and a pre-registered rule: retain all raw rows, use only the 09:15–15:30 regular F&O execution window, and exclude a non-special date from trading when fewer than 300 eligible regular-session timestamps exist. | Fresh CI reconciliation: 1,254 normal eligible dates, 7 special sessions, 1 data-gap exclusion, 0 unreconciled dates. |

| E044 | 2026-10-03 | 1 | Independent tester found the G4 control manifest still contained three unresolved-date entries while the reconciliation script ignored that field; special dates were labelled without checking their documented intervals. | Replaced the unresolved-date escape hatch with explicit date_controls; added executable F&O intervals and source-observation intervals for every special session; reconciliation now checks every special execution interval, every observed timestamp against documented observation windows, and every controlled anomaly against its expected classification. | Await fresh final-head CI and independent re-audit. |
| E045 | 2026-10-03 | 1 | Successful G4/G12 run 37124047220 tested commit dd5447f, while the developer branch had advanced to e9fce04 with session-control changes. | Treat prior run as historical evidence only. Final-head CI must execute after the corrected G4 logic is frozen. | Fresh final-head workflow and independent tester verification required before G12/G13 closure. |


## 2026-10-03 — E046 corrective step
- User-provided independent tester report recorded E046 and superseded PR #17 with PR #18.
- Developer confirmed the defect directly in the current reconciler: the observed-date groupby could never emit a failure for a manifest-only date.
- Developer created phase-1-e046-bidirectional-reconciliation from the exact previously tested head 09c4c2e4b6bc569d42d4743fac5132ad0672f8d8.
- The corrective implementation adds bidirectional reconciliation and regression tests for missing special dates, unknown observed dates, duplicate mappings and interval failures.
- Phase 2 remains blocked pending fresh final-head CI and independent tester PASS.


## 2026-10-03 — E047 corrective manifest completion
- Fresh exact-head CI run 37129894485 executed commit 4099cd1217f072be961f120ab114034578e19197 on the E046 corrective branch.
- The first exact-head rerun (37129371003) exposed three genuine NSE weekend live-trading dates absent from the control manifest: 2024-01-20, 2025-02-01, and 2026-02-01. The reconciler correctly failed closed with 3 unreconciled dates.
- Official exchange notices document those dates as live sessions. The control manifest was extended with dated special-session rules and source references; execution eligibility remains constrained to the documented F&O window.
- Resolution: manifest schema version 2.1 adds the three documented weekend sessions. Fresh exact-head CI now passes G4 reconciliation with 10 special sessions reconciled, 0 unreconciled dates, and 0 missing manifest-session dates.
- G4 and G12 are developer-evidence PASS on 4099cd1217f072be961f120ab114034578e19197; G13 remains blocked pending independent tester approval. Phase 2 remains blocked.


## 2026-10-03 — E048 manual-dispatch routing safeguard
- User-provided screenshot showed workflow run #52 manually dispatched from the default `main` workflow entry.
- Inspection found the `main` workflow definition still had the older Phase 1 default `research_ref=phase-1-data-acquisition-validation` and did not include the E046 bidirectional G4 reconciliation step.
- This means run #52 can only be accepted as corrective evidence if its manual input explicitly selected `phase-1-e046-bidirectional-reconciliation`; the screenshot alone does not establish that input.
- Resolution: updated the `main` workflow definition to the E046-corrected workflow, including the bidirectional G4 reconciliation/regression-test steps and default research ref `phase-1-e046-bidirectional-reconciliation`. Main workflow update commit: 097d29c2816614bc7ba45365454b7f0dc270bc5d.
- No Phase 2 work was started. G13 remains blocked pending independent tester approval.


## E049 — Run #52 is stale for corrective G12 evidence
- User screenshot confirms manual Phase 1 run #52 completed green on `main`.
- Because run #52 occurred before the E048 correction to the default-branch workflow, its green result cannot establish execution of the E046-corrected reconciliation workflow.
- Required resolution: a fresh manual run after commit `097d29c2816614bc7ba45365454b7f0dc270bc5d`, with logs proving checkout of `phase-1-e046-bidirectional-reconciliation` and the exact resulting commit.
- Phase 2 remains blocked; no performance/trading conclusion has been produced.


## E050 — final-tip CI execution control
- A branch-tip CI safeguard was added so push-triggered validation fails closed unless the run is executing on `phase-1-e046-bidirectional-reconciliation`.
- This is a control improvement, not a data-quality failure. The resulting latest branch-tip CI run is required for final G12 evidence.


## E051 — 2026-10-03 — exact-tip automatic CI not independently observable
- The documentation-only commit 7a0b43b81d6b69165d745527f639de94ee5a62ad did not satisfy the workflow's push-path filter, so it cannot be treated as an Actions execution.
- To force a current-head execution without changing research logic, the workflow file was touched with an explicit path-trigger verification marker in commit b6e8ff93edfd2d3e5f1797d0d1d2ed186189d512.
- The branch now points to b6e8ff93edfd2d3e5f1797d0d1d2ed186189d512. GitHub's commit-status endpoint currently reports pending with zero published statuses, and the available GitHub connector does not expose the resulting push-triggered run list.
- Resolution: do not infer G12 from the trigger attempt. Require an observable Actions run whose checkout SHA equals b6e8ff93edfd2d3e5f1797d0d1d2ed186189d512, then independent tester re-audit. Phase 2 remains blocked.


## E052 — 2026-10-03 — co-commit exact-tip execution control
- To prevent documentation-only commits from moving the research head after a workflow-trigger commit, the final control/documentation update is being co-committed with the workflow marker.
- This commit is intended to be the exact current-head candidate for automatic Phase 1 CI. No G12 PASS is claimed until an observable Actions run proves the checkout SHA and completes all validation steps.


| E053 | 2026-10-03 | 1 | Independent tester found stale top-level Phase 1 status text after the E046/E047 corrective work: README role/current gate wording and top-level gate/acceptance/handoff states did not clearly match the latest independent Run #55 result. | Reviewers could read superseded E044/E045/E046 states as current, weakening control-plane reproducibility even though G4/G12 technical evidence was valid. | Synchronized the developer branch's canonical current-state sections; explicitly labeled historical evidence as append-only; recorded Run #55 G4/G12 independent PASS and G13/G14 BLOCKED; retained Developer as the correct role label on the developer branch and kept tester role/result in PR #20 and the tester report. No Phase 2 advancement. |


## E054 — 2026-10-03 — README current-branch provenance mismatch
- Independent tester PR #22 audited developer PR #21 at exact head `4f7186c4d2478bdd83f86f0bb35547f4c8594fbc` and found a stale README branch identifier.
- The README identified `phase-1-e046-bidirectional-reconciliation` even though PR #21 was the developer branch `phase-1-e053-control-sync`.
- Impact: current branch provenance was ambiguous even though G4/G12 evidence remained valid.
- Resolution: created `phase-1-e054-readme-branch-provenance` from the audited PR #21 head and corrected the README branch identifier. This is a control-plane correction only; no research methodology or gate result changed.
- G13/G14 and Phase 2 remain blocked pending independent tester re-audit.
| E055 | 2026-10-03 | 1 | Independent tester PR #24 found a malformed SHA in CONVERSATION_LOG.md for the audited PR #21 developer head recorded under E054. | The E054 provenance record could not be reproduced from the recorded hash, so E054 could not be closed despite the README branch correction being valid. | Corrected the E054 SHA to `4f7186c4d2478bdd83f86f0bb35547f4c8594fbc`, recorded the tester finding and correction, and submitted the resulting exact developer head for independent re-audit. No gate result or research methodology changed. |

- E055 is closed. The 2026-10-03 G5–G11 source audit introduced no new error; source verification and documentation were completed without changing gate status.
| E056 | 2026-10-03 | 1 | Attempted direct local retrieval of the RBI WSS source for G6 extraction; this execution environment again had no outbound DNS/network resolution. | A local extraction cannot be used as production evidence in this environment. | Do not substitute local/network failure with inferred values. Retain the official web-verified RBI source and defer machine-readable full-series extraction to the repository's CI/data-acquisition environment or an explicitly acquired source file. No gate result changed. |
| E057 | 2026-10-03 | 1 | After independent tester PR #25 closed E055 PASS, several developer-side canonical documents still referenced tester PR #20 as the current tester result. | Stale tester provenance could make the current gate-control history ambiguous even though the substantive gate state was unchanged. | Updated README, gate matrix, acceptance report, tester handoff and research status to identify PR #25 as the current E055 re-audit record. No gate was advanced. |


## E058 — 2026-10-03 — local raw-file salvage network limitation
- Attempted direct local acquisition of the pinned antony9952/Nifty_option_TBT raw archive from Hugging Face revision 643b48383839947b5fe3ed9483c9f7c0f167e865.
- The local runtime could not resolve huggingface.co (DNS/network failure), so no raw file was downloaded or accepted locally.
- No substitute values, OHLC-to-quote conversion, or inferred bid/ask was used.
- Resolution: retain the pinned CI acquisition workflow using the repository's HF_TOKEN secret and cache; independently inspect the resulting artifact before any G9 decision.
- G9 remains BLOCKED; G13/G14 and Phase 2 remain BLOCKED.

| E059 | 2026-10-03 | 1 / G9 | Exact developer head `d2003df53d07a952aa7434c4c706f396067b6080` has no associated PR-triggered GitHub Actions run; the available GitHub connector does not expose workflow-dispatch. | Exact-head acquisition evidence cannot yet be independently observed. This is an execution/CI-access limitation, not evidence that the TBT candidate is absent or invalid. | Repaired the G9 workflow so push/PR/manual-dispatch triggers, pinned cache keys, per-raw-file audit and always-uploaded failure reports are explicit. Preserve G9 BLOCKED and require an independently observed CI run/artifact before judging the candidate. |

## E063 — 2026-10-03 — explicit bid/ask methodology change
- Developer formally changed the primary research methodology so historical bid/ask is no longer mandatory for the primary backtest.
- Impact: the previous G9 acceptance contract is no longer the correct mandatory criterion for the primary execution model, but the change must not be interpreted as evidence of historical executable fills.
- Resolution: added `research/PHASE1_EXECUTION_PROXY_SPEC.md` and updated `RESEARCH_PLAN.md` to freeze completed-1-minute decision / next-eligible-minute-open execution, adverse 0/5/10/20/50-bps per-leg slippage with an effective-date tick floor, date-effective transaction costs, and explicit missing-execution handling.
- Independent tester approval is required before Phase 2. No Phase 2 work has started.

## E064 — 2026-10-03 — execution-proxy specification formula rendering
- The initial `PHASE1_EXECUTION_PROXY_SPEC.md` commit rendered backslash-based formula escapes incorrectly because source-string escaping converted LaTeX sequences into tabs/brackets.
- Impact: the mathematical definition of the slippage function was not rendered reliably in the research control document.
- Resolution: replaced the formulas with plain-text/code-block notation and re-read the corrected specification. No methodology values changed.
- The corrected developer head is submitted for independent tester review. Phase 2 remains blocked.

| E065 | 2026-10-03 | 1 / G9 | Tester found the bid/ask-free proxy methodology did not define deterministic handling when one leg of a pending multi-leg adjustment lacked its next eligible bar. | Partial fills, repeated retries, or ambiguous strategy state could change P&L and invalidate reproducibility. | Corrected the specification: multi-leg adjustments are atomic; if any leg fails eligibility, no leg fills, the pre-adjustment state is retained, the triggering event is consumed, and re-entry into the trigger region is required before a new adjustment. Regression tests added. Await independent tester re-audit. |
| E066 | 2026-10-03 | 1 / G9 | Tester found the sell-side slippage formula max(0, P_base-S(P_base)) could create a zero-price fill while zero/negative fills were declared invalid. | Could manufacture economically impossible fills and bias results. | Corrected sell fills to P_base-S(P_base) with explicit rejection when P_base<=0 or P_fill<=0; buy fills use the same positivity validation. Regression tests added. Await independent tester re-audit. |

| E067 | 2026-10-03 | 1 / G9 | Independent tester approval changed G9 from BLOCKED to PASS under the revised proxy methodology; prior control text still reflected the blocked state. | Stale gate status could incorrectly prevent the next valid Phase 1 work or create conflicting audit records. | Synchronized the canonical gate matrix, research status, README and conversation log to Tester PR #32. G13/G14 and Phase 2 remain blocked by the remaining open gates. |


| E068 | 2026-10-03 | 1 / G5 | Initial G5 validator draft conflated session eligibility with NIFTY timestamp presence, which would have made the alignment acceptance test tautological. | A validator that defines eligibility using the same underlying-match condition cannot detect missing underlying observations. | Corrected the validator to determine session eligibility independently from date-specific intervals, then test exact timestamp membership in the NIFTY grid. Added explicit acceptance fields and bounded missing-index examples. No gate was advanced from this draft; exact-head CI remains required. |

| E069 | 2026-10-03 | 1 / G5 | No PR-triggered GitHub Actions run was observable for the exact G5 PR head through the available repository connector after PR #34 creation. | Without an observable exact-head run, the G5 evidence artifact cannot be claimed and the gate cannot be advanced. | Retained the G5 workflow with automatic push/PR/manual triggers and cache reuse; recorded the absence as an execution-environment limitation; no G5 PASS is claimed and no Phase 2 work is authorized. |


| E071 | 2026-10-04 | 1 / G5 | Static audit of the G5 validator found the expiry/day coverage section referenced a non-existent `in_session` column instead of the separately computed `decision_eligible` flag. | A production run would fail during report construction rather than produce valid expiry/day coverage evidence. | Corrected the two references to use `decision_eligible`; no data result was claimed before the correction. Exact-head CI evidence remains pending. |

| E073 | 2026-10-04 | 1 | Independent tester PR #36 found G5 manual-dispatch evidence did not bind the generated artifact explicitly to the checked-out commit SHA. | A manually selected research ref could produce an artifact whose provenance was not machine-bound to the exact checkout, weakening reproducibility. | Hardened the G5 validator to record `git rev-parse HEAD` in the evidence artifact and the workflow to verify the artifact SHA against the checkout; manual dispatch now accepts an optional exact expected commit SHA and fails closed on mismatch. G5 remains OPEN pending an observable exact-head run and independent tester re-audit. |

| E075 | 2026-10-04 | 1 | Canonical Phase 1 gate matrix retained superseded historical wording that described G9 as blocked even after Tester PR #32 independently approved the revised proxy methodology. | Conflicting current/historical language could cause an incorrect interpretation of the active gate state. | Synchronized the current decision and historical G9 status wording to G9 PASS under the independently approved proxy methodology; G13/G14 remain blocked by G5/G6/G7/G8/G10/G11. |

| E076 | 2026-10-04 | 1 / G5 | Tester PR #39 found the G5 workflow push trigger did not include the active correction branch, so automatic push execution could not establish exact-head CI evidence there. | The corrected workflow could remain unexecuted on its own branch, blocking reproducible CI evidence. | Added the active correction branches to the push trigger and aligned workflow_dispatch default ref to the correction branch. G5 remains OPEN pending observable exact-head CI and tester review. |
| E077 | 2026-10-04 | 1 / G6 | Tester PR #39 found that G6 cache restore/save did not actually prevent the acquisition script from re-downloading every source. | Cache persistence could not be demonstrated as acquisition reuse, causing unnecessary network dependence and weakening the project's cache/reuse requirement. | Changed the acquisition script to reuse non-empty retained source files as CACHE_HIT_LOCAL records; workflow also triggers on the correction branch. G6 remains OPEN pending full r/q/IV production evidence and tester re-audit. |
| E078 | 2026-10-04 | 1 / G9 | Tester PR #39 found stale historical G9-blocked wording after G9 was independently approved under the proxy methodology. | Conflicting historical/current language could cause ambiguity in the active gate state. | Synchronized the historical language to explicitly identify superseded pre-approval notes and retain G9 PASS as the current state. |

| E079 | 2026-10-04 | 1 / G6 | Tester PR #40 found CACHE_HIT_LOCAL accepted any non-empty file despite the code describing it as byte-validated. | A corrupted or replaced cached source could be treated as valid, weakening reproducibility/provenance. | Changed G6 acquisition to fail closed unless an immutable expected SHA-256 is configured and exactly matches the cached/acquired bytes. No unverified placeholder digest is treated as acceptance evidence. G6 remains OPEN pending real expected digests and substantive r/q/IV evidence. |

| E080 | 2026-10-04 | 1 / G6 | The first post-bootstrap G6 workflow revisions repeatedly produced path-named failed runs without jobs while the workflow definition was being simplified; the final known-good structure was restored from the previously validated PR #38 workflow pattern. | Invalid workflow structure could prevent exact-tip CI evidence despite correct acquisition code. | Restored the previously validated workflow structure, retained the correction-branch trigger and manual dispatch, and verified exact-tip G6 run `37148353717` succeeded at commit `e8fca6a6084a463528643b63dd8f310899c0b3bf`. |


| E082 | 2026-10-04 | 1 / G6 acquisition | A local direct attempt to retrieve official NSE historical valuation data for substantive q reconstruction failed because the execution environment could not resolve `nsearchives.nseindia.com` (DNS/network isolation). | Local acquisition could not independently populate the production q dataset or compute its file digest in this environment. Treating this as successful acquisition would create false provenance. | Logged as an environment limitation only. The production pipeline is fail-closed and requires acquired, hashed r/q inputs before evidence can be accepted; no proxy q values or backtest inputs were substituted. |

| E083 | 2026-10-04 | 1 / G6 implementation | Pre-CI review found the production Greek audit used an unsupported `nrows=0` argument to `pandas.read_parquet` for schema inspection. | The production workflow could fail before substantive validation, creating avoidable CI noise and weakening the fail-closed evidence path. | Replaced the schema probe with PyArrow ParquetFile schema inspection and added deterministic BS/IV regression tests to the dedicated G6 production workflow. No gate was advanced. |


| E084 | 2026-10-04 | 1 | G6 production scaffold initially measured strict-prior r/q coverage against the q input table itself, which could make missing trading dates invisible. | Coverage acceptance could become tautological and falsely appear complete. | Corrected the validator to derive the trading-date universe from actual NIFTY option-bar timestamps; invalid option timestamps now fail closed. No G6 gate advanced. |


| E085 | 2026-10-04 | 1 / G6 acquisition | Developer added an official-NSE q acquisition script and regression test, but the GitHub connector safety layer blocked the workflow-file mutation that would invoke the new acquisition stage automatically. | The acquisition code exists, but automatic CI execution of that new stage cannot yet be claimed from this interaction. | Retain the script/test as a controlled branch change; do not claim execution or G6 evidence. Reattempt workflow integration through a safer repository-control path. |


| E086 | 2026-10-04 | 1 / G5 | Exact-tip G5 alignment audit Run 37148487963 failed at the substantive alignment stage on commit db668dd2b89bf691a6481affb3cb2a9060c5fe98. Artifact provenance/check-out binding succeeded, but the validator did not meet its acceptance condition. | G5 cannot be accepted and Phase 1 remains blocked. | Preserve the failed artifact as evidence. Do not relax the 100% exact-timestamp alignment rule. Next developer action is diagnostic isolation of the failed alignment population and corrective methodology only if justified by pre-registered rules; independent tester review remains mandatory. |


## 2026-10-04 — E089 G6 production correction
- Independent tester PR #45 determined G6 FAIL / OPEN on developer head c5f28327c13efd9b93bd4ca5a809dfc39b447c3d. E088 is accepted without reinterpretation.
- The previous implementation was a scaffold rather than a completed historical Greek reconstruction.
- The correction now performs timestamp-level production reconstruction with exact contemporaneous NIFTY joins, strictly-prior r/q selection, study-window enforcement, 15:30 IST expiry timing, deterministic Brent IV solving, signed/absolute deltas, target-delta diagnostics, populated failure counters, checksums and exact-checkout provenance.
- G6 remains FAIL / OPEN because complete historical risk_free.csv and dividend_yield.csv inputs are not yet accepted and independent tester approval is still required.
- G5 remains FAIL / WAIVED FOR CONTINUED RESEARCH; G13/G14 and Phase 2 remain BLOCKED.


| E090 | 2026-10-04 | 1 / G6 CI | Corrective G6 unit tests imported scripts.phase1_g6_production_greeks, but scripts is not a Python package in the repository; exact-tip CI failed during test collection before production evidence generation. | The substantive G6 correction could not be exercised by CI and no evidence artifact was produced on that run. | Changed the test to import the module from the scripts execution path. No gate advanced; a fresh exact-head CI run is required. |


| E091 | 2026-10-04 | 1 / G6 CI | Exact-tip G6 run 37156932044 passed 6/7 tests but the strict-prior regression test failed because pandas 3.x preserved different datetime units on the left and right merge keys. | The no-lookahead join could not be CI-verified. | Normalized both strict-prior join keys to datetime64[ns]. No methodology relaxation or gate advancement. |


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


| E103 | 2026-10-04 | 1 / G6 | Final primary RBI acquisition run 37158613890 executed all three official RBI/WSS hostnames over the bounded archive range but produced zero parseable 91-Day Treasury Bill (Primary) Yield rows. | Production r input cannot be established from the primary machine-readable source in the CI environment; proceeding with a mirror without explicit provenance would contaminate G6 acceptance. | Record the external access/provenance blocker, retain G6 FAIL/OPEN, and investigate any secondary RBI mirror only as a separately labelled cross-check/provisional source. No silent substitution or gate advancement. |

## 2026-10-04 — Tester PR #46 secondary RBI cross-check
- Tester branch `tester/phase-1-g6-secondary-r-crosscheck-20261004` independently reviewed the provisional Dataful RBI-derived cross-check.
- Tester determination: **G6 FAIL / OPEN**. The source is not accepted as a production r input without immutable full-file provenance, coverage/duplicate audit, and reconciliation to primary RBI WSS observations.
- No Phase 2 authorization. G5 remains FAIL / WAIVED FOR CONTINUED RESEARCH.
- Tester report: `research/TESTER_REPORT_G6_SECONDARY_R_CROSSCHECK_20261004.md`; PR #46 targets this developer branch and is intentionally not merged as a gate-advancement mechanism.


| E104 | 2026-10-04 | 1 / G6 | Independent tester PR #47 found that the RBI acquisition restored a cache path but the acquisition script still unconditionally re-requested every WSS ID; it also did not explicitly preserve the conservative distinction between source observation date and actual publication/availability date. | Cache reuse/provenance requirements were not actually satisfied, and no-lookahead semantics were under-specified. | Corrected the acquisition to validate cached HTML plus sidecar SHA-256 provenance before reuse, reject unproven retained files, retain immutable expected hashes for bootstrapped WSS pages, and explicitly document/use the source observation date only as a conservative eligibility date with strict-prior exclusion. Added a same-day strict-prior regression test. Fresh tester handover required. |


| E105 | 2026-10-04 | 1 / G6 | Exact-head G6 CI run 37171349785 remained in RBI acquisition for an extended period because the source scanner used ~3,900 IDs, 20 workers, and 10-second request timeouts. | Functional fail-closed/cache logic was present, but acquisition could stall a research gate and did not bound the operational runtime tightly enough. | Tightened the bounded scan to IDs 24000–28500, 100 workers, and 3-second request timeouts. This does not relax provenance, target-series, conflict, or fail-closed requirements. Exact-head CI must be revalidated after the correction. The prior run remains non-authoritative and is not treated as a PASS. |


## 2026-10-04 — E106 RBI bootstrap-first correction
- The corrected RBI acquisition still used a broad archive scan before leveraging the four independently identified official WSS IDs with immutable expected SHA-256 values.
- This created unnecessary runtime exposure after E105. The acquisition was changed to try the known official IDs first and retain the 24,000–27,900 scan only as fallback discovery.
- No acceptance criterion, provenance rule, target-series rule, duplicate rule, or no-lookahead rule was relaxed. Fresh exact-head CI is required.


## 2026-10-04 — E107 exact-head CI trigger/evidence gap
- After E106, the available GitHub connector exposed no workflow-dispatch operation and reported zero workflow runs for corrected commits 5e90927245283c865c9a9a187fb9a3ec43e52dcd and 68c572e471b78009640d0e3aa3717d6a5d899e01.
- Tester PR #48 independently confirmed G6 FAIL/OPEN because exact-head Actions/artifact evidence is absent.
- Resolution: retain G6 FAIL/OPEN, do not substitute the prior run, and require an observable exact-head CI execution before any gate advancement.


| E106 | 2026-10-04 | 1 / G6 | The bounded RBI WSS ID scan remained operationally unsuitable for production validation and could not establish a complete primary risk-free series efficiently. | Continued scanning would risk an endless gate and still depended on fragile page-ID discovery. | Replaced production risk-free acquisition with RBI Bulletin Table 26 91-day Government of India Treasury-bill implicit auction yields from an immutable Reserve Bank Innovation Hub commit, verified by Git blob SHA-1. Cache reuse is fail-closed; source auction date is conservative eligibility date; same-day use is excluded. WSS remains reconciliation/control only. |


| E107 | 2026-10-04 | 1 / G6 | Fresh CI reported an immutable RBI Bulletin blob mismatch even though the pinned commit/tree identified the expected blob and the downloaded byte count matched. | The diagnostic revealed the verifier constructed the Git blob header with a literal backslash sequence rather than a NUL byte, creating a false mismatch. | Corrected the verifier to use the actual `\\0` Python escape (NUL byte) and retained the pinned commit/blob identity. Fresh exact-head CI required. |
| E108 | 2026-10-04 | 1 / G6 | Developer correction of E107 required a second source-level escaping fix after inspection showed the verifier still contained two backslashes. | Initial remediation was syntactically valid but semantically still wrong for Git blob hashing. | Replaced the two-backslash source sequence with a single `\\0` escape and verified the committed source line directly. Fresh CI required; no gate advancement. |


| E109 | 2026-10-04 | 1 / G6 | RBI Bulletin Excel parsing reached the pinned source successfully but a blank/metadata cell produced pandas `NaT`, which then failed comparison against `datetime.date`. | Date parser did not explicitly treat `NaT` as missing. | Changed date parsing to `errors="coerce"`, explicitly reject `pd.isna(v)`, then return the date. No source/provenance rule changed. |


| E110 | 2026-10-04 | 1 / G6 | Exact production artifact failed closed with `UNDERLYING_INPUT_MISSING`: `data/raw/index/NIFTY.parquet` was required by the solver but was never materialized by the G6 workflow. | G6 source acquisition covered q/r but omitted the contemporaneous underlying parquet, so the production Greek audit could not legitimately compute IV/Delta. | Added a pinned Hugging Face acquisition for the independently audited NIFTY parquet, revision `92e0288`, expected SHA-256 `613864738250107807354c17c7092986960220ac3062b830c65cc5f9ec16fcf7`; cache/provenance validation and HF_TOKEN support added. |
| E111 | 2026-10-04 | 1 / G6 | Initial workflow patch did not include `data/raw/index` in the G6 cache paths and did not fully add the new acquisition script to workflow path triggers. | The new source could be reacquired, but cache/reuse and workflow triggering were incomplete. | Corrected restore/save cache paths and push/PR path triggers for `scripts/acquire_g6_nifty_underlying.py`; fresh exact-head CI required. |


| E112 | 2026-10-04 | 1 / G6 | Exact production artifact `11292375340` at head `0c5c8b79005ceee27c6207d3446e5c405162a5e2` reported `OPTION_INPUTS_MISSING` after underlying/r/q acquisition succeeded. | The G6 workflow did not materialize the NIFTY option parquet inputs required by the production solver. | Added pinned HF NIFTY option acquisition at revision `0f4800e`, per-file SHA-256 validation, concurrent download, manifest provenance, and HF_TOKEN support. No option data are synthesized or interpolated. |
| E113 | 2026-10-04 | 1 / G6 | Initial option workflow patch did not yet persist the option directory in the G6 cache/save paths or fully propagate script path hashing. | Option acquisition would work for one run but cache reuse and deterministic workflow triggering were incomplete. | Corrected restore/save paths and hash inputs to include `data/raw/options/NIFTY` and `scripts/acquire_g6_nifty_options.py`; fresh exact-head CI required. |


| E114 | 2026-10-04 | 1 / G6 | HF option acquisition failed at the file-list stage with HTTP 400 because the tree API request combined `expand=true` and pagination parameters unsupported by that endpoint combination. | The acquisition contract was inferred too broadly instead of matching the documented recursive tree API. | Changed the listing call to the supported recursive tree endpoint without `expand/limit`; file-level SHA-256 validation remains unchanged. |


| E115 | 2026-10-04 | 1 / G6 | Complete production scan reached option/underlying/r/q data and then raised `KeyError: '0.30'` while recording target-delta diagnostics. | Target error storage was initialized with `str(float)` keys (`0.3`) but later accessed using canonical two-decimal keys (`0.30`). | Standardized target-error keys to `f"{t:.2f}"` and added a deterministic regression test for all five target keys. |


| E115 | 2026-10-04 | 1 / G6 | Complete G6 production scan failed after all inputs/coverage were valid with `failure_reason: "'0.30'"`. | `target_errors` was keyed by raw float strings (`0.3`) while the selected-target lookup used normalized two-decimal labels (`0.30`). | Normalized `target_errors` initialization to `f"{t:.2f}"`, matching counters and lookup keys. No selection criterion or data rule changed. |


| E116 | 2026-10-04 | 1 / G6 | Exact-head full production scan `37173353749` remained in the production audit for many hours without completing. | The workflow had no explicit runtime bound, so a pathological/full-sample solver execution could stall the gate indefinitely. | Added a 30-minute CI timeout to the production evidence step. This is a runtime safety bound only; it does not change data, solver, selection, or fail-closed rules. A timeout is a FAIL, never a PASS. |


| E117 | 2026-10-04 | 1 / G6 | Bounded exact-head run `37175103199` failed deterministic tests: `test_vectorized_delta_matches_scalar` referenced undefined `load_module` and nonexistent `bs_delta_arrays`. | Regression test was stale relative to the production solver API. | Added the actual `bs_delta_arrays` numba primitive and repaired the test to import/call the production functions directly. This changes no trading or Greek calculation semantics except exposing the already scalar-defined delta as a deterministic vector primitive. |


| E118 | 2026-10-04 | 1 / G6 | Full-sample G6 production scan remained computationally slow because the Brent IV solver evaluated independent roots serially for every valid option row. | Serial execution made the 77M-row-scale historical option evidence impractical within the bounded CI window. | Changed the IV solver to Numba `prange` parallel execution. Each row remains solved by the identical Brent algorithm, bounds, tolerance, and rejection rules; only independent execution order is parallelized. |


| E119 | 2026-10-04 | 1 / G6 | Full exact production reconstruction remained too slow/memory-heavy when each option parquet file was loaded as one pandas frame. | Whole-file loading created large transient frames and prevented controlled progress without changing the mathematical sample. | Changed the production loop to process every parquet file in exact 250,000-row Arrow batches. All rows remain included; no sampling, filtering of decision rows, or mathematical shortcut was introduced. Counters and target-selection logic run identically per batch. |


| E120 | 2026-10-04 | 1 / G6 | Full exact G6 production scan remained computationally unbounded in a single job even after row batching and Numba parallel roots. | The exhaustive requirement was correct, but single-job execution was the bottleneck. | Re-architected production evidence into 8 exact option-file shards, each processing every assigned row with unchanged mathematics, then a deterministic aggregator verifies complete file partition and merges counters/histograms. No sampling or approximation. |

| E121 | 2026-10-04 | 1 / G6 | Exact sharded G6 run `37177271358` at `def91894f5cd6f30c94bd63f60d2f0e414bfccf3` failed immediately with `name 'SHARD_COUNT' is not defined`. | E120 added shard partitioning in the production solver but omitted the runtime configuration definition. | Added validated `G6_SHARD_INDEX`/`G6_SHARD_COUNT` environment configuration with safe defaults, shard-specific evidence filenames, and a deterministic regression test. No mathematical or data-selection rule changed. Fresh exact-head CI required. |


### E121 — G6 shard runtime configuration failure (2026-10-04)
- **Status:** Corrected; revalidation required.
- Exact E120 run `37177271358` checked out `def91894f5cd6f30c94bd63f60d2f0e414bfccf3` and failed closed with `name 'SHARD_COUNT' is not defined`.
- Cause: E120 introduced 8-way workflow sharding without wiring `G6_SHARD_INDEX` / `G6_SHARD_COUNT` into the production Python module.
- Correction: E121 reads and validates both environment variables and writes shard-specific evidence files; default remains single-shard-compatible.
- No research conclusion or gate advancement is permitted from the failed artifact.


### E122 — G6 exhaustive shard runtime saturation (2026-10-04)
- **Status:** OPEN / under investigation.
- E121 corrected the undefined shard configuration and the eight shards entered the exhaustive IV/Greek scan.
- All eight shard jobs remained in the production scan step for an extended period without terminal status, while the exact-head validation run remained queued behind them.
- No production result is accepted from this run until all shards terminate and aggregation completes.
- This is being treated as a bounded CI/runtime issue, not as evidence that the mathematical method passed or failed.


### E123 — G6 dividend-coverage evidence gap detected before tester audit (2026-10-04)
- **Status:** OPEN / remediation required after current exact-head run is resolved.
- `scripts/aggregate_g6_production_greeks.py` expects `dividend_coverage`, but the current production report does not emit that field.
- Consequently, the aggregator's equality check can compare `None` across shards and fail to establish actual dividend coverage.
- This is a substantive evidence-completeness defect, not a mathematical conclusion.
- Current exact-head run 37180326783 must not be promoted to G6 PASS on this basis.


### E124 — G6 aggregate workflow trigger omission (2026-10-04)
- **Status:** CORRECTED; fresh exact-head validation required.
- The aggregate script was not included in push/PR path filters, so an aggregation-only correction could fail to launch automatic validation.
- Added `scripts/aggregate_g6_production_greeks.py` to both push and pull-request trigger paths.


### E125 — superseded G6 workflow queue (2026-10-04)
- **Status:** CORRECTED.
- Incremental E123/E124 commits produced multiple queued G6 runs.
- Added GitHub Actions concurrency with `cancel-in-progress: true` per branch so only the latest developer head can remain authoritative.
- Superseded runs are not eligible for tester evidence.


### E126 — G6 shard timeout at 30 minutes (2026-10-04)
- **Status:** CORRECTED; fresh exact-head validation required.
- Exact-head run 37180326783 demonstrated shard 3 exhaustively scanning for 30 minutes before timeout, with the log confirming the production Python process was terminated at the 30-minute limit.
- The shard held roughly one-eighth of the full option population, so the calculation did not complete within the bounded wall-clock budget.
- No rows are to be sampled, skipped, interpolated, or mathematically simplified to hide the runtime issue.
- Increased exhaustive file-index partitioning from 8 to 32 shards while retaining the same production solver, row traversal, exact timestamp joins, and aggregation logic.


### E128 — G6 shard failure evidence was hidden (2026-10-04)
- **Status:** CORRECTED; fresh exact-head validation required.
- In run 37182645762, shard 10 exited code 2 after ~9m50s, but the shard evidence upload was skipped because the workflow uploaded only on success.
- The production script writes structured failure reports, but the workflow did not preserve them on failure, preventing independent diagnosis.
- Added `if: always()` evidence printing and artifact upload for shard reports.
- No data rows are to be skipped or simplified to avoid this failure.


### E126 — G6 SHA-256 helper unbound-variable defect (2026-10-04)
- **Status:** CORRECTED; fresh exact-head validation required.
- Final-head shard 15 completed its full 3,421,493-row scan and failed while constructing the report because `sha256_file()` used an unbound lambda default variable.
- This defect was exposed by the terminal evidence artifact, not by a partial scan.
- Corrected to explicit chunk iteration and added a deterministic regression test.
- No mathematical/data-quality conclusion was drawn from the failed run.


### E131 — G6 32-shard aggregation mismatch (2026-10-04)
- **Status:** CORRECTED; fresh exact-head validation required.
- The production workflow scans 32 deterministic shards, but the aggregate job still supplied `G6_SHARD_COUNT=8`.
- This would have caused the aggregator to inspect only shard 00–07 and reject/incompletely represent the 32-shard evidence set.
- Corrected the aggregate environment to `G6_SHARD_COUNT=32`.
- No mathematical/data-selection rule changed.


### E133 — G6 shard-count expansion to 32 (2026-10-04)
- **Status:** OPEN / audit in progress.
- Exact-head run 37188412462 uses 32 shards rather than the earlier 8-shard design.
- Several shards have completed successfully and others remain active/queued.
- Tester approval must verify deterministic complete file partitioning, aggregate coverage, and absence of row omission/duplication under the 32-way partition.


### E126 — G6 aggregate missing NumPy dependency (2026-10-04)
- **Status:** CORRECTED / fresh exact-head validation required.
- Run `37188412462`, developer execution head `7825a59b47766b3116f6a3588a26fcaa4b2692a7`.
- All 32 shard artifacts completed successfully and downloaded by aggregate job `111405080689`.
- Aggregate failed because `scripts/aggregate_g6_production_greeks.py` imports NumPy but the aggregate job installed no NumPy.
- No scientific output was accepted from the failed aggregate.


### E134 — G6 final tester evidence-completeness failure (2026-10-04)
- **Status:** CORRECTIVE BRANCH ACTIVE; fresh tester audit required.
- Independent tester PR #49 audited exact head `1a9eab7389b972c05362271ee9fb23092aa7354d` and found G6 FAIL/OPEN because the evidence artifact omitted IV iteration/residual summaries, explicit expiry/date coverage, and explicit future-input/no-lookahead counters.
- The underlying mathematical/data-path consistency checks passed; this is an evidence-completeness defect, not a change to the scientific model.
- Developer remediation branch `phase-1-g6-evidence-remediation-20261004` adds these fields and fail-closed aggregate checks. Fresh exact-head CI and a fresh isolated tester branch are mandatory before G6 can pass.

### E135 — G6 tester orchestration tooling-limit record (2026-10-04)
- **Status:** Tooling limitation; no scientific conclusion affected.
- A batch artifact-download attempt hit the Code Mode nested-tool-call ceiling after 20 shard downloads. The remaining shard artifacts were not locally unpacked in that call; exact-head metadata and the aggregate's 32-shard fail-closed checks remain available.
- This limitation did not alter the tester's G6 FAIL determination.

### E136 — GitHub branch-creation connector parameter misuse (2026-10-04)
- **Status:** Corrected; no repository mutation occurred from the failed call.
- The first tester-branch creation request used incorrect connector parameter names. The branch was subsequently created correctly from the frozen developer SHA.


### E137 — G6 remediation exact-head Actions trigger not observable (2026-10-04)
- **Status:** OPEN / execution-environment blocker.
- The corrected remediation head `e43acf88e10b4af13af54fe11d0c0a3cec5295ec` has the G6 workflow push trigger explicitly enabled for `phase-1-g6-evidence-remediation-20261004`, but the GitHub connector reports zero workflow runs for the commit. The connector exposes no workflow-dispatch action.
- No prior-run artifact is being reused as evidence for the corrected code.
- Resolution: retain the remediation branch and G6 FAIL/OPEN; continue repository-native execution attempts when available. A fresh exact-head Actions run is mandatory before tester re-audit.


## 2026-10-04 — E138 G6 conditional-acceptance assessment
- User authorized assessment of whether the completed G6 numerical scan can be retained as conditional evidence rather than recomputed solely to populate audit fields.
- This is not a gate pass. A formal proposal documents D1-D3 and requires independent tester disposition.
- Fresh tester branch `tester/phase-1-g6-conditional-acceptance-20261004` was created from exact developer remediation SHA `e9d319e7f2e902f77696fc4dbd029fa93cbbce7f`.
- Until the independent verdict, G6 remains FAIL/OPEN and no Phase 2 work is authorized.


### E139 — progression-waiver transition to Phase 2 (2026-10-04)
- **Status:** CONTROL-POLICY CHANGE; no scientific conclusion affected.
- The project owner accepted the historical G6 aggregate for research progression with deferred audit and instructed that intermediate gate strictness be reduced.
- Effect: later research phases may proceed without waiting for a fresh exact-head G6 evidence artifact, while D1–D3 remain explicit limitations and material scientific/data/execution/reproducibility defects remain blocking.
- Safeguard: no historical G6 artifact is relabelled as containing missing evidence; final independent audit remains mandatory before any validated trading conclusion.


### E140 — Phase 2 validation workflow not observable through connector (2026-10-04)
- **Status:** OPEN / execution-environment limitation.
- Exact Phase 2 developer head `8a060402e76e5d3b8acdc10b13a7c21f3bdd538f` was placed in PR #53 with a dedicated PR/manual workflow.
- The GitHub connector reports zero workflow runs and zero published statuses for that exact commit.
- No CI pass is claimed from this absence. Source code, specification and regression design remain subject to later independent milestone audit.


### E141 — cost schedule unit-conversion defect caught before integration (2026-10-04)
- **Severity:** MATERIAL PRE-INTEGRATION COST-MODEL DEFECT; corrected before any production backtest result.
- Initial JSON conversion incorrectly divided several NSE/IPFT rupee-per-crore/rupee-per-lakh rates by an extra factor of ten.
- Corrected:
  - NSE ₹3,503/crore → 0.0003503 turnover rate.
  - NSE ₹3,552.99/crore → 0.000355299 turnover rate.
  - IPFT ₹50/crore → 0.000005 turnover rate.
  - IPFT ₹0.01/crore → 0.000000001 turnover rate.
- Added explicit unit-conversion regression tests and CI inclusion.
- **Outcome:** no backtest results were generated from the defective schedule.


### E142 — Phase 2 naive-timestamp timezone defect caught before production run (2026-10-04)
- **Severity:** MATERIAL CHRONOLOGY / LOOK-AHEAD DEFECT; corrected before any production result.
- G6 normalization produces timezone-naive Asia/Kolkata timestamps. The initial Phase 2 parser interpreted naive timestamps as UTC, which would have shifted bars by 5 hours 30 minutes.
- Corrected Phase 2 timestamp normalization now localizes naive values to Asia/Kolkata and converts timezone-aware values to Asia/Kolkata.
- Added a regression test covering naive decision and expiry-close timestamps.
- **Outcome:** no production backtest result used the defective timezone interpretation.

### E143 — direct public-data fetch unavailable in the model-side container (2026-10-04)
- **Status:** EXECUTION-ENVIRONMENT LIMITATION; no scientific result affected.
- Direct container/network retrieval of the pinned Hugging Face parquet file failed because the model-side runtime has no external DNS/network access.
- The repository workflow retains the pinned Hugging Face acquisition path, cache-first restoration and immutable source-revision controls.
- No external data were fabricated or substituted as a consequence of this failure.

### E144 — inclusive minimum-DTE boundary mismatch (2026-10-04)
- **Severity:** MINOR LOGIC/SPECIFICATION MISMATCH; corrected before production run.
- The written rule specified an expiry at least 20 calendar days from entry, while the first implementation used a strict greater-than comparison.
- Corrected both the engine and cycle scheduler to use an inclusive 20-day boundary.
- Added a regression test at exactly 20 days.
- **Outcome:** no production result used the prior strict-boundary implementation.

### E145 — cycle-runner pandas truth-value bug caught before production (2026-10-04)
- **Severity:** RUNTIME BOOKKEEPING DEFECT; corrected before production run.
- The manifest calculation attempted boolean conversion of pandas DataFrames.
- Replaced with deterministic list-length counting.
- No production result used the defective expression.


### E146 — Phase 2 workflow expression interpolation defect (2026-10-04)
- **Severity:** MATERIAL PRODUCTION-WORKFLOW DEFECT; no production result affected.
- Independent tester found malformed GitHub Actions expression interpolation in `.github/workflows/phase2-production-backtest.yml`, including checkout/ref expressions using single-brace syntax rather than `${{ ... }}`.
- **Impact:** exact-head checkout and workflow execution cannot be treated as reproducible until corrected.
- **Resolution required:** correct all affected expressions and independently inspect the corrected workflow.

### E147 — Phase 2 analysis artifact-pattern mismatch (2026-10-04)
- **Severity:** MATERIAL PRODUCTION-WORKFLOW DEFECT; no production result affected.
- Matrix jobs upload `phase2-backtest-<bps>bps` artifacts, while the analysis job requests `slippage-*-bps`.
- **Impact:** combined analysis may receive none of the intended scenario artifacts.
- **Resolution required:** align artifact names/patterns and add a fail-closed assertion that all five registered scenarios are present before analysis.
