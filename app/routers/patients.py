from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.database import get_db
from app.models.user import User

from app.schemas.patient import (
    PatientCreate,
    PatientResponse,
    PatientUpdate,
    PatientPatch,
    PatientPaginationResponse
)

from app.services.patient_service import (
    create_patient,
    get_all_patients,
    get_patient_by_id,
    update_patient,
    patch_patient,
    delete_patient
)


router = APIRouter(
    prefix="/api/v1/patients",
    tags=["Patients"]
)


# =========================================================
# CREATE PATIENT
# =========================================================

@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED
)
def create_patient_api(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    patient = create_patient(
        db=db,
        name=patient_data.name,
        age=patient_data.age,
        phone=patient_data.phone,
        address=patient_data.address,
        gender=patient_data.gender,
        doctor_id=patient_data.doctor_id
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

    return patient


# =========================================================
# GET ALL PATIENTS + AGE FILTER + PAGINATION
# =========================================================

@router.get(
    "",
    response_model=PatientPaginationResponse
)
def get_patients(
    age_gt: int | None = Query(
        default=None,
        gt=0,
        description="Return patients older than this age"
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
    return get_all_patients(
        db=db,
        age_gt=age_gt,
        page=page,
        limit=limit
    )


# =========================================================
# GET PATIENT BY ID
# =========================================================

@router.get(
    "/{patient_id}",
    response_model=PatientResponse
)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    patient = get_patient_by_id(
        db=db,
        patient_id=patient_id
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    return patient


# =========================================================
# UPDATE PATIENT - PUT
# =========================================================

@router.put(
    "/{patient_id}",
    response_model=PatientResponse
)
def update_patient_api(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    patient = update_patient(
        db=db,
        patient_id=patient_id,
        name=patient_data.name,
        age=patient_data.age,
        phone=patient_data.phone,
        address=patient_data.address,
        gender=patient_data.gender,
        doctor_id=patient_data.doctor_id
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
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

    return patient


# =========================================================
# PATCH PATIENT
# =========================================================

@router.patch(
    "/{patient_id}",
    response_model=PatientResponse
)
def patch_patient_api(
    patient_id: int,
    patient_data: PatientPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    patient = patch_patient(
        db=db,
        patient_id=patient_id,
        name=patient_data.name,
        age=patient_data.age,
        phone=patient_data.phone,
        address=patient_data.address,
        gender=patient_data.gender,
        doctor_id=patient_data.doctor_id
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
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

    return patient


# =========================================================
# DELETE PATIENT
# =========================================================

@router.delete(
    "/{patient_id}",
    response_model=PatientResponse
)
def delete_patient_api(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    patient = delete_patient(
        db=db,
        patient_id=patient_id
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    return patient