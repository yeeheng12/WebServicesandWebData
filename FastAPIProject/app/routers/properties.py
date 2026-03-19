from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.dependencies import get_db
from app.security import require_api_key

router = APIRouter(prefix="/properties", tags=["Properties"])


@router.get(
    "/",
    response_model=schemas.PropertyListResponse,
    summary="List properties",
    description="Returns property records with filtering, sorting, and pagination.",
)
def read_properties(
    postcode: str = None,
    town_city: str = None,
    district: str = None,
    county: str = None,
    property_type: str = None,
    min_price: float = Query(default=None, gt=0),
    max_price: float = Query(default=None, gt=0),
    date_from: date = None,
    date_to: date = None,
    epc_rating: str = None,
    min_efficiency: float = None,
    max_efficiency: float = None,
    sort_by: str = "sale_date",
    order: str = "desc",
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=400, detail="min_price cannot be greater than max_price")
    if min_efficiency is not None and max_efficiency is not None and min_efficiency > max_efficiency:
        raise HTTPException(status_code=400, detail="min_efficiency cannot be greater than max_efficiency")
    if order not in {"asc", "desc"}:
        raise HTTPException(status_code=400, detail="order must be 'asc' or 'desc'")
    if sort_by not in {"price", "sale_date", "current_energy_efficiency", "total_floor_area"}:
        raise HTTPException(
            status_code=400,
            detail="sort_by must be one of: price, sale_date, current_energy_efficiency, total_floor_area",
        )

    items = crud.get_properties(
        db=db,
        postcode=postcode,
        town_city=town_city,
        district=district,
        county=county,
        property_type=property_type,
        min_price=min_price,
        max_price=max_price,
        date_from=date_from,
        date_to=date_to,
        epc_rating=epc_rating,
        min_efficiency=min_efficiency,
        max_efficiency=max_efficiency,
        sort_by=sort_by,
        order=order,
        skip=skip,
        limit=limit,
    )

    return {
        "items": items,
        "skip": skip,
        "limit": limit,
        "returned": len(items),
    }


@router.get(
    "/{property_id}",
    response_model=schemas.PropertyResponse,
    summary="Get property by ID",
    description="Returns a single property record by its internal database ID.",
)
def read_property(property_id: int, db: Session = Depends(get_db)):
    db_property = crud.get_property(db=db, property_id=property_id)
    if db_property is None:
        raise HTTPException(status_code=404, detail="Property not found")
    return db_property


@router.post(
    "/",
    response_model=schemas.PropertyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create property",
    description="Creates a new property record in the database.",
)
def create_property(
    property_data: schemas.PropertyCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
):
    return crud.create_property(db=db, property_data=property_data)

@router.put(
    "/{property_id}",
    response_model=schemas.PropertyResponse,
    summary="Update property",
    description="Updates an existing property record by ID.",
)
def update_property(
    property_id: int,
    property_data: schemas.PropertyUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
):
    updated_property = crud.update_property(db=db, property_id=property_id, property_data=property_data)
    if updated_property is None:
        raise HTTPException(status_code=404, detail="Property not found")
    return updated_property


@router.delete(
    "/{property_id}",
    response_model=schemas.PropertyResponse,
    summary="Delete property",
    description="Deletes a property record by ID.",
)
def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
):
    deleted_property = crud.delete_property(db=db, property_id=property_id)
    if deleted_property is None:
        raise HTTPException(status_code=404, detail="Property not found")
    return deleted_property