from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    specialization = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    is_active = Column(
        Boolean,
        default=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="doctor"
    )

    patients = relationship(
        "Patient",
        back_populates="doctor"
    )