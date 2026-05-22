# TODO-301-Integrations-IMD-Weather

**GitHub Issue**: N/A
**Status**: ACTIVE

## Description

Integrate India Meteorological Department (IMD) API for weather forecasts and alerts in Nashik region.

## Context

Demo.html Screen 6 shows 7-day forecast (28°C clear, 24°C rain, 23°C thunderstorm), heavy rain warning for May 28. Need real weather data for irrigation advice and pesticide timing.

## Acceptance Criteria

- [ ] `GET /api/weather?location=nashik` returns current weather + 7-day forecast
- [ ] Data includes: temperature, condition (clear/rain/storm), humidity, wind
- [ ] Heavy rain / storm alerts returned as `alerts[]` array
- [ ] Pesticide spraying advice: block recommendations during heavy rain
- [ ] Irrigation advice: next irrigation date based on soil moisture + forecast
- [ ] Cache weather data for 1 hour

## Subtasks

- [ ] Study IMD API options (Est: 2h) - open APIs vs registered endpoints
- [ ] Create weather client with caching (Est: 1h)
- [ ] Implement 7-day forecast fetch (Est: 2h) - temperature, precipitation, wind
- [ ] Implement weather alert extraction (Est: 1h) - heavy rain, storm warnings
- [ ] Add irrigation timing logic (Est: 1h) - moisture + forecast combination
- [ ] Add pesticide timing logic (Est: 1h) - block during rain forecast
- [ ] Write integration tests with mocked IMD responses (Est: 1h)

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Weather data enables Gate 2 (weather fit) evaluation in CPE

## Dependencies

- TODO-000 (Project Scaffold)
- TODO-201 (CPE Engine)
