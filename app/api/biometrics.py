from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Biometric
from app.schemas.pydantic_models import BiometricIn, BiometricOut

router = APIRouter(tags=["biometrics"])

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()


class BiometricListOut(BaseModel):
    page: int
    size: int
    total: int
    items: List[BiometricOut]

@router.get("/biometrics", response_model=BiometricListOut)
def get_biometric_history(
    patient_id: int = Query(...),
    type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Biometric).filter(Biometric.patient_id == patient_id)

    if type:
        query = query.filter(Biometric.type == type)

    total = query.count()
    items = (
        query.order_by(Biometric.timestamp.desc())
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


@router.post("/biometrics", response_model=BiometricOut)
def upsert_biometric(
    data: BiometricIn,
    db: Session = Depends(get_db)
):
    biometric = db.query(Biometric).filter_by(
        patient_id=data.patient_id,
        timestamp=data.timestamp,
        type=data.type
    ).first()

    if biometric:
        biometric.value = data.value
    else:
        biometric = Biometric(**data.dict())
        db.add(biometric)

    db.commit()
    db.refresh(biometric)
    return biometric

@router.delete("/biometrics/{biometric_id}")
def delete_biometric(
    biometric_id: int,
    db: Session = Depends(get_db)
):
    biometric = db.query(Biometric).filter_by(id=biometric_id).first()

    if not biometric:
        raise HTTPException(status_code=404, detail="Biometric record not found")

    db.delete(biometric)
    db.commit()

    return {"ok": True, "deleted_id": biometric_id}


