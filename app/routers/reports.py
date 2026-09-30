from datetime import date, datetime, time
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.billing import Billing
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.report import (
    DailyRevenueResponse,
    DoctorRevenueResponse,
    RevenueReportResponse,
)


router = APIRouter(
    prefix="/api/v1/reports",
    tags=["Reports"]
)


# ============================================================
# REVENUE REPORT
# ============================================================

@router.get(
    "/revenue",
    response_model=RevenueReportResponse
)
def get_revenue_report(
    doctor_id: int | None = Query(
        default=None,
        gt=0,
        description="Filter revenue by doctor ID"
    ),

    from_date: date | None = Query(
        default=None,
        alias="from",
        description="Revenue start date"
    ),

    to_date: date | None = Query(
        default=None,
        alias="to",
        description="Revenue end date"
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    # ========================================================
    # AUTHORIZATION
    # ========================================================

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # ========================================================
    # DATE VALIDATION
    # ========================================================

    if (
        from_date is not None
        and to_date is not None
        and from_date > to_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="from date cannot be greater than to date"
        )

    # ========================================================
    # DOCTOR VALIDATION
    # ========================================================

    if doctor_id is not None:

        doctor = (
            db.query(Doctor)
            .filter(
                Doctor.id == doctor_id
            )
            .first()
        )

        if doctor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found"
            )

    # ========================================================
    # DATE RANGE
    # ========================================================

    from_datetime = None
    to_datetime = None

    if from_date is not None:
        from_datetime = datetime.combine(
            from_date,
            time.min
        )

    if to_date is not None:
        to_datetime = datetime.combine(
            to_date,
            time.max
        )

    # ========================================================
    # BASE QUERY
    #
    # Revenue is calculated only from:
    # - active billings
    # - paid billings
    # ========================================================

    base_filters = [
        Billing.is_active.is_(True),
        Billing.payment_status == "paid"
    ]

    # ========================================================
    # DOCTOR FILTER
    # ========================================================

    if doctor_id is not None:

        base_filters.append(
            Billing.doctor_id == doctor_id
        )

    # ========================================================
    # FROM DATE FILTER
    # ========================================================

    if from_datetime is not None:

        base_filters.append(
            Billing.created_at >= from_datetime
        )

    # ========================================================
    # TO DATE FILTER
    # ========================================================

    if to_datetime is not None:

        base_filters.append(
            Billing.created_at <= to_datetime
        )

    # ========================================================
    # TOTAL REVENUE
    # ========================================================

    total_revenue = (
        db.query(
            func.coalesce(
                func.sum(Billing.total_amount),
                0
            )
        )
        .filter(*base_filters)
        .scalar()
    )

    if total_revenue is None:
        total_revenue = Decimal("0.00")

    else:
        total_revenue = Decimal(
            str(total_revenue)
        )

    # ========================================================
    # REVENUE PER DOCTOR
    # ========================================================

    doctor_revenue_rows = (
        db.query(
            Doctor.id.label("doctor_id"),
            Doctor.name.label("doctor_name"),
            func.coalesce(
                func.sum(Billing.total_amount),
                0
            ).label("total_revenue")
        )
        .join(
            Billing,
            Billing.doctor_id == Doctor.id
        )
        .filter(*base_filters)
        .group_by(
            Doctor.id,
            Doctor.name
        )
        .order_by(
            Doctor.id
        )
        .all()
    )

    revenue_by_doctor = []

    for row in doctor_revenue_rows:

        revenue_by_doctor.append(
            DoctorRevenueResponse(
                doctor_id=row.doctor_id,
                doctor_name=row.doctor_name,
                total_revenue=Decimal(
                    str(row.total_revenue)
                )
            )
        )

    # ========================================================
    # REVENUE PER DAY
    # ========================================================

    # SQLite uses DATE(created_at)
    revenue_by_day_rows = (
        db.query(
            func.date(
                Billing.created_at
            ).label("revenue_date"),

            func.coalesce(
                func.sum(Billing.total_amount),
                0
            ).label("total_revenue")
        )
        .filter(*base_filters)
        .group_by(
            func.date(
                Billing.created_at
            )
        )
        .order_by(
            func.date(
                Billing.created_at
            )
        )
        .all()
    )

    revenue_by_day = []

    for row in revenue_by_day_rows:

        revenue_by_day.append(
            DailyRevenueResponse(
                date=date.fromisoformat(
                    str(row.revenue_date)
                ),
                total_revenue=Decimal(
                    str(row.total_revenue)
                )
            )
        )

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return RevenueReportResponse(
        from_date=from_date,
        to_date=to_date,
        doctor_id=doctor_id,
        total_revenue=total_revenue,
        revenue_by_doctor=revenue_by_doctor,
        revenue_by_day=revenue_by_day
    )