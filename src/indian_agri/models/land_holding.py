from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .base import OfflineMixin
from .enums import IrrigationType, TenureType


class LandHolding(OfflineMixin):
    """Land holding entity — links farmer to cultivated land parcels."""

    model_config = ConfigDict(use_enum_values=True)

    farmer_id: int = Field(foreign_key=True, index=True)
    area: float = Field(gt=0, description="Area in hectares")
    area_unit: str = Field(default="hectare", max_length=20)

    # Tenure
    tenure_type: TenureType = TenureType.OWNER
    tenure_document_ref: Optional[str] = Field(
        default=None, max_length=200
    )  # land record reference

    # Location
    survey_no: Optional[str] = Field(default=None, max_length=50)
    village: str = Field(max_length=200)
    district: str = Field(max_length=100)
    state: str = Field(max_length=100)

    # Soil
    soil_type: Optional[str] = Field(default=None, max_length=50)
    soil_npk_ref: Optional[str] = Field(
        default=None, max_length=100
    )  # link to Soil Health Card data
    irrigation_type: IrrigationType = IrrigationType.RAINFED
    irrigation_sources: Optional[str] = Field(
        default=None, max_length=200
    )  # comma-separated

    # Soil Health Card reference
    soil_health_card_no: Optional[str] = Field(default=None, max_length=50)
    shc_fetched_at: Optional[datetime] = None

    # Geolocation
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    def __init__(self, **data):
        if data.get("created_at") is None:
            data["created_at"] = datetime.utcnow()
        if data.get("updated_at") is None:
            data["updated_at"] = datetime.utcnow()
        super().__init__(**data)
