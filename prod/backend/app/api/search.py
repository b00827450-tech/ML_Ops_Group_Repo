"""Search routes."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..services.search import search_properties

router = APIRouter(prefix="/api/search", tags=["search"])

class SearchRequest(BaseModel):
    city: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    limit: int = 10


@router.post("")
def search(request: SearchRequest, db: Session = Depends(get_db)):
    results = search_properties(
        db,
        city=request.city,
        price_min=request.price_min,
        price_max=request.price_max,
        limit=request.limit,
    )
    return {"count": len(results), "results": results}
