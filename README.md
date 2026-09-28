 Doctor Patient Management API

A production-style REST API built with FastAPI for managing doctors, patients, authentication, and doctor-patient relationships.

 Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- JWT Authentication
- Alembic
- Uvicorn
- Docker
- CORS
- Pytest

 Features

 Authentication

- User registration
- JWT login
- Password hashing
- Protected API endpoints
- Role-based authorization

 Doctor Management

- Create doctor
- Get all doctors
- Get doctor by ID
- Update doctor
- Patch doctor
- Soft delete doctor
- Filter by specialization
- Filter by active status

Patient Management

- Create patient
- Get all patients
- Get patient by ID
- Update patient
- Patch patient
- Delete patient
- Filter patients by age
- Pagination

Doctor-Patient Relationship

- Assign patients to doctors
- Prevent assignment to non-existing doctors
- Prevent assignment to inactive doctors
- Get all patients assigned to a doctor

 Validation

- Email validation
- Unique doctor email
- Patient phone number validation
- Patient age validation
- Request/response schema validation

 Production Features

- API versioning with `/api/v1/`
- Centralized logging
- Global exception handling
- CORS configuration
- Environment variables
- Alembic database migrations
- Docker support
- Swagger/OpenAPI documentation

 Project Structure

text

doctor_patient_backend/
│
├── alembic/
│   └── versions/
│
├── app/
│   ├── auth/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   ├── config.py
│   ├── database.py
│   └── main.py
│
├── .env
├── .gitignore
├── alembic.ini
├── Dockerfile
├── requirements.txt
└── README.md