import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import engine
from app.db.models import Base

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Create all tables before tests
    Base.metadata.create_all(bind=engine)
    yield
    # Optionally, drop tables after tests
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)
class TestBiometricType:
    def test_list_patients_empty(self):
        response = client.get("/api/v1/patients?page=1&size=10")
        assert response.status_code == 200
        data = response.json()
        assert "page" in data
        assert "size" in data
        assert "total" in data
        assert "items" in data
        assert isinstance(data["items"], list)