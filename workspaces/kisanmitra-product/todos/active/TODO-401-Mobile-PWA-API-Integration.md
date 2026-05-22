# TODO-401-Mobile-PWA-API-Integration

**GitHub Issue**: N/A
**Status**: ACTIVE

## Description

Replace all mock JavaScript data in demo.html with real API calls to Kailash backend.

## Context

Demo.html has hardcoded mock data (Rambhau Gite profile, mandi prices, CPE scenarios). PWA needs to fetch all data from backend API.

## Acceptance Criteria

- [ ] Dashboard fetches farmer profile, obligations, cash flow from API
- [ ] Mandi screen fetches real prices from `/api/mandi/prices`
- [ ] Soil screen shows data from farmer's soil record (future: from soil test API)
- [ ] Climate screen fetches from `/api/weather`
- [ ] Credit screen fetches scheme eligibility from `/api/schemes/eligible`
- [ ] CPE screen fetches gate state from `/api/farmers/{phone}/state`
- [ ] Ledger screen fetches from `/api/farmers/{phone}/ledger`
- [ ] Sell screen uses `/api/farmers/{phone}/income-engine`
- [ ] Loading states, error states, empty states for all screens
- [ ] Demo mode: if backend unavailable, show friendly "setup required" message
- [ ] **Test coverage:** API client unit tests with mocked fetch responses (happy path + error + timeout)
- [ ] **Test coverage:** Playwright E2E tests for all 17 screen API integrations (each screen loads and displays data)
- [ ] **Test coverage:** Offline mode tests: app works with cached data when API unreachable

## Subtasks

- [ ] Create API client module (Est: 1h) - fetch wrapper with error handling
- [ ] Create mock data layer (Est: 2h) - for development without backend
- [ ] Wire dashboard API calls (Est: 2h) - profile, obligations, alerts
- [ ] Wire mandi API calls (Est: 1h) - prices, trends
- [ ] Wire climate API calls (Est: 1h) - weather, forecast
- [ ] Wire credit API calls (Est: 1h) - schemes
- [ ] Wire CPE API calls (Est: 1h) - state
- [ ] Wire ledger API calls (Est: 1h) - sales
- [ ] Wire sell API calls (Est: 1h) - income engine

## Definition of Done

- [ ] All acceptance criteria met
- [ ] All screens load with real API data
- [ ] Demo mode works when backend not available

## Dependencies

- TODO-400 (PWA Architecture)
- TODO-200 (Income Engine API)
- TODO-201 (CPE Engine)
- TODO-300 (eNAM Integration)
- TODO-301 (IMD Weather)
