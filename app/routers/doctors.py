from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.doctor import (
    DoctorCreate,
    DoctorResponse,
    DoctorUpdate
)
from app.services.doctor_service import (
    create_doctor,
    delete_doctor,
    get_all_doctors,
    get_doctor_by_id,
    update_doctor
)


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)


@router.post(
    "",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED
)
def create_doctor_api(
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    doctor = create_doctor(
        db=db,
        name=doctor_data.name,
        specialization=doctor_data.specialization,
        email=doctor_data.email
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor with this email already exists"
        )

    return doctor


@router.get(
    "",
    response_model=list[DoctorResponse]
)
def get_doctors(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return get_all_doctors(db)


@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse
)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    doctor = get_doctor_by_id(
        db=db,
        doctor_id=doctor_id
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    return doctor


@router.put(
    "/{doctor_id}",
    response_model=DoctorResponse
)
def update_doctor_api(
    doctor_id: int,
    doctor_data: DoctorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    doctor = get_doctor_by_id(
        db=db,
        doctor_id=doctor_id
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    updated_doctor = update_doctor(
        db=db,
        doctor=doctor,
        name=doctor_data.name,
        specialization=doctor_data.specialization,
        email=doctor_data.email,
        is_active=doctor_data.is_active
    )

    return updated_doctor


@router.delete(
    "/{doctor_id}",
    response_model=DoctorResponse
)
def delete_doctor_api(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    doctor = get_doctor_by_id(
        db=db,
        doctor_id=doctor_id
    )

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    return delete_doctor(
        db=db,
        doctor=doctor
    )