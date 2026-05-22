# Domain Spec: Market Intelligence & Selling Decision Support

## Overview

This spec defines the market intelligence layer — mandi prices, price trends, historical patterns, and selling decision support. The goal is NOT to replace mandis or create a new marketplace, but to **empower farmers with better selling decisions** through price intelligence.

---

## 1. Data Sources

### 1.1 Price Data

| Source | Coverage | Granularity | Latency |
|---|---|---|---|
| e-NAM | 1,361 mandis | Commodity × Variety × District | Daily (closing prices) |
| State APMC | Varies by state | Variable | Often weekly |
| Agmarknet | 1,000+ mandis | Modal price | 24-48 hour lag |
| Private (Reuters, Agrostar) | Selected commodities | Varies | Real-time for subscribers |

### 1.2 Data Quality Issues

**Known problems with current price data:**
- **Modal price problem**: Agmarknet reports modal (most common) price, not volume-weighted average
- **Quality variation**: Same commodity grade varies; "modal" masks quality premium/discount
- **Spatial coverage**: Large states (MP, Rajasthan) have sparse mandi coverage
- **Commodity classification**: Inconsistent variety naming across mandis
- **Missing prices**: Holidays, technical issues create data gaps

### 1.3 Data Model

```python
class MandiPrice:
    mandi_id: str           # e-NAM mandi code
    commodity_code: str      # NPCS standard
    variety: str             # e.g., "Medium Grain"
    grade: str               # A/B/C or null
    price_min: float         # Rs/quintal
    price_max: float         # Rs/quintal
    price_modal: float       # Most common price
    volume_traded: float     # Quintals (if available)
    date: date
    source: str              # e-NAM / Agmarknet / StateAPMC

class PriceTrend:
    commodity_code: str
    mandi_id: str
    period: str              # "7day", "30day", "season"
    trend: enum              # Rising, Stable, Falling
    change_pct: float        # % change over period
    volatility: float       # CV (coefficient of variation)
    forecast_7day: float    # Predicted price (ML-based)
    forecast_confidence: float
```

---

## 2. Price Intelligence Features

### 2.1 Current Price View

**For farmer**: "Today's price at nearest mandis for your crop"

| Information | Display Format |
|---|---|
| Price at 3 nearest mandis | Table with distance, price, trend |
| Price at major consumption center | For crops with transport arbitrage |
| Comparison to MSP | Is current price above or below MSP? |
| Price vs last week | % change, direction arrow |

**Example WhatsApp output**:
```
📊 *TODAY'S MUSTARD PRICES*

🏪 Mandi          Price    vs MSP
   Jaipur       ₹5,200/Q   +3%
   Kota         ₹5,100/Q   +1%
   Bikaner      ₹4,950/Q   -1%

📈 Last 7 days: Stable (+1%)

💡 TIP: Prices may rise after Diwali.
Consider storing if you have storage.
```

### 2.2 Price Trend Analysis

| Trend Type | Description | Farmer Action |
|---|---|---|
| **Rising** | Prices increasing week-over-week | Consider holding if storage available |
| **Stable** | Prices within ±5% range | Sell when convenient |
| **Falling** | Prices declining | Sell soon; avoid storage |
| **Seasonal low** | Below historical average for this period | Wait if possible; may recover |

### 2.3 Selling Window Prediction

**Key insight**: Most farmers sell at harvest when prices are seasonal low. Storage can capture 10-20% price appreciation over 2-3 months.

**Prediction model**: When will prices be highest this season?

```
Historical pattern for [Crop] in [Region]:
- Peak price month: February
- Low price month: October (harvest)
- Typical storage gain: 15-20%
- Current price: ₹4,800/Q
- Predicted peak: ₹5,600/Q
- Potential gain from storage: ₹800/Q

Is storage viable?
✓ Your production: 20 quintals
✓ Potential additional income: ₹16,000
✓ Storage cost: ₹2,000 (₹100/Q × 20Q)
✓ Net gain: ₹14,000
```

### 2.4 Distress Sale Detection

**Warning signals that indicate distress selling:**
- Price >15% below MSP
- Price at seasonal low (<10th percentile)
- Farmer sells within 7 days of harvest
- Farmer sells entire crop immediately

**Platform response to distress signals:**
- Alert channel partner (arthiya, FPO staff)
- Offer alternative: nearby FPO that buys at MSP
- Offer storage facility information
- Document for future intervention

---

## 3. mandi Accessibility Mapping

### 3.1 Distance & Cost Calculation

For each farmer, compute:
- Nearest 3 mandis by road distance
- Transport cost at current fuel prices
- Time to reach each mandi
- Commodity-specific mandi specialization (some mandis have better prices for specific crops)

### 3.2 mandi Profile

| Attribute | Description |
|---|---|
| `mandi_id` | e-NAM code |
| `mandi_name` | Full name |
| `district` | District location |
| `commodities_traded` | List of major commodities |
| `typical_volume` | Average daily volume |
| `closing_time` | When trading ends |
| `facilities` | Cold storage, grading, etc. |
| `weekend_closure` | Days closed |

---

## 4. Selling Decision Support

### 4.1 Should I Sell Now or Store?

**Decision Framework**:

```
┌─────────────────────────────────────────────────────────────┐
│                    SELLING DECISION                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Current Price vs MSP?                                      │
│  ├── Above MSP (+10%+) → Consider selling NOW              │
│  ├── At MSP (±10%)  → Calculate storage economics         │
│  └── Below MSP       → Check price trend; is it recovering?│
│                                                             │
│  Do you have storage?                                       │
│  ├── NO  → Forced to sell at current price                 │
│  │      → Check if FPO/Processor buys at MSP nearby       │
│  │      → Alert for future seasons (storage needed)       │
│  └── YES → Proceed to storage economics calculation        │
│                                                             │
│  Storage Economics:                                         │
│  ├── Expected price gain if stored (2-3 months)            │
│  ├── Storage cost (facility + quality loss)               │
│  ├── Cash flow need (do you need money NOW?)              │
│  └── Net benefit calculation                               │
│                                                             │
│  Price Forecast:                                            │
│  ├── 7-day forecast: [Direction]                           │
│  ├── Seasonal pattern: [Expected peak month]               │
│  └── Weather impact: [Any events affecting prices]         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Storage Economics Calculator

```python
def calculate_storage_benefit(
    current_price: float,      # Rs/quintal today
    expected_price_peak: float, # Rs/quintal at seasonal peak
    storage_cost: float,         # Rs/quintal for season
    quality_loss: float,         # % weight loss in storage
    quantity_quintal: float,     # Quintals to store
    cash_need_urgency: int      # 1-5, how urgently need cash
) -> dict:
    gross_gain = (expected_price_peak - current_price) * quantity_quintal
    net_gain = gross_gain - (storage_cost * quantity_quintal)
    adjusted_quantity = quantity_quintal * (1 - quality_loss)
    effective_gain = (expected_price_peak * adjusted_quantity) - (current_price * quantity_quintal) - storage_cost

    if cash_need_urgency >= 4:
        recommendation = "SELL NOW - urgent cash need"
    elif net_gain < 0:
        recommendation = "SELL NOW - storage not profitable"
    elif net_gain < storage_cost * 0.3:
        recommendation = "BORDERLINE - depends on your cash position"
    else:
        recommendation = "STORAGE VIABLE - consider holding"

    return {
        "recommendation": recommendation,
        "gross_gain": gross_gain,
        "net_gain": net_gain,
        "payback_days": None  # not applicable for agricultural
    }
```

---

## 5. Market Information Features

### 5.1 Demand/Supply Indicators

| Indicator | Source | Use |
|---|---|---|
| Arrivals trend | e-NAM daily volume | Is market flooded? |
| Export demand | Trade news | Will prices get support? |
| Procurement进度 | FCI/state procurement | Will MSP procurement push prices up? |
| Stock levels | Industry estimates | Is there a glut? |

### 5.2 Policy Impact Signals

**What to monitor:**
- Export duty changes (onion, rice, sugar)
- Import duty changes
- Stock holding limits
- MSP procurement announcement

**How to communicate:**
- "📢 Government may release onion export ban. Prices expected to [rise/fall]."
- "⚠️ Rice export duty increased. Impact on paddy prices expected in 2-3 weeks."

---

## 6. Integration with Arthiya/FPO System

### 6.1 Arthiya Information Access

**Current reality**:
- Arthiyas have information advantage (know prices across mandis)
- Farmers trust arthiyas because they're local and provide credit
- Arthiya profit from price spread, not farmer welfare

**Platform approach**:
- Provide arthiyas with better price intelligence (they become channel partners)
- Make information asymmetry less profitable
- Track price offered vs market price; flag discrepancies

### 6.2 FPO Direct Purchase Support

**FPOs can offer MSP or better prices if:**
- They have grading and storage infrastructure
- They have buyers lined up
- They can aggregate volume

**Platform supports FPO by:**
- Telling farmers which FPOs are buying and at what price
- Helping FPOs manage procurement logistics
- Tracking quality and ensuring payment

---

## 7. Farmer-Facing Messages

### 7.1 Price Alert Format

```
📈 *PRICE ALERT — [CROP]*

Your area: [Village], [District]
Latest price: ₹[X]/quintal at [Mandi]

vs MSP ₹[Y]: [Above/At/Below]

[7-day trend: ▲/▼/— ]

[Reason for movement]

[Recommendation: Sell/Hold/Store]
```

### 7.2 What NOT to Do

- ❌ Don't just show raw prices without context (MSP, trend)
- ❌ Don't assume farmers can transport to distant mandis
- ❌ Don't recommend selling if farmer has no viable buyer
- ❌ Don't give short-term speculation advice (this isn't a stock market)

---

## 8. Metrics

### 8.1 System Metrics

| Metric | Target |
|---|---|
| Price data coverage (% mandis reporting) | >85% |
| Data latency (price to farmer) | <24 hours |
| Price accuracy (vs actual transaction) | Within 5% |
| Forecast accuracy (7-day direction) | >65% |

### 8.2 Farmer Impact Metrics

| Metric | Target |
|---|---|
| % farmers receiving price > MSP | >50% |
| Average selling price vs district average | +5% or better |
| Reduction in distress sales | Measurable from baseline |
| Storage uptake (where viable) | >20% of viable cases |

---

## 9. Edge Cases

### 9.1 No Price Data for Farmer's Crop/Mandi
- Show prices from nearest comparable mandi
- Clearly state "This is the closest mandi; prices may vary"
- Flag as "insufficient data" if <3 comparable prices

### 9.2 Farmer Has No Transport
- Show local buyer options (arthiya, FPO)
- Don't suggest distant mandis unless transport is arranged
- Connect with logistics providers if available

### 9.3 Perishable Crops (Tomato, Onion, Milk)
- Short selling windows (days, not weeks)
- Cold storage facility information
- Processing unit locations

### 9.4 Contract Farming
- If farmer has a contract, price certainty is already there
- Provide only quality standards and timing
- Don't duplicate contract details

---

## 10. Compliance & Data

### 10.1 Data Licensing

- e-NAM data: Public domain, but API access needs registration
- Agmarknet: Government open data
- Private sources: License required per provider

### 10.2 Anti-Trust Considerations

- Platform must NOT:
  - Coordinate prices among buyers
  - Suggest buyers collude on pricing
  - Act as a price-fixing mechanism
- Platform shows information; does NOT negotiate or trade

---

*Spec authority: Market Intelligence & Selling Decision Support*
*Version: 1.0*
