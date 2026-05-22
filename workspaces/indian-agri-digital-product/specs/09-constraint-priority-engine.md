# Spec: Constraint Priority Engine

## Overview

The Constraint Priority Engine (CPE) is the platform-level architectural layer that makes the three domain engines (Income, Climate, Soil) behave as complementary modules rather than competing ones. It does this through a strict gate-based filtering architecture: each engine produces domain recommendations, but the CPE evaluates them against the farmer's current constraint state and suppresses recommendations that violate binding constraints.

**The core principle: the CPE suppresses, never modifies.** A recommendation that cannot be acted on given the farmer's current constraints is not shown. The CPE does not try to adapt, adjust, or re-rank recommendations — it filters.

**Second principle: one recommendation at a time.** When the CPE passes multiple recommendations from different engines, it issues them sequentially in priority order, not simultaneously. The farmer receives one clear action, not a list.

---

## 1. Architecture

### 1.1 Position in the System

```
┌─────────────────────────────────────────────────────────────┐
│                    Farmer OS Platform                        │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Income      │  │   Climate    │  │    Soil      │   │
│  │   Engine      │  │   Engine     │  │   Engine     │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                  │                  │            │
│         └──────────────────┼──────────────────┘            │
│                            ▼                               │
│              ┌─────────────────────────┐                   │
│              │  Constraint Priority    │                   │
│              │      Engine            │                   │
│              │  (Platform Layer)      │                   │
│              └───────────┬────────────┘                   │
│                          │                               │
│                          ▼                               │
│              ┌─────────────────────────┐                 │
│              │  Single Recommendation │                 │
│              │       Output            │                 │
│              └─────────────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow

1. Each engine publishes recommendations to the Recommendation Bus (event stream)
2. The CPE subscribes to the Recommendation Bus
3. The CPE evaluates all published recommendations against the current Constraint State
4. The CPE outputs exactly one recommendation (or a suppression notification)

### 1.3 Module Independence

Each domain engine remains fully independent. The CPE knows nothing about soil chemistry, weather forecasting, or market dynamics — it only knows the constraint state and the constraint gates.

**Why this matters:** The Soil Engine can be developed and deployed without the Climate Engine. The Income Engine can launch first without the others. Each engine added to the system simply publishes more recommendations to the bus; the CPE handles the filtering without requiring engine-level modifications.

---

## 2. Constraint State

### 2.1 State Entity

The Constraint State is a first-class data entity stored in the farmer's profile. It is not computed fresh each time — it is maintained incrementally as events fire.

| Field | Type | Values | Update Trigger |
|---|---|---|---|
| `health_status` | Enum | `normal`, `stress`, `crisis` | Health event (hospitalization, medical expense logged) |
| `tenure_type` | Enum | `owner`, `tenant` | Onboarding, lease renewal event |
| `cash_flow_status` | Enum | `surplus`, `balanced`, `deficit`, `emergency` | Income Engine Module 2 assessment |
| `selling_window` | Enum | `open`, `closed` | Crop cycle: harvest date entered |
| `time_criticality` | Enum | `normal`, `sowing_window`, `growing_window`, `harvest_window` | Crop cycle dates |
| `active_constraint` | Enum | `null`, `health`, `tenure`, `cash`, `selling`, `timing` | CPE computed |

### 2.2 Health Status

| Value | Meaning | Trigger |
|---|---|---|
| `normal` | No health stress detected | Default |
| `stress` | Household member illness, increased medical expenses | Farmer self-report, agent observation |
| `crisis` | Hospitalization, major medical expense, death in family | Farmer self-report, urgent cash need flagged |

**The Health Gate (Gate 1) is the binding constraint.** When `health_status = crisis`, all recommendations except health crisis resources are suppressed.

### 2.3 Cash Flow Status

| Value | Meaning | Trigger |
|---|---|---|
| `surplus` | Cash available beyond immediate needs | Income Engine Module 2 |
| `balanced` | Cash meets needs without buffer | Income Engine Module 2 |
| `deficit` | Cannot meet all obligations without selling / borrowing | Income Engine Module 2 |
| `emergency` | Immediate cash need within 48 hours | Income Engine Module 2 health shock detection |

**The Cash Flow Gate (Gate 3) gates investment recommendations.** When `cash_flow_status = emergency`, all Soil Engine investment recommendations and Climate Engine capital-intensive recommendations are suppressed.

### 2.4 Time Criticality Windows

Derived from the crop cycle entity (`specs/01-domain-model.md` §3):

| Window | Trigger | CPE Behavior |
|---|---|---|
| `sowing_window` | Current date within 14 days of `sowing_date` | Climate sowing advisories pass; long-duration Soil recommendations suppressed |
| `growing_window` | Between sowing and harvest | All engines issue normal advisories |
| `harvest_window` | Within 7 days of `expected_harvest_date` | Selling recommendations take priority; Soil investment recommendations suppressed |

---

## 3. The Five Gates

The gates evaluate in strict priority order. A gate that fires (constraint is active) suppresses all recommendations from engines ranked below it, and all recommendations from engines ranked at the same level.

| Gate | Priority | Name | When Active | Suppresses |
|---|---|---|---|---|
| Gate 1 | 1 (highest) | Health | `health_status = crisis` | Everything except health crisis resources |
| Gate 2 | 2 | Tenure | `tenure_type = tenant` AND `recommendation.requires_tenure_security = true` | Soil multi-year investments |
| Gate 3 | 3 | Cash Flow | `cash_flow_status = emergency` OR `cash_flow_status = deficit` | Capital-intensive recommendations (Soil Options B/C, CSA practices) |
| Gate 4 | 4 | Selling Window | `selling_window = open` AND `harvest_within_7_days = true` | Soil planting recommendations, Climate sowing delay advisories |
| Gate 5 | 5 | Time Criticality | `time_criticality = sowing_window` OR `harvest_window` | Recommendations requiring multi-day action |

### 3.1 Gate 1: Health Gate (Priority 1)

**Rule:** When `health_status = crisis`, suppress all recommendations except health crisis resources.

**Why this is first:** A household with a medical emergency is not making optimal input investment decisions or market timing decisions. No Soil recommendation about next season's fertilizer matters if the family cannot afford to eat this month.

**What passes:**
- Emergency credit pathway (Income Module 5, but only for medical emergency context)
- Ayushman Bharat / government health scheme information
- Hospital / clinic contact information
- Emergency fund resources

**What is suppressed:**
- All Soil Engine recommendations
- All Climate Engine recommendations
- Income Engine selling recommendations (except distress sale support)
- All financial product recommendations (insurance, warehouse receipts)

**Implementation:**
```python
def health_gate(recommendation, constraint_state):
    if constraint_state.health_status != "crisis":
        return PASS
    if recommendation.category == "health_crisis_resource":
        return PASS
    return SUPPRESS(reason="health_crisis_active")
```

### 3.2 Gate 2: Tenure Gate (Priority 2)

**Rule:** When `tenure_type = tenant`, suppress all recommendations that require multi-year tenure to deliver value.

**Why this matters:** A tenant farmer on a 1-year lease cannot recover the residual value of a soil health investment (vermicompost, land leveling, borewell). If the landowner does not renew the lease, the tenant's investment is lost.

**What passes for tenant farmers:**
- Season-level interventions with return within the lease period (zinc sulfate, IPM practices, harvest timing)
- Recommendations that the tenant can negotiate into the lease agreement
- Input cost optimization that pays back within the current season

**What is suppressed for tenant farmers:**
- Multi-year soil health improvement plans
- Vermicompost / organic transition programs
- Land improvement investments (borewell, leveling)
- Crop diversification requiring landlord approval

**Tenant detection:** `land_tenure = "Tenant"` or `land_tenure = "Lease"` in the Land Holding entity (`specs/01-domain-model.md` §2.2).

**Recommendation metadata required:** Each Soil Engine recommendation must carry a `tenure_requirement` field: `owner_only`, `tenant_viable`, `any`.

### 3.3 Gate 3: Cash Flow Gate (Priority 3)

**Rule:** When `cash_flow_status = emergency` or `deficit`, suppress capital-intensive recommendations from all engines.

**Capital-intensive recommendations suppressed:**
- Soil Engine Options B/C (organic inputs, balanced fertilization)
- Climate Engine CSA practices (drip irrigation, laser leveling)
- Financial product recommendations requiring upfront premium

**What passes:**
- Selling recommendations (Income Engine Module 4)
- Minimum-cost input optimization (Soil Engine Option A — reduced urea, not organic transition)
- Weather monitoring advisories (no-cost action)
- Harvest timing recommendations

**Cash flow status source:** Income Engine Module 2 assessment, updated weekly during active crop cycles.

### 3.4 Gate 4: Selling Window Gate (Priority 4)

**Rule:** When `selling_window = open` AND `harvest_within_7_days = true`, suppress all recommendations except selling and storage.

**Why this matters:** The 7 days before and after harvest is the highest-stakes selling window. Recommendations about next season's inputs or future climate planning are distractions from the immediate financial decision.

**What passes during harvest window:**
- Income Engine Module 4 (Selling Decision Guide)
- Income Engine Module 3 (Multi-Mandi Bargaining Visibility)
- Storage recommendations (warehouse receipt options)
- Emergency credit for harvest labor costs

**What is suppressed:**
- Soil Engine input recommendations for next season
- Climate Engine sowing advisories
- Climate-smart practice recommendations

### 3.5 Gate 5: Time Criticality Gate (Priority 5)

**Rule:** When `time_criticality = sowing_window`, suppress recommendations requiring multi-day action.

**Specific behaviors:**

**During `sowing_window`:**
- Climate Engine sowing delay advisories pass (action: wait 5 days)
- Climate Engine long-duration practice recommendations suppressed (action requires weeks)
- Soil Engine input recommendations for current season suppressed (too late — inputs must already be purchased)
- Soil Engine pre-planting soil preparation recommendations pass

**During `harvest_window`:**
- All non-selling recommendations suppressed
- Harvest timing optimization passes

**During `growing_window`:**
- All gates 1–4 rules apply normally
- Gate 5 is inactive (normal state)

---

## 4. Recommendation Bus

### 4.1 Message Format

Each engine publishes recommendations to the Recommendation Bus in this format:

```json
{
  "recommendation_id": "uuid",
  "engine": "income|climate|soil",
  "module": "module identifier",
  "category": "selling|input|weather|practice|financial|health",
  "action": "human-readable action description",
  "target_date": "date or null",
  "requires_tenure_security": true|false,
  "capital_intensity": "none|low|medium|high",
  "time_to_action": "immediate|hours|days|weeks",
  "priority_for_engine": 1|2|3,
  "metadata": {}
}
```

### 4.2 CPE Output Format

```json
{
  "output_type": "recommendation|suppression",
  "recommendation": { /* passed recommendation */ },
  "suppressed_reasons": [
    {
      "engine": "soil",
      "module": "module_3",
      "reason": "cash_flow_emergency",
      "gate": 3
    }
  ],
  "active_constraint": "cash_flow",
  "confidence_note": "string or null"
}
```

### 4.3 Suppression vs. Not-Shown

**Suppression:** The recommendation was evaluated and blocked by a gate. The suppression is logged and surfaced to the farmer as: "We have a recommendation for you about [topic], but given your current situation we want to focus on [active_constraint] first."

**Not-shown:** The recommendation was not evaluated because a higher-priority gate already fired. The engine may not have even published the recommendation — the CPE does not surface not-shown items.

---

## 5. Sequencing Consistency

### 5.1 Phase 1: Income Engine Only (Months 0–6)

The CPE runs with only the Income Engine publishing to the Recommendation Bus.

**Active gates:** Gate 1 (Health), Gate 3 (Cash Flow), Gate 4 (Selling Window), Gate 5 (Time Criticality)

**Gate 2 (Tenure) is active but Soil Engine is not publishing yet.**

**Constraint state updates from:** Income Engine Module 2 (cash flow), crop cycle data (selling window, time criticality), farmer self-report (health status)

### 5.2 Phase 2: Income + Soil Micro-Zoning (Months 6–18)

Soil Engine publishes recommendations to the Recommendation Bus. Soil Engine is constrained to micro-zoning (farmer self-assessment) and season-level interventions — NOT multi-year soil health plans.

**Active gates:** All five gates

**New capabilities in Phase 2:**
- Soil Engine recommendations filtered by Gate 2 (Tenure)
- Soil Engine capital-intensive recommendations (Option B/C) filtered by Gate 3 (Cash Flow)
- Soil Engine pre-sowing recommendations filtered by Gate 5 (Time Criticality)

### 5.3 Phase 3: Add Climate Engine at District Level (Months 18–30)

Climate Engine publishes district-level advisories (not plot-level — plot-level requires ground truth that does not yet exist).

**Active gates:** All five gates

**Climate Engine constraints in Phase 3:**
- Only district-interpolated advisories (not AWS-verified plot-level)
- No capital-intensive CSA practice recommendations until capital access infrastructure exists
- Explicit confidence labeling on every advisory

### 5.4 Phase 4: Full Integration (Month 30+)

All three engines publishing. Ground truth data validating the forecast model. Plot-level advisories in AWS-covered areas.

---

## 6. The One-Recommendation Rule

### 6.1 Why One?

Multiple simultaneous recommendations cause decision paralysis. The farmer who receives "sell now" AND "delay sowing" AND "apply balanced fertilizer" does none of them.

The CPE enforces one-recommendation-at-a-time by issuing in priority order:

1. If Gate 1 (Health) fires: issue health crisis resource
2. Else if Gate 4 (Selling Window) fires: issue selling recommendation
3. Else issue the highest-priority recommendation from the active engine (by crop cycle phase: sowing → Climate, growing → Soil, harvest → Income)

### 6.2 Suppression Notification

When recommendations are suppressed, the farmer receives a suppression notification — not the suppressed recommendation.

**Format:** "Right now, [active_constraint] is your main priority. We have [topic] advice ready for you — we'll share it once [constraint] is addressed."

**Why this matters:** The farmer knows the platform has relevant information. The suppression is temporary and conditional. The farmer is not abandoned — they are protected from irrelevant noise.

---

## 7. Constraint State Update Events

### 7.1 Event Types

| Event | Source | Effect on Constraint State |
|---|---|---|
| `health_status_changed` | Farmer self-report, agent observation, health scheme enrollment | Sets `health_status` |
| `harvest_date_entered` | Farmer or field agent | Opens `selling_window` |
| `harvest_completed` | Farmer self-report | Closes `selling_window`, sets `growing_window` |
| `cash_flow_assessed` | Income Engine Module 2 | Sets `cash_flow_status` |
| `season_changed` | Crop cycle update | Sets `time_criticality` |
| `tenant_lease_updated` | Farmer self-report | Sets `tenure_type` |

### 7.2 Health Status Update Protocol

**How health status changes to `crisis`:**
- Farmer self-reports hospitalization or major medical expense via IVR (call, press 1 for medical emergency)
- Field agent observes and logs
- Income Engine Module 2 detects pattern: urgent cash need + recent health-related expense category

**How health status returns to `normal`:**
- Farmer self-reports resolution via IVR
- 30-day period without health-related cash outflow
- Auto-reassessment at next crop cycle start

---

## 8. Edge Cases

### 8.1 Multiple Gates Fire Simultaneously

Gates fire in priority order. Gate 1 (Health) always wins over Gate 4 (Selling Window). A farmer in health crisis who is also in harvest window receives health crisis resources — not selling recommendations — even if grain is ready to harvest.

**Why this ordering:** The farmer's health is a life-safety issue. Selling grain can wait; a medical emergency cannot.

### 8.2 Contradictory Recommendations From Same Engine

If the Income Engine itself publishes contradictory recommendations (Module 2 says "hold" AND Module 4 says "sell now"), the CPE catches this at the engine level before the cross-engine gate evaluation. Each engine must resolve its own internal contradictions before publishing to the Recommendation Bus.

### 8.3 Farmer in Harvest Window With Health Crisis

**Gate 1 fires:** Health crisis resources
**Result:** Farmer receives health information, not selling advice. A family member or village agent must handle the harvest decision.

**Why this is correct:** The farmer in health crisis cannot be expected to simultaneously manage a harvest and a medical emergency. The platform should connect them to harvest labor support (via MGNREGA, village agents) rather than adding harvest decision complexity.

### 8.4 Tenant Farmer in Sowing Window With Cash Deficit

**Gate 2 fires (Tenant):** Multi-year soil investments suppressed
**Gate 3 fires (Cash Deficit):** Capital-intensive recommendations suppressed
**Gate 5 fires (Sowing Window):** Recommendations requiring multi-day action suppressed

**Result:** Farmer receives only immediate, no-cost, season-level recommendations: zinc sulfate application (if cash permits), harvest timing from previous season, weather monitoring.

**Why this is correct:** The tenant with cash deficit cannot invest in soil health. The platform's job is to protect the farmer from recommendations they cannot follow — not to issue a perfect plan for a situation that cannot be perfect.

---

## 9. What This Enables

### 9.1 Module Complementarity

With the CPE, the three engines are genuinely complementary:

- **Income Engine** handles the selling decision and cash flow management
- **Soil Engine** handles input optimization when cash and tenure allow
- **Climate Engine** handles weather advisories when timing allows

Each engine contributes when its domain is relevant and constrained by when the farmer can actually act.

### 9.2 Honest Limitations

The CPE makes limitations explicit rather than hiding them:

- "We can't recommend soil investment because you're a tenant" (Gate 2)
- "We can't recommend organic transition because you need cash this season" (Gate 3)
- "We can't advise on sowing timing because we don't have your plot-level weather data yet" (Phase 3 prerequisite)

### 9.3 Trust Preservation

Farmers stop trusting platforms that issue recommendations they cannot follow. The CPE prevents the trust-destroying pattern: recommendation → failure to act → platform blames farmer → farmer leaves.

By suppressing recommendations that cannot be acted on, the CPE ensures that every recommendation the farmer receives is actually actionable.

---

## 10. Open Questions

### 10.1 Who Owns Constraint State Updates?

The CPE requires real-time constraint state updates. In Phase 1 (Income-only), the Income Engine's Module 2 (Cash Flow Assessment) updates the constraint state. But who updates health status? The farmer self-reports via IVR — but how is this incentivized?

**Options:**
1. Field agents update health status during farmer interactions
2. Health status is inferred from cash flow patterns (medical expenses flag health stress)
3. Government health scheme enrollment data (Ayushman Bharat) provides passive updates

### 10.2 Tenure Gate Accuracy

The `tenure_type` field requires accurate farmer self-reporting. How is this verified? Land records in India are often incomplete, especially for tenant farmers who have informal lease agreements.

**Minimum viable approach:** Accept farmer self-report at onboarding; flag as "unverified." Route tenant farmers to programs that help formalize lease agreements (MGNREGA, state land rights schemes).

### 10.3 Selling Window Detection

The `selling_window = open` trigger requires accurate harvest date data. Farmers often do not know their harvest date in advance.

**Minimum viable approach:** Use crop calendar estimates (`expected_harvest_date` from Crop Cycle entity) with a 14-day window. Confirm actual harvest with farmer report after harvest.

---

*Spec authority: Constraint Priority Engine*
*Version: 1.0*
*Prerequisites: Farmer entity model (specs/01-domain-model.md), Income Engine, Soil Engine, Climate Engine*
*Sequencing: Phase 1 deployable, Phase 2 additions documented*
