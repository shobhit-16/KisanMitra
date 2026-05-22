# Specs Index — Indian Agri Digital Product

This document serves as the authority manifest for the project domain. Every spec file listed here represents a domain authority — flows, contracts, constraints, edge cases, and decisions documented within are binding unless explicitly superseded by a later spec revision.

---

## Spec Files

| Spec File | Domain | Description |
|---|---|---|
| `01-domain-model.md` | Farmer & Farm Entity | Core data model for farmer profiles, land holdings, crops, and farm attributes |
| `02-climate-advisory.md` | Climate Intelligence | Weather forecasting, climate advisories, and personalized crop guidance |
| `03-market-intelligence.md` | Market & Prices | mandi price data, price trends, selling decision support |
| `04-soil-inputs.md` | Soil & Input Optimization | Soil health data, fertilizer recommendations, input quality |
| `05-scheme-access.md` | Government Schemes | PM-KISAN, Soil Health Card, PMFBY enrollment and eligibility |
| `06-delivery-channels.md` | Multi-Channel Delivery | IVR, WhatsApp, USSD, app — voice-first, offline-capable architecture |
| `07-institution-integration.md` | B2B Platform | Institution APIs, SDK, partner onboarding |
| `08-farmer-identity.md` | Identity & Consent | Agristack integration, farmer ID, data consent management |
| `09-constraint-priority-engine.md` | Constraint Architecture | Platform-level gate system that makes Income/Climate/Soil engines complementary |

---

## Traceability Matrix

| Brief Requirement | Spec File | Section |
|---|---|---|
| Smallholder income volatility | `03-market-intelligence.md` | § selling-timing, § price-benchmarking |
| Soil degradation / NPK imbalance | `04-soil-inputs.md` | § fertilizer-recommendations, § npk-correction |
| Information fragmentation | `01-domain-model.md`, `07-institution-integration.md` | § data-silos, § api-aggregation |
| Climate risk personalization | `02-climate-advisory.md` | § hyperlocal-forecast, § advisory-engine |
| Government scheme access | `05-scheme-access.md` | § eligibility-engine, § enrollment-flow |
| Digital infrastructure gaps | `06-delivery-channels.md` | § offline-first, § voice-interface |
| Module complementarity / constraint conflicts | `09-constraint-priority-engine.md` | § five-gates, § one-recommendation-rule |

---

## Out of Scope (Explicitly Excluded)

- Direct MSP procurement or mandi transaction processing (e-NAM territory)
- Crop insurance claims processing (PMFBY territory)
- Input e-commerce / marketplace (Agrostar, DeHaat territory)
- Cold chain or logistics management
- Credit/lending decisions (bank domain)

---

## Assumptions

- Agristack farmer ID system will be available for integration
- Government scheme data (PM-KISAN, Soil Health Card) will be accessible via APIs
- IMD weather data will be available at block-level or better
- e-NAM mandi price data will be accessible

---

*Last updated: Phase 01 analysis complete*
