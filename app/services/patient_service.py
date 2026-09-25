from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.doctor import Doctor


def create_patient(
    db: Session,
    name: str,
    age: int,
    phone: str,
    doctor_id: int | None = None
):
    # Check whether the doctor exists
    if doctor_id is not None:
        doctor = db.query(Doctor).filter(
            Doctor.id == doctor_id
        ).first()

        if doctor is None:
            return None

    new_patient = Patient(
        name=name,
        age=age,
        phone=phone,
        doctor_id=doctor_id
    )

    try:
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)

    except Exception:
        db.rollback()
        raise

    return new_patient


def get_all_patients(db: Session):
    return db.query(Patient).all()


def get_patient_by_id(
    db: Session,
    patient_id: int
):
    return db.query(Patient).filter(
        Patient.id == patient_id
    ).first()


def update_patient(
    db: Session,
    patient_id: int,
    name: str,
    age: int,
    phone: str,
    doctor_id: int | None = None
):
    # Find the patient
    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if patient is None:
        return None

    # Check whether the new doctor exists
    if doctor_id is not None:
        doctor = db.query(Doctor).filter(
            Doctor.id == doctor_id
        ).first()

        if doctor is None:
            return "doctor_not_found"

    # Update patient details
    patient.name = name
    patient.age = age
    patient.phone = phone
    patient.doctor_id = doctor_id

    try:
        db.commit()
        db.refresh(patient)

    except Exception:
        db.rollback()
        raise

    return patient


def delete_patient(
    db: Session,
    patient_id: int
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if patient is None:
        return None

    try:
        db.delete(patient)
        db.commit()

    except Exception:
        db.rollback()
        raise

    return patient