# TODO-201-Backend-CPE-Engine

**GitHub Issue**: N/A
**Status**: ACTIVE

## Description

Build the Constraint Priority Engine (CPE) - 5-gate rule engine that filters recommendations based on farmer state.

## Context

Demo.html Screen 8 (CPE Simulator) shows 4 scenarios (healthy, cash_stress, crisis, harvest) with 5 gates:
- Gate 1: Resource Category (HEALTH_CRISIS, CASH_STRESS, NORMAL)
- Gate 2: Weather Fit (seasonal weather conditions)
- Gate 3: Cash Flow (30-day surplus status)
- Gate 4: Selling Window (harvest timing, price peak window)
- Gate 5: Loan Compliance (KCC repayment status)

## Acceptance Criteria

- [ ] `POST /api/cpe/evaluate` evaluates a recommendation against farmer's 5-gate state
- [ ] Gate 1: HEALTH_CRISIS unlocks Ayushman, suppresses commercial credit recommendations
- [ ] Gate 2: Weather unfit blocks pesticide recommendations during heavy rain
- [ ] Gate 3: Cash flow deficit blocks fertilizer credit, delays non-urgent recommendations
- [ ] Gate 4: Selling window status affects when market-price recommendations fire
- [ ] Gate 5: Loan compliance blocks new credit if KCC EMI overdue
- [ ] Each gate returns pass/block/partial with reason text
- [ ] Recommendation bus: recommendations enter, CPE filters, approved recommendations exit
- [ ] API matches demo.html 4-scenario behavior exactly

## Subtasks

- [ ] Define CPEGateState model (Est: 1h) - all 5 gate fields with pass/block/partial enum
- [ ] Implement Gate 1: Resource Category classifier (Est: 1h) - HEALTH_CRISIS detection
- [ ] Implement Gate 2: Weather fit checker (Est: 1h) - uses IMD weather data
- [ ] Implement Gate 3: Cash flow evaluator (Est: 1h) - from TODO-101 surplus calculation
- [ ] Implement Gate 4: Selling window evaluator (Est: 1h) - harvest timing logic
- [ ] Implement Gate 5: Loan compliance checker (Est: 1h) - KCC EMI status
- [ ] Build RecommendationBus (Est: 1h) - in → CPE filters → out
- [ ] Wire into Kailash workflow (Est: 1h)
- [ ] Write tests for all 4 demo scenarios (Est: 2h)

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Cash stress scenario correctly blocks urea recommendation (Gate 3)
- [ ] Health crisis scenario unlocks Ayushman only (Gate 1)
- [ ] Demo.html CPE simulator behavior exactly replicated

## Dependencies

- TODO-101 (Obligation Calendar)
- TODO-200 (Income Engine API)
- TODO-302 (IMD Weather Integration)
