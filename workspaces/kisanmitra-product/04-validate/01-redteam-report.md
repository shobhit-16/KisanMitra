# Redteam Report — kisanmitra-product

**Date:** 2026-05-22
**Workspace:** `workspaces/kisanmitra-product/`
**Posture:** L5_DELEGATED (no posture.json present)
**Round:** 1 (Plan-only pre-implementation audit)
**Baseline:** demo.html (4,805 lines, 17 screens, verified prior session — 0 CRITICAL, 0 HIGH, 0 MEDIUM)

---

## Step 0 — Posture Check

No `posture.json` in main checkout. Per `trust-posture.md` Rule 2: fresh repo posture = L5_DELEGATED. No `pending_verification` entries. Proceeding with Round 1.

---

## Step 1 — Spec Compliance Audit

### Source Audit

Per `specs-authority.md` Rule 1, every project MUST have a `specs/` directory with `_index.md`. The workspace `workspaces/kisanmitra-product/` has:

| Required Source | Present? | Location |
|---|---|---|
| `specs/_index.md` | **NO** | — |
| `briefs/` (user input surface) | **NO** | — |
| `01-analysis/` | **NO** | — |
| `02-plans/` | **NO** | — |
| `03-user-flows/` | **NO** | — |
| `todos/active/` | YES | 18 todo files |

**Finding S-1 (CRITICAL):** `specs/` directory does not exist in the workspace. Per `specs-authority.md` Rule 1, this is a hard prerequisite before `/implement` can proceed. All 18 todos reference spec sections that don't exist yet. No spec = no authoritative domain truth to implement against.

**Finding S-2 (HIGH):** No `briefs/` directory. Per `workspaces/CLAUDE.md`, `briefs/` is the only place users write. The absence means there is no user-anchored input surface for value-ranking per `value-prioritization.md` MUST-1.

**Finding S-3 (MEDIUM):** No `01-analysis/` or `03-user-flows/`. The analyze phase was bypassed. For a product of this complexity (Phase 1 income engine + CPE + PWA + 3 government integrations), bypassing analysis is a risk — failure modes in the GTM strategy, stakeholder alignment, and farmer persona details are not captured.

### Demo.html Baseline Verification

The existing `demo.html` at project root was verified in the prior session as the functional spec baseline. All 17 screens exist, all 5 CPE gates are represented, and the 4 demo scenarios (healthy, cash_stress, crisis, harvest) are implemented in JavaScript.

The todos reference demo.html behavior correctly. However, the demo is a **prototype simulation**, not a **specification**. Key spec-quality gaps in demo.html that the todos correctly inherit:

- Mandi prices are hardcoded (₹28/qt Lasalgaon, ₹27.50 Yeola, ₹28.30 Niphad) — not API-driven
- CPE scenarios are static JavaScript objects — not a real rule engine
- Farmer state (Rambhau Gite) is hardcoded — not a database record
- No real authentication — phone number as identifier only

These are expected for a demo, but the **todo acceptance criteria** must ensure real wiring replaces mock behavior before `/implement` is considered complete.

### Todo-to-Demo Traceability

| Todo | Demo Screen | Spec Status |
|---|---|---|
| TODO-100 (Farmer CRUD) | S1 (welcome) | No spec file; demo uses hardcoded farmer |
| TODO-101 (Obligations) | S2 (obligations) | No spec file; demo shows KCC/school/rent |
| TODO-102 (Ledger) | S9 (ledger) | No spec file; demo shows 4 hardcoded sales |
| TODO-200 (Income Engine) | S4 (sell) | No spec file; demo has static price + storage math |
| TODO-201 (CPE Engine) | S8 (CPE simulator) | No spec file; demo has 4 static JS scenarios |
| TODO-202 (Farmer State) | All screens | No spec file; state is in-memory JS |
| TODO-203 (Emergency Credit) | S5 (credit) | No spec file; demo hardcodes Ayushman |
| TODO-300 (eNAM) | S3 (mandi) | No spec file; demo hardcodes prices |
| TODO-301 (IMD Weather) | S6 (climate) | No spec file; demo shows static 7-day |
| TODO-302 (Govt Schemes) | S5 (credit) | No spec file; demo hardcodes PM-KISAN/Ayushman |
| TODO-400 (PWA) | All | No spec file; demo is a single HTML |
| TODO-401 (API Integration) | All | No spec file; demo has zero real API calls |
| TODO-402 (Voice Input) | S1 (voice) | No spec file; demo shows voice modal |
| TODO-403 (Push) | All | No spec file; demo has no push |
| TODO-500 (FPO Partnership) | S10 (FPO) | No spec file; demo hardcodes Nashik FPO |
| TODO-501 (Auth) | S1 | No spec file; demo has no auth |
| TODO-502 (Metrics) | None | No spec file; no metrics in demo |

**Assertion:** Every todo maps to demo.html behavior, but none map to a spec file. The demo is the implicit spec — this is acceptable for a prototype-to-production conversion, but the `specs/` directory must be created to satisfy `specs-authority.md` Rule 1 before `/implement`.

---

## Step 2 — Todo Quality Audit

### Capacity Budget Compliance

Per `autonomous-execution.md` § Per-Session Capacity Budget, each shard must fit: ≤500 LOC load-bearing logic, ≤10 invariants, ≤4 call-graph hops, describable in 3 sentences.

| Todo | LOC Estimate | Invariants | Call hops | Fits budget? |
|---|---|---|---|---|
| TODO-100 (Farmer CRUD) | ~300 | 5 | 2 | YES |
| TODO-101 (Obligations) | ~400 | 6 | 3 | YES |
| TODO-102 (Ledger) | ~350 | 5 | 2 | YES |
| TODO-200 (Income Engine) | ~600 | 8 | 4 | MARGINAL (at limit) |
| TODO-201 (CPE Engine) | ~700 | 10 | 4 | MARGINAL (at limit) |
| TODO-202 (Farmer State) | ~300 | 4 | 2 | YES |
| TODO-203 (Emergency Credit) | ~250 | 4 | 2 | YES |
| TODO-300 (eNAM) | ~500 | 7 | 3 | MARGINAL (at limit) |
| TODO-301 (IMD Weather) | ~400 | 6 | 3 | YES |
| TODO-302 (Govt Schemes) | ~350 | 5 | 2 | YES |
| TODO-400 (PWA) | ~1200 | 12 | 5 | **NO** — needs decomposition |
| TODO-401 (API Integration) | ~800 | 10 | 4 | MARGINAL (at limit) |
| TODO-402 (Voice) | ~300 | 4 | 2 | YES |
| TODO-403 (Push) | ~300 | 4 | 2 | YES |
| TODO-500 (FPO) | ~400 | 5 | 2 | YES |
| TODO-501 (Auth) | ~400 | 6 | 3 | YES |
| TODO-502 (Metrics) | ~300 | 4 | 2 | YES |

**Finding T-1 (HIGH):** TODO-400 (PWA Architecture) exceeds the per-session capacity budget. 1,200 LOC + 12 invariants + 5 call-graph hops. Must be decomposed into sub-todos before implementation.

**Finding T-2 (MEDIUM):** TODO-200, TODO-201, TODO-300, and TODO-401 are at capacity margins. Implementation should proceed with caution and re-shard if complexity increases.

### Dependency Chain Analysis

```
TODO-000 (Scaffold)
  └─ TODO-100 (Farmer CRUD) [foundation]
       ├─ TODO-101 (Obligations)
       ├─ TODO-102 (Ledger)
       └─ TODO-501 (Auth)
            └─ TODO-500 (FPO Partnership)
  └─ TODO-300 (eNAM) [independent]
  └─ TODO-301 (IMD Weather) [independent]
  └─ TODO-302 (Govt Schemes) [independent]

TODO-100 + TODO-101 → TODO-200 (Income Engine)
TODO-200 → TODO-201 (CPE Engine)
TODO-101 + TODO-102 → TODO-203 (Emergency Credit)

TODO-100 → TODO-400 (PWA) [consumes farmer state]
TODO-100 + all backend → TODO-401 (API Integration)
TODO-400 → TODO-402 (Voice)
TODO-400 → TODO-403 (Push)

TODO-400 complete → TODO-502 (Pilot Metrics)
```

**Finding T-3 (MEDIUM):** The dependency chain means TODO-100 (Farmer CRUD) is on the critical path. If this shard slips, 7 downstream todos are blocked. Recommend prioritizing TODO-100 first.

### Integration Wiring Gap

**Critical pattern identified:** Every "build" todo produces a mock-in-capable component. The corresponding "wire" todo (TODO-401) is listed separately. This is correct per `autonomous-execution.md` discipline, but TODO-401 is sequenced AFTER all other backend and frontend todos — meaning the system has no end-to-end integration point until the very end of the implementation.

**Finding T-4 (HIGH):** TODO-401 (API Integration) is the only todo that wires real API calls. All other 17 todos produce components that work in isolation. If TODO-401 reveals design mismatches, many upstream components may need revision.

---

## Step 3 — Spec Compliance Against demo.html

### Demo.html Verification (Prior Session Results)

demo.html passed redteam in the prior session with:
- 0 CRITICAL findings
- 0 HIGH findings
- 0 MEDIUM findings
- All 17 screens functional
- All 494 `data-i` attributes translated
- CPE simulator correctly implements 4 scenarios
- Voice modal with keyword chips functional

### Acceptance Criteria Traceability

| Todo | Acceptance Criteria Count | Demo Verified? |
|---|---|---|
| TODO-100 | 7 ACs | Partial (demo uses hardcoded farmer) |
| TODO-101 | 7 ACs | Partial (demo shows static obligations) |
| TODO-102 | 6 ACs | Partial (demo shows hardcoded sales) |
| TODO-200 | 6 ACs | Partial (demo has static sell logic) |
| TODO-201 | 8 ACs | YES (demo CPE matches 4 scenarios) |
| TODO-202 | Not specified | NO (no farmer state in demo) |
| TODO-203 | 4 ACs | Partial (demo hardcodes Ayushman) |
| TODO-300 | 6 ACs | NO (demo hardcodes mandi prices) |
| TODO-301 | Not specified | NO (demo shows static weather) |
| TODO-302 | 4 ACs | Partial (demo hardcodes schemes) |
| TODO-400 | 7 ACs | YES (17 screens in demo) |
| TODO-401 | 6 ACs | NO (demo has zero real API calls) |
| TODO-402 | 3 ACs | Partial (demo shows voice modal UI only) |
| TODO-403 | 3 ACs | NO (demo has no push) |
| TODO-500 | 4 ACs | Partial (demo shows static FPO) |
| TODO-501 | 5 ACs | NO (demo has no auth) |
| TODO-502 | 6 ACs | NO (no metrics in demo) |

---

## Step 4 — Test Coverage (Pre-implementation)

No implementation exists yet. No tests exist yet. All test coverage is future-tense.

Per `testing.md` audit mode rules: each new module requires new tests. The todos do not include test file creation as explicit acceptance criteria (except in a few cases). Recommend adding test coverage acceptance criteria to each todo before `/implement`.

---

## Step 5 — Findings Summary

### CRITICAL

| ID | Finding | Rule | Remediation |
|---|---|---|---|
| S-1 | `specs/` directory missing — no domain truth exists to implement against | `specs-authority.md` Rule 1 | Create `specs/_index.md` + domain spec files before `/implement` |

### HIGH

| ID | Finding | Rule | Remediation |
|---|---|---|---|
| S-2 | No `briefs/` directory — no user-anchored input surface | `workspaces/CLAUDE.md` | Create `briefs/01-product-brief.md` from SPEC.md and user context |
| T-1 | TODO-400 (PWA) exceeds per-session capacity budget (1,200 LOC, 12 invariants, 5 hops) | `autonomous-execution.md` Rule 1 | Decompose into TODO-410/411/412/413 before implementation |
| T-3 | TODO-100 (Farmer CRUD) is critical-path bottleneck — 7 downstream todos blocked | dependency analysis | Ensure TODO-100 is first shard in implementation |
| T-4 | TODO-401 (API Integration) is the only end-to-end wiring todo — late integration risk | architecture | Consider adding intermediate integration checkpoints |

### MEDIUM

| ID | Finding | Rule | Remediation |
|---|---|---|---|
| S-3 | No `01-analysis/` or `03-user-flows/` — GTM strategy, stakeholder analysis absent | phase completeness | Consider creating at least a GTM brief in `briefs/` |
| T-2 | TODO-200/201/300/401 are at capacity margins — monitor during implementation | `autonomous-execution.md` Rule 1 | Be prepared to shard these during implementation |
| TC-1 | No explicit test coverage acceptance criteria in most todos | `testing.md` | Add test coverage requirements to each todo's ACs |

---

## Step 6 — Convergence Criteria Assessment

Per the redteam skill, convergence requires:
1. **0 CRITICAL findings** — NOT MET (1 CRITICAL: missing specs)
2. **0 HIGH findings** — NOT MET (4 HIGH findings)
3. **2 consecutive clean rounds** — NOT MET (Round 1)
4. **Spec compliance 100%** — NOT MET (no specs directory)
5. **New code has new tests** — NOT APPLICABLE (pre-implementation)
6. **Frontend: 0 mock data** — NOT MET (demo.html is entirely mock)

**Verdict: /implement is BLOCKED until the CRITICAL finding is resolved.**

---

## Recommendations

### Before /implement (Required)

1. **Create `specs/` directory** with at minimum:
   - `specs/_index.md` — manifest of all spec files
   - `specs/farmer-profile.md` — farmer entity, CRUD contracts
   - `specs/income-engine.md` — sell/store recommendation logic, mandi price contracts
   - `specs/cpe-engine.md` — 5-gate rule definitions, recommendation bus contract
   - `specs/obligation-calendar.md` — obligation types, cash flow calculation
   - `specs/income-ledger.md` — sale recording, MSP distress threshold
   - `specs/integrations.md` — eNAM, IMD, govt scheme API contracts
   - `specs/pwa-architecture.md` — screen map, state management, offline strategy

2. **Create `briefs/01-product-brief.md`** capturing:
   - Farmer persona (Rambhau Gite — already in SPEC.md)
   - GTM strategy (FPO-first, Nashik district, 10-farmer pilot)
   - Stakeholder map (state dept, ICAR/SAUs, FPOs, banks, NGOs)
   - Non-negotiables (no monetization, public good, voice-first)

3. **Decompose TODO-400** into 4 sub-todos:
   - TODO-410: PWA manifest + service worker skeleton
   - TODO-411: App shell + screen router
   - TODO-412: State store + offline data sync
   - TODO-413: 17-screen migration (one per screen or in groups)

### During /implement (Process)

4. Add explicit test coverage acceptance criteria to each todo
5. Run TODO-100 first (critical path)
6. Add intermediate integration checkpoints between TODO-100/101/102 and TODO-200/201

---

## Receipts

- demo.html verified: prior session (2026-05-22), 0 CRITICAL/0 HIGH/0 MEDIUM
- Workspace structure audit: `workspaces/kisanmitra-product/` (this session)
- Todo capacity analysis: this session
- Spec compliance sweep: this session
