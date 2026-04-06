# App Setup

Simple split setup:
- `backend`: FastAPI API
- `frontend`: React (Vite)
- `DATABASE_URL`: external database used by the backend

## Run

```bash
docker-compose up --build
```

## URLs

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

## API

### `GET /api/search`

Example:

```text
/api/search?city=Paris&price_min=100000&price_max=800000&limit=10
```

### `GET /api/audit/{property_id}`

Example:

```text
/api/audit/11111111-1111-1111-1111-111111111111
```

The audit now estimates:
- `estimated_rental_income`
- `estimated_maintenance_costs`
- `gross_yield_percentage`

These values are derived heuristically from property attributes such as city, zip code, property type, size, room count, and year built.

### `GET /api/anomaly/{property_id}`

Example:

```text
/api/anomaly/11111111-1111-1111-1111-111111111111
```

Anomaly detection now checks:
- low yield when an audit exists
- missing or invalid basic property info
- suspiciously cheap or wildly overpriced price-per-square-meter versus similar homes in the same zip code

### `GET /health`
Returns API health.
