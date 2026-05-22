# TODO-302-Integrations-Govt-Scheme-APIs

**GitHub Issue**: N/A
**Status**: ACTIVE

## Description

Integrate PM-KISAN and Ayushman eligibility check APIs for government scheme recommendations.

## Context

Demo.html shows PM-KISAN (10,000/year), Ayushman (5 lakh free treatment), Soil Health Card subsidy. Need to check eligibility and return scheme details.

## Acceptance Criteria

- [ ] `GET /api/schemes/pmkisan/check?aadhaar={aadhaar}` returns PM-KISAN eligibility and next installment date
- [ ] `GET /api/schemes/ayushman/check?aadhaar={aadhaar}` returns Ayushman coverage status
- [ ] `GET /api/schemes/eligible?phone={phone}` returns all schemes farmer is eligible for
- [ ] Eligibility check does NOT submit applications (pilot scope - just information)
- [ ] Mock responses for pilot (actual APIs require official partnerships)

## Subtasks

- [ ] Research PM-KISAN API availability (Est: 2h) - determine if mock or real API
- [ ] Create scheme eligibility checker (Est: 1h) - logic for PM-KISAN, Ayushman
- [ ] Add scheme data model (Est: 1h) - name, amount, eligibility criteria, application steps
- [ ] Wire eligible schemes into recommendation bus (Est: 1h)
- [ ] Write unit tests (Est: 1h)

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Ayushman shown for HEALTH_CRISIS farmers only (Gate 1 filter)

## Dependencies

- TODO-000 (Project Scaffold)
- TODO-201 (CPE Engine)
