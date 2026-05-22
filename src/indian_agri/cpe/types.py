"""CPE types — Recommendation message format per specs/09-constraint-priority-engine.md §4.1."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class EngineName(str, Enum):
    """Which engine published this recommendation."""
    INCOME = "income"
    CLIMATE = "climate"
    SOIL = "soil"


class RecommendationCategory(str, Enum):
    """Category of recommendation — determines which gates apply."""
    SELLING = "selling"
    INPUT = "input"
    WEATHER = "weather"
    PRACTICE = "practice"
    FINANCIAL = "financial"
    HEALTH = "health"
    HEALTH_CRISIS_RESOURCE = "health_crisis_resource"  # Gate 1 passes these


class CapitalIntensity(str, Enum):
    """How much capital is required to act on this recommendation."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TimeToAction(str, Enum):
    """How quickly the farmer must act."""
    IMMEDIATE = "immediate"  # hours
    HOURS = "hours"  # within 24 hours
    DAYS = "days"  # 1-7 days
    WEEKS = "weeks"  # 7+ days


class TenureRequirement(str, Enum):
    """Whether this recommendation requires tenure security."""
    ANY = "any"  # works for anyone
    TENANT_VIABLE = "tenant_viable"  # works for tenant farmers
    OWNER_ONLY = "owner_only"  # requires multi-year tenure


@dataclass
class Recommendation:
    """Recommendation message published to the Recommendation Bus.

    Per specs/09-constraint-priority-engine.md §4.1.
    """

    engine: EngineName
    module: str  # e.g. "module_4_selling", "module_2_cashflow"
    category: RecommendationCategory
    action: str  # human-readable action description
    target_date: Optional[datetime] = None

    # Gate evaluation metadata
    requires_tenure_security: bool = False
    tenure_requirement: TenureRequirement = TenureRequirement.ANY
    capital_intensity: CapitalIntensity = CapitalIntensity.NONE
    time_to_action: TimeToAction = TimeToAction.DAYS
    priority_for_engine: int = 1  # 1 = highest priority from this engine

    # Tracking
    recommendation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    published_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for bus transport."""
        return {
            "recommendation_id": self.recommendation_id,
            "engine": self.engine.value,
            "module": self.module,
            "category": self.category.value,
            "action": self.action,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "requires_tenure_security": self.requires_tenure_security,
            "tenure_requirement": self.tenure_requirement.value,
            "capital_intensity": self.capital_intensity.value,
            "time_to_action": self.time_to_action.value,
            "priority_for_engine": self.priority_for_engine,
            "published_at": self.published_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Recommendation":
        """Deserialize from bus transport."""
        return cls(
            recommendation_id=data["recommendation_id"],
            engine=EngineName(data["engine"]),
            module=data["module"],
            category=RecommendationCategory(data["category"]),
            action=data["action"],
            target_date=datetime.fromisoformat(data["target_date"]) if data.get("target_date") else None,
            requires_tenure_security=data.get("requires_tenure_security", False),
            tenure_requirement=TenureRequirement(data.get("tenure_requirement", "any")),
            capital_intensity=CapitalIntensity(data.get("capital_intensity", "none")),
            time_to_action=TimeToAction(data.get("time_to_action", "days")),
            priority_for_engine=data.get("priority_for_engine", 1),
            published_at=datetime.fromisoformat(data["published_at"]) if data.get("published_at") else datetime.utcnow(),
            metadata=data.get("metadata", {}),
        )


@dataclass
class SuppressedReason:
    """Why a recommendation was suppressed at a gate."""
    engine: EngineName
    module: str
    recommendation_id: str
    reason: str  # e.g. "health_crisis_active", "cash_flow_deficit"
    gate: int  # 1-5


@dataclass
class CPEOutput:
    """Output from CPE.evaluate() — exactly one recommendation or suppression.

    Per specs/09-constraint-priority-engine.md §4.2.
    """
    output_type: str  # "recommendation" or "suppression"
    recommendation: Optional[Recommendation] = None
    suppressed_reasons: list[SuppressedReason] = field(default_factory=list)
    active_constraint: Optional[str] = None  # e.g. "health", "cash_flow"
    confidence_note: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_type": self.output_type,
            "recommendation": self.recommendation.to_dict() if self.recommendation else None,
            "suppressed_reasons": [
                {
                    "engine": s.engine.value,
                    "module": s.module,
                    "recommendation_id": s.recommendation_id,
                    "reason": s.reason,
                    "gate": s.gate,
                }
                for s in self.suppressed_reasons
            ],
            "active_constraint": self.active_constraint,
            "confidence_note": self.confidence_note,
        }
