from pydantic import BaseModel, ConfigDict, Field, field_validator


class PatientCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., gt=0)
    phone: str = Field(..., min_length=10, max_length=15)
    doctor_id: int | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("Phone number must contain only digits")

        if not 10 <= len(value) <= 15:
            raise ValueError(
                "Phone number must contain 10 to 15 digits"
            )

        return value


class PatientUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., gt=0)
    phone: str = Field(..., min_length=10, max_length=15)
    doctor_id: int | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("Phone number must contain only digits")

        if not 10 <= len(value) <= 15:
            raise ValueError(
                "Phone number must contain 10 to 15 digits"
            )

        return value


class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    phone: str
    doctor_id: int | None

    model_config = ConfigDict(from_attributes=True)