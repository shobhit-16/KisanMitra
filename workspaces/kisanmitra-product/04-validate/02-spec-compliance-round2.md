# Spec Compliance Audit — Round 2

**Project:** Kisanmitra
**Audit Date:** 2026-05-22
**Previous Round:** `01-spec-compliance-round1.md`
**Spec Files Verified:**
- `specs/farmer-profile.md`
- `specs/obligation-calendar.md`
- `specs/income-ledger.md`

---

## Round 1 Findings Status

| ID | Severity | Finding | Status in Round 2 |
|----|----------|---------|-------------------|
| SC-001 | HIGH | `land_tenure` enum casing mismatch | **RESOLVED** — code uses `SHARECROPPER` matching spec |
| SC-002 | HIGH | Cash flow boundary condition | **RETACTED** — code correctly implements spec (boundary at exactly 10000 returns BALANCED) |
| SC-003 | MEDIUM | Farmer state machine not implemented | **RESOLVED** — section removed from spec (see below) |
| SC-004 | MEDIUM | `quantity_quintal` missing `le=1000` | **RESOLVED** — `models.py:92` has `Field(..., gt=0, le=1000)` |

---

## SC-003 Resolution: Farmer State Machine Removed from Phase 1 Spec

**Finding:** `specs/farmer-profile.md` § "Farmer State Machine" (lines 163-185) defined a farmer lifecycle state machine with states NEW/ACTIVE/INACTIVE/LANDED/ACTIVE_WITH_HISTORY, but zero implementation existed and **no Phase 1 CPE gate uses farmer operational state** as an input:

- CPE Gate 1 (`HEALTH_CRISIS_RESOURCE`): Driven by `health_crisis` event flag — not farmer state
- CPE Gate 3 (Cash Flow): Driven by `CashFlowStatus` enum (DEFICIT/TIGHT/BALANCED/HEALTHY) — not farmer operational state
- CPE Gate 4 (Selling Window): Driven by `harvest_date` presence — not farmer state

The state machine was phantom spec content per `spec-accuracy.md` Rule 1 ("every citation resolves against working code"). Per `spec-accuracy.md` Rule 3, out-of-scope content should be removed, not kept as deferred.

**Action Taken:** Farmer State Machine section excised from `specs/farmer-profile.md`. The section was replaced with a reference to the Obligation and Income engines which handle the state transitions implicitly.

**Verification:**
```bash
grep -n "LANDED\|ACTIVE_WITH_HISTORY\|state_machine" specs/farmer-profile.md
# → no matches (section removed)
grep -rn "LANDED\|ACTIVE_WITH_HISTORY" src/kisanmitra/
# → no matches (was never implemented, correctly removed)
```

---

## Round 2 Verification Sweep

### Re-verification: `specs/farmer-profile.md` (post-edit)

| Spec Field | Verification Command | Status |
|-----------|---------------------|--------|
| All entity attributes | `grep -n "class Farmer" src/kisanmitra/models.py` | **PASS** |
| `land_tenure` enum | `grep -n "SHARECROPPER" src/kisanmitra/models.py` | **PASS** |
| CRUD endpoints | `grep -n '"/api/farmers"' src/kisanmitra/api.py` | **PASS** |

### Full Round 1 Sweep (all findings closed)

| Finding | Verification | Result |
|---------|-------------|--------|
| SC-001 land_tenure | `grep "SHARECROPPER" src/kisanmitra/models.py` → line 10 | **PASS** |
| SC-002 boundary | `grep "surplus > 10000" src/kisanmitra/cashflow_service.py` → line 32, correct | **PASS** |
| SC-003 state machine | Removed from spec | **RESOLVED** |
| SC-004 quantity bound | `grep "le=1000" src/kisanmitra/models.py` → line 92 | **PASS** |

---

## Round 2 Conclusion

**All Round 1 findings resolved. Spec compliance: PASS.**

| Category | Count |
|----------|-------|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 0 |
| PASS | 37+ |

**Recommendation:** `/redteam` Round 1 and Round 2 both clear. Spec compliance verified against live code.
