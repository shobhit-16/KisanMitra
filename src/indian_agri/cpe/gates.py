"""CPE gate functions — per specs/09-constraint-priority-engine.md §3.

Each gate evaluates one recommendation against one constraint_state.
Returns PASS or SUPPRESS(reason).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from ..models.constraint_state import ConstraintState
from ..models.enums import CashFlowStatus, HealthStatus, SellingWindow, TenureType, TimeCriticality
from .types import Recommendation, RecommendationCategory, CapitalIntensity, TenureRequirement


@dataclass
class GateResult:
    """Result of a gate evaluation."""
    passed: bool
    reason: str | None = None  # e.g. "health_crisis_active"


# Sentinel for suppression
SUPPRESS = GateResult(passed=False)
PASS = GateResult(passed=True)


def health_gate(recommendation: Recommendation, constraint_state: ConstraintState) -> GateResult:
    """Gate 1: Health Gate — suppress everything except health crisis resources when crisis.

    Per specs/09-constraint-priority-engine.md §3.1.
    """
    if constraint_state.health_status != HealthStatus.CRISIS:
        return PASS

    # Health crisis is active — only health crisis resources pass
    if recommendation.category == RecommendationCategory.HEALTH_CRISIS_RESOURCE:
        return PASS

    return GateResult(passed=False, reason="health_crisis_active")


def tenure_gate(recommendation: Recommendation, constraint_state: ConstraintState) -> GateResult:
    """Gate 2: Tenure Gate — suppress multi-year investments for tenant farmers.

    Per specs/09-constraint-priority-engine.md §3.2.

    Phase 1: Even though Soil Engine isn't publishing yet, Gate 2 is live.
    Tenant detection uses farmer's tenure_type from ConstraintState.
    """
    if constraint_state.tenure_type not in (TenureType.TENANT, TenureType.LEASE):
        return PASS

    # Tenant/lease farmer — check if recommendation requires tenure security
    if not recommendation.requires_tenure_security:
        return PASS

    # Recommendation requires tenure security and farmer is tenant/lease
    if recommendation.tenure_requirement == TenureRequirement.OWNER_ONLY:
        return GateResult(passed=False, reason="tenant_no_tenure_security")

    # Multi-year investments suppressed for tenant farmers
    return GateResult(passed=False, reason="tenant_no_tenure_security")


def cash_flow_gate(recommendation: Recommendation, constraint_state: ConstraintState) -> GateResult:
    """Gate 3: Cash Flow Gate — suppress capital-intensive when cash is tight.

    Per specs/09-constraint-priority-engine.md §3.3.
    """
    if constraint_state.cash_flow_status not in (CashFlowStatus.DEFICIT, CashFlowStatus.EMERGENCY):
        return PASS

    # Emergency/deficit — suppress capital-intensive recommendations
    if recommendation.capital_intensity == CapitalIntensity.HIGH:
        return GateResult(passed=False, reason="cash_flow_emergency")

    if recommendation.capital_intensity == CapitalIntensity.MEDIUM:
        return GateResult(passed=False, reason="cash_flow_deficit")

    # Low/none capital intensity passes
    return PASS


def selling_window_gate(recommendation: Recommendation, constraint_state: ConstraintState) -> GateResult:
    """Gate 4: Selling Window Gate — suppress non-selling during harvest window.

    Per specs/09-constraint-priority-engine.md §3.4.
    """
    if constraint_state.selling_window != SellingWindow.OPEN:
        return PASS

    # Selling window is open — check if harvest is within 7 days
    if not constraint_state.harvest_within_7_days:
        return PASS

    # Harvest within 7 days — only selling/storage recommendations pass
    # Health crisis resources always pass Gate 4 — Gate 1 (health) takes precedence
    if recommendation.category == RecommendationCategory.HEALTH_CRISIS_RESOURCE:
        return PASS
    if recommendation.category == RecommendationCategory.SELLING:
        return PASS

    return GateResult(passed=False, reason="harvest_window_active")


def time_criticality_gate(recommendation: Recommendation, constraint_state: ConstraintState) -> GateResult:
    """Gate 5: Time Criticality Gate — suppress long-lead recommendations in time-critical windows.

    Per specs/09-constraint-priority-engine.md §3.5.
    """
    tc = constraint_state.time_criticality

    if tc == TimeCriticality.IMMEDIATE:
        # Harvest window — only immediate-action recommendations pass
        if recommendation.time_to_action.value in ("immediate", "hours"):
            return PASS
        return GateResult(passed=False, reason="time_criticality_immediate")

    if tc == TimeCriticality.NEAR_TERM:
        # Sowing window active — suppress recommendations requiring weeks
        if recommendation.time_to_action == "weeks":
            return GateResult(passed=False, reason="time_criticality_near_term")
        return PASS

    # MEDIUM_TERM or LONG_TERM — all gates 1-4 apply, Gate 5 is inactive
    return PASS
