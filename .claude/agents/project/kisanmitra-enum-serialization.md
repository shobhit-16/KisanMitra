---
name: kisanmitra-enum-serialization
description: Kisanmitra str,enum.Enum mixin serialization pattern
trigger_phrases:
  - "ObligationPriority"
  - "str(priority)"
  - "enum value serialization"
  - ".value vs str(enum)"
---

# Kisanmitra: `str, enum.Enum` Mixin Serialization

## The Problem

`test_by_type_has_priority_and_due_in_days` failed with:
```
AssertionError: 'ObligationPriority.SOON' not found in ('CRITICAL', 'URGENT', 'SOON', 'NORMAL')
```

The test asserted against `'SOON'` but the code returned `'ObligationPriority.SOON'`.

## Root Cause

When a Python enum inherits from both `str` and `enum.Enum`, the two types have different repr/value semantics:

```python
class ObligationPriority(str, enum.Enum):
    SOON = "SOON"
    URGENT = "URGENT"

# str(ObligationPriority.SOON)  → 'ObligationPriority.SOON'  (the repr, WRONG)
# ObligationPriority.SOON.value  → 'SOON'                     (the actual value, CORRECT)
```

`str(priority)` calls `__str__` which returns the enum's repr form `'ObligationPriority.SOON'`. The actual string value lives in `.value`.

## The Fix

Always use `.value` when you need the string value of a `str, enum.Enum` member:

```python
# WRONG
"priority": str(priority),         # → 'ObligationPriority.SOON'

# CORRECT
"priority": priority.value,         # → 'SOON'
```

## Verification

```python
# Quick check in a REPL:
>>> from src.kisanmitra.models import ObligationPriority
>>> str(ObligationPriority.SOON)
'ObligationPriority.SOON'   # repr — wrong for serialization
>>> ObligationPriority.SOON.value
'SOON'                       # actual value — correct
```

## When This Matters

Any time a `str, enum.Enum` member is:
- Serialized to JSON (API responses)
- Used as a dict key or database value
- Compared to a string literal

## Origin

2026-05-22 — `cashflow_service.py:107` used `str(priority)` in a response dict. The test `test_by_type_has_priority_and_due_in_days` asserted `'SOON'` and failed. Fixed by changing to `priority.value`.

## DO NOT

- Use `str(member)` to get the string value of a `str, enum.Enum`
- Assume that because the enum's value IS a string, `str()` will return it
