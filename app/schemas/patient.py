from pydantic import BaseModel, ConfigDict, Field


# =========================================================
# CREATE PATIENT
# =========================================================

class PatientCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    age: int = Field(
        ...,
        gt=0
    )

    phone: str = Field(
        ...,
        pattern=r"^\d{10}$"
    )

    address: str | None = Field(
        default=None,
        max_length=255
    )

    gender: str | None = Field(
        default=None,
        max_length=20
    )

    doctor_id: int | None = None


# =========================================================
# UPDATE PATIENT - PUT
# =========================================================

class PatientUpdate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    age: int = Field(
        ...,
        gt=0
    )

    phone: str = Field(
        ...,
        pattern=r"^\d{10}$"
    )

    address: str | None = Field(
        default=None,
        max_length=255
    )

    gender: str | None = Field(
        default=None,
        max_length=20
    )

    doctor_id: int | None = None


# =========================================================
# PATCH PATIENT
# =========================================================

class PatientPatch(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    age: int | None = Field(
        default=None,
        gt=0
    )

    phone: str | None = Field(
        default=None,
        pattern=r"^\d{10}$"
    )

    address: str | None = Field(
        default=None,
        max_length=255
    )

    gender: str | None = Field(
        default=None,
        max_length=20
    )

    doctor_id: int | None = None


# =========================================================
# PATIENT RESPONSE
# =========================================================

class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    phone: str
    address: str | None
    gender: str | None
    doctor_id: int | None

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================================================
# PAGINATED PATIENT RESPONSE
# =========================================================

class PatientPaginationResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: list[PatientResponse]