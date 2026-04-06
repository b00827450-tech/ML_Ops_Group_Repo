"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import anomaly_routes, audit_routes, search_routes
from .core.database import ensure_database_schema

app = FastAPI(title="Real Estate API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(search_routes.router)
app.include_router(audit_routes.router)
app.include_router(anomaly_routes.router)


@app.on_event("startup")
def startup():
    ensure_database_schema()


@app.get("/health")
def health():
    return {"status": "ok"}
