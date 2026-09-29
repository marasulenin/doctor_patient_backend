from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.doctor import Doctor
from app.utils.logging_config import get_logger


logger = get_logger(__name__)


# =========================================================
# CREATE PATIENT
# =========================================================

def create_patient(
    db: Session,
    name: str,
    age: int,
    phone: str,
    address: str | None = None,
    gender: str | None = None,
    doctor_id: int | None = None
):
    logger.info(
        "Creating patient | name=%s | doctor_id=%s",
        name,
        doctor_id
    )

    if doctor_id is not None:

        doctor = db.get(
            Doctor,
            doctor_id
        )

        if doctor is None:
            logger.warning(
                "Patient creation failed: doctor id=%s not found",
                doctor_id
            )
            return "doctor_not_found"

        if not doctor.is_active:
            logger.warning(
                "Patient creation failed: doctor id=%s is inactive",
                doctor_id
            )
            return "doctor_inactive"

    new_patient = Patient(
        name=name,
        age=age,
        phone=phone,
        address=address,
        gender=gender,
        doctor_id=doctor_id
    )

    try:
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)

        logger.info(
            "Patient created successfully with id=%s",
            new_patient.id
        )

    except Exception:
        db.rollback()

        logger.exception(
            "Error while creating patient name=%s",
            name
        )

        raise

    return new_patient


# =========================================================
# GET ALL PATIENTS + AGE FILTER + PAGINATION
# =========================================================

def get_all_patients(
    db: Session,
    age_gt: int | None = None,
    page: int = 1,
    limit: int = 10
):
    logger.info(
        "Getting patients | age_gt=%s | page=%s | limit=%s",
        age_gt,
        page,
        limit
    )

    query = select(Patient)

    if age_gt is not None:
        query = query.where(
            Patient.age > age_gt
        )

    # Count matching records
    count_query = select(
        func.count()
    ).select_from(
        query.subquery()
    )

    total = db.scalar(count_query) or 0

    # Pagination
    offset = (page - 1) * limit

    patients = db.scalars(
        query
        .order_by(Patient.id)
        .offset(offset)
        .limit(limit)
    ).all()

    logger.info(
        "Retrieved %s patients",
        len(patients)
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": patients
    }


# =========================================================
# GET PATIENT BY ID
# =========================================================

def get_patient_by_id(
    db: Session,
    patient_id: int
):
    logger.info(
        "Getting patient with id=%s",
        patient_id
    )

    patient = db.get(
        Patient,
        patient_id
    )

    if patient is None:
        logger.warning(
            "Patient not found with id=%s",
            patient_id
        )

    return patient


# =========================================================
# GET PATIENTS BY DOCTOR
# =========================================================

def get_patients_by_doctor(
    db: Session,
    doctor_id: int
):
    logger.info(
        "Getting patients for doctor_id=%s",
        doctor_id
    )

    doctor = db.get(
        Doctor,
        doctor_id
    )

    if doctor is None:
        logger.warning(
            "Doctor not found with id=%s",
            doctor_id
        )
        return "doctor_not_found"

    if not doctor.is_active:
        logger.warning(
            "Doctor is inactive with id=%s",
            doctor_id
        )
        return "doctor_inactive"

    patients = db.scalars(
        select(Patient)
        .where(
            Patient.doctor_id == doctor_id
        )
        .order_by(Patient.id)
    ).all()

    logger.info(
        "Retrieved %s patients for doctor_id=%s",
        len(patients),
        doctor_id
    )

    return patients


# =========================================================
# UPDATE PATIENT - PUT
# =========================================================

def update_patient(
    db: Session,
    patient_id: int,
    name: str,
    age: int,
    phone: str,
    address: str | None = None,
    gender: str | None = None,
    doctor_id: int | None = None
):
    logger.info(
        "Updating patient id=%s",
        patient_id
    )

    patient = db.get(
        Patient,
        patient_id
    )

    if patient is None:
        logger.warning(
            "Patient update failed: patient id=%s not found",
            patient_id
        )
        return None

    if doctor_id is not None:

        doctor = db.get(
            Doctor,
            doctor_id
        )

        if doctor is None:
            logger.warning(
                "Patient update failed: doctor id=%s not found",
                doctor_id
            )
            return "doctor_not_found"

        if not doctor.is_active:
            logger.warning(
                "Patient update failed: doctor id=%s is inactive",
                doctor_id
            )
            return "doctor_inactive"

    patient.name = name
    patient.age = age
    patient.phone = phone
    patient.address = address
    patient.gender = gender
    patient.doctor_id = doctor_id

    try:
        db.commit()
        db.refresh(patient)

        logger.info(
            "Patient id=%s updated successfully",
            patient_id
        )

    except Exception:
        db.rollback()

        logger.exception(
            "Error while updating patient id=%s",
            patient_id
        )

        raise

    return patient


# =========================================================
# PATCH PATIENT
# =========================================================

def patch_patient(
    db: Session,
    patient_id: int,
    name=None,
    age=None,
    phone=None,
    address=None,
    gender=None,
    doctor_id=None
):
    logger.info(
        "Patching patient id=%s",
        patient_id
    )

    patient = db.get(
        Patient,
        patient_id
    )

    if patient is None:
        logger.warning(
            "Patient patch failed: patient id=%s not found",
            patient_id
        )
        return None

    if doctor_id is not None:

        doctor = db.get(
            Doctor,
            doctor_id
        )

        if doctor is None:
            logger.warning(
                "Patient patch failed: doctor id=%s not found",
                doctor_id
            )
            return "doctor_not_found"

        if not doctor.is_active:
            logger.warning(
                "Patient patch failed: doctor id=%s is inactive",
                doctor_id
            )
            return "doctor_inactive"

    if name is not None:
        patient.name = name

    if age is not None:
        patient.age = age

    if phone is not None:
        patient.phone = phone

    if address is not None:
        patient.address = address

    if gender is not None:
        patient.gender = gender

    if doctor_id is not None:
        patient.doctor_id = doctor_id

    try:
        db.commit()
        db.refresh(patient)

        logger.info(
            "Patient id=%s patched successfully",
            patient_id
        )

    except Exception:
        db.rollback()

        logger.exception(
            "Error while patching patient id=%s",
            patient_id
        )

        raise

    return patient


# =========================================================
# DELETE PATIENT
# =========================================================

def delete_patient(
    db: Session,
    patient_id: int
):
    logger.info(
        "Deleting patient id=%s",
        patient_id
    )

    patient = db.get(
        Patient,
        patient_id
    )

    if patient is None:
        logger.warning(
            "Patient delete failed: patient id=%s not found",
            patient_id
        )
        return None

    try:
        db.delete(patient)
        db.commit()

        logger.info(
            "Patient id=%s deleted successfully",
            patient_id
        )

    except Exception:
        db.rollback()

        logger.exception(
            "Error while deleting patient id=%s",
            patient_id
        )

        raise

    return patient