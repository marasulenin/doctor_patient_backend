import os

from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# DATABASE
# =========================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./doctor_patient.db"
)


# =========================================================
# JWT AUTHENTICATION
# =========================================================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "change-this-secret-key"
)


ALGORITHM = os.getenv(
    "ALGORITHM",
    "HS256"
)


ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "30"
    )
)


# =========================================================
# CORS
# =========================================================

CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173"
).split(",")