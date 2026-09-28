from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin, get_current_user
from app.database import get_db
from app.models.user import User

from app.schemas.doctor import (
    DoctorCreate,
    DoctorResponse,
    DoctorUpdate,
    DoctorPatch,
    DoctorPaginationResponse
)

from app.schemas.patient import PatientResponse

from app.services.doctor_service import (
    create_doctor,
    get_all_doctors,
    get_doctor_by_id,
    update_doctor,
    patch_doctor,
    delete_doctor,
    assign_patient_to_doctor,
    get_patients_by_doctor
)


router = APIRouter(
    prefix="/api/v1/doctors",
    tags=["Doctors"]
)


# =========================================================
# CREATE DOCTOR
# =========================================================

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


# =========================================================
# GET ALL DOCTORS + FILTERING + PAGINATION
# =========================================================

@router.get(
    "",
    response_model=DoctorPaginationResponse
)
def get_doctors(
    specialization: str | None = Query(
        default=None,
        description="Filter doctors by specialization"
    ),
    is_active: bool | None = Query(
        default=None,
        description="Filter doctors by active status"
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
    current_user: User = Depends(require_admin)
):
    return get_all_doctors(
        db=db,
        specialization=specialization,
        is_active=is_active,
        page=page,
        limit=limit
    )


# =========================================================
# GET DOCTOR BY ID
# =========================================================

@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse
)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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


# =========================================================
# UPDATE DOCTOR - PUT
# =========================================================

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

    if updated_doctor == "duplicate_email":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor with this email already exists"
        )

    return updated_doctor


# =========================================================
# PATCH DOCTOR
# =========================================================

@router.patch(
    "/{doctor_id}",
    response_model=DoctorResponse
)
def patch_doctor_api(
    doctor_id: int,
    doctor_data: DoctorPatch,
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

    updated_doctor = patch_doctor(
        db=db,
        doctor=doctor,
        name=doctor_data.name,
        specialization=doctor_data.specialization,
        email=doctor_data.email,
        is_active=doctor_data.is_active
    )

    if updated_doctor == "duplicate_email":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor with this email already exists"
        )

    return updated_doctor


# =========================================================
# DELETE DOCTOR - SOFT DELETE
# =========================================================

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


# =========================================================
# ASSIGN PATIENT TO DOCTOR
# =========================================================

@router.post(
    "/{doctor_id}/patients/{patient_id}",
    response_model=PatientResponse
)
def assign_patient(
    doctor_id: int,
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    patient = assign_patient_to_doctor(
        db=db,
        doctor_id=doctor_id,
        patient_id=patient_id
    )

    if patient == "doctor_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    if patient == "doctor_inactive":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot assign patient to an inactive doctor"
        )

    if patient == "patient_not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    return patient


# =========================================================
# GET PATIENTS BY DOCTOR
# =========================================================

@router.get(
    "/{doctor_id}/patients",
    response_model=list[PatientResponse]
)
def get_doctor_patients(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    # ADMIN
    if current_user.role == "admin":

        patients = get_patients_by_doctor(
            db=db,
            doctor_id=doctor_id
        )

        if patients == "doctor_not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found"
            )

        if patients == "doctor_inactive":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot retrieve patients for an inactive doctor"
            )

        return patients

    # DOCTOR
    if current_user.role == "doctor":

        if doctor.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctors can only view their own patients"
            )

        patients = get_patients_by_doctor(
            db=db,
            doctor_id=doctor_id
        )

        if patients == "doctor_not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found"
            )

        if patients == "doctor_inactive":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot retrieve patients for an inactive doctor"
            )

        return patients

    # OTHER ROLES
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )