# TODO-02-INCOME-ENGINE

**Status**: ACTIVE

## Description

Income Engine Phase 1 modules: Module 1 (Obligation Calendar), Module 2 (Cash Flow Assessment), Module 3 (Multi-Mandi Price Visibility via e-NAM API), Module 4 (Selling Decision Guide), Module 5 (Emergency Credit Pathway), Module 6 (Income Ledger). All modules publish to Recommendation Bus.

Per `specs/09-constraint-priority-engine.md §5.1`, Income Engine is the only engine publishing in Phase 1.

## Spec Reference

- `specs/03-market-intelligence.md` — mandi price data, selling decision framework, storage economics, distress sale detection
- `specs/09-constraint-priority-engine.md §5.1` — Phase 1: Income Engine only, all 5 gates active
- `specs/01-domain-model.md §4` — HarvestRecord, SalesRecord with distress_sale_flag

## Acceptance Criteria

- [ ] Module 1: ObligationCalendar — capture school fees (April, June, October), loan repayments, social obligations by season; store in `Obligation` entity; drive `cash_flow_status` computation
- [ ] Module 2: CashFlowAssessment — weekly status assessment: surplus/balanced/deficit/emergency; updates `constraint_state.cash_flow_status`; triggers Gate 3
- [ ] Module 3: MandiPriceVisibility — e-NAM API integration at `src/indian_agri/integrations/enam.py`; fetch daily modal prices for farmer's crop and nearest 3 mandis; cache in Redis with 24h TTL; handle missing data per `specs/03-market-intelligence.md §9.1`
- [ ] Module 4: SellingDecisionGuide — storage economics calculator per `specs/03-market-intelligence.md §4.2`; price threshold triggers (above MSP, below MSP, seasonal patterns); recommend sell/store/hold; publish recommendation to bus with `capital_intensity` and `time_to_action` fields
- [ ] Module 5: EmergencyCreditPathway — health shock detection via `health_status = crisis` events; emergency credit pathway only for medical emergency context per `specs/09-constraint-priority-engine.md §3.1`; NOT a general credit product; publish `health_crisis_resource` category recommendations
- [ ] Module 6: IncomeLedger — record actual transaction prices from farmer self-report or field agent; establish baseline per `specs/03-market-intelligence.md §4a`; track `production_kg`, `price_per_kg`, `total_value`; compute distress_sale_flag per `specs/01-domain-model.md §4.3`
- [ ] All modules publish to Recommendation Bus with correct `engine="income"`, `category`, `capital_intensity`, `requires_tenure_security`, `time_to_action` fields
- [ ] Module 2 (CashFlowAssessment) updates `constraint_state.cash_flow_status` via event: `cash_flow_assessed`
- [ ] Module 4 (SellingDecisionGuide) opens `selling_window` when farmer enters harvest date

## Subtasks

- [ ] BUILD-1 (Est: 2h) — Module 1 (ObligationCalendar) at `src/indian_agri/income/obligations.py` — `Obligation` entity, `obligation_calendar` per farmer, season-based obligation mapping, `compute_cash_flow_impact()` for Module 2
- [ ] BUILD-2 (Est: 3h) — Module 2 (CashFlowAssessment) at `src/indian_agri/income/cash_flow.py` — weekly assessment, 4-tier status, `cash_flow_status` update event, obligation calendar integration, `assess(farmer_id)` → status enum
- [ ] BUILD-3 (Est: 3h) — Module 3 (MandiPriceVisibility) at `src/indian_agri/income/mandi_prices.py` + `src/indian_agri/integrations/enam.py` — e-NAM API client (daily modal prices, commodity × variety × mandi), Redis cache layer, nearest-3-mandis computation, fallback when data missing
- [ ] BUILD-4 (Est: 3h) — Module 4 (SellingDecisionGuide) at `src/indian_agri/income/selling.py` — storage economics calculator, price threshold logic, sell/store/hold recommendation, `publish_selling_recommendation()` to bus
- [ ] BUILD-5 (Est: 2h) — Module 5 (EmergencyCreditPathway) at `src/indian_agri/income/emergency_credit.py` — health_shock detection, medical emergency context filtering, Ayushman Bharat info publishing, emergency credit recommendation publishing
- [ ] BUILD-6 (Est: 2h) — Module 6 (IncomeLedger) at `src/indian_agri/income/ledger.py` — record actual prices, baseline establishment, distress_sale_flag computation per `specs/01-domain-model.md §4.3`, `add_sale()` method
- [ ] WIRE-1 (Est: 2h) — Wire all 6 modules to RecommendationBus: each module's `publish_*()` method wired to `recommendation_bus.publish()`; verify all 6 module recommendation types appear in bus
- [ ] WIRE-2 (Est: 1h) — Wire Module 2 → ConstraintState: `CashFlowAssessment.assess()` triggers `cash_flow_assessed` event; verify `constraint_state.cash_flow_status` updates correctly
- [ ] WIRE-3 (Est: 1h) — Wire Module 4 → selling_window: harvest date entry from farmer closes `selling_window = open`; verify Gate 4 fires correctly at harvest

## Definition of Done

- [ ] All 6 Income Engine modules publish recommendations to Recommendation Bus
- [ ] e-NAM API returns real price data (or graceful degradation with cached data + explicit staleness label)
- [ ] Module 2 updates constraint_state.cash_flow_status correctly for all 4 tiers
- [ ] Module 4 selling recommendation includes `capital_intensity: none|low|medium|high` and `time_to_action: immediate|hours|days|weeks`
- [ ] Module 5 publishes only `health_crisis_resource` category — no general credit product
- [ ] Module 6 correctly computes `distress_sale_flag` per all 4 triggers in `specs/01-domain-model.md §4.3`
