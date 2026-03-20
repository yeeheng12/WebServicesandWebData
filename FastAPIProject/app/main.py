import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.database import engine
from app.models import Base
from app.routers import analytics, auth, energy_certificates, locations, properties

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="House Sales and Energy Efficiency API",
    description=(
        "A RESTful API for querying UK house sale records enriched with "
        "energy efficiency and location data. "
        "Write operations require bearer-token authentication with role-based authorization."
    ),
    version="3.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "Authentication", "description": "User registration, login, and current-user endpoints"},
        {"name": "Properties", "description": "Property record CRUD and related links"},
        {"name": "Energy Certificates", "description": "Energy certificate CRUD for existing properties"},
        {"name": "Locations", "description": "Location summaries and related resource discovery"},
        {"name": "Analytics", "description": "Aggregated property and EPC analytics"},
    ],
)

allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.get(
    "/info",
    tags=["Info"],
    summary="API information",
    description="Returns API metadata, available resources, and security model."
)
def api_info():
    return {
        "message": "House Sales and Energy Efficiency API",
        "version": "3.0.0",
        "docs_url": "/docs",
        "resources": {
            "properties": "/properties",
            "locations": "/locations",
            "analytics": "/analytics",
            "energy_certificates": "/energy-certificates",
        },
        "security": {
            "scheme": "Bearer JWT",
            "login": "/auth/login",
            "roles": {
                "viewer": ["GET"],
                "editor": ["POST", "PATCH"],
                "admin": ["DELETE"],
            },
        },
    }

@app.get("/health", tags=["Health"], summary="Health check")
def health_check():
    return {
        "status": "ok",
        "service": "House Sales and Energy Efficiency API",
        "version": "3.0.0",
    }

app.include_router(auth.router)
app.include_router(properties.router)
app.include_router(locations.router)
app.include_router(energy_certificates.router)
app.include_router(analytics.router)