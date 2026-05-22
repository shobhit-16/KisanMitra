# GTM Strategy: Public-Good Agricultural Digital Platform

**Date:** 2026-05-20
**Author:** Analysis Specialist
**Classification:** Internal Strategy

---

## Executive Summary

The platform's revenue model — institutional partners pay, farmers receive free access — creates a structural tension that shapes every stakeholder relationship. The CPE suppresses recommendations that violate binding farmer constraints; institutional partners may pressure for softened findings. Successful GTM depends on selecting partners whose incentives genuinely align with farmer welfare, and structuring engagement terms that make deviation from farmer-first principles costly.

**Complexity: Moderate** — ten distinct stakeholder categories, each with different value frames, engagement timelines, and risk profiles. The B2B2F tension is navigable but requires explicit deal structures, not informal partnerships.

---

## Stakeholder Analysis

### a) State Agriculture Department — Krishi Vibhag, Krishi Mitras, PACS

#### Value Proposition
- **Access to real-time farmer decision data** without survey overhead — the platform surfaces what farmers are deciding, not just what schemes they enrolled in
- **Scheme delivery amplification** — Soil Health Card distribution, PM KISAN enrollment, and FPO formation targets are easier to hit when Krishi Mitras have a tool that makes schemes legible to farmers
- **Political visibility** — department leadership can show digital penetration metrics that are easy to report upward

#### Engagement Model
Direct engagement with the state agriculture minister and the relevant Mission Director (often for Digital Agriculture missions). Requires a pilot district with measurable outcomes before state-wide scaling.

Onboarding: 3–6 month pilot with 1–2 blocks, 1,000–5,000 farmers. Krishi Mitras receive the platform as a field tool; PACS officers receive aggregate lending-risk insights.

#### Collaboration Terms
- **Data sharing**: Platform receives GPS-validated plot boundaries, soil health card data, crop cutting experiment results. Department receives anonymized farmer decision-pattern analytics
- **No recommendation interference**: The CPE suppresses recommendations based on farmer constraint state — not government scheme enrollment targets. This is non-negotiable and must be in the MoU
- **Co-branding**: Department gets visibility in the farmer-facing app ("Supported by Department of Agriculture, [State]") — this is high-value credibility for farmer adoption
- **Scheme integration API**: Platform can surface scheme eligibility — this is additive, not a replacement for department's own portals

#### Risks
- **Political capture**: A new minister may deprioritize digital agriculture and withdraw support. Mitigation: build district-level institutional champions (DAO, Block Agricultural Officer) who persist through political cycles
- **Data demand escalation**: Department may request farmer-level identifiable data for surveillance or targeting. This must be contractually blocked — anonymized aggregates only
- **Scheme enrollment pressure**: Department may want the platform to push enrollment in specific schemes regardless of farmer fit. This is the B2B2F tension in its sharpest form. The CPE suppresses inappropriate recommendations; the MoU must explicitly prohibit using the platform as enrollment machinery

---

### b) Agriculture Universities & KVKs (Krishi Vigyan Kendra)

#### Value Proposition
- **Research data pipeline** — KVKs conduct Frontline Demonstrations (FLDs) and On-Farm Trials (OFTs). Platform farmers generate ground-truth observations that validate (or challenge) university recommendations at scale
- **Extension reach** — KVK scientists can publish advisories through the platform to a farmer base far larger than their direct contact network
- **Curriculum integration** — B.Sc. Agriculture students can use the platform as a field training tool; university gains a technology-forward positioning

#### Engagement Model
Engage the Vice-Chancellor of the state agricultural university and the KVK network coordinator (typically a Deputy Director of Agriculture at district level). Start with one KVK as a knowledge-partner — they validate the platform's agronomic recommendations against their own trial data.

Onboarding: 6–12 months. KVK scientists get a researcher dashboard; platform farmers receive KVK-validated advisories.

#### Collaboration Terms
- **Mutual validation**: KVK shares FLD/OFT results for platform-relevant crops and geographies. Platform shares anonymized farmer-reported outcomes ("farmers who received this recommendation — 73% reported yield improvement")
- **Joint research publications**: When platform data validates a KVK finding, co-authorship on research papers
- **No exclusive arrangement**: KVK scientists remain free to work with other platforms and private companies — alignment is intellectual, not contractual exclusivity

#### Risks
- **Academic bureaucracy**: University technology transfer offices can slow agreements. Mitigation: frame as research collaboration, not commercial licensing
- **Recommendation divergence**: KVK recommendations may lag behind platform's real-time advisories. The CPE gates recommendations appropriately — KVK is one input, not the authority
- **Credibility transfer**: If platform issues a recommendation that KVK later contradicts, farmer trust fractures. Mitigation: explicit confidence labeling on every advisory ("KVK-verified" vs "platform-estimated")

---

### c) FPOs (Farmer Producer Organizations)

#### Value Proposition
- **Member services differentiation**: FPOs compete for members. A digital advisory tool that demonstrably improves member incomes is a retention lever
- **Collective marketing intelligence**: The platform's multi-mandi price visibility (Income Engine Module 3) helps FPO leadership negotiate better terms for collective sales
- **Input procurement leverage**: Soil health data aggregated across FPO members can be used to negotiate better prices for balanced fertilizer procurement

#### Engagement Model
Engage the CEO and board of the FPO. FPOs are legally registered entities — formal MoU is straightforward. Pilot with one FPO that has an active CEO driving member services.

Onboarding: 3–6 months. FPO receives a dashboard aggregating its members' constraint states and market access data. Individual farmers receive personal advisories.

#### Collaboration Terms
- **FPO as institutional subscriber, not farmer**: The FPO pays a nominal institutional subscription (Rs 500–2,000/month for up to 500 members). Revenue is institutional — this is the model working correctly.
- **Aggregate data stays with FPO**: The platform does not sell or share member-level data to third parties. The FPO's own aggregated analytics are the FPO's property
- **Board-level reporting**: Quarterly report to FPO board showing member income outcomes, input cost savings, and market price realization vs non-member peers

#### Risks
- **FPO capture by middlemen**: Some FPO board members have conflicts of interest with input dealers or arthiyas. If the platform surfaces information that threatens those interests, board support may withdraw. Mitigation: build direct relationships with farmer-members through the app, not just FPO leadership
- **Digital literacy variance**: FPO members vary widely in smartphone access. The IVR channel and field agent-assisted onboarding are critical for FPOs with low digital penetration
- **FPO financial instability**: Many FPOs are financially weak and may default on subscription. Mitigation: start with FPOs that have active bank credit relationships (BCR norm)

---

### d) Agripreneurs / Rural Entrepreneurs

#### Value Proposition
- **Business tool**: Agripreneurs (custom hiring centres, cold storage operators, input dealers, aggregation agents) use the platform to offer better services to their farmer customers
- **Commission-free advisory**: Unlike input companies that push their own products, the platform's recommendations are constraint-gated and product-agnostic — agripreneurs can differentiate by offering honest advice
- **Customer acquisition**: Farmers who use the platform and have a good experience ask their local agripreneur for help — this is organic reach

#### Engagement Model
Open access model with a premium tier. Agripreneurs self-register. The free tier gives basic advisories; the premium tier (Rs 99–299/month) gives advanced market intelligence and multi-FPO coordination tools.

Onboarding: Self-serve with in-app tutorial. Support via WhatsApp and phone helpline.

#### Collaboration Terms
- **No exclusivity**: Agripreneurs remain free to sell any products; the platform does not take commission on sales
- **Referral programme**: Agripreneurs who bring farmers to the platform receive a revenue share on institutional contracts for those farmers (e.g., if a bank extends credit to a referred farmer, the agripreneur gets Rs 50)
- **Quality covenant**: Agripreneurs who use the platform to mislead farmers (e.g., misinterpreting recommendations to push their own inventory) are suspended

#### Risks
- **Channel conflict**: Agripreneurs may feel the platform competes with their business if it offers direct farmer services (e.g., direct market linkage). Mitigation: position the platform as infrastructure that makes agripreneurs more effective, not a replacement
- **Misinformation amplification**: An agripreneur with a large farmer network could propagate incorrect interpretations of platform recommendations. Mitigation: every recommendation carries explicit confidence labeling; the CPE suppresses inappropriate recommendations at source
- **Subscription churn**: Agripreneurs in low-margin businesses may cancel when they don't see immediate ROI. Mitigation: free tier with enough value to demonstrate benefit before asking for payment

---

### e) Cooperatives (IFFCO, NAFED, State Cooperatives)

#### Value Proposition
- **Member engagement tool**: Cooperatives compete with private input retailers for farmer loyalty. A digital advisory tool that improves member outcomes is a membership benefit
- **Supply chain planning**: Aggregate soil health and crop意向 data across members helps cooperatives plan input procurement and storage capacity
- **Compliance with cooperative law**: Many cooperatives are required to provide extension services to members — the platform provides a verifiable delivery mechanism

#### Engagement Model
Engage at the state federation level (e.g., IFFCO's state offices, NAFED's district federations) and through Primary Agricultural Credit Societies (PACS) at village level. State-level engagement unlocks PACS access.

Onboarding: 12–18 months for state-level federation MoU; 3–6 months for individual PACS.

#### Collaboration Terms
- **Institutional subscription**: Cooperative federation pays an institutional license. Individual PACS receive free access as a member service
- **Bulk data integration**: Platform integrates with cooperative ERP systems for input offtake data and output sale data — validates platform price recommendations against actual transaction prices
- **Board representation**: One seat on the platform's farmer advisory board (non-voting) — gives cooperatives visibility into recommendation logic without control

#### Risks
- **Bureaucratic timelines**: Cooperative federations have multi-layer approval processes. Mitigation: start with individual PACS that are more agile, demonstrate results, then use as a reference for federation engagement
- **Political interference**: State cooperative elections change leadership and priorities. Mitigation: institutionalize the partnership at the staff level (MD/CEO), not just political appointee level
- **Competitive sensitivity**: cooperatives may be reluctant to share member transaction data. Mitigation: anonymized aggregates for planning; identifiable data only with explicit farmer consent and only for the specific purpose

---

### f) Regional Rural Banks (RRBs) and NABARD

#### Value Proposition
- **Risk assessment data**: RRBs lend to farmers with limited formal credit history. The platform's constraint state (cash flow status, health status, tenure type) gives RRBs a forward-looking view of farmer repayment capacity that formal credit scoring misses
- **Reduced NPAs**: Farmers who receive timely selling recommendations and climate advisories are less likely to default. NABARD has a direct interest in reducing agricultural NPA rates across the RRB system
- **Priority sector lending targets**: NABARD requires RRBs to meet priority sector lending targets for agriculture. The platform's farmer base is a pre-screened pool for agricultural credit

#### Engagement Model
NABARD is the entry point — its Department of Agricultural Finance has influence over RRB priorities. Engage NABARD's Compendium cell and the RRB Credit cell. A successful pilot with one RRB in one district demonstrates the model.

Onboarding: 12–18 months for NABARD-level MoU; 6–12 months for individual RRB pilot.

#### Collaboration Terms
- **Risk-sharing data**: Platform provides anonymized, aggregated constraint-state distributions for RRB service areas. Individual farmer data is NOT shared — RRBs assess risk at the portfolio level
- **No credit product recommendations**: The platform's Income Engine Module 5 identifies emergency credit pathways only for genuine distress (health shock, cash emergency) — not as a general credit marketing tool
- **NABARD refinance linkage**: Platform helps identify farmers eligible for NABARD refinance windows — this is additive value, not a substitute for RRB's own credit assessment
- **Periodic impact assessment**: NABARD receives annual impact data on NPA rates, loan utilization, and farmer income in platform-covered areas vs controls

#### Risks
- **Data misuse for credit denial**: RRBs may use platform data to deny credit to already-distressed farmers. This is the inverse of the intended effect — the CPE gates investment recommendations for distressed farmers, not credit access. Mitigation: contractual prohibition on using platform data for credit denial decisions; platform data is for portfolio risk management, not individual credit decisions
- **Conflicting incentive on insurance**: NABARD is a major crop insurance player. If the Climate Engine surfaces basis risk (as documented in the cross-framework redteam), this conflicts with insurance enrollment goals. Mitigation: platform surfaces basis risk information to farmers directly, not to NABARD — the farmer makes the informed choice
- **NPA targeting pressure**: RRBs under NPA pressure may want the platform to push farmers toward loans that benefit the bank's balance sheet rather than the farmer's income. The CPE does not recommend financial products for farmers in emergency cash status — this must be contractually explicit

---

### g) NBFCs Working in Agriculture (Samhita, Ayeza, etc.)

#### Value Proposition
- **Alternative credit scoring**: NBFCs serving smallholder farmers lack formal credit history. The platform's constraint-state data (cash flow patterns, health status, tenure security) provides a forward-looking view of repayment capacity
- **Loan utilization monitoring**: Farmers who receive platform advisories use loans for intended productive purposes at higher rates — reduces diversion risk
- **Client retention**: NBFC field officers equipped with platform insights provide better farmer service, improving client retention and collection efficiency

#### Engagement Model
Direct engagement with NBFC leadership — these are typically Series B+ companies with clear commercial mandates. A pilot with 500–1,000 farmers who are existing NBFC clients demonstrates the model.

Onboarding: 6–12 months for commercial agreement.

#### Collaboration Terms
- **Commercial data agreement**: NBFC pays for access to anonymized, aggregated farmer constraint-state distributions in their service areas. Individual farmer data is never shared without explicit consent
- **Field officer tool**: NBFC's field officers receive a simplified dashboard showing client constraint states — helps them time visits and collections appropriately
- **No recommendation interference**: NBFC does not have the right to ask the platform to suppress or modify recommendations for their clients. The CPE is non-negotiable

#### Risks
- **Adverse selection**: NBFCs may use platform data to cherry-pick low-risk farmers, leaving high-risk farmers without credit access. Mitigation: aggregate data only; individual-level data sharing contractually prohibited for underwriting decisions
- **Data sale to third parties**: NBFC may sell or share the anonymized aggregate data further. Mitigation: contractually prohibit re-sale; platform retains audit rights
- **Mission drift pressure**: NBFCs with high yield targets may pressure the platform to soften cash flow assessments (make distressed farmers look creditworthy). The CPE has no mechanism for this — it suppresses, never modifies. This must be contractually explicit

---

### h) Civil Society Organizations and NGOs (WWF, Oxfam, WWF-India)

#### Value Proposition
- **Program monitoring tool**: NGOs running agricultural development projects use the platform to monitor farmer outcomes at lower cost than surveys
- **Advocacy credibility**: An independent digital platform provides credible data for policy advocacy — NGOs can cite platform findings without the perception of self-reported data
- **Farmer network access**: NGOs with established field presence can accelerate platform adoption in remote areas without digital infrastructure

#### Engagement Model
Engage with large international NGOs (Oxfam India, WWF-India) and domestic rural development NGOs (PRADAN, SEW). Frame as a public-good infrastructure, not a commercial product.

Onboarding: 3–12 months depending on NGO's internal approval processes.

#### Collaboration Terms
- **Free institutional access**: NGOs receive free institutional subscriptions for their field staff and program beneficiaries — this is consistent with the revenue model (institutions pay, farmers receive)
- **Data contribution**: NGO field programs contribute anonymized farmer outcome data back to the platform — a mutually beneficial data exchange
- **Joint advocacy**: Platform and NGO jointly publish annual "State of Smallholder Agriculture" reports using platform data and NGO field insights

#### Risks
- **Political sensitivity**: Some NGOs work in states with hostile governments. Association with international NGOs may create political complications. Mitigation: emphasize the Indian institutional ownership of the platform and compliance with all applicable regulations
- **Donor-driven priorities**: NGO programs are often donor-driven. If a donor changes priorities, the NGO's engagement with the platform may lapse. Mitigation: institutionalize the partnership at the program level, not the donor-grant level
- **Advocacy conflicts**: An NGO may use platform data in ways that embarrass government partners or institutional partners. Mitigation: joint publication agreements require mutual consent before public release

---

### i) Think Tanks and Policy Labs (NITI Aayog, ICRIER, CSISA)

#### Value Proposition
- **Policy research data**: Platform generates de-identified, large-scale data on farmer decision-making, input use, and market access — unprecedented for Indian agriculture policy research
- **Pilot validation**: Think tanks running agricultural policy pilots use the platform as a monitoring and evaluation partner — provides real-time outcome data without the lag of official surveys
- **Evidence-based advocacy**: The platform's findings (e.g., on fertilizer counterfeit rates, basis risk in crop insurance, arthiya margin structures) provide evidence for policy reform

#### Engagement Model
Engage through research partnerships and data access agreements. NITI Aayog is the apex — a MoU with NITI enables cross-sectoral data access and policy integration. ICRIER and other agriculture economists engage through research collaborations.

Onboarding: 12–18 months for formal MoU; faster for research partnerships (6 months).

#### Collaboration Terms
- **Research data access**: De-identified, aggregated platform data available to credentialed researchers under a Data Use Agreement. Individual farmer data is never accessible
- **Joint research publications**: Platform data combined with think tank analytical capacity produces research papers — co-authored with appropriate attribution
- **Policy briefs**: Platform analysis distilled into 2-page policy briefs for government circulation — think tanks provide the formatting and advocacy channel; platform provides the data

#### Risks
- **Data sensitivity**: Farmer decision data at scale is politically sensitive. Government may view it as a threat to agricultural information monopolies. Mitigation: emphasize the public-good framing and farmer-welfare orientation
- **Research independence**: Think tanks may face pressure to produce findings favorable to government or corporate partners. Mitigation: platform retains the right to publish independent findings; research agreements include data publication rights
- **Bureaucratic timelines**: Government MoU processes are slow. Mitigation: start with academic and NGO research partnerships that are faster to execute

---

### j) PPP Models (Digital Agriculture Missions, State-Level Initiatives)

#### Value Proposition
- **Scalable reach**: PPP models combine government mandate with private efficiency — the platform's technology infrastructure operated within a government framework
- **Funding bridge**: PPP structures can access government digital agriculture budgets that pure private platforms cannot
- **Institutional legitimacy**: A PPP-backed platform has the credibility of government with the agility of technology

#### Engagement Model
Engage with the Ministry of Agriculture & Farmers Welfare (MoA&FW) for central PPP frameworks and with state-level Digital Agriculture Missions for state-specific arrangements. The India Digital Ecosystem of Agriculture (IDEA) framework is the entry point.

Onboarding: 18–24 months for PPP framework agreements; faster for state-specific pilots (6–12 months).

#### Collaboration Terms
- **Technology partner structure**: Platform is the technology provider; government is the institutional partner. Government provides farmer access, scheme integration, and institutional credibility. Platform provides the CPE, recommendation engine, and farmer interface
- **Revenue split**: PPP arrangements typically require a revenue-sharing model. Negotiate for platform to receive per-farmer-per-month fee from government digital agriculture budget; institutional partner subscriptions continue to flow to platform directly
- **Data sovereignty**: All farmer data remains under government data sovereignty frameworks (India's upcoming Data Protection Act compliance). Platform processes data as a data fiduciary, not an owner

#### Risks
- **Bureaucratic capture**: PPP structures are susceptible to contractor capture — the private partner uses the government relationship to exclude competitors and extract rents. Mitigation: open architecture requirements in PPP contracts; platform must remain interoperable with other government systems
- **Mandate conflict**: Government may want the platform to serve scheme enrollment targets (e.g., PM-KISAN enrollment numbers) rather than farmer welfare. The CPE suppresses inappropriate recommendations regardless of government pressure — this must be technically embedded, not just contractually promised
- **Contractor instability**: PPP contracts are typically 3–5 years. If the platform loses the PPP contract, farmer trust is disrupted. Mitigation: maintain direct institutional relationships (FPOs, NGOs) as parallel channels that persist regardless of PPP status

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Institutional partner pressures platform to soften harmful findings | High | Critical | CPE suppresses, never modifies — technically non-negotiable; MoU clause prohibits interference |
| Farmer data used for credit denial or surveillance | Medium | Critical | Anonymized aggregates only; individual data sharing prohibited; audit rights retained |
| Government schemes weaponized through platform | Medium | Major | Scheme integration is additive — platform never pushes enrollment regardless of fit |
| PPP contractor capture | Medium | Major | Open architecture requirements; interoperability clauses |
| FPO/agripreneur misinformation amplification | Medium | Significant | Confidence labeling on all advisories; quality covenant enforcement |
| Political cycle disrupts government partnerships | High | Significant | Build district-level champions; institutionalize at staff level, not political level |
| B2B2F trust collapse from any single partner violation | Low | Critical | Partner code of conduct; escalation protocol; farmer-facing transparency reports |

---

## Top 4 High-Impact Collaboration Recommendations

### Recommendation 1: NABARD / RRB System — Highest Leverage on Farmer Financial Access

**Why this first:** Financial distress is the binding constraint documented in the CPE (Gate 3 — Cash Flow). NABARD and the RRB system are the single largest institutional channel for agricultural credit in India. A working relationship with NABARD means the platform's constraint-state data directly informs credit allocation decisions that determine whether a farmer can act on any other recommendation.

**Selection logic:**
- NABARD has a systemic incentive to reduce agricultural NPAs — platform-derived selling recommendations and cash flow assessments directly reduce default risk
- RRBs serve exactly the target population (smallholder farmers, <2 hectares) in exactly the geographies where the platform operates
- NABARD's mandate is farmer welfare — alignment is structural, not just rhetorical
- Unlike input companies or insurance providers, NABARD's revenue doesn't depend on farmer purchasing more products

**What to offer:** Anonymized aggregate constraint-state distributions at district/block level for RRB portfolio risk management. No individual farmer data. No credit marketing access.

**What to ask for:** NABARD endorsement as a "Digital Agriculture Partner" for RRB capacity building. Access to RRB field officer network for platform onboarding. Joint impact assessment of farmer income and NPA rates in platform-covered areas.

**Timeline:** 12 months to NABARD MoU; 6 months to first RRB pilot district.

---

### Recommendation 2: State Agriculture Department — Highest Leverage on Farmer Adoption Reach

**Why second:** The Krishi Vibhag has field staff (Krishi Mitras) in every block who interact with farmers regularly. Government endorsement provides the credibility signal that overcomes initial farmer skepticism of a digital tool. A department endorsement ("official digital agricultural companion") opens doors that no private sales force can.

**Selection logic:**
- State governments have Digital Agriculture Missions with dedicated budgets — PPP structures can access these
- Krishi Mitras are the only institutional actor with village-level presence — no other partner can reach the marginal farmer without a last-mile partner
- Department has statutory obligation to disseminate agricultural information — the platform provides the infrastructure for this mandate
- Unlike commercial partners, the department's primary accountability is farmer welfare (politically enforced)

**What to offer:** Free platform access for all department-verified farmers. Krishi Mitra app with simplified dashboard. Integration with existing department systems (soil health card portal, scheme eligibility engine).

**What to ask for:** Official endorsement ("Supported by Department of Agriculture"). Integration with department's farmer contact programmes. Access to department's farmer network data for platform onboarding.

**Timeline:** 6 months to pilot MoU in one district; 18 months to state-level framework agreement.

---

### Recommendation 3: FPOs — Highest Leverage on Farmer Organizing and Collective Power

**Why third:** FPOs are the institutional structure through which smallholder farmers can access markets, credit, and inputs at scale. An FPO that uses the platform for member services creates a proof point that is legible to policymakers (FPO board reports show income improvements) and to other FPOs (referral network effect).

**Selection logic:**
- FPO leadership is typically motivated by member welfare — alignment is genuine, not contractual
- FPO aggregate data (soil health, crop planning, market access) has commercial value that FPOs can capture — they become institutional subscribers who help fund the platform
- FPO-organized farmers have more agency than isolated smallholders — they can actually act on platform recommendations (collective transport to distant mandis, pooled input procurement)
- FPO scale (500–5,000 members per FPO) creates meaningful adoption metrics for PPP negotiations

**What to offer:** FPO dashboard aggregating member constraint states and market access data. Board-level quarterly impact reports. Institutional subscription model (Rs 1,000–5,000/month based on membership).

**What to ask for:** FPO promotes platform to members as official advisory tool. FPO shares anonymized member transaction data for platform validation. FPO board provides governance oversight of recommendation quality.

**Timeline:** 3 months to first FPO MoU; 12 months to 10-FPO network.

---

### Recommendation 4: KVK Network — Highest Leverage on Agronomic Credibility and Ground Truth

**Why fourth:** KVKs are the only institutional actor with the mandate and capability to validate the platform's agronomic recommendations. Without KVK validation, the platform is a guessing machine that looks credible. With KVK validation, the platform has a scientifically defensible evidence base.

**Selection logic:**
- KVK recommendations reach farmers through extension channels — platform can amplify KVK recommendations at scale that KVK scientists cannot achieve alone
- KVKs conduct FLDs and OFTs that generate ground truth — platform can use this data to validate recommendation accuracy
- Academic institutions provide political insulation that commercial partners lack — KVKs are part of ICAR, a scientific body, not a commercial or political entity
- KVK validation is the credible evidence base that other institutional partners (RRBs, insurance companies) require before committing

**What to offer:** Platform as a channel for KVK recommendations to reach farmers at scale. Anonymized farmer-reported outcome data that validates KVK trial results. Joint research publications.

**What to ask for:** KVK scientists review platform recommendations for their area of specialization. KVK shares FLD/OFT results for platform validation. KVK provides agronomic hotline support for platform edge cases.

**Timeline:** 6 months to first KVK research collaboration; 18 months to national KVK network integration.

---

## Implementation Roadmap

### Phase 1 (Months 0–6): Foundation

- **NABARD**: Initiate discussions with NABARD's Agricultural Finance division. Identify one RRB pilot district (preferred: one district in Maharashtra or Karnataka with high mobile penetration)
- **State Department**: Identify one state with an active Digital Agriculture Mission (Madhya Pradesh or Karnataka). Negotiate pilot MoU for one district
- **FPO**: Identify 3–5 FPOs in the pilot district with active CEOs. Execute first FPO MoU
- **KVK**: Engage the KVK in the pilot district. Establish research collaboration for agronomic validation

### Phase 2 (Months 6–12): Validation

- **Pilot district metrics**: 5,000 active farmers on platform. Measurable improvement in selling price realization (vs non-platform peers). RRB pilot shows NPA reduction in platform-covered portfolio
- **NABARD MoU**: Execute national MoU based on pilot district evidence
- **FPO network**: Expand to 10 FPOs across 3 states
- **State expansion**: Move from single-district pilot to state-level framework agreement

### Phase 3 (Months 12–24): Scaling

- **State-wide deployment**: Platform available to all farmers in pilot state through Krishi Mitra network
- **National RRB engagement**: 5 RRBs using platform for portfolio risk management
- **PPP exploration**: Engage with Ministry of Agriculture for national Digital Agriculture Mission partnership
- **NGO network**: 10+ NGO partnerships driving adoption in non-government channels

---

## Success Criteria

- [ ] 50,000 active farmers receiving recommendations across 3 states by Month 18
- [ ] Average selling price improvement of 8–12% vs non-platform peers (measured through FPO data)
- [ ] RRB NPA rate in platform-covered portfolio ≥2 percentage points lower than control group
- [ ] Zero instances of institutional partner interfering with CPE recommendations (contractual and technical enforcement)
- [ ] KVK validation of platform agronomic accuracy in at least 3 crop systems by Month 24
- [ ] Farmer trust score ≥4.2/5.0 on quarterly farmer satisfaction survey

---

*GTM Strategy for Public-Good Agricultural Digital Platform*
*Cross-references: 01-user-brief.md (product vision), 14-cross-framework-redteam.md (B2B2F tension), 09-constraint-priority-engine.md (CPE architecture)*
