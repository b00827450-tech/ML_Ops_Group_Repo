"""Audit routes."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..services.audit import audit_single_property

router = APIRouter(prefix="/api/audit", tags=["audit"])

class AuditRequest(BaseModel):
    property_id: str


@router.post("")
def audit(request: AuditRequest, db: Session = Depends(get_db)):
    try:
        return audit_single_property(db, request.property_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
