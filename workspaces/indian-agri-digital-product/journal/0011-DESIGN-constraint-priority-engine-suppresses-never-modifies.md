---
name: 0011-DESIGN-constraint-priority-engine-suppresses-never-modifies
description: Key design decision: CPE suppresses recommendations that violate constraints; it never modifies recommendations
metadata:
  type: DESIGN
---

# DESIGN: Constraint Priority Engine — Suppresses, Never Modifies

## The Decision

The Constraint Priority Engine is a **gate-based filter** — it suppresses recommendations that violate the farmer's current constraints. It does not modify, rank, score, or re-prioritize recommendations. A recommendation that cannot be acted on given the farmer's current health status, tenure security, cash flow, and timing constraints is simply not shown.

## Why Suppress Over Modify

The alternative — the CPE scores each recommendation against constraints and presents a modified recommendation ("instead of organic fertilizer, use half the urea") — was rejected for three reasons:

**1. Modified recommendations are still wrong.**
If a tenant farmer cannot invest in multi-year soil health, telling them to "do a cheaper version" does not solve the problem. The cheaper version still requires cash the farmer does not have. Suppression is honest; modification is misleading.

**2. Modification requires the CPE to understand the recommendation domain.**
To modify a Soil Engine recommendation, the CPE would need to understand NPK ratios and fertilizer chemistry. To modify a Climate Engine recommendation, it would need to understand phenology. The CPE would become a super-engine that understands all three domains — exactly what the modular architecture was designed to avoid.

**3. Suppression preserves trust.**
A farmer who receives a recommendation they cannot follow loses trust in the platform. A farmer who receives no recommendation (because the CPE suppressed it) but receives a suppression notification ("we have soil advice, but right now cash is your constraint") trusts the platform to understand their situation.

## The Five Gates

The CPE runs five gates in strict priority order. This ordering is not arbitrary — it reflects the binding nature of each constraint in the farmer's decision space:

1. **Health Gate (Priority 1):** A household with a medical emergency is not making agricultural decisions. Nothing else matters until health is resolved.

2. **Tenure Gate (Priority 2):** A tenant farmer cannot recover the residual value of soil investments. Multi-year recommendations are structurally unavailable to them.

3. **Cash Flow Gate (Priority 3):** Capital-intensive recommendations require cash. If cash is not available, capital-intensive recommendations are not actionable.

4. **Selling Window Gate (Priority 4):** During harvest, the immediate financial transaction takes priority over future planning.

5. **Time Criticality Gate (Priority 5):** Within critical crop windows (sowing, harvest), only recommendations that fit the window timeline pass.

## One Recommendation At A Time

When multiple recommendations pass all gates, the CPE issues them in priority order by crop cycle phase:
- Sowing window: Climate Engine recommendation
- Growing window: Soil Engine recommendation
- Harvest window: Income Engine recommendation

But this ordering is secondary to the gate system. If Gate 3 fires, nothing else matters regardless of crop cycle phase.

## Source

`specs/09-constraint-priority-engine.md`
