# Prod Setup

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

### `POST /api/search`
Body:

```json
{
  "city": "Paris",
  "price_min": 100000,
  "price_max": 800000,
  "limit": 10
}
```

### `POST /api/audit`
Body:

```json
{
  "property_id": "11111111-1111-1111-1111-111111111111"
}
```

### `GET /health`
Returns API health.
