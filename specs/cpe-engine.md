# CPE Engine — Domain Spec

**Spec File:** `cpe-engine.md`
**Domain:** Recommendation Filtering
**Phase:** 1
**Last Updated:** 2026-05-22

---

## Overview

The Constraint Priority Engine (CPE) is a 5-gate rule engine that filters recommendations before they reach the farmer. Each gate evaluates the farmer's current state against the recommendation's constraints. A recommendation must pass ALL applicable gates to reach the farmer.

```
[Engine] → [Rec Bus] → [G1] → [G2] → [G3] → [G4] → [G5] → [Farmer]
                         ↓       ↓       ↓       ↓       ↓
                       PASS   PASS   PASS   PASS   PASS
                       or      or      or      or      or
                      BLOCK  BLOCK  BLOCK  BLOCK  BLOCK
```

---

## Recommendation Bus

### Structure

```python
@dataclass
class Recommendation:
    id: str                          # UUID
    category: RecCategory             # HEALTH_CRISIS, CASH_STRESS, NORMAL, etc.
    type: RecType                    # SCHEME, CREDIT, INFO, ACTION
    title: str                       # Short title (EN)
    title_hi: str                    # Hindi translation
    title_mr: str                    # Marathi translation
    description: str                  # Description (EN)
    description_hi: str
    description_mr: str
    priority: int                    # 1=highest
    gate_requirements: List[GateID]  # Which gates must pass
    resource_url: Optional[str]       # Link to apply / learn more
    resource_phone: Optional[str]    # Helpline number
    amount: Optional[int]            # Monetary value (₹) if applicable
    icon: str                        # Emoji or SVG icon name
    triggered_by: Optional[TriggerType]  # What entered this rec
```

### Recommendation Categories

```python
class RecCategory(Enum):
    HEALTH_CRISIS    # Emergency health resources
    CASH_STRESS      # Credit/scheme for financial stress
    NORMAL           # Standard recommendations
    SEASONAL         # Crop-specific seasonal advice
    MARKET           # Price/selling recommendations
    SOIL             # Soil health (Phase 2)
    CLIMATE          # Weather alerts (Phase 3)
```

---

## Gate Definitions

### Gate 1 — Resource Category

**Purpose:** Unlocks or suppresses based on farmer's current resource crisis level.

**Inputs:**
```python
@dataclass
class Gate1Input:
    health_status: HealthStatus  # NORMAL, CRISIS
    has_hospitalized_member: bool
```

**Logic:**
```
IF health_status == CRISIS OR has_hospitalized_member:
    PASS: HEALTH_CRISIS category recommendations
    BLOCK: All commercial credit recommendations
ELSE:
    PASS: All recommendations
```

**Suppressed when crisis:** Commercial credit ads, non-emergency loans, luxury recommendations

**Unlocked when crisis:** Ayushman Bharat, emergency grants, CSC hospital referrals

---

### Gate 2 — Weather Fit

**Purpose:** Blocks recommendations that are inappropriate given current weather conditions.

**Inputs:**
```python
@dataclass
class Gate2Input:
    current_weather: WeatherCondition  # CLEAR, CLOUDY, RAIN, HEAVY_RAIN, STORM
    forecast_7day: List[WeatherCondition]
    crop_stage: CropStage  # SOWING, GROWTH, HARVEST, POST_HARVEST
```

**Logic:**
```
IF weather == HEAVY_RAIN OR weather == STORM:
    BLOCK: Pesticide spraying recommendations
    BLOCK: Fertilizer application recommendations
    PASS: All others

IF forecast_7day contains HEAVY_RAIN within 3 days:
    WARN: "Heavy rain expected — delay pesticide spraying"

IF crop_stage == HARVEST:
    PASS: Harvest timing recommendations only
    BLOCK: New planting recommendations
```

**Suppressed during heavy rain:** Pesticide, fertilizer application timing

---

### Gate 3 — Cash Flow

**Purpose:** Suppresses non-essential recommendations when farmer has cash flow deficit.

**Inputs:**
```python
@dataclass
class Gate3Input:
    surplus_30day: int        # Net position after all obligations
    obligation_count_urgent: int  # Count of obligations due within 7 days
    has_overdue_emi: bool
```

**Logic:**
```
IF surplus_30day < 0:
    BLOCK: Non-essential recommendations (entertainment, luxury)
    BLOCK: Fertilizer credit recommendations
    PASS: Emergency resources, obligation management, MSP-selling recommendations
    FLAG: "Cash flow deficit — prioritize essential recommendations"

IF surplus_30day < 5000:
    PARTIAL: Credit recommendations — show only emergency credit options
    FLAG: "Limited cash flow — review upcoming obligations"

ELSE:
    PASS: All recommendations
```

**Suppressed during deficit:** Non-essential consumer recommendations, cosmetic/luxury recommendations

**Passes during deficit:** Ayushman Bharat, MSP-linked selling recommendations, obligation management tools

---

### Gate 4 — Selling Window

**Purpose:** Activates or deactivates market-timing recommendations based on harvest status.

**Inputs:**
```python
@dataclass
class Gate4Input:
    harvest_date_entered: bool
    days_since_harvest: int       # -1 if not harvested
    current_price: int            # ₹/quintal from e-NAM
    price_trend_7day: float      # Percentage change
    storage_cost_estimated: int   # ₹ to store remaining crop
    expected_price_peak: int      # ₹/quintal at peak (Feb)
```

**Logic:**
```
IF NOT harvest_date_entered:
    PASS: Pre-harvest recommendations (price watch, storage planning)
    BLOCK: Selling/mandi recommendations
    EXIT

IF days_since_harvest <= 7:
    PASS: SELL recommendations (immediate sale after harvest)
    BLOCK: Storage recommendations (too late to store)

IF current_price >= expected_price_peak * 0.9:
    PASS: SELL recommendations (price near peak)
    FLAG: "Price is near peak — consider selling soon"
    EXIT

IF storage_cost_estimated < (expected_price_peak - current_price) * quantity:
    PASS: STORE recommendations
    EXIT

ELSE:
    PASS: SELL recommendations (storage not profitable)
```

**Recommendation types by selling window:**
- Pre-harvest: price watch, storage cost calculator, mandi price alerts
- Harvest window (≤7 days post-harvest): immediate selling, no storage
- Peak price window: sell recommendations with net gain math
- Post-peak: sell recommendations (storage cost exceeds gains)

---

### Gate 5 — Loan Compliance

**Purpose:** Blocks new credit recommendations when farmer has overdue KCC EMI or default.

**Inputs:**
```python
@dataclass
class Gate5Input:
    has_kcc_loan: bool
    kcc_emi_status: EMIStatus  # CURRENT, DUE, OVERDUE
    kcc_overdue_amount: int     # ₹ overdue amount
    has_other_default: bool
```

**Logic:**
```
IF NOT has_kcc_loan:
    PASS: All credit recommendations
    EXIT

IF kcc_emi_status == OVERDUE:
    BLOCK: All commercial credit recommendations
    PASS: Government emergency credit only
    PASS: KCC restructuring schemes
    FLAG: "KCC payment overdue — new credit restricted"
    EXIT

IF kcc_emi_status == DUE:
    PARTIAL: Show only emergency credit and government schemes
    BLOCK: Commercial bank credit, private NBFC recommendations
    EXIT

ELSE:
    PASS: All credit recommendations
```

**Suppressed when KCC overdue:** Commercial bank loans, NBFC credit cards, private lender recommendations

**Passes when KCC overdue:** KCC restructuring, government emergency credit, Ayushman Bharat

---

## Gate Response Schema

Each gate returns:

```python
@dataclass
class GateResult:
    gate_id: GateID
    status: GateStatus  # PASS, BLOCK, PARTIAL, NOT_APPLICABLE
    reason: str                    # Human-readable reason
    reason_hi: str                 # Hindi translation
    reason_mr: str                 # Marathi translation
    suppressed_recs: List[str]     # List of rec IDs blocked (if any)
```

---

## CPE Evaluation Endpoint

### POST /api/cpe/evaluate

**Request:**
```json
{
  "phone": "9876543210",
  "recommendations": [
    {
      "id": "rec-ayushman-001",
      "category": "HEALTH_CRISIS",
      "type": "SCHEME",
      "gate_requirements": ["G1", "G3"]
    }
  ]
}
```

**Response:**
```json
{
  "phone": "9876543210",
  "evaluated_at": "2026-05-22T10:00:00Z",
  "gate_states": {
    "G1": {"status": "PASS", "reason": "Health status normal"},
    "G2": {"status": "PASS", "reason": "Weather is clear"},
    "G3": {"status": "PASS", "reason": "Cash flow healthy"},
    "G4": {"status": "PASS", "reason": "Selling window open"},
    "G5": {"status": "NOT_APPLICABLE", "reason": "No KCC loan"}
  },
  "recommendations": [
    {
      "id": "rec-ayushman-001",
      "status": "APPROVED",
      "passed_gates": ["G1", "G3"],
      "blocked_by": null
    }
  ]
}
```

---

## Demo Scenarios (from demo.html)

| Scenario | G1 | G2 | G3 | G4 | G5 | Result |
|---|---|---|---|---|---|---|
| Healthy owner | PASS | PASS | PASS | OPEN | PASS | All recs pass |
| Cash stress | PASS | PASS | **BLOCK** | OPEN | PASS | Non-essential blocked |
| Health crisis | **BLOCK** | PASS | PASS | OPEN | PASS | Only health rec passes |
| Harvest window | PASS | PASS | PASS | **OPEN** | PASS | Selling recs active |

---

## Out of Scope (Phase 2/3)

- Soil health recommendations (Gate 2 variant for soil type)
- Climate adaptation recommendations (drought, flood responses)
- Crop disease alerts (requires image recognition — Phase 3)
