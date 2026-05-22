---
name: 0014-DISCOVERY-geography-maharashtra-karnataka-onion-pilot
description: Maharashtra Karnataka onion pilot is the recommended Phase 1 geography; 2000 farmers 18 months
metadata:
  type: DISCOVERY
date: 2026-05-20
created_at: 2026-05-20T15:30:00+05:30
author: agent
session_id: 24b211f3-1394-4baa-8bbf-005fbaea9dae
project: indian-agri-digital-product
topic: geography pilot strategy — Maharashtra Karnataka two-state onion anchor
phase: analyze
tags: [geography, pilot, maharashtra, karnataka, onion, demographics, cpe-gates]
---

# DISCOVERY: Geography, Pilot, and Demography — Maharashtra + Karnataka Onion Anchor

## The Finding

**Geography:** Maharashtra (Nashik + Ahmednagar) and Karnataka (Dharwad + Belgaum) in parallel. Onion is the anchor crop — it has the most extreme documented price volatility of any widely-grown smallholder crop in India (farmgate Rs 3-80/kg range), which makes the Income Engine's selling decision module the clearest possible use case.

**Why not Bihar or UP:** These states fail the mandi infrastructure test. Bihar repealed its APMC Act in 2006 — farmers sell to informal traders at farmgate with no price discovery mechanism. The Income Engine's mandi price module has nothing to optimize against.

**Pilot Design:**
- 2,000 farmers enrolled (500/district × 2 states × 2 districts), 2,500 with buffer
- 3-5 villages per district, 6-criterion village filter
- 18 months minimum (covers two full crop cycles)
- June launch to capture kharif + rabi cycle

**Demographics at Start:**
- Farm size: 0.5-2.5 ha (marginal + small — enough surplus for selling decisions, enough smallholder economics for volatility)
- Tenure: 60% owner / 35% tenant — explicitly tests Gate 2 (Tenure) filtering
- Gender: >30% women via SHG partnerships (Maharashtra's DAY-NRLM network), IVR-primary delivery
- Languages: Marathi (Maharashtra), Kannada (Karnataka)

## The CPE Gate Validation Sequence

The pilot is not just a product test — it is a **CPE gate validation sequence**:

| Gate | Validation Event | When |
|---|---|---|
| Gate 4 (Selling Window) | Kharif harvest months 4-6 | First testable event |
| Gate 4 (Selling Window) | Rabi harvest months 16-18 | Second validation |
| Gate 2 (Tenure) | Ongoing | 35% tenant enrollment validates suppression |
| Gate 3 (Cash Flow) | Ongoing | Cash flow status distribution measured |
| Gate 1 (Health) | As triggered | Requires health event to test |

**Critical metric:** If >50% of farmers are in "deficit" or "emergency" cash flow status, most farmers receive only selling recommendations. The platform appears feature-poor not because the CPE is wrong but because the cash flow constraint is chronic.

## Women Farmers — The Design Constraint That Shapes Channel Choice

The brief includes women farmers. The ground reality: female farmers have 25-30% smartphone penetration and 10-15% smartphone operational capability. A "download the app" strategy excludes most women farmers by design.

**The SHG solution:** Maharashtra's DAY-NRLM network and Stree Shakti SHGs in Karnataka provide institutional infrastructure for women farmer enrollment without requiring individual smartphone access. IVR is the primary delivery channel — no smartphone required.

**This is not just an enrollment tactic:** The choice of IVR-first for women farmers implies the platform's **most trusted interface is voice**, which has implications for all farmer segments in Phase 1.

## Must-Clear Criteria for Phase 2 GO

1. Selling price improvement >10% in at least one district
2. MAU rate >55% for 3 months
3. Gate 2 (Tenure) accuracy >80%
4. Gate 3 (Cash Flow) accuracy >75%
5. At least one institutional partner LOI signed
6. Women farmer enrollment >25%

## For Discussion

1. **Counterfactual:** If the pilot starts in June but the institutional partnerships (FPO MoUs, KVK agreements) are not finalized, should the pilot proceed with only field agents as the channel? Or wait? (Likely: proceed with field agents only — institutional partnerships can be signed during the pilot if farmer enrollment is strong.)

2. **Implication for CPE:** The pilot's Gate 4 (Selling Window) validation at months 4-6 is the first evidence point for whether the CPE's constraint-priority architecture produces better farmer outcomes than unconstrained recommendation delivery. This data is critical for Phase 2 Soil Engine integration decisions.

3. **Open question:** The village selection criterion "no more than 80% owner-cultivators, tenant share >20% preferred" directly tests Gate 2. But informal tenant arrangements are common and self-reported tenure may not match ground truth. What's the threshold of Gate 2 accuracy error that would make the Phase 2 Soil Engine integration decision invalid?
