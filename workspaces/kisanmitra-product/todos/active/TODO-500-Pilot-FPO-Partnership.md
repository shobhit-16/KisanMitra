# TODO-500-Pilot-FPO-Partnership

**GitHub Issue**: N/A
**Status**: ACTIVE

## Description

Establish pilot partnerships with 1-2 Nashik FPOs for farmer enrollment and baseline measurement.

## Context

GTM strategy: Nashik district first (1-2 FPOs, 100 farmers), then Maharashtra, then national. Demo.html shows 3 FPOs: Nashik Krishi Sangh FPC (3km), Niphad Onion Growers FPC (7km), Shri Sant Kabir Pulses FPC (12km).

## Acceptance Criteria

- [ ] Identify 1 FPO partner in Niphad/Ozar area for pilot
- [ ] Create FPO onboarding flow: registration, KYC verification, agreement
- [ ] Create FPO dashboard: view enrolled farmers, aggregate metrics
- [ ] Enroll first 10 farmers for pilot (internal testing)
- [ ] Baseline measurements: farmer profile completeness, obligation tracking started
- [ ] Signed MOU or informal agreement with FPO leadership
- [ ] **Test coverage:** FPO registration API tests with ≥80% coverage
- [ ] **Test coverage:** Enrollment flow tests: referral code, profile creation
- [ ] **Test coverage:** Metrics aggregation tests: per-FPO and overall pilot metrics

## Subtasks

- [ ] Research FPO contacts in Niphad/Ozar (Est: 3h) - existing networks, government contacts
- [ ] Draft FPO partnership agreement (Est: 2h) - terms, data sharing, mutual benefits
- [ ] Create FPO registration API (Est: 2h) - name, location, contact, services
- [ ] Create FPO dashboard endpoints (Est: 3h) - enrolled farmer count, metrics aggregation
- [ ] Create farmer enrollment flow (Est: 2h) - FPO referral code, streamlined signup
- [ ] Document pilot baseline metrics (Est: 1h) - what to measure

## Definition of Done

- [ ] All acceptance criteria met
- [ ] At least 1 FPO partnership established
- [ ] First 10 farmers enrolled with complete profiles

## Dependencies

- TODO-100 (Farmer Profile CRUD)
