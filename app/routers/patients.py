from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.patient import (
    PatientCreate,
    PatientResponse,
    PatientUpdate
)
from app.services.patient_service import (
    create_patient,
    get_all_patients,
    get_patient_by_id,
    update_patient,
    delete_patient
)


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


# Create Patient
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
        doctor_id=patient_data.doctor_id
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    return patient


# Get All Patients
@router.get(
    "",
    response_model=list[PatientResponse]
)
def get_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return get_all_patients(db)


# Get Patient By ID
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


# Update Patient
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

    return patient


# Delete Patient
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