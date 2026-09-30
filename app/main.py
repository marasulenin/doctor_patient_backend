from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.database import Base, engine

# Models must be imported before create_all()
from app.models.user import User
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.billing import Billing

# Routers
from app.routers.auth import router as auth_router
from app.routers.doctors import router as doctors_router
from app.routers.patients import router as patients_router
from app.routers.appointments import router as appointments_router
from app.routers.billings import router as billings_router
from app.routers import reports


app = FastAPI(
    title="Doctor Patient Management API",
    description="FastAPI backend for Doctor, Patient, Appointment and Billing Management",
    version="1.0.0"
)


# ---------------------------------------------------------
# Database Initialization
# ---------------------------------------------------------

Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------
# Global Exception Handler
# ---------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error"
        }
    )


# ---------------------------------------------------------
# Root Endpoint
# ---------------------------------------------------------

@app.get(
    "/",
    tags=["default"]
)
def root():
    return {
        "message": "Doctor Patient Management API is running"
    }


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------

@app.get(
    "/health",
    tags=["default"]
)
def health_check():
    return {
        "status": "healthy"
    }


# ---------------------------------------------------------
# API Routers
# ---------------------------------------------------------

app.include_router(auth_router)

app.include_router(doctors_router)

app.include_router(patients_router)

app.include_router(appointments_router)

app.include_router(billings_router)

app.include_router(reports.router)