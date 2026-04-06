import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

API_BASE_URL = os.getenv("TEST_API_BASE_URL", "http://localhost:8001")
VALID_PROPERTY_ID = "11111111-1111-1111-1111-111111111111"
MISSING_PROPERTY_ID = "99999999-9999-9999-9999-999999999999"


def _read_json(response):
    body = response.read().decode("utf-8")
    return json.loads(body) if body else {}


def _api_get(path):
    request = urllib.request.Request(f"{API_BASE_URL}{path}")
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, _read_json(response)
    except urllib.error.HTTPError as exc:
        return exc.code, _read_json(exc)


def _wait_for_health():
    deadline = time.time() + 60
    last_error = None
    while time.time() < deadline:
        try:
            status, data = _api_get("/health")
            if status == 200 and data.get("status") == "ok":
                return
        except Exception as exc:
            last_error = exc
        time.sleep(1)
    raise RuntimeError(f"Backend did not become healthy at {API_BASE_URL}") from last_error


@pytest.fixture(scope="session", autouse=True)
def wait_for_backend():
    _wait_for_health()


@pytest.fixture
def api_get():
    return _api_get


@pytest.fixture
def wait_for_health():
    return _wait_for_health


@pytest.fixture
def valid_property_id():
    return VALID_PROPERTY_ID


@pytest.fixture
def missing_property_id():
    return MISSING_PROPERTY_ID


@pytest.fixture
def repo_dir():
    return Path(__file__).resolve().parents[3]
