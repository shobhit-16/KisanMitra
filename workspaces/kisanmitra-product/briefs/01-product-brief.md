# 01 — Product Brief: Kisanmitra Farmer Companion

**Date:** 2026-05-22
**Author:** User (from session brief + SPEC.md)
**Version:** 1.0

---

## Product Vision

Kisanmitra is a **public-good farmer companion** that sits in a farmer's pocket — not a sales channel, but a calm, trustworthy agronomist, risk coach, and climate ally. Its only job is to protect the farmer's future and the land they farm.

The product runs on a basic Jio smartphone, works offline, speaks Hindi and Marathi, and costs nothing to use.

---

## Problem Statement

Small farmers in Nashik (Maharashtra) face five compounding failures:

1. **Market failure**: Sell at harvest because they don't know tomorrow's price — even when storage would earn 25% more
2. **Cash flow surprise**: KCC EMI and school fee hit the same week — forced to sell at a loss
3. **Crisis with no backstop**: Hospital bill → sell standing crop at any price
4. **Distress selling**: Sell immediately after harvest because village trader offers cash now — even below MSP
5. **Digital illiteracy**: Existing apps have 47 screens and require reading; this farmer has a 2nd-grade literacy level

---

## Farmer Persona

**Rambhau Gite, 38**
- Village: Ozar, Block: Niphad, District: **Nashik**, Maharashtra
- Land: **2 hectares**, irrigated, owner-operated
- Crops: **Rabi Onion** (Nov sowing → Feb/Mar harvest), **Kharif Paddy** (Jun–Oct)
- Language: **Marathi primary**, Hindi understood, limited English
- Phone: Basic smartphone (Jio, 4G available)
- Literacy: Functional — reads Marathi, numbers, phone numbers

---

## Product Principles

| Principle | What It Means |
|---|---|
| **Voice-first** | Every action reachable by voice, not just taps |
| **One screen, one decision** | Never show more than the farmer needs right now |
| **Offline-capable** | Works without internet — data cached locally |
| **No monetization** | Not a sales channel. Government schemes, not commercial products |
| **No data extraction** | Privacy-first. Farmer owns their data. DPDP compliant |
| **Trusted source** | e-NAM prices, IMD weather, government scheme data — not ads |

---

## Core Features (Phase 1)

### 1. Obligation Calendar — "Aapka Niyam"
Track all upcoming obligations: KCC EMI, school fees, land rent. Color-coded urgency. Cash flow health bar.

### 2. Mandi Price Visibility — "Aajcha Market"
Real-time onion prices from e-NAM at Lasalgaon, Yeola, Niphad. MSP comparison chip. Price trend. Alert on threshold.

### 3. Selling Decision Guide — "Bechana Ka Sirf?"
Enter harvest quantity. See storage math (cost vs. expected gain). Get a clear SELL or STORE recommendation. CPE Gate 4 activates selling window.

### 4. Income Ledger — "Aapki Kitaab"
Record every sale. Automatic distress flagging below MSP. Seasonal baseline price. One-tap view of selling performance.

### 5. Emergency Credit Pathway — "Rashi Ki Seva"
One tap on hospital icon. Ayushman Bharat PM-JAY (₹5 lakh, no premium). CPE Gate 1 suppresses all other recommendations in crisis.

### 6. CPE Simulator — "Kya Hota Hai"
Animated pipeline showing how recommendations get filtered. Farmer can toggle gates to see what they would see under different conditions.

---

## GTM Strategy

### Phase 0 — Pilot (This Implementation)
- **Geography:** Nashik district, Maharashtra
- **Entry point:** 1-2 FPOs (Farmer Producer Organizations) in Niphad block
- **Target:** 10 farmers in pilot — all onion growers, Rabi season
- **Duration:** One Rabi cycle (Nov 2026 → Mar 2027)

### Phase 1 — Nashik Expansion (H2 2027)
- Expand to 5 FPOs across Nashik district
- 100 farmers
- Add Kharif Paddy support

### Phase 2 — Maharashtra (2028)
- Expand to 3 districts: Jalgaon, Solapur, Pune
- 1,000 farmers
- Soil Health Card integration

### Phase 3 — Karnataka + Gujarat (2029)
- Onion belts in Karnataka (Dharwad) and Gujarat (Bhavnagar)
- 10,000 farmers

### Non-Negotiables
- **No advertising** — never commercial
- **No data selling** — farmer data stays with farmer
- **No premium tier** — entirely free
- **Open source** — government can deploy independently

---

## Stakeholder Map

### Primary Users
| Stakeholder | Role | Interest |
|---|---|---|
| Small/marginal farmers (1-5 ha) | End users | Better prices, less distress, lower risk |
| FPO leaders | Adoption partners | Value to members, differentiation |

### Partnership Target (in priority order)

| Stakeholder | Type | Why Partner |
|---|---|---|
| **Maharashtra State Agriculture Dept** | Government | Scale (district extension network), legitimacy, scheme integration |
| **ICAR/SAUs (Niphad Krishi Vidyalaya)** | Research | Crop calendars, soil health data, agronomy expertise |
| **Nashik FPO Consortium** | FPO network | Farmer access, trust, aggregation pilot |
| **Nabard** | Funder/partner | FPO financing, project support |
| **Regional Rural Banks (Nashik)** | Credit partner | KCC data, credit history — NOT a sales channel |
| **CSC (Common Service Centre)** | Distribution | Physical touchpoints in every village for enrollment |
| **e-NAM** | Data provider | Real-time mandi prices |
| **IMD** | Data provider | Weather forecasts |

### Civil Society / NGO Partners
- **BAIF Development Research Foundation** — tribal and small farmer focus
- **IWMI** — water and agriculture research
- **CSE (Centre for Science and Environment)** — if policy-facing

### NOT Targets
- Private pesticide/fertilizer companies (conflicts with trust model)
- Commercial banks (we are not a distribution channel for credit products)
- Data brokers or agritech companies (data extraction conflicts with privacy principle)

---

## Pilot Design (Phase 0)

### Target Demographics
- 10 farmers in Ozar village, Niphad block, Nashik
- All Rabi onion growers
- Mix: 6 small (1-2 ha), 4 marginal (<1 ha)
- Mix: 7 owner-operators, 3 tenants
- Gender: 8 male, 2 female (FPO may have more women members)

### Success Metrics

| Metric | Baseline | 6-Month Target |
|---|---|---|
| Obligation miss rate | ~30% (assumed) | <10% |
| Average onion sale price | ₹22/kg (assumed) | ≥₹28/kg |
| Distress sale count | ~3 per season (assumed) | <1 |
| Recommendation acceptance rate | N/A | ≥50% |
| App retention (DAU/MAU) | N/A | ≥40% |

### What to Measure
- Obligation entries per farmer per week
- Price alert trigger rate
- Sell vs. store decision logging
- CPE recommendation pass/fail rates per gate
- FPO advisor notification (when farmer flagged as distress)

---

## Technical Constraints

| Constraint | Implication |
|---|---|
| Basic Jio phone (Android Go) | Must work on 1GB RAM, slow processor |
| Offline-first | All critical data cached locally |
| No app store install | PWA installable from browser |
| 2G/3G in rural areas | API responses must be <50KB |
| Noto Sans font | Only font that renders Devanagari + Latin cleanly |
| 48px minimum tap targets | Accessibility for older farmers |

---

## Revenue Model

**There is none.**

Kisanmitra is a public good. Operating costs are covered by:
- Government grants (state agriculture department partnerships)
- FPO membership fees (paid by FPO, not farmer)
- Research grants (ICAR, universities)
- Philanthropic funding (foundations supporting smallholder farmers)

---

## Competitive Positioning

We are not an "agri-tech startup." We do not:
- Sell inputs (fertilizers, seeds)
- Buy produce (mandi aggregation)
- Lend money (no credit product)
- Show advertisements

We are a **public agricultural extension service** in a farmer's pocket — the digital equivalent of a Krishi Vigyan Kendra (KVK) advisor who is available 24×7.

---

## What's Coming

| Phase | Features |
|---|---|
| Phase 1 (now) | Income Engine + CPE + Obligation tracking |
| Phase 2 (H2 2027) | Soil Health Card integration, fertilizer recommendations |
| Phase 3 (2028) | Weather/climate alerts, disease detection via photo |
| Phase 4 (2029) | FPO aggregation coordination, group selling |
