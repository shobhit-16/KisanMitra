---
name: 0013-DISCOVERY-gtm-four-stakeholders-revenue-model
description: Four stakeholder collaborations form the GTM core; revenue model must stay institutional not farmer
metadata:
  type: DISCOVERY
date: 2026-05-20
created_at: 2026-05-20T15:30:00+05:30
author: agent
session_id: 24b211f3-1394-4baa-8bbf-005fbaea9dae
project: indian-agri-digital-product
topic: GTM strategy — four high-impact collaborations and B2B2F tension
phase: analyze
tags: [gtm, stakeholder, nabard, fpo, kvk, state-agriculture-dept, revenue-model]
---

# DISCOVERY: Four Stakeholder Collaborations Form the GTM Core

## The Finding

The GTM analysis evaluated 10 stakeholder categories and converged on **4 high-impact collaborations** that together form the GTM core:

### Top 4 (In Priority Order)

1. **NABARD / RRB System** — highest leverage on farmer financial access (the binding constraint per CPE Gate 3)
2. **State Agriculture Department** — highest leverage on farmer adoption reach (Krishi Mitra network + government credibility)
3. **FPOs** — highest leverage on farmer organizing and collective power (farmers who are organized can actually act on recommendations)
4. **KVK Network** — highest leverage on agronomic credibility and ground truth validation

### Why These Four Specifically

**NABARD/RRB first:** The CPE identifies cash flow as the binding constraint (Gate 3). NABARD and the RRB system are the single largest institutional channel for agricultural credit in India. A working relationship with NABARD means the platform's constraint-state data directly informs credit allocation decisions that determine whether a farmer can act on any other recommendation.

**State Agriculture Department second:** The Krishi Vibhag has field staff (Krishi Mitras) in every block who interact with farmers regularly. Government endorsement provides the credibility signal that overcomes initial farmer skepticism. No private sales force can replicate this reach.

**FPOs third:** An FPO that uses the platform for member services creates proof points that are legible to policymakers and to other FPOs. FPO-organized farmers have more agency than isolated smallholders — they can actually act on platform recommendations (collective transport to mandis, pooled input procurement).

**KVK fourth:** KVKs are the only institutional actor with the mandate and capability to validate the platform's agronomic recommendations. Without KVK validation, the platform is a guessing machine. With KVK validation, it has a scientifically defensible evidence base.

## The B2B2F Tension — Navigable But Not Solvable by Design Alone

The revenue model (institutional partners pay, farmers receive free access) creates structural pressure to soften platform findings. The CPE's "suppresses, never modifies" architecture provides the technical defense — but the GTM analysis reveals the B2B2F tension requires **explicit deal structures**, not just good intentions:

**The specific risk:** Institutional partners (input companies, insurance companies, credit providers) may want the platform to suppress findings that threaten their commercial interests — or worse, to use the platform as a marketing channel to push their products.

**The defense:**
1. **CPE is technically non-negotiable** — embedded in every MoU structure, not a promise but a technical fact
2. **Revenue relationships are structured as aggregate data analytics** (portfolio risk for RRBs, research collaboration for KVKs) — not individual farmer data access
3. **No recommendation interference clause** in every MoU — explicit prohibition on using the platform as enrollment machinery or product marketing channel

## The Institutional vs. Farmer Revenue Model Question

The analysis raises a structural question: can the platform sustain operations on institutional revenue alone (FPO subscriptions, NABARD data agreements, KVK research partnerships) without ever charging farmers?

**The answer is likely yes in Phase 1-2, but uncertain at Phase 3-4 scale.** The cost model for 50,000 farmers with field agents and IVR infrastructure requires significant institutional revenue. The risk is that institutional revenue at scale creates leverage for the partners who provide it — which is why the MoU structure and the CPE technical non-negotiable are load-bearing.

## For Discussion

1. **Counterfactual:** What happens to the GTM if NABARD partnership takes 24 months instead of 12? (The pilot would need to run on FPO and KVK revenue alone, which is insufficient for field-agent-scale operations.)

2. **Implication:** Every MoU with an institutional partner must include the CPE non-negotiable clause and the no-recommendation-interference clause before the agreement is signed. Is the team prepared to walk away from a revenue relationship if the partner won't accept these terms?

3. **Open question:** How should the platform handle the situation where an RRB uses platform data to deny credit to a distressed farmer (explicitly against the MoU terms) but the platform has no audit rights to detect it?
