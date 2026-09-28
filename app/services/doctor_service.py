from sqlalchemy.orm import Session

from app.models.doctor import Doctor
from app.models.patient import Patient
from app.utils.logging_config import get_logger


logger = get_logger(__name__)


# =========================================================
# CREATE DOCTOR
# =========================================================

def create_doctor(
    db: Session,
    name: str,
    specialization: str,
    email: str,
    is_active: bool = True
):
    logger.info(
        "Creating doctor with email=%s",
        email
    )

    existing_doctor = db.query(Doctor).filter(
        Doctor.email == email
    ).first()

    if existing_doctor:
        logger.warning(
            "Doctor creation failed: duplicate email=%s",
            email
        )
        return "duplicate_email"

    new_doctor = Doctor(
        name=name,
        specialization=specialization,
        email=email,
        is_active=is_active
    )

    try:
        db.add(new_doctor)
        db.commit()
        db.refresh(new_doctor)

        logger.info(
            "Doctor created successfully with id=%s",
            new_doctor.id
        )

    except Exception:
        db.rollback()

        logger.exception(
            "Error while creating doctor with email=%s",
            email
        )

        raise

    return new_doctor


# =========================================================
# GET ALL DOCTORS + FILTER + PAGINATION
# =========================================================

def get_all_doctors(
    db: Session,
    specialization: str | None = None,
    is_active: bool | None = None,
    page: int = 1,
    limit: int = 10
):
    logger.info(
        "Getting doctors | specialization=%s | is_active=%s | page=%s | limit=%s",
        specialization,
        is_active,
        page,
        limit
    )

    query = db.query(Doctor)

    if specialization is not None:
        query = query.filter(
            Doctor.specialization == specialization
        )

    if is_active is not None:
        query = query.filter(
            Doctor.is_active == is_active
        )

    total = query.count()

    offset = (page - 1) * limit

    doctors = query.offset(offset).limit(limit).all()

    logger.info(
        "Retrieved %s doctors",
        len(doctors)
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": doctors
    }


# =========================================================
# GET DOCTOR BY ID
# =========================================================

def get_doctor_by_id(
    db: Session,
    doctor_id: int
):
    logger.info(
        "Getting doctor with id=%s",
        doctor_id
    )

    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if doctor is None:
        logger.warning(
            "Doctor not found with id=%s",
            doctor_id
        )

    return doctor


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

    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

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

    patients = db.query(Patient).filter(
        Patient.doctor_id == doctor_id
    ).all()

    logger.info(
        "Retrieved %s patients for doctor_id=%s",
        len(patients),
        doctor_id
    )

    return patients


# =========================================================
# ASSIGN PATIENT TO DOCTOR
# =========================================================

def assign_patient_to_doctor(
    db: Session,
    doctor_id: int,
    patient_id: int
):
    logger.info(
        "Assigning patient id=%s to doctor id=%s",
        patient_id,
        doctor_id
    )

    # Check doctor
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if doctor is None:
        logger.warning(
            "Assignment failed: doctor id=%s not found",
            doctor_id
        )
        return "doctor_not_found"

    # Check doctor active status
    if not doctor.is_active:
        logger.warning(
            "Assignment failed: doctor id=%s is inactive",
            doctor_id
        )
        return "doctor_inactive"

    # Check patient
    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if patient is None:
        logger.warning(
            "Assignment failed: patient id=%s not found",
            patient_id
        )
        return "patient_not_found"

    # Assign patient
    patient.doctor_id = doctor_id

    try:
        db.commit()
        db.refresh(patient)

        logger.info(
            "Patient id=%s successfully assigned to doctor id=%s",
            patient_id,
            doctor_id
        )

    except Exception:
        db.rollback()

        logger.exception(
            "Error assigning patient id=%s to doctor id=%s",
            patient_id,
            doctor_id
        )

        raise

    return patient


# =========================================================
# UPDATE DOCTOR - PUT
# =========================================================

def update_doctor(
    db: Session,
    doctor_id: int,
    name: str,
    specialization: str,
    email: str,
    is_active: bool
):
    logger.info(
        "Updating doctor id=%s",
        doctor_id
    )

    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if doctor is None:
        logger.warning(
            "Doctor update failed: doctor id=%s not found",
            doctor_id
        )
        return None

    existing_doctor = db.query(Doctor).filter(
        Doctor.email == email,
        Doctor.id != doctor_id
    ).first()

    if existing_doctor:
        logger.warning(
            "Doctor update failed: duplicate email=%s",
            email
        )
        return "duplicate_email"

    doctor.name = name
    doctor.specialization = specialization
    doctor.email = email
    doctor.is_active = is_active

    try:
        db.commit()
        db.refresh(doctor)

        logger.info(
            "Doctor id=%s updated successfully",
            doctor_id
        )

    except Exception:
        db.rollback()

        logger.exception(
            "Error while updating doctor id=%s",
            doctor_id
        )

        raise

    return doctor


# =========================================================
# PATCH DOCTOR
# =========================================================

def patch_doctor(
    db: Session,
    doctor_id: int,
    name=None,
    specialization=None,
    email=None,
    is_active=None
):
    logger.info(
        "Patching doctor id=%s",
        doctor_id
    )

    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if doctor is None:
        logger.warning(
            "Doctor patch failed: doctor id=%s not found",
            doctor_id
        )
        return None

    if email is not None:

        existing_doctor = db.query(Doctor).filter(
            Doctor.email == email,
            Doctor.id != doctor_id
        ).first()

        if existing_doctor:
            logger.warning(
                "Doctor patch failed: duplicate email=%s",
                email
            )
            return "duplicate_email"

    if name is not None:
        doctor.name = name

    if specialization is not None:
        doctor.specialization = specialization

    if email is not None:
        doctor.email = email

    if is_active is not None:
        doctor.is_active = is_active

    try:
        db.commit()
        db.refresh(doctor)

        logger.info(
            "Doctor id=%s patched successfully",
            doctor_id
        )

    except Exception:
        db.rollback()

        logger.exception(
            "Error while patching doctor id=%s",
            doctor_id
        )

        raise

    return doctor


# =========================================================
# DELETE DOCTOR - SOFT DELETE
# =========================================================

def delete_doctor(
    db: Session,
    doctor_id: int
):
    logger.info(
        "Soft deleting doctor id=%s",
        doctor_id
    )

    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if doctor is None:
        logger.warning(
            "Doctor delete failed: doctor id=%s not found",
            doctor_id
        )
        return None

    doctor.is_active = False

    try:
        db.commit()
        db.refresh(doctor)

        logger.info(
            "Doctor id=%s soft deleted successfully",
            doctor_id
        )

    except Exception:
        db.rollback()

        logger.exception(
            "Error while deleting doctor id=%s",
            doctor_id
        )

        raise

    return doctor