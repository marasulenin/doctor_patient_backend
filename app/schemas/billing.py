from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# PAYMENT TYPES
# ============================================================

PaymentStatus = Literal[
    "pending",
    "paid",
    "cancelled"
]

PaymentMode = Literal[
    "cash",
    "card",
    "upi"
]


# ============================================================
# CREATE BILLING
# ============================================================

class BillingCreate(BaseModel):

    patient_id: int = Field(
        ...,
        gt=0
    )

    doctor_id: int = Field(
        ...,
        gt=0
    )

    appointment_id: int | None = Field(
        default=None,
        gt=0
    )

    consultation_fee: Decimal = Field(
        default=Decimal("0.00"),
        ge=0
    )

    additional_charges: Decimal = Field(
        default=Decimal("0.00"),
        ge=0
    )

    payment_status: PaymentStatus = "pending"

    payment_mode: PaymentMode | None = None


# ============================================================
# FULL UPDATE - PUT
# ============================================================

class BillingUpdate(BaseModel):

    patient_id: int = Field(
        ...,
        gt=0
    )

    doctor_id: int = Field(
        ...,
        gt=0
    )

    appointment_id: int | None = Field(
        default=None,
        gt=0
    )

    consultation_fee: Decimal = Field(
        default=Decimal("0.00"),
        ge=0
    )

    additional_charges: Decimal = Field(
        default=Decimal("0.00"),
        ge=0
    )

    payment_status: PaymentStatus = "pending"

    payment_mode: PaymentMode | None = None


# ============================================================
# PARTIAL UPDATE - PATCH
# ============================================================

class BillingPatch(BaseModel):

    patient_id: int | None = Field(
        default=None,
        gt=0
    )

    doctor_id: int | None = Field(
        default=None,
        gt=0
    )

    appointment_id: int | None = Field(
        default=None,
        gt=0
    )

    consultation_fee: Decimal | None = Field(
        default=None,
        ge=0
    )

    additional_charges: Decimal | None = Field(
        default=None,
        ge=0
    )

    payment_status: PaymentStatus | None = None

    payment_mode: PaymentMode | None = None


# ============================================================
# BILLING RESPONSE
# ============================================================

class BillingResponse(BaseModel):

    id: int

    patient_id: int

    doctor_id: int

    appointment_id: int | None

    consultation_fee: Decimal

    additional_charges: Decimal

    total_amount: Decimal

    payment_status: PaymentStatus

    payment_mode: PaymentMode | None

    is_active: bool

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# PAGINATED BILLING RESPONSE - LEVEL 28
# ============================================================

class BillingListResponse(BaseModel):

    items: list[BillingResponse]

    total: int

    page: int

    limit: int

    total_pages: int