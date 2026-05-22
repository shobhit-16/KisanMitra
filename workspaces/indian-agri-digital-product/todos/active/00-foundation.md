# TODO-00-FOUNDATION

**Status**: COMPLETED

## Description

Project foundation for Indian Agri Digital Product — Python package setup, FastAPI skeleton, PostgreSQL + Redis infrastructure, and domain model: Farmer entity, Land Holding entity, Crop Cycle entity, Harvest Record, Scheme Enrollment Status.

## Spec Reference

- `specs/01-domain-model.md` — farmer entity, land holdings, crop cycle, income & market entities, scheme eligibility
- `specs/01-domain-model.md §9.3` — offline capability requirement (all entities cacheable locally)

## Acceptance Criteria

- [ ] Python package at `src/indian_agri/` with `pyproject.toml` using kailash core + dataflow + nexus
- [ ] FastAPI application at `src/indian_agri/api/` with app skeleton, CORS, health endpoint
- [ ] PostgreSQL models via DataFlow: `Farmer`, `LandHolding`, `CropCycle`, `HarvestRecord`, `SalesRecord`, `SchemeEnrollment`
- [ ] Redis session store at `src/indian_agri/cache/` using kailash-dataflow pool
- [ ] Farmer entity with full field set from `specs/01-domain-model.md §1` including Agristack ID linkage, language, literacy_level, consent_status
- [ ] LandHolding entity with irrigation details, soil data reference, tenure_type enum
- [ ] CropCycle entity with season/year/crop_code/status + operations log
- [ ] HarvestRecord + SalesRecord with distress_sale_flag computation
- [ ] SchemeEnrollment entity per `specs/01-domain-model.md §5`
- [ ] Offline-first: all entities implement `to_dict()` and `from_dict()` for local SQLite cache
- [ ] Farmer ID → phone lookup table for IVR authentication

## Subtasks

- [ ] BUILD-1 (Est: 2h) — Python project setup: `pyproject.toml`, directory structure, `__init__.py` files, .env.example with `DATABASE_URL`, `REDIS_URL`, `AGRISACK_API_KEY`, `ENAM_API_KEY`
- [ ] BUILD-2 (Est: 2h) — FastAPI app skeleton: `src/indian_agri/api/main.py`, router structure, `src/indian_agri/api/deps.py` with DataFlow session + Redis session per request
- [ ] BUILD-3 (Est: 3h) — DataFlow models: Farmer, LandHolding, CropCycle, HarvestRecord, SalesRecord, SchemeEnrollment — DataFlow entities with proper field types, enums, and JSON fields
- [ ] BUILD-4 (Est: 2h) — Offline cache layer: base mixin with `to_dict()`/`from_dict()`, local SQLite setup for offline-first per `specs/01-domain-model.md §9.3`
- [ ] BUILD-5 (Est: 1h) — Farmer ID → phone lookup + basic Agristack identity verification stub at `src/indian_agri/auth/`

## Definition of Done

- [ ] All DataFlow models migrate cleanly (`dataflow migrate`)
- [ ] FastAPI app starts without errors (`python -m uvicorn`)
- [ ] All entity `to_dict()`/`from_dict()` round-trip correctly
- [ ] Farmer entity covers every field in `specs/01-domain-model.md §1–5`
