
from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_admin():
    email = "pytest_admin_api@example.com"

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "pytest_admin_api",
            "email": email,
            "password": "Admin@123",
            "role": "admin"
        }
    )

    if register_response.status_code not in (201, 400):
        raise AssertionError(
            f"Admin registration failed: "
            f"{register_response.status_code} "
            f"{register_response.text}"
        )

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": "Admin@123"
        }
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


def create_doctor_user():
    email = "pytest_doctor_api@example.com"

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "pytest_doctor_api",
            "email": email,
            "password": "Doctor@123",
            "role": "doctor"
        }
    )

    if register_response.status_code not in (201, 400):
        raise AssertionError(
            f"Doctor registration failed: "
            f"{register_response.status_code} "
            f"{register_response.text}"
        )

    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": "Doctor@123"
        }
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


def test_admin_can_create_doctor():
    token = create_admin()

    response = client.post(
        "/api/v1/doctors",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Pytest Doctor",
            "specialization": "Cardiology",
            "email": "pytest_doctor_create@example.com"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Pytest Doctor"
    assert data["specialization"] == "Cardiology"
    assert data["email"] == "pytest_doctor_create@example.com"


def test_doctor_cannot_create_doctor():
    token = create_doctor_user()

    response = client.post(
        "/api/v1/doctors",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Unauthorized Doctor",
            "specialization": "Neurology",
            "email": "unauthorized_doctor@example.com"
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_admin_can_create_patient():
    token = create_admin()

    response = client.post(
        "/api/v1/patients",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Pytest Patient",
            "age": 30,
            "phone": "9000000001",
            "address": "Hyderabad",
            "gender": "Male"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Pytest Patient"
    assert data["age"] == 30
    assert data["phone"] == "9000000001"


def test_doctor_cannot_create_patient():
    token = create_doctor_user()

    response = client.post(
        "/api/v1/patients",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Unauthorized Patient",
            "age": 25,
            "phone": "9000000002"
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_admin_can_create_and_cancel_appointment():
    token = create_admin()

    doctor_response = client.post(
        "/api/v1/doctors",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Appointment Test Doctor",
            "specialization": "Neurology",
            "email": "pytest_appointment_doctor@example.com"
        }
    )

    assert doctor_response.status_code == 201

    doctor_id = doctor_response.json()["id"]

    patient_response = client.post(
        "/api/v1/patients",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Appointment Test Patient",
            "age": 40,
            "phone": "9000000003",
            "address": "Hyderabad",
            "gender": "Male"
        }
    )

    assert patient_response.status_code == 201

    patient_id = patient_response.json()["id"]

    assign_response = client.post(
        f"/api/v1/doctors/{doctor_id}/patients/{patient_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert assign_response.status_code == 200

    appointment_date = (
        datetime.now() + timedelta(days=1)
    ).isoformat()

    appointment_response = client.post(
        "/api/v1/appointments",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "appointment_date": appointment_date,
            "reason": "Routine checkup"
        }
    )

    assert appointment_response.status_code == 201

    appointment_id = appointment_response.json()["id"]

    assert appointment_response.json()["status"] == "scheduled"

    cancel_response = client.delete(
        f"/api/v1/appointments/{appointment_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"


def test_appointment_rejects_unassigned_patient():
    token = create_admin()

    doctor_response = client.post(
        "/api/v1/doctors",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Unassigned Test Doctor",
            "specialization": "Dermatology",
            "email": "pytest_unassigned_doctor@example.com"
        }
    )

    assert doctor_response.status_code == 201

    doctor_id = doctor_response.json()["id"]

    patient_response = client.post(
        "/api/v1/patients",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Unassigned Test Patient",
            "age": 28,
            "phone": "9000000004"
        }
    )

    assert patient_response.status_code == 201

    patient_id = patient_response.json()["id"]

    appointment_date = (
        datetime.now() + timedelta(days=1)
    ).isoformat()

    response = client.post(
        "/api/v1/appointments",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "doctor_id": doctor_id,
            "patient_id": patient_id,
            "appointment_date": appointment_date,
            "reason": "Test"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Patient is not assigned to this doctor"
    )


def test_invalid_appointment_status():
    token = create_admin()

    response = client.put(
        "/api/v1/appointments/1",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "status": "invalid_status"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid appointment status"


def test_invalid_pagination():
    token = create_admin()

    response = client.get(
        "/api/v1/doctors?page=0&limit=10",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 422

