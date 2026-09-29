from datetime import datetime

from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.patient import Patient


def create_appointment(
    db: Session,
    doctor_id: int,
    patient_id: int,
    appointment_date: datetime,
    reason: str | None
):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if doctor is None:
        return "doctor_not_found"

    if not doctor.is_active:
        return "doctor_inactive"

    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if patient is None:
        return "patient_not_found"

    if patient.doctor_id != doctor_id:
        return "patient_not_assigned"

    appointment = Appointment(
        doctor_id=doctor_id,
        patient_id=patient_id,
        appointment_date=appointment_date,
        status="scheduled",
        reason=reason
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return appointment


def get_all_appointments(db: Session):
    return db.query(Appointment).order_by(
        Appointment.appointment_date
    ).all()


def get_appointment_by_id(
    db: Session,
    appointment_id: int
):
    return db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()


def update_appointment(
    db: Session,
    appointment: Appointment,
    appointment_date: datetime | None,
    status: str | None,
    reason: str | None
):
    if appointment_date is not None:
        appointment.appointment_date = appointment_date

    if status is not None:
        appointment.status = status

    if reason is not None:
        appointment.reason = reason

    db.commit()
    db.refresh(appointment)

    return appointment


def delete_appointment(
    db: Session,
    appointment: Appointment
):
    # Soft delete: mark appointment as cancelled
    appointment.status = "cancelled"

    db.commit()
    db.refresh(appointment)

    return appointment