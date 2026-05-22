# TODO-502-Pilot-Metrics-Baseline

**GitHub Issue**: N/A
**Status**: ACTIVE

## Description

Define and collect pilot metrics for measuring Kisanmitra impact on farmer outcomes.

## Context

Kisanmitra aims to be a calm trustworthy pocket companion. Need metrics to measure whether farmers are making better decisions: price alerts caught, obligations not missed, better selling timing.

## Acceptance Criteria

- [ ] Define pilot KPIs: obligation miss rate, avg sale price vs market baseline, recommendation acceptance rate, weekly active users
- [ ] Create metrics collection endpoints for backend
- [ ] Create metrics dashboard API for FPO partners
- [ ] Collect baseline measurements before Kisanmitra use (retrospective)
- [ ] Weekly metrics report generation
- [ ] Privacy: metrics aggregated, no individual farmer data shared without consent
- [ ] **Test coverage:** KPI calculation unit tests with ≥80% coverage
- [ ] **Test coverage:** Metrics aggregation tests: per-farmer, per-FPO, overall
- [ ] **Test coverage:** Privacy tests: no individual farmer records in aggregated output

## Subtasks

- [ ] Define pilot KPI list with definitions (Est: 2h) - consult with stakeholders
- [ ] Create metrics aggregation endpoints (Est: 2h) - per-farmer, per-FPO, overall
- [ ] Implement weekly report generation (Est: 2h) - automated email to pilot team
- [ ] Create FPO metrics dashboard API (Est: 2h) - simple JSON endpoint
- [ ] Document privacy policy for pilot data (Est: 1h)
- [ ] Baseline data collection from first 10 farmers (Est: 2h)

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Metrics dashboard shows first pilot week data
- [ ] Baseline vs Week 1 comparison available

## Dependencies

- TODO-500 (FPO Partnership)
- TODO-501 (Auth)
