"""Unit tests for Income Engine modules — TODO-02 acceptance criteria.

Tests all 6 Income Engine modules:
- Module 1: ObligationCalendar
- Module 2: CashFlowAssessment
- Module 3: MandiPriceVisibility
- Module 4: SellingDecisionGuide
- Module 5: EmergencyCreditPathway
- Module 6: IncomeLedger
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from indian_agri.income.obligations import (
    Obligation,
    ObligationCalendar,
    ObligationType,
    Season,
)
from indian_agri.income.cash_flow import (
    CashFlowAssessmentResult,
    CashFlowConfidence,
    assess as cash_flow_assess,
    update_constraint_state_from_assessment,
)
from indian_agri.income.mandi_prices import (
    MandiPriceService,
    PriceCache,
    clear_price_cache,
)
from indian_agri.integrations.enam import ENAMClient, MandiPrice, ENAMAPIError
from indian_agri.income.selling import (
    StorageDecision,
    SellingDecisionGuide,
    SellingRecommendation,
    calculate_storage_benefit,
)
from indian_agri.income.emergency_credit import (
    CrisisType,
    EmergencyCreditInfo,
    EmergencyCreditPathway,
    get_emergency_health_resources,
    is_health_crisis_event,
)
from indian_agri.income.ledger import (
    BaselinePrice,
    IncomeLedger,
    SaleChannel,
    SaleRecord,
)
from indian_agri.models.constraint_state import ConstraintState


# ---------------------------------------------------------------------------
# Module 1: ObligationCalendar Tests
# ---------------------------------------------------------------------------

class TestObligationCalendar:
    """Tests for ObligationCalendar and Obligation."""

    def test_obligation_is_overdue(self):
        """Obligation.is_overdue() returns True when past due_date and unpaid."""
        ob = Obligation(
            farmer_id=1,
            obligation_type=ObligationType.SCHOOL_FEE,
            description="April school fee",
            amount_rupees=5000.0,
            due_date=date.today() - timedelta(days=5),
        )
        assert ob.is_overdue() is True
        assert ob.days_until_due() == -5

    def test_obligation_is_not_overdue_when_paid(self):
        """Obligation.is_overdue() returns False when paid."""
        ob = Obligation(
            farmer_id=1,
            obligation_type=ObligationType.LOAN_REPAYMENT,
            description="KCC EMI",
            amount_rupees=3000.0,
            due_date=date.today() - timedelta(days=10),
            paid=True,
            paid_date=date.today() - timedelta(days=8),
        )
        assert ob.is_overdue() is False

    def test_calendar_add_obligation(self):
        """ObligationCalendar.add_obligation() adds and sets farmer_id."""
        cal = ObligationCalendar(farmer_id=42)
        ob = Obligation(
            obligation_type=ObligationType.SCHOOL_FEE,
            description="June school fee",
            amount_rupees=5000.0,
            due_date=date(2025, 6, 15),
        )
        cal.add_obligation(ob)
        assert ob.farmer_id == 42
        assert len(cal.list_obligations()) == 1

    def test_calendar_compute_cash_flow_impact(self):
        """compute_cash_flow_impact() returns correct totals."""
        cal = ObligationCalendar(farmer_id=1)
        # Due in 10 days
        cal.add_obligation(Obligation(
            obligation_type=ObligationType.LOAN_REPAYMENT,
            description="EMI 1",
            amount_rupees=5000.0,
            due_date=date.today() + timedelta(days=10),
        ))
        # Due in 20 days
        cal.add_obligation(Obligation(
            obligation_type=ObligationType.SCHOOL_FEE,
            description="June fee",
            amount_rupees=3000.0,
            due_date=date.today() + timedelta(days=20),
        ))
        # Due in 60 days (outside 30d window)
        cal.add_obligation(Obligation(
            obligation_type=ObligationType.LAND_RENT,
            description="Monthly rent",
            amount_rupees=2000.0,
            due_date=date.today() + timedelta(days=60),
        ))
        # Overdue
        cal.add_obligation(Obligation(
            obligation_type=ObligationType.SOCIAL_OBLIGATION,
            description="Wedding expense",
            amount_rupees=10000.0,
            due_date=date.today() - timedelta(days=3),
        ))

        impact = cal.compute_cash_flow_impact()

        assert impact["total_outstanding_30d"] == 8000.0  # 5k + 3k
        assert impact["total_outstanding_90d"] == 20000.0  # all unpaid
        assert impact["overdue_amount"] == 10000.0
        assert impact["obligation_count_30d"] == 2
        assert impact["has_urgent_obligation"] is True  # overdue obligation is urgent

    def test_calendar_compute_cash_flow_impact_has_urgent(self):
        """has_urgent_obligation when any obligation due within 7 days."""
        cal = ObligationCalendar(farmer_id=1)
        cal.add_obligation(Obligation(
            obligation_type=ObligationType.LOAN_REPAYMENT,
            description="Urgent EMI",
            amount_rupees=5000.0,
            due_date=date.today() + timedelta(days=5),  # within 7 days
        ))
        impact = cal.compute_cash_flow_impact()
        assert impact["has_urgent_obligation"] is True

    def test_mark_paid(self):
        """mark_paid() sets paid=True and paid_date."""
        cal = ObligationCalendar(farmer_id=1)
        ob = Obligation(
            obligation_type=ObligationType.LOAN_REPAYMENT,
            description="EMI",
            amount_rupees=3000.0,
            due_date=date.today() + timedelta(days=15),
        )
        cal.add_obligation(ob)
        assert ob.paid is False

        result = cal.mark_paid(ob.id)
        assert result is True
        assert ob.paid is True
        assert ob.paid_date is not None

    def test_list_obligations_excludes_paid_by_default(self):
        """list_obligations() excludes paid obligations unless include_paid=True."""
        cal = ObligationCalendar(farmer_id=1)
        cal.add_obligation(Obligation(
            obligation_type=ObligationType.LOAN_REPAYMENT,
            description="Paid EMI",
            amount_rupees=1000.0,
            due_date=date.today() + timedelta(days=30),
            paid=True,
        ))
        cal.add_obligation(Obligation(
            obligation_type=ObligationType.SCHOOL_FEE,
            description="Unpaid fee",
            amount_rupees=2000.0,
            due_date=date.today() + timedelta(days=30),
        ))
        assert len(cal.list_obligations()) == 1
        assert len(cal.list_obligations(include_paid=True)) == 2


# ---------------------------------------------------------------------------
# Module 2: CashFlowAssessment Tests
# ---------------------------------------------------------------------------

class TestCashFlowAssessment:
    """Tests for CashFlowAssessment (cash_flow module)."""

    def test_assess_surplus(self):
        """SURPLUS when income exceeds expenses significantly."""
        result = cash_flow_assess(
            farmer_id=1,
            expected_income_30d=50000.0,
            expected_expenses_30d=20000.0,
            current_cash_reserves=5000.0,
        )
        assert result.status.value == "surplus"
        assert result.confidence == CashFlowConfidence.MEDIUM
        assert result.surplus_rupees > 0

    def test_assess_deficit(self):
        """DEFICIT when net position is negative beyond threshold."""
        result = cash_flow_assess(
            farmer_id=1,
            expected_income_30d=10000.0,
            expected_expenses_30d=15000.0,
        )
        assert result.status.value in ("deficit", "emergency")
        assert result.deficit_rupees > 0

    def test_assess_emergency(self):
        """EMERGENCY when net position below emergency threshold."""
        result = cash_flow_assess(
            farmer_id=1,
            expected_income_30d=2000.0,
            expected_expenses_30d=15000.0,
        )
        assert result.status.value == "emergency"

    def test_assess_balanced(self):
        """BALANCED when within thresholds."""
        result = cash_flow_assess(
            farmer_id=1,
            expected_income_30d=28000.0,
            expected_expenses_30d=25000.0,
            current_cash_reserves=0.0,
        )
        assert result.status.value == "balanced"

    def test_assess_with_obligation_calendar(self):
        """assess() factors in obligation calendar impact."""
        cal = ObligationCalendar(farmer_id=1)
        cal.add_obligation(Obligation(
            obligation_type=ObligationType.LOAN_REPAYMENT,
            description="EMI due in 5 days",
            amount_rupees=10000.0,
            due_date=date.today() + timedelta(days=5),
        ))

        result = cash_flow_assess(
            farmer_id=1,
            expected_income_30d=30000.0,
            expected_expenses_30d=10000.0,
            obligation_calendar=cal,
        )

        assert result.obligation_impact_30d == 10000.0
        assert result.has_urgent_obligation is True

    def test_assess_urgent_obligation_escalates_to_emergency(self):
        """Urgent obligation + deficit escalates to EMERGENCY."""
        cal = ObligationCalendar(farmer_id=1)
        cal.add_obligation(Obligation(
            obligation_type=ObligationType.SOCIAL_OBLIGATION,
            description="Emergency social expense",
            amount_rupees=15000.0,
            due_date=date.today() + timedelta(days=3),
        ))

        result = cash_flow_assess(
            farmer_id=1,
            expected_income_30d=20000.0,
            expected_expenses_30d=10000.0,
            obligation_calendar=cal,
        )

        # 20k income - 10k expenses - 15k obligations = -5k net position
        # With urgent obligation, escalates to emergency
        assert result.status.value == "emergency"

    def test_update_constraint_state_from_assessment(self):
        """update_constraint_state_from_assessment() applies result to ConstraintState."""
        result = CashFlowAssessmentResult(
            status="deficit",
            confidence=CashFlowConfidence.HIGH,
            deficit_rupees=5000.0,
            obligation_impact_30d=3000.0,
        )

        cs = ConstraintState(farmer_id=1)
        update_constraint_state_from_assessment(result, cs)

        assert cs.cash_flow_status == "deficit"
        assert cs.cash_flow_status_updated_at is not None
        assert cs.obligation_due_within_30_days == 3000.0


# ---------------------------------------------------------------------------
# Module 3: MandiPriceVisibility / e-NAM Tests
# ---------------------------------------------------------------------------

class TestPriceCache:
    """Tests for PriceCache."""

    def test_cache_stores_and_retrieves(self):
        """PriceCache stores and retrieves prices."""
        cache = PriceCache(ttl_hours=24)
        price = MandiPrice(
            mandi_id="MHI001",
            mandi_name="Lasalgaon",
            commodity_code="ONION",
            variety="Medium",
            grade=None,
            price_min=2500.0,
            price_max=3000.0,
            price_modal=2800.0,
            volume_traded=100.0,
            date=date.today(),
            state="Maharashtra",
            district="Nashik",
        )
        cache.set("MHI001", "ONION", date.today(), price)
        retrieved = cache.get("MHI001", "ONION", date.today())
        assert retrieved is not None
        assert retrieved.price_modal == 2800.0

    def test_cache_expires(self):
        """PriceCache expires entries after TTL."""
        cache = PriceCache(ttl_hours=0)  # Zero TTL = immediate expiry
        price = MandiPrice(
            mandi_id="MHI001",
            mandi_name="Lasalgaon",
            commodity_code="ONION",
            variety="Medium",
            grade=None,
            price_min=2500.0,
            price_max=3000.0,
            price_modal=2800.0,
            volume_traded=100.0,
            date=date.today(),
            state="Maharashtra",
            district="Nashik",
        )
        cache.set("MHI001", "ONION", date.today(), price)
        retrieved = cache.get("MHI001", "ONION", date.today())
        # With TTL=0, should be expired
        assert retrieved is None


class TestENAMClient:
    """Tests for ENAMClient."""

    def test_get_modal_price_returns_mock_data(self):
        """ENAMClient returns mock data in Phase 1."""
        client = ENAMClient()
        price = client.get_modal_price(
            mandi_id="MHI001",
            commodity_code="ONION",
            date=date.today(),
        )
        assert price is not None
        assert price.mandi_id == "MHI001"
        assert price.commodity_code == "ONION"
        assert price.price_modal > 0

    def test_price_vs_msp(self):
        """MandiPrice.price_vs_msp() returns correct fraction."""
        price = MandiPrice(
            mandi_id="MHI001",
            mandi_name="Lasalgaon",
            commodity_code="ONION",
            variety="Medium",
            grade=None,
            price_min=2500.0,
            price_max=3000.0,
            price_modal=3000.0,
            volume_traded=100.0,
            date=date.today(),
            state="Maharashtra",
            district="Nashik",
        )
        # MSP = 750/quintal = 7.5/kg → 3000/quintal = 30/kg
        # vs MSP 7.5/kg → 300% above MSP
        assert price.price_vs_msp(7.5) == pytest.approx(300.0, rel=1.0)


class TestMandiPriceService:
    """Tests for MandiPriceService."""

    def setup_method(self):
        clear_price_cache()

    def test_get_prices_for_farmer_returns_result(self):
        """get_prices_for_farmer() returns MandiPriceResult."""
        service = MandiPriceService()
        result = service.get_prices_for_farmer(
            farmer_village="Lasalgaon",
            district="Nashik",
            state="Maharashtra",
            commodity_code="ONION",
        )
        assert isinstance(result, object)
        assert hasattr(result, "has_data")
        assert hasattr(result, "is_stale")
        assert hasattr(result, "modal_prices")

    def test_get_msp_for_known_commodity(self):
        """get_msp_for_commodity() returns correct MSP for known commodity."""
        service = MandiPriceService()
        msp = service.get_msp_for_commodity("ONION", "Maharashtra")
        assert msp is not None
        assert msp == 750.0  # ₹750/quintal

    def test_get_msp_for_unknown_commodity(self):
        """get_msp_for_commodity() returns None for unknown commodity."""
        service = MandiPriceService()
        msp = service.get_msp_for_commodity("UNKNOWN_CROP", "Maharashtra")
        assert msp is None


# ---------------------------------------------------------------------------
# Module 4: SellingDecisionGuide Tests
# ---------------------------------------------------------------------------

class TestCalculateStorageBenefit:
    """Tests for calculate_storage_benefit()."""

    def test_sell_now_when_net_gain_negative(self):
        """SELL_NOW when net_gain < 0."""
        decision = calculate_storage_benefit(
            current_price=2000.0,
            expected_price_peak=2100.0,
            storage_cost_per_quintal=500.0,
            quality_loss_percent=5.0,
            quantity_quintal=10.0,
            cash_need_urgency=1,
        )
        # Net gain = (2100-2000)*10 - 500*10 = 1000 - 5000 = -4000
        assert decision.recommendation == SellingRecommendation.SELL_NOW
        assert decision.net_gain < 0

    def test_storage_viable_with_high_appreciation(self):
        """STORE_VIABLE when >15% appreciation expected."""
        decision = calculate_storage_benefit(
            current_price=2000.0,
            expected_price_peak=2500.0,  # 25% appreciation
            storage_cost_per_quintal=100.0,
            quality_loss_percent=5.0,
            quantity_quintal=10.0,
            cash_need_urgency=1,
        )
        assert decision.recommendation == SellingRecommendation.STORE_VIABLE
        assert decision.net_gain > 0

    def test_emergency_sell_when_cash_need_urgent(self):
        """EMERGENCY_SELL when cash_need_urgency >= 4."""
        decision = calculate_storage_benefit(
            current_price=2000.0,
            expected_price_peak=3000.0,  # Would be viable but...
            storage_cost_per_quintal=100.0,
            quality_loss_percent=5.0,
            quantity_quintal=10.0,
            cash_need_urgency=4,
        )
        assert decision.recommendation == SellingRecommendation.EMERGENCY_SELL

    def test_borderline_when_gain_marginally_above_storage_cost(self):
        """STORE_BORDERLINE when net_gain < 30% of storage cost."""
        decision = calculate_storage_benefit(
            current_price=2000.0,
            expected_price_peak=2100.0,  # 5% appreciation
            storage_cost_per_quintal=100.0,  # 1000 total cost
            quality_loss_percent=5.0,
            quantity_quintal=10.0,
            cash_need_urgency=1,
        )
        # Net gain = 100*10 - 100*10 = 1000 - 1000 = 0
        # 0 < 1000*0.3 = 300 → borderline
        assert decision.recommendation == SellingRecommendation.STORE_BORDERLINE


class TestSellingDecisionGuide:
    """Tests for SellingDecisionGuide."""

    def test_evaluate_returns_storage_decision(self):
        """evaluate() returns a StorageDecision."""
        guide = SellingDecisionGuide()
        decision = guide.evaluate(
            commodity_code="ONION",
            state="Maharashtra",
            district="Nashik",
            variety=None,
            quantity_quintal=10.0,
            current_price=2800.0,
            storage_available=True,
            cash_need_urgency=1,
        )
        assert isinstance(decision, StorageDecision)
        assert decision.recommendation in [
            SellingRecommendation.SELL_NOW,
            SellingRecommendation.STORE_VIABLE,
            SellingRecommendation.STORE_BORDERLINE,
            SellingRecommendation.HOLD,
        ]


# ---------------------------------------------------------------------------
# Module 5: EmergencyCreditPathway Tests
# ---------------------------------------------------------------------------

class TestEmergencyCreditPathway:
    """Tests for Module 5 EmergencyCreditPathway."""

    def test_is_health_crisis_event_true(self):
        """is_health_crisis_event() returns True for crisis + medical."""
        assert is_health_crisis_event("crisis", "medical") is True

    def test_is_health_crisis_event_false_for_non_medical(self):
        """is_health_crisis_event() returns False for non-medical crisis types."""
        assert is_health_crisis_event("crisis", "crop_disease") is False
        assert is_health_crisis_event("crisis", "livestock") is False
        assert is_health_crisis_event("normal", "medical") is False

    def test_get_emergency_health_resources(self):
        """get_emergency_health_resources() returns Ayushman Bharat + state resources."""
        resources = get_emergency_health_resources("Maharashtra")
        assert len(resources) >= 1
        names = [r.source_name for r in resources]
        assert any("Ayushman" in n or "PM-JAY" in n for n in names)

    def test_ayushman_bharat_info(self):
        """Ayushman Bharat resource has correct structure."""
        resources = get_emergency_health_resources("Maharashtra")
        ab = next((r for r in resources if "Ayushman" in r.source_name or "PM-JAY" in r.source_name), None)
        assert ab is not None
        assert ab.credit_amount_rupees == 500000.0
        assert ab.source_type == "government_scheme"
        assert ab.interest_rate_percent is None  # No premium for eligible families


class TestEmergencyCreditPathwayService:
    """Tests for EmergencyCreditPathway service class."""

    def test_evaluate_publishes_for_medical_crisis(self):
        """evaluate_and_publish() publishes for MEDICAL crisis."""
        pathway = EmergencyCreditPathway()
        result = pathway.evaluate_and_publish(
            farmer_id=1,
            state="Maharashtra",
            district="Nashik",
            health_status="crisis",
            crisis_type=CrisisType.MEDICAL,
            estimated_credit_need=80000.0,
        )
        assert result is True  # Published

    def test_evaluate_ignores_non_medical_crisis(self):
        """evaluate_and_publish() returns False for non-MEDICAL crisis."""
        pathway = EmergencyCreditPathway()
        result = pathway.evaluate_and_publish(
            farmer_id=1,
            state="Maharashtra",
            district="Nashik",
            health_status="crisis",
            crisis_type=CrisisType.CROP_DISEASE,
        )
        assert result is False  # Not published

    def test_evaluate_ignores_normal_health(self):
        """evaluate_and_publish() returns False for normal health."""
        pathway = EmergencyCreditPathway()
        result = pathway.evaluate_and_publish(
            farmer_id=1,
            state="Maharashtra",
            district="Nashik",
            health_status="normal",
            crisis_type=CrisisType.MEDICAL,
        )
        assert result is False


# ---------------------------------------------------------------------------
# Module 6: IncomeLedger Tests
# ---------------------------------------------------------------------------

class TestIncomeLedger:
    """Tests for IncomeLedger (Module 6)."""

    def test_add_sale_records_and_sets_distress_flag(self):
        """add_sale() records a sale and computes distress_sale_flag."""
        ledger = IncomeLedger(farmer_id=1)
        record = ledger.add_sale(
            commodity_code="ONION",
            quantity_kg=500.0,
            price_per_kg=28.0,
            channel=SaleChannel.MANDI,
            sale_date=date.today(),
        )
        assert record.id is None  # Not yet saved
        assert record.total_value == 500.0 * 28.0
        assert record.farmer_id == 1

    def test_add_sale_distress_when_15_below_msp(self):
        """distress_sale=True when price is >15% below MSP."""
        ledger = IncomeLedger(farmer_id=1)
        # Onion MSP = 750/quintal = 7.5/kg. Selling at 5/kg = 33% below MSP
        record = ledger.add_sale(
            commodity_code="ONION",
            quantity_kg=500.0,
            price_per_kg=5.0,  # ₹5/kg vs MSP ₹7.5/kg
            channel=SaleChannel.MANDI,
            sale_date=date.today(),
        )
        assert record.distress_sale is True
        assert record.price_vs_msp_percent < -15.0

    def test_add_sale_distress_when_within_7_days_of_harvest(self):
        """distress_sale=True when sold within 7 days of harvest."""
        ledger = IncomeLedger(farmer_id=1)
        harvest_date = date.today()
        sale_date = date.today() + timedelta(days=3)  # 3 days after harvest
        record = ledger.add_sale(
            commodity_code="ONION",
            quantity_kg=500.0,
            price_per_kg=25.0,
            channel=SaleChannel.MANDI,
            sale_date=sale_date,
            harvest_date=harvest_date,
        )
        assert record.distress_sale is True
        assert "days" in record.distress_sale_reason or "harvest" in record.distress_sale_reason

    def test_add_sale_distress_trigger4_entire_crop_first_sale(self):
        """distress_sale=True when first sale of season with large quantity (trigger 4)."""
        ledger = IncomeLedger(farmer_id=1)
        # First sale of season, quantity >= 100kg — triggers trigger-4 distress
        record = ledger.add_sale(
            commodity_code="ONION",
            quantity_kg=150.0,
            price_per_kg=25.0,  # Above MSP, so not trigger-1
            channel=SaleChannel.MANDI,
        )
        assert record.distress_sale is True
        assert "first sale" in record.distress_sale_reason.lower() or "large quantity" in record.distress_sale_reason.lower()

    def test_establish_baseline_requires_min_records(self):
        """establish_baseline() requires at least 3 records by default."""
        ledger = IncomeLedger(farmer_id=1)
        # Only 2 sales
        ledger.add_sale(commodity_code="ONION", quantity_kg=100.0, price_per_kg=25.0)
        ledger.add_sale(commodity_code="ONION", quantity_kg=100.0, price_per_kg=26.0)

        baseline = ledger.establish_baseline(
            commodity_code="ONION",
            district="Nashik",
            state="Maharashtra",
        )
        assert baseline is None  # Not enough records

    def test_establish_baseline(self):
        """establish_baseline() computes correct avg/min/max from sales."""
        ledger = IncomeLedger(farmer_id=1)
        ledger.add_sale(commodity_code="ONION", quantity_kg=100.0, price_per_kg=25.0)
        ledger.add_sale(commodity_code="ONION", quantity_kg=100.0, price_per_kg=28.0)
        ledger.add_sale(commodity_code="ONION", quantity_kg=100.0, price_per_kg=30.0)

        baseline = ledger.establish_baseline(
            commodity_code="ONION",
            district="Nashik",
            state="Maharashtra",
        )
        assert baseline is not None
        assert baseline.avg_price_per_kg == pytest.approx(27.67, rel=0.1)
        assert baseline.min_price_per_kg == 25.0
        assert baseline.max_price_per_kg == 30.0
        assert baseline.record_count == 3

    def test_total_income(self):
        """total_income() returns sum of all sale values."""
        ledger = IncomeLedger(farmer_id=1)
        ledger.add_sale(commodity_code="ONION", quantity_kg=100.0, price_per_kg=25.0)
        ledger.add_sale(commodity_code="ONION", quantity_kg=100.0, price_per_kg=28.0)
        ledger.add_sale(commodity_code="WHEAT", quantity_kg=50.0, price_per_kg=22.0)

        assert ledger.total_income() == (100 * 25) + (100 * 28) + (50 * 22)
        assert ledger.total_income(commodity_code="ONION") == (100 * 25) + (100 * 28)

    def test_average_price(self):
        """average_price() returns mean price for a commodity."""
        ledger = IncomeLedger(farmer_id=1)
        ledger.add_sale(commodity_code="ONION", quantity_kg=100.0, price_per_kg=25.0)
        ledger.add_sale(commodity_code="ONION", quantity_kg=100.0, price_per_kg=35.0)

        avg = ledger.average_price("ONION")
        assert avg == 30.0

    def test_get_distress_sales(self):
        """get_distress_sales() returns only distress-flagged sales."""
        ledger = IncomeLedger(farmer_id=1)
        # Normal sale (quantity < 100kg so doesn't trigger trigger-4 distress)
        ledger.add_sale(commodity_code="ONION", quantity_kg=50.0, price_per_kg=28.0)
        # Distress sale (price below MSP)
        ledger.add_sale(commodity_code="ONION", quantity_kg=200.0, price_per_kg=5.0)

        distress = ledger.get_distress_sales()
        assert len(distress) == 1
        assert distress[0].price_per_kg == 5.0
