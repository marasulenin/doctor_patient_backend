from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from app.auth.dependencies import get_current_user
from app.database import Base, engine
from app.models import User, Doctor, Patient
from app.models.user import User as UserModel

from app.routers.auth import router as auth_router
from app.routers.doctors import router as doctors_router
from app.routers.patients import router as patients_router


# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(
    title="Doctor Patient Management API",
    description="Production-style FastAPI backend for managing doctors and patients",
    version="1.0.0"
)


# Global error handler
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


# Register routers
app.include_router(auth_router)
app.include_router(doctors_router)
app.include_router(patients_router)


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Doctor Patient API is working"
    }


# Protected test endpoint
@app.get("/protected")
def protected_route(
    current_user: UserModel = Depends(get_current_user)
):
    return {
        "message": "You are authenticated",
        "user_id": current_user.id,
        "username": current_user.username,
        "role": current_user.role
    }