import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from backend.app.services import anomaly_service

class _QueryResult:
    def __init__(self, result):
        self.result = result

    def filter(self, *args):
        return self

    def all(self):
        return self.result

    def first(self):
        return self.result


def test_detect_property_anomaly_creates_multiple_red_flags(monkeypatch):
    property_id = uuid.uuid4()
    anomaly_ids = iter([uuid.uuid4(), uuid.uuid4(), uuid.uuid4()])
    property_obj = SimpleNamespace(
        id=property_id,
        address="3 Rue de Metz",
        bathrooms=0,
        square_meters=40.0,
        zip_code="75001",
        property_type="apartment",
        bedrooms=1,
    )

    listing_obj = SimpleNamespace(property_id=property_id, asking_price="140000")
    audit_obj = SimpleNamespace(id=uuid.uuid4(), property_id=property_id, gross_yield_percentage=4.2)
    db = MagicMock()
    db.query.side_effect = [
        _QueryResult(property_obj),
        _QueryResult(listing_obj),
        _QueryResult(audit_obj),
        _QueryResult([]),
    ]

    monkeypatch.setattr(
        anomaly_service,
        "_build_rules",
        lambda *_: (
            {
                anomaly_service.LOW_YIELD_FLAG_TYPE: anomaly_service.LOW_YIELD_DESCRIPTION,
                anomaly_service.MISSING_INFO_FLAG_TYPE: "Missing or invalid basic info: bathrooms",
                anomaly_service.UNDERPRICED_FLAG_TYPE: "Price per sqm 3500 is far below peer average 5200 in zip 75001",
            },
            3500,
            5200,
            4
        )
    )

    monkeypatch.setattr(anomaly_service.uuid, "uuid4", lambda: next(anomaly_ids))

    result = anomaly_service.detect_property_anomaly(db, str(property_id))

    assert db.add.call_count == 3
    db.commit.assert_called_once()
    assert db.refresh.call_count == 3
    assert result["property_id"] == str(property_id)
    assert result["address"] == "3 Rue de Metz"
    assert result["audit_id"] == str(audit_obj.id)
    assert result["yield"] == 4.2
    assert result["red_flag"] is True
    assert result["triggered"] is True
    assert result["action"] == "updated"
    assert result["price_per_square_meter"] == 3500
    assert result["peer_average_price_per_square_meter"] == 5200
    assert result["comparables_analyzed"] == 4
    assert len(result["anomalies"]) == 3
    assert {item["flag_type"] for item in result["anomalies"]} == {
        anomaly_service.LOW_YIELD_FLAG_TYPE,
        anomaly_service.MISSING_INFO_FLAG_TYPE,
        anomaly_service.UNDERPRICED_FLAG_TYPE,
    }
    severities = {item["flag_type"]: item["severity"] for item in result["anomalies"]}
    assert severities[anomaly_service.LOW_YIELD_FLAG_TYPE] == "Medium"
    assert severities[anomaly_service.MISSING_INFO_FLAG_TYPE] == "High"
    assert severities[anomaly_service.UNDERPRICED_FLAG_TYPE] == "High"


def test_detect_property_anomaly_clears_existing_flags_when_rules_no_longer_match(monkeypatch):
    property_id = uuid.uuid4()
    property_obj = SimpleNamespace(
        id=property_id,
        address="18 Avenue Jean Jaures",
        bathrooms=1,
        square_meters=55.0,
        zip_code="69006",
        property_type="apartment",
        bedrooms=2,
    )

    listing_obj = SimpleNamespace(property_id=property_id, asking_price="310000")
    audit_obj = SimpleNamespace(id=uuid.uuid4(), property_id=property_id, gross_yield_percentage=5.4)
    existing_low_yield = SimpleNamespace(
        id=uuid.uuid4(),
        property_id=property_id,
        flag_type=anomaly_service.LOW_YIELD_FLAG_TYPE,
        description=anomaly_service.LOW_YIELD_DESCRIPTION,
        severity="Medium",
    )

    existing_pricing = SimpleNamespace(
        id=uuid.uuid4(),
        property_id=property_id,
        flag_type=anomaly_service.OVERPRICED_FLAG_TYPE,
        description="old description",
        severity="High",
    )

    db = MagicMock()
    db.query.side_effect = [
        _QueryResult(property_obj),
        _QueryResult(listing_obj),
        _QueryResult(audit_obj),
        _QueryResult([existing_low_yield, existing_pricing]),
    ]

    monkeypatch.setattr(
        anomaly_service,
        "_build_rules",
        lambda *_: (
            {},
            5636.36,
            5500,
            3,
        ),
    )

    result = anomaly_service.detect_property_anomaly(db, str(property_id))

    assert db.delete.call_count == 2
    db.commit.assert_called_once()
    db.add.assert_not_called()
    db.refresh.assert_not_called()
    assert result["property_id"] == str(property_id)
    assert result["red_flag"] is False
    assert result["triggered"] is False
    assert result["action"] == "updated"
    assert result["anomaly"] is None
    assert result["anomalies"] == []


def test_detect_property_anomaly_can_flag_missing_info_without_audit(monkeypatch):
    property_id = uuid.uuid4()
    property_obj = SimpleNamespace(
        id=property_id,
        address="22 Rue des Fleurs",
        bathrooms=0,
        square_meters=35,
        zip_code="33000",
        property_type="apartment",
        bedrooms=1,
    )

    listing_obj = SimpleNamespace(property_id=property_id, asking_price="120000")
    db = MagicMock()
    db.query.side_effect = [
        _QueryResult(property_obj),
        _QueryResult(listing_obj),
        _QueryResult(None),
        _QueryResult([]),
    ]

    monkeypatch.setattr(
        anomaly_service,
        "_build_rules",
        lambda *_: (
            {
                anomaly_service.MISSING_INFO_FLAG_TYPE: "Missing or invalid basic info: bathrooms"
            },
            3428.57,
            None,
            1,
        ),
    )

    result = anomaly_service.detect_property_anomaly(db, str(property_id))
    db.commit.assert_called_once()
    
    assert result["audit_id"] is None
    assert result["yield"] is None
    assert result["red_flag"] is True
    assert result["anomaly"]["flag_type"] == anomaly_service.MISSING_INFO_FLAG_TYPE
    assert result["anomaly"]["severity"] == "High"
