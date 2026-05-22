# TODO-000-Foundation-Project-Scaffold

**GitHub Issue**: N/A (new project)
**Status**: COMPLETED

## Verification

- [x] `src/kisanmitra/__init__.py` created with `__version__ = "0.1.0"`
- [x] `src/kisanmitra/models.py` created with FarmerCreate, Farmer models and all enums (LandTenure, CropType, Season, Language)
- [x] `src/kisanmitra/db/schema.sql` created with farmers, obligations, sales, price_alerts, scheme_eligibility tables
- [x] `tests/unit/test_schema.py` — 9 tests: schema existence, parse, table creation (farmers/obligations/sales), migration, phone constraint, land_size bounds, land_tenure enum — all PASSING
- [x] pytest result: `9 passed in 0.02s`
- [x] pyproject.toml, .env, .gitignore, README.md existed from COC template

## Description

Set up the Kisanmitra project structure with Python/Kailash SDK backend, PWA frontend scaffold, and development environment.

## Context

Demo.html exists at repo root (4,805 lines) as mobile-first HTML prototype with 17 screens, multi-language support (EN/HI/MR), and mock state machine. This todo converts the prototype into a production-grade application.

## Acceptance Criteria

- [ ] Project directory structure created: `backend/`, `frontend/`, `integrations/`, `tests/`
- [ ] Python virtual environment with Kailash SDK installed
- [ ] SQLite database initialized with schema for farmer profiles, obligations, sales records
- [ ] `.env` file created with placeholder API keys
- [ ] Git repository initialized with `.gitignore`
- [ ] README.md with project overview and setup instructions
- [ ] `pyproject.toml` with project metadata and dependencies
- [ ] **Test coverage:** SQLite schema migrations have unit tests covering up/down migrations
- [ ] **Test coverage:** `pytest tests/unit/test_schema.py` passes with ≥80% coverage on migration logic

## Subtasks

- [ ] Create project directory structure (Est: 15 min) - directories for backend, frontend, tests, docs
- [ ] Initialize Python venv and install kailash SDK (Est: 10 min) - `pip install kailash` plus dependencies
- [ ] Design SQLite schema for pilot (Est: 1h) - farmers, obligations, sales, recommendations tables
- [ ] Create `.env` template with API key placeholders (Est: 10 min) - eNAM, IMD, PM-KISAN keys
- [ ] Write `README.md` with setup, GTM phases, farmer persona (Est: 30 min) - Rambhau Gite context

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Project runs locally with `python -m kisanmitra.api`
- [ ] Database migrations apply cleanly
- [ ] README explains Nashik-first GTM strategy
