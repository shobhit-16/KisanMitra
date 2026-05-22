# Domain Spec: Soil & Input Optimization

## Overview

This spec addresses the soil health crisis and input optimization system. The goal is to move farmers from "blanket fertilizer application" to **precision input management** based on their specific soil conditions and crop needs.

---

## 1. Soil Health Data

### 1.1 Soil Health Card (SHC) Data Model

| Field | Type | Source | Quality |
|---|---|---|---|
| `shc_number` | String | Government SHC | Variable |
| `issue_date` | Date | Government | Often outdated |
| `n_level` | Enum | Lab analysis | Moderate |
| `p_level` | Enum | Lab analysis | Moderate |
| `k_level` | Enum | Lab analysis | Moderate |
| `ph` | Float | Lab analysis | Good |
| `oc_percent` | Float | Lab analysis | Good |
| `sampling_date` | Date | Field sample | Often missing |
| `sampling_location` | GPS | Field | Coarse (10-25 ha grid) |

### 1.2 NPK Classification

| Level | N | P | K |
|---|---|---|---|
| Very Low (VL) | <280 kg/ha | <23 kg/ha | <108 kg/ha |
| Low (L) | 280-560 | 23-45 | 108-280 |
| Medium (M) | 560-840 | 45-68 | 280-337 |
| High (H) | >840 | >68 | >337 |

### 1.3 Soil Type Classification

| Soil Type | Characteristics | Suitable Crops |
|---|---|---|
| Sandy | Low water retention, high drainage | Groundnut, watermelon, potato |
| Sandy Loam | Moderate drainage | Cotton, wheat, jowar |
| Loam | Balanced | Most crops |
| Clay Loam | High water retention | Rice, sugarcane |
| Black (Vertisol) | High swelling/clay | Cotton, soybean, sorghum |
| Red Loam | Low organic matter | Groundnut, ragi |
| Saline/Alkaline | High pH, salt | Barley, sugar beet, dhaincha |

---

## 2. Fertilizer Recommendations

### 2.1 Recommendation Engine Logic

```python
def generate_fertilizer_recommendation(
    soil_npk: dict,
    crop: Crop,
    yield_target: float,
    previous_crop: Crop = None,
    irrigation_type: str,
    organic_matter_available: float = 0  # kg
) -> dict:

    # Step 1: Calculate crop nutrient requirement
    crop_npk_req = get_crop_requirement(crop, yield_target)

    # Step 2: Adjust for soil supply
    available_n = soil_npk['n'] * soil_depth_factor * irrigation_factor
    available_p = soil_npk['p'] * fixation_factor
    available_k = soil_npk['k'] * leaching_factor

    # Step 3: Calculate deficiency
    deficit_n = max(0, crop_npk_req['n'] - available_n)
    deficit_p = max(0, crop_npk_req['p'] - available_p)
    deficit_k = max(0, crop_npk_req['k'] - available_k)

    # Step 4: Convert to fertilizer products
    urea_needed = deficit_n / 0.46  # Urea is 46% N
    dap_needed = deficit_p / 0.46   # DAP is 46% P2O5
    mop_needed = deficit_k / 0.60   # MOP is 60% K2O

    # Step 5: Apply organic matter correction
    if organic_matter_available > 0:
        reduced_urea = urea_needed * organic_correction_factor

    # Step 6: Check subsidy eligibility
    subsidy_products = get_subsidy_products()
    recommended_products = apply_subsidy_optimization(...)

    return {
        "primary_recommendation": {
            "urea_kg_per_ha": round(reduced_urea, 1),
            "dap_kg_per_ha": round(dap_needed, 1),
            "mop_kg_per_ha": round(mop_needed, 1)
        },
        "cost_estimate": compute_cost(...),
        "subsidy_savings": compute_subsidy(...),
        "application_timing": get_timing_recommendation(crop),
        "organic_supplement": if organic_matter_available < threshold
    }
```

### 2.2 NPK Imbalance Correction

**Current problem**: N:P:K ratio has skewed from 4:2:1 (optimal) to 19:5:1 (current)

**For farmers with excessive N:**
- Recommend N-inhibitor or slow-release N
- Increase K application to balance
- Shift to legume crops to fix atmospheric N
- Reduce urea application by 25-50% and monitor

**For farmers with excessive P:**
- P has low mobility; avoid further DAP application for 2 seasons
- Use phosphorus-solubilizing bacteria
- Focus on K correction

**For farmers with excessive K:**
- Less common but occurs in intensive horticulture
- Reduce MOP application
- Ensure N balance for crop uptake

### 2.3 Micronutrient Deficiency

| Deficiency | Symptoms | Correction |
|---|---|---|
| Zinc (Zn) | Stunted plants, pale leaves | ZnSO4 25-50 kg/ha |
| Iron (Fe) | Yellowing between veins | FeSO4 foliar spray |
| Boron (B) | Poor flowering/fruit set | Borax 10-20 kg/ha |
| Manganese (Mn) | Interveinal chlorosis | MnSO4 foliar spray |

---

## 3. Crop-Specific Recommendations

### 3.1 Crop Suitability Mapping

For each plot, recommend crops based on:

| Factor | Data Source |
|---|---|
| Soil type | SHC + soil survey |
| Soil pH | SHC |
| Irrigation availability | Farmer profile |
| Water table depth | Groundwater survey |
| Climate zone | IMD district data |
| Market demand | Price intelligence |
| MSP support | Government procurement |

### 3.2 Diversification Recommendations

**Why farmers don't diversify (despite being rational):**
- Risk of new crop failure (no experience)
- No guaranteed market for new crops
- Consumption preferences (wheat/rice are food security)
- Credit availability (moneylender won't finance new crop)

**How to make diversification viable:**
- Show historical yield stability of alternative vs current crop
- Connect to buyers before farmer commits
- Recommend incremental shift (25% area, not 100%)
- Factor in MSP-like support for traditional crops (millets)

### 3.3 Water-Intensive Crop Warnings

**For water-scarce regions (Punjab, Haryana, Western UP):**
- Warn when rice/wheat recommended for areas with declining aquifer
- Show groundwater depth trend (5-year)
- Recommend alternative: maize, soybean, pulses
- Calculate water footprint per crop

---

## 4. Input Quality

### 4.1 Fertilizer Quality

**Known problems**:
- 15-20% of fertilizer in India is counterfeit or substandard
- Urea is most commonly adulterated (added with sand, ash)
- DAP quality varies (low P2O5 content)

**How to address:**
- Link to quality-certified input dealers
- Show how to check for spurious fertilizers (label, color, smell)
- Provide field test kits where possible
- Don't recommend saving money by buying cheap/unbranded

### 4.2 Seed Quality

**Seed replacement rate targets**:
| Crop | Recommended SRR | Current SRR |
|---|---|---|
| Rice | 100% | 50-55% |
| Wheat | 100% | 60-65% |
| Cotton | 100% | 50-60% |
| Pulses | 100% | 30-35% |

**Quality indicators to check:**
- Certification label (Tag 1, Tag 2)
- Germination rate (should be >85%)
- Physical purity (>98%)
- Moisture content (<12%)

### 4.3 Pesticide Quality

**Counterfeit pesticide problem:**
- ~15-20% of pesticide market is counterfeit
- Most common: under-strength active ingredient
- Dangerous: wrong compound sold as another

**Platform role:**
- List registered pesticide products
- Show how to verify registration number
- Alert when new generic alternatives available
- Integrate with state agriculture department blacklists

---

## 5. Fertilizer Subsidy Integration

### 5.1 How Subsidy Works

- Farmers buy fertilizer at subsidized price (government pays difference to manufacturer)
- Urea subsidy: ~Rs 242/Q vs actual cost ~Rs 2,500/Q
- NBS (Nutrient-Based Subsidy) for P and K: fixed per kg of nutrient

### 5.2 Subsidy Calculator

```python
def calculate_subsidy_benefit(
    products: list,       # [{product: "Urea", qty_kg: 100}, ...]
    farmer_category: str  # General, SC, ST, small_marginal
) -> dict:

    subsidy_amount = 0
    for product in products:
        subsidy = get_product_subsidy(product.name)
        # NBS calculation for P and K
        if product.name in ["DAP", "MOP", "NPK"]:
            subsidy = product.qty_kg * product.nutrient_content * nbs_rate
        # Urea is fixed rate
        elif product.name == "Urea":
            subsidy = product.qty_kg * urea_subsidy_rate

        subsidy_amount += subsidy

    return {
        "subsidy_amount": subsidy_amount,
        "farmer_pays": total_cost - subsidy_amount,
        "effective_discount_pct": subsidy_amount / total_cost * 100
    }
```

### 5.3 Subsidy Smart Recommendations

**The problem**: Current subsidy structure incentivizes N over K (urea highly subsidized; K less so)

**Recommendations that work with the subsidy system:**
- Optimize N:P:K ratio within available subsidy products
- Suggest neem-coated urea (better efficiency, same subsidy)
- Recommend complex fertilizers (NPK) when multiple nutrients needed
- Flag when farmer is over-applying subsidized N

---

## 6. Integrated Nutrient Management (INM)

### 6.1 The 4R Principle

| Principle | Description |
|---|---|
| Right Source | Organic + inorganic combination |
| Right Rate | Based on soil test + crop need |
| Right Time | Split application, not one-shot |
| Right Place | Soil incorporation vs foliar |

### 6.2 Organic Supplement Recommendations

| Source | N content | When to Use |
|---|---|---|
| Farmyard Manure (FYM) | 0.5-1% N | Base application, all crops |
| Compost | 1-2% N | Pre-season, all crops |
| Green Manure (Sesbania) | Fixes 60-80 kg N/ha | Pre-rice, if land available |
| Vermicompost | 1.5-2% N | Vegetable crops, high value |
| Poultry Manure | 2-3% N | Strong, use carefully |
| Biofertilizers | N-fixation, P-solubilization | Supplement, not replace |

### 6.3 Recommended Approach by Farmer Segment

| Segment | Primary Recommendation |
|---|---|
| Marginal, low capital | FYM + reduced urea; focus on organic |
| Small, moderate capital | Balanced NPK + organic supplement |
| Commercial, high capital | Precision INM with soil sensor integration |
| Organic transition | Full organic with biofertilizer focus |

---

## 7. Edge Cases

### 7.1 No Soil Health Card Data
- Use district-level soil maps as proxy
- Recommend basic soil test (low cost, ~Rs 100-200)
- Provide visual soil health assessment guide
- Flag as "unverified soil data"

### 7.2 Soil Test Conflict with Farmer Practice
- Acknowledge farmer's current practice
- Don't recommend abrupt change
- Suggest small trial plot (100 sqm) with recommended practice
- Share results after one season

### 7.3 Input Dealer Conflicts
- Input dealer may recommend excessive fertilizer (commission)
- Platform must be trustworthy — not seen as dealer alternative
- Show economic analysis (cost vs benefit of extra application)
- Connect to dealer network that follows recommendations

### 7.4 Region-Specific Issues

**Punjab/Haryana**: High N, declining groundwater → Recommend rice diversification, reduce urea

**Maharashtra**: Variable soil, drought-prone → Rainfall-based fertilizer timing, drought-tolerant varieties

**Bihar**: Low organic carbon → Recommend organic integration

**Rajasthan**: Saline-alkaline soils → Specific reclamation crops

---

## 8. Metrics

### 8.1 Advisory Quality Metrics

| Metric | Target |
|---|---|
| % recommendations followed | >30% (baseline from SHC: 15-18%) |
| Yield improvement in followed cases | >10% vs baseline |
| Input cost reduction | >15% where over-applying |
| Soil health improvement (repeat SHC) | Measureable in 2-3 seasons |

### 8.2 Engagement Metrics

| Metric | Target |
|---|---|
| Soil test request generated | >20% of farmers |
| Fertilizer recommendation views | >40% of recommendations shown |
| Input quality complaint reports | Baseline + tracked |

---

*Spec authority: Soil & Input Optimization*
*Version: 1.0*
