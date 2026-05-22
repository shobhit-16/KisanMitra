# TODO-04-SCHEME-ACCESS

**Status**: ACTIVE

## Description

Farmer Scheme Access: PM-KISAN enrollment eligibility + application workflow, Soil Health Card data integration, PMFBY enrollment support, scheme eligibility engine. Per `specs/05-scheme-access.md`, scheme access is a high-value intervention — reduces exclusion errors and increases effective coverage of government schemes.

## Spec Reference

- `specs/05-scheme-access.md` — PM-KISAN, PMFBY, Soil Health Card, Kisan Credit Card eligibility rules; tenant farmer pathways; women farmer access; document checklist generation; enrollment journey
- `specs/05-scheme-access.md §8` — Government API integration (where available), data quality handling

## Acceptance Criteria

- [ ] PM-KISAN eligibility engine at `src/indian_agri/schemes/pmkisan.py` — age check, land holding ≤2ha, land record verification, Aadhaar linkage, bank account validation; returns `eligible: bool + reason + action`
- [ ] PM-KISAN application workflow — document checklist generation per `specs/05-scheme-access.md §2.2`, application submission tracking, payment status tracking
- [ ] PMFBY eligibility engine at `src/indian_agri/schemes/pmfby.py` — loanee/non-loanee paths, rainfed crop detection, premium estimation, sum insured calculation
- [ ] Soil Health Card integration at `src/indian_agri/schemes/shc.py` — card data fetch (API or field agent input), N/P/K levels, pH, organic carbon, micronutrient status; link to LandHolding entity
- [ ] Scheme eligibility engine at `src/indian_agri/schemes/eligibility.py` — `recommend_schemes(farmer, land)` returning personalized scheme list per `specs/05-scheme-access.md §7.1`; filters by farmer segment, crop, state
- [ ] Tenant farmer pathway handling — `is_tenant()` detection, alternative scheme recommendations (state-specific per `specs/05-scheme-access.md §4.2`), cultivator certificate guidance
- [ ] Women farmer pathway — alternate contact (husband's phone), female field agent assignment recommendation, SHG linkage
- [ ] Document checklist generator — personalized per exclusion reason (name_mismatch, land_record_error, tenant, bank_account)
- [ ] Scheme benefit calculator at `src/indian_agri/schemes/calculator.py` — `estimate_scheme_benefits(farmer)` computing annual benefit from PM-KISAN, PMFBY, KCC
- [ ] Government API stubs: PM-KISAN beneficiary status API, SHC card data API, e-NAM transaction API (where APIs available); graceful degradation when APIs unavailable

## Subtasks

- [ ] BUILD-1 (Est: 2h) — PM-KISAN eligibility engine at `src/indian_agri/schemes/pmkisan.py` — `check_eligibility()` per `specs/05-scheme-access.md §2.1`, land record verification stub, exclusion reason classification
- [ ] BUILD-2 (Est: 2h) — PM-KISAN application workflow at `src/indian_agri/schemes/pmkisan_enrollment.py` — document checklist, submission tracking, status polling, payment alert
- [ ] BUILD-3 (Est: 2h) — PMFBY eligibility engine at `src/indian_agri/schemes/pmfby.py` — loanee/non-loanee, premium estimation, sum insured, `check_eligibility()` per `specs/05-scheme-access.md §2.1`
- [ ] BUILD-4 (Est: 2h) — Soil Health Card integration at `src/indian_agri/schemes/shc.py` — card data model, API fetch or field agent input, N/P/K/Ph/OC parsing, linking to LandHolding
- [ ] BUILD-5 (Est: 2h) — Scheme eligibility + recommendation engine at `src/indian_agri/schemes/eligibility.py` — `recommend_schemes()` per `specs/05-scheme-access.md §7.1`, state-specific scheme registry
- [ ] BUILD-6 (Est: 2h) — Tenant + women farmer pathways at `src/indian_agri/schemes/special_paths.py` — tenant detection, alternative schemes per state, women farmer handling
- [ ] BUILD-7 (Est: 2h) — Scheme benefit calculator at `src/indian_agri/schemes/calculator.py` — annual benefit estimation for PM-KISAN, PMFBY, KCC
- [ ] BUILD-8 (Est: 2h) — Government API integration stubs at `src/indian_agri/integrations/govApis.py` — PM-KISAN status API, SHC API, graceful degradation with farmer self-report fallback
- [ ] WIRE-1 (Est: 1h) — Wire scheme access into IVR: scheme eligibility check via IVR menu (press 3 for scheme info); suppression notifications apply — scheme recommendations suppressed when higher-priority constraint active
- [ ] WIRE-2 (Est: 1h) — Wire scheme enrollment status into farmer profile: `SchemeEnrollment` entity updated on successful enrollment; visible in village agent dashboard

## Definition of Done

- [ ] PM-KISAN eligibility check returns correct reason when excluded (land record error, tenant, bank account issue, name mismatch)
- [ ] Document checklist is personalized to exclusion reason — not a generic list
- [ ] Tenant farmer sees alternative scheme options, not a flat rejection
- [ ] e-NAM API returns real mandi data or degrades gracefully with cached data + staleness label
- [ ] Scheme benefit calculator shows annual benefit in rupees — "₹6,000 per year from PM-KISAN"
