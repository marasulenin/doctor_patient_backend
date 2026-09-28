from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    age = Column(
        Integer,
        nullable=False
    )

    phone = Column(
        String(15),
        nullable=False
    )

    address = Column(
        String(255),
        nullable=True
    )

    gender = Column(
        String(20),
        nullable=True
    )

    doctor_id = Column(
        Integer,
        ForeignKey("doctors.id"),
        nullable=True
    )

    doctor = relationship(
        "Doctor",
        back_populates="patients"
    )