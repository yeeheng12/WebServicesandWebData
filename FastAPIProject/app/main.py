from fastapi import FastAPI

from app.database import engine, Base
from app import models
from app.routers import locations, listings, analytics

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Housing Rental Insights API")


@app.get("/")
def read_root():
    return {"message": "Housing Rental API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(locations.router, prefix="/locations", tags=["Locations"])
app.include_router(listings.router, prefix="/listings", tags=["Listings"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])