from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.dependencies import get_db

router = APIRouter()


@router.post("/", response_model=schemas.LocationResponse, status_code=201)
def create_location(location: schemas.LocationCreate, db: Session = Depends(get_db)):
    return crud.create_location(db=db, location=location)


@router.get("/", response_model=List[schemas.LocationResponse])
def read_locations(db: Session = Depends(get_db)):
    return crud.get_locations(db=db)


@router.get("/{location_id}", response_model=schemas.LocationResponse)
def read_location(location_id: int, db: Session = Depends(get_db)):
    db_location = crud.get_location(db=db, location_id=location_id)
    if db_location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return db_location


@router.put("/{location_id}", response_model=schemas.LocationResponse)
def update_location(location_id: int, location: schemas.LocationCreate, db: Session = Depends(get_db)):
    db_location = crud.update_location(db=db, location_id=location_id, location=location)
    if db_location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return db_location


@router.delete("/{location_id}", response_model=schemas.LocationResponse)
def delete_location(location_id: int, db: Session = Depends(get_db)):
    db_location = crud.delete_location(db=db, location_id=location_id)
    if db_location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return db_location