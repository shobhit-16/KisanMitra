from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .base import OfflineMixin
from .enums import CashFlowStatus, HealthStatus, SellingWindow, TenureType, TimeCriticality


class ConstraintState(OfflineMixin):
    """Constraint state entity — CPE's view of a farmer's active constraints.

    This is the canonical state that CPE gates evaluate against.
    Updated by Income Engine modules and enrollment workflow.

    Per specs/09-constraint-priority-engine.md §1, the CPE uses
    constraint state to suppress or pass recommendations.
    """

    model_config = ConfigDict(use_enum_values=True)

    farmer_id: int = Field(unique=True, foreign_key=True, index=True)

    # Gate 1: Health constraint
    health_status: HealthStatus = HealthStatus.NORMAL
    health_status_updated_at: Optional[datetime] = None
    health_crisis_type: Optional[str] = Field(
        default=None, max_length=100
    )  # medical | crop_disease | livestock

    # Gate 2: Tenure constraint
    tenure_type: TenureType = TenureType.OWNER
    tenure_type_updated_at: Optional[datetime] = None
    requires_tenure_security: bool = False  # metadata: true for tenant farmers
    tenure_verified: bool = False
    tenure_unverified_reason: Optional[str] = None

    # Gate 3: Cash flow constraint
    cash_flow_status: CashFlowStatus = CashFlowStatus.BALANCED
    cash_flow_status_updated_at: Optional[datetime] = None
    capital_intensity: Optional[str] = Field(
        default=None, max_length=50
    )  # low | medium | high — metadata for Gate 3
    obligation_due_within_30_days: Optional[float] = None  # rupees outstanding
    cash_flow_confidence: float = Field(
        default=0.5, ge=0.0, le=1.0
    )  # confidence in assessment

    # Gate 4: Selling window constraint
    selling_window: SellingWindow = SellingWindow.CLOSED
    selling_window_updated_at: Optional[datetime] = None
    harvest_within_7_days: bool = False  # derived from crop cycle

    # Gate 5: Time criticality constraint
    time_criticality: TimeCriticality = TimeCriticality.MEDIUM_TERM
    time_criticality_updated_at: Optional[datetime] = None
    sowing_window_active: bool = False  # true during sowing period
    harvest_window_active: bool = False  # true during harvest period

    # CPE computation metadata
    last_evaluated_at: Optional[datetime] = None
    last_recommendation_id: Optional[str] = None
    active_gates: list[str] = Field(
        default_factory=list
    )  # list of gate names that suppressed

    # Cascade suppression flag
    cascade_suppression: bool = False  # true if any gate suppressed

    def __init__(self, **data):
        if data.get("created_at") is None:
            data["created_at"] = datetime.utcnow()
        if data.get("updated_at") is None:
            data["updated_at"] = datetime.utcnow()
        super().__init__(**data)

    def is_any_gate_active(self) -> bool:
        """Return True if any constraint gate is active."""
        return (
            self.health_status == HealthStatus.CRISIS
            or self.tenure_type == TenureType.TENANT
            or self.cash_flow_status in (CashFlowStatus.DEFICIT, CashFlowStatus.EMERGENCY)
            or self.selling_window == SellingWindow.OPEN
            or self.time_criticality == TimeCriticality.IMMEDIATE
        )

    def active_gate_names(self) -> list[str]:
        """Return list of active gate names."""
        gates = []
        if self.health_status == HealthStatus.CRISIS:
            gates.append("gate1_health")
        if self.tenure_type == TenureType.TENANT:
            gates.append("gate2_tenure")
        if self.cash_flow_status in (CashFlowStatus.DEFICIT, CashFlowStatus.EMERGENCY):
            gates.append("gate3_cashflow")
        if self.selling_window == SellingWindow.OPEN:
            gates.append("gate4_selling_window")
        if self.time_criticality == TimeCriticality.IMMEDIATE:
            gates.append("gate5_time_criticality")
        return gates
