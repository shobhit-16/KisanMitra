# DISCOVERY: Two Phase-1 Integration Test Patterns

**Date:** 2026-05-22
**Session:** Kisanmitra Phase 1 implementation

## Pattern 1: Nexus Deduplication Middleware Interferes with Duplicate-Detection Tests

**Context:** `test_create_farmer_duplicate` returned 200 for the second POST instead of 409.

**Finding:** `Nexus(enable_http_transport=True)` installs `RequestDeduplicator` middleware which caches POST requests by fingerprint (method + path + query_params + body — headers excluded). The second identical POST returned the cached 200 response.

**Fix:** Pass `enable_durability=False` to the `Nexus()` constructor in test app setup:
```python
app = Nexus(enable_http_transport=True, enable_durability=False)
```

**Why this matters:** The fingerprint excludes headers, so `Idempotency-Key` header approaches don't work. `enable_durability=False` is the only clean bypass for integration tests.

**Codified as:**
- `agents/project/kisanmitra-dedup-test-pattern.md`
- `skills/project/kisanmitra-phase1-testing.md`

---

## Pattern 2: `str(priority)` vs `priority.value` on `str, enum.Enum` Mixins

**Context:** `test_by_type_has_priority_and_due_in_days` failed with `'ObligationPriority.SOON' not in ('CRITICAL', 'URGENT', 'SOON', 'NORMAL')`.

**Finding:** Kisanmitra's priority enums (`ObligationPriority`, `CashFlowStatus`) inherit from both `str` and `enum.Enum`. `str(priority)` returns the repr (`'ObligationPriority.SOON'`), not the value (`'SOON'`).

**Fix:** Always use `.value` for serialization:
```python
"priority": priority.value   # CORRECT
"priority": str(priority)   # WRONG — returns repr
```

**Codified as:**
- `agents/project/kisanmitra-enum-serialization.md`
- `skills/project/kisanmitra-phase1-testing.md`
