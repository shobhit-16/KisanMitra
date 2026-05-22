# Kisanmitra Security Audit - Round 1

**Project:** Kisanmitra
**Audit Date:** 2026-05-22
**Reviewer:** security-reviewer
**Modules Reviewed:** src/kisanmitra/models.py, repository.py, api.py, obligation_repository.py, cashflow_service.py, sale_repository.py

---

## Findings Summary

| Category | Severity | Result |
|----------|----------|--------|
| Hardcoded Secrets | PASS | PASS |
| SQL Injection | PASS | PASS |
| JWT Secret Configuration | **HIGH** | **FAIL** |
| Phone Validation | PASS | PASS |
| Enum Validation | PASS | PASS |
| eval()/exec() Usage | PASS | PASS |
| .env in Git | PASS | PASS |
| Foreign Key Constraint Handling | PASS | PASS |

---

## Detailed Findings

### 1. Hardcoded Secrets

**Status:** PASS

**Evidence:**
- No hardcoded API keys (`sk-`), passwords, or `api_key =` patterns found in source code
- `.env` file contains placeholder values (`change-me-in-production`) which are templates only
- `.env` is properly listed in `.gitignore`

**File:** `.gitignore:1` | Severity: PASS

---

### 2. SQL Injection Prevention

**Status:** PASS

**Evidence:** All database queries use parameterized statements with `?` placeholders:

```python
# repository.py:150-152 - parameterized query
cursor = await conn.execute(
    "SELECT * FROM farmers WHERE phone = ? AND is_active = 1",
    (phone,),
)

# obligation_repository.py:185-187 - parameterized query
cursor = await conn.execute(
    "SELECT * FROM obligations WHERE phone = ? AND is_paid = 0 ORDER BY due_date ASC",
    (phone,),
)

# sale_repository.py:182-184 - parameterized query
cursor = await conn.execute(
    "SELECT * FROM sales WHERE phone = ? ORDER BY sale_date ASC",
    (phone,),
)
```

No f-string concatenation or string interpolation in SQL queries detected.

**Files:** repository.py, obligation_repository.py, sale_repository.py | Severity: PASS

---

### 3. JWT Secret Configuration

**Status:** **FAIL** | Severity: **HIGH**

**Finding:** `JWT_SECRET` is configured in `.env` but is never read or used in any source file.

**Evidence:**
- `.env:5` contains `JWT_SECRET=change-me-in-production`
- `api.py:41` only reads `KISANMITRA_DB`: `DB_PATH = os.environ.get("KISANMITRA_DB", ":memory:")`
- No `jwt`, `JWT`, `SECRET`, or `authorize` imports in api.py
- No authentication middleware present in the API

**Risk:** Security theater - the `.env` implies authentication is configured but no authentication mechanism is implemented. Any party with network access can create/modify/delete farmer records, obligations, and sales data.

**Files:** api.py:41, .env:5 | Severity: HIGH

**Recommendation:** Either implement JWT authentication per the configured secret, or remove `JWT_SECRET` from `.env` to avoid misleading configuration.

---

### 4. Phone Validation

**Status:** PASS

**Evidence:** 10-digit phone validation is enforced at multiple layers:

**API/Model Layer (models.py:43, 55-60):**
```python
phone: str = Field(..., min_length=10, max_length=10)

@field_validator("phone")
@classmethod
def phone_must_be_digits(cls, v: str) -> str:
    if not v.isdigit():
        raise ValueError("Phone number must contain only digits")
    return v
```

**Repository Layer (repository.py:57-61):**
```python
def _validate_phone(self, phone: str) -> str:
    if not (isinstance(phone, str) and phone.isdigit() and len(phone) == 10):
        raise PhoneFormatError("phone must be exactly 10 decimal digits")
    return phone
```

**Files:** models.py:43, models.py:55-60, repository.py:57-61 | Severity: PASS

---

### 5. Enum Validation

**Status:** PASS

**Evidence:** All enums inherit from `str` and are validated by Pydantic:

```python
# models.py:7-10
class LandTenure(str, Enum):
    OWNER = "OWNER"
    TENANT = "TENANT"
    SHARECROPPER = "SHARECROPPER"
```

Pydantic's enum validation automatically rejects invalid values. Invalid enum input returns a clear error:
```
Input should be 'OWNER', 'TENANT' or 'SHARECROPPER'
```

**Files:** models.py:7-39 | Severity: PASS

---

### 6. eval()/exec() Usage

**Status:** PASS

**Evidence:** No `eval()` or `exec()` patterns found in any source file.

**Command:** `grep -rn "eval\|exec" src/kisanmitra/` | Severity: PASS

---

### 7. .env in Git

**Status:** PASS

**Evidence:** `.env` is properly ignored in `.gitignore:1`

```
.env
```

**File:** .gitignore:1 | Severity: PASS

---

### 8. Foreign Key Constraint Handling

**Status:** PASS

**Evidence:** Foreign key constraints are properly handled:

**Schema (schema.sql:25, 42):**
```sql
phone TEXT NOT NULL REFERENCES farmers(phone)  -- obligations table
phone TEXT NOT NULL REFERENCES farmers(phone)  -- sales table
```

**All Repositories Enable FK (repository.py:47, obligation_repository.py:60, sale_repository.py:80):**
```python
await conn.execute("PRAGMA foreign_keys=ON")
```

**API Validates Farmer Exists Before Related Records (api.py:174-180):**
```python
try:
    await self._farmer_repo.get_by_phone(phone)
except FarmerNotFoundError:
    logger.warning("create_sale.farmer_not_found", phone=phone)
    return JSONResponse(
        {"error": f"Farmer with phone {phone} not found"}, status_code=404
    )
```

**Test Fixture Creates Parent Record First (test_cashflow_service.py:36-50):**
```python
# Create a test farmer (required for FK constraint on obligations)
await conn.execute(
    """INSERT INTO farmers (phone, name, village, block, district, state,
        land_size, land_tenure, crop_type, season, primary_language, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
    ("9876543210", "Test Farmer", "Test Village", "Test Block",
     "NASHIK", "MAHARASHTRA", 2.0, "OWNER", "RABI_ONION", "RABI", "MARATHI"),
)
```

**Files:** schema.sql, repository.py, obligation_repository.py, sale_repository.py, api.py, test_cashflow_service.py | Severity: PASS

---

## Recommendations

1. **JWT Authentication (HIGH):** Implement JWT middleware or remove `JWT_SECRET` from `.env` to avoid misleading security configuration.

2. **No Other Action Required:** All other security controls are properly implemented.
