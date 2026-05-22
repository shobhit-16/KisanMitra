"""Module 5: Emergency Credit Pathway — specs/09-constraint-priority-engine.md §3.1.

Health shock detection and emergency credit pathway. Health crisis resource recommendations
are published ONLY for medical emergency context — NOT a general credit product.
Published only when health_status = crisis AND crisis_type = medical.

Per Gate 1: only HEALTH_CRISIS_RESOURCE category passes when health = crisis.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from .bus_integration import publish_emergency_credit

logger = logging.getLogger(__name__)


class CrisisType(str, Enum):
    """Types of crisis events that can trigger emergency pathway."""
    MEDICAL = "medical"          # Health emergency — ONLY this type triggers Module 5
    CROP_DISEASE = "crop_disease"  # Crop disease — handled by scheme access
    LIVESTOCK = "livestock"        # Livestock death/injury — handled by scheme access
    WEATHER = "weather"            # Weather event — handled by scheme access
    OTHER = "other"


@dataclass
class EmergencyCreditInfo:
    """Information about available emergency credit for a crisis."""

    source_name: str
    source_type: str              # e.g. "government_scheme", "bank", "nbfc"
    credit_amount_rupees: float
    interest_rate_percent: Optional[float]
    repayment_months: Optional[int]
    eligibility_criteria: str
    application_method: str
    contact_info: Optional[str] = None


# ---------------------------------------------------------------------------
# Ayushman Bharat Jan Arogya Yojana (AB PM-JAY) — flagship government health cover
# ---------------------------------------------------------------------------
_AYUSHMAN_BHARAT = EmergencyCreditInfo(
    source_name="Ayushman Bharat PM-JAY (Pradhan Mantri Jan Arogya Yojana)",
    source_type="government_scheme",
    credit_amount_rupees=500000.0,
    interest_rate_percent=None,
    repayment_months=None,
    eligibility_criteria="Families identified via SECC 2011 database; no premium for eligible families",
    application_method="Contact nearest Common Service Centre (CSC), empanelled hospital, or state nodal officer",
    contact_info="Toll-free: 14555 | Website: pmjay.gov.in",
)


# Additional emergency health resources by state (Phase 1: static table)
_STATE_HEALTH_RESOURCES: dict[str, list[EmergencyCreditInfo]] = {
    "Maharashtra": [
        EmergencyCreditInfo(
            source_name="Maharashtra State Health Agency - MAHAARB",
            source_type="government_scheme",
            credit_amount_rupees=1500000.0,
            interest_rate_percent=None,
            repayment_months=None,
            eligibility_criteria="Maharashtra residents below poverty line; MAHAARB card holders",
            application_method="Apply at district civil hospital or CSC",
            contact_info="MAHAARB: 1800-233-2200",
        ),
    ],
    "Karnataka": [
        EmergencyCreditInfo(
            source_name="Arogya Karnataka",
            source_type="government_scheme",
            credit_amount_rupees=500000.0,
            interest_rate_percent=None,
            repayment_months=None,
            eligibility_criteria="Karnataka residents; below SECC poverty line",
            application_method="Apply at nearest government hospital or CSC",
            contact_info=None,
        ),
    ],
}


def get_emergency_health_resources(
    state: str,
    district: Optional[str] = None,
) -> list[EmergencyCreditInfo]:
    """Return available emergency health resources for a state.

    Phase 1: static table. Phase 2: would query scheme eligibility API.
    """
    resources = [_AYUSHMAN_BHARAT]
    state_resources = _STATE_HEALTH_RESOURCES.get(state, [])
    resources.extend(state_resources)
    return resources


def is_health_crisis_event(
    health_status: str,
    crisis_type: Optional[str] = None,
) -> bool:
    """Return True if this event qualifies as a health crisis for Module 5.

    Per specs/09-constraint-priority-engine.md §3.1:
    - health_status must be "crisis"
    - crisis_type must be "medical" specifically
    """
    return (
        health_status == "crisis"
        and crisis_type == CrisisType.MEDICAL.value
    )


def publish_health_crisis_resource(
    farmer_id: int,
    state: str,
    district: Optional[str] = None,
    credit_amount_rupees: Optional[float] = None,
    crisis_type: CrisisType = CrisisType.MEDICAL,
    action: Optional[str] = None,
) -> None:
    """Publish a health crisis resource recommendation for a farmer in crisis.

    This is the ONLY function in Module 5 that publishes to the bus.
    Per Gate 1: health_crisis_resource is the ONLY category that passes
    when health_status = crisis.

    Args:
        farmer_id: ID of the farmer in crisis
        state: Farmer's state
        district: Farmer's district
        credit_amount_rupees: Optional estimated credit need
        crisis_type: Must be MEDICAL for Module 5 (other types handled elsewhere)
        action: Optional custom action text (generated if not provided)
    """
    if crisis_type != CrisisType.MEDICAL:
        logger.warning(
            "Module 5 publishes only MEDICAL crisis. Received %s. Ignoring.",
            crisis_type,
        )
        return

    # Get available resources
    resources = get_emergency_health_resources(state, district)
    primary_resource = resources[0] if resources else None

    if action is None and primary_resource:
        action = (
            f"Access emergency health fund via {primary_resource.source_name}. "
            f"Coverage up to ₹{primary_resource.credit_amount_rupees:,.0f} — no premium for eligible families. "
            f"Apply at nearest CSC or empanelled hospital. "
            f"Toll-free: 14555."
        )
    elif action is None:
        action = (
            "Contact your nearest government hospital or Common Service Centre (CSC) "
            "for emergency health assistance programs."
        )

    publish_emergency_credit(
        action=action,
        credit_amount_rupees=(
            credit_amount_rupees
            or (primary_resource.credit_amount_rupees if primary_resource else None)
        ),
        crisis_type=crisis_type.value,
    )


class EmergencyCreditPathway:
    """Service for evaluating and publishing emergency credit recommendations.

    Usage:
        pathway = EmergencyCreditPathway()
        pathway.evaluate_and_publish(
            farmer_id=123,
            state="Maharashtra",
            district="Nashik",
            health_status="crisis",
            crisis_type=CrisisType.MEDICAL,
            estimated_credit_need=80000.0,
        )
    """

    def evaluate_and_publish(
        self,
        farmer_id: int,
        state: str,
        district: Optional[str],
        health_status: str,
        crisis_type: CrisisType,
        estimated_credit_need: Optional[float] = None,
    ) -> bool:
        """Evaluate whether to publish an emergency credit recommendation.

        Returns:
            True if a recommendation was published, False if not applicable.
        """
        if not is_health_crisis_event(health_status, crisis_type.value):
            return False

        publish_health_crisis_resource(
            farmer_id=farmer_id,
            state=state,
            district=district,
            credit_amount_rupees=estimated_credit_need,
            crisis_type=crisis_type,
        )
        return True
