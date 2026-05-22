from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .base import OfflineMixin
from .constraint_state import ConstraintState
from .enums import (
    CashFlowStatus,
    ConsentStatus,
    HealthStatus,
    Language,
    LiteracyLevel,
    SellingWindow,
    TenureType,
    TimeCriticality,
)


class Farmer(OfflineMixin):
    """Farmer entity — core agent in the platform.

    Includes CPE constraint state fields (health_status, tenure_type,
    cash_flow_status, selling_window, time_criticality) collected at
    enrollment and updated throughout the crop cycle.
    """

    model_config = ConfigDict(use_enum_values=True)

    # Identity
    name: str = Field(max_length=200)
    phone: str = Field(max_length=15, unique=True, index=True)
    agristack_id: Optional[str] = Field(default=None, max_length=50, unique=True)
    language: Language = Language.ENGLISH
    literacy_level: LiteracyLevel = LiteracyLevel.FUNCTIONAL

    # Location
    village: str = Field(max_length=200)
    district: str = Field(max_length=100)
    state: str = Field(max_length=100)
    pincode: Optional[str] = Field(default=None, max_length=10)

    # Consent
    consent_status: ConsentStatus = ConsentStatus.PENDING
    consent_granted_at: Optional[datetime] = None

    # CPE constraint state — collected at enrollment, updated by Income Engine
    constraint_state_id: Optional[int] = Field(default=None, foreign_key=True, index=True)
    health_status: HealthStatus = HealthStatus.NORMAL
    tenure_type: TenureType = TenureType.OWNER
    cash_flow_status: CashFlowStatus = CashFlowStatus.BALANCED
    selling_window: SellingWindow = SellingWindow.CLOSED
    time_criticality: TimeCriticality = TimeCriticality.MEDIUM_TERM

    # Enrollment metadata
    enrolled_at: Optional[datetime] = None
    enrollment_source: Optional[str] = Field(
        default=None, max_length=50
    )  # ivr | field_agent | fpo | kvk
    field_agent_id: Optional[str] = Field(default=None, max_length=50)

    # Tenure verification (Gate 2)
    tenure_verified: bool = False
    tenure_unverified_reason: Optional[str] = None

    # Women farmer support
    is_women_farmer: bool = False
    shg_name: Optional[str] = Field(default=None, max_length=200)
    alternate_contact_phone: Optional[str] = Field(default=None, max_length=15)

    # CPDP consent (per DPDP Act 2023)
    dpdp_consent_given: bool = False
    dpdp_consent_given_at: Optional[datetime] = None
    dpdp_consent_purpose: Optional[str] = Field(
        default=None, max_length=500
    )

    def update_constraint_state(self) -> ConstraintState:
        """Sync this farmer's raw constraint fields to a ConstraintState entity.

        Called by Income Engine modules after assessment (e.g., cash_flow_assessed,
        harvest_date_entered). Creates or updates the linked ConstraintState.

        Returns the synced ConstraintState.
        """
        from datetime import datetime

        cs = ConstraintState(
            farmer_id=self.id,
            health_status=self.health_status,
            tenure_type=self.tenure_type,
            cash_flow_status=self.cash_flow_status,
            selling_window=self.selling_window,
            time_criticality=self.time_criticality,
            health_status_updated_at=datetime.utcnow() if self.health_status != HealthStatus.NORMAL else None,
            tenure_type_updated_at=datetime.utcnow() if self.tenure_type != TenureType.OWNER else None,
            cash_flow_status_updated_at=datetime.utcnow(),
            selling_window_updated_at=datetime.utcnow() if self.selling_window == SellingWindow.OPEN else None,
            time_criticality_updated_at=datetime.utcnow(),
        )
        return cs

    def record_harvest_date(
        self,
        harvest_date,
        days_until_harvest: Optional[int] = None,
    ) -> None:
        """Record that the farmer has entered or updated their harvest date.

        Sets selling_window = OPEN so Gate 4 passes for selling recommendations.
        Also updates time_criticality based on proximity to harvest.

        Called by the enrollment or crop-cycle workflow when the farmer
        records their expected harvest date.

        Args:
            harvest_date: Expected harvest date
            days_until_harvest: Optional days remaining until harvest
        """
        from datetime import datetime

        self.selling_window = SellingWindow.OPEN
        self.updated_at = datetime.utcnow()

        # Escalate time criticality as harvest approaches
        if days_until_harvest is not None:
            if days_until_harvest <= 3:
                self.time_criticality = TimeCriticality.IMMEDIATE
            elif days_until_harvest <= 7:
                self.time_criticality = TimeCriticality.SHORT_TERM

    # Operational timestamps
    def __init__(self, **data):
        if data.get("created_at") is None:
            data["created_at"] = datetime.utcnow()
        if data.get("updated_at") is None:
            data["updated_at"] = datetime.utcnow()
        super().__init__(**data)


class FarmerPhoneLookup(BaseModel):
    """Phone → Farmer ID lookup for IVR authentication."""

    phone: str = Field(max_length=15, index=True)
    farmer_id: int
    language: Language = Language.ENGLISH
    district: str = Field(max_length=100)
    registered_at: datetime = None

    def __init__(self, **data):
        if data.get("registered_at") is None:
            data["registered_at"] = datetime.utcnow()
        super().__init__(**data)
