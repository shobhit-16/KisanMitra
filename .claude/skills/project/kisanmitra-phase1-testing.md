---
name: kisanmitra-phase1-testing
description: Kisanmitra Phase 1 testing patterns and integration test setup
priority: 20
scope: skill-embedded
---

# Kisanmitra Phase 1 — Testing Patterns

## Test Setup

All Kisanmitra integration tests use a real SQLite database. The DB is initialized from `schema.sql` for each test module.

```python
# tests/integration/test_api.py
import pytest
from starlette.testclient import TestClient
from kisanmitra.api import create_app
from indian_agri.db import get_aiosqlite_pool
import tempfile, os

@pytest.fixture
def client():
    # Create temp DB from schema
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    pool = get_aiosqlite_pool(f"file:{db_path}?mode=memory&cache=shared")
    # Run schema
    import sqlite3
    with sqlite3.connect(db_path) as conn:
        conn.executescript(open("src/indian_agri/schema.sql").read())
    os.environ["KISANMITRA_DB"] = db_path
    app = create_app()
    with TestClient(app) as c:
        yield c
    os.unlink(db_path)
```

**Critical:** `create_app()` must be called inside the fixture's `with` block, after `KISANMITRA_DB` is set. The pool is initialized at import time.

## Pattern 1: Disable Deduplication Middleware in Tests

Nexus ships with `RequestDeduplicator` middleware for production duplicate-request handling. In integration tests, this caches the second identical POST and returns 200.

```python
# WRONG for tests — deduplication interferes with duplicate-detection tests
app = Nexus(enable_http_transport=True)

# CORRECT for tests
app = Nexus(enable_http_transport=True, enable_durability=False)
```

**Why:** The fingerprint excludes headers, so `Idempotency-Key` does not bypass it. Query params ARE included, so adding a fake param also does not work. `enable_durability=False` is the only clean solution for test apps.

## Pattern 2: `str, enum.Enum` — Use `.value`, Not `str()`

Kisanmitra's priority enums (`ObligationPriority`, `CashFlowStatus`) inherit from both `str` and `enum.Enum`.

```python
# WRONG — str() returns repr
"priority": str(priority),         # 'ObligationPriority.SOON'

# CORRECT — .value returns the actual string
"priority": priority.value,         # 'SOON'
```

Quick verification:
```python
>>> from kisanmitra.models import ObligationPriority
>>> str(ObligationPriority.SOON)
'ObligationPriority.SOON'   # repr — wrong
>>> ObligationPriority.SOON.value
'SOON'                       # value — correct
```

## Pattern 3: aiosqlite Connection — Plain Path, Not SQLAlchemy URL

`aiosqlite` takes a plain file path or `file:` URI. It does NOT accept SQLAlchemy-style URLs.

```python
# WRONG
pool = get_aiosqlite_pool("sqlite+aiosqlite:///path/to/db.db")

# CORRECT
pool = get_aiosqlite_pool("file:path/to/db.db?mode=memory&cache=shared")
# or for file-based:
pool = get_aiosqlite_pool("file:/absolute/path/to/db.db")
```

## Pattern 4: API Response Field Assertions

For enum fields in API responses, assert against `.value`:

```python
def test_cashflow_status_healthy():
    response = client.get("/api/farmers/9876543210/cashflow?days=30")
    assert response.status_code == 200
    data = response.json()
    assert data["cashflow_status"] == "HEALTHY"      # string, not enum
    assert data["priority"] == "SOON"                   # .value, not str(enum)
```

## Integration Test Checklist

- [ ] Test app uses `enable_durability=False`
- [ ] `KISANMITRA_DB` env var set before `create_app()` call
- [ ] `aiosqlite` pool uses `file:` URI format
- [ ] Enum fields serialized as `.value`, not `str(enum)`
- [ ] Duplicate-detection tests verify 409 response, not 200 from cache
- [ ] All 220 tests pass (`pytest tests/ -x -q`)
