# Test Coverage Audit — Round 1

## Summary

- **Total tests collected:** 205
- **Audit date:** 2026-05-22

---

## Module Coverage

| Module | Test File(s) | Import Found | Test Count | Status |
|--------|--------------|--------------|------------|--------|
| `src/kisanmitra/models.py` | `test_obligation_repository.py`, `test_farmer_repository.py`, `test_cashflow_service.py`, `test_sale_repository.py` | YES | — | PASS |
| `src/kisanmitra/repository.py` (FarmerRepository) | `test_farmer_repository.py`, `test_sale_repository.py` | YES | — | PASS |
| `src/kisanmitra/api.py` | — | **NO** | — | **HIGH — No test coverage** |
| `src/kisanmitra/obligation_repository.py` | `test_obligation_repository.py`, `test_cashflow_service.py` | YES | — | PASS |
| `src/kisanmitra/cashflow_service.py` | `test_cashflow_service.py` | YES | — | PASS |
| `src/kisanmitra/sale_repository.py` | `test_sale_repository.py` | YES | — | PASS |

---

## Test Count Per Module

| Test File | Target Module | Tests Collected |
|-----------|---------------|-----------------|
| `tests/unit/test_farmer_repository.py` | `repository.py` (FarmerRepository) | 25 |
| `tests/unit/test_obligation_repository.py` | `obligation_repository.py` | 27 |
| `tests/unit/test_cashflow_service.py` | `cashflow_service.py` | 19 |
| `tests/unit/test_sale_repository.py` | `sale_repository.py` | 22 |

**Total: 93 tests across the 4 core repository/service files**

---

## Findings

### HIGH: `api.py` has zero test coverage

`src/kisanmitra/api.py` is not imported by any test file. This is a significant gap — the API layer has no automated tests verifying endpoint behavior.

**Action required:** Add tests for API endpoints in `tests/unit/test_api.py` or similar.

---

## Current Test Failures

Running `pytest tests/unit/test_cashflow_service.py::TestCashFlowCompute -v`:

| Test | Result | Error |
|------|--------|-------|
| `test_empty_obligations` | PASS | — |
| `test_single_obligation_in_window` | PASS | — |
| `test_obligation_outside_window_not_counted` | PASS | — |
| `test_multiple_obligations_by_type` | **FAIL** | `AssertionError: assert 'LAND_RENT' in {'KCC_EMI': ..., 'SCHOOL_FEE': ...}` |
| `test_income_included` | PASS | — |
| `test_critical_count_for_tight_status` | PASS | — |
| `test_window_days_max_90` | PASS | — |
| `test_window_days_clamped_to_1` | **FAIL** | `assert 0 == 1` |
| `test_healthy_status` | PASS | — |
| `test_by_type_has_priority_and_due_in_days` | PASS | — |

**2 failed, 8 passed in `TestCashFlowCompute`**

### Root Cause Analysis

**`test_multiple_obligations_by_type` failure:** The `by_type` dict is missing `LAND_RENT`. Looking at `cashflow_service.py` line 103:

```python
priority = compute_priority(ob.due_date, today)
```

`compute_priority` is **never defined or imported** in `cashflow_service.py`. This is a real bug — the function does not exist in scope.

**`test_window_days_clamped_to_1` failure:** `result["window_days"]` returns `0` instead of `1`. This may be a separate bug in the window clamping logic or in how the test sets up the obligation dates.

---

## Recommendations

1. **Fix `cashflow_service.py`:** The `compute_priority` call on line 103 references an undefined function. It should likely be `ObligationPriority.compute_priority` or similar, imported from `obligation_repository`.
2. **Add API tests:** `src/kisanmitra/api.py` needs test coverage.
3. **Fix `test_window_days_clamped_to_1`:** Investigate why `window_days` returns `0` when it should be clamped to `1`.

---

## Audit Verification

- Collected tests via: `.venv/bin/python -m pytest --collect-only -q tests/`
- Import verification via: `grep -r "kisanmitra" tests/`
- Test execution: `.venv/bin/python -m pytest tests/unit/test_cashflow_service.py::TestCashFlowCompute -v --tb=short`
