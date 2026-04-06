

from database import SessionLocal
import models


def search_properties(city=None, price_min=None, price_max=None, limit=5):

    db = SessionLocal()

    try:

        query = db.query(models.Property).join(
            models.Listing,
            models.Property.id == models.Listing.property_id
        )

        # Apply city filter if provided
        if city:
            query = query.filter(models.Property.city == city)

        # Apply minimum price filter
        if price_min is not None:
            query = query.filter(models.Listing.asking_price >= price_min)

        # Apply maximum price filter
        if price_max is not None:
            query = query.filter(models.Listing.asking_price <= price_max)

        properties = query.limit(limit).all()

        results = []
        for p in properties:
            results.append({
                "id": str(p.id),
                "address": p.address,
                "city": p.city,
                "zip_code": p.zip_code,
                "property_type": p.property_type,
                "bedrooms": p.bedrooms,
                "bathrooms": p.bathrooms,
                "square_meters": p.square_meters,
                "year_built": p.year_built
            })

        return results

    finally:
        db.close()