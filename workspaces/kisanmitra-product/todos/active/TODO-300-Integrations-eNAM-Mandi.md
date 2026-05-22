# TODO-300-Integrations-eNAM-Mandi

**GitHub Issue**: N/A
**Status**: ACTIVE

## Description

Integrate e-NAM API for real-time mandi price data for onion prices across Nashik district mandis.

## Context

Demo.html Screen 3 shows Lasalgaon (28/q), Yeola (27.50/q), Niphad (28.30/q). Need to fetch actual prices from e-NAM API and cache them.

## Acceptance Criteria

- [ ] `GET /api/mandi/prices?commodity=onion&district=nashik` returns current prices from e-NAM
- [ ] Prices include: mandi_name, modal_price, min_price, max_price, arrival_date
- [ ] Response time < 2 seconds (cache prices for 15 minutes)
- [ ] Fallback to cached price if e-NAM API unavailable
- [ ] Alert threshold support: `GET /api/mandi/alerts?phone={phone}` returns farmer's configured price alerts
- [ ] Price trend calculation: 7-day trend (up/down percentage)
- [ ] **Test coverage:** Unit tests for price alert matching logic with ≥80% coverage
- [ ] **Test coverage:** Tier-2 integration tests with mocked e-NAM responses (fallback behavior, cache expiry)
- [ ] **Test coverage:** MSP comparison calculation tests — 100% coverage on MSP math

## Subtasks

- [ ] Study e-NAM API documentation (Est: 2h) - understand endpoint structure, authentication
- [ ] Create eNAM client with rate limiting (Est: 1h) - 15-min cache, retry logic
- [ ] Implement price fetch for onion in Nashik mandis (Est: 2h) - Lasalgaon, Yeola, Niphad
- [ ] Add price alert storage and matching (Est: 1h) - alert when price crosses threshold
- [ ] Implement fallback to demo.html mock data if API fails (Est: 30 min)
- [ ] Write integration tests with mocked e-NAM responses (Est: 1h)

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Returns actual Lasalgaon, Yeola, Niphad prices
- [ ] API doesn't break if e-NAM is down (graceful fallback)

## Dependencies

- TODO-000 (Project Scaffold)
