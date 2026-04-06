"""Batch audit processing and anomaly management."""

import os
import sys
import uuid
from decimal import Decimal
from datetime import datetime

current_path = os.getcwd()
sys.path.append(os.path.join(current_path,".."))

from database import SessionLocal
from models import Property, Listing, Audit, Anomaly


def get_properties_without_audit(db):
    """Get properties that don't have audits."""
    properties = db.query(Property).all()
    audits = db.query(Audit).all()
    audited_ids = {a.property_id for a in audits}
    return [p for p in properties if p.id not in audited_ids]


def _audit_property(db, property_id):
    """Audit a single property (internal, uses existing session)."""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    listing_obj = db.query(Listing).filter(Listing.property_id == property_id).first()
    
    if not (property_obj and listing_obj):
        return None
    
    asking_price = Decimal(listing_obj.asking_price)
    estimated_rental_income = asking_price * Decimal("0.045")
    estimated_maintenance_costs = asking_price * Decimal("0.01")
    gross_yield_percentage = (estimated_rental_income / asking_price) * Decimal("100")
    
    audit = db.query(Audit).filter(Audit.property_id == property_id).first()
    if audit:
        audit.estimated_rental_income = estimated_rental_income
        audit.estimated_maintenance_costs = estimated_maintenance_costs
        audit.gross_yield_percentage = gross_yield_percentage
        audit.calculated_at = datetime.now(datetime.timezone.utc)
    else:
        audit = Audit(
            id=uuid.uuid4(),
            property_id=property_obj.id,
            estimated_rental_income=estimated_rental_income,
            estimated_maintenance_costs=estimated_maintenance_costs,
            gross_yield_percentage=gross_yield_percentage,
            calculated_at=datetime.now(datetime.timezone.utc),
        )
        db.add(audit)
    
    return audit


def batch_audit_properties(db):
    """Batch audit all properties without audits."""
    properties_without_audit = get_properties_without_audit(db)
    count = 0
    for prop in properties_without_audit:
        if _audit_property(db, prop.id):
            count += 1
    db.commit()
    return count


def evaluate_and_flag_anomalies(db):
    """Flag properties with low yield (< 4.6%)."""
    audits = db.query(Audit).all()
    inserted = 0
    for audit in audits:
        if audit.gross_yield_percentage < 4.6:
            anomaly = Anomaly(
                id=uuid.uuid4(),
                property_id=audit.property_id,
                flag_type="Low Yield",
                description="Yield below 4.6%",
                severity="Medium"
            )
            db.add(anomaly)
            inserted += 1
    db.commit()
    return inserted


def remove_duplicate_anomalies(db):
    """Remove duplicate anomalies per property."""
    anomalies = db.query(Anomaly).all()
    seen_properties = set()
    for anomaly in anomalies:
        if anomaly.property_id in seen_properties:
            db.delete(anomaly)
        else:
            seen_properties.add(anomaly.property_id)
    db.commit()


def run_batch_pipeline():
    """Run batch audit, evaluation, and cleanup pipeline."""
    db = SessionLocal()
    try:
        # Batch audit properties
        audited = batch_audit_properties(db)
        print(f"Audited {audited} properties")
        
        # Evaluate and flag anomalies
        flagged = evaluate_and_flag_anomalies(db)
        print(f"Flagged {flagged} anomalies")
        
        # Remove duplicates
        remove_duplicate_anomalies(db)
        print("Removed duplicate anomalies")
    finally:
        db.close()


if __name__ == "__main__":
    run_batch_pipeline()
