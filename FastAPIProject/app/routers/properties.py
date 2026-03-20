from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.dependencies import get_db
from app.security import require_admin, require_editor

router = APIRouter(prefix="/properties", tags=["Properties"])


@router.get(
    "/",
    response_model=schemas.PropertyListResponse,
    summary="List properties",
    description="Returns property records with filtering, sorting, and pagination.",
    responses={
        400: {
            "description": "Invalid query parameters",
            "content": {
                "application/json": {
                    "examples": {
                        "bad_price_range": {
                            "summary": "min_price greater than max_price",
                            "value": {"detail": "min_price cannot be greater than max_price"},
                        },
                        "bad_date_range": {
                            "summary": "date_from later than date_to",
                            "value": {"detail": "date_from cannot be later than date_to"},
                        },
                        "bad_epc_rating": {
                            "summary": "Invalid EPC rating",
                            "value": {"detail": "epc_rating must be one of: A, B, C, D, E, F, G"},
                        },
                        "bad_sort_field": {
                            "summary": "Invalid sort field",
                            "value": {
                                "detail": "sort_by must be one of: price, sale_date, current_energy_efficiency, total_floor_area"
                            },
                        },
                    }
                }
            },
        }
    },
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
    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from cannot be later than date_to")
    if epc_rating is not None:
        epc_rating = epc_rating.upper()
        if epc_rating not in {"A", "B", "C", "D", "E", "F", "G"}:
            raise HTTPException(status_code=400, detail="epc_rating must be one of: A, B, C, D, E, F, G")
    if order not in {"asc", "desc"}:
        raise HTTPException(status_code=400, detail="order must be 'asc' or 'desc'")
    if sort_by not in {"price", "sale_date", "current_energy_efficiency", "total_floor_area"}:
        raise HTTPException(
            status_code=400,
            detail="sort_by must be one of: price, sale_date, current_energy_efficiency, total_floor_area",
        )

    items, total = crud.get_properties(
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
        "pagination": crud.build_pagination_meta(
            skip=skip,
            limit=limit,
            returned=len(items),
            total=total,
        ),
    }


@router.get(
    "/{property_id}",
    response_model=schemas.PropertyDetailResponse,
    summary="Get property by ID",
    description="Returns a single property record by its internal database ID.",
    responses={
        200: {
            "description": "Property found",
            "content": {
                "application/json": {
                    "example": {
                        "id": 123,
                        "price": 285000.0,
                        "sale_date": "2023-06-15",
                        "postcode": "LS6 2AB",
                        "property_type": "T",
                        "town_city": "Leeds",
                        "district": "Leeds",
                        "county": "West Yorkshire",
                        "current_energy_rating": "C",
                        "current_energy_efficiency": 72.0,
                        "_links": {
                            "self": "/properties/123",
                            "related_area_properties": "/properties/?town_city=Leeds",
                            "price_trend": "/analytics/price-trend?area_type=town_city&area=Leeds",
                            "energy_price_impact": "/analytics/energy-price-impact?area_type=town_city&area=Leeds",
                            "energy_certificates": "/properties/123/energy-certificates"
                        }
                    }
                }
            }
        },
        404: {
            "description": "Property not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Property not found"
                    }
                }
            }
        }
    },
)
def read_property(property_id: int, db: Session = Depends(get_db)):
    db_property = crud.get_property(db=db, property_id=property_id)
    if db_property is None:
        raise HTTPException(status_code=404, detail="Property not found")

    area_query = f"/properties/?town_city={db_property.town_city}" if db_property.town_city else None
    trend_query = (
        f"/analytics/price-trend?area_type=town_city&area={db_property.town_city}"
        if db_property.town_city else None
    )
    energy_query = (
        f"/analytics/energy-price-impact?area_type=town_city&area={db_property.town_city}"
        if db_property.town_city else None
    )

    payload = schemas.PropertyResponse.model_validate(db_property).model_dump()
    payload["_links"] = {
        "self": f"/properties/{property_id}",
        "related_area_properties": area_query,
        "price_trend": trend_query,
        "energy_price_impact": energy_query,
        "energy_certificates": f"/properties/{property_id}/energy-certificates",
    }
    return payload


@router.post(
    "/",
    response_model=schemas.PropertyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create property",
    description="Creates a new property record in the database.",
    responses={
        201: {
            "description": "Property created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 999,
                        "price": 250000.0,
                        "sale_date": "2024-01-10",
                        "postcode": "LS1 4EF",
                        "property_type": "F",
                        "town_city": "Leeds",
                        "district": "Leeds",
                        "county": "West Yorkshire"
                    }
                }
            }
        },
        401: {
            "description": "Missing or invalid bearer token",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            },
        },
        403: {
            "description": "Forbidden or insufficient permissions",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_key": {
                            "value": {"detail": "Could not validate credentials"}
                        },
                        "insufficient_permissions": {
                            "value": {
                                "detail": "Insufficient permissions: editor or admin role required"
                            }
                        },
                    }
                }
            },
        },
        409: {
            "description": "Duplicate transaction_id",
            "content": {
                "application/json": {
                    "example": {"detail": "transaction_id already exists"}
                }
            },
        },
    }
)
def create_property(
    property_data: schemas.PropertyCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_editor),
):
    property_obj, error = crud.create_property(
        db=db,
        property_data=property_data,
        created_by_user_id=current_user.id,
    )
    if error == "duplicate_transaction_id":
        raise HTTPException(status_code=409, detail="transaction_id already exists")

    return property_obj

@router.patch(
    "/{property_id}",
    response_model=schemas.PropertyResponse,
    summary="Partially update property",
    description="Partially updates an existing property record by ID.",
    responses={
        401: {
            "description": "Missing or invalid bearer token",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            },
        },
        403: {
            "description": "Forbidden or insufficient permissions",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_key": {
                            "value": {"detail": "Could not validate credentials"}
                        },
                        "insufficient_permissions": {
                            "value": {
                                "detail": "Insufficient permissions: editor or admin role required"
                            }
                        },
                    }
                }
            },
        },
        404: {
            "description": "Property not found",
            "content": {"application/json": {"example": {"detail": "Property not found"}}},
        },
        409: {
            "description": "Duplicate transaction_id",
            "content": {"application/json": {"example": {"detail": "transaction_id already exists"}}},
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "price"],
                                "msg": "Input should be a valid number",
                                "type": "float_parsing"
                            }
                        ]
                    }
                }
            },
        },
    },
)
def update_property(
    property_id: int,
    property_data: schemas.PropertyUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_editor),
):
    updated_property, error = crud.update_property(
        db=db,
        property_id=property_id,
        property_data=property_data,
        updated_by_user_id=current_user.id,
    )

    if error == "not_found":
        raise HTTPException(status_code=404, detail="Property not found")

    if error == "duplicate_transaction_id":
        raise HTTPException(status_code=409, detail="transaction_id already exists")

    return updated_property


@router.delete(
    "/{property_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete property",
    description="Deletes a property record by ID.",
    responses={
        204: {"description": "Property deleted successfully"},
        401: {
            "description": "Missing or invalid bearer token",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            },
        },
        403: {
            "description": "Forbidden or insufficient permissions",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_key": {
                            "value": {"detail": "Could not validate credentials"}
                        },
                        "insufficient_permissions": {
                            "value": {
                                "detail": "Insufficient permissions: admin role required"
                            }
                        },
                    }
                }
            },
        },
        404: {
            "description": "Property not found",
            "content": {"application/json": {"example": {"detail": "Property not found"}}},
        },
    },
)
def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    _ = Depends(require_admin),
):
    deleted_property = crud.delete_property(db=db, property_id=property_id)
    if deleted_property is None:
        raise HTTPException(status_code=404, detail="Property not found")
    return None

@router.get(
    "/{property_id}/energy-certificates",
    response_model=schemas.EnergyCertificateListResponse,
    summary="List energy certificates for a property",
    description="Returns energy certificates linked to a specific property with pagination.",
)
def read_property_energy_certificates(
    property_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    certificates, total, error = crud.get_property_energy_certificates(
        db=db,
        property_id=property_id,
        skip=skip,
        limit=limit,
    )

    if error == "property_not_found":
        raise HTTPException(status_code=404, detail="Property not found")

    return {
        "items": certificates,
        "pagination": crud.build_pagination_meta(
            skip=skip,
            limit=limit,
            returned=len(certificates),
            total=total,
        ),
    }