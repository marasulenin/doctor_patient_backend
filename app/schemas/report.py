from datetime import date
from decimal import Decimal

from pydantic import BaseModel


# ============================================================
# REVENUE BY DOCTOR
# ============================================================

class DoctorRevenueResponse(BaseModel):

    doctor_id: int

    doctor_name: str

    total_revenue: Decimal


# ============================================================
# REVENUE BY DAY
# ============================================================

class DailyRevenueResponse(BaseModel):

    date: date

    total_revenue: Decimal


# ============================================================
# REVENUE REPORT RESPONSE
# ============================================================

class RevenueReportResponse(BaseModel):

    from_date: date | None

    to_date: date | None

    doctor_id: int | None

    total_revenue: Decimal

    revenue_by_doctor: list[DoctorRevenueResponse]

    revenue_by_day: list[DailyRevenueResponse]