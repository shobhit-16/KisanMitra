"""Constraint Priority Engine (CPE) — suppresses recommendations that violate farmer constraints."""

from .types import (
    CapitalIntensity,
    EngineName,
    Recommendation,
    RecommendationCategory,
    TenureRequirement,
    TimeToAction,
)
from .bus import RecommendationBus
from .gates import (
    GateResult,
    SUPPRESS,
    PASS,
    health_gate,
    tenure_gate,
    cash_flow_gate,
    selling_window_gate,
    time_criticality_gate,
)
from .engine import CPE, CPEOutput

__all__ = [
    "Recommendation",
    "RecommendationBus",
    "CPE",
    "CPEOutput",
    "GateResult",
    "SUPPRESS",
    "PASS",
    "health_gate",
    "tenure_gate",
    "cash_flow_gate",
    "selling_window_gate",
    "time_criticality_gate",
    "EngineName",
    "RecommendationCategory",
    "CapitalIntensity",
    "TimeToAction",
    "TenureRequirement",
]
