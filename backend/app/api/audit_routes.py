"""Audit routes."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..services.audit_service import get_saved_audit

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/{property_id}")
def audit(property_id: str, db: Session = Depends(get_db)):
    try:
        return get_saved_audit(db, property_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
