import os
import statistics
import time
import urllib.request

API_BASE_URL = os.getenv("TEST_API_BASE_URL", "http://localhost:8001")
REQUEST_COUNT = int(os.getenv("LATENCY_REQUESTS", "30"))
PROPERTY_ID = "11111111-1111-1111-1111-111111111111"
ENDPOINTS = {
    "search": "/api/search?city=Paris&limit=2",
    "audit": f"/api/audit/{PROPERTY_ID}",
    "anomaly": f"/api/anomaly/{PROPERTY_ID}",
}


def wait_for_health():
    deadline = time.time() + 60
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{API_BASE_URL}/health", timeout=5) as response:
                if response.status == 200:
                    return
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError(f"Backend did not become healthy at {API_BASE_URL}")


def percentile(values, value):
    ordered = sorted(values)
    index = int((len(ordered) - 1) * value)
    return ordered[index]


def measure(path):
    timings = []
    for _ in range(REQUEST_COUNT):
        started = time.perf_counter()
        with urllib.request.urlopen(f"{API_BASE_URL}{path}", timeout=10) as response:
            if response.status != 200:
                raise RuntimeError(f"Request failed for {path} with status {response.status}")
            response.read()
        timings.append((time.perf_counter() - started) * 1000)
    return timings


def print_stats(name, timings):
    print(name)
    print("min =", round(min(timings), 2), "ms")
    print("avg =", round(statistics.mean(timings), 2), "ms")
    print("p50 =", round(percentile(timings, 0.5), 2), "ms")
    print("p95 =", round(percentile(timings, 0.95), 2), "ms")
    print("max =", round(max(timings), 2), "ms")



def main():
    wait_for_health()
    print(f"Latency check against {API_BASE_URL} with {REQUEST_COUNT} requests per endpoint")
    for name, path in ENDPOINTS.items():
        timings = measure(path)
        print_stats(name, timings)


if __name__ == "__main__":
    main()
