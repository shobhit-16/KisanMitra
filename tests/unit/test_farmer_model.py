"""Unit tests for Farmer model and constraint state integration."""

from __future__ import annotations

import pytest

from indian_agri.models.farmer import Farmer
from indian_agri.models.constraint_state import ConstraintState
from indian_agri.models.enums import HealthStatus, TenureType, CashFlowStatus, SellingWindow, TimeCriticality


class TestFarmerConstraintStateIntegration:
    """Tests for Farmer model's constraint state integration."""

    def test_farmer_has_constraint_state_id_field(self):
        """Farmer model must have constraint_state_id FK field."""
        f = Farmer(
            id=1,
            name="Test Farmer",
            phone="9876543210",
            village="Test Village",
            district="Test District",
            state="Maharashtra",
        )
        assert hasattr(f, "constraint_state_id")

    def test_update_constraint_state_returns_constraint_state(self):
        """update_constraint_state() returns a ConstraintState instance."""
        f = Farmer(
            id=1,
            name="Test Farmer",
            phone="9876543210",
            village="Test Village",
            district="Test District",
            state="Maharashtra",
        )
        cs = f.update_constraint_state()
        assert isinstance(cs, ConstraintState)

    def test_update_constraint_state_maps_all_fields(self):
        """update_constraint_state() correctly maps all 6 constraint fields."""
        f = Farmer(
            id=1,
            name="Test Farmer",
            phone="9876543210",
            village="Test Village",
            district="Test District",
            state="Maharashtra",
            health_status=HealthStatus.NORMAL,
            tenure_type=TenureType.TENANT,
            cash_flow_status=CashFlowStatus.DEFICIT,
            selling_window=SellingWindow.OPEN,
            time_criticality=TimeCriticality.IMMEDIATE,
        )
        cs = f.update_constraint_state()

        assert cs.farmer_id == 1
        assert cs.health_status == HealthStatus.NORMAL
        assert cs.tenure_type == TenureType.TENANT
        assert cs.cash_flow_status == CashFlowStatus.DEFICIT
        assert cs.selling_window == SellingWindow.OPEN
        assert cs.time_criticality == TimeCriticality.IMMEDIATE

    def test_update_constraint_state_sets_timestamps(self):
        """update_constraint_state() sets appropriate timestamps."""
        f = Farmer(
            id=1,
            name="Test Farmer",
            phone="9876543210",
            village="Test Village",
            district="Test District",
            state="Maharashtra",
            health_status=HealthStatus.CRISIS,
            tenure_type=TenureType.TENANT,
            cash_flow_status=CashFlowStatus.DEFICIT,
            selling_window=SellingWindow.OPEN,
            time_criticality=TimeCriticality.IMMEDIATE,
        )
        cs = f.update_constraint_state()

        # Timestamps should be set for non-default values
        assert cs.health_status_updated_at is not None
        assert cs.tenure_type_updated_at is not None
        assert cs.cash_flow_status_updated_at is not None
        assert cs.selling_window_updated_at is not None
        assert cs.time_criticality_updated_at is not None

    def test_update_constraint_state_no_timestamp_for_owner(self):
        """update_constraint_state() doesn't set tenure timestamp for owner farmers."""
        f = Farmer(
            id=1,
            name="Test Farmer",
            phone="9876543210",
            village="Test Village",
            district="Test District",
            state="Maharashtra",
            health_status=HealthStatus.NORMAL,
            tenure_type=TenureType.OWNER,
        )
        cs = f.update_constraint_state()

        # OWNER is the default tenure type — no timestamp needed
        assert cs.tenure_type_updated_at is None

    def test_update_constraint_state_no_timestamp_for_normal_health(self):
        """update_constraint_state() doesn't set health timestamp when NORMAL."""
        f = Farmer(
            id=1,
            name="Test Farmer",
            phone="9876543210",
            village="Test Village",
            district="Test District",
            state="Maharashtra",
            health_status=HealthStatus.NORMAL,
            tenure_type=TenureType.OWNER,
        )
        cs = f.update_constraint_state()

        # NORMAL is the default health status — no timestamp needed
        assert cs.health_status_updated_at is None

    def test_update_constraint_state_no_timestamp_for_closed_window(self):
        """update_constraint_state() doesn't set selling_window timestamp when CLOSED."""
        f = Farmer(
            id=1,
            name="Test Farmer",
            phone="9876543210",
            village="Test Village",
            district="Test District",
            state="Maharashtra",
            selling_window=SellingWindow.CLOSED,
        )
        cs = f.update_constraint_state()

        # CLOSED is the default — no timestamp needed
        assert cs.selling_window_updated_at is None
