# 0003-GAP-no-test-coverage-acceptance-criteria

**Type:** GAP
**Date:** 2026-05-22
**Round:** kisanmitra-product redteam Round 1

## Finding

Only 4 of 18 todos include test coverage as an explicit acceptance criterion:
- TODO-100: "Unit tests covering CRUD operations"
- TODO-101: "Unit tests for obligation CRUD and cash flow calculation"
- TODO-102: "Unit tests for sale recording and distress detection"
- TODO-201: "Write tests for all 4 demo scenarios"

The remaining 14 todos have no test coverage acceptance criteria. Per `testing.md` audit mode, every new module requires a test — and per `specs-authority.md` Rule 5b, every spec edit triggers a full sibling-spec re-derivation.

## Why This Is a Gap

Without explicit test ACs in the todo, the implementation agent may treat tests as optional. The result: modules ship with zero test coverage, and the first `/redteam` round produces 14 HIGH findings (zero new tests for new modules).

More critically, Kisanmitra handles **financial data** (obligation amounts, sale prices, KCC EMI calculations) and **health crisis detection** (Ayushman Bharat pathway). These are the categories in `testing.md` that require 100% coverage, not 80%.

## How to Resolve

Add test coverage acceptance criteria to each todo's AC list before `/implement` begins. The pattern:

```
## Acceptance Criteria (additions)
- [ ] Unit tests for <module> with ≥80% coverage
- [ ] Tier-2 integration test against real SQLite database
- [ ] For financial modules (TODO-101, TODO-102, TODO-200): 100% coverage on calculation logic
```

## Status

OPEN — test ACs to be added to all 18 todos.
