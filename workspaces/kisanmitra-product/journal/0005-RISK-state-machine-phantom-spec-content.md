# RISK: Farmer State Machine Phantom Spec Content

**Date:** 2026-05-22
**Finding:** SC-003 from Round 1 spec compliance audit

## The Problem

`specs/farmer-profile.md` § "Farmer State Machine" (lines 163-185) defined a farmer lifecycle state machine with states NEW/ACTIVE/INACTIVE/LANDED/ACTIVE_WITH_HISTORY. Zero implementation existed. Per `spec-accuracy.md` Rule 1, every citation in spec must resolve against working code.

## Why It Was Phantom

The Phase 1 CPE gates do NOT use farmer operational state as an input:
- **Gate 1** (Health Crisis): Driven by `health_crisis` event flag
- **Gate 3** (Cash Flow): Driven by `CashFlowStatus` enum (DEFICIT/TIGHT/BALANCED/HEALTHY)
- **Gate 4** (Selling Window): Driven by `harvest_date` presence

The state machine was spec decoration with no implementation and no consumers.

## Resolution

Section excised from `specs/farmer-profile.md`. Verification:
```bash
grep -rn "LANDED\|ACTIVE_WITH_HISTORY" src/kisanmitra/
# → no matches (never implemented, correctly removed)
```

## Lesson

If a spec section defines behavior, either implement it or remove the spec. A spec that describes unimplemented behavior creates lookahead risk — someone assumes it works and builds around it.

## Files Changed

- `specs/farmer-profile.md` — removed State Machine section
- `04-validate/02-spec-compliance-round2.md` — Round 2 closure report
