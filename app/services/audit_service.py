
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    user_id: int | None,
    action: str,
    resource: str,
    resource_id: int | None = None,
    description: str | None = None
):
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        description=description
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log

