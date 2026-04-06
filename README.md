# Real Estate Search and Audit Platform

## 1. Executive Summary

### Problem Statement
Real estate analysis is often split across manual spreadsheets and disconnected data tools, making it slow to compare listings and evaluate investment quality.

### The Solution
This project provides a simple API + frontend workflow to:
- search properties by city and price range,
- audit a property's gross yield from listing price,
- expose the results through a minimal React UI.

### Target Persona
- Internal analysts and agents
- Product and data teams prototyping property intelligence features

### Value Proposition
- Faster decision support for property filtering and basic ROI checks
- Clear separation between development notebooks and production API
- Practical end-to-end reference architecture (DB -> FastAPI -> React)

---

## 2. Product Vision and User Experience

### User Stories
- As an agent, I want to search properties by city and budget so I can shortlist candidates quickly.
- As an analyst, I want to audit one property by ID so I can estimate yield before deeper review.
- As a developer, I want simple endpoints and predictable payloads so the frontend can render results reliably.

### Core MVP Features
- Property search endpoint (`/api/search`)
- Property audit endpoint (`/api/audit`)
- Health endpoint (`/health`)
- React frontend with search form and audit form
- Docker Compose setup for backend and frontend services

---

## 3. System Architecture and Technical Stack

### Stack
- Backend: FastAPI + SQLAlchemy
- Frontend: React (Vite)
- Database: PostgreSQL-compatible URL (Neon in current env file)
- Runtime: Docker Compose

### Why this stack
- FastAPI provides clear request models and fast API iteration
- SQLAlchemy keeps DB access explicit and portable
- React/Vite gives a lightweight local UI for endpoint consumption
- Docker Compose standardizes local run and reduces machine drift

### High-level Flow
1. Frontend sends request to backend API.
2. API validates payload and calls service layer.
3. Service layer queries database via SQLAlchemy session.
4. API returns JSON response consumed by frontend.

### Example Pipeline
User Input
   ↓
Search Service (filter properties)
   ↓
Audit Service (ROI + rule-based evaluation)
   ↓
Evaluation Layer (future ML scoring)
   ↓
FastAPI Response
   ↓
Frontend Display

### Service Responsibilites
1. Search Service
- Retrieves properties based on filters (city, price range)
- Returns candidate property list
- No financial evaluation

2. Audit Service
- Retrieves property and listing data for financial audit
- Uses listing price as the basis for financial estimation
- Calculates estimated rental income, maintenance costs, and gross yield percentage
- Applies rule-based checks to detect anomalies, such as low yield
- Returns computed audit metrics and anomaly indicators for downstream evaluation


### Repository Structure

```text
ML_Ops_Group_Repo/
├── .env
├── .gitignore
├── README.md
├── DataStructure.md
├── development/                         # Notebook-first experimentation (Batch dev and unit test)
│   ├── __init__.py
│   ├── database.py                      # database connection
│   ├── models.py                        # define data structure (LLM generated via prompt)
│   ├── dev_search/
│   │   ├── evaluation_search.py
│   │   └── search.py
│   └── dev_audit/
│       ├── __init__.py
│       ├── audit_api.py
│       ├── audit_dev.ipynb
│       ├── audit.ipynb
│       └── batch_update/                # batch update all the audit
│           ├── audit_update.py
│           └── validation.py
└── prod/                                # Production-style application (real-time application, UAT)
  ├── docker-compose.yml
  ├── README.md
  ├── test.ipynb
  ├── backend/
  │   ├── Dockerfile
  │   ├── requirements.txt
  │   ├── run.py
  │   └── app/
  │       ├── __init__.py
  │       ├── main.py
  │       ├── api/                     # FastAPI routes
  │       │   ├── __init__.py
  │       │   ├── audit.py
  │       │   └── search.py
  │       ├── core/                    # DB/session config
  │       │   ├── __init__.py
  │       │   ├── config.py
  │       │   └── database.py
  │       ├── models/                  # SQLAlchemy models (refer to DataStructure.md)
  │       │   ├── __init__.py
  │       │   └── models.py
  │       └── services/                # Business logic
  │           ├── __init__.py
  │           ├── audit.py
  │           └── search.py
  └── frontend/
    ├── Dockerfile
    ├── index.html
    ├── package.json
    └── src/
      ├── App.jsx
      └── main.jsx
```

---

## 4. Engineering Excellence and Operational Readiness

### Current Operational Constraints
- Search and audit depend entirely on a valid `DATABASE_URL`.
- No authentication/authorization layer yet.
- No migration framework yet (schema expected to exist in target DB).

### Production Readiness Checklist
- [ ] Add DB migration tooling (Alembic)
- [ ] Add API auth and role-based access
- [ ] Add structured logging and request tracing
- [ ] Add retry/backoff for transient DB/network errors
- [ ] Add CI pipeline for linting/tests/image build

### Scalability Strategy
- API: run multiple backend replicas behind a reverse proxy/load balancer.
- Database: use connection pooling, read replicas for heavy search traffic, and indexed query paths.
- Caching: introduce Redis for common search filters and short-lived audit responses.
- Workload split: move expensive audit/anomaly operations to background workers for non-blocking API latency.
- Frontend delivery: serve static assets through CDN and enable gzip/brotli compression.

### Fallback and Resilience Design
- Database unavailable:
   - Return a clear degraded-service response (HTTP 503) with retry guidance.
   - Keep health endpoint status explicit so orchestrators can restart unhealthy instances.
- External latency spikes:
   - Apply timeout limits and retry with exponential backoff for transient failures.
   - Use circuit breaker logic to avoid cascading failures.
- Partial service failure:
   - Keep search endpoint available even if audit/anomaly components are temporarily disabled.
   - Provide default "audit_pending" status when full audit cannot complete in SLA.
- Deployment rollback:
   - Maintain versioned Docker images and one-click rollback to previous stable release.

### CI/CD Pipeline (Target State)
1. Trigger on pull requests and merges to main.
2. Run lint + format checks for backend and frontend.
3. Run unit/integration API tests and smoke tests for key endpoints.
4. Build backend/frontend Docker images with immutable tags.
5. Scan dependencies and images for known vulnerabilities.
6. Push approved images to registry.
7. Deploy to staging and run post-deploy health checks.
8. Require manual approval for production deploy, then run smoke validation.
9. Auto-notify team channel on success/failure with links to logs and artifacts.

### Sanity Checks
- Backend health: `GET /health`
- Search API: `POST /api/search`
- Audit API: `POST /api/audit`
- Frontend load: open `http://localhost:3000`

### Observability to Add
- API latency (`/api/search`, `/api/audit`)
- Error rates by endpoint and status code
- Database connection failures/timeouts

### Near-term Roadmap
- Add anomaly endpoint and UI card
- Add input validation and stronger error messages
- Add pagination/sorting to search results

---

## 5. Domain Analysis and Limitations

### Functional Limits
- Audit uses fixed assumptions (`4.5%` rental income, `1%` maintenance)
- Search is filter-based only (no ranking/recommendation model)
- No multi-user state or saved portfolios

### Non-functional Considerations
- Security: currently open API with permissive CORS
- Scalability: no caching or async DB pattern yet
- Data quality: assumes core listing fields are complete and accurate

### Key Risk
**Risk:** backend and notebook may connect to different databases if environment variables differ.

**Mitigation:** keep one authoritative database URL for prod (`prod/.env_prod`) and verify with health + query smoke tests before demos.

---

## 6. Team and Collaboration

### Team Working Model
- Notebook-first development under `development/`
- API-first stabilization under `prod/backend/`
- UI integration under `prod/frontend/`

### Branching and Delivery
- Feature branches by function area (search/audit)
- Small, focused commits and endpoint-level validation
- Integration verified through Docker Compose and manual API checks

---

## Run Guide 

### Real-Time

#### Prerequisites
- Docker Desktop running
- `DATABASE_URL` available in `prod/.env_prod`

#### Start

```bash
cd prod
docker compose up --build
```

#### Access
- Frontend: `http://localhost:3000`
- Backend API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

---

#### API Examples

##### Search

```http
POST /api/search
Content-Type: application/json

{
  "city": "Paris",
  "price_min": 100000,
  "price_max": 900000,
  "limit": 5
}
```

##### Audit

```http
POST /api/audit
Content-Type: application/json

{
  "property_id": "11111111-1111-1111-1111-111111111111"
}
```
### Batch-Update (to be config)
Run py files under dev_audit/audit_update. 
   - audit_update.py would audit all the records(or selected records). 
   - validation.py would further validate the result.
Once the frequency and scope was decided, this can be applied in prod via docker.
