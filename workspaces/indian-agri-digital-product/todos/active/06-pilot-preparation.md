# TODO-06-PILOT-PREPARATION

**Status**: ACTIVE

## Description

Pilot preparation for Maharashtra (Nashik + Ahmednagar) and Karnataka (Dharwad + Belgaum) launch in June. Farmer enrollment workflow with constraint state data collection, Gate 2/3 validation data collection, ground truth data collection infrastructure, field agent mobile app.

Per `specs/17-geography-pilot-demography.md §2`, pilot: 2,000 farmers across 4 districts, 12-month minimum (one complete kharif + rabi cycle), 18-month recommended.

## Spec Reference

- `specs/17-geography-pilot-demography.md` — pilot strategy, village selection criteria, sample size (2,000 farmers), field agent model, data collection during pilot
- `specs/17-geography-pilot-demography.md §3` — target demographics: 0.5-2.5ha operational holding, 30-35% tenant farmer inclusion, 30% women farmers, Marathi + Kannada languages
- `specs/17-geography-pilot-demography.md §5.1-5.5` — CPE gate implications for pilot design
- `specs/15-ground-challenges-practical-feasibility.md §1` — offline-first, queue-and-sync; Challenge 1 safeguards

## Acceptance Criteria

- [ ] Farmer enrollment workflow at `src/indian_agri/pilot/enrollment.py` — constraint state initial data collection at onboarding: health_status (default: normal), tenure_type (from land_tenure), cash_flow_status (initial assessment), selling_window (default: closed), time_criticality (from crop cycle)
- [ ] Gate 2 (Tenure) validation data collection — land_tenure capture (owner/tenant/lease/community), tenant detection protocol, "unverified" flag for self-reported tenure per `specs/17-geography-pilot-demography.md §5.2`
- [ ] Gate 3 (Cash Flow) validation data collection — 90-day expenditure recall survey at enrollment, obligation calendar initial capture, cash flow status baseline
- [ ] Crop cycle data collection — sowing date, expected harvest date, area_sown, crop_code; time_criticality derivation per `specs/09-constraint-priority-engine.md §2.4`
- [ ] Ground truth data collection infrastructure — actual selling prices at 7/30/60 days post-harvest, mandi visited, distress_sale_flag; agent recall survey form
- [ ] Field agent mobile app API at `src/indian_agri/agents/mobile_api.py` — farmer enrollment form, constraint state update, crop log submission, recommendation delivery confirmation, feedback capture
- [ ] Women farmer enrollment support — SHG linkage, female field agent assignment, alternate contact (husband's phone as secondary)
- [ ] Language support: Marathi + Kannada enrollment forms; IVR content in both languages
- [ ] Village agent performance tracking — farmers per agent, advisory delivery rate, scheme application success rate per `specs/06-delivery-channels.md §6.4`
- [ ] Enrollment buffer: system supports 2,500 enrolled to yield 2,000 active cohort (20% attrition)

## Subtasks

- [ ] BUILD-1 (Est: 2h) — Enrollment workflow at `src/indian_agri/pilot/enrollment.py` — multi-step enrollment form, constraint state initial data, land tenure capture, consent status management
- [ ] BUILD-2 (Est: 2h) — Gate 2 validation data collection at `src/indian_agri/pilot/gate2_validation.py` — tenant detection form, unverified flag, lease agreement documentation stub, field agent attestation
- [ ] BUILD-3 (Est: 2h) — Gate 3 validation data collection at `src/indian_agri/pilot/gate3_validation.py` — 90-day expenditure recall survey, obligation calendar initial capture, cash flow baseline assessment
- [ ] BUILD-4 (Est: 2h) — Ground truth collection at `src/indian_agri/pilot/ground_truth.py` — selling price recall at 7/30/60 days, mandi visited, distress sale flag, agent survey forms
- [ ] BUILD-5 (Est: 3h) — Field agent mobile API at `src/indian_agri/agents/mobile_api.py` — FastAPI endpoints for enrollment, constraint state update, crop log, recommendation delivery, feedback; offline-capable (accepts queued submissions)
- [ ] BUILD-6 (Est: 2h) — Women farmer enrollment support at `src/indian_agri/pilot/women_enrollment.py` — SHG linkage, female agent assignment, alternate contact management
- [ ] BUILD-7 (Est: 2h) — Language infrastructure at `src/indian_agri/i18n/` — Marathi + Kannada translations for enrollment forms, IVR content, suppression notifications; language detection from farmer profile
- [ ] WIRE-1 (Est: 1h) — Wire enrollment into CPE: enrolled farmer's constraint state immediately available to CPE; enrollment completion triggers first CPE evaluation
- [ ] WIRE-2 (Est: 1h) — Wire ground truth into Income Engine: selling price data populates Module 6 (IncomeLedger); Module 3 (MandiPriceVisibility) uses ground truth to calibrate price accuracy

## Definition of Done

- [ ] Enrollment form captures all fields needed for CPE constraint state + Gate 2/3 validation
- [ ] Field agent mobile API accepts offline submissions; syncs when connected
- [ ] Ground truth recall survey scheduled automatically at 7/30/60 days post-harvest
- [ ] Tenant farmer detected and flagged as "unverified" at enrollment
- [ ] Women farmer enrollment achieves 30% target via SHG linkage and female agent assignment
