from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Float, Enum, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

class Gender(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    dob = Column(Date, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    address = Column(String)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    biometrics = relationship("Biometric", back_populates="patient")
    analytics = relationship("Analytics", back_populates="patient")

class BiometricType(str, enum.Enum):
    glucose = "glucose"
    systolic = "systolic"
    diastolic = "diastolic"
    weight = "weight"

class Biometric(Base):
    __tablename__ = "biometrics"
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    type = Column(Enum(BiometricType), nullable=False)
    value = Column(Float, nullable=False)
    patient = relationship("Patient", back_populates="biometrics")
    __table_args__ = (
        UniqueConstraint("patient_id", "timestamp", "type", name="u_patient_time_type"),
    )

from sqlalchemy.orm import relationship

class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    metric_name = Column(String)
    value = Column(Float)
    computed_at = Column(DateTime)

    patient = relationship("Patient", back_populates="analytics")
