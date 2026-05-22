# TODO-203-Backend-Emergency-Credit-Pathway

**GitHub Issue**: N/A
**Status**: ACTIVE

## Description

Build emergency credit pathway API for Ayushman eligibility checking and crisis resource routing.

## Context

Demo.html Screen 7 (Credit) shows emergency credit pathway with Ayushman Bharat (5 lakh free treatment). Only HEALTH_CRISIS resource category unlocks this (Gate 1). Commercial credit and gold loans are blocked for crisis situations.

## Acceptance Criteria

- [ ] `GET /api/farmers/{phone}/credit/emergency` returns available emergency resources
- [ ] Ayushman eligibility check: PM-KISAN status, Aadhaar linkage
- [ ] Gate 1 filter: only HEALTH_CRISIS category shows Ayushman
- [ ] Commercial credit (12% interest) blocked for HEALTH_CRISIS farmers
- [ ] Gold loan (9% interest) blocked for HEALTH_CRISIS farmers
- [ ] Crisis resource recommendation: prioritize grants/govt schemes over loans
- [ ] Unit tests for credit pathway scenarios

## Subtasks

- [ ] Define CreditResource model (Est: 1h) - type, name, amount, interest_rate, eligibility_criteria
- [ ] Implement Ayushman eligibility check (Est: 1h) - PM-KISAN linkage check
- [ ] Implement Gate 1 credit filter (Est: 1h) - HEALTH_CRISIS only unlocks Ayushman
- [ ] Implement resource suppression logic (Est: 1h) - commercial credit hidden for crisis
- [ ] Create credit recommendation ranker (Est: 1h) - grants > subsidized > commercial
- [ ] Wire into Kailash workflow (Est: 1h)
- [ ] Write tests for all 3 demo scenarios (Est: 1h)

## Definition of Done

- [ ] All acceptance criteria met
- [ ] HEALTH_CRISIS farmer sees only Ayushman
- [ ] Demo.html suppressed credit cards behavior replicated exactly

## Dependencies

- TODO-201 (CPE Engine)
- TODO-302 (Govt Scheme APIs)
