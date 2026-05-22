# Kisanmitra — Master Todo List

**Product**: Kisanmitra Farmer Companion App
**Target Users**: Onion farmers in Nashik, Maharashtra (pilot: Rambhau Gite, Ozar Niphad, 2ha Rabi Onion)
**GTM**: Nashik district first → Maharashtra → national
**Monetization**: None (public good)

## Project Overview

Demo.html exists (4,805 lines) as mobile-first HTML prototype with:
- 17 screens: lang, dashboard, obligations, mandi, sell, soil, climate, credit, cpe, ledger, timeline, soil-passport, fpo-advisor, summary, community, news, knowledge
- Multi-language: EN/HI/MR with 494 translatable keys
- Mock JS state machine, CPE simulator with 4 scenarios
- Web Audio API for alerts, voice keyword simulation

## Phase 1: Foundation

| TODO | Title | Status | LOC Est | Dependencies |
|------|-------|--------|---------|--------------|
| [TODO-000](TODO-000-Foundation-Project-Scaffold.md) | Project Scaffold | ACTIVE | 200 | — |
| [TODO-100](TODO-100-Foundation-Farmer-Profile-CRUD.md) | Farmer Profile CRUD | ACTIVE | 300 | 000 |
| [TODO-101](TODO-101-Foundation-Obligation-Calendar.md) | Obligation Calendar | ACTIVE | 350 | 100 |
| [TODO-102](TODO-102-Foundation-Income-Ledger.md) | Income Ledger | ACTIVE | 350 | 100 |

**Phase 1 Shard Budget**: ~1,200 LOC load-bearing, 15 invariants, 8 call-graph hops
**Phase 1 Exit Criteria**: Farmer Rambhau Gite can be created, obligations tracked, sales recorded

## Phase 2: Backend Engine

| TODO | Title | Status | LOC Est | Dependencies |
|------|-------|--------|---------|--------------|
| [TODO-200](TODO-200-Backend-Income-Engine-API.md) | Income Engine API | ACTIVE | 400 | 101, 102, 300 |
| [TODO-201](TODO-201-Backend-CPE-Engine.md) | CPE Engine (5-Gate) | ACTIVE | 500 | 101, 200, 302 |
| [TODO-202](TODO-202-Backend-Farmer-State-Machine.md) | Farmer State Machine | ACTIVE | 350 | 101, 102, 201 |

**Phase 2 Shard Budget**: ~1,250 LOC load-bearing, 25 invariants, 12 call-graph hops
**Phase 2 Exit Criteria**: Sell recommendation matches demo.html math (store vs sell decision)

## Phase 3: Integrations

| TODO | Title | Status | LOC Est | Dependencies |
|------|-------|--------|---------|--------------|
| [TODO-300](TODO-300-Integrations-eNAM-Mandi.md) | e-NAM Mandi Prices | ACTIVE | 300 | 000 |
| [TODO-301](TODO-301-Integrations-IMD-Weather.md) | IMD Weather API | ACTIVE | 350 | 000, 201 |
| [TODO-302](TODO-302-Integrations-Govt-Scheme-APIs.md) | Govt Scheme APIs | ACTIVE | 250 | 000, 201 |

**Phase 3 Shard Budget**: ~900 LOC load-bearing, 15 invariants, 6 call-graph hops
**Phase 3 Exit Criteria**: Real mandi prices and weather data flowing into backend

## Phase 4: Mobile PWA

| TODO | Title | Status | LOC Est | Dependencies |
|------|-------|--------|---------|--------------|
| [TODO-410](TODO-410-PWA-Manifest-And-Service-Worker.md) | PWA Manifest + Service Worker | ACTIVE | 200 | 000 |
| [TODO-411](TODO-411-PWA-App-Shell-And-Screen-Router.md) | App Shell + Screen Router | ACTIVE | 300 | 410 |
| [TODO-412](TODO-412-PWA-State-Store-And-Offline-Data.md) | State Store + Offline Data | ACTIVE | 350 | 410, 411 |
| [TODO-413](TODO-413-PWA-17-Screen-Migration.md) | 17-Screen Migration | ACTIVE | 500 | 411, 412 |
| [TODO-401](TODO-401-Mobile-PWA-API-Integration.md) | API Integration | ACTIVE | 450 | 410, 200, 201 |
| [TODO-402](TODO-402-Mobile-PWA-Voice-Input.md) | Voice Input | ACTIVE | 250 | 410 |
| [TODO-403](TODO-403-Mobile-PWA-Push-Notifications.md) | Push Notifications | ACTIVE | 300 | 410, 300, 301 |

**Note:** TODO-400 (PWA Architecture) is SUPERSEDED by TODO-410/411/412/413.

**Phase 4 Shard Budget**: ~2,100 LOC load-bearing, 25 invariants, 12 call-graph hops
**Phase 4 Exit Criteria**: PWA installable, works offline, 17 screens all functional

## Phase 5: Pilot

| TODO | Title | Status | LOC Est | Dependencies |
|------|-------|--------|---------|--------------|
| [TODO-500](TODO-500-Pilot-FPO-Partnership.md) | FPO Partnership | ACTIVE | 300 | 100 |
| [TODO-501](TODO-501-Pilot-Auth-Phone-OTP.md) | Phone OTP Auth | ACTIVE | 250 | 100 |
| [TODO-502](TODO-502-Pilot-Metrics-Baseline.md) | Metrics & Baseline | ACTIVE | 300 | 500, 501 |

**Phase 5 Shard Budget**: ~850 LOC load-bearing, 10 invariants, 5 call-graph hops
**Phase 5 Exit Criteria**: 10 farmers enrolled, baseline metrics collected, FPO dashboard live

## Total Project Summary

| Phase | Todos | Est. LOC | Invariants | Call Hops |
|-------|-------|----------|-----------|-----------|
| Foundation | 4 | 1,200 | 15 | 8 |
| Backend | 3 | 1,250 | 25 | 12 |
| Integrations | 3 | 900 | 15 | 6 |
| Mobile PWA | 7 | 2,100 | 25 | 12 |
| Pilot | 3 | 850 | 10 | 5 |
| **Total** | **20** | **6,300** | **90** | **43** |

## Invariant Count by Domain

- **Tenant isolation**: 1 (farmer data separated by phone)
- **Audit**: 1 (all API calls logged)
- **Redaction**: 1 (no PII in logs)
- **Cache key shape**: 2 (mandi prices, weather)
- **Error taxonomy**: 5 (validation, not_found, unauthorized, external_api, internal)
- **Gate state machine**: 5 (Gate 1-5 pass/block/partial)
- **Currency precision**: 1 (all money in paise internally)
- **Total**: 17 base + domain-specific

## Call-Graph Depth by Feature

- Farmer CRUD: 2 hops (API → Repository → SQLite)
- Income Engine: 3 hops (API → Engine → Mandi API + Ledger Repo)
- CPE: 4 hops (API → CPE → Gate Evaluators → Weather + CashFlow + Obligations)
- PWA API calls: 3 hops (UI → API Client → Backend → Repositories)

## Sharding Guidance

Per `rules/autonomous-execution.md`:
- Foundation (4 todos): Can run 2 in parallel (scaffold + farmer CRUD), then calendar + ledger
- Backend (3 todos): Sequential (200 before 201, 201 before 202)
- Integrations (3 todos): All independent, can run in parallel
- Mobile PWA (7 todos): 410 first, then 411, then 412 and 401 in parallel, then 413, then 402 and 403 last
- Pilot (3 todos): Sequential (500 before 501, 501 before 502)

## Pilot Success Metrics

1. Obligation miss rate < 10% (vs baseline)
2. Average sale price > Nashik district average
3. Recommendation acceptance rate > 40%
4. Weekly active users > 70% of enrolled
5. Zero data privacy incidents

---

*Generated for Kisanmitra project — Nashik onion farmer companion app*
*Persona: Rambhau Gite, Ozar Niphad Nashik, 2ha Rabi Onion*
