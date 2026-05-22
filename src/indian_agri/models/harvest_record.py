from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .base import OfflineMixin


class HarvestRecord(OfflineMixin):
    """Harvest record — captures harvest output for a crop cycle."""

    model_config = ConfigDict(use_enum_values=True)

    crop_cycle_id: int = Field(foreign_key=True, index=True)
    farmer_id: int = Field(foreign_key=True, index=True)

    harvest_date: date

    # Quantity
    quantity_harvested: float = Field(gt=0)
    unit: str = Field(default="quintal", max_length=20)

    # Quality
    quality_grade: Optional[str] = Field(
        default=None, max_length=20
    )  # A | B | C | below_par

    # Post-harvest handling
    storage_type: Optional[str] = Field(
        default=None, max_length=50
    )  # own_storage | sold_immediately | cold_storage
    storage_location: Optional[str] = Field(default=None, max_length=200)
    storage_cost: Optional[float] = None

    # Distress sale flag — computed from cash_flow_status + market conditions
    distress_sale_flag: bool = False
    distress_sale_reason: Optional[str] = Field(default=None, max_length=200)

    # Field agent attestation
    attested_by_agent_id: Optional[str] = Field(default=None, max_length=50)
    attested_at: Optional[datetime] = None

    def __init__(self, **data):
        if data.get("created_at") is None:
            data["created_at"] = datetime.utcnow()
        if data.get("updated_at") is None:
            data["updated_at"] = datetime.utcnow()
        super().__init__(**data)

    def compute_distress_sale(self, cash_flow_status: str) -> bool:
        """Compute distress_sale_flag based on cash flow status.

        Per ground truth collection spec, distress sale occurs when farmer
        is in DEFICIT or EMERGENCY cash flow status.
        """
        if cash_flow_status in ("deficit", "emergency"):
            self.distress_sale_flag = True
            self.distress_sale_reason = f"Cash flow status: {cash_flow_status}"
        return self.distress_sale_flag
