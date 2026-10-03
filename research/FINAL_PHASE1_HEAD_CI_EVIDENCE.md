# Final Phase 1 Head CI Evidence

Date: 2026-10-03

## Exact final-head execution

- Developer branch final head: `09c4c2e4b6bc569d42d4743fac5132ad0672f8d8`
- GitHub Actions run: `37125656878`
- Job/check: `111210327724`
- Artifact: `11275311823`
- Artifact SHA-256: `754a71a1b50f532b49e43be45f24ddc3eab80a4aa56df1f43b23f0030f04aa9c`
- Workflow conclusion: SUCCESS
- The run head SHA exactly equals the developer branch final head, satisfying E045's final-head requirement.

## G4 reconciliation result

- Normal eligible dates: 1,254
- Special sessions reconciled: 7
- Data-gap exclusions: 1
- Unreconciled dates: 0
- Controlled anomalies: 2021-06-28, 2026-06-03, 2026-07-01
- No unresolved-date escape hatch exists in the corrected manifest.
- Special-session execution intervals are checked for observed coverage.
- Every observed timestamp is checked against either the documented F&O execution interval or the documented exchange source-observation interval.

## Special-session evidence

- 2021-11-04: F&O 18:15–19:15; source observations covered by NSE capital-market Muhurat schedule.
- 2022-10-24: F&O 18:15–19:15; source observations covered by NSE capital-market Muhurat schedule.
- 2023-11-12: F&O 18:15–19:15; source observations covered by NSE capital-market Muhurat schedule.
- 2024-03-02: F&O 09:15–10:00 and 11:30–12:30; source observations covered by the documented CM/DR schedule.
- 2024-05-18: F&O 09:15–10:00 and 11:30–12:30; source observations covered by the documented CM/DR schedule.
- 2024-11-01: F&O 18:00–19:00; source observations covered by the documented CM Muhurat schedule.
- 2025-10-21: F&O 13:45–14:45; source observations covered by the documented CM Muhurat schedule.

## Gate status

This file records developer evidence only. G4/G12 are not marked independently accepted here. G13 remains blocked until the independent tester reviews this exact final-head execution. G14/Phase 2 remain blocked.
