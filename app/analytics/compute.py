from sqlalchemy.exc import IntegrityError
from app.db.session import SessionLocal
from app.db.models import Patient, Biometric
from app.etl.extract import load_patients, load_readings
from app.etl.transform import validate_patient, normalize_reading

def run_etl():
    session = SessionLocal()

    # Step 1: Add or update patients
    for p in load_patients():
        data = validate_patient(p)
        patient = session.query(Patient).filter_by(email=data["email"]).first()
        if patient:
            for key, value in data.items():
                setattr(patient, key, value)
        else:
            session.add(Patient(**data))
    session.commit()

    # Step 2: Prepare biometric data (glucose, weight, etc.)
    existing = set(
        session.query(Biometric.patient_id, Biometric.timestamp, Biometric.type).all()
    )

    new_biometrics = []
    for raw in load_readings():
        for r in normalize_reading(raw):
            patient = session.query(Patient).filter_by(email=r["email"]).first()
            if not patient:
                continue  # Skip if patient not found

            key = (patient.id, r["timestamp"], r["type"])
            if key not in existing:
                new_biometrics.append(Biometric(
                    patient_id=patient.id,
                    timestamp=r["timestamp"],
                    type=r["type"],
                    value=r["value"]
                ))
                existing.add(key)

    # Step 3: Save new biometrics
    if new_biometrics:
        session.bulk_save_objects(new_biometrics)
        session.commit()

    session.close()
