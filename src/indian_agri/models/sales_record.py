from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .base import OfflineMixin
from .enums import BuyerType


class SalesRecord(OfflineMixin):
    """Sales record — captures each sale event of harvested crop."""

    model_config = ConfigDict(use_enum_values=True)

    harvest_record_id: int = Field(foreign_key=True, index=True)
    farmer_id: int = Field(foreign_key=True, index=True)
    crop_cycle_id: int = Field(foreign_key=True, index=True)

    sale_date: date

    # Quantity sold
    quantity_sold: float = Field(gt=0)
    unit: str = Field(default="quintal", max_length=20)

    # Price
    price_per_unit: float = Field(gt=0)
    total_amount: float = Field(gt=0)

    # Mandi / buyer
    mandi_name: Optional[str] = Field(default=None, max_length=200)
    buyer_type: BuyerType = BuyerType.MANDI
    buyer_name: Optional[str] = Field(default=None, max_length=200)

    # e-NAM transaction
    enam_transaction_id: Optional[str] = Field(default=None, max_length=100)
    enam_sale_id: Optional[str] = Field(default=None, max_length=100)

    # Distress sale flag — per ground truth collection spec
    distress_sale_flag: bool = False
    distress_sale_reason: Optional[str] = Field(default=None, max_length=200)

    # Payment
    payment_received: bool = False
    payment_date: Optional[date] = None

    # Recall survey tracking (7/30/60 day ground truth)
    recall_7day_done: bool = False
    recall_30day_done: bool = False
    recall_60day_done: bool = False

    def __init__(self, **data):
        if data.get("created_at") is None:
            data["created_at"] = datetime.utcnow()
        if data.get("updated_at") is None:
            data["updated_at"] = datetime.utcnow()
        if "total_amount" not in data and "price_per_unit" in data and "quantity_sold" in data:
            data["total_amount"] = data["price_per_unit"] * data["quantity_sold"]
        super().__init__(**data)
