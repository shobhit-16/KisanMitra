# TODO-05-INSTITUTIONAL-INTEGRATION

**Status**: ACTIVE

## Description

Institutional integration for GTM partnerships: FPO dashboard (member constraint states, aggregate analytics), RRB/NABARD portfolio risk API (anonymized constraint-state distributions), KVK data exchange (FLD/OFT results), State Agriculture Department integration (Krishi Mitra tool).

Per pilot design in `specs/17-geography-pilot-demography.md`, institutional partnerships (FPO, KVK, RRB) are the B2B2F anchor for Phase 1.

## Spec Reference

- `specs/17-geography-pilot-demography.md §4.1` — FPO ecosystem as institutional anchor; FPO dashboard requirements
- `specs/17-geography-pilot-demography.md §4.2` — channel investment: FPO staff as channel intermediary
- `specs/06-delivery-channels.md §6` — agent types: FPO Staff, KVK Scientist, input dealer, SHG leader
- `specs/05-scheme-access.md §9` — FPO-specific scheme benefits, FPO member scheme benefits

## Acceptance Criteria

- [ ] FPO dashboard API at `src/indian_agri/institutions/fpo/dashboard.py` — member constraint state overview (how many members in health crisis, cash deficit, selling window), aggregate analytics per FPO
- [ ] FPO member management at `src/indian_agri/institutions/fpo/members.py` — link farmers to FPO membership, bulk constraint state query per FPO, FPO-level selling window tracking
- [ ] FPO suppression notification delivery — when CPE suppresses a recommendation for an FPO member, structured notification sent to FPO staff per `specs/15-ground-challenges-practical-feasibility.md §7a`
- [ ] RRB/NABARD portfolio risk API at `src/indian_agri/institutions/rrb/risk_api.py` — anonymized constraint-state distribution (count of farmers per constraint state bucket); no individual farmer data exposed; portfolio-level analytics
- [ ] KVK data exchange at `src/indian_agri/institutions/kvk/dataExchange.py` — FLD/OFT result ingestion (field demonstrations, on-farm trials); validation of platform recommendations against KVK results; KVK block-level recommendation validation per `specs/15-ground-challenges-practical-feasibility.md §6c`
- [ ] State Agriculture Department integration at `src/indian_agri/institutions/stateagri/integration.py` — Krishi Mitra tool compatibility; scheme enrollment data sync with state systems; district-level advisory co-delivery
- [ ] Institutional partner API authentication — FPO staff auth, KVK scientist auth, RRB API auth; per-partner data access controls
- [ ] Extension officer suppression briefing — structured notification per `specs/15-ground-challenges-practical-feasibility.md §7a`: "Your farmer [name] in [village] has [constraint] active. [Recommendation] is ready but suppressed. Suggested intervention: [short-term action]."

## Subtasks

- [ ] BUILD-1 (Est: 2h) — FPO dashboard API at `src/indian_agri/institutions/fpo/dashboard.py` — member overview, constraint state aggregate counts, selling window status per FPO
- [ ] BUILD-2 (Est: 2h) — FPO member management at `src/indian_agri/institutions/fpo/members.py` — farmer-FPO linkage, bulk queries, FPO staff auth
- [ ] BUILD-3 (Est: 2h) — FPO suppression notification generator at `src/indian_agri/institutions/fpo/suppression_notifications.py` — structured notifications for FPO staff when member farmer has active constraint
- [ ] BUILD-4 (Est: 2h) — RRB/NABARD risk API at `src/indian_agri/institutions/rrb/risk_api.py` — anonymized constraint-state distribution endpoint, portfolio-level analytics, API auth
- [ ] BUILD-5 (Est: 2h) — KVK data exchange at `src/indian_agri/institutions/kvk/dataExchange.py` — FLD/OFT result ingestion, recommendation validation against KVK results, block-level attribution
- [ ] BUILD-6 (Est: 2h) — State Agriculture Dept integration at `src/indian_agri/institutions/stateagri/integration.py` — Krishi Mitra API compatibility, scheme data sync, advisory co-delivery endpoint
- [ ] BUILD-7 (Est: 2h) — Institutional auth framework at `src/indian_agri/institutions/auth.py` — per-partner API keys, data access scopes, audit logging
- [ ] WIRE-1 (Est: 1h) — Wire FPO dashboard to CPE: aggregate constraint state counts computed from live CPE constraint states; real-time per FPO
- [ ] WIRE-2 (Est: 1h) — Wire KVK validation into recommendation bus: KVK FLD/OFT results tagged against Income Engine module recommendations; validate recommendation accuracy

## Definition of Done

- [ ] FPO dashboard shows real-time aggregate constraint state for all member farmers — no individual farmer data in aggregate view
- [ ] RRB risk API returns anonymized distribution — cannot reverse-engineer individual farmer constraint state
- [ ] KVK data exchange accepts FLD/OFT results in standard format; results linked to platform recommendations for accuracy tracking
- [ ] Extension officer suppression briefing format matches `specs/15-ground-challenges-practical-feasibility.md §7a` exactly
