"""Integration tests for CPE.evaluate() — specs/09-constraint-priority-engine.md §6.

Tests the full CPE evaluation pipeline with all gate combinations.
"""

from __future__ import annotations

import pytest

from indian_agri.cpe.engine import CPE
from indian_agri.cpe.bus import RecommendationBus
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
def empty_bus() -> RecommendationBus:
    """Fresh empty recommendation bus."""
    bus = RecommendationBus()
    return bus


@pytest.fixture
def farmer_id() -> int:
    return 1


def make_recommendation(
    category: RecommendationCategory = RecommendationCategory.INPUT,
    capital_intensity: CapitalIntensity = CapitalIntensity.LOW,
    time_to_action: TimeToAction = TimeToAction.DAYS,
    priority_for_engine: int = 1,
    requires_tenure_security: bool = False,
    tenure_requirement: TenureRequirement = TenureRequirement.ANY,
    action: str = "Test recommendation",
    module: str = "module_test",
) -> Recommendation:
    """Helper to create recommendations for testing."""
    return Recommendation(
        engine=EngineName.INCOME,
        module=module,
        category=category,
        action=action,
        capital_intensity=capital_intensity,
        time_to_action=time_to_action,
        priority_for_engine=priority_for_engine,
        requires_tenure_security=requires_tenure_security,
        tenure_requirement=tenure_requirement,
    )


# ---------------------------------------------------------------------------
# One-Recommendation Rule Tests — specs/09-constraint-priority-engine.md §6
# ---------------------------------------------------------------------------

class TestOneRecommendationRule:
    """Tests for the one-recommendation output rule."""

    @pytest.mark.asyncio
    async def test_returns_single_recommendation(
        self, empty_bus, farmer_id
    ):
        """CPE.evaluate() returns exactly one recommendation, never a list."""
        await empty_bus.publish(make_recommendation(action="Sell onions"))
        await empty_bus.publish(make_recommendation(action="Buy fertilizer"))

        cs = ConstraintState(farmer_id=farmer_id, health_status=HealthStatus.NORMAL)
        cpe = CPE(bus=empty_bus, constraint_state=cs)
        output = cpe.evaluate()

        assert output.output_type == "recommendation"
        assert output.recommendation is not None
        assert isinstance(output.recommendation, Recommendation)

    @pytest.mark.asyncio
    async def test_never_returns_zero_outputs(
        self, empty_bus, farmer_id
    ):
        """CPE.evaluate() always returns exactly one output (never zero)."""
        await empty_bus.publish(make_recommendation(action="Sell onions"))

        cs = ConstraintState(farmer_id=farmer_id, health_status=HealthStatus.CRISIS)
        cpe = CPE(bus=empty_bus, constraint_state=cs)
        output = cpe.evaluate()

        # Should return suppression, not zero
        assert output.output_type in ("recommendation", "suppression")
        assert output.recommendation is not None or output.active_constraint is not None

    @pytest.mark.asyncio
    async def test_health_crisis_wins_over_selling(
        self, empty_bus, farmer_id
    ):
        """When health = crisis, health_crisis_resource wins over SELLING (Gate 1 priority)."""
        health_rec = make_recommendation(
            category=RecommendationCategory.HEALTH_CRISIS_RESOURCE,
            action="Access Jan Arogya Yojana",
            capital_intensity=CapitalIntensity.NONE,
            time_to_action=TimeToAction.IMMEDIATE,
            module="module_5",
        )
        selling_rec = make_recommendation(
            category=RecommendationCategory.SELLING,
            action="Sell onion crop",
            capital_intensity=CapitalIntensity.NONE,
            module="module_4",
        )

        await empty_bus.publish(selling_rec)
        await empty_bus.publish(health_rec)

        cs = ConstraintState(farmer_id=farmer_id, health_status=HealthStatus.CRISIS)
        cpe = CPE(bus=empty_bus, constraint_state=cs)
        output = cpe.evaluate()

        assert output.output_type == "recommendation"
        assert output.recommendation.category == RecommendationCategory.HEALTH_CRISIS_RESOURCE

    @pytest.mark.asyncio
    async def test_suppression_when_all_blocked(
        self, empty_bus, farmer_id
    ):
        """When all recommendations are suppressed, returns suppression output."""
        # Non-health rec published when health = crisis
        selling_rec = make_recommendation(
            category=RecommendationCategory.SELLING,
            action="Sell onion crop",
            module="module_4",
        )
        await empty_bus.publish(selling_rec)

        cs = ConstraintState(farmer_id=farmer_id, health_status=HealthStatus.CRISIS)
        cpe = CPE(bus=empty_bus, constraint_state=cs)
        output = cpe.evaluate()

        assert output.output_type == "suppression"
        assert output.recommendation is None
        assert output.active_constraint == "health"


# ---------------------------------------------------------------------------
# Gate Priority Order Tests — specs/09-constraint-priority-engine.md §3
# ---------------------------------------------------------------------------

class TestGatePriorityOrder:
    """Tests verifying gates evaluate in strict priority order."""

    @pytest.mark.asyncio
    async def test_gate_1_health_blocks_gate_4_selling(
        self, empty_bus, farmer_id
    ):
        """Gate 1 (Health) blocks Gate 4 (Selling Window) — health crisis wins."""
        # Farmer is in harvest window AND health crisis
        health_rec = make_recommendation(
            category=RecommendationCategory.HEALTH_CRISIS_RESOURCE,
            action="Emergency health fund",
            capital_intensity=CapitalIntensity.NONE,
            module="module_5",
        )
        selling_rec = make_recommendation(
            category=RecommendationCategory.SELLING,
            action="Sell immediately",
            capital_intensity=CapitalIntensity.NONE,
            module="module_4",
        )

        await empty_bus.publish(selling_rec)
        await empty_bus.publish(health_rec)

        cs = ConstraintState(
            farmer_id=farmer_id,
            health_status=HealthStatus.CRISIS,
            selling_window=SellingWindow.OPEN,
            harvest_within_7_days=True,
        )
        cpe = CPE(bus=empty_bus, constraint_state=cs)
        output = cpe.evaluate()

        # Gate 1 (health) takes precedence over Gate 4 (selling window)
        assert output.recommendation.category == RecommendationCategory.HEALTH_CRISIS_RESOURCE

    @pytest.mark.asyncio
    async def test_gate_3_cash_blocks_high_capital(
        self, empty_bus, farmer_id
    ):
        """Gate 3 (Cash Flow) suppresses high-capital recommendations during deficit."""
        high_cap_rec = make_recommendation(
            category=RecommendationCategory.INPUT,
            action="Buy tractor",
            capital_intensity=CapitalIntensity.HIGH,
            module="module_soil",
        )
        low_cap_rec = make_recommendation(
            category=RecommendationCategory.INPUT,
            action="Apply pesticide",
            capital_intensity=CapitalIntensity.LOW,
            module="module_test",
        )

        await empty_bus.publish(high_cap_rec)
        await empty_bus.publish(low_cap_rec)

        cs = ConstraintState(
            farmer_id=farmer_id,
            cash_flow_status=CashFlowStatus.DEFICIT,
        )
        cpe = CPE(bus=empty_bus, constraint_state=cs)
        output = cpe.evaluate()

        assert output.recommendation.capital_intensity == CapitalIntensity.LOW


# ---------------------------------------------------------------------------
# Suppression Notification Tests — specs/09-constraint-priority-engine.md §6.2
# ---------------------------------------------------------------------------

class TestSuppressionNotification:
    """Tests for suppression notification format."""

    @pytest.mark.asyncio
    async def test_suppression_has_active_constraint(
        self, empty_bus, farmer_id
    ):
        """Suppression output includes the active_constraint field."""
        await empty_bus.publish(make_recommendation(
            category=RecommendationCategory.SELLING,
            action="Sell",
        ))

        cs = ConstraintState(farmer_id=farmer_id, health_status=HealthStatus.CRISIS)
        cpe = CPE(bus=empty_bus, constraint_state=cs)
        output = cpe.evaluate()

        assert output.output_type == "suppression"
        assert output.active_constraint is not None
        assert output.active_constraint == "health"

    @pytest.mark.asyncio
    async def test_suppression_format_matches_spec(
        self, empty_bus, farmer_id
    ):
        """Suppression notification format: 'Right now, [active_constraint] is your main priority.'"""
        await empty_bus.publish(make_recommendation(
            category=RecommendationCategory.INPUT,
            action="Soil test",
        ))

        cs = ConstraintState(
            farmer_id=farmer_id,
            health_status=HealthStatus.CRISIS,
        )
        cpe = CPE(bus=empty_bus, constraint_state=cs)
        output = cpe.evaluate()

        # Per spec §6.2: suppression message references active_constraint
        assert output.active_constraint == "health"
        assert output.suppressed_reasons is not None
        assert len(output.suppressed_reasons) >= 1


# ---------------------------------------------------------------------------
# Phase 1 Gate Activation Tests — specs/09-constraint-priority-engine.md §5.1
# ---------------------------------------------------------------------------

class TestPhase1GateActivation:
    """Tests verifying Phase 1 gate activation matches spec."""

    @pytest.mark.asyncio
    async def test_phase1_gate_1_active(
        self, empty_bus, farmer_id
    ):
        """Phase 1: Gate 1 (Health) is active."""
        health_rec = make_recommendation(
            category=RecommendationCategory.HEALTH_CRISIS_RESOURCE,
            action="Health scheme info",
            module="module_5",
        )
        selling_rec = make_recommendation(
            category=RecommendationCategory.SELLING,
            action="Sell crop",
            module="module_4",
        )

        await empty_bus.publish(health_rec)
        await empty_bus.publish(selling_rec)

        cs = ConstraintState(
            farmer_id=farmer_id,
            health_status=HealthStatus.CRISIS,
        )
        cpe = CPE(bus=empty_bus, constraint_state=cs)
        output = cpe.evaluate()

        # Gate 1 fires: health crisis resource passes
        assert output.recommendation.category == RecommendationCategory.HEALTH_CRISIS_RESOURCE

    @pytest.mark.asyncio
    async def test_phase1_gate_2_evaluates_tenant(
        self, empty_bus, farmer_id
    ):
        """Phase 1: Gate 2 is live — tenant detection from Farmer's tenure_type."""
        owner_only_rec = make_recommendation(
            category=RecommendationCategory.PRACTICE,
            action="Multi-year soil investment",
            requires_tenure_security=True,
            tenure_requirement=TenureRequirement.OWNER_ONLY,
            module="module_soil",
        )
        tenant_viable_rec = make_recommendation(
            category=RecommendationCategory.INPUT,
            action="Zinc sulfate",
            requires_tenure_security=False,
            tenure_requirement=TenureRequirement.TENANT_VIABLE,
            module="module_test",
        )

        await empty_bus.publish(owner_only_rec)
        await empty_bus.publish(tenant_viable_rec)

        # Farmer is tenant
        cs = ConstraintState(
            farmer_id=farmer_id,
            tenure_type=TenureType.TENANT,
            health_status=HealthStatus.NORMAL,
        )
        cpe = CPE(bus=empty_bus, constraint_state=cs)
        output = cpe.evaluate()

        # Tenant-viable recommendation should pass
        assert output.recommendation.tenure_requirement == TenureRequirement.TENANT_VIABLE

    @pytest.mark.asyncio
    async def test_phase1_gate_3_active(
        self, empty_bus, farmer_id
    ):
        """Phase 1: Gate 3 (Cash Flow) is active."""
        high_cap_rec = make_recommendation(
            category=RecommendationCategory.INPUT,
            action="Equipment purchase",
            capital_intensity=CapitalIntensity.HIGH,
        )
        selling_rec = make_recommendation(
            category=RecommendationCategory.SELLING,
            action="Sell crop",
            capital_intensity=CapitalIntensity.NONE,
            module="module_4",
        )

        await empty_bus.publish(high_cap_rec)
        await empty_bus.publish(selling_rec)

        cs = ConstraintState(
            farmer_id=farmer_id,
            cash_flow_status=CashFlowStatus.EMERGENCY,
        )
        cpe = CPE(bus=empty_bus, constraint_state=cs)
        output = cpe.evaluate()

        # High capital suppressed; selling passes
        assert output.recommendation.category == RecommendationCategory.SELLING

    @pytest.mark.asyncio
    async def test_phase1_gate_4_active(
        self, empty_bus, farmer_id
    ):
        """Phase 1: Gate 4 (Selling Window) is active."""
        selling_rec = make_recommendation(
            category=RecommendationCategory.SELLING,
            action="Sell now",
            capital_intensity=CapitalIntensity.NONE,
            module="module_4",
        )
        input_rec = make_recommendation(
            category=RecommendationCategory.INPUT,
            action="Buy fertilizer",
            capital_intensity=CapitalIntensity.MEDIUM,
            module="module_test",
        )

        await empty_bus.publish(selling_rec)
        await empty_bus.publish(input_rec)

        cs = ConstraintState(
            farmer_id=farmer_id,
            selling_window=SellingWindow.OPEN,
            harvest_within_7_days=True,
        )
        cpe = CPE(bus=empty_bus, constraint_state=cs)
        output = cpe.evaluate()

        # Selling window: selling passes, input suppressed
        assert output.recommendation.category == RecommendationCategory.SELLING

    @pytest.mark.asyncio
    async def test_phase1_gate_5_active(
        self, empty_bus, farmer_id
    ):
        """Phase 1: Gate 5 (Time Criticality) is active."""
        immediate_rec = make_recommendation(
            category=RecommendationCategory.SELLING,
            action="Check price now",
            time_to_action=TimeToAction.IMMEDIATE,
            module="module_3",
        )
        weeks_rec = make_recommendation(
            category=RecommendationCategory.PRACTICE,
            action="Land preparation",
            time_to_action=TimeToAction.WEEKS,
            module="module_soil",
        )

        await empty_bus.publish(immediate_rec)
        await empty_bus.publish(weeks_rec)

        cs = ConstraintState(
            farmer_id=farmer_id,
            time_criticality=TimeCriticality.IMMEDIATE,
        )
        cpe = CPE(bus=empty_bus, constraint_state=cs)
        output = cpe.evaluate()

        # Immediate passes; weeks suppressed
        assert output.recommendation.time_to_action == TimeToAction.IMMEDIATE
