from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    age = Column(Integer, nullable=False)

    phone = Column(String(20), nullable=False)

    doctor_id = Column(
        Integer,
        ForeignKey("doctors.id"),
        nullable=True
    )

    # Relationship with Doctor
    doctor = relationship(
        "Doctor",
        back_populates="patients"
    )

    # Relationship with Appointments
    appointments = relationship(
        "Appointment",
        back_populates="patient"
    )

    # Relationship with Billings
    billings = relationship(
        "Billing",
        back_populates="patient"
    )