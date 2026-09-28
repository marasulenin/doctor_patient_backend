from pydantic import BaseModel, ConfigDict, EmailStr, Field


# =========================================================
# CREATE DOCTOR
# =========================================================

class DoctorCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    specialization: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    email: EmailStr


# =========================================================
# UPDATE DOCTOR - PUT
# =========================================================

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


# =========================================================
# PATCH DOCTOR
# =========================================================

class DoctorPatch(BaseModel):
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


# =========================================================
# DOCTOR RESPONSE
# =========================================================

class DoctorResponse(BaseModel):
    id: int
    name: str
    specialization: str
    email: EmailStr
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================================================
# PAGINATED DOCTOR RESPONSE
# =========================================================

class DoctorPaginationResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: list[DoctorResponse]