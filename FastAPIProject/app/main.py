from fastapi import FastAPI

from app.database import Base, engine
from app.routers import analytics, locations, properties
from app.routers import energy_certificates

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="House Sales and Energy Efficiency API",
    description=(
        "A RESTful API for querying UK house sale records enriched with "
        "energy efficiency and location data. "
        "Write operations on /properties and /energy-certificates "
        "require an API key via the X-API-Key header."
    ),
    version="2.1.0",
)


@app.get("/", summary="API root", description="Returns basic API metadata and available resource groups.")
def root():
    return {
        "message": "House Sales and Energy Efficiency API is running",
        "version": "2.1.0",
        "docs_url": "/docs",
        "resources": [
            "/properties",
            "/locations",
            "/analytics",
            "/energy-certificates",
        ],
        "security": {
            "write_endpoints_require_header": "X-API-Key",
            "protected_resources": [
                "/properties",
                "/energy-certificates",
            ],
        },
    }


app.include_router(properties.router)
app.include_router(locations.router)
app.include_router(analytics.router)
app.include_router(energy_certificates.router)