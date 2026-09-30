from datetime import datetime
from decimal import Decimal
from math import ceil
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.appointment import Appointment
from app.models.billing import Billing
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.user import User

from app.schemas.billing import (
    BillingCreate,
    BillingListResponse,
    BillingPatch,
    BillingResponse,
    BillingUpdate,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["Billings"]
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def calculate_total(
    consultation_fee: Decimal,
    additional_charges: Decimal
) -> Decimal:
    """
    Calculate total billing amount.
    """
    return consultation_fee + additional_charges


def validate_billing_relationships(
    db: Session,
    patient_id: int,
    doctor_id: int,
    appointment_id: int | None = None
):
    """
    Validate patient, doctor and appointment relationships.
    """

    # --------------------------------------------------------
    # PATIENT VALIDATION
    # --------------------------------------------------------

    patient = (
        db.query(Patient)
        .filter(
            Patient.id == patient_id
        )
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    # --------------------------------------------------------
    # DOCTOR VALIDATION
    # --------------------------------------------------------

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

    if not doctor.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create or update billing for an inactive doctor"
        )

    # --------------------------------------------------------
    # APPOINTMENT VALIDATION
    # --------------------------------------------------------

    appointment = None

    if appointment_id is not None:

        appointment = (
            db.query(Appointment)
            .filter(
                Appointment.id == appointment_id
            )
            .first()
        )

        if appointment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )

        # Appointment must belong to same doctor
        if appointment.doctor_id != doctor_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appointment does not belong to the selected doctor"
            )

        # Appointment must belong to same patient
        if appointment.patient_id != patient_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appointment does not belong to the selected patient"
            )

        # Cancelled appointments cannot be billed
        if appointment.status == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create billing for a cancelled appointment"
            )

    return patient, doctor, appointment


def get_current_doctor(
    db: Session,
    current_user: User
) -> Doctor:
    """
    Get doctor profile associated with logged-in doctor user.
    """

    doctor = (
        db.query(Doctor)
        .filter(
            Doctor.user_id == current_user.id
        )
        .first()
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )

    return doctor


def check_doctor_billing_access(
    billing: Billing,
    current_doctor: Doctor
):
    """
    Verify that a doctor can access the billing.
    """

    if billing.doctor_id != current_doctor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctors can only view billings related to their patients"
        )


def validate_date_range(
    from_date: datetime | None,
    to_date: datetime | None
):
    """
    Validate billing date range.
    """

    if (
        from_date is not None
        and to_date is not None
        and from_date > to_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="from_date cannot be greater than to_date"
        )


def build_paginated_response(
    query,
    page: int,
    limit: int
) -> BillingListResponse:
    """
    Apply pagination and return standardized billing response.
    """

    total = query.count()

    offset = (page - 1) * limit

    billings = (
        query
        .order_by(
            Billing.created_at.desc(),
            Billing.id.desc()
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    total_pages = (
        ceil(total / limit)
        if total > 0
        else 0
    )

    return BillingListResponse(
        items=billings,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


# ============================================================
# LEVEL 28
# GET ALL BILLINGS
# ============================================================

@router.get(
    "/billings",
    response_model=BillingListResponse
)
def get_all_billings(
    payment_status: Literal[
        "pending",
        "paid",
        "cancelled"
    ] | None = Query(
        default=None,
        description="Filter by payment status"
    ),

    doctor_id: int | None = Query(
        default=None,
        gt=0,
        description="Filter by doctor ID"
    ),

    patient_id: int | None = Query(
        default=None,
        gt=0,
        description="Filter by patient ID"
    ),

    from_date: datetime | None = Query(
        default=None,
        description="Filter billing records from this date"
    ),

    to_date: datetime | None = Query(
        default=None,
        description="Filter billing records up to this date"
    ),

    page: int = Query(
        default=1,
        ge=1,
        description="Page number"
    ),

    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of records per page"
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "doctor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    validate_date_range(
        from_date=from_date,
        to_date=to_date
    )

    query = (
        db.query(Billing)
        .filter(
            Billing.is_active.is_(True)
        )
    )

    if current_user.role == "doctor":

        current_doctor = get_current_doctor(
            db=db,
            current_user=current_user
        )

        query = query.filter(
            Billing.doctor_id == current_doctor.id
        )

    if payment_status is not None:

        query = query.filter(
            Billing.payment_status == payment_status
        )

    if doctor_id is not None:

        if current_user.role == "doctor":

            current_doctor = get_current_doctor(
                db=db,
                current_user=current_user
            )

            if current_doctor.id != doctor_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Doctors can only view their own billings"
                )

        query = query.filter(
            Billing.doctor_id == doctor_id
        )

    if patient_id is not None:

        query = query.filter(
            Billing.patient_id == patient_id
        )

    if from_date is not None:

        query = query.filter(
            Billing.created_at >= from_date
        )

    if to_date is not None:

        query = query.filter(
            Billing.created_at <= to_date
        )

    return build_paginated_response(
        query=query,
        page=page,
        limit=limit
    )


# ============================================================
# LEVEL 29
# CREATE BILLING + UPDATE APPOINTMENT
# ATOMIC DATABASE TRANSACTION
# ============================================================

@router.post(
    "/billings",
    response_model=BillingResponse,
    status_code=status.HTTP_201_CREATED
)
def create_billing(
    billing_data: BillingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # --------------------------------------------------------
    # AUTHORIZATION
    # --------------------------------------------------------

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # --------------------------------------------------------
    # VALIDATE RELATIONSHIPS
    # --------------------------------------------------------

    patient, doctor, appointment = validate_billing_relationships(
        db=db,
        patient_id=billing_data.patient_id,
        doctor_id=billing_data.doctor_id,
        appointment_id=billing_data.appointment_id
    )

    # --------------------------------------------------------
    # DUPLICATE BILLING CHECK
    # --------------------------------------------------------

    if billing_data.appointment_id is not None:

        existing_billing = (
            db.query(Billing)
            .filter(
                Billing.appointment_id
                == billing_data.appointment_id
            )
            .first()
        )

        if existing_billing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Billing already exists for this appointment"
            )

    # --------------------------------------------------------
    # CALCULATE TOTAL
    # --------------------------------------------------------

    total_amount = calculate_total(
        billing_data.consultation_fee,
        billing_data.additional_charges
    )

    # --------------------------------------------------------
    # CREATE BILLING OBJECT
    # --------------------------------------------------------

    billing = Billing(
        patient_id=billing_data.patient_id,
        doctor_id=billing_data.doctor_id,
        appointment_id=billing_data.appointment_id,
        consultation_fee=billing_data.consultation_fee,
        additional_charges=billing_data.additional_charges,
        total_amount=total_amount,
        payment_status=billing_data.payment_status,
        payment_mode=billing_data.payment_mode,
        is_active=True
    )

    # --------------------------------------------------------
    # ATOMIC TRANSACTION
    #
    # Billing creation and appointment status update are
    # performed before ONE commit.
    #
    # If any operation fails, everything is rolled back.
    # --------------------------------------------------------

    try:

        # Add billing to current transaction
        db.add(billing)

        # ----------------------------------------------------
        # UPDATE APPOINTMENT STATUS
        # ----------------------------------------------------

        if appointment is not None:

            appointment.status = "completed"

        # ----------------------------------------------------
        # FLUSH
        #
        # Send pending INSERT/UPDATE statements to database
        # without committing the transaction.
        # ----------------------------------------------------

        db.flush()

        # ----------------------------------------------------
        # ONE COMMIT
        # ----------------------------------------------------

        db.commit()

        # Refresh billing after successful transaction
        db.refresh(billing)

    except IntegrityError:

        # Roll back BOTH billing and appointment changes
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Billing transaction failed because of a database constraint"
        )

    except SQLAlchemyError:

        # Roll back BOTH operations
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Billing transaction failed. No changes were saved."
        )

    except Exception:

        # Safety rollback for unexpected failures
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Billing transaction failed. No changes were saved."
        )

    return billing


# ============================================================
# GET BILLING BY ID
# ============================================================

@router.get(
    "/billings/{billing_id}",
    response_model=BillingResponse
)
def get_billing(
    billing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    billing = (
        db.query(Billing)
        .filter(
            Billing.id == billing_id,
            Billing.is_active.is_(True)
        )
        .first()
    )

    if billing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Billing not found"
        )

    if current_user.role == "admin":
        return billing

    if current_user.role == "doctor":

        current_doctor = get_current_doctor(
            db=db,
            current_user=current_user
        )

        check_doctor_billing_access(
            billing=billing,
            current_doctor=current_doctor
        )

        return billing

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )


# ============================================================
# GET BILLINGS BY PATIENT
# ============================================================

@router.get(
    "/patients/{patient_id}/billings",
    response_model=BillingListResponse
)
def get_patient_billings(
    patient_id: int,

    payment_status: Literal[
        "pending",
        "paid",
        "cancelled"
    ] | None = Query(
        default=None,
        description="Filter by payment status"
    ),

    from_date: datetime | None = Query(
        default=None,
        description="Filter billing records from this date"
    ),

    to_date: datetime | None = Query(
        default=None,
        description="Filter billing records up to this date"
    ),

    page: int = Query(
        default=1,
        ge=1,
        description="Page number"
    ),

    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of records per page"
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
    patient = (
        db.query(Patient)
        .filter(
            Patient.id == patient_id
        )
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    validate_date_range(
        from_date=from_date,
        to_date=to_date
    )

    if current_user.role not in ["admin", "doctor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    query = (
        db.query(Billing)
        .filter(
            Billing.patient_id == patient_id,
            Billing.is_active.is_(True)
        )
    )

    if current_user.role == "doctor":

        current_doctor = get_current_doctor(
            db=db,
            current_user=current_user
        )

        query = query.filter(
            Billing.doctor_id == current_doctor.id
        )

    if payment_status is not None:

        query = query.filter(
            Billing.payment_status == payment_status
        )

    if from_date is not None:

        query = query.filter(
            Billing.created_at >= from_date
        )

    if to_date is not None:

        query = query.filter(
            Billing.created_at <= to_date
        )

    return build_paginated_response(
        query=query,
        page=page,
        limit=limit
    )


# ============================================================
# GET BILLINGS BY DOCTOR
# ============================================================

@router.get(
    "/doctors/{doctor_id}/billings",
    response_model=BillingListResponse
)
def get_doctor_billings(
    doctor_id: int,

    payment_status: Literal[
        "pending",
        "paid",
        "cancelled"
    ] | None = Query(
        default=None,
        description="Filter by payment status"
    ),

    from_date: datetime | None = Query(
        default=None,
        description="Filter billing records from this date"
    ),

    to_date: datetime | None = Query(
        default=None,
        description="Filter billing records up to this date"
    ),

    page: int = Query(
        default=1,
        ge=1,
        description="Page number"
    ),

    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of records per page"
    ),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user)
):
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

    validate_date_range(
        from_date=from_date,
        to_date=to_date
    )

    if current_user.role not in ["admin", "doctor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    if current_user.role == "doctor":

        current_doctor = get_current_doctor(
            db=db,
            current_user=current_user
        )

        if current_doctor.id != doctor_id:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctors can only view their own billings"
            )

    query = (
        db.query(Billing)
        .filter(
            Billing.doctor_id == doctor_id,
            Billing.is_active.is_(True)
        )
    )

    if payment_status is not None:

        query = query.filter(
            Billing.payment_status == payment_status
        )

    if from_date is not None:

        query = query.filter(
            Billing.created_at >= from_date
        )

    if to_date is not None:

        query = query.filter(
            Billing.created_at <= to_date
        )

    return build_paginated_response(
        query=query,
        page=page,
        limit=limit
    )


# ============================================================
# UPDATE BILLING - PUT
# ============================================================

@router.put(
    "/billings/{billing_id}",
    response_model=BillingResponse
)
def update_billing(
    billing_id: int,
    billing_data: BillingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    billing = (
        db.query(Billing)
        .filter(
            Billing.id == billing_id,
            Billing.is_active.is_(True)
        )
        .first()
    )

    if billing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Billing not found"
        )

    validate_billing_relationships(
        db=db,
        patient_id=billing_data.patient_id,
        doctor_id=billing_data.doctor_id,
        appointment_id=billing_data.appointment_id
    )

    if billing_data.appointment_id is not None:

        existing_billing = (
            db.query(Billing)
            .filter(
                Billing.appointment_id
                == billing_data.appointment_id,
                Billing.id != billing_id
            )
            .first()
        )

        if existing_billing is not None:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Billing already exists for this appointment"
            )

    billing.patient_id = billing_data.patient_id
    billing.doctor_id = billing_data.doctor_id
    billing.appointment_id = billing_data.appointment_id

    billing.consultation_fee = (
        billing_data.consultation_fee
    )

    billing.additional_charges = (
        billing_data.additional_charges
    )

    billing.total_amount = calculate_total(
        billing_data.consultation_fee,
        billing_data.additional_charges
    )

    billing.payment_status = (
        billing_data.payment_status
    )

    billing.payment_mode = (
        billing_data.payment_mode
    )

    try:

        db.commit()

        db.refresh(billing)

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Billing update violates a database constraint"
        )

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Billing update failed"
        )

    return billing


# ============================================================
# PATCH BILLING
# ============================================================

@router.patch(
    "/billings/{billing_id}",
    response_model=BillingResponse
)
def patch_billing(
    billing_id: int,
    billing_data: BillingPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    billing = (
        db.query(Billing)
        .filter(
            Billing.id == billing_id,
            Billing.is_active.is_(True)
        )
        .first()
    )

    if billing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Billing not found"
        )

    final_patient_id = (
        billing_data.patient_id
        if billing_data.patient_id is not None
        else billing.patient_id
    )

    final_doctor_id = (
        billing_data.doctor_id
        if billing_data.doctor_id is not None
        else billing.doctor_id
    )

    final_appointment_id = (
        billing_data.appointment_id
        if billing_data.appointment_id is not None
        else billing.appointment_id
    )

    final_consultation_fee = (
        billing_data.consultation_fee
        if billing_data.consultation_fee is not None
        else billing.consultation_fee
    )

    final_additional_charges = (
        billing_data.additional_charges
        if billing_data.additional_charges is not None
        else billing.additional_charges
    )

    validate_billing_relationships(
        db=db,
        patient_id=final_patient_id,
        doctor_id=final_doctor_id,
        appointment_id=final_appointment_id
    )

    if final_appointment_id is not None:

        existing_billing = (
            db.query(Billing)
            .filter(
                Billing.appointment_id
                == final_appointment_id,
                Billing.id != billing_id
            )
            .first()
        )

        if existing_billing is not None:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Billing already exists for this appointment"
            )

    billing.patient_id = final_patient_id
    billing.doctor_id = final_doctor_id
    billing.appointment_id = final_appointment_id

    billing.consultation_fee = (
        final_consultation_fee
    )

    billing.additional_charges = (
        final_additional_charges
    )

    billing.total_amount = calculate_total(
        final_consultation_fee,
        final_additional_charges
    )

    if billing_data.payment_status is not None:

        billing.payment_status = (
            billing_data.payment_status
        )

    if billing_data.payment_mode is not None:

        billing.payment_mode = (
            billing_data.payment_mode
        )

    try:

        db.commit()

        db.refresh(billing)

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Billing update violates a database constraint"
        )

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Billing update failed"
        )

    return billing


# ============================================================
# DELETE BILLING - SOFT DELETE
# ============================================================

@router.delete(
    "/billings/{billing_id}",
    response_model=BillingResponse
)
def delete_billing(
    billing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    billing = (
        db.query(Billing)
        .filter(
            Billing.id == billing_id,
            Billing.is_active.is_(True)
        )
        .first()
    )

    if billing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Billing not found"
        )

    billing.is_active = False

    try:

        db.commit()

        db.refresh(billing)

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Billing deletion failed"
        )

    return billing