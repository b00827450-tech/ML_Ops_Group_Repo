
from search import search_properties
from database import SessionLocal
import models


def evaluate_search():
    print("Running Test 1: City filter")

    results_city = search_properties(city="Paris", limit=5)

    # Ensure limit respected
    assert len(results_city) <= 5, "ERROR: More results than limit"

    # Ensure all results belong to requested city
    for r in results_city:
        assert r["city"] == "Paris", f"ERROR: Wrong city returned → {r['city']}"

    print("Test 1 PASSED")


    print("Running Test 2: Price range filter")

    results_price = search_properties(price_min=300000, price_max=800000, limit=10)

    db = SessionLocal()
    try:
        for r in results_price:
            prop = db.query(models.Property).filter(models.Property.id == r["id"]).first()

            # Ensure property exists
            assert prop is not None, f"ERROR: Property missing in DB → {r['id']}"

            # Check price range using listing relation
            if prop.listings:
                price = float(prop.listings[0].asking_price)

                assert price >= 300000, f"ERROR: price below min → {price}"
                assert price <= 800000, f"ERROR: price above max → {price}"

        print("Test 2 PASSED")

    finally:
        db.close()


    print("Running Test 3: Output structure")

    if results_city:
        sample = results_city[0]

        required_fields = [
            "id",
            "address",
            "city",
            "zip_code",
            "property_type",
            "bedrooms",
            "bathrooms",
            "square_meters",
            "year_built"
        ]

        for f in required_fields:
            assert f in sample, f"ERROR: Missing output field → {f}"

        print("Test 3 PASSED")




if __name__ == "__main__":
    evaluate_search()