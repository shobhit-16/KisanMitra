"""Module 2: Cash Flow Assessment — specs/09-constraint-priority-engine.md §5.1.

Weekly cash flow status assessment: SURPLUS | BALANCED | DEFICIT | EMERGENCY.
Updates constraint_state.cash_flow_status via cash_flow_assessed event.
Drives Gate 3 (CashFlowGate) in CPE.

The assess() function is the canonical entry point — it takes a Farmer +
ObligationCalendar impact and returns a CashFlowStatus enum value.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from ..models.enums import CashFlowStatus
from .obligations import ObligationCalendar


class CashFlowConfidence(str, Enum):
    """Confidence level in the cash flow assessment."""
    HIGH = "high"       # Based on actual sales records + obligation calendar
    MEDIUM = "medium"  # Based on partial data
    LOW = "low"        # Estimate only


@dataclass
class CashFlowAssessmentResult:
    """Result of a cash flow assessment — used to update ConstraintState."""

    status: CashFlowStatus
    confidence: CashFlowConfidence
    surplus_rupees: float = 0.0
    deficit_rupees: float = 0.0
    obligation_impact_30d: float = 0.0  # From ObligationCalendar
    has_urgent_obligation: bool = False
    assessed_at: datetime = field(default_factory=datetime.utcnow)
    reason: str = ""

    def obligation_due_within_30_days(self) -> Optional[float]:
        """Return obligation amount due within 30 days, or None if not applicable."""
        if self.obligation_impact_30d > 0:
            return self.obligation_impact_30d
        return None


def assess(
    farmer_id: int,
    expected_income_30d: float,
    expected_expenses_30d: float,
    obligation_calendar: Optional[ObligationCalendar] = None,
    current_cash_reserves: float = 0.0,
    prior_status: Optional[CashFlowStatus] = None,
) -> CashFlowAssessmentResult:
    """Assess a farmer's cash flow status for the next 30 days.

    This is the canonical entry point for Module 2. Called by the income engine
    on a weekly cadence (or on-demand when a major event occurs).

    Args:
        farmer_id: ID of the farmer being assessed
        expected_income_30d: Expected cash inflows in the next 30 days (rupees)
        expected_expenses_30d: Expected cash outflows in the next 30 days (rupees)
        obligation_calendar: Farmer's obligation calendar for near-term obligations
        current_cash_reserves: Current cash on hand (rupees)
        prior_status: Previous cash flow status (for trend detection)

    Returns:
        CashFlowAssessmentResult with status, confidence, and reasoning
    """
    # Factor in obligation calendar impact if provided
    obligation_impact_30d = 0.0
    has_urgent_obligation = False

    if obligation_calendar is not None:
        impact = obligation_calendar.compute_cash_flow_impact()
        obligation_impact_30d = impact["total_outstanding_30d"]
        has_urgent_obligation = impact["has_urgent_obligation"]

    # Net position = income - expenses - obligations + reserves
    net_position = (
        expected_income_30d
        - expected_expenses_30d
        - obligation_impact_30d
        + current_cash_reserves
    )

    # Thresholds for classification
    EMERGENCY_THRESHOLD = -5000.0   # Severe deficit
    DEFICIT_THRESHOLD = -1000.0    # Moderate deficit
    SURPLUS_THRESHOLD = 5000.0     # Significant surplus

    if net_position <= EMERGENCY_THRESHOLD:
        status = CashFlowStatus.EMERGENCY
        reason = (
            f"Emergency deficit: net position ₹{net_position:.0f} "
            f"(income ₹{expected_income_30d:.0f} - expenses ₹{expected_expenses_30d:.0f} "
            f"- obligations ₹{obligation_impact_30d:.0f})"
        )
    elif net_position <= DEFICIT_THRESHOLD:
        status = CashFlowStatus.DEFICIT
        reason = (
            f"Deficit: net position ₹{net_position:.0f} "
            f"(income ₹{expected_income_30d:.0f} - expenses ₹{expected_expenses_30d:.0f} "
            f"- obligations ₹{obligation_impact_30d:.0f})"
        )
    elif net_position >= SURPLUS_THRESHOLD and obligation_impact_30d == 0:
        status = CashFlowStatus.SURPLUS
        reason = f"Surplus: net position ₹{net_position:.0f}"
    else:
        status = CashFlowStatus.BALANCED
        if net_position < 0:
            reason = (
                f"Near-balanced with small deficit: ₹{abs(net_position):.0f}"
            )
        else:
            reason = f"Balanced: net position ₹{net_position:.0f}"

    # Downgrade to EMERGENCY if there are urgent obligations and deficit
    if has_urgent_obligation and status in (CashFlowStatus.DEFICIT, CashFlowStatus.BALANCED):
        # Check if the deficit + urgent obligation creates emergency
        if net_position + (obligation_impact_30d * 0.5) <= EMERGENCY_THRESHOLD:
            status = CashFlowStatus.EMERGENCY
            reason = (
                f"Emergency escalated due to urgent obligation: "
                f"deficit ₹{abs(net_position):.0f} with payment due within 7 days"
            )

    # Confidence assessment
    if obligation_calendar is not None and expected_income_30d > 0:
        confidence = CashFlowConfidence.HIGH
    elif expected_income_30d > 0 or expected_expenses_30d > 0:
        confidence = CashFlowConfidence.MEDIUM
    else:
        confidence = CashFlowConfidence.LOW

    surplus = max(net_position, 0.0) if status == CashFlowStatus.SURPLUS else 0.0
    deficit = abs(min(net_position, 0.0)) if status in (CashFlowStatus.DEFICIT, CashFlowStatus.EMERGENCY) else 0.0

    return CashFlowAssessmentResult(
        status=status,
        confidence=confidence,
        surplus_rupees=surplus,
        deficit_rupees=deficit,
        obligation_impact_30d=obligation_impact_30d,
        has_urgent_obligation=has_urgent_obligation,
        reason=reason,
    )


def update_constraint_state_from_assessment(
    result: CashFlowAssessmentResult,
    constraint_state,
) -> None:
    """Apply CashFlowAssessmentResult to a ConstraintState entity.

    Called by the wiring layer after assess() returns.

    Args:
        result: The assessment result from assess()
        constraint_state: The ConstraintState entity to update (in-place)
    """
    constraint_state.cash_flow_status = result.status
    constraint_state.cash_flow_status_updated_at = datetime.utcnow()
    constraint_state.cash_flow_confidence = (
        0.9 if result.confidence == CashFlowConfidence.HIGH else
        0.6 if result.confidence == CashFlowConfidence.MEDIUM else
        0.3
    )
    if result.obligation_due_within_30_days() is not None:
        constraint_state.obligation_due_within_30_days = result.obligation_due_within_30_days()
