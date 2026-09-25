from pydantic import BaseModel, ConfigDict, EmailStr, Field


class DoctorCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    specialization: str = Field(..., min_length=2, max_length=100)
    email: EmailStr


class DoctorUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    specialization: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    email: EmailStr | None = None

    is_active: bool | None = None


class DoctorResponse(BaseModel):
    id: int
    name: str
    specialization: str
    email: EmailStr
    is_active: bool

    model_config = ConfigDict(from_attributes=True)