"""Anomaly routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..services.anomaly_service import get_saved_anomaly

router = APIRouter(prefix="/api/anomaly", tags=["anomaly"])


@router.get("/{property_id}")
def anomaly(property_id: str, db: Session = Depends(get_db)):
    try:
        return get_saved_anomaly(db, property_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
