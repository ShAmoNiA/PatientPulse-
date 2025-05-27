from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Patient
from app.schemas.pydantic_models import PatientOut

router = APIRouter(tags=["patients"])

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.get("/patients")
def list_patients(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    total = db.query(Patient).count()
    items = (
        db.query(Patient)
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return {
        "page": page,
        "size": size,
        "total": total,
        "items": items,
    }
