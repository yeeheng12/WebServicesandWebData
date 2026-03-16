from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.dependencies import get_db

router = APIRouter()


@router.post("/", response_model=schemas.ListingResponse, status_code=201)
def create_listing(listing: schemas.ListingCreate, db: Session = Depends(get_db)):
    db_location = crud.get_location(db=db, location_id=listing.location_id)
    if db_location is None:
        raise HTTPException(status_code=400, detail="Invalid location_id")
    return crud.create_listing(db=db, listing=listing)


@router.get("/", response_model=List[schemas.ListingResponse])
def read_listings(
    city: str = None,
    district: str = None,
    min_rent: float = None,
    max_rent: float = None,
    bedrooms: int = None,
    property_type: str = None,
    is_active: bool = None,
    sort_by: str = None,
    order: str = "asc",
    db: Session = Depends(get_db)
):
    return crud.get_listings(
        db=db,
        city=city,
        district=district,
        min_rent=min_rent,
        max_rent=max_rent,
        bedrooms=bedrooms,
        property_type=property_type,
        is_active=is_active,
        sort_by=sort_by,
        order=order
    )


@router.get("/{listing_id}", response_model=schemas.ListingResponse)
def read_listing(listing_id: int, db: Session = Depends(get_db)):
    db_listing = crud.get_listing(db=db, listing_id=listing_id)
    if db_listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return db_listing


@router.put("/{listing_id}", response_model=schemas.ListingResponse)
def update_listing(listing_id: int, listing: schemas.ListingCreate, db: Session = Depends(get_db)):
    db_location = crud.get_location(db=db, location_id=listing.location_id)
    if db_location is None:
        raise HTTPException(status_code=400, detail="Invalid location_id")

    db_listing = crud.update_listing(db=db, listing_id=listing_id, listing=listing)
    if db_listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return db_listing


@router.delete("/{listing_id}", response_model=schemas.ListingResponse)
def delete_listing(listing_id: int, db: Session = Depends(get_db)):
    db_listing = crud.delete_listing(db=db, listing_id=listing_id)
    if db_listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return db_listing