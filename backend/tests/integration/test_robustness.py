import os
import shutil
import subprocess
import time

import pytest

RUN_DOCKER_CONTROL_TESTS = os.getenv("RUN_DOCKER_CONTROL_TESTS") == "1"


def test_search_rejects_invalid_limit(api_get):
    status, data = api_get("/api/search?city=Paris&limit=bad")

    assert status == 422
    assert "detail" in data


def test_audit_returns_404_for_missing_property(api_get, missing_property_id):
    status, data = api_get(f"/api/audit/{missing_property_id}")

    assert status == 404
    assert data["detail"] == "Property not found"


def test_anomaly_returns_404_for_missing_property(api_get, missing_property_id):
    status, data = api_get(f"/api/anomaly/{missing_property_id}")

    assert status == 404
    assert data["detail"] == "Property not found"


@pytest.mark.skipif(
    not RUN_DOCKER_CONTROL_TESTS or shutil.which("docker") is None,
    reason="Set RUN_DOCKER_CONTROL_TESTS=1 with Docker available to run restart test",
)
def test_backend_recovers_after_restart(api_get, repo_dir, wait_for_health):
    subprocess.run(
        ["docker", "compose", "-f", "backend/tests/integration/docker-compose.yml", "restart", "backend"],
        cwd=repo_dir,
        check=True,
        timeout=120,
    )

    wait_for_health()
    status, data = api_get("/health")

    assert status == 200
    assert data == {"status": "ok"}


@pytest.mark.skipif(
    not RUN_DOCKER_CONTROL_TESTS or shutil.which("docker") is None,
    reason="Set RUN_DOCKER_CONTROL_TESTS=1 with Docker available to run batch/search test",
)
def test_search_still_works_while_batch_runs(api_get, repo_dir):
    subprocess.run(
        ["docker", "compose", "-f", "backend/tests/integration/docker-compose.yml", "--profile", "batch", "up", "-d", "batch"],
        cwd=repo_dir,
        check=True,
        timeout=120,
    )

    try:
        time.sleep(2)
        for _ in range(3):
            status, data = api_get("/api/search?city=Paris&limit=2")
            assert status == 200
            assert data["count"] == 2
    finally:
        subprocess.run(
            ["docker", "compose", "-f", "backend/tests/integration/docker-compose.yml", "stop", "batch"],
            cwd=repo_dir,
            check=False,
            timeout=120,
        )
