from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.db.models import Gender, BiometricType

class PatientBase(BaseModel):
    name: str
    dob: date
    gender: Gender
    address: Optional[str]
    email: EmailStr
    phone: Optional[str]

class PatientOut(PatientBase):
    id: int
    class Config: orm_mode = True

class BiometricBase(BaseModel):
    timestamp: datetime
    type: BiometricType
    value: float

class BiometricIn(BaseModel):
    patient_id: int
    timestamp: datetime
    type: str
    value: float

class BiometricOut(BiometricBase):
    id: int; patient_id: int
    class Config: orm_mode = True

class AnalyticsOut(BaseModel):
    patient_id: int
    metric_name: str
    value: float
    computed_at: datetime
