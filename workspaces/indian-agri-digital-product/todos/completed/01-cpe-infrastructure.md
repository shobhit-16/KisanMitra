# TODO-01-CPE-INFRASTRUCTURE

**Status**: COMPLETED

## Description

CPE (Constraint Priority Engine) infrastructure: ConstraintState entity with all 6 state fields, Recommendation Bus pub/sub layer, all 5 gates with suppression logic, one-recommendation output rule, suppression notification format.

**CPE is the highest-priority milestone.** All engines are suppressed until CPE gates are live. Per `specs/09-constraint-priority-engine.md §1.1`, CPE sits between engines and the single-recommendation output.

## Spec Reference

- `specs/09-constraint-priority-engine.md` — constraint state entity, five gates, recommendation bus, one-recommendation rule, suppression notification format
- `specs/09-constraint-priority-engine.md §5.1` — Phase 1: Income Engine only, active gates: 1, 3, 4, 5 (Gate 2 active but Soil not publishing)

## Acceptance Criteria

- [x] `ConstraintState` entity with all 6 fields: `health_status`, `tenure_type`, `cash_flow_status`, `selling_window`, `time_criticality`, `active_constraint`
- [x] `Recommendation` message format at `src/indian_agri/cpe/types.py` matching `specs/09-constraint-priority-engine.md §4.1`
- [x] `RecommendationBus` pub/sub at `src/indian_agri/cpe/bus.py` — engines publish; CPE subscribes; in-memory for Phase 1
- [x] Gate 1 (Health) with `health_gate(recommendation, constraint_state)` → PASS/SUPPRESS per `specs/09-constraint-priority-engine.md §3.1`
- [x] Gate 2 (Tenure) with `tenure_gate(recommendation, constraint_state)` → PASS/SUPPRESS per `specs/09-constraint-priority-engine.md §3.2`
- [x] Gate 3 (Cash Flow) with `cash_flow_gate(recommendation, constraint_state)` → PASS/SUPPRESS per `specs/09-constraint-priority-engine.md §3.3`
- [x] Gate 4 (Selling Window) with `selling_window_gate(recommendation, constraint_state)` → PASS/SUPPRESS per `specs/09-constraint-priority-engine.md §3.4`
- [x] Gate 5 (Time Criticality) with `time_criticality_gate(recommendation, constraint_state)` → PASS/SUPPRESS per `specs/09-constraint-priority-engine.md §3.5`
- [x] `CPE.evaluate(recommendations, constraint_state)` — evaluates gates in strict priority order (1→5); returns exactly one recommendation or suppression notification
- [x] One-recommendation output rule per `specs/09-constraint-priority-engine.md §6` — when multiple pass, issue in priority order (health > selling window > engine priority)
- [x] Suppression notification format per `specs/09-constraint-priority-engine.md §6.2` — "Right now, [active_constraint] is your main priority. We have [topic] advice ready — we'll share it once [constraint] resolves."
- [x] Gate 2 active in Phase 1 (even though Soil Engine not publishing yet) — tenant detection must work from farmer's `land_tenure` field
- [x] `CPEOutput` dataclass with `output_type: recommendation|suppression`, `recommendation`, `suppressed_reasons`, `active_constraint`, `confidence_note`

## Subtasks

- [x] BUILD-1 (Est: 2h) — ConstraintState entity at `src/indian_agri/models/constraint_state.py` — all gate fields with timestamps
- [x] BUILD-2 (Est: 2h) — Recommendation message type + RecommendationBus pub/sub at `src/indian_agri/cpe/bus.py` — engine publishes, CPE subscribes, in-memory event stream
- [x] BUILD-3 (Est: 3h) — Gate 1 (Health) + Gate 2 (Tenure) at `src/indian_agri/cpe/gates.py` — standalone gate functions with typed inputs/outputs, tested independently
- [x] BUILD-4 (Est: 3h) — Gate 3 (Cash Flow) + Gate 4 (Selling Window) + Gate 5 (Time Criticality) at `src/indian_agri/cpe/gates.py` — same pattern as BUILD-3
- [x] BUILD-5 (Est: 2h) — CPE orchestrator `CPE.evaluate()` at `src/indian_agri/cpe/engine.py` — gate priority evaluation loop, one-recommendation rule, suppression notification assembly
- [x] WIRE-1 (Est: 1h) — Wire ConstraintState to Farmer entity: add `constraint_state_id` FK + `update_constraint_state()` method on Farmer model
- [x] WIRE-2 (Est: 1h) — Wire RecommendationBus into Income Engine: Income Engine modules publish to bus via `publish_recommendation()`, `publish_selling_recommendation()`, `publish_emergency_credit()`

## Definition of Done

- [x] All 5 gates pass independent unit tests (each gate tested in isolation with PASS/SUPPRESS cases)
- [x] CPE.evaluate() returns exactly one item (recommendation or suppression) — never zero, never more than one
- [x] Gate priority order verified: Gate 1 always wins over Gate 4 (health crisis farmer in harvest window gets health resource, not selling recommendation)
- [x] Suppression notification matches format in `specs/09-constraint-priority-engine.md §6.2`
- [x] Phase 1 gate activation matches spec: Gate 1, 3, 4, 5 live; Gate 2 evaluates but no Soil recommendations exist yet
