# Operations Runbook

This document is for engineers operating the platform in test, staging, or production-like environments.

Related reference:

- [DataStructure.md](DataStructure.md)

## 1. Scope

Use this runbook before:

- promoting a new version,
- updating running services,
- validating system health after deployment.

## 2. Required Preconditions

Before any release or update, confirm all items below:

- Docker is installed and running.
- Python and Poetry are available.
- A valid DATABASE_URL is configured.
- You know the target environment and rollback target.

## 3. Standard Bring-Up

From repository root:

```bash
docker compose up --build
```

Expected services/endpoints:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## 4. Mandatory Pre-Production Gate

Run this sequence before any promotion.

1. Unit tests

```bash
poetry run python -m pytest backend/tests/unit -q
```

2. Start integration stack

```bash
docker compose -f backend/tests/integration/docker-compose.yml up -d --build
```

3. Integration tests

```bash
poetry run python -m pytest backend/tests/integration -q
```

4. Latency sanity benchmark

```bash
poetry run python backend/tests/benchmarks/latency_check.py
```

5. Load sanity benchmark

```bash
poetry run python backend/tests/benchmarks/load_check.py
```

6. Stop integration stack

```bash
docker compose -f backend/tests/integration/docker-compose.yml down -v
```

Release decision rule:

- Do not promote if any step fails.

## 5. Sanity Checks After Deployment

Run quick endpoint checks:

```bash
curl "http://localhost:8000/health"
curl "http://localhost:8000/api/search?city=Paris&limit=2"
curl "http://localhost:8000/api/audit/11111111-1111-1111-1111-111111111111"
curl "http://localhost:8000/api/anomaly/11111111-1111-1111-1111-111111111111"
```

Expected behavior:

- health returns status ok,
- search returns count and id fields,
- audit endpoint returns a persisted audit payload,
- anomaly endpoint returns anomaly payload with comparables information.

## 6. Automated Behavior Checks (Model-Like Sanity)

This system is rule-based, but these checks serve as model sanity gates.

Checks already implemented in backend/tests:

- known seeded property returns expected audit/anomaly values,
- missing property id returns 404,
- invalid query parameter type returns 422,
- optional robustness checks validate restart and batch coexistence.

Run core behavior checks:

```bash
poetry run python -m pytest backend/tests/integration -q
```

Run optional Docker control robustness checks:

PowerShell:

```powershell
$env:RUN_DOCKER_CONTROL_TESTS = "1"
poetry run python -m pytest backend/tests/integration/test_robustness.py -q
```

Bash:

```bash
RUN_DOCKER_CONTROL_TESTS=1 poetry run python -m pytest backend/tests/integration/test_robustness.py -q
```

Interpretation:

- If seeded-output tests fail, block release.
- If robustness tests fail repeatedly, investigate deployment stability before promotion.

## 7. Updating the System Safely

When applying an update:

1. Pull and verify target branch/tag.
2. Rebuild and restart with docker compose up --build.
3. Run post-deploy sanity checks.
4. Monitor backend and batch logs.

Useful log commands:

```bash
docker compose logs backend --tail=200
docker compose logs batch --tail=200
```

## 8. Batch-Specific Operational Checks

Confirm all below:

- batch service is up,
- batch logs show cycle start and completion counts,
- no recurring exception pattern,
- search endpoint remains healthy while batch runs.

## 9. Rollback Procedure

If release quality is not acceptable:

1. Stop current stack.
2. Redeploy last known-good version.
3. Re-run post-deploy sanity checks.
4. Record failed checks and remediation actions.

## 10. Operator Sign-Off Checklist

Before handoff or approval:

- pre-production gate passed,
- endpoint sanity checks passed,
- batch behavior verified,
- rollback path identified and validated.