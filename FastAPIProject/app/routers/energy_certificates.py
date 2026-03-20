from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.dependencies import get_db
from app.security import require_admin, require_editor

router = APIRouter(prefix="/energy-certificates", tags=["Energy Certificates"])


@router.get(
    "/",
    response_model=schemas.EnergyCertificateListResponse,
    summary="List energy certificates",
    description="Returns energy certificate records with optional filtering by property ID and pagination."
)
def read_energy_certificates(
    property_id: Optional[int] = Query(default=None, ge=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    items, total = crud.get_energy_certificates(
        db=db,
        property_id=property_id,
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
    "/{certificate_id}",
    response_model=schemas.EnergyCertificateResponse,
    summary="Get energy certificate by ID",
    description="Returns a single energy certificate record by its internal database ID.",
)
def read_energy_certificate(certificate_id: int, db: Session = Depends(get_db)):
    certificate = crud.get_energy_certificate(db=db, certificate_id=certificate_id)
    if certificate is None:
        raise HTTPException(status_code=404, detail="Energy certificate not found")
    return certificate


@router.post(
    "/",
    response_model=schemas.EnergyCertificateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create energy certificate",
    description="Creates a new energy certificate linked to an existing property.",
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
        404: {"description": "Property not found"},
        409: {
            "description": "Duplicate lmk_key",
            "content": {
                "application/json": {
                    "example": {"detail": "lmk_key already exists"}
                }
            },
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "current_energy_rating"],
                                "msg": "Value error, energy rating must be one of: A, B, C, D, E, F, G",
                                "type": "value_error"
                            }
                        ]
                    }
                }
            },
        },
    },
)
def create_energy_certificate(
    certificate_data: schemas.EnergyCertificateCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_editor),
):
    certificate, error = crud.create_energy_certificate(db=db, certificate_data=certificate_data, created_by_user_id=current_user.id,)
    if error == "duplicate_lmk_key":
        raise HTTPException(status_code=409, detail="lmk_key already exists")
    if error == "property_not_found":
        raise HTTPException(status_code=404, detail="Property not found")
    return certificate


@router.patch(
    "/{certificate_id}",
    response_model=schemas.EnergyCertificateResponse,
    summary="Partially update energy certificate",
    description="Partially updates an existing energy certificate record.",
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
        404: {"description": "Energy certificate or property not found"},
        409: {
            "description": "Duplicate lmk_key",
            "content": {
                "application/json": {
                    "example": {"detail": "lmk_key already exists"}
                }
            },
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "current_energy_efficiency"],
                                "msg": "Value error, energy efficiency must be between 0 and 100",
                                "type": "value_error"
                            }
                        ]
                    }
                }
            },
        },
    },
)
def update_energy_certificate(
    certificate_id: int,
    certificate_data: schemas.EnergyCertificateUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_editor),
):
    certificate, error = crud.update_energy_certificate(
        db=db,
        certificate_id=certificate_id,
        certificate_data=certificate_data,
        updated_by_user_id=current_user.id,
    )

    if error == "certificate_not_found":
        raise HTTPException(status_code=404, detail="Energy certificate not found")
    if error == "property_not_found":
        raise HTTPException(status_code=404, detail="Property not found")
    if error == "duplicate_lmk_key":
        raise HTTPException(status_code=409, detail="lmk_key already exists")

    return certificate


@router.delete(
    "/{certificate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete energy certificate",
    description="Deletes an energy certificate record by ID.",
    responses={
        204: {"description": "Energy certificate deleted successfully"},
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
        404: {"description": "Energy certificate not found"},
    },
)
def delete_energy_certificate(
    certificate_id: int,
    db: Session = Depends(get_db),
    _ = Depends(require_admin),
):
    certificate = crud.delete_energy_certificate(db=db, certificate_id=certificate_id)
    if certificate is None:
        raise HTTPException(status_code=404, detail="Energy certificate not found")
    return None