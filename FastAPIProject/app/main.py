from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import analytics, auth, energy_certificates, locations, properties


@asynccontextmanager
async def lifespan(app: FastAPI):
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


@app.get("/", summary="API root", description="Returns API metadata and discoverable resource groups.")
def root():
    return {
        "message": "House Sales and Energy Efficiency API is running",
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

app.include_router(auth.router)
app.include_router(properties.router)
app.include_router(locations.router)
app.include_router(energy_certificates.router)
app.include_router(analytics.router)
