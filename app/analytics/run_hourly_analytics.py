from sqlalchemy import func, tuple_
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
    ).group_by(
        Biometric.patient_id,
        Biometric.type
    ).all()

    metrics = []
    computed_at = now.replace(minute=0, second=0, microsecond=0)
    for patient_id, btype, min_val, max_val, avg_val in results:
        metrics.extend([
            Analytics(patient_id=patient_id, metric_name=f"{btype}_min", value=min_val, computed_at=computed_at),
            Analytics(patient_id=patient_id, metric_name=f"{btype}_max", value=max_val, computed_at=computed_at),
            Analytics(patient_id=patient_id, metric_name=f"{btype}_avg", value=avg_val, computed_at=computed_at),
        ])

    if metrics:
        # Build set of unique keys for new metrics
        new_keys = set((m.patient_id, m.metric_name, m.computed_at) for m in metrics)
        # Query for existing analytics with these keys
        existing = set(
            session.query(Analytics.patient_id, Analytics.metric_name, Analytics.computed_at)
            .filter(
                tuple_(
                    Analytics.patient_id,
                    Analytics.metric_name,
                    Analytics.computed_at
                ).in_(list(new_keys))
            )
            .all()
        )
        # Filter out metrics that already exist
        to_insert = [m for m in metrics if (m.patient_id, m.metric_name, m.computed_at) not in existing]

        if to_insert:
            session.bulk_save_objects(to_insert)
            session.commit()
            print(f"Inserted {len(to_insert)} analytics rows.")
        else:
            print("No new data to process.")
    else:
        print("No new data to process.")

    session.close()