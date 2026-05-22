# Gap Analysis: Indian Agri Digital Product — Phase 1 Todo Decomposition

**Date:** 2026-05-20
**Analyst:** Analysis Specialist
**Phase:** 01-analysis → 02-todos
**Status:** INDEPENDENT GAP ANALYSIS (no generated todos found in `todos/active/`)

---

## Executive Summary

The Phase 1 scope (Income Engine + CPE + farmer domain model + multi-channel delivery) is well-defined in the CPE spec (`09-constraint-priority-engine.md`) and the ground challenges analysis (`15-ground-challenges-practical-feasibility.md`). However, the Phase 1 todo decomposition is missing critical implementation work that the specs and analysis documents explicitly require. Five categories of gaps were identified:

1. **Missing TODOs** — work explicitly mandated by specs that has no corresponding todo
2. **Cloudest TODOs** — existing todos too vague to implement without clarification
3. **Wrong Scope** — items included in Phase 1 that belong elsewhere
4. **Phase 2+ Leakage** — work pulled into Phase 1 that belongs in later phases
5. **Missing Dependencies** — sequencing gaps where one piece of work blocks another

**Complexity: Moderate** — no architectural gaps; all gaps are coverage gaps in the todo decomposition. The CPE architecture is sound; the issue is incomplete work breakdown.

---

## 1. MISSING TODOS

### 1.1 Women Farmer SHG Integration (CRITICAL — 30% enrollment target)

**Spec basis:** `17-geography-pilot-demography.md` §3.3 (Gender Strategy) explicitly requires:
- SHG (Self-Help Group) linkage via Mahila SHG federations in Maharashtra and Stree Shakti SHGs in Karnataka
- IVR as primary channel for women farmers (no smartphone required)
- At least one female field agent per district
- Women farmer WhatsApp groups through SHG leaders
- 30% women farmer enrollment target (1,500 of 5,000 over 18 months)

**Gap:** No todo covers the SHG partnership workflow, the female field agent deployment plan, or the IVR-first design for women farmers. The delivery channels spec (`06-delivery-channels.md`) describes channels in general terms but has no women-specific implementation todo.

**Required todo:**
- SHG partnership framework (Maharashtra + Karnataka SHG federation agreements)
- Women-farmer IVR workflow design (separate from general IVR — language, content, escalation)
- Female field agent recruitment plan (at least 1 per district, with SHG-facing responsibilities)
- Women farmer enrollment tracking metric (30% target, gender-segmented MAU)

**Spec reference:** `17-geography-pilot-demography.md` §3.3, lines 246-269

---

### 1.2 Farmer-Reported Obligation Calendar (Challenge 5 Safeguard)

**Spec basis:** `15-ground-challenges-practical-feasibility.md` §5b explicitly mandates the Non-Negotiable Obligation Calendar as a Challenge 5 safeguard:

> "At onboarding, capture the known upcoming non-negotiable cash outflows: school fee cycles (April, June, October), loan repayment due dates, anticipated wedding/social obligations by season. Use this to set `cash_flow_status` dynamically."

**CPE mapping:** The obligation calendar drives `cash_flow_status` computation alongside Income Module 2 assessment. Without it, Gate 3 (Cash Flow) fires incorrectly for farmers whose cash deficit is predictable (and thus manageable) rather than crisis-level.

**Gap:** No todo covers the obligation calendar data model, collection workflow, or integration with the CPE's cash flow status computation. This is explicitly a Phase 1 deliverable per the ground challenges analysis.

**Required todo:**
- Obligation calendar data model (add to farmer profile — school fee cycles, loan due dates, social obligations by season)
- Onboarding collection workflow (field agent script + IVR self-report option)
- Cash flow status integration (how obligation calendar data feeds Gate 3 computation)

**Spec reference:** `15-ground-challenges-practical-feasibility.md` §5b, lines 144-149

---

### 1.3 Emergency Credit Pathway Legal/Compliance Framework

**Spec basis:** `09-constraint-priority-engine.md` §3.1 (Gate 1: Health Gate) states:

> "What passes: Emergency credit pathway (Income Module 5, but only for medical emergency context)"

And `09-constraint-priority-engine.md` §10.1 (Open Questions):

> "Emergency credit pathway — who provides it? How is it triggered? What are the liability implications?"

**Gap:** No todo covers the emergency credit product design, the institutional partner (NABARD/RRB per the GTM journal), or the legal/compliance framework. This is a product decision that must be resolved before Phase 1 launch — farmers in health crisis will need this pathway to pass through the CPE.

**Required todo:**
- Emergency credit product design (what instrument? How triggered? Who provides capital?)
- NABARD/RRB partnership for emergency credit delivery
- Liability framework (who bears risk when an emergency credit recommendation fails?)
- Gate 1 emergency credit metadata (what does an `emergency_credit` recommendation look like in the Recommendation Bus?)

**Spec reference:** `09-constraint-priority-engine.md` §3.1, §10.1

---

### 1.4 India DPDP Act Compliance Infrastructure

**Spec basis:** `08-farmer-identity.md` §9.1 (Compliance) references:

> "PDP Bill (proposed) — Consent, data principal rights, breach notification"

The farmer identity spec requires consent management, data principal rights, and breach notification — all of which map to India DPDP Act (Digital Personal Data Protection Act, 2023) requirements.

**Gap:** No todo covers DPDP Act compliance implementation. The farmer identity spec describes the model but not the compliance infrastructure required to operationalize it.

**Required todo:**
- DPDP consent collection infrastructure (consent records, consent types per `08-farmer-identity.md` §3.1)
- Data principal rights workflow (access, correction, deletion, portability requests)
- Breach notification system (72-hour notification timeline per `08-farmer-identity.md` §6.3)
- Data retention and disposal automation (per `08-farmer-identity.md` §4.2 retention schedule)

**Spec reference:** `08-farmer-identity.md` §9.1, §4.2, §6.3

---

### 1.5 CPE Gate Accuracy Monitoring and Observability

**Spec basis:** `09-constraint-priority-engine.md` §5.1 (Phase 1 gates) and `17-geography-pilot-demography.md` §2.4 (Success Metrics) require:

- Gate 2 (Tenure) accuracy: cross-validate self-reported `tenure_type` against field agent observations; error rate <15%
- Gate 3 (Cash Flow) accuracy: cross-validate against 90-day farmer expenditure recall survey; error rate <20%
- False suppression rate: share of suppression notifications where farmer could have acted; <10%

**Gap:** No todo covers the monitoring infrastructure to measure these gate accuracy metrics. Without it, the pilot cannot validate that the CPE is working correctly — a critical Phase 1 success gate.

**Required todo:**
- Gate accuracy telemetry (track suppression events with farmer feedback)
- False suppression rate dashboard (CPE suppression events vs. farmer action rate)
- Cash flow status ground truth validation (90-day recall survey instrument and timing)
- Tenure accuracy ground truth validation (field agent spot-check protocol)

**Spec reference:** `09-constraint-priority-engine.md` §5.1, `17-geography-pilot-demography.md` §2.4

---

### 1.6 Confidence Labeling Stub for Future Climate Engine

**Spec basis:** `09-constraint-priority-engine.md` §5.3 (Phase 3 Climate Engine constraints):

> "Explicit confidence labeling on every advisory"

And `15-ground-challenges-practical-feasibility.md` §8a (Challenge 8 safeguard):

> "Every advisory must display its confidence level."

**Gap:** Phase 1 does not include the Climate Engine, but the recommendation output format already requires a `confidence_note` field (`09-constraint-priority-engine.md` §4.2). Without a stub implementation in Phase 1, the confidence labeling requirement will be retrofitted rather than designed in. This is a forward-compatibility gap.

**Required todo:**
- Confidence metadata schema for Recommendation Bus (all fields in `09-constraint-priority-engine.md` §4.1 — `confidence_note` is already specified)
- Confidence label UI component (for IVR: spoken confidence; for WhatsApp: text confidence; for App: visual indicator)
- Phase 3 Climate Engine stub: income recommendations carry a `confidence_note: "income engine — high confidence"` placeholder

**Spec reference:** `09-constraint-priority-engine.md` §4.1, §4.2, §5.3

---

### 1.7 Ground Truth Data Collection Infrastructure for Phase 2/3 Readiness

**Spec basis:** `17-geography-pilot-demography.md` §4.3 (Data Collection During Pilot) explicitly states:

> "The pilot is not just a product validation — it is a ground truth data collection exercise that enables Phase 2 (Soil micro-zoning) and Phase 3 (Climate Engine district-level advisories)."

The document specifies eight data layers to collect, including soil self-assessment, weather outcomes, and crop yield data.

**Gap:** No todo covers the ground truth data collection infrastructure — the pipelines, storage, and validation workflows needed to accumulate Phase 2/3-ready data during Phase 1. Without this, Phase 2 Soil Engine integration starts without training data.

**Required todo:**
- Soil self-assessment data pipeline (paper form digitization, field agent input, storage)
- Weather outcome reporting workflow (farmer-reported extreme weather events)
- Crop yield data collection (field agent crop cut estimate + farmer self-report)
- Ground truth data governance (anonymization, retention, access controls per `17-geography-pilot-demography.md` §4.3)

**Spec reference:** `17-geography-pilot-demography.md` §4.3, lines 374-388

---

### 1.8 Extension Officer Notification System (Challenge 7 Safeguard)

**Spec basis:** `15-ground-challenges-practical-feasibility.md` §7a (Extension Integration safeguard):

> "When the CPE suppresses a recommendation for a farmer, generate a structured notification for the farmer's assigned extension officer: 'Your farmer [name] in [village] has a cash constraint active. Soil recommendation for zinc application is ready but suppressed. Suggested intervention: discuss short-term credit option or input subsidy scheme.'"

**Gap:** No todo covers the extension officer notification system. The suppression notification per farmer is in the CPE spec, but the extension officer briefing layer (per Challenge 7 safeguard) is not specified for implementation.

**Required todo:**
- Extension officer assignment model (which officer is assigned to which farmer — per `15-ground-challenges-practical-feasibility.md` §7a)
- Extension officer notification format (structured SMS or WhatsApp message)
- Suppression-to-notification pipeline (CPE suppression event → extension officer alert)

**Spec reference:** `15-ground-challenges-practical-feasibility.md` §7a, lines 195-200

---

## 2. CLOUDEST TODOS

### 2.1 "Build Multi-Channel delivery infrastructure"

**If such a todo exists:** This is too vague. Multi-channel delivery spans IVR, WhatsApp, SMS, USSD, App, and village agents — each with fundamentally different technical stacks, content formats, and user interaction patterns. Per `06-delivery-channels.md`, the channel architecture is distinct per channel.

**Required clarification:**
- Which channels are Phase 1? (IVR + WhatsApp + field agents per `17-geography-pilot-demography.md` §4.2 channel priorities)
- What is the offline-first requirement for each channel?
- What is the content format per channel?

**Recommendation:** Break into channel-specific todos with explicit scope.

---

### 2.2 "Implement CPE gates"

**If such a todo exists:** "Implement CPE gates" covers 5 distinct gates with different logic, data dependencies, and suppression behaviors. Gate 1 (Health) and Gate 3 (Cash Flow) have external data dependencies (health status self-report, obligation calendar). Gate 2 (Tenure) requires land tenure data. Gate 4 (Selling Window) requires harvest date tracking. Gate 5 (Time Criticality) requires crop calendar integration.

**Required clarification:**
- Which gates are Phase 1 (Gate 2 is specified as Phase 2 per `09-constraint-priority-engine.md` §5.2)?
- What triggers each gate's constraint state update?
- What is the suppression notification format per gate?

**Recommendation:** Break into gate-specific todos with explicit data dependency mapping.

---

### 2.3 "Farmer enrollment"

**If such a todo exists:** Farmer enrollment spans onboarding, constraint state data collection, consent collection, and SHG linkage for women farmers. The enrollment process for a tenant farmer in Ahmednagar (Gate 2 relevance) vs. an owner-cultivator in Dharwad requires different data collection priorities.

**Required clarification:**
- What data is collected at enrollment vs. during the crop cycle?
- What is the enrollment channel (field agent app, IVR, or both)?
- What is the enrollment consent workflow per `08-farmer-identity.md`?

**Recommendation:** Break into enrollment workflow todos with channel-specific variants.

---

## 3. WRONG SCOPE

### 3.1 B2B2F Revenue Model Infrastructure Pulled Into Phase 1

**Spec basis:** `07-institution-integration.md` describes the B2B institution integration platform, API architecture, partner onboarding, and revenue model. The journal entry `0013-DISCOVERY-gtm-four-stakeholders-revenue-model.md` explicitly states:

> "The answer is likely yes in Phase 1-2, but uncertain at Phase 3-4 scale." [revenue from institutional partners]

**Issue:** If the todo decomposition includes institution API infrastructure, partner dashboards, or SDK packages from `07-institution-integration.md`, these are Phase 2+ work. Phase 1 revenue is institutional partnerships (FPO, RRB, KVK) — not the technical infrastructure for charging institutions.

**Correct Phase 1 scope:**
- Institutional partnership agreements (MOUs with NABARD, FPOs, KVKs)
- Field agent deployment for farmer enrollment
- B2B2F pilot validation with 1-2 anchor institutions

**Phase 2 scope:**
- Institution API and SDK
- Partner dashboard
- Revenue tracking

---

## 4. PHASE 2+ LEAKAGE

### 4.1 Soil Micro-Zoning Infrastructure in Phase 1

**Spec basis:** `09-constraint-priority-engine.md` §5.2 (Phase 2: Income + Soil Micro-Zoning):

> "Soil Engine publishes recommendations to the Recommendation Bus. Soil Engine is constrained to micro-zoning (farmer self-assessment) and season-level interventions — NOT multi-year soil health plans."

**Issue:** If soil micro-zoning data collection, soil recommendation engine, or Soil Engine → Recommendation Bus integration appears in Phase 1 todos, this is Phase 2 leakage.

**Correct Phase 1 scope:** Soil self-assessment data collection (form design, field agent input) as ground truth infrastructure for Phase 2. The Soil Engine itself belongs in Phase 2.

---

### 4.2 Climate Engine Any-District Infrastructure in Phase 1

**Spec basis:** `09-constraint-priority-engine.md` §5.3 (Phase 3: Add Climate Engine at District Level):

> "Climate Engine publishes district-level advisories (not plot-level — plot-level requires ground truth that does not yet exist)."

**Issue:** Any Climate Engine infrastructure in Phase 1 todos is Phase 3 leakage. The exception is the confidence labeling stub (Gap 1.6 above), which is a Phase 1 forward-compatibility task.

**Correct Phase 1 scope:** Weather data API integration (for display only, not for recommendations). Confidence metadata stub on Income Engine recommendations.

---

### 4.3 Full Agristack Integration in Phase 1

**Spec basis:** `08-farmer-identity.md` §7.1 (Agristack Integration):

> "Once Agristack APIs are available and stable: 1. Read-only access to farmer and land data..."

**Issue:** Agristack is in pilot stage, APIs are unstable, and the 2022 data breach (140M farmer records) makes aggressive integration risky. Full Agristack integration belongs in Phase 3+.

**Correct Phase 1 scope:** Platform's own farmer graph with internal UUID. PM-KISAN ID linkage (where available). Aadhaar hash only (never raw Aadhaar). Land record self-report with field agent attestation.

---

## 5. MISSING DEPENDENCIES

### 5.1 Obligation Calendar → Cash Flow Status → Gate 3

**Dependency chain:**
1. Farmer-reported obligation calendar collected at onboarding (Gap 1.2 above)
2. Cash flow status computation updated to incorporate obligation calendar (not just Income Module 2 inference)
3. Gate 3 suppression logic uses the updated cash flow status

**Issue:** If any of these three steps are in different todos with incorrect sequencing, the obligation calendar safeguard (Challenge 5) breaks.

**Required sequencing:** Obligation calendar data model → obligation collection workflow → cash flow status integration → Gate 3 recalibration with obligation-adjusted cash flow.

---

### 5.2 Farmer Identity → Consent Collection → Data Access → Institution Integration

**Dependency chain:**
1. Farmer identity model (per `08-farmer-identity.md` §2)
2. Consent collection infrastructure (per `08-farmer-identity.md` §3)
3. Privacy engine access checks (per `08-farmer-identity.md` §5.2)
4. Institution integration API (Phase 2)

**Issue:** Institution integration cannot begin without farmer consent infrastructure. If institution API todos appear before consent infrastructure todos, the B2B2F revenue model will ship without a functional consent layer — a legal and trust risk.

**Required sequencing:** Farmer identity core → consent collection → privacy engine → institution API.

---

### 5.3 Crop Calendar → Time Criticality → Gate 5

**Dependency chain:**
1. Crop cycle data model (per `01-domain-model.md` §3)
2. Crop cycle dates collection (sowing date, expected harvest date)
3. Time criticality derivation (sowing_window, growing_window, harvest_window)
4. Gate 5 evaluation (suppress recommendations requiring multi-day action during sowing_window)

**Issue:** Gate 5 is a Phase 1 active gate per `09-constraint-priority-engine.md` §5.1, but it depends on crop calendar data that must be collected from farmers. If crop calendar collection is not a Phase 1 todo, Gate 5 cannot function.

**Required sequencing:** Crop cycle data model → field agent collection workflow → time criticality derivation → Gate 5 activation.

---

### 5.4 Women Farmer Channel Design → Women Farmer Enrollment Target

**Dependency chain:**
1. Women-farmer IVR workflow design (Gap 1.1 above)
2. SHG partnership agreements (Gap 1.1 above)
3. Female field agent deployment (Gap 1.1 above)
4. Women farmer enrollment tracking (Gap 1.1 above)

**Issue:** The 30% women farmer enrollment target (`17-geography-pilot-demography.md` §3.3) cannot be achieved without the three upstream dependencies. If women farmer enrollment appears as a metric without the channel design and partnership todos, it will fail.

**Required sequencing:** IVR workflow + SHG partnership + female agents → enrollment tracking.

---

## 6. SUMMARY TABLE

| Gap ID | Category | Priority | Spec Basis | Blocks |
|--------|----------|----------|-----------|--------|
| 1.1 | Missing | CRITICAL | `17-geography-pilot-demography.md` §3.3 | Women farmer 30% target |
| 1.2 | Missing | CRITICAL | `15-ground-challenges-practical-feasibility.md` §5b | Gate 3 accuracy |
| 1.3 | Missing | HIGH | `09-constraint-priority-engine.md` §3.1, §10.1 | Gate 1 emergency path |
| 1.4 | Missing | HIGH | `08-farmer-identity.md` §9.1 | Legal compliance |
| 1.5 | Missing | HIGH | `09-constraint-priority-engine.md` §5.1 | Pilot success metrics |
| 1.6 | Missing | MEDIUM | `09-constraint-priority-engine.md` §4.1, §5.3 | Phase 3 compatibility |
| 1.7 | Missing | MEDIUM | `17-geography-pilot-demography.md` §4.3 | Phase 2 Soil Engine |
| 1.8 | Missing | MEDIUM | `15-ground-challenges-practical-feasibility.md` §7a | Extension integration |
| 2.1-2.3 | Cloudy | HIGH | `06-delivery-channels.md`, `09-constraint-priority-engine.md` | Implementation |
| 3.1 | Wrong Scope | MEDIUM | `07-institution-integration.md` | Phase 2 revenue model |
| 4.1 | Phase 2 Leakage | MEDIUM | `09-constraint-priority-engine.md` §5.2 | Phase 2 Soil Engine |
| 4.2 | Phase 3 Leakage | LOW | `09-constraint-priority-engine.md` §5.3 | Phase 3 Climate |
| 4.3 | Phase 3+ Leakage | MEDIUM | `08-farmer-identity.md` §7.1 | Legal risk |
| 5.1-5.4 | Missing Dependencies | CRITICAL | All specs | Core CPE function |

---

## 7. RECOMMENDED SUPPLEMENTARY TODO FILES

The following missing todos should be created as separate todo files:

### `01-women-farmer-implementation.md`
- SHG partnership framework
- Women-farmer IVR workflow design
- Female field agent deployment plan
- Women farmer enrollment tracking

### `02-obligation-calendar.md`
- Obligation calendar data model
- Onboarding collection workflow
- Cash flow status integration

### `03-emergency-credit-pathway.md`
- Emergency credit product design
- NABARD/RRB partnership
- Liability framework
- Gate 1 emergency credit metadata

### `04-dpdp-consent-infrastructure.md`
- Consent collection infrastructure
- Data principal rights workflow
- Breach notification system

### `05-cpe-gate-monitoring.md`
- Gate accuracy telemetry
- False suppression rate dashboard
- Ground truth validation protocols

### `06-ground-truth-data-pipeline.md`
- Soil self-assessment pipeline
- Weather outcome reporting
- Crop yield data collection

### `07-extension-officer-notification.md`
- Extension officer assignment model
- Structured notification format
- Suppression-to-notification pipeline

---

*Gap analysis prepared from: `briefs/01-user-brief.md`, `specs/09-constraint-priority-engine.md`, `01-analysis/15-ground-challenges-practical-feasibility.md`, `01-analysis/17-geography-pilot-demography.md`, `journal/0013-DISCOVERY-gtm-four-stakeholders-revenue-model.md`, `specs/01-domain-model.md`, `specs/06-delivery-channels.md`, `specs/07-institution-integration.md`, `specs/08-farmer-identity.md`*
