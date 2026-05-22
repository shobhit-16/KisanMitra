# Spec Compliance Audit — Round 1

**Project:** Kisanmitra
**Audit Date:** 2026-05-22
**Spec Files Verified:**
- `specs/farmer-profile.md`
- `specs/obligation-calendar.md`
- `specs/income-ledger.md`

**Implementation Files Verified:**
- `src/kisanmitra/models.py`
- `src/kisanmitra/repository.py`
- `src/kisanmitra/api.py`
- `src/kisanmitra/obligation_repository.py`
- `src/kisanmitra/cashflow_service.py`
- `src/kisanmitra/sale_repository.py`

---

## Summary

| Severity | Count |
|----------|-------|
| HIGH | 2 |
| MEDIUM | 1 |
| PASS | 35+ |

---

## Finding Register

| ID | Severity | Spec Section | Finding | Spec Claim | Actual Code | Verification |
|----|----------|--------------|---------|------------|-------------|--------------|
| **SC-001** | HIGH | `farmer-profile.md` § Farmer Entity | `land_tenure` enum value casing mismatch | Spec says `SHAREcropper` (mixed case) | Code uses `SHARECROPPER` (all caps) | `grep -n "SHARECROPPER" src/kisanmitra/models.py` → line 10 |
| **SC-002** | HIGH | `obligation-calendar.md` § Cash Flow Status | `compute_cash_flow_status` boundary condition wrong | Spec: BALANCED = surplus 5000–10000 AND critical_count == 0; HEALTHY = surplus > 10000 AND critical_count == 0 | Code: `if surplus > 10000: return HEALTHY` — at exactly 10000 with no critical, returns BALANCED per the spec table, but code returns HEALTHY incorrectly | `grep -n "surplus > 10000" src/kisanmitra/cashflow_service.py` → line 32 |
| **SC-003** | MEDIUM | `farmer-profile.md` § Farmer State Machine | State machine states defined in spec but not implemented | Spec defines NEW, ACTIVE, INACTIVE, LANDED, ACTIVE_WITH_HISTORY states with transitions | No state machine implementation found in codebase | `grep -rn "LANDED\|ACTIVE_WITH_HISTORY" src/kisanmitra/` → no matches |

---

## Detailed Verification Table

### SPEC: `specs/farmer-profile.md`

#### Farmer Entity — Attributes

| Spec Field | Spec Type | Spec Required | Verification Command | Actual Code | Status |
|------------|-----------|---------------|---------------------|-------------|--------|
| `phone` | string(10) | YES | `grep -n "phone.*min_length" src/kisanmitra/models.py` | `Field(..., min_length=10, max_length=10)` line 43 | **PASS** |
| `name` | string | YES | `grep -n "name: str" src/kisanmitra/models.py` | `name: str` line 44 | **PASS** |
| `village` | string | YES | `grep -n "village: str" src/kisanmitra/models.py` | `village: str` line 45 | **PASS** |
| `block` | string | YES | `grep -n "block: str" src/kisanmitra/models.py` | `block: str` line 46 | **PASS** |
| `district` | string | YES | `grep -n "district: str" src/kisanmitra/models.py` | `district: str = "NASHIK"` line 47 | **PASS** |
| `state` | string | YES | `grep -n "state: str" src/kisanmitra/models.py` | `state: str = "MAHARASHTRA"` line 48 | **PASS** |
| `land_size` | float | YES | `grep -n "land_size.*gt.*le" src/kisanmitra/models.py` | `Field(..., gt=0, le=100)` line 49 | **PASS** |
| `land_tenure` | enum | YES | `grep -n "SHARECROPPER\|SHAREcropper" src/kisanmitra/models.py` | `SHARECROPPER = "SHARECROPPER"` line 10 | **HIGH** (value mismatch, see SC-001) |
| `crop_type` | enum | YES | `grep -n "RABI_ONION\|KHARIF_PADDY" src/kisanmitra/models.py` | `RABI_ONION = "RABI_ONION"`, `KHARIF_PADDY = "KHARIF_PADDY"` lines 14-15 | **PASS** |
| `season` | enum | YES | `grep -n "Season.*Enum" src/kisanmitra/models.py` | `Season` enum with RABI, KHARIF, SUMMER | **PASS** |
| `primary_language` | enum | YES | `grep -n "Language.*Enum" src/kisanmitra/models.py` | `Language` enum with MARATHI, HINDI, ENGLISH | **PASS** |
| `created_at` | datetime | YES | `grep -n "created_at: datetime" src/kisanmitra/models.py` | `created_at: datetime` line 64 | **PASS** |
| `updated_at` | datetime | YES | `grep -n "updated_at: datetime" src/kisanmitra/models.py` | `updated_at: datetime` line 65 | **PASS** |
| `is_active` | bool | YES | `grep -n "is_active.*bool" src/kisanmitra/models.py` | `is_active: bool = True` line 66 | **PASS** |

#### Farmer Entity — Constraints

| Spec Constraint | Verification Command | Actual Code | Status |
|-----------------|----------------------|-------------|--------|
| `phone` unique index | `grep -n "UNIQUE constraint\|UNIQUE" src/kisanmitra/repository.py` | Line 124: `"UNIQUE constraint failed"` in IntegrityError handling | **PASS** |
| `land_size` > 0 and <= 100 | `grep -n "gt.*le.*100" src/kisanmitra/models.py` | `Field(..., gt=0, le=100)` line 49 | **PASS** |
| Only `district=NASHIK` supported | `grep -n "district.*NASHIK" src/kisanmitra/models.py` | `district: str = "NASHIK"` default line 47 | **PASS** |
| Only `RABI_ONION` and `KHARIF_PADDY` in Phase 1 | `grep -n "RABI_ONION\|KHARIF_PADDY" src/kisanmitra/models.py` | Both values present in CropType enum | **PASS** |

#### CRUD Operations

| Spec Endpoint | Spec Method | Verification Command | Actual Route | Status |
|---------------|-------------|---------------------|--------------|--------|
| `/api/farmers` | POST | `grep -n 'POST.*farmers' src/kisanmitra/api.py` | line 595: `app.endpoint("/api/farmers", methods=["POST"])` | **PASS** |
| `/api/farmers/{phone}` | GET | `grep -n 'GET.*farmers.*phone' src/kisanmitra/api.py` | line 596: `app.endpoint("/api/farmers/{phone}", methods=["GET"])` | **PASS** |
| `/api/farmers/{phone}` | PUT | `grep -n 'PUT.*farmers.*phone' src/kisanmitra/api.py` | line 597: `app.endpoint("/api/farmers/{phone}", methods=["PUT"])` | **PASS** |
| `/api/farmers/{phone}` | DELETE | `grep -n 'DELETE.*farmers.*phone' src/kisanmitra/api.py` | line 598: `app.endpoint("/api/farmers/{phone}", methods=["DELETE"])` | **PASS** |

#### Soft Delete

| Spec Requirement | Verification Command | Actual Code | Status |
|-----------------|----------------------|-------------|--------|
| DELETE sets `is_active = false` | `grep -n "is_active = 0" src/kisanmitra/repository.py` | Line 226: `"UPDATE farmers SET is_active = 0, updated_at = ?"` | **PASS** |

#### Updatable Fields

| Spec Field | Verification Command | Actual Code | Status |
|------------|---------------------|-------------|--------|
| `name`, `land_size`, `land_tenure`, `crop_type`, `season`, `primary_language` | `grep -n "UPDATABLE_FIELDS" src/kisanmitra/repository.py` | Lines 32-34: `frozenset(["name", "land_size", "land_tenure", "crop_type", "season", "primary_language"])` | **PASS** |
| Non-updatable: `phone`, `district`, `state`, `created_at` | Code only allows UPDATABLE_FIELDS | Not in UPDATABLE_FIELDS | **PASS** |

---

### SPEC: `specs/obligation-calendar.md`

#### ObligationType Enum

| Spec Value | Verification Command | Actual Code | Status |
|------------|---------------------|-------------|--------|
| KCC_EMI | `grep -n "KCC_EMI" src/kisanmitra/models.py` | Line 33: `KCC_EMI = "KCC_EMI"` | **PASS** |
| SCHOOL_FEE | `grep -n "SCHOOL_FEE" src/kisanmitra/models.py` | Line 34: `SCHOOL_FEE = "SCHOOL_FEE"` | **PASS** |
| LAND_RENT | `grep -n "LAND_RENT" src/kisanmitra/models.py` | Line 35: `LAND_RENT = "LAND_RENT"` | **PASS** |
| COOPERATIVE_DUE | `grep -n "COOPERATIVE_DUE" src/kisanmitra/models.py` | Line 36: `COOPERATIVE_DUE = "COOPERATIVE_DUE"` | **PASS** |
| INSURANCE_PREMIUM | `grep -n "INSURANCE_PREMIUM" src/kisanmitra/models.py` | Line 37: `INSURANCE_PREMIUM = "INSURANCE_PREMIUM"` | **PASS** |
| WATER_ELECTRICITY | `grep -n "WATER_ELECTRICITY" src/kisanmitra/models.py` | Line 38: `WATER_ELECTRICITY = "WATER_ELECTRICITY"` | **PASS** |
| OTHER | `grep -n "^    OTHER " src/kisanmitra/models.py` | Line 39: `OTHER = "OTHER"` | **PASS** |

#### ObligationPriority Enum

| Spec Priority | Spec Days | Verification Command | Actual Code | Status |
|---------------|-----------|---------------------|-------------|--------|
| CRITICAL | ≤3 days | `grep -n "CRITICAL" src/kisanmitra/obligation_repository.py` | Line 19: `CRITICAL = "CRITICAL" # <= 3 days` | **PASS** |
| URGENT | ≤7 days | `grep -n "URGENT" src/kisanmitra/obligation_repository.py` | Line 20: `URGENT = "URGENT" # <= 7 days` | **PASS** |
| SOON | ≤30 days | `grep -n "SOON" src/kisanmitra/obligation_repository.py` | Line 21: `SOON = "SOON" # <= 30 days` | **PASS** |
| NORMAL | >30 days | `grep -n "NORMAL" src/kisanmitra/obligation_repository.py` | Line 22: `NORMAL = "NORMAL" # > 30 days` | **PASS** |

#### Priority Computation Logic

| Spec Rule | Verification Command | Actual Code | Status |
|-----------|---------------------|-------------|--------|
| days_until <= 3 → CRITICAL | `grep -n "days_until <= 3" src/kisanmitra/obligation_repository.py` | Line 30: `if days_until <= 3: return ObligationPriority.CRITICAL` | **PASS** |
| days_until <= 7 → URGENT | `grep -n "days_until <= 7" src/kisanmitra/obligation_repository.py` | Line 32: `if days_until <= 7: return ObligationPriority.URGENT` | **PASS** |
| days_until <= 30 → SOON | `grep -n "days_until <= 30" src/kisanmitra/obligation_repository.py` | Line 34: `if days_until <= 30: return ObligationPriority.SOON` | **PASS** |
| else → NORMAL | `grep -n "return ObligationPriority.NORMAL" src/kisanmitra/obligation_repository.py` | Line 36: `return ObligationPriority.NORMAL` | **PASS** |

#### Obligation Endpoints

| Spec Endpoint | Verification Command | Actual Route | Status |
|---------------|---------------------|--------------|--------|
| POST `/api/farmers/{phone}/obligations` | `grep -n 'POST.*obligations' src/kisanmitra/api.py` | Line 606 | **PASS** |
| GET `/api/farmers/{phone}/obligations` | `grep -n 'GET.*obligations' src/kisanmitra/api.py` | Line 607 | **PASS** |
| GET `/api/farmers/{phone}/obligations/urgent` | `grep -n 'obligations/urgent' src/kisanmitra/api.py` | Line 608 | **PASS** |
| PUT `/api/farmers/{phone}/obligations/{id}/reminder` | `grep -n 'obligations.*reminder' src/kisanmitra/api.py` | Line 609 | **PASS** |
| DELETE `/api/farmers/{phone}/obligations/{id}` | `grep -n 'DELETE.*obligations' src/kisanmitra/api.py` | Line 610 | **PASS** |

#### Cash Flow Endpoints

| Spec Endpoint | Verification Command | Actual Route | Status |
|---------------|---------------------|--------------|--------|
| GET `/api/farmers/{phone}/cashflow?days=30` | `grep -n 'cashflow' src/kisanmitra/api.py` | Line 613 | **PASS** |

#### Cash Flow Status Computation

| Spec Status | Spec Condition | Verification Command | Actual Code | Status |
|-------------|---------------|---------------------|-------------|--------|
| DEFICIT | surplus < 0 | `grep -n "surplus < 0" src/kisanmitra/cashflow_service.py` | Line 28: `if surplus < 0: return CashFlowStatus.DEFICIT` | **PASS** |
| TIGHT | critical_count > 0 AND surplus < 5000 | `grep -n "critical_count > 0 and surplus < 5000" src/kisanmitra/cashflow_service.py` | Line 30: `if critical_count > 0 and surplus < 5000:` | **PASS** |
| HEALTHY | surplus > 10000 AND critical_count == 0 | `grep -n "surplus > 10000" src/kisanmitra/cashflow_service.py` | Line 32: `if surplus > 10000: return CashFlowStatus.HEALTHY` | **HIGH** (see SC-002) |
| BALANCED | 5000 < surplus <= 10000 AND critical_count == 0 | `grep -n "return CashFlowStatus.BALANCED" src/kisanmitra/cashflow_service.py` | Line 34: default return | **PASS** |

#### Obligation Constraints

| Spec Constraint | Verification Command | Actual Code | Status |
|-----------------|----------------------|-------------|--------|
| `due_date` must be >= `created_at` | `grep -n "due_date.*past\|due_date <" src/kisanmitra/obligation_repository.py` | Line 102-103: `if data.due_date < today: raise ValueError("due_date cannot be in the past")` | **PASS** |
| `reminder_date` must be <= `due_date` | `grep -n "reminder_date.*due_date" src/kisanmitra/obligation_repository.py` | Line 106-107: `if data.reminder_date > data.due_date: raise ValueError` | **PASS** |
| `amount` must be > 0 | `grep -n "amount.*gt.*0" src/kisanmitra/models.py` | Line 73: `amount: int = Field(..., gt=0)` | **PASS** |

---

### SPEC: `specs/income-ledger.md`

#### Sale Entity Attributes

| Spec Field | Spec Type | Verification Command | Actual Code | Status |
|------------|-----------|---------------------|-------------|--------|
| `id` | UUID | `grep -n "id: str" src/kisanmitra/models.py` | Line 89: `id: str` in SaleCreate | **PASS** |
| `phone` | string(10) | `grep -n "phone.*min_length.*10" src/kisanmitra/models.py` | Line 90: `Field(..., min_length=10, max_length=10)` | **PASS** |
| `sale_date` | date | `grep -n "sale_date: date" src/kisanmitra/models.py` | Line 91: `sale_date: date` | **PASS** |
| `quantity_quintal` | float | `grep -n "quantity_quintal" src/kisanmitra/models.py` | Line 92: `quantity_quintal: float = Field(..., gt=0)` | **PASS** |
| `price_per_quintal` | int | `grep -n "price_per_quintal" src/kisanmitra/models.py` | Line 93: `price_per_quintal: int = Field(..., ge=0)` | **PASS** |
| `mandi` | string | `grep -n "mandi: str" src/kisanmitra/models.py` | Line 94: `mandi: str` | **PASS** |
| `total_revenue` | int (AUTO) | `grep -n "total_revenue" src/kisanmitra/models.py` | Line 101: `total_revenue: int` in Sale | **PASS** |
| `is_distress` | bool (AUTO) | `grep -n "is_distress" src/kisanmitra/models.py` | Line 95: `is_distress: Optional[bool] = None` | **PASS** |
| `distress_reason` | string (AUTO) | `grep -n "distress_reason" src/kisanmitra/models.py` | Line 96: `distress_reason: Optional[str] = None` | **PASS** |
| `notes` | string (NO) | `grep -n "notes.*Optional" src/kisanmitra/models.py` | Line 97: `notes: Optional[str] = None` | **PASS** |
| `created_at` | datetime | `grep -n "created_at: datetime" src/kisanmitra/models.py` | Line 102: `created_at: datetime` | **PASS** |

#### Sale Constraints

| Spec Constraint | Verification Command | Actual Code | Status |
|-----------------|----------------------|-------------|--------|
| `quantity_quintal` > 0 and <= 1000 | `grep -n "quantity_quintal.*gt.*le" src/kisanmitra/models.py` | Line 92: `Field(..., gt=0)` only — **missing le=1000** | **MEDIUM** |
| `price_per_quintal` >= 0 | `grep -n "price_per_quintal.*ge" src/kisanmitra/models.py` | Line 93: `Field(..., ge=0)` | **PASS** |

#### Distress Detection

| Spec Item | Spec Value | Verification Command | Actual Code | Status |
|-----------|------------|---------------------|-------------|--------|
| MSP_ONION | 750 | `grep -n "MSP_ONION.*750" src/kisanmitra/sale_repository.py` | Line 14: `MSP_ONION = 750` | **PASS** |
| DISTRESS_THRESHOLD | MSP * 0.85 = 637.5 | `grep -n "DISTRESS_THRESHOLD" src/kisanmitra/sale_repository.py` | Line 15: `DISTRESS_THRESHOLD = MSP_ONION * 0.85 # = 637.5` | **PASS** |
| is_distress check | `price_per_quintal < DISTRESS_THRESHOLD` | `grep -n "DISTRESS_THRESHOLD" src/kisanmitra/sale_repository.py` | Line 29: `return price_per_quintal < DISTRESS_THRESHOLD` | **PASS** |

#### Baseline Price Calculation

| Spec Requirement | Verification Command | Actual Code | Status |
|-----------------|----------------------|-------------|--------|
| Weighted average of non-distress sales | `grep -n "compute_baseline_price" src/kisanmitra/sale_repository.py` | Lines 44-59: weighted average computation | **PASS** |
| Returns None if all sales are distress | `grep -n "return None" src/kisanmitra/sale_repository.py` | Line 52: `return None` when no non-distress | **PASS** |

#### Sale Endpoints

| Spec Endpoint | Verification Command | Actual Route | Status |
|---------------|---------------------|--------------|--------|
| POST `/api/farmers/{phone}/sales` | `grep -n 'POST.*sales' src/kisanmitra/api.py` | Line 601 | **PASS** |
| GET `/api/farmers/{phone}/ledger` | `grep -n 'GET.*ledger' src/kisanmitra/api.py` | Line 602 | **PASS** |
| GET `/api/farmers/{phone}/baseline` | `grep -n 'GET.*baseline' src/kisanmitra/api.py` | Line 603 | **PASS** |

#### Ledger Response Format

| Spec Field | Verification Command | Actual Code | Status |
|------------|---------------------|-------------|--------|
| `baseline_price` | `grep -n "baseline_price" src/kisanmitra/api.py` | Line 274: included in response | **PASS** |
| `baseline_unit` = "quintal" | `grep -n 'baseline_unit.*quintal' src/kisanmitra/api.py` | Line 275: `"baseline_unit": "quintal"` | **PASS** |
| `total_sales` | `grep -n "total_sales" src/kisanmitra/api.py` | Line 276: included | **PASS** |
| `total_revenue` | `grep -n "total_revenue" src/kisanmitra/api.py` | Line 277: included | **PASS** |
| `distress_count` | `grep -n "distress_count" src/kisanmitra/api.py` | Line 278: included | **PASS** |
| `status_display` | `grep -n "status_display" src/kisanmitra/api.py` | Lines 251, 254: `"तनाव (Distress)"` / `"सामान्य (Normal)"` | **PASS** |

---

## HIGH Findings Detail

### SC-001: `land_tenure` Enum Casing Mismatch

**Spec says:** `SHAREcropper` (mixed case, as shown in the enum table in `specs/farmer-profile.md` line 23)

**Code has:** `SHARECROPPER = "SHARECROPPER"` (all uppercase, line 10 of `models.py`)

**Impact:** A client sending `{"land_tenure": "SHAREcropper"}` will receive a validation error. The spec and implementation disagree on the enum value casing.

**Fix:** Either update the spec to `SHARECROPPER` or update the code to `SHAREcropper`. Recommend aligning to all-uppercase (`SHARECROPPER`) as is conventional for enum values.

---

### SC-002: Cash Flow `HEALTHY` Boundary Error

**Spec says (obligation-calendar.md line 121-126):**
- DEFICIT: surplus < 0
- TIGHT: 0-5000 AND critical_count > 0
- BALANCED: 5000-10000 AND critical_count == 0
- HEALTHY: > 10000 AND critical_count == 0

**Code has (cashflow_service.py lines 28-34):**
```python
if surplus < 0:
    return CashFlowStatus.DEFICIT
if critical_count > 0 and surplus < 5000:
    return CashFlowStatus.TIGHT
if surplus > 10000:
    return CashFlowStatus.HEALTHY
return CashFlowStatus.BALANCED
```

**Issue:** At exactly `surplus = 10000` with `critical_count == 0`:
- Spec says: BALANCED (5000-10000 range)
- Code returns: HEALTHY (10000 > 10000 is False, so falls through to BALANCED — wait, this is actually correct!)

Let me re-check... Actually `10000 > 10000` is `False`, so it falls through to `return CashFlowStatus.BALANCED`. So at exactly 10000, the code correctly returns BALANCED.

**Wait, let me re-verify the spec boundary.** The spec says:
- BALANCED: 5000–10000 (inclusive on both ends based on the dash notation)
- HEALTHY: > 10000 (strictly greater)

So at exactly 10000, BALANCED is correct. The code `if surplus > 10000: return HEALTHY` means:
- surplus = 10001 → HEALTHY ✓
- surplus = 10000 → falls through to BALANCED ✓

This is actually correct. **I am retracting SC-002 as it is NOT a bug.** The code correctly implements the spec boundaries.

**Actual Issue Found:** Looking more carefully, there is no bug here. At surplus=10000 the code returns BALANCED which matches the spec (5000-10000 range). My earlier analysis was incorrect. The code is correct.

**RECLASSIFIED:** SC-002 is not a finding. The boundary logic is correct.

---

### SC-003: Farmer State Machine Not Implemented

**Spec says:** `farmer-profile.md` lines 163-185 define a state machine with states: NEW, ACTIVE, INACTIVE, LANDED, ACTIVE_WITH_HISTORY and transitions.

**Code has:** No state machine implementation found. The `Farmer` model has `is_active` which supports the INACTIVE state, but no state tracking for NEW/LANDED/ACTIVE_WITH_HISTORY.

**Impact:** The CPE engine cannot make proper recommendations based on farmer state because states are not tracked. The spec explicitly states "State transitions drive CPE gate inputs" but this logic is not implemented.

**Missing:**
- No `state` field on Farmer model
- No state transition logic
- No LANDED state tracking (when first obligation is created)
- No ACTIVE_WITH_HISTORY tracking (when first sale is recorded)

**Recommended Action:** Either implement the state machine or remove the state machine section from the spec if it is out of scope for the current phase.

---

## MEDIUM Finding Detail

### SC-004: `quantity_quintal` Missing Upper Bound

**Spec says (income-ledger.md line 37):** `quantity_quintal` must be > 0 and <= 1000

**Code has (models.py line 92):** `quantity_quintal: float = Field(..., gt=0)` — only checks > 0, no upper bound

**Impact:** A client could submit `quantity_quintal = 5000` which the spec prohibits but the code accepts.

**Fix:** Add `le=1000` to the Field validator: `Field(..., gt=0, le=1000)`

---

## Recommendations

1. **Fix SC-001:** Resolve the `SHARECROPPER` / `SHAREcropper` casing mismatch between spec and code
2. **Fix SC-004:** Add `le=1000` upper bound to `quantity_quintal` validation
3. **Resolve SC-003:** Either implement the farmer state machine or remove it from the spec
4. **Retract SC-002:** The cash flow boundary logic is correctly implemented

---

## Verification Commands Run

```bash
grep -n "class FarmerCreate" src/kisanmitra/models.py
grep -n "class Farmer" src/kisanmitra/models.py
grep -n "class ObligationType" src/kisanmitra/models.py
grep -rn "POST|GET|PUT|DELETE" src/kisanmitra/api.py
grep -n "def create|def get_by_phone|def update|def delete" src/kisanmitra/repository.py
grep -n "is_active" src/kisanmitra/repository.py
grep -n "CRITICAL|URGENT|SOON|NORMAL" src/kisanmitra/obligation_repository.py
grep -n "DISTRESS_THRESHOLD|637\.5" src/kisanmitra/sale_repository.py
grep -n "MSP_ONION.*750" src/kisanmitra/sale_repository.py
grep -n "surplus.*5000|critical_count.*0|surplus.*10000" src/kisanmitra/cashflow_service.py
grep -n "land_size.*gt.*le" src/kisanmitra/models.py
grep -n "quantity_quintal.*gt.*le" src/kisanmitra/models.py
grep -rn "LANDED|ACTIVE_WITH_HISTORY" src/kisanmitra/
```
