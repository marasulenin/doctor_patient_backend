 Doctor Patient Management API

A production-style REST API built with **FastAPI** for managing doctors, patients, authentication, doctor-patient relationships, appointments, audit logging, and role-based access control.

 Features

Authentication & Authorization

* User registration
* JWT-based authentication
* Secure password hashing
* Password strength validation
* Protected API endpoints
* Role-based access control
* Admin and Doctor roles
* Inactive user account protection
* Invalid JWT protection

 Doctor Management

* Create doctor
* Get doctor by ID
* Get all doctors
* Update doctor
* Partial update using PATCH
* Soft delete doctor
* Filter by specialization
* Filter by active status
* Pagination
* Duplicate email prevention

Patient Management

* Create patient
* Get patient by ID
* Get all patients
* Update patient
* Partial update using PATCH
* Delete patient
* Filter patients by age
* Pagination
* Patient-doctor relationship

 Doctor-Patient Relationship

* Assign patients to doctors
* Prevent assignment to non-existing doctors
* Prevent assignment to inactive doctors
* Retrieve patients assigned to a doctor
* Doctors can only view their own assigned patients
* Admins can view patients assigned to any doctor

 Appointment Management

* Create appointments
* Get all appointments
* Get appointment by ID
* Update appointments
* Cancel appointments
* Appointment status validation
* Prevent appointments with inactive doctors
* Prevent appointments for non-existing patients
* Prevent appointments when the patient is not assigned to the doctor

Supported appointment statuses:

text
scheduled
completed
cancelled


 Audit Logging

The application supports audit logging for tracking important system actions.

Audit information includes:

* User ID
* Action
* Resource
* Resource ID
* Description
* Timestamp

Validation & Data Integrity

* Pydantic request validation
* Email validation
* Password strength validation
* Patient age validation
* Phone validation
* Unique doctor email
* Foreign key constraints
* Appointment status database constraint
* User account status validation
* Integrity error handling

Security

* JWT authentication
* Secure password hashing using `pwdlib`
* Password strength requirements
* Environment-based secret key configuration
* Role-based authorization
* Protected endpoints
* Inactive account protection
* Database foreign key enforcement
* CORS configuration
* Generic internal server error responses
* Database integrity error handling

Performance

* SQLAlchemy `select()` queries
* Pagination
* Database-level filtering
* Efficient count queries
* Indexed database columns
* Ordered query results

 Logging

Centralized application logging is implemented for:

* Authentication
* Doctor operations
* Patient operations
* Appointment operations
* Database errors
* Unhandled exceptions
* Important business operations

---

 Tech Stack

| Technology  | Purpose                    |
| ----------- | -------------------------- |
| Python 3.14 | Programming language       |
| FastAPI     | REST API framework         |
| SQLAlchemy  | ORM                        |
| SQLite      | Development database       |
| Pydantic    | Data validation            |
| JWT         | Authentication             |
| pwdlib      | Password hashing           |
| Alembic     | Database migrations        |
| Uvicorn     | ASGI server                |
| Pytest      | Automated testing          |
| Docker      | Containerization           |
| CORS        | Cross-origin configuration |

---

 Project Structure

 text

doctor_patient_backend/
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── app/
│   ├── auth/
│   │   ├── dependencies.py
│   │   ├── jwt.py
│   │   └── password.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── doctor.py
│   │   ├── patient.py
│   │   ├── appointment.py
│   │   └── audit_log.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── doctors.py
│   │   ├── patients.py
│   │   └── appointments.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── doctor.py
│   │   ├── patient.py
│   │   └── appointment.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── doctor_service.py
│   │   ├── patient_service.py
│   │   ├── appointment_service.py
│   │   └── audit_service.py
│   │
│   ├── utils/
│   │   └── logging_config.py
│   │
│   ├── config.py
│   ├── database.py
│   └── main.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_api.py
│
├── .env
├── .gitignore
├── alembic.ini
├── Dockerfile
├── pytest.ini
├── requirements.txt
└── README.md


---

 Authentication

The API uses JWT Bearer authentication.

Register

http
POST /api/v1/auth/register


Example:

json
{
    "username": "doctoruser",
    "email": "doctor@example.com",
    "password": "Doctor@123",
    "role": "doctor"
}


 Login

http
POST /api/v1/auth/login


The login endpoint uses OAuth2 form data:

text
username = doctor@example.com
password = Doctor@123


Successful authentication returns:

json
{
    "access_token": "JWT_TOKEN",
    "token_type": "bearer"
}


Use the returned token in protected requests:

text
Authorization: Bearer <access_token>


---

 Roles & Permissions

Admin

Admins can:

* Manage doctors
* Manage patients
* Assign patients to doctors
* Manage appointments
* View doctors
* View patients
* View appointments

Doctor

Doctors can:

* Authenticate
* Access protected endpoints
* View their own assigned patients
* View their own appointments

Doctors cannot perform admin-only management operations.

---

 API Endpoints

All application endpoints use the `/api/v1/` prefix.

Authentication

| Method | Endpoint                | Access |
| ------ | ----------------------- | ------ |
| POST   | `/api/v1/auth/register` | Public |
| POST   | `/api/v1/auth/login`    | Public |

 Doctors

| Method | Endpoint                                            | Access         |
| ------ | --------------------------------------------------- | -------------- |
| POST   | `/api/v1/doctors`                                   | Admin          |
| GET    | `/api/v1/doctors`                                   | Admin          |
| GET    | `/api/v1/doctors/{doctor_id}`                       | Admin          |
| PUT    | `/api/v1/doctors/{doctor_id}`                       | Admin          |
| PATCH  | `/api/v1/doctors/{doctor_id}`                       | Admin          |
| DELETE | `/api/v1/doctors/{doctor_id}`                       | Admin          |
| POST   | `/api/v1/doctors/{doctor_id}/patients/{patient_id}` | Admin          |
| GET    | `/api/v1/doctors/{doctor_id}/patients`              | Admin / Doctor |

 Patients

| Method | Endpoint                        | Access |
| ------ | ------------------------------- | ------ |
| POST   | `/api/v1/patients`              | Admin  |
| GET    | `/api/v1/patients`              | Admin  |
| GET    | `/api/v1/patients/{patient_id}` | Admin  |
| PUT    | `/api/v1/patients/{patient_id}` | Admin  |
| PATCH  | `/api/v1/patients/{patient_id}` | Admin  |
| DELETE | `/api/v1/patients/{patient_id}` | Admin  |

Appointments

| Method | Endpoint                                | Access         |
| ------ | --------------------------------------- | -------------- |
| POST   | `/api/v1/appointments`                  | Admin          |
| GET    | `/api/v1/appointments`                  | Admin          |
| GET    | `/api/v1/appointments/{appointment_id}` | Admin / Doctor |
| PUT    | `/api/v1/appointments/{appointment_id}` | Admin          |
| DELETE | `/api/v1/appointments/{appointment_id}` | Admin          |

---

 API Documentation

FastAPI automatically provides interactive API documentation.

After starting the application, open:

text
http://127.0.0.1:8000/docs


Alternative OpenAPI documentation:

text
http://127.0.0.1:8000/redoc


---

 Database & Migrations

The project uses **SQLAlchemy** for database operations and **Alembic** for database migrations.

Create a migration:

powershell
alembic revision --autogenerate -m "migration message"


Apply migrations:

powershell
alembic upgrade head


Check current migration:

powershell
alembic current


View migration history:

powershell
alembic history


---

 Environment Variables

Create a `.env` file in the project root.

Example:

env
DATABASE_URL=sqlite:///./doctor_patient.db

SECRET_KEY=your-secret-key

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30

CORS_ORIGINS=http://localhost:3000,http://localhost:5173


**Do not commit the real `.env` file to GitHub.**

Use `.env.example` for sharing configuration structure.

---

 Running the Application

1. Clone the repository

powershell
git clone <your-repository-url>
cd doctor_patient_backend


 2. Create a virtual environment

```powershell
python -m venv venv
```

 3. Activate the virtual environment

Windows PowerShell:

powershell
.\venv\Scripts\Activate.ps1


 4. Install dependencies

powershell
pip install -r requirements.txt


5. Configure environment variables

Create `.env` and configure the required variables.

 6. Apply database migrations

powershell
alembic upgrade head


 7. Start the server

powershell
uvicorn app.main:app --reload


The API will be available at:

text
http://127.0.0.1:8000


Swagger UI:

text
http://127.0.0.1:8000/docs


---

 Testing

The project uses **Pytest** for automated testing.

Run the complete test suite:

powershell
pytest -v


Run authentication tests:

powershell
pytest -v tests/test_auth.py


Run API tests:

powershell
pytest -v tests/test_api.py


The tests use a separate in-memory SQLite database so test data does not modify the development database.

---

 Architecture

The project follows a layered backend architecture:

```text
Client
   │
   ▼
FastAPI Router
   │
   ▼
Pydantic Schema
   │
   ▼
Service Layer
   │
   ▼
SQLAlchemy ORM
   │
   ▼
Database
```

Authentication flow:

```text
Client
   │
   ▼
Login
   │
   ▼
JWT Token
   │
   ▼
Protected Endpoint
   │
   ▼
JWT Validation
   │
   ▼
Role Authorization
   │
   ▼
Service Layer
   │
   ▼
Database


---

 Error Handling

The API provides centralized handling for:

* Authentication errors
* Authorization errors
* Validation errors
* Resource-not-found errors
* Database integrity errors
* Unexpected server errors

Internal server errors return a generic response rather than exposing sensitive implementation details.

Example:

json
{
    "detail": "Internal server error"
}


---

 Database Relationships

The main relationships are:

```text
User
 │
 │ 1:1
 ▼
Doctor
 │
 │ 1:N
 ▼
Patient
 │
 │ 1:N
 ▼
Appointment


Doctors can have multiple patients.

Patients can be assigned to a doctor.

Doctors and patients can have multiple appointments.

---

 Audit Logging

Important application actions can be recorded in the `audit_logs` table.

Audit records contain:

```text
user_id
action
resource
resource_id
description
created_at


This provides a foundation for tracking important system activity.

---

 Docker

The project includes Docker support through the `Dockerfile`.

Build the image:

powershell
docker build -t doctor-patient-api .


Run the container:

powershell
docker run -p 8000:8000 doctor-patient-api


Then access:

text
http://127.0.0.1:8000/docs


---

 Project Status

The following backend capabilities have been implemented:

* Authentication
* JWT authorization
* Role-based access control
* Doctor management
* Patient management
* Doctor-patient relationships
* Appointment management
* Data validation
* Database integrity constraints
* Pagination and filtering
* Performance optimization
* Audit logging
* Security hardening
* Centralized logging
* Global exception handling
* Automated testing
* Test database isolation
* Alembic migrations
* Docker support
* API documentation

---

 Development

This project was developed as a backend learning and implementation project focused on:

* FastAPI
* REST API design
* SQLAlchemy
* Database relationships
* Authentication
* Authorization
* Validation
* Business logic
* Testing
* Production-oriented backend practices



 