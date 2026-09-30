from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Billing(Base):
    __tablename__ = "billings"

    __table_args__ = (
        UniqueConstraint(
            "appointment_id",
            name="uq_billing_appointment_id"
        ),
        CheckConstraint(
            "consultation_fee >= 0",
            name="check_consultation_fee_non_negative"
        ),
        CheckConstraint(
            "additional_charges >= 0",
            name="check_additional_charges_non_negative"
        ),
        CheckConstraint(
            "total_amount >= 0",
            name="check_total_amount_non_negative"
        ),
        CheckConstraint(
            "payment_status IN ('pending', 'paid', 'cancelled')",
            name="check_payment_status"
        ),
        CheckConstraint(
            "payment_mode IN ('cash', 'card', 'upi') "
            "OR payment_mode IS NULL",
            name="check_payment_mode"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id"),
        nullable=False,
        index=True
    )

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id"),
        nullable=False,
        index=True
    )

    appointment_id: Mapped[int | None] = mapped_column(
        ForeignKey("appointments.id"),
        nullable=True,
        index=True
    )

    consultation_fee: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )

    additional_charges: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )

    total_amount: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0
    )

    payment_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        index=True
    )

    payment_mode: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationship with Patient
    patient = relationship(
        "Patient",
        back_populates="billings"
    )

    # Relationship with Doctor
    doctor = relationship(
        "Doctor",
        back_populates="billings"
    )

    # Relationship with Appointment
    appointment = relationship(
        "Appointment",
        back_populates="billing",
        uselist=False
    )