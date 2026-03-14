"""
Search module for property listings.

This script provides functions to query properties from the database
based on user-defined filters such as city and price range.

"""

from database import SessionLocal
import models


def search_properties(city=None, price_min=None, price_max=None, limit=5):
    """
    Search properties using optional filters.

    Parameters
    ----------
    city : str | None
        Filter properties by city name.
    price_min : float | None
        Minimum asking price.
    price_max : float | None
        Maximum asking price.
    limit : int
        Maximum number of results returned.

    Returns
    -------
    List[dict]
        A list of property records formatted as dictionaries.
    """

    # Create a database session
    db = SessionLocal()

    try:
        # Base query:
        # join Property table with Listing table to access price info
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

        # Execute query with limit
        properties = query.limit(limit).all()

        # Format results into API-friendly dictionaries
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
        # Always close DB session to avoid connection leaks
        db.close()