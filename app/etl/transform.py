import re
from datetime import datetime
from app.db.models import BiometricType

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

def validate_patient(raw: dict) -> dict:
    raw["dob"] = datetime.fromisoformat(raw["dob"]).date()
    if not EMAIL_REGEX.fullmatch(raw["email"]):
        raise ValueError(f"Invalid email: {raw['email']}")
    raw["gender"] = raw["gender"].lower()
    return raw

def normalize_reading(raw: dict) -> list[dict]:
    raw["timestamp"] = datetime.fromisoformat(raw["timestamp"])
    normalized = []
    for key, val in raw.items():
        if key in ("patient_email", "timestamp") or val in (None, ""):
            continue
        name = key.split("_")[0]
        if name not in BiometricType.__members__:
            continue
        normalized.append({
            "email": raw["patient_email"],
            "timestamp": raw["timestamp"],
            "type": name,
            "value": float(val)
        })
    return normalized