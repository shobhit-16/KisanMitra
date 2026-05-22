---
name: 0010-DISCOVERY-cross-framework-constraint-priority-is-the-missing-core
description: The binding constraint priority problem — not which engine, but which constraint wins
metadata:
  type: DISCOVERY
---

# DISCOVERY: Constraint Priority Is the Missing Core Architecture

## What I Found

The three individual red team reports (Income, Climate, Soil) each identified critical gaps within their engine. The cross-framework synthesis reveals a gap that is more fundamental than any single engine: **there is no constraint priority engine**.

When all three engines fire simultaneously — which is the common case for a farmer under financial stress — they issue recommendations that directly contradict each other. The Soil Engine recommends investing in balanced fertilization. The Income Engine detects urgent cash need and recommends selling now. The Climate Engine recommends delaying sowing. The farmer has enough cash for fertilizer OR transport to a better mandi — not all three.

None of the three engines knows about the others' constraints. More critically, there is no architectural layer that ranks which constraint takes precedence when constraints conflict.

## Why This Matters

This is not a missing feature. It is a missing core architecture. The Farmer OS as currently specified assumes the three engines are complementary modules. In practice, they are competing recommendation systems with no arbitration mechanism.

The farmer who most needs the platform (distressed, cash-constrained, tenant farmer with health shock exposure) is the farmer who will receive the most contradictory recommendations — and who will lose trust fastest.

## The Health Shock Is the Binding Constraint

Across all three engines, health shock emerges as the binding constraint that none of them model. A household medical emergency:

- Triggers Income Engine's "urgent cash need" detection
- Makes Soil Engine's input investment recommendations irrelevant (cash not available)
- Prevents Climate Engine's "delay sowing" recommendation from being actionable
- Converts the platform from decision support into noise

The platform needs a health status gate that suppresses all investment and timing recommendations when household health status = crisis.

## The B2B2F Tension Is the Second Unresolved Gap

All three engines will face pressure to soften findings that harm institutional partners. Input companies want more fertilizer recommendations, not optimized ones. Financial institutions want to expand lending, not be told emergency credit fails distressed borrowers. Insurance agents want enrollment, not basis risk disclosure.

The B2B2F revenue model requires intermediaries. The product efficacy requires disrupting intermediary information monopolies. These requirements are in direct conflict.

## Implications

1. **Build the constraint priority engine before any module integration.** It must be platform-level, not engine-level.

2. **Health shock detection needs to be a constraint gate, not a module.** It suppresses recommendations across all engines.

3. **The platform should launch as Income-only, stripped down**, not as a comprehensive Farmer OS. The other engines require infrastructure that doesn't exist yet.

4. **Ground truth collection must be platform-level infrastructure**, shared across all three engines, with a dedicated budget.

## Source

Cross-framework synthesis at `01-analysis/14-cross-framework-redteam.md`
