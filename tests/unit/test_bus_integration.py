"""Unit tests for Income Engine → Recommendation Bus integration."""

from __future__ import annotations

import asyncio

import pytest

from indian_agri.cpe.bus import get_recommendation_bus
from indian_agri.cpe.types import (
    RecommendationCategory,
    CapitalIntensity,
    EngineName,
    TenureRequirement,
    TimeToAction,
)


class TestBusIntegrationPublishHelpers:
    """Tests for income bus_integration publish helper functions."""

    def setup_method(self):
        """Clear the global bus before each test."""
        bus = get_recommendation_bus()
        bus.clear()

    def test_publish_recommendation_returns_recommendation(self):
        """publish_recommendation() returns a Recommendation object."""
        from indian_agri.income.bus_integration import publish_recommendation

        rec = publish_recommendation(
            module="module_test",
            category=RecommendationCategory.INPUT,
            action="Test action",
        )

        assert rec is not None
        assert rec.engine == EngineName.INCOME
        assert rec.module == "module_test"
        assert rec.category == RecommendationCategory.INPUT
        assert rec.action == "Test action"

    def test_publish_recommendation_sets_metadata(self):
        """publish_recommendation() correctly sets all metadata fields."""
        from indian_agri.income.bus_integration import publish_recommendation

        rec = publish_recommendation(
            module="module_2_cashflow",
            category=RecommendationCategory.FINANCIAL,
            action="Apply for KCC",
            capital_intensity=CapitalIntensity.LOW,
            tenure_requirement=TenureRequirement.ANY,
            requires_tenure_security=False,
            time_to_action=TimeToAction.DAYS,
            priority_for_engine=1,
            metadata={"test_key": "test_value"},
        )

        assert rec.capital_intensity == CapitalIntensity.LOW
        assert rec.tenure_requirement == TenureRequirement.ANY
        assert rec.requires_tenure_security is False
        assert rec.time_to_action == TimeToAction.DAYS
        assert rec.priority_for_engine == 1
        assert rec.metadata["test_key"] == "test_value"

    def test_publish_selling_recommendation_sets_correct_category(self):
        """publish_selling_recommendation() sets category to SELLING."""
        from indian_agri.income.bus_integration import publish_selling_recommendation

        rec = publish_selling_recommendation(
            action="Sell onion crop at current prices",
            price_above_msp=True,
            days_until_harvest=5,
        )

        assert rec.category == RecommendationCategory.SELLING
        assert rec.module == "module_4_selling"
        assert rec.metadata["price_above_msp"] is True
        assert rec.metadata["days_until_harvest"] == 5

    def test_publish_selling_recommendation_sets_immediate_for_close_harvest(self):
        """publish_selling_recommendation() sets IMMEDIATE for harvest within 3 days."""
        from indian_agri.income.bus_integration import publish_selling_recommendation

        rec = publish_selling_recommendation(
            action="Sell now",
            days_until_harvest=2,
        )

        assert rec.time_to_action == TimeToAction.IMMEDIATE

    def test_publish_selling_recommendation_sets_days_for_further_harvest(self):
        """publish_selling_recommendation() sets DAYS for harvest beyond 3 days."""
        from indian_agri.income.bus_integration import publish_selling_recommendation

        rec = publish_selling_recommendation(
            action="Prepare to sell",
            days_until_harvest=10,
        )

        assert rec.time_to_action == TimeToAction.DAYS

    def test_publish_emergency_credit_sets_health_crisis_resource(self):
        """publish_emergency_credit() sets category to HEALTH_CRISIS_RESOURCE."""
        from indian_agri.income.bus_integration import publish_emergency_credit

        rec = publish_emergency_credit(
            action="Access emergency health fund via Jan Arogya Yojana",
            credit_amount_rupees=50000.0,
            crisis_type="medical",
        )

        assert rec.category == RecommendationCategory.HEALTH_CRISIS_RESOURCE
        assert rec.module == "module_5_emergency_credit"
        assert rec.time_to_action == TimeToAction.IMMEDIATE
        assert rec.capital_intensity == CapitalIntensity.NONE
        assert rec.metadata["crisis_type"] == "medical"
        assert rec.metadata["credit_amount_rupees"] == 50000.0

    @pytest.mark.asyncio
    async def test_published_recommendation_appears_on_bus(self):
        """Recommendations published via bus_integration appear on the RecommendationBus."""
        from indian_agri.income.bus_integration import publish_recommendation

        bus = get_recommendation_bus()
        bus.clear()

        rec = publish_recommendation(
            module="module_test",
            category=RecommendationCategory.SELLING,
            action="Test sell",
        )

        # Wait for async publish to complete
        await asyncio.sleep(0)

        all_recs = bus.get_all()
        assert len(all_recs) == 1
        assert all_recs[0].recommendation_id == rec.recommendation_id

    def test_income_module_exports_publish_recommendation(self):
        """income module exports publish_recommendation via __all__."""
        from indian_agri.income import publish_recommendation

        assert callable(publish_recommendation)

    def test_income_module_exports_get_recommendation_bus(self):
        """income module exports get_recommendation_bus via __all__."""
        from indian_agri.income import get_recommendation_bus

        assert callable(get_recommendation_bus)
