# E-Cell / Hero Housing submission audit
Updated 7 November 2026. Deadline: **8 November**, confirmed by the user; exact cutoff time and upload format still unconfirmed.

## Authoritative scope
Source: [Hero Housing Fintech Challenge problem statements](https://docs.google.com/presentation/d/1TRd67oaFJUE5jlbIFhi199VV2B7_E3q5/edit), supplied by the user and read via Drive.

GroundValue aligns with **Problem Statement 1: AI-Powered Digital Property Valuation Engine for India**. The rules require one solution for one problem statement, teams of 1–4, original work with sources cited, and coverage of all six listed points. A prototype or architecture diagram is welcome. The brief does not specify a mandatory trained model artifact, public deployment, video length, slide count, or submission cutoff time. Do not infer these from earlier internal plans.

Judging: accuracy/feasibility, data use, explainability, regulatory fit, scalability, presentation clarity.

## Requirements against the code
| Requirement | Present now | Missing / submission action |
|---|---|---|
| 1. Scope market | Electronic City, Bengaluru apartment asking-price research; validates city, locality, bedrooms and area | Explicit residential AND commercial expansion strategy. State initial scope honestly; do not label current engine pan-India. |
| 2. Combine sources | Listing-source connectors, property attributes, normalization, deduplication, source URLs and exclusion reasons | Verified transaction/government integration, geocoding, imagery, infrastructure and time-series features. Describe collection rights, parcel/property linkage, timestamps and conflict resolution. |
| 3. AI/ML and accuracy | Deterministic median comparable asking-rate baseline; no trained sale-price model | Model/features design, transaction-label dataset, leakage-safe evaluation, AVM benchmark access, measured results. Higher accuracy is currently unproven. |
| 4. Explainability | Estimate, observed comparison band, formula, evidence records, warnings, history and exports | Calibrated uncertainty, per-feature model explanation, versioned model/data provenance and reviewer decisions. Existing percentile band is NOT confidence. |
| 5. Automate/scale | Background research, progress, cancellation, persisted runs | Queue/workers, multi-user isolation, auth, service monitoring, city adapters, performance/cost evidence. Current manager is single-process; static hosting does not deploy the Python backend. |
| 6. Lending decisions | Research report can inform an analyst | Explicit lender flow, evidence-based referral, risk/coverage flags, approval ownership and audit trail. Current output must not automatically approve loans or substitute for a formal valuation. |

## Immediate implementation findings
Both root and real_groundvalue contain matching API/frontend copies; fixes were mirrored to avoid leaving the Git checkout behind.
- FIXED: API previously passed a property ID string where the worker requires a validated Property object; now links the run to its project.
- FIXED: detail endpoint attempted to JSON-decode an already-decoded property dict.
- FIXED: estimate range/rate and accepted-comparable fields mismatched the core engine.
- FIXED: pending runs with a null report crashed report-reading routes.
- FIXED: invalid sources/properties rejected before a provider call; invalid area rejected on create.
- FIXED: frontend now surfaces failed API responses instead of treating them as successful research.
- FIXED: default backend port now matches frontend 5001; Flask dependencies declared.
- FIXED: dashboard test expected an old heading.
- Verification: 42 local backend/UI tests pass, including six new API contract tests. No paid live provider run or browser verification performed in this audit.
- STILL OPEN: deployed frontend hardcodes localhost API, Vercel config hosts static files only; public end-to-end deployment is not established.
- STILL OPEN: start.sh uses system Python and outdated port instructions; use the tested virtual environment for demonstrations.
- STILL OPEN: a larger set of nearby localities is accepted as Electronic City in core.py. Audit geographic boundaries before claiming locality-level valuation accuracy.
- STILL OPEN: API is local-demo oriented: permissive CORS, no user auth, debug server, no ownership isolation. Do not expose as a production lender service.

## Deadline order
1. Finish a submission narrative covering all six points (draft in ECELL_SOLUTION_DESIGN.md), with implemented/proposed labels and citations.
2. Prepare one reproducible demo: input → research/source trace → evidence/exclusions → estimate or explicit insufficiency → saved report/export. Keep a clearly labeled recorded run as backup; do not pass synthetic observations off as live data.
3. Add lender review/referral and an audit record to the report/workspace. Treat listing-only evidence as research support, not a lending valuation.
4. Prepare a reproducible model/evaluation pipeline only if a legitimately usable transaction-label dataset is available. Otherwise show methodology and explicitly report results as pending. Do not train on a tiny scraped sample and claim AVM superiority.
5. Assemble the final submission artifact in the portal's required format; verify team details, citations, access permissions, and cutoff time.

## Large gaps that cannot be honestly solved with UI work
Verified sale-price ground truth; evidence of outperforming existing AVMs; calibrated coverage on independent data; nationwide/commercial generalization; operational lending validation. These require datasets, evaluation, and partner access, not cosmetic confidence scores.

## Final acceptance checklist
- [ ] Six requirements visibly covered in submission
- [ ] Current prototype and proposed engine distinguished
- [ ] No unsupported accuracy, confidence, regulatory-compliance or nationwide-coverage claims
- [ ] Data/source citations and access rights included
- [ ] Live/recorded demo verified and labelled
- [ ] Lender workflow/referral shown
- [ ] Exact upload format, deadline time and portal confirmed
- [ ] Team (1–4) and submission access verified
