from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from .base import OfflineMixin
from .enums import CropCycleStatus, Season


class CropOperation(BaseModel):
    """Single operation in the crop cycle operations log."""

    operation_date: date
    operation_type: str = Field(max_length=50)  # sowing | irrigation | fertilizer | pesticide | harvest
    description: Optional[str] = None
    cost_incurred: Optional[float] = None
    labour_hours: Optional[float] = None


class CropCycle(OfflineMixin):
    """Crop cycle entity — tracks a single crop on a single land holding for one season."""

    model_config = ConfigDict(use_enum_values=True)

    farmer_id: int = Field(foreign_key=True, index=True)
    land_holding_id: int = Field(foreign_key=True, index=True)

    # Crop identification
    crop_code: str = Field(max_length=20, index=True)  # e.g. "onion", "wheat", "soybean"
    crop_name: str = Field(max_length=100)

    # Season and year
    season: Season = Season.KHARIF
    year: int = Field(ge=2020, le=2050)

    # Key dates
    sowing_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    actual_harvest_date: Optional[date] = None

    # Area
    area_sown: float = Field(gt=0, description="Area sown in hectares")

    # Status
    status: CropCycleStatus = CropCycleStatus.SOWING

    # Operations log (stored as JSON list of CropOperation)
    operations_log: list[dict[str, Any]] = Field(default_factory=list)

    # Yield estimation
    expected_yield_quintal: Optional[float] = None
    actual_yield_quintal: Optional[float] = None

    # Cost tracking
    total_input_cost: Optional[float] = None
    total_labour_cost: Optional[float] = None

    def __init__(self, **data):
        if data.get("created_at") is None:
            data["created_at"] = datetime.utcnow()
        if data.get("updated_at") is None:
            data["updated_at"] = datetime.utcnow()
        super().__init__(**data)

    def add_operation(self, operation: CropOperation) -> None:
        """Add an operation to the log."""
        ops = self.operations_log.copy() if self.operations_log else []
        ops.append(operation.model_dump(mode="json"))
        self.operations_log = ops
        self.updated_at = datetime.utcnow()

    def derive_time_criticality(self) -> str:
        """Derive time_criticality from crop cycle dates.

        Returns one of: immediate | near_term | medium_term | long_term
        """
        if self.actual_harvest_date:
            return "immediate"
        if self.expected_harvest_date:
            from datetime import timedelta

            today = date.today()
            days_to_harvest = (self.expected_harvest_date - today).days
            if days_to_harvest <= 7:
                return "immediate"
            elif days_to_harvest <= 30:
                return "near_term"
            elif days_to_harvest <= 90:
                return "medium_term"
            else:
                return "long_term"
        return "medium_term"
