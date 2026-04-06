"""Anomaly detection service."""
import uuid
from sqlalchemy.orm import Session
from ..models.models import Anomaly, Audit, Listing, Property

LOW_YIELD_THRESHOLD = 4.6
LOW_YIELD_FLAG_TYPE = "Low Yield"
LOW_YIELD_DESCRIPTION = "Yield below 4.6%"
MISSING_INFO_FLAG_TYPE = "Missing Basic Info"
UNDERPRICED_FLAG_TYPE = "Suspiciously Cheap"
OVERPRICED_FLAG_TYPE = "Wildly Overpriced"
UNDERPRICED_THRESHOLD = 0.75
OVERPRICED_THRESHOLD = 1.35
MIN_COMPARABLES = 2
MIN_SIZE_RATIO = 0.6
MAX_SIZE_RATIO = 1.4
MANAGED_FLAG_TYPES = {LOW_YIELD_FLAG_TYPE, MISSING_INFO_FLAG_TYPE, UNDERPRICED_FLAG_TYPE, OVERPRICED_FLAG_TYPE}


def _to_float(value):
    return float(value) if value is not None else None


def _price_per_sqm(square_meters, asking_price):
    sqm = _to_float(square_meters)
    price = _to_float(asking_price)
    if sqm is None or price is None or sqm <= 0 or price <= 0:
        return None
    return price / sqm


def _serialize(anomalies):
    items = sorted(anomalies, key=lambda anomaly: anomaly.flag_type)
    return [{"id": str(anomaly.id), "flag_type": anomaly.flag_type, "description": anomaly.description} for anomaly in items]


def _check_low_yield(audit):
    if not audit or audit.gross_yield_percentage is None:
        return None
    if float(audit.gross_yield_percentage) >= LOW_YIELD_THRESHOLD:
        return None
    
    return LOW_YIELD_FLAG_TYPE, LOW_YIELD_DESCRIPTION


def _check_missing_info(property_obj):
    missing = []
    if property_obj.bathrooms is None or property_obj.bathrooms <= 0:
        missing.append("bathrooms")
    if property_obj.square_meters is None or property_obj.square_meters <= 0:
        missing.append("square_meters")
    if not str(property_obj.zip_code or "").strip():
        missing.append("zip_code")
    if not str(property_obj.property_type or "").strip():
        missing.append("property_type")
    if not missing:
        return None
    
    description = "Missing or invalid basic info: " + ", ".join(missing)
    return MISSING_INFO_FLAG_TYPE, description


def _collect_peer_prices(db: Session, property_obj):
    rows = (db
        .query(Property, Listing.asking_price)
        .join(Listing, Property.id == Listing.property_id)
        .filter(
            Property.zip_code == property_obj.zip_code,
            Property.property_type == property_obj.property_type,
            Property.id != property_obj.id
        )
    ).all()
    peer_prices = []
    
    current_size = _to_float(property_obj.square_meters)
    for other_property, other_price in rows:
        other_ppsm = _price_per_sqm(other_property.square_meters, other_price)
        
        if other_ppsm is None:
            continue
        if property_obj.bedrooms is not None and other_property.bedrooms is not None:
            if abs(other_property.bedrooms - property_obj.bedrooms) > 1:
                continue
        
        other_size = _to_float(other_property.square_meters)
        if current_size and other_size:
            ratio = other_size / current_size
            if ratio < MIN_SIZE_RATIO or ratio > MAX_SIZE_RATIO:
                continue
        peer_prices.append(other_ppsm)
    
    return peer_prices


def _check_price_gap(db: Session, property_obj, listing_obj):
    price_per_square_meter = _price_per_sqm(property_obj.square_meters, listing_obj.asking_price)
    if price_per_square_meter is None:
        return None, None, 0, None

    peer_prices = _collect_peer_prices(db, property_obj)
    comparables = len(peer_prices)
    if comparables < MIN_COMPARABLES:
        return price_per_square_meter, None, comparables, None
    
    peer_average = sum(peer_prices) / comparables
    if price_per_square_meter <= peer_average * UNDERPRICED_THRESHOLD:
        description = f"Price per sqm {price_per_square_meter:.2f} is far below peer average {peer_average:.2f} in zip {property_obj.zip_code}"
        return price_per_square_meter, peer_average, comparables, (UNDERPRICED_FLAG_TYPE, description)
    
    if price_per_square_meter >= peer_average * OVERPRICED_THRESHOLD:
        description = f"Price per sqm {price_per_square_meter:.2f} is far above peer average {peer_average:.2f} in zip {property_obj.zip_code}"
        return price_per_square_meter, peer_average, comparables, (OVERPRICED_FLAG_TYPE, description)
    
    return price_per_square_meter, peer_average, comparables, None


def _build_rules(db: Session, property_obj, listing_obj, audit):
    rules = {}

    for rule in (_check_low_yield(audit), _check_missing_info(property_obj)):
        if rule:
            flag_type, data = rule
            rules[flag_type] = data
    
    price_per_square_meter, peer_average, comparables, price_rule = _check_price_gap(db, property_obj, listing_obj)
    if price_rule:
        flag_type, data = price_rule
        rules[flag_type] = data
    
    return rules, price_per_square_meter, peer_average, comparables


def _sync_anomalies(db: Session, property_obj, rules):
    existing = db.query(Anomaly).filter(Anomaly.property_id == property_obj.id).all()
    active = []
    created = []
    seen = set()
    changed = False

    for anomaly in existing:
        if anomaly.flag_type not in MANAGED_FLAG_TYPES:
            continue
        if anomaly.flag_type in seen:
            db.delete(anomaly)
            changed = True
            continue
        seen.add(anomaly.flag_type)
        rule = rules.pop(anomaly.flag_type, None)

        if rule is None:
            db.delete(anomaly)
            changed = True
            continue
        
        description = rule
        if anomaly.description != description:
            anomaly.description = description
            changed = True
        active.append(anomaly)

    for flag_type, description in rules.items():
        anomaly = Anomaly(
            id=uuid.uuid4(),
            property_id=property_obj.id,
            flag_type=flag_type,
            description=description,
        )
        db.add(anomaly)
        active.append(anomaly)
        created.append(anomaly)
        changed = True

    if changed:
        db.commit()
        for anomaly in created:
            db.refresh(anomaly)
    
    return active, changed


def _build_response(property_obj, audit, anomalies, changed, price_per_square_meter, peer_average, comparables):
    red_flag = len(anomalies) > 0
    
    return {
        "property_id": str(property_obj.id),
        "address": property_obj.address,
        "audit_id": str(audit.id) if audit else None,
        "yield": float(audit.gross_yield_percentage) if audit and audit.gross_yield_percentage is not None else None,
        "red_flag": red_flag,
        "triggered": red_flag,
        "action": "updated" if changed else ("existing" if red_flag else "none"),
        "anomaly": anomalies[0] if anomalies else None,
        "anomalies": anomalies,
        "price_per_square_meter": round(price_per_square_meter, 2) if price_per_square_meter is not None else None,
        "peer_average_price_per_square_meter": round(peer_average, 2) if peer_average is not None else None,
        "comparables_analyzed": comparables
    }


def detect_property_anomaly(db: Session, property_id):
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise ValueError("Property not found")
    
    listing_obj = db.query(Listing).filter(Listing.property_id == property_id).first()
    if not listing_obj:
        raise ValueError("Listing not found")
    
    audit = db.query(Audit).filter(Audit.property_id == property_id).first()
    rules, price_per_square_meter, peer_average, comparables = _build_rules(db, property_obj, listing_obj, audit)
    active, changed = _sync_anomalies(db, property_obj, rules)
    anomalies = _serialize(active)
    
    return _build_response(property_obj, audit, anomalies, changed, price_per_square_meter, peer_average, comparables)
