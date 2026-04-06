# Real Estate Search, Audit and Anomaly Platform

## Problem Statement
Real-estate acquisition teams do not struggle to find listings; they struggle to evaluate them fast and consistently. A large share of analyst time is spent on repetitive screening: checking whether a property is financially interesting, whether the input data is reliable, and whether the asking price looks plausible relative to the local market.

This project addresses that problem as a production-style data application on top of structured property records. It combines low-latency search, persisted audit outputs, anomaly detection, scheduled refresh logic, and Docker-based deployment so that a user can move from raw listings to explainable investment signals without recomputing everything on every request.

## Project Goal
The target customer is a real-estate investment or advisory team that needs a first-pass decision layer before human review. The system is designed to answer three practical questions:

- Which properties match the current search?
- What is the estimated rental yield of a given property?
- Does this property look risky, incomplete, or mispriced?

## What the Platform Does
- `Search`: returns properties filtered by city and price, with the full record needed for downstream review.
- `Audit`: returns a saved audit with estimated rental income, estimated maintenance costs, and gross yield.
- `Anomaly detection`: returns saved red flags such as low yield, missing basic information, or strong deviation from peer price-per-square-meter levels.
- `Batch refresh`: recomputes all audits first, then anomalies, every 6 hours.

In practice, this creates a simple analyst workflow: search the market, inspect a property, retrieve its saved audit, then check whether the system has already identified a red flag.

## Why the Architecture Makes Sense
The main design choice is to separate what must be online from what should be precomputed.

- `Search` is request-time because it is directly user-driven and cheap to evaluate as a database query.
- `Audit` and `anomaly` outputs are stored and refreshed in batch because they are deterministic functions of existing data. Persisting them keeps the API fast, avoids unnecessary recomputation, and gives users a stable view of the latest approved calculations.
- The batch order is deliberate: anomaly detection depends partly on the audit output, so audits are refreshed first and anomalies second.
- The API surface remains simple: `GET` endpoints expose current system state, while the batch worker is responsible for keeping that state fresh.

This is a small project, but the pattern is the same one used in larger data systems: online serving for interactive retrieval, offline refresh for heavier feature generation.

## Core Analytical Logic
The project stays intentionally simple and explainable.

- Audit metrics are estimated from structured property fields such as city, property type, bedrooms, bathrooms, square meters, year built, and asking price.
- Anomaly detection combines three checks:
  - financial risk: low yield,
  - data quality risk: missing or invalid core attributes,
  - market pricing risk: suspiciously cheap or overpriced properties based on price per square meter versus similar properties in the same zip code.

The goal is not to claim a perfect valuation model. The goal is to provide a clear, reproducible screening layer that helps a team focus attention on the right records first.

## Main Innovations
- A clean split between interactive search and scheduled analytical refresh.
- Explainable heuristics instead of opaque scoring: each anomaly is attached to a concrete reason.
- A batch pipeline that mirrors production logic: audit generation first, anomaly generation second.
- A testing setup that goes beyond unit tests and includes Docker-backed integration checks plus simple latency and load measurements.

## Technical Architecture
- **Backend**: FastAPI + SQLAlchemy
- **Frontend**: React (Vite)
- **Database**: PostgreSQL via `DATABASE_URL`
- **Orchestration**: Docker Compose
- **Dependency management**: Poetry
- **Batch processing**: dedicated batch container running `python -m app.batch.batch_update`
- **Testing**:
  - mocked unit tests,
  - Docker integration tests with seeded Postgres data,
  - benchmark scripts for latency and throughput

The deployed services are:
- `backend`: serves the API
- `frontend`: user interface
- `batch`: refreshes audits and anomalies on schedule

## Validation Strategy
The system is validated at three levels.

- **Unit tests** verify service logic in isolation.
- **Integration tests** run the backend against a dedicated Dockerized Postgres instance seeded with known data.
- **Benchmark scripts** measure response latency and simple throughput under concurrent search load.

This matters because the project is not only about writing feature code. It is also about showing that the system can be run, queried, and evaluated as an actual application.

## Main API Endpoints
- `GET /api/search`
- `GET /api/audit/{property_id}`
- `GET /api/anomaly/{property_id}`
- `GET /health`

## Quick Start
Run the main application:

```bash
docker compose up --build
```

Then open:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

Run validation:

```bash
poetry run python -m pytest backend/tests/unit -q
docker compose -f backend/tests/integration/docker-compose.yml up -d --build
poetry run python -m pytest backend/tests/integration -q
poetry run python backend/tests/benchmarks/latency_check.py
poetry run python backend/tests/benchmarks/load_check.py
docker compose -f backend/tests/integration/docker-compose.yml down -v
```

## Outcome
The result is a compact but coherent decision-support pipeline for real-estate screening: one interface for retrieval, one persisted layer for financial and anomaly signals, one batch process to keep those signals fresh, and one testing stack that shows the system works beyond notebooks or static scripts.
