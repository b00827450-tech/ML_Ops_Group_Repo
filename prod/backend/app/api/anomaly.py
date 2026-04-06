"""Anomaly routes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..services.anomaly import detect_property_anomaly

router = APIRouter(prefix="/api/anomaly", tags=["anomaly"])


class AnomalyRequest(BaseModel):
    property_id: str


@router.post("")
def anomaly(request: AnomalyRequest, db: Session = Depends(get_db)):
    try:
        return detect_property_anomaly(db, request.property_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
