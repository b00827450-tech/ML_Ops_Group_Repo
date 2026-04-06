import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from backend.app.models.models import Listing, Property
from backend.app.services.search_service import search_properties


def _build_query(rows):
    query = MagicMock()
    query.join.return_value = query
    query.filter.return_value = query
    query.limit.return_value = query
    query.all.return_value = rows
    return query


def test_search_properties_applies_filters_and_serializes_results():
    property_id = uuid.uuid4()
    property_obj = SimpleNamespace(
        id=property_id,
        address="10 Rue de Rivoli",
        city="Paris",
        zip_code="75001",
        property_type="apartment",
        bedrooms=2,
        bathrooms=1,
        square_meters=52,
        year_built=1998,
    )
    query = _build_query([(property_obj, 420000)])
    db = MagicMock()
    db.query.return_value = query

    results = search_properties(
        db,
        city="Paris",
        price_min=300000,
        price_max=500000,
        limit=5,
    )

    db.query.assert_called_once_with(Property, Listing.asking_price)
    query.join.assert_called_once()
    assert query.filter.call_count == 3
    query.limit.assert_called_once_with(5)
    assert results == [
        {
            "id": str(property_id),
            "address": "10 Rue de Rivoli",
            "city": "Paris",
            "zip_code": "75001",
            "property_type": "apartment",
            "bedrooms": 2,
            "bathrooms": 1,
            "square_meters": 52,
            "year_built": 1998,
            "asking_price": 420000,
        }
    ]


def test_search_properties_uses_default_limit_when_no_filters_are_provided():
    property_obj = SimpleNamespace(
        id=uuid.uuid4(),
        address="5 Avenue Victor Hugo",
        city="Lyon",
        zip_code="69006",
        property_type="studio",
        bedrooms=0,
        bathrooms=1,
        square_meters=24,
        year_built=2012,
    )
    
    query = _build_query([(property_obj, 180000)])
    db = MagicMock()
    db.query.return_value = query

    results = search_properties(db)

    query.filter.assert_not_called()
    query.limit.assert_called_once_with(10)
    assert results[0]["city"] == "Lyon"
    assert results[0]["asking_price"] == 180000
