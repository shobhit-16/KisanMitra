# TODO-202-Backend-Farmer-State-Machine

**GitHub Issue**: N/A
**Status**: ACTIVE

## Description

Build farmer state management API that tracks CPE gate states, recommendation history, and season phase for each farmer.

## Context

The CPE engine needs to know each farmer's current state (healthy, cash_stress, crisis, harvest) to evaluate recommendations. Farmer state evolves based on obligations paid, sales recorded, and season progression.

## Acceptance Criteria

- [ ] `GET /api/farmers/{phone}/state` returns current farmer state with all 5 gate values
- [ ] `GET /api/farmers/{phone}/state/history` returns state change history
- [ ] State automatically updated when: obligation paid, sale recorded, season changes
- [ ] Season phase tracking: SOWING (Oct), GROWING (Nov-Jan), HARVEST (Feb-Mar)
- [ ] State refresh endpoint: `POST /api/farmers/{phone}/state/refresh`
- [ ] Farmer state persisted in SQLite, not recomputed on every request

## Subtasks

- [ ] Define FarmerState model (Est: 1h) - gate values, season_phase, state_category, last_updated
- [ ] Implement state transition logic (Est: 2h) - when and how state changes
- [ ] Create FarmerStateRepository (Est: 1h) - persistence layer
- [ ] Add state refresh workflow (Est: 1h) - recompute all gates from current data
- [ ] Wire into Kailash (Est: 1h)
- [ ] Write tests (Est: 1h)

## Definition of Done

- [ ] All acceptance criteria met
- [ ] State transitions match demo.html scenario changes
- [ ] Season phase auto-updates based on date

## Dependencies

- TODO-101 (Obligation Calendar)
- TODO-102 (Income Ledger)
- TODO-201 (CPE Engine)
