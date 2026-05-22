# TODO-200-Backend-Income-Engine-API

**GitHub Issue**: N/A
**Status**: ACTIVE

## Description

Build the Income Engine API combining mandi price fetching, selling recommendation, and cash flow into a unified income assessment endpoint.

## Context

Demo.html Screen 4 (Sell Decision) combines mandi prices, storage math, and cash flow to recommend store-vs-sell. The backend needs a unified engine that evaluates the farmer's complete financial picture.

## Acceptance Criteria

- [ ] `GET /api/farmers/{phone}/income-engine` returns comprehensive income assessment
- [ ] Assessment includes: current mandi price, storage cost estimate, recommended action (store/sell/hold)
- [ ] Selling recommendation considers: Gate 4 status, cash flow health, obligation urgency
- [ ] Net gain calculation: `(expected_price - current_price) * quantity - storage_cost`
- [ ] MSP comparison always included in response
- [ ] All 17 screens' backend endpoints wired and returning real data (not mocks)
- [ ] **Test coverage:** Unit tests for sell/store/hold decision logic with ≥80% coverage on calculation logic
- [ ] **Test coverage:** Tier-2 integration tests against real SQLite for income engine with farmer state
- [ ] **Test coverage:** Emergency sell trigger tests (cash crisis, health crisis, KCC EMI ≤3 days)

## Subtasks

- [ ] Design IncomeEngine input/output schema (Est: 1h) - FarmerState dataclass with all gates
- [ ] Implement sell recommendation logic (Est: 2h) - store vs sell decision tree
- [ ] Add storage cost estimation (Est: 30 min) - per-quintal storage rates
- [ ] Add MSP comparison math (Est: 30 min) - always show MSP floor advantage
- [ ] Wire with mandi prices from external API (Est: 1h) - TODO-301
- [ ] Wire with cash flow assessment (Est: 30 min) - from TODO-101
- [ ] Write integration tests (Est: 1h)

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Rambhau with 5q at 28/q shows store recommendation with net gain math
- [ ] Response matches demo.html sell screen logic

## Dependencies

- TODO-101 (Obligation Calendar)
- TODO-102 (Income Ledger)
- TODO-301 (eNAM Mandi Integration)
