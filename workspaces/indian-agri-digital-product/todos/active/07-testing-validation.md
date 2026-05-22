# TODO-07-TESTING-VALIDATION

**Status**: ACTIVE

## Description

Testing and validation infrastructure: CPE gate unit tests (each gate independently), integration tests (Income Engine → Recommendation Bus → CPE → output), suppression notification delivery tests, offline sync tests, IVR/WhatsApp/USSD channel tests.

Per `specs/17-geography-pilot-demography.md §2.4`, platform performance metrics include Gate 2/3 accuracy cross-validation, false suppression rate <10%.

## Spec Reference

- `specs/09-constraint-priority-engine.md` — all 5 gates, suppression logic, one-recommendation rule
- `specs/17-geography-pilot-demography.md §2.4` — platform performance metrics: gate accuracy, false suppression rate, recommendation action rate
- Ground Challenges: `specs/15-ground-challenges-practical-feasibility.md §8` — honest accuracy standard, recommendation attribution chain

## Acceptance Criteria

- [ ] CPE Gate 1 unit tests — health_status=crisis suppresses all except health_crisis_resource; PASS when health_status=normal; test each category passes/suppresses correctly per `specs/09-constraint-priority-engine.md §3.1`
- [ ] CPE Gate 2 unit tests — tenant farmer: multi-year investments suppressed, season-level interventions pass; owner farmer: all pass; test `requires_tenure_security` metadata
- [ ] CPE Gate 3 unit tests — emergency: capital-intensive suppressed, selling recommendations pass; deficit: same; balanced/surplus: all pass; test `capital_intensity` metadata
- [ ] CPE Gate 4 unit tests — selling_window=open + harvest_within_7_days: soil/climate suppressed, selling/storage passes; closed: all pass
- [ ] CPE Gate 5 unit tests — sowing_window: multi-day actions suppressed, immediate actions pass; harvest_window: non-selling suppressed; growing_window: all pass
- [ ] CPE integration test: Income Engine Module 4 (SellingDecisionGuide) publishes → RecommendationBus → CPE.evaluate() → exactly one recommendation or suppression
- [ ] CPE integration test: Multiple engines publish simultaneously → CPE selects by gate priority → only highest-priority recommendation issued
- [ ] CPE integration test: Health crisis farmer in harvest window → Gate 1 fires → health crisis resource, not selling recommendation (edge case from `specs/09-constraint-priority-engine.md §8.3`)
- [ ] Suppression notification delivery tests: suppression rendered correctly in IVR TTS, WhatsApp template, USSD screen, SMS; plain language, no jargon
- [ ] Offline sync tests: queue operations offline, sync when online, conflict resolution (last-write-wins), retry with exponential backoff
- [ ] IVR channel tests: phone→farmer lookup, TTS rendering, recommendation playback, harvest status reporting
- [ ] WhatsApp channel tests: price query → price alert template; scheme query → scheme info; unknown query → unknown response
- [ ] USSD channel tests: sell now/wait binary choice rendering, session timeout handling
- [ ] Gate accuracy cross-validation: 90-day recall survey results compared against Income Engine Module 2 cash flow status; error rate computable
- [ ] False suppression rate test: farmer self-reports could-have-acted vs CPE suppression; track rate per `specs/17-geography-pilot-demography.md §2.4`

## Subtasks

- [ ] BUILD-1 (Est: 2h) — CPE gate unit tests at `tests/unit/cpe/test_gate1_health.py` through `tests/unit/cpe/test_gate5_time_criticality.py` — each gate in independent test file; all PASS/SUPPRESS cases per spec
- [ ] BUILD-2 (Est: 2h) — CPE integration tests at `tests/integration/cpe/test_evaluate_recommendation_bus.py` — full flow: engine publishes → bus → CPE → output; multiple engine scenario; gate priority ordering
- [ ] BUILD-3 (Est: 2h) — CPE edge case tests at `tests/integration/cpe/test_edge_cases.py` — health crisis + harvest window; tenant + cash deficit + sowing window; multiple gates fire simultaneously
- [ ] BUILD-4 (Est: 2h) — Suppression notification delivery tests at `tests/integration/channels/test_suppression_notifications.py` — IVR TTS format, WhatsApp template format, USSD screen format, plain language verification
- [ ] BUILD-5 (Est: 2h) — Offline sync tests at `tests/integration/sync/test_offline_manager.py` — queue, sync, conflict resolution, retry backoff
- [ ] BUILD-6 (Est: 2h) — Channel tests at `tests/integration/channels/test_ivr.py`, `tests/integration/channels/test_whatsapp.py`, `tests/integration/channels/test_ussd.py` — end-to-end recommendation rendering per channel
- [ ] BUILD-7 (Est: 2h) — Gate accuracy tests at `tests/integration/cpe/test_gate_accuracy.py` — cash flow status prediction vs 90-day recall; tenure type vs field agent attestation; false suppression rate tracking
- [ ] WIRE-1 (Est: 1h) — Wire full pipeline integration test: farmer enrolls → constraint state collected → Income Engine Module 4 fires → RecommendationBus → CPE.evaluate() → IVR plays recommendation → suppression logged

## Definition of Done

- [ ] All 5 CPE gates: 100% spec case coverage (PASS and SUPPRESS for every relevant recommendation category)
- [ ] CPE.evaluate() never returns more than 1 item — one-recommendation rule enforced
- [ ] Health crisis + harvest window edge case: health resource issued, not selling recommendation
- [ ] Suppression notification passes plain language check (no technical jargon per `rules/communication.md`)
- [ ] Offline sync: queued operations survive app restart; sync completes within 30s of connectivity restoration
- [ ] Gate 3 (Cash Flow) accuracy: Income Engine Module 2 assessment vs recall survey error rate computable and <20% target per `specs/17-geography-pilot-demography.md §2.4`
