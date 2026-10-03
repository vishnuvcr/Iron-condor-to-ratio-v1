# Iron Condor to Ratio v1

Research project to reproduce and independently backtest the YouTube strategy “What If the Iron Condor Starts Trending? Ratio Spread Strategy”.

## Current role
Developer.

## Current phase
**Phase 1 — data acquisition and validation: IN PROGRESS. Phase 0 is APPROVED.**

## Gate
Phase 1 is active but not yet approved for Phase 2. The independent tester gate remains mandatory.

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
phase-1-data-acquisition-validation.

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
