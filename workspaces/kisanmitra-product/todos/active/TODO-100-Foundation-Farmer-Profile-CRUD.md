# TODO-100-Foundation-Farmer-Profile-CRUD

**GitHub Issue**: N/A
**Status**: COMPLETED

## Verification

- [x] `src/kisanmitra/repository.py` — FarmerRepository with async CRUD using aiosqlite (WAL mode, busy_timeout, foreign_keys PRAGMAs)
- [x] `src/kisanmitra/api.py` — Nexus app with 4 endpoints: POST/GET/PUT/DELETE /api/farmers/{phone}
- [x] `tests/unit/test_farmer_repository.py` — 25 tests: create (success, duplicate 409, Pydantic validation 400), get (success, not found), update (6 fields, multiple, non-updatable ignored), delete (success, not found), full flow
- [x] pytest result: `25 passed in 0.31s`
- [x] All acceptance criteria met per spec/farmer-profile.md § CRUD Operations

## Description

Implement farmer profile management API (Create, Read, Update, Delete) with CRUD operations and phone-based identification.

## Context

Demo.html defines farmer Rambhau Gite (Ozar Niphad Nashik, 2ha, Rabi Onion). Backend needs to store and retrieve farmer profiles. Phone number is the primary identifier for pilot (no OTP implementation yet).

## Acceptance Criteria

- [ ] `POST /api/farmers` creates new farmer profile with phone, name, location, land_size, crop_type
- [ ] `GET /api/farmers/{phone}` returns farmer profile by phone number
- [ ] `PUT /api/farmers/{phone}` updates farmer profile fields
- [ ] `DELETE /api/farmers/{phone}` soft-deletes farmer profile
- [ ] All endpoints return JSON with appropriate HTTP status codes
- [ ] Input validation: phone format (10 digits), land_size (positive number), valid crop_type enum
- [ ] Unit tests covering CRUD operations

## Subtasks

- [ ] Define Farmer Pydantic model (Est: 30 min) - phone, name, location, land_size, crop_type, season, created_at
- [ ] Create FarmerRepository with SQLite CRUD (Est: 1h) - async SQLite operations
- [ ] Wire FarmerRepository into Kailash workflow (Est: 30 min) - runtime.execute pattern
- [ ] Add input validation with error responses (Est: 30 min) - 422 for validation errors
- [ ] Write unit tests for FarmerRepository (Est: 1h) - pytest with in-memory SQLite

## Definition of Done

- [ ] All acceptance criteria met
- [ ] `pytest tests/test_farmer.py` passes
- [ ] API responds correctly to all CRUD operations
- [ ] Farmer Rambhau Gite profile can be created and retrieved

## Dependencies

- TODO-000 (Foundation Project Scaffold)
