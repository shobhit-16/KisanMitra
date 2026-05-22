# Obligation Calendar — Domain Spec

**Spec File:** `obligation-calendar.md`
**Domain:** Financial Obligations
**Phase:** 1
**Last Updated:** 2026-05-22

---

## Purpose

Track all financial obligations a farmer has — KCC EMI, school fees, land rent, cooperative dues — and compute cash flow health to inform recommendations.

---

## Obligation Types

### Enum: ObligationType

```python
class ObligationType(Enum):
    KCC_EMI           # Kisan Credit Card equated monthly installment
    SCHOOL_FEE       # School/college fee for children
    LAND_RENT        # Rent for leased land
    COOPERATIVE_DUE  # Cooperative society dues
    INSURANCE_PREMIUM # Crop insurance or life insurance
    WATER_ELECTRICITY # Irrigation water or electricity bill
    OTHER            # Miscellaneous
```

### Priority Levels

```python
class ObligationPriority(Enum):
    CRITICAL  # ≤3 days — KCC EMI default,饿死饿饿 hospital bill
    URGENT    # ≤7 days — school fee, KCC EMI approaching
    SOON      # ≤30 days — rent, cooperative dues
    NORMAL    # >30 days
```

---

## Obligation Entity

### Attributes

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | UUID | YES | Unique identifier |
| `phone` | string(10) | YES | Farmer's phone (FK) |
| `type` | ObligationType | YES | Category of obligation |
| `amount` | int | YES | Amount due in ₹ |
| `due_date` | date | YES | When payment is due |
| `description` | string | NO | Free text description |
| `reminder_date` | date | NO | When to send reminder |
| `reminder_flag` | bool | YES | Is reminder active — default false |
| `is_paid` | bool | YES | Has been paid — default false |
| `paid_date` | date | NO | Actual payment date |
| `paid_amount` | int | NO | Actual amount paid (may differ) |
| `created_at` | datetime | YES | Record creation |
| `updated_at` | datetime | YES | Last modification |

### Constraints

- `due_date` must be ≥ `created_at` (cannot have past-due obligations created today)
- `reminder_date` must be ≤ `due_date`
- `is_paid == True` implies `paid_date` is set
- `amount` must be > 0

---

## Cash Flow Calculation

### GET /api/farmers/{phone}/cashflow?days=30

**Request params:**
- `days` — time window in days (default 30, max 90)

**Response:**
```json
{
  "phone": "9876543210",
  "window_days": 30,
  "calculated_at": "2026-05-22T10:00:00Z",
  "income": {
    "expected_sale_revenue": 14000,
    "other_income": 2000,
    "total_income": 16000
  },
  "obligations": {
    "total_due": 10200,
    "count_urgent": 1,
    "by_type": {
      "KCC_EMI": {"amount": 3200, "due_in_days": 12, "priority": "URGENT"},
      "SCHOOL_FEE": {"amount": 5000, "due_in_days": 4, "priority": "CRITICAL"},
      "LAND_RENT": {"amount": 2000, "due_in_days": 60, "priority": "SOON"}
    }
  },
  "cash_flow": {
    "surplus": 5800,
    "surplus_after_critical": 800,
    "status": "BALANCED",
    "status_detail": "Cash flow positive but tight — ₹800 after critical obligations"
  }
}
```

### Cash Flow Status

```python
def compute_cash_flow_status(surplus, critical_count):
    if surplus < 0:
        return "DEFICIT"
    if critical_count > 0 and surplus < 5000:
        return "TIGHT"
    if surplus > 10000:
        return "HEALTHY"
    return "BALANCED"
```

| Status | Surplus | Critical obligations | CPE Gate 3 |
|---|---|---|---|
| DEFICIT | < 0 | Any | BLOCK non-essential |
| TIGHT | 0–5000 | ≥1 | PARTIAL — emergency credit only |
| BALANCED | 5000–10000 | 0 | PASS |
| HEALTHY | > 10000 | 0 | PASS |

---

## Endpoints

### POST /api/farmers/{phone}/obligations

**Request:**
```json
{
  "type": "KCC_EMI",
  "amount": 3200,
  "due_date": "2026-06-03",
  "description": "KCC EMI June 2026",
  "reminder_date": "2026-06-01"
}
```

**Response (201):** Created obligation object

### GET /api/farmers/{phone}/obligations

**Query params:**
- `status` — `pending`, `paid`, `all` (default `pending`)
- `sort` — `due_date`, `amount`, `priority` (default `due_date`)

**Response (200):**
```json
{
  "phone": "9876543210",
  "obligations": [
    {
      "id": "uuid-1",
      "type": "SCHOOL_FEE",
      "amount": 5000,
      "due_date": "2026-06-15",
      "priority": "CRITICAL",
      "due_in_days": 4,
      "reminder_flag": true,
      "is_paid": false
    },
    {
      "id": "uuid-2",
      "type": "KCC_EMI",
      "amount": 3200,
      "due_date": "2026-06-03",
      "priority": "URGENT",
      "due_in_days": 12,
      "reminder_flag": false,
      "is_paid": false
    }
  ],
  "total_pending": 8200
}
```

### GET /api/farmers/{phone}/obligations/urgent

Returns only obligations with `due_in_days ≤ 7`.

### PUT /api/farmers/{phone}/obligations/{id}/reminder

**Request:**
```json
{"reminder_flag": true}
```

**Response (200):** Updated obligation

### DELETE /api/farmers/{phone}/obligations/{id}

Marks obligation as paid: `is_paid=true`, `paid_date=today`.

**Response (204):** No content

---

## Reminder Logic

When `reminder_flag=True` and current date ≥ `reminder_date`:

1. App shows notification: "Obligation due: ₹{amount} in {due_in_days} days"
2. If obligation is CRITICAL and no reminder sent in 48 hours → send reminder
3. Reminders sent at 9am local time

---

## Demo Data (from demo.html)

| Obligation | Amount | Due Date | Priority |
|---|---|---|---|
| School fee | ₹5,000 | April 15 (4 days) | CRITICAL |
| KCC EMI | ₹3,200 | June 3 (12 days) | URGENT |
| Land rent | ₹2,000 | July 15 (60 days) | SOON |

Cash flow after critical obligations: ₹8,500 surplus
