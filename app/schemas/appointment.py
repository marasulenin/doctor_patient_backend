from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AppointmentCreate(BaseModel):
    doctor_id: int = Field(gt=0)
    patient_id: int = Field(gt=0)
    appointment_date: datetime
    reason: str | None = None


class AppointmentUpdate(BaseModel):
    appointment_date: datetime | None = None
    status: str | None = None
    reason: str | None = None


class AppointmentResponse(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    appointment_date: datetime
    status: str
    reason: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)