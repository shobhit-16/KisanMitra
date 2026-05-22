# Income Ledger — Domain Spec

**Spec File:** `income-ledger.md`
**Domain:** Sale Recording
**Phase:** 1
**Last Updated:** 2026-05-22

---

## Purpose

Record every onion sale the farmer makes, compute the seasonal baseline price, and automatically flag distress sales that fall below MSP.

---

## Sale Entity

### Attributes

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | UUID | YES | Unique identifier |
| `phone` | string(10) | YES | Farmer's phone (FK) |
| `sale_date` | date | YES | Date of sale |
| `quantity_quintal` | float | YES | Quantity sold (quintals) |
| `price_per_quintal` | int | YES | Price received (₹/quintal) |
| `mandi` | string | YES | Which mandi sold at |
| `total_revenue` | int | AUTO | `quantity_quintal * price_per_quintal` |
| `is_distress` | bool | AUTO | True if `price_per_quintal < msp * 0.85` |
| `distress_reason` | string | AUTO | Reason if distress |
| `notes` | string | NO | Farmer's notes |
| `created_at` | datetime | YES | Record creation |

### Constraints

- `sale_date` must be ≥ farmer's `created_at` (can't record sales before account)
- `quantity_quintal` must be > 0 and ≤ 1000
- `price_per_quintal` must be ≥ 0
- Only one distress record per farmer per day (no duplicate distress entries)

---

## Distress Detection

### Threshold

```python
MSP_ONION = 750  # ₹/quintal for Rabi onion (2024-25)
DISTRESS_THRESHOLD = MSP_ONION * 0.85  # = 637.5

def is_distress_sale(price_per_quintal):
    return price_per_quintal < DISTRESS_THRESHOLD
```

### Distress Reasons

```python
class DistressReason(Enum):
    FORCED_SELL = "Sold immediately due to cash emergency"
    NO_STORAGE = "No storage capacity — had to sell at any price"
    WEAK_BARGAINING = "Sold at low price due to weak bargaining position"
    MIDDLEMAN_EXPLOITATION = "Sold to village trader below mandi price"
```

Auto-assigned based on available data:
- If `price_per_quintal < MSP * 0.5` (less than half MSP) → `MIDDLEMAN_EXPLOITATION`
- If farmer has CRITICAL obligation due within 3 days → `FORCED_SELL`
- If no storage capacity on record → `NO_STORAGE`
- Otherwise → `WEAK_BARGAINING`

---

## Baseline Price Calculation

### Algorithm

```python
def compute_baseline_price(sales: List[Sale]):
    non_distress_sales = [s for s in sales if not s.is_distress]
    if not non_distress_sales:
        return None  # All sales are distress

    total_revenue = sum(s.quantity_quintal * s.price_per_quintal for s in non_distress_sales)
    total_quantity = sum(s.quantity_quintal for s in non_distress_sales)

    return total_revenue / total_quantity  # Weighted average
```

Baseline is a **weighted average** of all non-distress sales, weighted by quantity. This ensures a farmer who sold 10q at ₹28 and 5q at ₹30 has a baseline closer to ₹28.50 (not ₹29 flat).

### Baseline Display Thresholds

| Baseline Price | Display Message |
|---|---|
| ≥ ₹35/qt | "Your baseline is excellent — strong bargaining position" |
| ₹27–35/qt | "Your baseline: ₹X/kg — above market average" |
| ₹20–27/qt | "Your baseline: ₹X/kg — monitor prices carefully" |
| < ₹20/qt | "Your baseline is low — consider FPO aggregation" |

---

## Income Ledger Endpoint

### GET /api/farmers/{phone}/ledger

**Response:**
```json
{
  "phone": "9876543210",
  "season": "RABI",
  "year": 2026,
  "baseline_price": 2700,
  "baseline_unit": "quintal",
  "total_sales": 4,
  "total_revenue": 58500,
  "distress_count": 1,
  "sales": [
    {
      "id": "uuid-1",
      "sale_date": "2026-02-15",
      "quantity_quintal": 5,
      "price_per_quintal": 2800,
      "mandi": "Lasalgaon",
      "total_revenue": 14000,
      "is_distress": false,
      "status_display": "सामान्य (Normal)"
    },
    {
      "id": "uuid-2",
      "sale_date": "2026-02-22",
      "quantity_quintal": 4,
      "price_per_quintal": 500,
      "mandi": "Village Trader",
      "total_revenue": 2000,
      "is_distress": true,
      "distress_reason": "Sold immediately due to cash emergency",
      "status_display": "तनाव (Distress)"
    }
  ]
}
```

### GET /api/farmers/{phone}/ledger/summary

Returns only aggregate statistics without the full sales list (lighter response).

---

## Sale Recording Endpoint

### POST /api/farmers/{phone}/sales

**Request:**
```json
{
  "sale_date": "2026-02-20",
  "quantity_quintal": 5,
  "price_per_quintal": 2800,
  "mandi": "Lasalgaon",
  "notes": "Good quality batch"
}
```

**Response (201):**
```json
{
  "id": "uuid-new",
  "sale_date": "2026-02-20",
  "quantity_quintal": 5,
  "price_per_quintal": 2800,
  "mandi": "Lasalgaon",
  "total_revenue": 14000,
  "is_distress": false,
  "created_at": "2026-05-22T10:00:00Z"
}
```

**Auto-computed:** `is_distress` is computed server-side — client cannot override it.

---

## MSP Reference Table

| Commodity | MSP (₹/quintal) | Crop Season | Note |
|---|---|---|---|
| Onion (Rabi) | 750 | Nov–Mar | 2024-25 rate |
| Paddy (Kharif) | 2,183 | Jun–Oct | 2024-25 rate (per quintal) |

MSP values are fetched from government API or stored as constants. Display: "MSP ₹750/quintal → You're ₹2,050 above floor price" for ₹28/qt.

---

## Demo Data (from demo.html Screen 7)

4 recorded sales:
1. **Normal** — 5q at ₹28/kg = ₹14,000, Lasalgaon ✓
2. **Normal** — 4q at ₹27/kg = ₹10,800, Niphad ✓
3. **Normal** — 3q at ₹26/kg = ₹7,800, Yeola ✓
4. **DISTRESS** — 2q at ₹5/kg = ₹1,000, Village Trader ⚠️

Baseline: ₹27/kg (weighted average of first 3 sales)

Distress sale flagged because ₹5/kg = ₹500/quintal, which is below ₹637.5 threshold.
