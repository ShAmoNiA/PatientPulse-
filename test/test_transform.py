import pytest
from datetime import date, datetime
from app.etl.transform import validate_patient, normalize_reading
class TestTransform:
    def test_validate_patient_valid(self):
        raw = {
            "dob": "2000-01-01",
            "email": "test@example.com",
            "gender": "MALE"
        }
        result = validate_patient(raw.copy())
        assert result["dob"] == date(2000, 1, 1)
        assert result["email"] == "test@example.com"
        assert result["gender"] == "male"

    def test_validate_patient_invalid_email(self):
        raw = {
            "dob": "2000-01-01",
            "email": "invalid-email",
            "gender": "female"
        }
        with pytest.raises(ValueError):
            validate_patient(raw)

    def test_validate_patient_invalid_dob(self):
        raw = {
            "dob": "not-a-date",
            "email": "test@example.com",
            "gender": "male"
        }
        with pytest.raises(ValueError):
            validate_patient(raw)

    def test_normalize_reading_valid(self,monkeypatch):
        # Patch BiometricType to have known members
        from types import SimpleNamespace
        monkeypatch.setattr("app.db.models.BiometricType", SimpleNamespace(__members__={"glucose": 1, "weight": 2}))
        raw = {
            "patient_email": "a@b.com",
            "timestamp": "2024-06-01T12:00:00",
            "glucose": "100",
            "weight": "70",
            "systolic": None,
            "diastolic": "",
        }
        result = normalize_reading(raw.copy())
        assert len(result) == 2
        assert result[0]["type"] == "glucose"
        assert result[0]["value"] == 100.0
        assert result[1]["type"] == "weight"
        assert result[1]["value"] == 70.0
        assert all(r["email"] == "a@b.com" for r in result)
        assert all(isinstance(r["timestamp"], datetime) for r in result)

    def test_normalize_reading_skips_invalid(self,monkeypatch):
        monkeypatch.setattr("app.db.models.BiometricType", type("BT", (), {"__members__": {"glucose": 1}}))
        raw = {
            "patient_email": "a@b.com",
            "timestamp": "2024-06-01T12:00:00",
            "glucose": "100",
            "heart_rate": "80",  # not in __members__
        }
        result = normalize_reading(raw.copy())
        assert len(result) == 1
        assert result[0]["type"] == "glucose"

    def test_normalize_reading_empty(self, monkeypatch):
        monkeypatch.setattr("app.db.models.BiometricType", type("BT", (), {"__members__": {}}))
        raw = {
            "patient_email": "a@b.com",
            "timestamp": "2024-06-01T12:00:00",
        }
        result = normalize_reading(raw.copy())
        assert result == []