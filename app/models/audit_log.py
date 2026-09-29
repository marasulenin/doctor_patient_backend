from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    action = Column(
        String(50),
        nullable=False,
        index=True
    )

    resource = Column(
        String(50),
        nullable=False,
        index=True
    )

    resource_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    description = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )