# Specs Index — Kisanmitra

**Project:** Kisanmitra Farmer Companion
**Version:** 1.0 (Phase 1)
**Last Updated:** 2026-05-22

## Domain Specs

| File | Domain | Description |
|---|---|---|
| `farmer-profile.md` | Farmer Identity | Phone-based farmer entity, CRUD contracts, authentication |
| `obligation-calendar.md` | Obligations | KCC EMI, school fee, land rent tracking; cash flow math |
| `income-ledger.md` | Income | Sale recording, MSP distress threshold, baseline price calculation |
| `income-engine.md` | Income Decision | Mandi price, storage cost, sell/store/hold recommendation |
| `cpe-engine.md` | Recommendations | 5-gate rule engine, recommendation bus, suppression logic |
| `integrations.md` | External APIs | e-NAM mandi prices, IMD weather, government schemes |
| `pwa-architecture.md` | Mobile App | PWA structure, offline strategy, screen routing, state management |

## Design Standards

| Concern | Spec File |
|---|---|
| Color palette | `pwa-architecture.md` § Design Language |
| Typography | `pwa-architecture.md` § Design Language |
| Voice interaction | `pwa-architecture.md` § Voice |
| Multi-language (EN/HI/MR) | `pwa-architecture.md` § i18n |

## Phase Coverage

| Phase | Specs Covered |
|---|---|
| Phase 1 | All specs below — Income Engine + CPE |
| Phase 2 | Soil Health Card — `integrations.md` § Soil Health |
| Phase 3 | Climate/Weather — `integrations.md` § IMD Weather |
