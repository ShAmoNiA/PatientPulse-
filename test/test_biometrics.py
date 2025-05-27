import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import engine
from app.db.models import Base

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)
class TestBiometricsAPI:
    def test_get_biometric_history_empty(self):
        response = client.get("/api/v1/biometrics?patient_id=1&page=1&size=10")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 10
        assert data["total"] == 0
        assert isinstance(data["items"], list)

    def test_upsert_biometric_and_get(self):
        payload = {
            "patient_id": 1,
            "timestamp": "2024-06-01T12:00:00Z",
            "type": "glucose",
            "value": 80
        }
        response = client.post("/api/v1/biometrics", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["patient_id"] == 1
        assert data["type"] == "glucose"
        assert data["value"] == 80

        # Get biometrics for patient
        response = client.get("/api/v1/biometrics?patient_id=1")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["type"] == "glucose"

    def test_delete_biometric(self):
        payload = {
            "patient_id": 2,
            "timestamp": "2024-06-01T13:00:00Z",
            "type": "systolic",
            "value": 120
        }
        response = client.post("/api/v1/biometrics", json=payload)
        assert response.status_code == 200
        biometric_id = response.json()["id"]

        # Delete the biometric
        response = client.delete(f"/api/v1/biometrics/{biometric_id}")
        assert response.status_code == 200
        assert response.json()["ok"] is True

        # Ensure it's deleted
        response = client.get("/api/v1/biometrics?patient_id=2")
        assert response.status_code == 200
        assert response.json()["total"] == 0