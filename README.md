# Doctor Patient Management API

A production-style REST API built with **FastAPI** for managing doctors, patients, authentication, and role-based access control.

 Features

* User registration and login
* JWT-based authentication
* Role-based authorization
* Doctor CRUD operations
* Patient CRUD operations
* Doctor–Patient relationship
* Request validation using Pydantic
* SQLAlchemy ORM
* SQLite database
* Password hashing
* Global exception handling
* Database transaction rollback
* Interactive Swagger API documentation
* Environment-based configuration
* Soft delete for doctors
* Permanent delete for patients
* Docker-ready project structure

 Tech Stack

* **Python 3.14**
* **FastAPI**
* **Uvicorn**
* **SQLAlchemy**
* **Pydantic**
* **SQLite**
* **python-jose**
* **Passlib**
* **python-dotenv**
* **Docker**

 Project Structure

doctor_patient_backend/
│
├── app/
│   ├── auth/
│   │   ├── dependencies.py
│   │   └── jwt.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── doctor.py
│   │   └── patient.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── doctors.py
│   │   └── patients.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── doctor.py
│   │   ├── patient.py
│   │   └── user.py
│   │
│   ├── services/
│   │   ├── doctor_service.py
│   │   └── patient_service.py
│   │
│   ├── config.py
│   ├── database.py
│   └── main.py
│
├── tests/
├── .env
├── .gitignore
├── Dockerfile
├── requirements.txt
└── README.md
```

> `.env`, the SQLite database, virtual environment, and Python cache files are excluded from Git using `.gitignore`.

## 🔐 Authentication

The API uses **JWT Bearer authentication**.

 Register

http
POST /auth/register


 Login

http
POST /auth/login


The login endpoint returns an access token:

json
{
  "access_token": "YOUR_ACCESS_TOKEN",
  "token_type": "bearer"
}


The token is then used to access protected endpoints.
 Protected Endpoint

http
GET /protected


Example response:

json
{
  "message": "You are authenticated",
  "user_id": 3,
  "username": "admin",
  "role": "admin"
}


 Doctor APIs

| Method | Endpoint               | Description       |
| ------ | ---------------------- | ----------------- |
| POST   | `/doctors`             | Create a doctor   |
| GET    | `/doctors`             | Get all doctors   |
| GET    | `/doctors/{doctor_id}` | Get doctor by ID  |
| PUT    | `/doctors/{doctor_id}` | Update doctor     |
| DELETE | `/doctors/{doctor_id}` | Deactivate doctor |


 Doctor Delete

Doctor deletion is implemented as a **soft delete**.

Instead of removing the database record:

text
is_active: true


is changed to:

text
is_active: false


 Patient APIs

| Method | Endpoint                 | Description       |
| ------ | ------------------------ | ----------------- |
| POST   | `/patients`              | Create a patient  |
| GET    | `/patients`              | Get all patients  |
| GET    | `/patients/{patient_id}` | Get patient by ID |
| PUT    | `/patients/{patient_id}` | Update patient    |
| DELETE | `/patients/{patient_id}` | Delete patient    |

Patients can optionally be assigned to a doctor using:

json
{
  "name": "Suresh Kumar",
  "age": 32,
  "phone": "9876543215",
  "doctor_id": 2
}


Database

The project uses **SQLAlchemy ORM** with SQLite.

Main tables:

text
users
doctors
patients


Relationships:

text
User
 │
 └── Doctor

Doctor
 │
 └──< Patients


A doctor can have multiple patients, while a patient can optionally be assigned to one doctor.


 Installation

 1. Clone the repository

bash
git clone https://github.com/marasulenin/doctor_patient_backend.git


 2. Navigate to the project

bash
cd doctor_patient_backend


3. Create a virtual environment

Windows:


powershell
python -m venv venv


 4. Activate the virtual environment

powershell
.\venv\Scripts\Activate.ps1


5. Install dependencies

powershell
pip install -r requirements.txt

Environment Variables

Create a `.env` file in the project root:

env
SECRET_KEY=your-long-random-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./doctor_patient.db


Do not commit `.env` to GitHub.


Run the Application

From the project root:

powershell
uvicorn app.main:app --reload


The application will run at:

text
http://127.0.0.1:8000


 API Documentation

FastAPI automatically provides interactive Swagger documentation.

Open:

text
http://127.0.0.1:8000/docs


Alternative ReDoc documentation:

text
http://127.0.0.1:8000/redoc

 API Testing

The APIs were tested using FastAPI Swagger UI, including:

* User login
* JWT authorization
* Protected endpoint
* Doctor creation
* Doctor retrieval
* Doctor update
* Doctor soft deletion
* Patient creation
* Patient retrieval
* Patient update
* Patient deletion
* Doctor–Patient relationship


 Error Handling

The application includes:

* HTTP exception handling
* Global exception handling
* Database rollback on failed transactions
* Authentication validation
* Role authorization
* Request validation
* Resource-not-found handling

 Security

Security-related configuration is stored in environment variables.

Sensitive files are excluded through `.gitignore`:

text
.env
venv/
__pycache__/
*.pyc
doctor_patient.db
*.tar.gz
*.whl


 Future Improvements

Possible future enhancements:

* PostgreSQL database
* Alembic database migrations
* Refresh tokens
* Email verification
* Password reset
* Pagination and filtering
* Search functionality
* API rate limiting
* Automated unit and integration tests
* CI/CD with GitHub Actions
* Docker deployment
* Cloud deployment
* Logging and monitoring
* Admin dashboard
* Production API documentation

 Author

Lenin Marasu

Python Backend Developer

GitHub:
https://github.com/marasulenin
