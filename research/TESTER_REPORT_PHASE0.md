# Independent Tester Report — Phase 0

**Repository:** vishnuvcr/Iron-condor-to-ratio-v1  
**Role:** Tester  
**Branch:** tester/phase-0-audit  
**Audit date:** 2026-10-03  
**Scope:** Phase 0 specification, source fidelity, research controls, data plan, reproducibility readiness, and gate compliance.

## 1. Verdict

**FAIL — corrections required before Phase 1 can be approved.**

The repository has a solid control structure and the core strategy description is substantially faithful to the uploaded transcript. However, several execution-critical definitions remain unresolved. These are not cosmetic issues: without them, two independent implementations can produce materially different trades and performance.

No Phase 1 data acquisition or Phase 2 backtest implementation should be treated as an approved production research step until the corrections below are addressed and re-tested.

## 2. Checks performed

| Check | Result | Finding |
|---|---|---|
| Repository controls present | PASS | Project instructions, plan, status, error log and conversation log exist. |
| Separate phase branch discipline documented | PASS | Phase 0 branch exists and project instructions require separate phase branches. |
| Tester gate documented | PASS | Status and handoff explicitly block Phase 1 pending tester approval. |
| Source strategy fidelity | PASS WITH CORRECTIONS | Main structural rules match the transcript, but delta/sign/trigger semantics need formalization. |
| Discretionary rules isolated | PASS | Profit-taking and expiry-day discretion are explicitly kept outside the deterministic core. |
| Intraday data requirement | PASS | Repository correctly identifies intraday option data as necessary. |
| Cost/friction requirement | PASS | Plan requires slippage, brokerage and applicable charges. |
| Data provenance/licensing control | PASS | Provenance and licensing are identified as Phase 1 requirements. |
| Deterministic implementation readiness | FAIL | Trigger frequency, delta definition, strike selection, entry timing and fill semantics remain open. |
| No hidden dependency | FAIL | Exact historical bid/ask/Greek availability is unresolved and is essential to a realistic implementation. |
| Literature/data review completeness | PARTIAL | Scoping review is useful, but it should be refreshed and independently sourced before being called comprehensive. |
| README/status consistency | FAIL | Main README still says the current role is Developer; this tester audit must be reflected on the tester branch and later reconciled by the developer. |

## 3. Source-fidelity audit

The transcript supports the following core structure:

1. Initial monthly Iron Condor: short call and short put around 0.30 delta; long call and put around 0.10 delta.
2. When an IC short leg reaches approximately 0.10 delta, exit the IC and transition to a directional ratio.
3. Downward move -> call-side ratio; upward move -> put-side ratio.
4. Initial ratio: long approximately 0.50 delta, short two lots approximately 0.40 delta, hedge approximately 0.10 delta.
5. Same-direction continuation: when combined short-leg delta falls from approximately 0.80 toward 0.20, reset to approximately 0.40 / short 2 x 0.30 / hedge 0.08.
6. Reversal: when the combined short-leg delta rises to roughly 1.20–1.30, exit and switch to the opposite directional ratio.

These are supported by the uploaded transcript and are correctly represented in the repository's source-derived specification.

### Important semantic correction

The implementation must define whether delta thresholds use:

- absolute delta magnitude,
- signed option delta,
- platform-displayed delta,
- or another convention.

For example, the put short has negative Black-Scholes delta while the call short has positive delta. The video's language such as 0.30 delta, 0.10 delta, 0.80 combined delta and 1.20–1.30 is operationally understandable in context but is not sufficient as machine-readable mathematics.

**Required correction:** define a canonical quantity such as abs(delta) for individual legs and sum(abs(delta)) for the two short legs, if that is the intended interpretation, and explicitly document it before production testing.

## 4. Execution-critical gaps

### 4.1 Trigger sampling frequency — BLOCKER

The video describes monitoring delta continuously, but the transcript does not establish whether a backtest should evaluate:

- every tick,
- every quote,
- every 1-minute bar,
- bar close,
- bar high/low,
- or another event.

A 1-minute close-only implementation can miss a trigger crossed intra-minute.

**Required:** specify the event frequency and the rule for a trigger crossed between observations.

### 4.2 Delta source/model — BLOCKER

The video uses displayed deltas but does not identify the exact Greek calculation/model.

The backtest must specify whether it uses:

- vendor-provided historical Greeks,
- Black-Scholes,
- Black-76,
- an implied-volatility surface,
- or another model.

If Greeks are reconstructed, the methodology must state the volatility input, rate/dividend assumptions, interpolation and treatment of stale/illiquid contracts.

### 4.3 Strike-selection algorithm — BLOCKER

0.30 delta, 0.10 delta, etc. are target values, not necessarily exact listed contracts.

The engine must specify:

- nearest delta vs nearest strike,
- tie-breaking,
- maximum delta error,
- whether call/put selection is performed independently,
- what happens when no valid contract is available,
- whether the target is selected from the full expiry chain or only a liquidity-filtered subset.

### 4.4 Entry timing — BLOCKER

The transcript demonstrates examples involving entry one trading day before monthly expiry and references a 5:15 PM setup screen, but this is not enough to establish a universal rule.

A production backtest must explicitly define:

- monthly expiry identification,
- entry date,
- entry time,
- whether entry occurs at market open, close, or another timestamp,
- and what happens when the exchange session has changed.

### 4.5 Fill model — BLOCKER

The strategy performs multi-leg exits and entries. Using a single mid-price for an entire multi-leg structure can materially overstate execution quality.

The engine should use, in descending preference:

1. contemporaneous bid/ask quotes;
2. a documented conservative fill rule if quotes are unavailable;
3. configurable stress slippage.

The report must separately show gross P&L and net P&L after execution costs.

### 4.6 Trigger-to-fill ordering — BLOCKER

When a trigger occurs, the system needs an unambiguous sequence:

1. observe trigger;
2. mark old position for exit;
3. execute exit;
4. determine new target strikes using information available at that point;
5. execute new ratio;
6. record transaction costs.

The new strike selection must not use future information.

### 4.7 Expiry-day and profit-taking — CORRECTLY ISOLATED

The video contains discretionary examples of taking profits early and sometimes discussing expiry-day management. The repository correctly avoids silently turning these into core rules.

The developer should preserve this separation. Any discretionary rule should be tested as a clearly named sensitivity/variant, never mixed into the literal core result.

## 5. Mathematical/state-machine risks

The eventual engine should explicitly test:

- signed versus absolute delta;
- the direction mapping;
- combined short delta calculation;
- crossing versus equality at thresholds;
- repeated continuation resets;
- reversal after a continuation reset;
- multiple triggers within the same observation interval;
- zero/negative net-credit cases;
- unavailable target strikes;
- expiry crossing;
- stale option prices;
- contracts with zero volume/open interest;
- partial or impossible fills.

A particularly important invariant is that the ratio construction must have exactly the intended net option quantities and hedge direction after every reset. Unit tests should calculate the position Greeks from individual legs and verify the expected qualitative delta exposure.

## 6. Data-source audit

The repository's conclusion that daily NSE reports alone are insufficient is correct. NSE currently exposes historical derivatives reports and contract-wise price/volume information, while its historical-data offering also includes historical order/trade data. These sources should be used where appropriate for reference/validation, but the production strategy trigger still requires sufficiently granular intraday option observations.

Open-source ICICI Breeze tooling demonstrates that 1-minute NIFTY option OHLCV/OI data can be accessed for specific contracts, subject to the API/data-access constraints. This supports the repository's identification of broker/API-derived intraday data as a possible acquisition route, but does not establish complete historical coverage for this project.

**Tester requirement:** Phase 1 must document exact dataset coverage, missingness, licensing, contract continuity, timestamps, bid/ask availability, and historical Greeks before the dataset is accepted for the primary backtest.

## 7. Literature-review audit

The existing review is appropriately cautious about not treating prior literature as proof that this strategy works. Independent checking confirms relevant background evidence:

- Dziawgo's 2020 paper discusses iron-condor structure and the effects of underlying price on delta, gamma, vega and theta; it is relevant background but is not evidence for this NIFTY transition system.
- Bhat and co-author research examines day/night asymmetry in NIFTY option returns, which supports careful treatment of timing but does not validate this strategy.
- Research on variance-risk premia in Indian/NIFTY options provides relevant context for short-volatility exposure, but published estimates differ by sample, methodology and implementation costs.
- Recent NIFTY research using large intraday datasets reinforces the value of intraday data and regime analysis, but such work should be treated as contextual evidence rather than direct validation.
- A recent NIFTY short-volatility backtest explicitly models brokerage, STT and slippage and reports materially different net outcomes from gross option-premium intuition, reinforcing the need for a transparent friction model. This is an external study, not evidence that its assumptions should be copied into this project.

**Required correction:** before the literature review is called final/comprehensive, refresh it with a reproducible bibliography and explicitly classify peer-reviewed papers, preprints, vendor documentation, GitHub projects and other sources by evidence quality and relevance.

## 8. Cost-model audit

The plan correctly requires brokerage, transaction charges, slippage and applicable taxes/fees.

The implementation specification should additionally distinguish:

- brokerage per executed leg/order;
- exchange transaction charges;
- SEBI charges;
- GST;
- stamp duty;
- STT/CTT as applicable to the exact option transaction and side;
- any applicable regulatory or clearing charges;
- slippage;
- bid/ask spread;
- rejected/partial fills if modeled;
- margin/capital opportunity cost.

The exact Paytm Money schedule must be verified from contemporaneous official documentation for the period being backtested; it must not be assumed from a generic broker-cost template.

## 9. Regime and external-factor requirements

The research plan appropriately includes regime analysis. The tester recommends that Phase 3 explicitly tag, where data permit:

- India VIX / implied-volatility regime;
- realized volatility;
- gap versus intraday movement;
- trend/range measures;
- major market stress periods;
- FII/DII activity where available;
- major scheduled macro events;
- global index/overnight-market moves.

These are explanatory variables and stratification variables, not additional trading signals unless separately pre-specified.

## 10. Phase-gate decision

**Phase 0 tester decision: NOT APPROVED for Phase 1 production progression.**

Phase 1 may be prepared only after the developer resolves the blockers above in a revised specification and submits it for a second tester check.

### Minimum conditions for re-test

1. Canonical delta/sign definitions.
2. Trigger sampling and crossing rules.
3. Deterministic entry timing.
4. Deterministic target-strike selection.
5. Data-source/Greek methodology.
6. Execution/fill/slippage rules.
7. Trigger-to-fill sequencing and no-look-ahead guarantee.
8. Explicit expiry and position-forced-exit rules for the literal core.
9. Cost-model specification with broker-period verification.
10. Updated status/error log and README.
11. Unit-test requirements for position quantities, delta arithmetic and state transitions.

## 11. What was NOT found

No evidence was found in the audited repository of:

- a production backtest engine;
- a production historical dataset;
- a production performance result;
- a validated strategy return;
- an optimization result;
- a completed Phase 1 dataset;
- a completed Phase 2 engine.

Therefore no performance conclusion should be reported at this stage.

## 12. Final tester statement

The project has a credible research-control foundation and a substantially faithful transcription of the source strategy. The principal issue is **not that the strategy was mistranscribed**; it is that the source itself leaves enough execution detail unspecified that a production backtest could otherwise become implementation-dependent.

The next developer revision should make the unresolved semantics explicit, without inventing undocumented trading preferences. The revised specification should then return to the tester for independent re-validation before production Phase 1/Phase 2 work proceeds.
