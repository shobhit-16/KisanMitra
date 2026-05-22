---
name: kisanmitra-dedup-test-pattern
description: Kisanmitra duplicate-detection integration test pattern
trigger_phrases:
  - "duplicate farmer test"
  - "test_create_farmer_duplicate"
  - "Nexus deduplication"
  - "enable_durability"
---

# Kisanmitra: Duplicate-Detection Test Pattern

## The Problem

When testing POST `/api/farmers` duplicate detection (`test_create_farmer_duplicate`), a second identical POST returned HTTP 200 instead of 409. The cause: Nexus's built-in **deduplication middleware** (`RequestDeduplicator`) caches the request by fingerprint and returns the cached response.

The fingerprint is computed as: `method + path + query_params + body` — **headers are NOT included**. This means `Idempotency-Key` header approaches do not work.

## Root Cause

`kailash.middleware.gateway.deduplicator.RequestDeduplicator` caches POST requests keyed on the request fingerprint. For duplicate-detection tests, the second identical POST is served from cache as 200.

Evidence:
```
kailash.middleware.gateway.deduplicator: Duplicate request detected: POST /api/farmers
```

## The Fix

Pass `enable_durability=False` to the `Nexus()` constructor in test app setup:

```python
# src/kisanmitra/api.py — production
app = Nexus(enable_http_transport=True)

# tests/integration/test_api.py — test app
app = Nexus(enable_http_transport=True, enable_durability=False)
```

This disables the deduplication middleware entirely for test apps. The deduplication middleware is a production feature for exactly-once delivery guarantees — not needed in integration tests.

## Verification

```bash
# The second POST should return 409, not 200
response1 = client.post("/api/farmers", json={...})   # 201
response2 = client.post("/api/farmers", json={...})   # 409 (not 200 from cache)
assert response2.status_code == 409
```

## Origin

2026-05-22 — `test_create_farmer_duplicate` was failing. Investigation showed `create_farmer.start` appearing only once in logs for two POST attempts, confirming the deduplicator cached the second request.

## DO NOT

- Use `Idempotency-Key` header as a bypass — headers are excluded from fingerprint
- Use query params to differentiate duplicate requests — query_params ARE included in fingerprint
- Disable `enable_durability` in production code — the deduplication middleware is correct for production use
