"""Audit service."""

import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..models.models import Property, Listing, Audit
from .audit_metrics import calculate_audit_metrics


def get_saved_audit(db: Session, property_id):
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise ValueError("Property not found")

    audit = db.query(Audit).filter(Audit.property_id == property_id).first()
    if not audit:
        raise ValueError("Audit not found")

    return {
        "property_id": str(property_obj.id),
        "audit_id": str(audit.id),
        "address": property_obj.address,
        "estimated_rental_income": float(audit.estimated_rental_income),
        "estimated_maintenance_costs": float(audit.estimated_maintenance_costs),
        "gross_yield_percentage": float(audit.gross_yield_percentage),
        "yield": float(audit.gross_yield_percentage),
        "action": "existing"
    }


def audit_single_property(db: Session, property_id):
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise ValueError("Property not found")

    listing_obj = db.query(Listing).filter(Listing.property_id == property_id).first()
    if not listing_obj:
        raise ValueError("Listing not found")

    audit_metrics = calculate_audit_metrics(property_obj, listing_obj.asking_price)
    estimated_rental_income = audit_metrics["estimated_rental_income"]
    estimated_maintenance_costs = audit_metrics["estimated_maintenance_costs"]
    gross_yield_percentage = audit_metrics["gross_yield_percentage"]

    audit = db.query(Audit).filter(Audit.property_id == property_id).first()
    if audit:
        audit.estimated_rental_income = estimated_rental_income
        audit.estimated_maintenance_costs = estimated_maintenance_costs
        audit.gross_yield_percentage = gross_yield_percentage
        audit.calculated_at = datetime.now(timezone.utc)
        action = "updated"
    else:
        audit = Audit(
            id=uuid.uuid4(),
            property_id=property_obj.id,
            estimated_rental_income=estimated_rental_income,
            estimated_maintenance_costs=estimated_maintenance_costs,
            gross_yield_percentage=gross_yield_percentage,
            calculated_at=datetime.now(timezone.utc),
        )
        db.add(audit)
        action = "created"

    db.commit()
    return {
        "property_id": str(property_obj.id),
        "audit_id": str(audit.id),
        "address": property_obj.address,
        "estimated_rental_income": float(estimated_rental_income),
        "estimated_maintenance_costs": float(estimated_maintenance_costs),
        "gross_yield_percentage": float(gross_yield_percentage),
        "yield": float(gross_yield_percentage),
        "action": action
    }