from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth.dependencies import get_current_user
from app.config import CORS_ORIGINS
from app.database import Base, engine
from app.models import User, Doctor, Patient
from app.models.user import User as UserModel

from app.routers.auth import router as auth_router
from app.routers.doctors import router as doctors_router
from app.routers.patients import router as patients_router

from app.utils.logging_config import setup_logging, get_logger


# =========================================================
# LOGGING
# =========================================================

setup_logging()

logger = get_logger(__name__)


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Doctor Patient Management API",
    description="Production-style FastAPI backend for managing doctors and patients",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# =========================================================
# GLOBAL EXCEPTION HANDLER
# =========================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    # Log the actual error on the server
    logger.exception(
        "Unhandled exception occurred while processing %s %s",
        request.method,
        request.url.path
    )

    # Return a safe message to the API client
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error"
        }
    )


# =========================================================
# ROUTERS
# =========================================================

app.include_router(auth_router)
app.include_router(doctors_router)
app.include_router(patients_router)


# =========================================================
# HOME
# =========================================================

@app.get("/api/v1/")
def home():
    logger.info("Home endpoint called")

    return {
        "message": "Doctor Patient API is working"
    }


# =========================================================
# PROTECTED TEST ROUTE
# =========================================================

@app.get("/api/v1/protected")
def protected_route(
    current_user: UserModel = Depends(get_current_user)
):
    logger.info(
        "Protected endpoint accessed by user_id=%s",
        current_user.id
    )

    return {
        "message": "You are authenticated",
        "user_id": current_user.id,
        "username": current_user.username,
        "role": current_user.role
    }