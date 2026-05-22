# Income Engine — Domain Spec

**Spec File:** `income-engine.md`
**Domain:** Selling Decision
**Phase:** 1
**Last Updated:** 2026-05-22

---

## Purpose

The Income Engine evaluates the complete financial picture for a farmer's crop — mandi prices, storage costs, and cash flow — to recommend whether to sell now, store, or hold.

---

## Key Concepts

### Onion Price Calendar (Nashik, Rabi Season)

| Month | Typical Price (₹/quintal) | Reason |
|---|---|---|
| Feb (harvest) | ₹20–25 | Peak supply — all farmers harvest |
| Mar | ₹25–30 | Supply normalizes |
| Apr | ₹30–35 | Supply tightens |
| May | ₹35–42 | Off-season, onion scarce |
| Jun | ₹40–50 | Minimum supply |
| Jul | ₹45–55 | Peak storage profit month |
| Aug | ₹40–48 | New crop begins |
| Sep | ₹25–30 | Early kharif arrival |
| Oct | ₹20–25 | Kharif onion in market |

**MSP for Rabi Onion:** ₹750/quintal (2024-25 rate)
**Storage cost:** ₹2.50–3.00/quintal/day (ambient storage in Nashik)
**Storage loss:** 15–20% over 2 months (sprouting, rotting)

---

## Income Assessment Endpoint

### GET /api/farmers/{phone}/income-engine

**Response:**
```json
{
  "phone": "9876543210",
  "assessed_at": "2026-05-22T10:00:00Z",
  "crop": "RABI_ONION",
  "season": "RABI",
  "current_mandi": {
    "name": "Lasalgaon",
    "price": 2800,
    "unit": "quintal",
    "msp": 750,
    "above_msp": 2050,
    "trend_7day": 8.2,
    "trend_direction": "UP"
  },
  "storage_estimate": {
    "enabled": true,
    "quantity_quintal": 5,
    "storage_days": 60,
    "storage_cost": 160,
    "expected_sale_price": 3500,
    "expected_gain": 875,
    "net_gain": 715,
    "breakeven_price": 2810
  },
  "cash_flow": {
    "surplus_30day": 8500,
    "upcoming_obligations": 3200,
    "obligation_type": "KCC_EMI"
  },
  "recommendation": {
    "action": "STORE",
    "confidence": "HIGH",
    "message": "Storage viable — ₹715 net gain expected",
    "message_hi": "भंडारण व्यवहार्य — ₹715 शुद्ध लाभ अपेक्षित",
    "message_mr": "संग्रहण व्यवहार्य — ₹715 शुद्ध नफा अपेक्षित",
    "reason": "Current price ₹28/qt is below peak (₹35/qt in May). Storage 60 days costs ₹160 but gains ₹875.",
    "gate_4_status": "OPEN"
  }
}
```

---

## Selling Window Logic

### Decision Tree

```
START: Farmer has harvested quantity Q at current price P

Is harvest date entered in system?
  NO → BLOCK selling recommendations
  YES → Continue

Is Q > 0?
  NO → Recommend "Record your harvest first"
  YES → Continue

Is current date within 7 days of harvest_date?
  YES → EMERGENCY_SELL → "Sell immediately, no time for storage"
  NO → Continue

Is P >= expected_peak_price * 0.9?
  YES → SELL → "Price near peak, sell now"
  NO → Continue

Is (expected_peak_price - P) * Q > storage_cost?
  YES → STORE → "Storage profitable"
  NO → SELL → "Storage not profitable, sell now"
```

### Emergency Sell Trigger

When farmer has:
- KCC EMI due within 3 days, OR
- Hospital/health crisis, OR
- No cash for next 7 days

→ Emergency sell recommendation fires even if storage would be more profitable.

---

## Mandi Price Fetching

### e-NAM Integration Contract

**Endpoint:** `GET /api/mandi/prices?commodity=onion&district=nashik`

**Response from e-NAM:**
```json
{
  "commodity": "onion",
  "district": "nashik",
  "prices": [
    {
      "mandi": "Lasalgaon",
      "modal_price": 2800,
      "min_price": 2500,
      "max_price": 3100,
      "arrival_date": "2026-05-22",
      "arrival_quantity_quintal": 500
    },
    {
      "mandi": "Yeola",
      "modal_price": 2750,
      "min_price": 2400,
      "max_price": 3000,
      "arrival_date": "2026-05-22",
      "arrival_quantity_quintal": 150
    },
    {
      "mandi": "Niphad",
      "modal_price": 2830,
      "min_price": 2600,
      "max_price": 3100,
      "arrival_date": "2026-05-22",
      "arrival_quantity_quintal": 200
    }
  ],
  "fetched_at": "2026-05-22T09:30:00Z",
  "cache_expires_at": "2026-05-22T09:45:00Z"
}
```

**Cache TTL:** 15 minutes
**Fallback:** If e-NAM unavailable, return cached price with `is_cached: true` flag
**Alert threshold:** Store per-farmer price alert preferences — alert when price crosses threshold

---

## MSP Comparison

Every mandi price response MUST include MSP comparison:

```
above_msp = modal_price - msp
above_msp_percent = (modal_price - msp) / msp * 100

# Example:
# modal_price = 2800, msp = 750
# above_msp = 2050
# above_msp_percent = 273%
```

Display message: "MSP ₹750/qt → You're ₹2,050 above floor price"

---

## Distress Selling Detection

A sale is flagged as **DISTRESS** when:

```python
is_distress = sale_price_per_quintal < (msp * 0.85)
# MSP * 0.85 = ₹637.50 for onion
# A sale below ₹638/quintal is distress
```

Distress threshold is 15% below MSP. This captures farmers who are forced to sell immediately due to:
- Cash emergency (hospital, school fee, debt)
- No storage capacity
- No price negotiation power

---

## Price Alert System

### Alert Types

| Alert | Trigger | Message |
|---|---|---|
| Price rise | Price increases ≥8% in 7 days | "Onion prices up 8% this week — good time to check storage" |
| Price drop | Price drops ≥5% in 3 days | "Price dropped ₹2 in 3 days — consider selling if you have stock" |
| Above MSP | Any sale above MSP | No alert — expected behavior |
| Near peak | Price ≥ ₹40/qt | "Price at ₹40+ — highest in 3 months" |
| Below MSP | Any sale below MSP | Alert to FPO advisor: farmer may need support |

### Farmer Alert Preferences

```python
@dataclass
class PriceAlertPreference:
    phone: str
    enabled: bool              # Global toggle
    drop_threshold: int        # Alert if price drops ₹N (default 2)
    rise_threshold: int       # Alert if price rises N% (default 8)
    preferred_mandis: List[str]  # e.g., ["Lasalgaon", "Niphad"]
```
