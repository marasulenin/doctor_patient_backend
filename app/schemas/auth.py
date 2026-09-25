from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=6,
        max_length=100
    )

    role: str = "doctor"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str