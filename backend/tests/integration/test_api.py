def test_health_endpoint(api_get):
    status, data = api_get("/health")

    assert status == 200
    assert data == {"status": "ok"}


def test_search_returns_results_with_ids(api_get):
    status, data = api_get("/api/search?city=Paris&limit=2")

    assert status == 200
    assert data["count"] == 2
    assert len(data["results"]) == 2
    assert all(item["city"] == "Paris" for item in data["results"])
    assert all(item["id"] for item in data["results"])


def test_get_saved_audit_returns_seeded_data(api_get, valid_property_id):
    status, data = api_get(f"/api/audit/{valid_property_id}")

    assert status == 200
    assert data["property_id"] == valid_property_id
    assert data["address"] == "12 Rue de Rivoli"
    assert data["action"] == "existing"
    assert data["yield"] == 3.46


def test_get_saved_anomaly_returns_seeded_data(api_get, valid_property_id):
    status, data = api_get(f"/api/anomaly/{valid_property_id}")

    assert status == 200
    assert data["property_id"] == valid_property_id
    assert data["address"] == "12 Rue de Rivoli"
    assert data["action"] == "existing"
    assert data["red_flag"] is True
    assert data["comparables_analyzed"] == 2
    assert {item["flag_type"] for item in data["anomalies"]} == {
        "Low Yield",
        "Suspiciously Cheap",
    }
