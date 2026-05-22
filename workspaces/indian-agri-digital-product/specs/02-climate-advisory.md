# Domain Spec: Climate Advisory Engine

## Overview

This spec defines the climate intelligence and advisory system. Climate is the #1 risk factor for rainfed farmers and increasingly important even for irrigated farmers as weather variability increases. The advisory engine must deliver **actionable, personalized** guidance — not just raw weather data.

---

## 1. Data Sources

### 1.1 Weather Data

| Source | Granularity | Lead Time | Accuracy |
|---|---|---|---|
| IMD (India Meteorological Department) | District | 5-day forecast | 60-70% for precipitation |
| AWS (Automatic Weather Stations) | Block-level | Real-time | Higher but sparse |
| Satellite (INSAT, GPM) | 5km grid | Nowcast + 3 days | Moderate |
| IBM Deep Thunder (if available) | 1km | 5-day | Higher |

### 1.2 Climate Forecasts

| Type | Lead Time | Use Case |
|---|---|---|
| Extended Range (14-28 days) | Monsoon onset, dry spells | Sowing decisions |
| Seasonal (Month +) | kharif/rabi planning | Crop selection |
| Climate Projections (Decades) | Long-term | Resilience planning |

### 1.3 Crop Phenology Data

| Source | Description |
|---|---|
| ICAR Crop Calendar | Normal sowing/harvest windows by region |
| State Agriculture Universities | Local variety calendars |
| Remote Sensing (Sentinel, Landsat) | Actual crop stage from vegetation indices |

---

## 2. Advisory Types

### 2.1 By Timing

| Advisory Type | Lead Time | Content |
|---|---|---|
| **Nowcast** | 0-6 hours | "It will rain in your area in 2 hours. Delay pesticide spray." |
| **Short-range** | 1-5 days | Daily/agendar for field operations |
| **Extended range** | 1-4 weeks | Rainfall patterns, dry spell warnings |
| **Seasonal** | Month + | "Monsoon expected normal. Suitable for kharif crops." |

### 2.2 By Content Type

| Advisory Type | Description | Example |
|---|---|---|
| **Sowing** | When and what to sow | "Delay rice sowing by 5 days; heavy rain expected on 15th" |
| **Irrigation** | When to irrigate | "No irrigation needed for next 10 days due to forecast rain" |
| **Nutrient** | Fertilizer application timing | "Apply top-dress N after rain event; dry spell for 2 weeks" |
| **Pest/Disease** | Disease outbreak risk | "High blast risk; conditions favorable in next 5 days" |
| **Harvest** | When to harvest | "Clear weather for next 5 days; optimal harvest window" |
| **Weather Alert** | Extreme event warning | "Heat wave warning for 3 days; avoid fieldwork 12-4pm" |

---

## 3. Advisory Engine

### 3.1 Personalization Layers

```
Raw Forecast (District/Block)
    ↓
Crop-Specific Adjustment (CropPhenology × Forecast)
    ↓
Farm-Level Refinement (GPS × Soil × Historical)
    ↓
Language/Format Adaptation (Hindi + local dialect)
    ↓
Channel Optimization (IVR script vs WhatsApp vs App card)
    ↓
Actionable Advisory (with specific recommended action)
```

### 3.2 Personalization Inputs

| Input | Source | Used For |
|---|---|---|
| Farmer location (GPS/village) | Farmer profile | Spatial interpolation |
| Crop(s) planted | Crop Cycle entity | Crop phenology stage |
| Soil type | SHC or Soil Type classification | Drainage, heat stress |
| Irrigation availability | Farmer profile | Drought tolerance |
| Literacy level | Farmer profile | Message format |
| Language | Farmer profile | Translation |

### 3.3 Advisory Generation Rules

```python
# Pseudologic for advisory generation
def generate_advisory(farmer_id, weather_data, crop_cycles):
    farmer = get_farmer(farmer_id)
    active_cycle = get_active_cycle(crop_cycles)  # One per season
    crop = get_crop(active_cycle)
    growth_stage = get_growth_stage(active_cycle, weather_data.date)

    # Check for adverse conditions
    if weather_data.rainfall_probability > 0.8 and rainfall_amount > 50mm:
        advisory = "HEAVY_RAIN_ALERT"
        if crop.type == "rice" and growth_stage == "transplanting":
            advisory.detail = "Delay transplanting; flash flood risk"
        elif crop.type == "wheat" and growth_stage == "grain_fill":
            advisory.detail = "Avoid irrigation; disease risk"

    elif weather_data.temperature_max > crop.heat_threshold:
        advisory = "HEAT_STRESS"
        advisory.detail = "Avoid fieldwork 12-4pm; increase irrigation at night"

    # ... additional conditions

    return format_advisory(advisory, farmer.language, farmer.literacy_level)
```

---

## 4. Weather Alert System

### 4.1 Alert Severity Levels

| Level | Trigger | Channel | Response |
|---|---|---|---|
| **Green** | Normal conditions | Daily bulletin only | None required |
| **Yellow** | Marginal adverse | WhatsApp/IVR advisory | Monitor; prepare |
| **Orange** | Significant threat | WhatsApp + IVR + push | Take protective action |
| **Red** | Dangerous/severe | All channels + callbacks | Immediate action required |

### 4.2 Alert Types

| Alert | Threshold Examples |
|---|---|
| Heavy Rain | >64mm in 24hrs |
| Long Dry Spell | <5mm rain for >14 consecutive days |
| Heat Wave | Max temp >40°C for 2+ days (varies by region) |
| Cold Wave | Min temp <5°C for 2+ days |
| Hailstorm | Any hail occurrence |
| Frost | Min temp <2°C with high humidity |
| Strong Wind | >45 kmph |

---

## 5. Climate Risk Assessment

### 5.1 Farmer-Level Risk Profile

Computed per farmer based on:

| Risk Factor | Data Source | Weight |
|---|---|---|
| **Rainfall variability** | Historical district rainfall CV | 25% |
| **Drought frequency** | District drought history | 20% |
| **Flood risk** | District flood history + terrain | 15% |
| **Heat stress exposure** | Crop calendar × temperature | 15% |
| **Crop sensitivity** | Crop-specific vulnerability | 15% |
| **Irrigation buffer** | Irrigation type vs rainfed | 10% |

### 5.2 Risk Scores

| Score Range | Risk Class | Description |
|---|---|---|
| 0-25 | Low | Well-irrigated, resilient crops |
| 26-50 | Moderate | Some vulnerability; advisory beneficial |
| 51-75 | High | Significant exposure; advisory critical |
| 76-100 | Very High | Rainfed, drought-prone, marginal land |

---

## 6. Delivery Channels

### 6.1 Channel Prioritization

| Farmer Profile | Primary Channel | Secondary |
|---|---|---|
| Marginal (<1ha), Low literacy | IVR call (incoming) | Village agent visit |
| Marginal (<1ha), Medium literacy | WhatsApp (text + audio) | IVR |
| Small (1-2ha), any literacy | WhatsApp + App | IVR |
| Semi-medium+ (2+ha), literate | App + WhatsApp | SMS |

### 6.2 Message Formats by Channel

**IVR Script Format**:
```
[ greeting ]
[ alert type + severity ]
[ what to do (concrete action) ]
[ when (specific time window) ]
[ why (brief justification) ]
[ confirmation prompt ]
```

**WhatsApp Format**:
```
🌧️ *WEATHER ALERT — YOUR AREA*
Heavy rain expected tomorrow (15th June)
⏰ 8:00 AM - 6:00 PM

✅ *DO:* Delay pesticide spray
✅ *DO:* Check drainage in low-lying plots
❌ *DON'T:* Start sowing operations

📞 Need help? Call 1800-XXX-XXXX
```

**App Card Format**:
```
┌────────────────────────────┐
│ 🌧️ Heavy Rain Alert        │
│ June 15, 2024              │
├────────────────────────────┤
│ Your crops: Cotton ( squaring)│
│                           │
│ Action needed:            │
│ ✓ Delay pesticide spray   │
│ ✓ Check drainage          │
│                           │
│ Tap for details →         │
└────────────────────────────┘
```

---

## 7. Content Quality

### 7.1 Advisory Quality Checklist

- [ ] Specific location (not just district)
- [ ] Specific time window (not just "next few days")
- [ ] Specific action (not just "be careful")
- [ ] Translated to farmer's language
- [ ] Appropriate literacy level
- [ ] No technical jargon
- [ ] Actionable without external information

### 7.2 What NOT to Send

- ❌ "Monsoon expected to be normal" (too vague)
- ❌ "Take protective measures" (not actionable)
- ❌ Raw forecast data without interpretation
- ❌ "Contact KVK for more information" (passes the buck)
- ❌ Generic pest alerts without crop-stage context

---

## 8. Farmer Feedback Loop

### 8.1 Feedback Collection

After each advisory:
- **IVR**: "Was this information helpful? Press 1 for yes, 2 for no"
- **WhatsApp**: Quick reaction (👍/👎) or "More" for details
- **App**: "Was this helpful?" + optional text

### 8.2 Feedback Use

| Feedback | Action |
|---|---|
| "Not accurate" | Flag forecast source for review |
| "Not actionable" | Improve action specificity |
| "Too late" | Improve lead time |
| "Wrong language" | Fix translation |
| "Wrong crop" | Improve crop matching |

### 8.3 Ground Truth Collection

- **Rainfall**: Crowd-source via farmer-reported precipitation
- **Temperature**: If farmer has thermometer, periodic SMS check-in
- **Crop stage**: Photo-based verification (for advanced users)
- **Actual events**: Flood, hail, frost — farmer reports validated

---

## 9. Edge Cases

### 9.1 No Forecast Coverage
- If IMD has no block-level forecast for farmer's area:
  - Fall back to district-level
  - Explicitly state "forecast less certain for your specific area"
  - Increase confidence threshold before issuing alerts

### 9.2 Contradictory Forecasts
- If two sources disagree significantly:
  - Issue the more conservative (safer) advisory
  - Note the uncertainty: "Two forecasts disagree; we recommend preparing for..."

### 9.3 Farmer With No Crop
- Off-season advisories: land preparation, irrigation scheduling, weather for storage
- Crop planning advisories: which crops to consider for next season

### 9.4 Multiple Crops
- Generate separate advisories per crop
- If conflicting (one crop needs rain, another needs dry): prioritize economic value

---

## 10. Metrics

### 10.1 Advisory Quality Metrics

| Metric | Target |
|---|---|
| Forecast accuracy (precipitation) | >65% at district level |
| Advisory accuracy (did event occur?) | >70% |
| Actionable rate (% with specific action) | >90% |
| Farmer satisfaction (1-5) | >3.5 |

### 10.2 Engagement Metrics

| Metric | Target |
|---|---|
| Advisory open/receive rate | >60% |
| Action taken rate (when actionable) | >40% |
| Feedback response rate | >10% |
| Repeat consultation | >3/month |

---

## 11. Integration with Other Specs

### 11.1 With Soil & Inputs (04-soil-inputs.md)
- Irrigation advisory integrates soil moisture retention
- Fertilizer timing integrates rainfall forecast

### 11.2 With Market Intelligence (03-market-intelligence.md)
- Harvest timing integrates weather forecast
- Storage decision integrates weather outlook

### 11.3 With Scheme Access (05-scheme-access.md)
- PMFBY enrollment deadline integrates seasonal forecast
- Crop loss assessment integrates weather event data

---

*Spec authority: Climate Advisory Engine*
*Version: 1.0*
