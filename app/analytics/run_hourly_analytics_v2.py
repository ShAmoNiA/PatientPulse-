# analytics/compute.py

from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models import BiometricHourly, Analytics   # import the new table
from app.db.session import SessionLocal


def run_hourly_analytics_v2() -> None:
    """Consume rows from biometrics_hourly → write analytics → purge the hourly buffer."""
    session: Session = SessionLocal()
    try:
        # ── 1. Aggregate current buffer ──────────────────────────────────────────
        rows = (
            session.query(
                BiometricHourly.patient_id,
                BiometricHourly.type,
                func.min(BiometricHourly.value),
                func.max(BiometricHourly.value),
                func.avg(BiometricHourly.value)
            )
            .group_by(BiometricHourly.patient_id, BiometricHourly.type)
            .all()
        )

        if not rows:          # nothing in the buffer
            session.rollback()
            return

        # ── 2. Build Analytics objects ───────────────────────────────────────────
        computed_at = datetime.utcnow().replace(second=0, microsecond=0)
        metrics = [
            Analytics(patient_id=pid, metric_name=f"{typ}_min", value=mn,  computed_at=computed_at)
            for pid, typ, mn, _, _ in rows
        ] + [
            Analytics(patient_id=pid, metric_name=f"{typ}_max", value=mx,  computed_at=computed_at)
            for pid, typ, _, mx, _ in rows
        ] + [
            Analytics(patient_id=pid, metric_name=f"{typ}_avg", value=av,  computed_at=computed_at)
            for pid, typ, _, _, av in rows
        ]

        session.bulk_save_objects(metrics)

        # delete *only* the rows we just used (safer than TRUNCATE in prod)
        session.query(BiometricHourly).delete(synchronize_session=False)

        session.commit()
        print(f"Analytics written: {len(metrics)}  •  Buffer cleared.")
    except Exception as exc:
        session.rollback()
        print(f"Analytics job failed: {exc}")
        raise
    finally:
        session.close()
