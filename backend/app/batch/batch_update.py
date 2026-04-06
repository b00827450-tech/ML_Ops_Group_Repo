"""Run audit and anomaly batch updates every 6 hours."""

import time
from datetime import datetime

from ..core.database import ensure_database_schema, get_session_factory
from ..models.models import Listing, Property
from ..services.anomaly_service import detect_property_anomaly
from ..services.audit_service import audit_single_property

INTERVAL_SECONDS = 6 * 60 * 60


def _get_property_ids(db):
    properties = db.query(Property).join(Listing, Property.id == Listing.property_id).all()
    return list(dict.fromkeys(property_obj.id for property_obj in properties))


def _run_audit_batch():
    db = get_session_factory()()
    try:
        count = 0
        for property_id in _get_property_ids(db):
            try:
                audit_single_property(db, property_id)
                count += 1
            except ValueError:
                db.rollback()
            except Exception as exc:
                db.rollback()
                print(f"[{datetime.now().isoformat()}] Audit failed for {property_id}: {exc}")
        return count
    finally:
        db.close()


def _run_anomaly_batch():
    db = get_session_factory()()
    try:
        count = 0
        for property_id in _get_property_ids(db):
            try:
                detect_property_anomaly(db, property_id)
                count += 1
            except ValueError:
                db.rollback()
            except Exception as exc:
                db.rollback()
                print(f"[{datetime.now().isoformat()}] Anomaly update failed for {property_id}: {exc}")
        return count
    finally:
        db.close()


def run_batch_update():
    print(f"[{datetime.now().isoformat()}] Starting batch update")
    audited = _run_audit_batch()
    anomalies = _run_anomaly_batch()
    print(f"[{datetime.now().isoformat()}] Audited {audited} properties")
    print(f"[{datetime.now().isoformat()}] Updated anomalies for {anomalies} properties")


def main():
    ensure_database_schema()
    while True:
        try:
            run_batch_update()
        except Exception as exc:
            print(f"[{datetime.now().isoformat()}] Batch update failed: {exc}")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
