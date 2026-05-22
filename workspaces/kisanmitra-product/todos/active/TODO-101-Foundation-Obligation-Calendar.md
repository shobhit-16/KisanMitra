# TODO-101-Foundation-Obligation-Calendar

**GitHub Issue**: N/A
**Status**: ACTIVE

## Description

Build obligation calendar API for tracking farmer financial obligations (KCC EMI, school fees, land rent) with reminder scheduling.

## Context

Demo.html Screen 2 shows obligation tracking with KCC EMI (7 days), school fee (30 days), land rent (60+ days). Need API to add, view, set reminders for obligations.

## Acceptance Criteria

- [ ] `POST /api/farmers/{phone}/obligations` creates obligation with type, amount, due_date, reminder_date
- [ ] `GET /api/farmers/{phone}/obligations` lists all obligations for farmer, sorted by due_date
- [ ] `GET /api/farmers/{phone}/obligations/urgent` returns obligations due within 7 days
- [ ] `PUT /api/farmers/{phone}/obligations/{id}/reminder` sets/removes reminder_flag
- [ ] `DELETE /api/farmers/{phone}/obligations/{id}` marks obligation as paid
- [ ] Cash flow assessment endpoint: `GET /api/farmers/{phone}/cashflow?days=30`
- [ ] Returns surplus after all obligations in time window
- [ ] Unit tests for obligation CRUD and cash flow calculation

## Subtasks

- [ ] Define Obligation model (Est: 30 min) - type enum (KCC, SCHOOL_FEE, LAND_RENT, OTHER), amount, due_date, reminder_flag
- [ ] Create ObligationRepository (Est: 1h) - CRUD + urgent filter + cash flow aggregation
- [ ] Implement cash flow assessment logic (Est: 1h) - sum obligations, compute surplus
- [ ] Wire into Kailash workflow (Est: 30 min)
- [ ] Write unit tests (Est: 1h) - cover normal, urgent, cash flow scenarios

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Rambhau's KCC EMI (3,200 rupees, 12 days) shows as urgent
- [ ] 30-day cash flow shows correct surplus calculation

## Dependencies

- TODO-100 (Farmer Profile CRUD)
