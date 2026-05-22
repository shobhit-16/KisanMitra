"""Income Engine → Recommendation Bus integration.

Provides a simple synchronous interface for Income Engine modules to publish
recommendations. The async RecommendationBus.publish() is wrapped so modules
can call publish_recommendation() without needing to be async.

Per specs/09-constraint-priority-engine.md §4: engines publish recommendations
to the Recommendation Bus; CPE subscribes and evaluates.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Optional

from ..cpe.bus import get_recommendation_bus
from ..cpe.types import (
    CapitalIntensity,
    EngineName,
    Recommendation,
    RecommendationCategory,
    TenureRequirement,
    TimeToAction,
)


def publish_recommendation(
    *,
    module: str,
    category: RecommendationCategory,
    action: str,
    capital_intensity: CapitalIntensity = CapitalIntensity.NONE,
    tenure_requirement: TenureRequirement = TenureRequirement.ANY,
    requires_tenure_security: bool = False,
    time_to_action: TimeToAction = TimeToAction.DAYS,
    priority_for_engine: int = 1,
    target_date: Optional[datetime] = None,
    metadata: Optional[dict] = None,
) -> Recommendation:
    """Publish a recommendation from an Income Engine module to the Recommendation Bus.

    This is the canonical entry point for all Income Engine modules.
    Sync wrapper around RecommendationBus.publish().

    Args:
        module: Which Income Engine module is publishing (e.g. "module_2_cashflow")
        category: RecommendationCategory for CPE gate evaluation
        action: Human-readable recommendation text
        capital_intensity: Affects Gate 3 (Cash Flow)
        tenure_requirement: Affects Gate 2 (Tenure)
        requires_tenure_security: Affects Gate 2 (Tenure)
        time_to_action: Affects Gate 5 (Time Criticality)
        priority_for_engine: 1 = highest priority from Income Engine
        target_date: Optional date the recommendation targets
        metadata: Additional context for this recommendation

    Returns:
        The published Recommendation object
    """
    rec = Recommendation(
        engine=EngineName.INCOME,
        module=module,
        category=category,
        action=action,
        capital_intensity=capital_intensity,
        tenure_requirement=tenure_requirement,
        requires_tenure_security=requires_tenure_security,
        time_to_action=time_to_action,
        priority_for_engine=priority_for_engine,
        target_date=target_date,
        metadata=metadata or {},
    )

    bus = get_recommendation_bus()
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop — create one
        asyncio.run(bus.publish(rec))
    else:
        # Inside an async context — create task
        loop.create_task(bus.publish(rec))

    return rec


# ---------------------------------------------------------------------------
# Module-specific publish helpers (examples for Phase 1)
# ---------------------------------------------------------------------------

def publish_selling_recommendation(
    *,
    action: str,
    price_above_msp: bool = False,
    days_until_harvest: Optional[int] = None,
    priority: int = 1,
) -> Recommendation:
    """Publish a selling recommendation from Module 4 (SellingDecisionGuide).

    Args:
        action: e.g. "Sell onion crop at current prices"
        price_above_msp: True if modal price > MSP — higher confidence
        days_until_harvest: None if harvest done, or days remaining
        priority: From 1 (highest)
    """
    metadata = {"price_above_msp": price_above_msp}
    if days_until_harvest is not None:
        metadata["days_until_harvest"] = days_until_harvest

    return publish_recommendation(
        module="module_4_selling",
        category=RecommendationCategory.SELLING,
        action=action,
        capital_intensity=CapitalIntensity.NONE,
        time_to_action=TimeToAction.IMMEDIATE if days_until_harvest is not None and days_until_harvest <= 3 else TimeToAction.DAYS,
        priority_for_engine=priority,
        metadata=metadata,
    )


def publish_emergency_credit(
    *,
    action: str,
    credit_amount_rupees: Optional[float] = None,
    crisis_type: str = "health",
    priority: int = 1,
) -> Recommendation:
    """Publish a health crisis resource recommendation from Module 5.

    Per specs/09-constraint-priority-engine.md §3.1: Gate 1 passes ONLY
    health_crisis_resource recommendations when health_status = crisis.

    Args:
        action: e.g. "Access emergency health fund via Jan Arogya Yojana"
        credit_amount_rupees: Optional credit need amount
        crisis_type: "medical" | "crop_disease" | "livestock"
        priority: From 1 (highest)
    """
    metadata = {"crisis_type": crisis_type}
    if credit_amount_rupees is not None:
        metadata["credit_amount_rupees"] = credit_amount_rupees

    return publish_recommendation(
        module="module_5_emergency_credit",
        category=RecommendationCategory.HEALTH_CRISIS_RESOURCE,
        action=action,
        capital_intensity=CapitalIntensity.NONE,
        tenure_requirement=TenureRequirement.ANY,
        requires_tenure_security=False,
        time_to_action=TimeToAction.IMMEDIATE,
        priority_for_engine=priority,
        metadata=metadata,
    )
