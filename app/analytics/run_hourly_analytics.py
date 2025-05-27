from sqlalchemy import func, and_
from app.db.models import Biometric, Analytics
from datetime import datetime, timedelta

from app.db.session import SessionLocal


def run_hourly_analytics():
    print("🔄 Running hourly analytics...")
    session = SessionLocal()
    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)

    # Query: group by patient_id and type, compute min, max, avg
    results = session.query(
        Biometric.patient_id,
        Biometric.type,
        func.min(Biometric.value),
        func.max(Biometric.value),
        func.avg(Biometric.value),
    ).filter(
        Biometric.timestamp >= one_hour_ago,
        Biometric.timestamp < now
    ).group_by(
        Biometric.patient_id,
        Biometric.type
    ).all()

    metrics = []
    for patient_id, btype, min_val, max_val, avg_val in results:
        computed_at = now.replace(minute=0, second=0, microsecond=0)
        metrics.extend([
            Analytics(patient_id=patient_id, metric_name=f"{btype}_min", value=min_val, computed_at=computed_at),
            Analytics(patient_id=patient_id, metric_name=f"{btype}_max", value=max_val, computed_at=computed_at),
            Analytics(patient_id=patient_id, metric_name=f"{btype}_avg", value=avg_val, computed_at=computed_at),
        ])

    if metrics:
        session.bulk_save_objects(metrics)
        session.commit()
        print(f"✅ Inserted {len(metrics)} analytics rows.")
    else:
        print("ℹ️ No new data to process.")

    session.close()
