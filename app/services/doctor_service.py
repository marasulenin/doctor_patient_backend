from sqlalchemy.orm import Session

from app.models.doctor import Doctor
from app.models.user import User


def create_doctor(
    db: Session,
    name: str,
    specialization: str,
    email: str
):
    existing_doctor = db.query(Doctor).filter(
        Doctor.email == email
    ).first()

    if existing_doctor:
        return None

    # If a doctor user already exists with this email,
    # connect the doctor profile to that user.
    user = db.query(User).filter(
        User.email == email
    ).first()

    new_doctor = Doctor(
        name=name,
        specialization=specialization,
        email=email,
        is_active=True,
        user_id=user.id if user else None
    )

    try:
        db.add(new_doctor)
        db.commit()
        db.refresh(new_doctor)

    except Exception:
        db.rollback()
        raise

    return new_doctor


def get_all_doctors(db: Session):
    return db.query(Doctor).all()


def get_doctor_by_id(
    db: Session,
    doctor_id: int
):
    return db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()


def update_doctor(
    db: Session,
    doctor: Doctor,
    name=None,
    specialization=None,
    email=None,
    is_active=None
):
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

    except Exception:
        db.rollback()
        raise

    return doctor


def delete_doctor(
    db: Session,
    doctor: Doctor
):
    # Soft delete
    doctor.is_active = False

    try:
        db.commit()
        db.refresh(doctor)

    except Exception:
        db.rollback()
        raise

    return doctor