from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.orm import relationship

from app.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    __table_args__ = (
        CheckConstraint(
            "status IN ('scheduled', 'completed', 'cancelled')",
            name="check_appointment_status"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    doctor_id = Column(
        Integer,
        ForeignKey("doctors.id"),
        nullable=False,
        index=True
    )

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False,
        index=True
    )

    appointment_date = Column(
        DateTime,
        nullable=False,
        index=True
    )

    status = Column(
        String(20),
        nullable=False,
        default="scheduled",
        index=True
    )

    reason = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationship with Doctor
    doctor = relationship(
        "Doctor",
        back_populates="appointments"
    )

    # Relationship with Patient
    patient = relationship(
        "Patient",
        back_populates="appointments"
    )

    # Relationship with Billing
    billing = relationship(
        "Billing",
        back_populates="appointment",
        uselist=False
    )