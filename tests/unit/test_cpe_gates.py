"""Unit tests for CPE gate functions — specs/09-constraint-priority-engine.md §3.

Each gate is tested in isolation with PASS and SUPPRESS cases per the spec.
"""

from __future__ import annotations

import pytest

from indian_agri.cpe.gates import (
    PASS,
    SUPPRESS,
    GateResult,
    health_gate,
    tenure_gate,
    cash_flow_gate,
    selling_window_gate,
    time_criticality_gate,
)
from indian_agri.cpe.types import (
    Recommendation,
    RecommendationCategory,
    CapitalIntensity,
    EngineName,
    TenureRequirement,
    TimeToAction,
)
from indian_agri.models.constraint_state import ConstraintState
from indian_agri.models.enums import HealthStatus, TenureType, CashFlowStatus, SellingWindow, TimeCriticality


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def farmer_id() -> int:
    return 1


@pytest.fixture
def base_recommendation() -> Recommendation:
    """Base recommendation for testing."""
    return Recommendation(
        engine=EngineName.INCOME,
        module="module_test",
        category=RecommendationCategory.INPUT,
        action="Test recommendation",
        capital_intensity=CapitalIntensity.LOW,
        time_to_action=TimeToAction.DAYS,
        priority_for_engine=1,
    )


@pytest.fixture
def health_crisis_recommendation() -> Recommendation:
    """Health crisis resource recommendation."""
    return Recommendation(
        engine=EngineName.INCOME,
        module="module_5",
        category=RecommendationCategory.HEALTH_CRISIS_RESOURCE,
        action="Access emergency health fund via Jan Arogya Yojana",
        capital_intensity=CapitalIntensity.NONE,
        time_to_action=TimeToAction.IMMEDIATE,
        priority_for_engine=1,
    )


@pytest.fixture
def selling_recommendation() -> Recommendation:
    """Selling recommendation."""
    return Recommendation(
        engine=EngineName.INCOME,
        module="module_4",
        category=RecommendationCategory.SELLING,
        action="Sell onion crop at current prices",
        capital_intensity=CapitalIntensity.NONE,
        time_to_action=TimeToAction.IMMEDIATE,
        priority_for_engine=1,
    )


@pytest.fixture
def input_recommendation() -> Recommendation:
    """Input recommendation."""
    return Recommendation(
        engine=EngineName.INCOME,
        module="module_2",
        category=RecommendationCategory.INPUT,
        action="Buy DAP fertilizer",
        capital_intensity=CapitalIntensity.HIGH,
        time_to_action=TimeToAction.DAYS,
        priority_for_engine=1,
    )


# ---------------------------------------------------------------------------
# Gate 1: Health Gate — specs/09-constraint-priority-engine.md §3.1
# ---------------------------------------------------------------------------

class TestHealthGate:
    """Tests for health_gate (Gate 1)."""

    def test_passes_when_health_normal(self, base_recommendation, farmer_id):
        """When health_status = NORMAL, all recommendations pass."""
        cs = ConstraintState(farmer_id=farmer_id, health_status=HealthStatus.NORMAL)
        result = health_gate(base_recommendation, cs)
        assert result.passed is True
        assert result.reason is None

    def test_passes_health_crisis_resource_when_crisis(self, health_crisis_recommendation, farmer_id):
        """When health_status = CRISIS, only HEALTH_CRISIS_RESOURCE passes."""
        cs = ConstraintState(farmer_id=farmer_id, health_status=HealthStatus.CRISIS)
        result = health_gate(health_crisis_recommendation, cs)
        assert result.passed is True
        assert result.reason is None

    def test_suppresses_non_health_when_crisis(self, selling_recommendation, farmer_id):
        """When health_status = CRISIS, non-health recommendations are suppressed."""
        cs = ConstraintState(farmer_id=farmer_id, health_status=HealthStatus.CRISIS)
        result = health_gate(selling_recommendation, cs)
        assert result.passed is False
        assert result.reason == "health_crisis_active"

    def test_suppresses_input_when_crisis(self, input_recommendation, farmer_id):
        """When health_status = CRISIS, INPUT recommendations are suppressed."""
        cs = ConstraintState(farmer_id=farmer_id, health_status=HealthStatus.CRISIS)
        result = health_gate(input_recommendation, cs)
        assert result.passed is False
        assert result.reason == "health_crisis_active"


# ---------------------------------------------------------------------------
# Gate 2: Tenure Gate — specs/09-constraint-priority-engine.md §3.2
# ---------------------------------------------------------------------------

class TestTenureGate:
    """Tests for tenure_gate (Gate 2)."""

    def test_passes_for_owner(self, base_recommendation, farmer_id):
        """When tenure_type = OWNER, all recommendations pass."""
        cs = ConstraintState(farmer_id=farmer_id, tenure_type=TenureType.OWNER)
        result = tenure_gate(base_recommendation, cs)
        assert result.passed is True
        assert result.reason is None

    def test_passes_for_tenant_without_tenure_requirement(
        self, base_recommendation, farmer_id
    ):
        """When farmer is TENANT but recommendation doesn't require tenure, passes."""
        cs = ConstraintState(farmer_id=farmer_id, tenure_type=TenureType.TENANT)
        rec = Recommendation(
            engine=EngineName.INCOME,
            module="module_test",
            category=RecommendationCategory.INPUT,
            action="Test",
            requires_tenure_security=False,
            tenure_requirement=TenureRequirement.ANY,
        )
        result = tenure_gate(rec, cs)
        assert result.passed is True

    def test_suppresses_owner_only_for_tenant(self, farmer_id):
        """When farmer is TENANT and recommendation is OWNER_ONLY, suppressed."""
        cs = ConstraintState(farmer_id=farmer_id, tenure_type=TenureType.TENANT)
        rec = Recommendation(
            engine=EngineName.INCOME,
            module="module_soil",
            category=RecommendationCategory.INPUT,
            action="Multi-year soil investment",
            requires_tenure_security=True,
            tenure_requirement=TenureRequirement.OWNER_ONLY,
        )
        result = tenure_gate(rec, cs)
        assert result.passed is False
        assert result.reason == "tenant_no_tenure_security"

    def test_suppresses_multi_year_for_tenant(self, farmer_id):
        """Multi-year investments suppressed for tenant farmers (Phase 1 spec)."""
        cs = ConstraintState(farmer_id=farmer_id, tenure_type=TenureType.TENANT)
        rec = Recommendation(
            engine=EngineName.INCOME,
            module="module_soil",
            category=RecommendationCategory.PRACTICE,
            action="Vermicompost investment",
            requires_tenure_security=True,
            tenure_requirement=TenureRequirement.OWNER_ONLY,
        )
        result = tenure_gate(rec, cs)
        assert result.passed is False
        assert result.reason == "tenant_no_tenure_security"

    def test_passes_for_lease_with_tenant_viable(self, farmer_id):
        """When farmer is LEASE but recommendation is TENANT_VIABLE, passes."""
        cs = ConstraintState(farmer_id=farmer_id, tenure_type=TenureType.LEASE)
        rec = Recommendation(
            engine=EngineName.INCOME,
            module="module_test",
            category=RecommendationCategory.INPUT,
            action="Zinc sulfate application",
            requires_tenure_security=False,
            tenure_requirement=TenureRequirement.TENANT_VIABLE,
        )
        result = tenure_gate(rec, cs)
        assert result.passed is True


# ---------------------------------------------------------------------------
# Gate 3: Cash Flow Gate — specs/09-constraint-priority-engine.md §3.3
# ---------------------------------------------------------------------------

class TestCashFlowGate:
    """Tests for cash_flow_gate (Gate 3)."""

    def test_passes_when_balanced(self, base_recommendation, farmer_id):
        """When cash_flow_status = BALANCED, all recommendations pass."""
        cs = ConstraintState(farmer_id=farmer_id, cash_flow_status=CashFlowStatus.BALANCED)
        result = cash_flow_gate(base_recommendation, cs)
        assert result.passed is True

    def test_passes_when_surplus(self, base_recommendation, farmer_id):
        """When cash_flow_status = SURPLUS, all recommendations pass."""
        cs = ConstraintState(farmer_id=farmer_id, cash_flow_status=CashFlowStatus.SURPLUS)
        result = cash_flow_gate(base_recommendation, cs)
        assert result.passed is True

    def test_suppresses_high_capital_when_deficit(self, farmer_id):
        """When cash_flow_status = DEFICIT, HIGH capital recommendations suppressed."""
        cs = ConstraintState(farmer_id=farmer_id, cash_flow_status=CashFlowStatus.DEFICIT)
        rec = Recommendation(
            engine=EngineName.INCOME,
            module="module_soil",
            category=RecommendationCategory.INPUT,
            action="Buy equipment",
            capital_intensity=CapitalIntensity.HIGH,
        )
        result = cash_flow_gate(rec, cs)
        assert result.passed is False
        # HIGH capital intensity returns "cash_flow_emergency" reason regardless of status
        assert result.reason == "cash_flow_emergency"

    def test_suppresses_medium_capital_when_deficit(self, farmer_id):
        """When cash_flow_status = DEFICIT, MEDIUM capital recommendations suppressed."""
        cs = ConstraintState(farmer_id=farmer_id, cash_flow_status=CashFlowStatus.DEFICIT)
        rec = Recommendation(
            engine=EngineName.INCOME,
            module="module_soil",
            category=RecommendationCategory.INPUT,
            action="Organic transition",
            capital_intensity=CapitalIntensity.MEDIUM,
        )
        result = cash_flow_gate(rec, cs)
        assert result.passed is False
        assert result.reason == "cash_flow_deficit"

    def test_passes_low_capital_when_deficit(self, farmer_id):
        """When cash_flow_status = DEFICIT, LOW capital recommendations pass."""
        cs = ConstraintState(farmer_id=farmer_id, cash_flow_status=CashFlowStatus.DEFICIT)
        rec = Recommendation(
            engine=EngineName.INCOME,
            module="module_test",
            category=RecommendationCategory.INPUT,
            action="Reduced urea application",
            capital_intensity=CapitalIntensity.LOW,
        )
        result = cash_flow_gate(rec, cs)
        assert result.passed is True

    def test_suppresses_high_capital_when_emergency(self, farmer_id):
        """When cash_flow_status = EMERGENCY, HIGH capital suppressed."""
        cs = ConstraintState(farmer_id=farmer_id, cash_flow_status=CashFlowStatus.EMERGENCY)
        rec = Recommendation(
            engine=EngineName.INCOME,
            module="module_test",
            category=RecommendationCategory.INPUT,
            action="Drip irrigation investment",
            capital_intensity=CapitalIntensity.HIGH,
        )
        result = cash_flow_gate(rec, cs)
        assert result.passed is False
        assert result.reason == "cash_flow_emergency"

    def test_passes_none_capital_when_emergency(self, farmer_id):
        """When cash_flow_status = EMERGENCY, NONE capital recommendations pass."""
        cs = ConstraintState(farmer_id=farmer_id, cash_flow_status=CashFlowStatus.EMERGENCY)
        rec = Recommendation(
            engine=EngineName.INCOME,
            module="module_test",
            category=RecommendationCategory.SELLING,
            action="Sell crop now",
            capital_intensity=CapitalIntensity.NONE,
        )
        result = cash_flow_gate(rec, cs)
        assert result.passed is True


# ---------------------------------------------------------------------------
# Gate 4: Selling Window Gate — specs/09-constraint-priority-engine.md §3.4
# ---------------------------------------------------------------------------

class TestSellingWindowGate:
    """Tests for selling_window_gate (Gate 4)."""

    def test_passes_when_selling_window_closed(self, base_recommendation, farmer_id):
        """When selling_window = CLOSED, all recommendations pass."""
        cs = ConstraintState(
            farmer_id=farmer_id,
            selling_window=SellingWindow.CLOSED,
            harvest_within_7_days=False,
        )
        result = selling_window_gate(base_recommendation, cs)
        assert result.passed is True

    def test_passes_when_harvest_not_within_7_days(self, base_recommendation, farmer_id):
        """When selling_window = OPEN but harvest not within 7 days, all pass."""
        cs = ConstraintState(
            farmer_id=farmer_id,
            selling_window=SellingWindow.OPEN,
            harvest_within_7_days=False,
        )
        result = selling_window_gate(base_recommendation, cs)
        assert result.passed is True

    def test_passes_selling_during_harvest_window(self, selling_recommendation, farmer_id):
        """When harvest within 7 days, SELLING recommendations pass."""
        cs = ConstraintState(
            farmer_id=farmer_id,
            selling_window=SellingWindow.OPEN,
            harvest_within_7_days=True,
        )
        result = selling_window_gate(selling_recommendation, cs)
        assert result.passed is True

    def test_passes_health_crisis_during_harvest_window(
        self, health_crisis_recommendation, farmer_id
    ):
        """When harvest within 7 days, HEALTH_CRISIS_RESOURCE still passes (Gate 1 precedence)."""
        cs = ConstraintState(
            farmer_id=farmer_id,
            selling_window=SellingWindow.OPEN,
            harvest_within_7_days=True,
        )
        result = selling_window_gate(health_crisis_recommendation, cs)
        assert result.passed is True

    def test_suppresses_input_during_harvest_window(self, input_recommendation, farmer_id):
        """When harvest within 7 days, INPUT recommendations suppressed."""
        cs = ConstraintState(
            farmer_id=farmer_id,
            selling_window=SellingWindow.OPEN,
            harvest_within_7_days=True,
        )
        result = selling_window_gate(input_recommendation, cs)
        assert result.passed is False
        assert result.reason == "harvest_window_active"

    def test_suppresses_non_selling_during_harvest_window(self, base_recommendation, farmer_id):
        """When harvest within 7 days, non-selling/non-health suppressed."""
        cs = ConstraintState(
            farmer_id=farmer_id,
            selling_window=SellingWindow.OPEN,
            harvest_within_7_days=True,
        )
        result = selling_window_gate(base_recommendation, cs)
        assert result.passed is False
        assert result.reason == "harvest_window_active"


# ---------------------------------------------------------------------------
# Gate 5: Time Criticality Gate — specs/09-constraint-priority-engine.md §3.5
# ---------------------------------------------------------------------------

class TestTimeCriticalityGate:
    """Tests for time_criticality_gate (Gate 5)."""

    def test_passes_all_when_medium_term(self, base_recommendation, farmer_id):
        """When time_criticality = MEDIUM_TERM, all recommendations pass."""
        cs = ConstraintState(farmer_id=farmer_id, time_criticality=TimeCriticality.MEDIUM_TERM)
        result = time_criticality_gate(base_recommendation, cs)
        assert result.passed is True

    def test_passes_all_when_long_term(self, base_recommendation, farmer_id):
        """When time_criticality = LONG_TERM, all recommendations pass."""
        cs = ConstraintState(farmer_id=farmer_id, time_criticality=TimeCriticality.LONG_TERM)
        result = time_criticality_gate(base_recommendation, cs)
        assert result.passed is True

    def test_suppresses_weeks_when_immediate(self, farmer_id):
        """When time_criticality = IMMEDIATE, recommendations requiring weeks suppressed."""
        cs = ConstraintState(farmer_id=farmer_id, time_criticality=TimeCriticality.IMMEDIATE)
        rec = Recommendation(
            engine=EngineName.INCOME,
            module="module_climate",
            category=RecommendationCategory.PRACTICE,
            action="Laser leveling",
            time_to_action=TimeToAction.WEEKS,
        )
        result = time_criticality_gate(rec, cs)
        assert result.passed is False
        assert result.reason == "time_criticality_immediate"

    def test_passes_immediate_when_immediate(self, farmer_id):
        """When time_criticality = IMMEDIATE, immediate-action recommendations pass."""
        cs = ConstraintState(farmer_id=farmer_id, time_criticality=TimeCriticality.IMMEDIATE)
        rec = Recommendation(
            engine=EngineName.INCOME,
            module="module_test",
            category=RecommendationCategory.SELLING,
            action="Sell now",
            time_to_action=TimeToAction.IMMEDIATE,
        )
        result = time_criticality_gate(rec, cs)
        assert result.passed is True

    def test_passes_hours_when_immediate(self, farmer_id):
        """When time_criticality = IMMEDIATE, hours-action recommendations pass."""
        cs = ConstraintState(farmer_id=farmer_id, time_criticality=TimeCriticality.IMMEDIATE)
        rec = Recommendation(
            engine=EngineName.INCOME,
            module="module_test",
            category=RecommendationCategory.SELLING,
            action="Check price",
            time_to_action=TimeToAction.HOURS,
        )
        result = time_criticality_gate(rec, cs)
        assert result.passed is True

    def test_suppresses_weeks_when_near_term(self, farmer_id):
        """When time_criticality = NEAR_TERM, recommendations requiring weeks suppressed."""
        cs = ConstraintState(farmer_id=farmer_id, time_criticality=TimeCriticality.NEAR_TERM)
        rec = Recommendation(
            engine=EngineName.INCOME,
            module="module_soil",
            category=RecommendationCategory.INPUT,
            action="Compost preparation",
            time_to_action=TimeToAction.WEEKS,
        )
        result = time_criticality_gate(rec, cs)
        assert result.passed is False
        assert result.reason == "time_criticality_near_term"

    def test_passes_days_when_near_term(self, farmer_id):
        """When time_criticality = NEAR_TERM, days-action recommendations pass."""
        cs = ConstraintState(farmer_id=farmer_id, time_criticality=TimeCriticality.NEAR_TERM)
        rec = Recommendation(
            engine=EngineName.INCOME,
            module="module_test",
            category=RecommendationCategory.INPUT,
            action="Apply pesticide",
            time_to_action=TimeToAction.DAYS,
        )
        result = time_criticality_gate(rec, cs)
        assert result.passed is True


# ---------------------------------------------------------------------------
# Sentinel behavior verification
# ---------------------------------------------------------------------------

class TestGateSentinels:
    """Verify PASS and SUPPRESS sentinel behavior."""

    def test_pass_is_gate_result(self):
        """PASS should be a GateResult with passed=True."""
        assert isinstance(PASS, GateResult)
        assert PASS.passed is True
        assert PASS.reason is None

    def test_suppress_is_gate_result(self):
        """SUPPRESS should be a GateResult with passed=False."""
        assert isinstance(SUPPRESS, GateResult)
        assert SUPPRESS.passed is False
        assert SUPPRESS.reason is None

    def test_suppress_not_callable(self):
        """SUPPRESS should NOT be callable — it's an instance, not a function."""
        # SUPPRESS is a GateResult instance, not a callable
        assert not callable(SUPPRESS)
        assert hasattr(SUPPRESS, 'passed')
        assert hasattr(SUPPRESS, 'reason')
