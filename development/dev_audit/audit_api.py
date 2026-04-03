"""
Audit API Module

This module provides real-time API endpoints for auditing individual properties.
Can be integrated with FastAPI, Flask, or other web frameworks.
"""

import os
import sys
import uuid
from decimal import Decimal
from datetime import datetime

current_path = os.getcwd()
sys.path.append(os.path.join(current_path,".."))

from database import SessionLocal
from models import Property, Listing, Audit


def audit_single_property(property_id):
    """Create or update audit for a single property."""
    db = SessionLocal()
    try:
        property_obj = db.query(Property).filter(Property.id == property_id).first()
        if not property_obj:
            return {"success": False, "error": "Property not found"}
        
        listing_obj = db.query(Listing).filter(Listing.property_id == property_id).first()
        if not listing_obj:
            return {"success": False, "error": "Listing not found"}
        
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
            action = "updated"
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
            action = "created"
        
        db.commit()
        return {
            "success": True,
            "audit_id": str(audit.id),
            "property_id": str(property_obj.id),
            "address": property_obj.address,
            "yield": float(gross_yield_percentage),
            "action": action
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()
