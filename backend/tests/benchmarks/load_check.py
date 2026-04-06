import os
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

API_BASE_URL = os.getenv("TEST_API_BASE_URL", "http://localhost:8001")
DURATION_SECONDS = int(os.getenv("LOAD_DURATION_SECONDS", "30"))
CONCURRENCY_LEVELS = [1, 5, 10, 20]
SEARCH_PATH = "/api/search?city=Paris&limit=2"


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


def worker(deadline):
    total = 0
    success = 0
    failure = 0
    total_latency = 0
    while time.time() < deadline:
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(f"{API_BASE_URL}{SEARCH_PATH}", timeout=10) as response:
                response.read()
                if response.status == 200:
                    success += 1
                else:
                    failure += 1
        
        except Exception:
            failure += 1
        total += 1
        total_latency += time.perf_counter() - started
    
    return total, success, failure, total_latency


def run_level(concurrency):
    deadline = time.time() + DURATION_SECONDS
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        results = list(pool.map(worker, [deadline] * concurrency))

    total = sum(item[0] for item in results)
    success = sum(item[1] for item in results)
    failure = sum(item[2] for item in results)
    total_latency = sum(item[3] for item in results)
    requests_per_second = total / DURATION_SECONDS
    average_latency_ms = (total_latency / total) * 1000 if total else 0

    print(
        f"concurrency={concurrency}: total={total}, success={success}, failure={failure}, "
        f"requests_per_second={requests_per_second:.2f}, average_latency={average_latency_ms:.2f} ms"
    )



def main():
    wait_for_health()
    print(f"Load check against {API_BASE_URL} for {DURATION_SECONDS} seconds per level")
    for concurrency in CONCURRENCY_LEVELS:
        run_level(concurrency)


if __name__ == "__main__":
    main()
