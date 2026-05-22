from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .base import OfflineMixin


class SchemeEnrollment(OfflineMixin):
    """Scheme enrollment record — tracks farmer enrollment in government schemes.

    Per specs/05-scheme-access.md, schemes include: PM-KISAN, PMFBY,
    Soil Health Card, Kisan Credit Card.
    """

    model_config = ConfigDict(use_enum_values=True)

    farmer_id: int = Field(foreign_key=True, index=True)

    # Scheme identification
    scheme_code: str = Field(max_length=50, index=True)  # pmkisan | pmfby | shc | kcc
    scheme_name: str = Field(max_length=200)

    # Enrollment status
    status: str = Field(
        max_length=30, index=True
    )  # eligible | applied | enrolled | rejected | payment_received

    # Application tracking
    application_date: Optional[date] = None
    enrollment_date: Optional[date] = None
    rejection_reason: Optional[str] = Field(default=None, max_length=500)
    rejection_reason_code: Optional[str] = Field(
        default=None, max_length=50
    )  # name_mismatch | land_record_error | tenant | bank_account

    # Payment tracking
    payment_date: Optional[date] = None
    payment_amount: Optional[float] = None
    payment_reference: Optional[str] = Field(default=None, max_length=100)

    # PMFBY specific
    premium_paid: Optional[float] = None
    sum_insured: Optional[float] = None
    claim_status: Optional[str] = Field(default=None, max_length=50)

    # Document checklist status
    documents_submitted: dict[str, bool] = Field(default_factory=dict)

    # Notification preferences for this scheme
    notify_via_ivr: bool = True
    notify_via_sms: bool = True

    def __init__(self, **data):
        if data.get("created_at") is None:
            data["created_at"] = datetime.utcnow()
        if data.get("updated_at") is None:
            data["updated_at"] = datetime.utcnow()
        super().__init__(**data)
