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

| E070 | 2026-10-03 | 1 / G6 | Historical r/q source identification is available, but a complete date-aligned machine-readable production series has not yet been assembled. | Using sampled pages or current rates would create incomplete or potentially look-ahead-contaminated Greek inputs. | Registered official RBI/NSE Indices sources, froze a strict pre-trading-date source rule, and kept G6 OPEN until full production inputs and solver evidence exist. |


## E072 — 2026-10-04 — G6 source acquisition evidence boundary
- G6 source identification was previously documented, but no automated retained acquisition artifact existed yet.
- Impact: source provenance could be cited, but exact acquired bytes and acquisition outcome were not reproducibly captured by the repository workflow.
- Resolution: added a source-acquisition/hash script and GitHub Actions workflow with unconditional evidence upload. The artifact is explicitly non-accepting: it cannot promote G6 without full-period date-aligned r/q and production IV/Greek reconstruction.

| E074 | 2026-10-04 | 1 | Independent tester PR #36 found the G6 official-source acquisition workflow lacked cache restore/save. | Repeated G6 source-audit runs could reacquire the same official inputs unnecessarily and did not satisfy the project's required cache/reuse control. | Added deterministic restore/save caching keyed to the G6 control-source manifest and acquisition script; cache paths cover the G6 source staging directory. G6 remains OPEN because source acquisition alone does not constitute complete r/q production inputs or IV/Greek acceptance. |
