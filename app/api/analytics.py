from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.models import Analytics
from app.db.session import SessionLocal
from app.schemas.pydantic_models import AnalyticsOut


def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

router = APIRouter()

@router.get("/analytics", response_model=List[AnalyticsOut])
def get_patient_analytics(
    patient_id: int = Query(...),
    metric: Optional[str] = Query(None, description="Optional metric name filter (e.g., glucose_min)"),
    db: Session = Depends(get_db)
):
    query = db.query(Analytics).filter(Analytics.patient_id == patient_id)

    if metric:
        query = query.filter(Analytics.metric_name == metric)

    results = query.order_by(Analytics.computed_at.desc()).all()
    return results