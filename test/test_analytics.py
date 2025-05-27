import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import engine, SessionLocal
from app.db.models import Base, Analytics

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)
class TestAnalytics:
    def test_get_patient_analytics_empty(self):
        response = client.get("/api/v1/analytics?patient_id=1")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_patient_analytics_with_data(self):
        from datetime import datetime
        db = SessionLocal()
        analytic = Analytics(
            patient_id=1,
            metric_name="glucose_min",
            value=70,
            computed_at=datetime.utcnow()
        )
        db.add(analytic)
        db.commit()
        db.refresh(analytic)
        db.close()

        response = client.get("/api/v1/analytics?patient_id=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["metric_name"] == "glucose_min"