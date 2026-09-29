from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_current_user,
    require_admin
)
from app.database import get_db
from app.models.user import User
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate
)
from app.services.appointment_service import (
    create_appointment,
    get_all_appointments,
    get_appointment_by_id,
    update_appointment,
    delete_appointment
)


router = APIRouter(
    prefix="/api/v1/appointments",
    tags=["Appointments"]
)


# CREATE APPOINTMENT
@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_appointment_api(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    appointment = create_appointment(
        db=db,
        doctor_id=appointment_data.doctor_id,
        patient_id=appointment_data.patient_id,
        appointment_date=appointment_data.appointment_date,
        reason=appointment_data.reason
    )

    if appointment == "doctor_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    if appointment == "doctor_inactive":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create appointment with an inactive doctor"
        )

    if appointment == "patient_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    if appointment == "patient_not_assigned":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient is not assigned to this doctor"
        )

    return appointment


# GET ALL APPOINTMENTS
@router.get(
    "",
    response_model=list[AppointmentResponse]
)
def get_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return get_all_appointments(db=db)


# GET APPOINTMENT BY ID
@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse
)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appointment = get_appointment_by_id(
        db=db,
        appointment_id=appointment_id
    )

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    # Admin can view any appointment
    if current_user.role == "admin":
        return appointment

    # Doctor can view only their own appointments
    if current_user.role == "doctor":
        if appointment.doctor.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctors can only view their own appointments"
            )

        return appointment

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )


# UPDATE APPOINTMENT
@router.put(
    "/{appointment_id}",
    response_model=AppointmentResponse
)
def update_appointment_api(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    appointment = get_appointment_by_id(
        db=db,
        appointment_id=appointment_id
    )

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    allowed_statuses = {
        "scheduled",
        "completed",
        "cancelled"
    }

    if (
        appointment_data.status is not None
        and appointment_data.status not in allowed_statuses
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid appointment status"
        )

    return update_appointment(
        db=db,
        appointment=appointment,
        appointment_date=appointment_data.appointment_date,
        status=appointment_data.status,
        reason=appointment_data.reason
    )


# CANCEL APPOINTMENT
@router.delete(
    "/{appointment_id}",
    response_model=AppointmentResponse
)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    appointment = get_appointment_by_id(
        db=db,
        appointment_id=appointment_id
    )

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    return delete_appointment(
        db=db,
        appointment=appointment
    )