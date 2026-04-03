"""Search service."""

from sqlalchemy.orm import Session
from ..models.models import Property, Listing


def search_properties(db: Session, city=None, price_min=None, price_max=None, limit=10):
    query = db.query(Property, Listing.asking_price).join(Listing, Property.id == Listing.property_id)

    if city:
        query = query.filter(Property.city == city)
    if price_min is not None:
        query = query.filter(Listing.asking_price >= price_min)
    if price_max is not None:
        query = query.filter(Listing.asking_price <= price_max)

    rows = query.limit(limit).all()
    results = []
    for property_obj, asking_price in rows:
        results.append({
            "id": str(property_obj.id),
            "address": property_obj.address,
            "city": property_obj.city,
            "zip_code": property_obj.zip_code,
            "property_type": property_obj.property_type,
            "bedrooms": property_obj.bedrooms,
            "bathrooms": property_obj.bathrooms,
            "square_meters": property_obj.square_meters,
            "year_built": property_obj.year_built,
            "asking_price": float(asking_price),
        })

    return results
