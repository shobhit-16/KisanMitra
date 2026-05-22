# TODO-102-Foundation-Income-Ledger

**GitHub Issue**: N/A
**Status**: ACTIVE

## Description

Build income ledger API for recording onion sales, computing baseline price, and flagging distress sales below MSP.

## Context

Demo.html Screen 9 shows income ledger with 4 sales (baseline 27/kg, one distress sale at 5/kg flagged). Need API to record sales and automatically flag distress.

## Acceptance Criteria

- [ ] `POST /api/farmers/{phone}/sales` records sale with date, quantity, price_per_quintal, mandi
- [ ] `GET /api/farmers/{phone}/sales` lists all sales for farmer
- [ ] `GET /api/farmers/{phone}/ledger` returns ledger with baseline price, all sales, distress flags
- [ ] Distress flag: sale price < MSP (750/quintal for onion) triggers `status: distress`
- [ ] Baseline price: weighted average of non-distress sales
- [ ] Each sale record includes calculated total and status (normal/distress)
- [ ] Unit tests for sale recording and distress detection

## Subtasks

- [ ] Define Sale model (Est: 30 min) - date, quantity_q, price_per_q, mandi, total, status, is_distress
- [ ] Create SaleRepository (Est: 1h) - CRUD + distress computation + baseline calculation
- [ ] Implement distress detection logic (Est: 30 min) - price < MSP threshold
- [ ] Implement baseline calculation (Est: 30 min) - average of non-distress sales
- [ ] Wire into Kailash workflow (Est: 30 min)
- [ ] Write unit tests (Est: 1h) - cover normal, distress, baseline scenarios

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Sale at 5/quintal correctly flagged as distress
- [ ] Baseline correctly computed as weighted average of normal sales

## Dependencies

- TODO-100 (Farmer Profile CRUD)
