import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock
import uuid

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from backend.app.models.models import Audit
from backend.app.services import audit_service

class _FirstResultQuery:
    def __init__(self, result):
        self.result = result
        self.filter_calls = []

    def filter(self, *args, **kwargs):
        self.filter_calls.append((args, kwargs))
        return self

    def first(self):
        return self.result


def test_audit_single_property_creates_a_new_audit(monkeypatch):
    property_id = uuid.uuid4()
    audit_id = uuid.uuid4()
    property_obj = SimpleNamespace(id=property_id, address="12 Boulevard Saint-Germain")
    listing_obj = SimpleNamespace(property_id=property_id, asking_price="350000.00")
    metric_mock = Mock(
        return_value={
            "estimated_rental_income": 21000.0,
            "estimated_maintenance_costs": 3200.0,
            "gross_yield_percentage": 6.0,
        }
    )

    db = MagicMock()
    db.query.side_effect = [
        _FirstResultQuery(property_obj),
        _FirstResultQuery(listing_obj),
        _FirstResultQuery(None),
    ]

    monkeypatch.setattr(audit_service, "calculate_audit_metrics", metric_mock)
    monkeypatch.setattr(audit_service.uuid, "uuid4", lambda: audit_id)

    result = audit_service.audit_single_property(db, str(property_id))

    metric_mock.assert_called_once_with(property_obj, "350000.00")
    db.commit.assert_called_once()
    db.add.assert_called_once()

    created_audit = db.add.call_args.args[0]
    assert isinstance(created_audit, Audit)
    assert created_audit.id == audit_id
    assert created_audit.property_id == property_id
    assert created_audit.estimated_rental_income == 21000.0
    assert created_audit.estimated_maintenance_costs == 3200.0
    assert created_audit.gross_yield_percentage == 6.0

    assert result == {
        "property_id": str(property_id),
        "audit_id": str(audit_id),
        "address": "12 Boulevard Saint-Germain",
        "estimated_rental_income": 21000.0,
        "estimated_maintenance_costs": 3200.0,
        "gross_yield_percentage": 6.0,
        "yield": 6.0,
        "action": "created",
    }


def test_audit_single_property_updates_existing_audit(monkeypatch):
    property_id = uuid.uuid4()
    existing_audit = Audit(id=uuid.uuid4(), property_id=property_id)
    property_obj = SimpleNamespace(id=property_id, address="8 Rue de la Republique")
    listing_obj = SimpleNamespace(property_id=property_id, asking_price="280000.00")
    metric_mock = Mock(
        return_value={
            "estimated_rental_income": 16800.0,
            "estimated_maintenance_costs": 2500.0,
            "gross_yield_percentage": 6.0,
        }
    )
    
    db = MagicMock()
    db.query.side_effect = [
        _FirstResultQuery(property_obj),
        _FirstResultQuery(listing_obj),
        _FirstResultQuery(existing_audit),
    ]

    monkeypatch.setattr(audit_service, "calculate_audit_metrics", metric_mock)

    result = audit_service.audit_single_property(db, str(property_id))

    db.add.assert_not_called()
    db.commit.assert_called_once()
    assert existing_audit.estimated_rental_income == 16800.0
    assert existing_audit.estimated_maintenance_costs == 2500.0
    assert existing_audit.gross_yield_percentage == 6.0
    assert result["audit_id"] == str(existing_audit.id)
    assert result["action"] == "updated"


def test_audit_single_property_raises_when_property_is_missing():
    db = MagicMock()
    db.query.side_effect = [_FirstResultQuery(None)]

    with pytest.raises(ValueError, match="Property not found"):
        audit_service.audit_single_property(db, str(uuid.uuid4()))
