
from typing import Optional, List, Dict, Any

from development.database import SessionLocal
from development.models import Property, Listing


#测试数据库连接
#db = SessionLocal()

#try:
 #   results = db.query(Listing).limit(3).all()
  #  print(results)
#finally:
 #   db.close()



def search_properties(
    city: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Search property listings by city and/or price range.

    Parameters
    ----------
    city : str, optional
        City name for filtering properties.
    price_min : float, optional
        Minimum asking price.
    price_max : float, optional
        Maximum asking price.
    limit : int, optional
        Maximum number of returned results.

    Returns
    -------
    List[Dict[str, Any]]
        A list of matching property listings with related info.
    """

    # Basic input validation
    if city is None and price_min is None and price_max is None:
        raise ValueError("At least one search condition must be provided.")

    if price_min is not None and price_max is not None and price_min > price_max:
        raise ValueError("price_min cannot be greater than price_max.")

    if limit <= 0:
        raise ValueError("limit must be a positive integer.")

    db = SessionLocal()

    try:
        # Start from Listing because search focuses on listed properties
        query = db.query(Listing).join(Property, Property.id == Listing.property_id)

        # Optional status filter
        # If your team uses "active" as the available listing status, keep this line.
        # If not, change it later according to your actual data.
        query = query.filter(Listing.status == "active")

        # Filter by city
        if city is not None:
            city = city.strip()
            query = query.filter(Property.city.ilike(city))

        # Filter by minimum price
        if price_min is not None:
            query = query.filter(Listing.asking_price >= price_min)

        # Filter by maximum price
        if price_max is not None:
            query = query.filter(Listing.asking_price <= price_max)

        # Order by latest listing first
        results = query.order_by(Listing.listed_date.desc()).limit(limit).all()

        output = []

        for listing in results:
            prop = listing.property

            asking_price = float(listing.asking_price) if listing.asking_price is not None else None

            price_per_m2 = None
            if (
                asking_price is not None
                and prop.square_meters is not None
                and prop.square_meters > 0
            ):
                price_per_m2 = round(asking_price / prop.square_meters, 2)

            output.append({
                "property_id": str(prop.id),
                "listing_id": str(listing.id),
                "address": prop.address,
                "city": prop.city,
                "zip_code": prop.zip_code,
                "property_type": prop.property_type,
                "bedrooms": prop.bedrooms,
                "bathrooms": prop.bathrooms,
                "square_meters": prop.square_meters,
                "year_built": prop.year_built,
                "asking_price": asking_price,
                "status": listing.status,
                "listed_date": listing.listed_date.isoformat() if listing.listed_date else None,
                "price_per_m2": price_per_m2
            })

        return output

    finally:
        db.close()


def print_search_results(results: List[Dict[str, Any]]) -> None:
    """
    Print search results in a simple readable format.
    """
    if not results:
        print("No matching properties found.")
        return

    print(f"Found {len(results)} matching properties:\n")

    for i, item in enumerate(results, start=1):
        print(f"Result {i}")
        print(f"  Property ID   : {item['property_id']}")
        print(f"  Listing ID    : {item['listing_id']}")
        print(f"  Address       : {item['address']}")
        print(f"  City          : {item['city']}")
        print(f"  Zip Code      : {item['zip_code']}")
        print(f"  Type          : {item['property_type']}")
        print(f"  Bedrooms      : {item['bedrooms']}")
        print(f"  Bathrooms     : {item['bathrooms']}")
        print(f"  Size (m²)     : {item['square_meters']}")
        print(f"  Year Built    : {item['year_built']}")
        print(f"  Asking Price  : {item['asking_price']}")
        print(f"  Price per m²  : {item['price_per_m2']}")
        print(f"  Status        : {item['status']}")
        print(f"  Listed Date   : {item['listed_date']}")
        print("-" * 50)


if __name__ == "__main__":
    # Example tests
    try:
        print("=== Search by city ===")
        city_results = search_properties(city="Paris", limit=5)
        print_search_results(city_results)

        print("\n=== Search by price range ===")
        price_results = search_properties(price_min=300000, price_max=500000, limit=5)
        print_search_results(price_results)

    except Exception as e:
        print(f"Error while running search: {e}")