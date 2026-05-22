from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime
from enum import Enum


class LandTenure(str, Enum):
    OWNER = "OWNER"
    TENANT = "TENANT"
    SHARECROPPER = "SHARECROPPER"


class CropType(str, Enum):
    RABI_ONION = "RABI_ONION"
    KHARIF_PADDY = "KHARIF_PADDY"
    RABI_WHEAT = "RABI_WHEAT"
    SUMMER_MAIZE = "SUMMER_MAIZE"


class Season(str, Enum):
    RABI = "RABI"
    KHARIF = "KHARIF"
    SUMMER = "SUMMER"


class Language(str, Enum):
    MARATHI = "MARATHI"
    HINDI = "HINDI"
    ENGLISH = "ENGLISH"


class ObligationType(str, Enum):
    KCC_EMI = "KCC_EMI"
    SCHOOL_FEE = "SCHOOL_FEE"
    LAND_RENT = "LAND_RENT"
    COOPERATIVE_DUE = "COOPERATIVE_DUE"
    INSURANCE_PREMIUM = "INSURANCE_PREMIUM"
    WATER_ELECTRICITY = "WATER_ELECTRICITY"
    OTHER = "OTHER"


class FarmerCreate(BaseModel):
    phone: str = Field(..., min_length=10, max_length=10)
    name: str
    village: str
    block: str
    district: str = "NASHIK"
    state: str = "MAHARASHTRA"
    land_size: float = Field(..., gt=0, le=100)
    land_tenure: LandTenure
    crop_type: CropType
    season: Season
    primary_language: Language = Language.MARATHI

    @field_validator("phone")
    @classmethod
    def phone_must_be_digits(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("Phone number must contain only digits")
        return v


class Farmer(FarmerCreate):
    created_at: datetime
    updated_at: datetime
    is_active: bool = True


class ObligationCreate(BaseModel):
    id: str
    phone: str = Field(..., min_length=10, max_length=10)
    type: ObligationType
    amount: int = Field(..., gt=0)
    due_date: date
    description: Optional[str] = None
    reminder_date: Optional[date] = None
    reminder_flag: bool = False


class Obligation(ObligationCreate):
    is_paid: bool = False
    paid_date: Optional[date] = None
    paid_amount: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class SaleCreate(BaseModel):
    id: str
    phone: str = Field(..., min_length=10, max_length=10)
    sale_date: date
    quantity_quintal: float = Field(..., gt=0, le=1000)
    price_per_quintal: int = Field(..., ge=0)
    mandi: str
    is_distress: Optional[bool] = None
    distress_reason: Optional[str] = None
    notes: Optional[str] = None


class Sale(SaleCreate):
    total_revenue: int
    created_at: datetime


class PriceAlertCreate(BaseModel):
    id: str
    phone: str = Field(..., min_length=10, max_length=10)
    enabled: bool = True
    drop_threshold: int = Field(default=2, ge=1, le=10)
    rise_threshold_percent: int = Field(default=8, ge=1, le=50)
    preferred_mandis: list[str] = Field(default=["Lasalgaon", "Niphad"])


class PriceAlert(PriceAlertCreate):
    created_at: datetime
