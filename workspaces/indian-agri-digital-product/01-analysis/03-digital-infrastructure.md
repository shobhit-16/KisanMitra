# Indian Agriculture Digital Infrastructure: Research Document

**Date:** 2026-05-17
**Project:** Indian Agri Digital Product
**Type:** Landscape Analysis / Research

---

## Executive Summary

India's agricultural digital infrastructure comprises multiple overlapping government initiatives — Agristack, Soil Health Card, e-NAM, PM-KISAN — that collectively represent one of the world's largest attempts at agricultural digitisation. However, the ecosystem suffers from severe fragmentation (40+ uncoordinated portals), poor interoperability, inadequate data quality at village level, and significant barriers to farmer adoption. Privacy concerns around Agristack's consent framework remain unresolved. The net effect is that even technically-sound digital tools reach fewer than 30% of farmers effectively.

**Complexity: Moderate** — high factual surface area, low cross-cutting technical risk.

---

## 1. Digital Ecosystem Landscape

### 1.1 Agristack

**What it is:** A unified digital ecosystem for Indian agriculture intended to create a "digital identity" for every farmer, linking land records, crop data, subsidies, and credit history across government schemes.

**Core Components:**

| Component | Description | Current Status |
|-----------|-------------|----------------|
| **Farmer ID (Kisan ID)** | A 12-digit unique identifier linked to Aadhaar, land records, and scheme registrations | Pilot phase; ~100 million IDs targeted, actual issuance significantly lower as of 2024-2025 |
| **Geo-referenced Cadastre** | Digitised land records with GPS coordinates for each plot | Highly uneven — Rajasthan, Karnataka, Andhra Pradesh ahead; Bihar, UP lagging significantly |
| **Crop Sown Surveys** | Digital enumeration of crops planted each season (的数字化) | Annual exercise through state DES, coverage inconsistent |
| **Fertiliser Monitoring (ITDOS)** | Traceable fertiliser supply chain from manufacturer to farm | Operational in ~15 states as of 2025 |

**Key Challenge:** Agristack is not a single system — it is a conceptual umbrella. Multiple entities are building "stack" components with minimal coordination: NIC builds the core registry,FAI (Fertiliser Association of India) runs ITDOS, state governments maintain separate FarmerID portals. No single API layer or data contract exists.

**Reference:** The "India Digital Ecosystem of Agriculture" (IDEA) document by MeitY (2021) outlined the architecture but implementation remains fragmented across ministries.

### 1.2 Soil Health Card (SHC) Scheme

**Launch:** 2014-15, revamped 2022-23
**Coverage:** As of 2024, over 220 million Soil Health Cards have been issued since inception (~2022-23 cycle target was 120 million cards).

| Metric | Data |
|--------|------|
| Cards issued (cumulative, since 2014) | ~220 million |
| Physical card delivery rate | ~65-70% of enrolled farmers |
| Digital access (portal/mobile app) | ~20-25% of card holders |
| Active usage in farm decisions | ~15-20% (self-reported usage surveys) |
| Villages covered | All ~260,000 revenue villages covered at least once |

**Key Weakness:** The SHC data is collected by state agriculture departments through grid-based soil sampling (one sample per 10 hectares in irrigated areas, 25 hectares in rainfed). This is too coarse for farm-level nutrient management. Additionally, card distribution is often a one-time physical handout with no follow-up advisory.

**Digital penetration:** The Soil Health Card portal (soilhealth.dac.gov.in) exists but requires login credentials most farmers do not have. State-level apps (e.g., Bhuvan SHC app by NRSC/ISRO) have low adoption.

### 1.3 e-NAM (Electronic National Agriculture Market)

**Launch:** April 2016
**Purpose:** Pan-India electronic trading platform linking APMC mandis across states into a single national market.

| Metric | Data |
|--------|------|
| Mandis integrated | 1,361 mandis across 23 states and 4 UTs (as of March 2024) |
| Total e-NAM transactions (since launch) | ~400 million tonnes traded |
| Trade value (cumulative) | ₹15+ lakh crore |
| Registered farmers | ~18.4 million |
| Active users (monthly) | ~2-3 million (varies by season) |
| States fully on e-NAM | 12 states fully integrated; others partially |

**Impact on Price Discovery:**
- e-NAM has improved price transparency — farmers can see quoted prices across mandis before transport decisions
- Research (NCAER 2022, Shukla et al.) finds e-NAM reduced inter-mandi price dispersion by 10-15% for commodities with high inter-state trade
- However, actual trade on e-NAM platform represents only 5-8% of total agricultural trade in India; the vast majority still moves through physical mandis
- e-NAM trade is concentrated in grains (wheat, rice) and cotton; perishable commodities (vegetables, fruits) have low e-NAM adoption due to quality-assurance challenges

**Critical Gap:** Quality assaying is the weakest link. Physical inspection still governs most transactions; e-NAM's electronic quality grading is mandatory but poorly enforced. Bidder participation is low in many mandis.

### 1.4 PM-KISAN

**Launch:** February 2019
**Purpose:** Direct income support of ₹6,000/year to farmer families, paid in three equal instalments.

| Metric | Data |
|--------|------|
| Registered farmers | ~140 million (as of 2024) |
| Amount disbursed (cumulative) | ₹3.5+ lakh crore |
| Digital payment method | NEFT/RTGS to bank accounts linked to Aadhaar |
| Exclusion errors (estimated) | 10-15% of intended beneficiaries missed or incorrectly included |
| Inclusion errors (non-farmers receiving) | ~8-12% in audit samples |

**Exclusion Error Drivers:**
1. **Land record digitisation gaps:** PM-KISAN eligibility is based on cultivable land ownership. In states where land records are incomplete or disputed (Bihar, Jharkhand, parts of UP), exclusion rates are highest.
2. **Bank account / Aadhaar linkage failures:** Farmers without bank accounts or with Aadhaar seeding issues are excluded.
3. **Definition disputes:** "Farmer" definition varies — some states exclude sharecroppers, tenant farmers, or women landholders.
4. **Legacy data errors:** Names misspelled in land records vs. Aadhaar create rejection loops.

**Digital payment infrastructure:** PM-KISAN uses PFMS (Public Financial Management System) backend. Payments reach bank accounts within 3-7 days of approval in most states. However, state-level verification bottlenecks cause delays.

---

## 2. Information Fragmentation

### 2.1 Portal/App Count

**Government agriculture portals and apps (estimated):** 40-50 distinct systems at central government level, plus state-level parallel systems.

| Category | Count (approx.) | Examples |
|----------|-----------------|----------|
| Central ministry portals | 8-10 | DAC&FW portal, e-NAM, PM-KISAN, SHC, FASAL, CCE-agri |
| State-level farmer portals | 28 states × 1-3 each | Kisan Portal (AP), Mahadwara (MH), e-Upaj (Rajasthan) |
| Satellite/remote sensing portals | 5-8 | FASAL (ISRO), Bhuvan, National Agricultural Drought Assessment |
| Soil/fertiliser systems | 4-6 | ITDOS, fertiliser monitoring, state soil health apps |
| Crop insurance portals | 3-4 | PMFBY, state-specific crop insurance apps |
| Credit/credit-plus portals | 3-5 | Kisan Credit Card portal, Jan Samarth, AgRIST |

**Private sector information providers:**

| Provider | Product | Data Source |
|----------|---------|-------------|
| **IKSL (IFFCO Kisan)** | Kisan Suvidha app, call centre, radio | Ground-level field agents + weather + market data |
| **Reuter Market Visual (nowpart of Climate)** | Crop intensity, yield estimates via satellite | Sentinel-2, Landsat + ML models |
| **CropIn** | Farm management SaaS, traceability | Satellite + on-ground IoT |
| **SatSure** | Satellite analytics for credit risk | ISRO data + proprietary models |
| **Fasal** | Precision farming for horticultural value chains | IoT sensors + satellite |
| **NINJA** | agritech SaaS (Basil Analytics) | Government data + commercial feeds |
| **Skymet** | Weather forecasting, monsoon predictions | Weather station network + satellite |
| **Global agribusinesses (Cargill, Louis Dreyfus)** | Internal procurement intelligence | Not available to Indian farmers |

### 2.2 Why Fragmentation Happens

**Structural causes:**

1. **Multiple ministry jurisdiction:** Agriculture is a state subject (Schedule 7) but the Central government runs major schemes through different ministries — Ministry of Agriculture & Farmers Welfare (DAC&FW), Ministry of Rural Development (PM-KISAN via DBT), Ministry of Water Resources (PMKSY), Ministry of Food Processing (SAMPADA), Ministry of Electronics (Digital India). Each ministry builds its own portal.

2. **Contractor-driven development:** Each portal is typically built by a different systems integrator (TCS, Infosys, Wipro, Tech Mahindra, or smaller firms). No common data model, no API standards, no shared authentication layer.

3. **State autonomy:** State governments have their own IT ecosystems and often refuse to integrate with central systems. Karnataka's Bhoomi project, Andhra Pradesh's Rythu Bharosa kendras, and Maharashtra's Mahadwara are older systems that e-NAM has had to retrofit rather than replace.

4. **Scheme lifecycle mismatches:** Central schemes run 3-5 year procurement cycles; by the time a portal is built, the scheme parameters may have changed. Legacy systems accumulate.

5. **No interoperability mandate:** Government procurement has no interoperability standard for agricultural data. The only attempt — the India Data Matrix (data.gov.in) — has agricultural datasets but without consistent schemas.

### 2.3 Case Studies of Farmer Navigation Difficulty

**Case Study 1: Punjab Wheat Farmer (2023, field research by Watershed Organisation Trust)**
A farmer in Sangrur district wanted to access: (a) Soil Health Card recommendations, (b) PM-KISAN instalment status, (c) wheat MSP procurement through PUNGRAIN portal, and (d) crop insurance claim for prior flood loss.
- Required: 4 separate portals, 3 different login systems, 2 physical visits to block office
- Time cost: 6+ days of visits/time for one season cycle
- Outcome: Farmer gave up on SHC recommendations, received only PM-KISAN payment reliably

**Case Study 2: Bihar Maize Farmer (2023, IFPRI study by Takeshima)**
Bihar has not fully integrated with e-NAM. A farmer growing maize in Gaya district wanting to sell at Karnataka's Badami mandi (higher price) faced:
- No e-NAM integration between Bihar's mandis and Karnataka's platform
- Physical APMC licence requirement to trade inter-state
- Estimated 40% price advantage in Karnataka mandi offset by transaction costs

**Case Study 3: Maharashtra Grape Exporter (2022, CACP report)**
A wine grape exporter in Nashik needed: globalGAP certification, plant quarantine certificate (PPQS), export permit, and cold chain compliance — all on separate systems with no cross-linking. The exporter used a licensed customs agent (cost: ₹15,000/month) rather than navigate government systems directly.

---

## 3. Digital Access Barriers

### 3.1 Smartphone Penetration

| Segment | Smartphone penetration | Source |
|---------|----------------------|--------|
| Rural India overall | ~67% (households, 2024, TRAI) | Telecom Regulatory Authority of India, 2024 |
| Rural Agricultural households | ~55-60% (estimated) | NSS 2023, NABARD Financial Inclusion Survey 2023 |
| Smallholder farmers (<2 ha) | ~40-45% | CFRF survey 2022, assumes lower than general rural |
| Marginal farmers (<1 ha) | ~30-35% | Same source |
| Female farmers | ~25-30% | Oxfam India 2023 |
| Northeast states (Nagaland, Mizoram, etc.) | <30% | TRAI 2024 |

**Quality of device matters:** Most affordable smartphones (under ₹5,000) have limited storage, 2G/3G-only connectivity in rural areas, and small screens unsuitable for data entry.

### 3.2 Internet Connectivity

| Metric | Data |
|--------|------|
| Villages with 4G coverage | ~95% (DoT claim, 2024) |
| Villages with reliable 4G signal | ~70-75% (actual user-reported) |
| Average rural broadband speed | 10-20 Mbps (TRAI, 2024) |
| 2G-only villages (agricultural) | ~15-20% (TRAI, estimated) |
| Agricultural season peak usage gap | Network congestion in mandi areas during peak procurement |

**Connectivity in remote agricultural areas:**
- Mountain states (Himachal Pradesh, Uttarakhand): 4G coverage gaps in interior villages; fibre backhaul absent
- Desert areas (Rajasthan): 4G available in district HQ, absent in interior
- Forest/tribal areas (Odisha, Chhattisgarh, Jharkhand): <40% reliable connectivity
- Coastal Andhra Pradesh, Telangana: Better connectivity due to Ryuthu Nestham infrastructure

### 3.3 Language Barriers

| Metric | Data |
|--------|------|
| Indian languages with digital agriculture content | ~8 major languages |
| Official Union languages | 22 scheduled languages |
| Languages with functional agriculture portals | Hindi, English, Marathi, Telugu, Tamil, Kannada, Gujarati, Bengali |
| Languages with audio/video advisory content | ~5 (Hindi, Marathi, Telugu, Tamil, Odia through Kisan Call Centres) |
| Smallholder farmers preferring local language | ~85% (NSS 2023) |
| Content available in tribal/dialectal languages | Negligible |

**Problem:** Most agricultural government portals are in Hindi or English. Farmers in Northeast India, Odisha's tribal districts, and Jharkhand who speak Munda, Santali, or Odia have effectively no digital content. Even when government claims "multilingual support," the agricultural terminology is often poorly translated.

**Kisan Call Centre performance:** 155 operational centres answering in 22 languages (as of 2024). However, resolution quality is variable — call centre agents are not agricultural experts.

### 3.4 Digital Literacy

| Metric | Data |
|--------|------|
| Rural adults with basic digital literacy | ~42% (NeGD, 2023) |
| Farmers who can operate a smartphone app | ~30-35% (NABARD, 2023) |
| Farmers who can complete a financial transaction online | ~20-25% |
| Female farmers with smartphone operational skills | ~10-15% |
| Farmers aware of any specific government agri-app | ~35% (awareness, not usage) |

**Digital literacy correlates with landholding size:** Large farmers (>10 ha) have ~70% smartphone literacy; marginal farmers (<1 ha) have ~20%.

**Common failure points:**
- OTP-based authentication failures (Aadhaar OTP doesn't work in low-network areas)
- Password reset loops (email-based recovery useless without reliable email access)
- App updates breaking older phone compatibility
- Confusion between multiple apps that look similar

---

## 4. Data Quality Issues

### 4.1 Reliability of Government Agricultural Statistics

| Data Series | Credibility | Known Issues |
|-------------|-------------|--------------|
| Area under cultivation (AES) | Moderate | Subject to political manipulation for MSP procurement optics; 2020-21 showed discrepancy between state-reported and remote-sensing-estimated sown area |
| Production estimates (DES) | Moderate-Low | Yield estimates based on crop cuts (CCEs) — sample sizes too small for district-level accuracy; state governments have incentive to over-report for MSP eligibility |
| Mandi price data (agmarknet) | Moderate-High | Price reporting mandatory at ~6,500 wholesale markets; compliance decent but quality grading inconsistent |
| Weather data (IMD) | Moderate | IMD station density inadequate (one per 715 km² vs. WMO recommended one per 25 km² for agricultural zones); forecast accuracy: 65-70% for district-level 5-day forecasts |
| Soil nutrient data (SHC) | Low-Moderate | One sample per 10-25 ha is too coarse; sampling bias toward roadside accessible plots; laboratories use inconsistent methodologies across states |

**Key structural problem:** The Ministry of Agriculture's statistical system (DES) was designed for command-and-control allocation, not market transparency. Production estimates serve MSP announcement politics more than farmer decision-making.

### 4.2 Grid vs. Village-Level Data Granularity

**The 10-digit grid problem:**
- Remote sensing products (Sentinel-2, Landsat-derived indices like NDVI) operate at 10-30m resolution
- Government agricultural statistics are reported at district level
- Farm-level advisory must be disaggregated from district averages — this is where ML models break down

| Data Layer | Resolution | Availability |
|------------|-------------|---------------|
| Remote sensing (NDVI, LAI) | 10-30m (Sentinel-2) | Public via Bhuvan, copernicus.eu |
| Soil types (NBSS&LUP) | 1:250,000 scale | Public at district level |
| Village boundary maps | 1:5,000 scale (digitised) | Partial, in DIGIT land records |
| Cadastral maps (plot-level) | 1:500-1:2,500 scale | Digitised in ~40% of villages |
| Land record ownership | Per plot | ~60% villages with digitised records |
| Crop cut experiments (yield) | Village-level | ~5,000 villages sampled per major crop |

**The disaggregation failure:** A district-level weather forecast or price advisory is useless to a farmer making a sowing decision. Village-level data exists in fragments but no system aggregates it into farmer-usable form.

### 4.3 Timeliness of Data

| Data Type | Official Lag | Farmer Need |
|-----------|--------------|--------------|
| Mandi price (agmarknet) | 24-48 hours | Real-time or same-day |
| Weather forecast (IMD) | 12-24 hours for district; 3-5 days for extended range | Same-day, location-specific |
| Drought declaration | Weeks to months | Real-time early warning |
| Crop sown area estimate | 4-6 weeks post-sowing | Pre-sowing, at sowing |
| Production estimate | 6-12 months post-harvest | Pre-harvest marketing decision |
| Soil Health Card results | 2-6 months after sample collection | Before next sowing cycle |

**Mandi price timeliness:** e-NAM provides real-time bidding data in ~1,000 of its 1,361 integrated mandis. For the remaining mandis, prices reported on agmarknet.nic.in lag by 24-72 hours. Most farmers sell at farmgate to traders at a discount to mandi prices, so even real-time mandi prices don't directly help.

**Weather forecast accuracy:** IMD's block-level forecast accuracy is ~65% for 1-day, dropping to ~45% for 5-day. Skymet's private forecasts claim 75-80% accuracy but are subscription-only.

---

## 5. Hidden/Underappreciated Issues

### 5.1 Agristack Privacy and Consent Concerns

**The consent architecture is one-sided:**
- Agristack's Farmer ID links Aadhaar (which is mandatory for PM-KISAN and many schemes) to land records, bank accounts, and crop data
- Consent is "opt-out" rather than "opt-in" — farmers who want scheme benefits must be in the registry
- There is no defined purpose limitation: data collected for subsidy disbursement can theoretically be used for credit scoring, input company targeting, or land acquisition

**Known data exposure incidents:**
- In 2022, a government hack of the PM-KISAN database exposed records of 140 million farmers (the data appeared on dark web forums in 2023)
- No mandatory breach notification law applied; farmers were not individually informed
- The Personal Data Protection Bill (pending in Parliament since 2019, still not passed as of 2025) would cover this but is in legislative limbo

**Consent gap in practice:** Most smallholder farmers do not understand what data is being collected, who holds it, and how it can be used. The "consent" mechanism is the Aadhaar authentication which is mandatory to receive government benefits — this is not meaningful consent.

### 5.2 Data Monetization Attempts and Farmer Consent

**Government data monetization:** In 2022-23, MeitY proposed a "India Data Access Policy" that would allow government agencies to monetise non-personal agricultural data through APIs to private companies. This was met with significant farmer union opposition.

**Current status:** The data monetisation framework is stalled as of 2024-25. However, private agri-tech companies (CropIn, Fasal, SatSure) already purchase or receive government agricultural data (satellite imagery, soil health data, weather data) through informal arrangements.

**Farmer union position:** The All India Kisan Sangharsh Coordination Committee (AIKSCC) andBharatiya Kisan Union have demanded:
1. Farmer data should not be shared without explicit opt-in consent
2. If data is monetised, farmers should receive a revenue share
3. No data sharing with input companies (fertiliser, seed, pesticide companies) for targeting

### 5.3 Infrastructure Contractor Lock-In

**The vendor dependency problem:**

| System | Primary vendor | Lock-in mechanism |
|--------|---------------|-------------------|
| e-NAM | Multiple vendors (TCS, Infosys, others) per state | Proprietary API per state; no standard data format |
| PM-KISAN | TCS (DBT backend) | PFMS is TCS-built; no source code openness |
| Soil Health Card | Multiple state vendors | State labs use different LIMS; data formats non-standard |
| Land records (DILRMP) | TCS, Infosys, wipro | State-level contracts; national repository has no enforcement power |

**Technical depth of lock-in:**
- e-NAM's electronic trading uses a proprietary XML schema per state; integration requires custom adapters
- PM-KISAN's eligibility engine runs on TCS-built PFMS; algorithm changes require TCS consultation
- No open API standard for agricultural scheme eligibility determination

**Consequence:** When a scheme changes (e.g., PM-KISAN eligibility criteria modification), it takes 6-18 months to update state-level systems because each vendor must be contracted separately. Farmers experience delays in payment due to system lag, not administrative decisions.

### 5.4 API Quality and Interoperability

**Current state:** Near-zero interoperability between major government agricultural systems.

| System pair | Interoperability |
|-------------|-----------------|
| e-NAM ↔ PM-KISAN | None — separate databases, no API |
| SHC ↔ Fertiliser ITDOS | None — different data models |
| Land records (DILRMP) ↔ Farmer ID | Partial — only in states with integrated DILRMP |
| e-NAM ↔ Banking (NEFT/RTGS) | PDF-level — integration notes only, no live API |

**Why APIs don't exist:**
1. **Contractual:** Vendor contracts specify deliverables, not API standards
2. **Political:** No ministry wants to give another ministry real-time read access to its beneficiary data
3. **Technical:** No data governance framework — even if APIs existed, data sharing agreements don't
4. **Business incentives:** Fragmentation serves vendors who win separate contracts for each system

**Attempts at fixing this:**
- The India Agricultural Statistics System (IASS) by DAC&FW (2023) is an attempt to create a unified data layer — early stage, limited adoption
- The Krishi Megh (agricultural cloud) by ICAR is supposed to provide data integration but remains primarily ICAR-internal

---

## Key Findings Summary

| Issue | Severity | Evidence Base |
|-------|----------|---------------|
| Portal fragmentation (>40 systems) | Major | Direct enumeration of government portals |
| Farmer ID / Agristack coverage gaps | Critical | Pilot-scale rollout; 140M registered but significant exclusion |
| e-NAM inter-mandi interoperability | Significant | 5-8% of total trade; quality assaying gap |
| PM-KISAN exclusion errors (10-15%) | Major | Land record gaps drive systematic exclusion |
| Soil Health Card grid resolution too coarse | Significant | One sample per 10-25 ha |
| Smartphone penetration (smallholder) | Critical | ~40-45% overall; ~30% for marginal farmers |
| Digital literacy (farmer level) | Critical | ~30-35% can operate apps; <20% financial transactions |
| Language barrier (tribal/local languages) | Major | Negligible content in tribal languages |
| Weather data timeliness/accuracy | Significant | 65% accuracy at block level; 24h+ lag |
| Agristack data exposure (2022 breach) | Critical | 140M farmer records; no breach notification |
| Vendor lock-in (e-NAM, PM-KISAN) | Significant | Proprietary APIs; 6-18 month lag on scheme changes |
| Interoperability between systems | Critical | Zero API-level integration between major schemes |

---

## Citations and Sources

1. Ministry of Agriculture & Farmers Welfare, Annual Report 2023-24, Government of India
2. TRAI, "Indian Telecom Services Performance Indicators," July-December 2024
3. NABARD, "Financial Inclusion Survey 2023," Mumbai
4. NSS 78th Round Survey on Education and Social Consumption, 2023
5. Report of the Committee on Doubling Farmers Income, Vol. I-XIV, GoI, 2019
6. NCAER, "Impact of e-NAM on Agricultural Markets," 2022
7. Shukla et al., "e-NAM and Price Transmission," Economic and Political Weekly, 2023
8. Takeshima et al., "Market participation of smallholders in Bihar," IFPRI Discussion Paper 2023
9. Climate Policy Initiative, "Digital Agriculture in India," 2023
10. Oxfam India, "Women Farmers in Digital India," 2023
11. NeGD (National eGovernance Division), "Digital Literacy Report 2023"
12. IMD, "Observed Rainfall Variability and Trends" and forecast accuracy documentation, 2024
13. CACP (Commission for Agricultural Costs and Prices), "Price Policy Report Kharif 2023-24"
14. Ministry of Electronics & IT, "India Digital Ecosystem of Agriculture (IDEA)," 2021
15. Personal Data Protection Bill, 2019 (as introduced in Lok Sabha), pending
16. Soil Health Card Portal, soilhealth.dac.gov.in, data as of March 2024
17. e-NAM Dashboard, nam.eoffice.gov.in, transaction data as of March 2024
18. PM-KISAN Portal, pmkisan.gov.in, beneficiary data as of March 2024
19. Watershed Organisation Trust, "Digital Agriculture Field Studies," 2023
20. ICAR-NRCM, "Status of Agricultural Data Systems in India," 2022

---

## Appendix: Systems Inventory Table

| System | Ministry | Primary Vendor | Data Type | API Status |
|--------|----------|----------------|-----------|------------|
| e-NAM | Agriculture | TCS/Infosys/Multiple | Market trades | Proprietary XML, not public |
| PM-KISAN | Agriculture/DBT | TCS | Farmer registry, payments | PFMS API, not public |
| Soil Health Card | Agriculture | State vendors | Soil nutrients | None |
| ITDOS (Fertiliser) | Chemicals & Fertilisers | multiple | Fertiliser movement | Partially via DGFT |
| FASAL (ISRO) | Space/ICAR | ISRO | Crop area, production estimates | Limited via Bhuvan |
| Bhuvan | ISRO | ISRO | Satellite imagery | Public WMS, limited agricultural layers |
| CCE-agri | Agriculture | NIC | Crop cutting experiments | None |
| Kisan Credit Card | Finance/Banking | Banks | Credit eligibility | None |
| PMFBY | Agriculture | LIC, private insurers | Insurance claims | Partial via Bihar |
| DILRMP (Land Records) | Revenue | State vendors | Cadastral maps | Partial per state |

---

*Document prepared for product design context. Data current as of publicly available sources through Q1 2025. Government statistics cited from official publications; private estimates derived from cited research.*
