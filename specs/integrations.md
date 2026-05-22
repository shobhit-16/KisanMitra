# Integrations — Domain Spec

**Spec File:** `integrations.md`
**Domain:** External APIs
**Phase:** 1 (e-NAM, IMD Weather, Govt Schemes), 2 (Soil Health), 3 (Climate)
**Last Updated:** 2026-05-22

---

## e-NAM Mandi Price Integration

### API Overview

**Source:** National Agriculture Market (e-NAM) — electronic trading platform for agricultural commodities
**API Base:** `https://api.enam.gov.in/publicapi/v1/` (verify actual endpoint before implementation)
**Purpose:** Real-time mandi prices for onion across Nashik district

### Mandi List (Nashik District)

| Mandi Code | Name | Block |
|---|---|---|
| NAM-MH-001 | Lasalgaon | Niphad |
| NAM-MH-002 | Yeola | Yeola |
| NAM-MH-003 | Niphad | Niphad |
| NAM-MH-004 | Satana | Satana |
| NAM-MH-005 | Malegaon | Malegaon |

### Price Fetch Contract

**Endpoint:** `GET /api/mandi/prices?commodity=onion&district=nashik`

**Cache strategy:**
- Cache prices in SQLite for 15 minutes
- On API failure: return cached price with `is_cached: true` and `cached_at` timestamp
- If no cache exists and API fails: return error (do not fall back silently)

**Rate limit:** Max 10 requests per minute per IP
**Retry strategy:** 3 retries with exponential backoff (1s, 2s, 4s)

### Price Alert Contract

**Farmer alert preferences:**
```json
{
  "phone": "9876543210",
  "enabled": true,
  "drop_threshold_rs": 2,
  "rise_threshold_percent": 8,
  "preferred_mandis": ["Lasalgaon", "Niphad"]
}
```

**Alert trigger:** When e-NAM price for any preferred mandi crosses threshold, send in-app notification.

---

## IMD Weather Integration

### API Overview

**Source:** India Meteorological Department (IMD) — `api.imd.gov.in`
**Purpose:** 7-day weather forecast for Nashik district

### Weather Data Contract

**Endpoint:** `GET /api/weather?district=NASHIK&lang=mr`

**Response:**
```json
{
  "district": "NASHIK",
  "forecast": [
    {
      "date": "2026-05-22",
      "max_temp_c": 34,
      "min_temp_c": 24,
      "condition": "CLEAR",
      "condition_display": "स्पष्ट (Clear)",
      "rainfall_mm": 0,
      "humidity_percent": 45,
      "wind_speed_kmh": 12
    },
    {
      "date": "2026-05-23",
      "max_temp_c": 33,
      "min_temp_c": 23,
      "condition": "CLOUDY",
      "condition_display": "मेघाळ (Cloudy)",
      "rainfall_mm": 2,
      "humidity_percent": 55,
      "wind_speed_kmh": 15
    }
  ],
  "alerts": [
    {
      "type": "HEAVY_RAIN",
      "display": "Heavy rain expected on 28th May",
      "display_hi": "28 मे रोजी जोरदार पाऊस अपेक्षित",
      "valid_from": "2026-05-28T00:00:00Z",
      "valid_until": "2026-05-28T23:59:59Z"
    }
  ],
  "fetched_at": "2026-05-22T06:00:00Z",
  "cache_expires_at": "2026-05-22T07:00:00Z"
}
```

### Weather Conditions (IMD Standard)

```python
class WeatherCondition(Enum):
    CLEAR = "Clear sky"
    PARTLY_CLOUDY = "Partly cloudy"
    CLOUDY = "Cloudy"
    RAIN = "Rain"
    HEAVY_RAIN = "Heavy rain"
    THUNDERSTORM = "Thunderstorm"
    FOG = "Fog"
    STORM = "Dust storm"
```

### CPE Gate 2 Integration

Weather data feeds Gate 2 of the CPE engine:
- `HEAVY_RAIN` or `THUNDERSTORM` → blocks pesticide/fertilizer recommendations
- `RAIN` → blocks pesticide recommendations
- Alert: "Heavy rain expected on [date] — delay pesticide spraying"

### Cache Strategy

- Forecast cached for 1 hour
- Alerts cached for 6 hours
- On API failure: use last cached forecast

---

## Government Scheme Integration

### PM-KISAN

**Scheme:** Pradhan Mantri Kisan Samman Nidhi
**Benefit:** ₹6,000/year in 3 installments of ₹2,000
**Eligibility:** All landholding farmer families
**Source:** PM-KISAN portal API or static data (verify before implementation)

**Farmer eligibility check:**
```python
def check_pm_kisan_eligibility(farmer):
    # All farmer families with land are eligible
    return farmer.land_size > 0 and farmer.land_tenure != "TENANT"
```

**Display:** "PM-KISAN: ₹6,000/year — 3 installments of ₹2,000"

### Ayushman Bharat PM-JAY

**Scheme:** Pradhan Mantri Jan Arogya Yojana
**Benefit:** ₹5 lakh coverage per family per year
**Eligibility:** Based on SECC 2011 deprivation criteria + RSBY beneficiaries
**Source:** Static data for Phase 1 (verify actual API availability)

**Display (CPE Gate 1 unlocked):**
- "Ayushman Bharat PM-JAY — ₹5 lakh coverage"
- "No premium required"
- "Apply at CSC: call 14555 or visit nearest CSC"

### Scheme Data Contract

```json
{
  "schemes": [
    {
      "id": "pm-kisan-001",
      "name": "PM-KISAN",
      "name_hi": "प्रधानमंत्री किसान सम्मान निधि",
      "name_mr": "प्रधानमंत्री शेतकरी सन्मान निधी",
      "benefit_amount": 6000,
      "benefit_frequency": "ANNUAL",
      "benefit_unit": "₹",
      "eligibility": "All landholding farmer families",
      "application_method": "CSC or online",
      "documents_required": ["Aadhaar", "Land records", "Bank account"],
      "phone": "155261",
      "url": "https://pmkisan.gov.in"
    },
    {
      "id": "ayushman-001",
      "name": "Ayushman Bharat PM-JAY",
      "name_hi": "आयुष्मान भारत पीएम-जय",
      "name_mr": "आयुष्मान भारत पीएम-जय",
      "benefit_amount": 500000,
      "benefit_frequency": "ONE_TIME_USE",
      "benefit_unit": "₹",
      "eligibility": "SECC 2011 deprivation criteria",
      "application_method": "CSC or hospital",
      "documents_required": ["Aadhaar", "SECC ration card"],
      "phone": "14555",
      "url": "https://pmjay.gov.in"
    }
  ]
}
```

---

## Soil Health (Phase 2 — Coming)

### Data Source

**Source:** Soil Health Card scheme — state agriculture department
**API:** Verify availability — may be static data for pilot district

### Soil Health Card Contract

```json
{
  "phone": "9876543210",
  "village": "ओजर",
  "block": "निफाड",
  "last_test_date": "2025-11-15",
  "soil_type": "BLACK",
  "ph": 7.2,
  "nitrogen_kg_ha": 180,
  "phosphorus_kg_ha": 22,
  "potassium_kg_ha": 340,
  "recommendations": [
    {
      "nutrient": "NITROGEN",
      "deficiency": "LOW",
      "recommended_dose_kg_acre": 20,
      "subsidized_product": "Urea",
      "subsidized_price": 270,
      "subsidized_price_unit": "₹/bag (45kg)",
      "available_at": "Nashik Fertilizer Society"
    }
  ]
}
```

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Mobile App (PWA)                        │
│                   Kisanmitra Frontend                        │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   Kailash Backend (Nexus)                   │
│                   /api/farmers/{phone}/*                   │
│                   /api/cpe/evaluate                         │
│                   /api/mandi/prices                        │
│                   /api/weather                             │
└──────────┬──────────────────────────────────┬───────────────┘
           │                                  │
           ▼                                  ▼
   ┌───────────────┐              ┌─────────────────────┐
   │   e-NAM API   │              │   IMD Weather API   │
   │ (mandi prices)│              │   (7-day forecast)  │
   └───────────────┘              └─────────────────────┘
           │                                  │
           ▼                                  ▼
   ┌───────────────┐              ┌─────────────────────┐
   │  Government   │              │   Soil Health Card  │
   │  Scheme APIs  │              │   (Phase 2)         │
   └───────────────┘              └─────────────────────┘
```

---

## Out of Scope

- e-NAM authentication (Phase 1 uses public data)
- IMD authentication (verify if API key required)
- Real-time crop disease detection (Phase 3 — requires image upload)
- cold chain / logistics integration (future)
