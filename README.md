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

## Branch
phase-1-data-acquisition-validation.

## Latest Phase 1 controls
- Deterministic exact-row deduplication: `scripts/deduplicate_phase1_data.py`.
- Conflicting duplicate keys remain fatal.
- GitHub Actions concurrency/cache-save race mitigation added after E025.
