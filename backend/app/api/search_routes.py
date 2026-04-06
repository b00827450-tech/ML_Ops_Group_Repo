"""Search routes."""

from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..services.search_service import search_properties

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("")
def search(
    city: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    results = search_properties(
        db,
        city=city,
        price_min=price_min,
        price_max=price_max,
        limit=limit
    )
    
    return {"count": len(results), "results": results}
