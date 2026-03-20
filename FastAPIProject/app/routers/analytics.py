from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.dependencies import get_db

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/average-price",
    response_model=schemas.AveragePriceResponse,
    summary="Get average sale price",
    description="Returns the average sale price for all properties or for a filtered area.",
)
def average_price(area: str = None, db: Session = Depends(get_db)):
    result = crud.get_average_price(db=db, area=area)
    if result is None:
        raise HTTPException(status_code=404, detail="No matching properties found")
    return result


@router.get(
    "/median-price",
    response_model=schemas.MedianPriceResponse,
    summary="Get median sale price",
    description="Returns the median sale price for all properties or for a filtered area.",
)
def median_price(area: str = None, db: Session = Depends(get_db)):
    result = crud.get_median_price(db=db, area=area)
    if result is None:
        raise HTTPException(status_code=404, detail="No matching properties found")
    return result


@router.get(
    "/price-by-property-type",
    response_model=List[schemas.PriceByTypeItem],
    summary="Compare prices by property type",
    description="Returns average sale price grouped by property type, optionally filtered by area.",
)
def price_by_property_type(area: str = None, db: Session = Depends(get_db)):
    return crud.get_price_by_property_type(db=db, area=area)


@router.get(
    "/epc-distribution",
    response_model=List[schemas.EpcDistributionItem],
    summary="Get EPC rating distribution",
    description="Returns the distribution of current EPC energy ratings, optionally filtered by area.",
)
def epc_distribution(area: str = None, db: Session = Depends(get_db)):
    return crud.get_epc_distribution(db=db, area=area)


@router.get(
    "/efficiency-summary",
    response_model=schemas.EfficiencySummaryResponse,
    summary="Get energy efficiency summary",
    description="Returns average current and potential energy efficiency scores, optionally filtered by area.",
)
def efficiency_summary(area: str = None, db: Session = Depends(get_db)):
    result = crud.get_efficiency_summary(db=db, area=area)
    if result is None:
        raise HTTPException(status_code=404, detail="No matching properties found")
    return result


@router.get(
    "/price-vs-efficiency",
    response_model=List[schemas.PriceVsEfficiencyItem],
    summary="Compare price against EPC rating",
    description="Returns average price grouped by current EPC rating, optionally filtered by area.",
)
def price_vs_efficiency(area: str = None, db: Session = Depends(get_db)):
    return crud.get_price_vs_efficiency(db=db, area=area)


@router.get(
    "/compare-locations",
    response_model=schemas.CompareLocationsResponse,
    summary="Compare two locations",
    description="Returns average price and average energy efficiency for two named areas.",
)
def compare_locations(area1: str, area2: str, db: Session = Depends(get_db)):
    result = crud.get_compare_locations(db=db, area1=area1, area2=area2)
    if result is None:
        raise HTTPException(status_code=404, detail="One or both locations not found")
    return result


@router.get(
    "/price-trend",
    response_model=List[schemas.PriceTrendItem],
    summary="Get house price trend over time",
    description="Returns average and median sale prices over time, optionally filtered by area and property type.",
)
def price_trend(
    area_type: Literal["town_city", "district", "county", "postcode"] = "town_city",
    area: Optional[str] = None,
    property_type: Optional[str] = None,
    interval: Literal["year", "month"] = "year",
    db: Session = Depends(get_db),
):
    return crud.get_price_trend(
        db=db,
        area_type=area_type,
        area=area,
        property_type=property_type,
        interval=interval,
    )


@router.get(
    "/energy-price-impact",
    response_model=schemas.EnergyPriceImpactResponse,
    summary="Measure energy efficiency price impact",
    description="Compares average prices of higher-efficiency homes against lower-efficiency homes, optionally filtered by area and property type.",
    responses={
        200: {
            "description": "Energy price impact calculated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "area_type": "town_city",
                        "area": "Leeds",
                        "property_type": None,
                        "high_efficiency_ratings": ["A", "B", "C"],
                        "low_efficiency_ratings": ["E", "F", "G"],
                        "high_efficiency_average_price": 312450.25,
                        "low_efficiency_average_price": 248220.8,
                        "price_difference": 64229.45,
                        "percentage_difference": 25.88,
                        "high_efficiency_count": 180,
                        "low_efficiency_count": 240
                    }
                }
            }
        },
        404: {
            "description": "No matching properties found",
            "content": {
                "application/json": {
                    "example": {"detail": "No matching properties found"}
                }
            }
        }
    },
)
def energy_price_impact(
    area_type: Literal["town_city", "district", "county", "postcode"] = "town_city",
    area: Optional[str] = None,
    property_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    result = crud.get_energy_price_impact(
        db=db,
        area_type=area_type,
        area=area,
        property_type=property_type,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="No matching properties found")
    return result


@router.get(
    "/top-areas-by-price",
    response_model=List[schemas.TopAreasByPriceItem],
    summary="Rank areas by sale price",
    description="Returns the highest-priced areas by average and median sale price.",
)
def top_areas_by_price(
    area_type: Literal["town_city", "district", "county", "postcode"] = "town_city",
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return crud.get_top_areas_by_price(db=db, area_type=area_type, limit=limit)

@router.get(
    "/top-areas-by-energy-premium",
    response_model=List[schemas.TopAreasByEnergyPremiumItem],
    summary="Rank areas by energy-efficiency price premium",
    description=(
        "Returns areas where higher-efficiency homes (A/B/C) have the "
        "largest average sale price premium over lower-efficiency homes (E/F/G)."
    ),
)
def top_areas_by_energy_premium(
    area_type: Literal["town_city", "district", "county", "postcode"] = "town_city",
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return crud.get_top_areas_by_energy_premium(
        db=db,
        area_type=area_type,
        limit=limit,
    )
@router.get(
    "/sales-volume-trend",
    response_model=List[schemas.SalesVolumeTrendItem],
    summary="Get sales volume trend",
    description="Returns transaction count over time, optionally filtered by area.",
)
def sales_volume_trend(
    area_type: Literal["town_city", "district", "county", "postcode"] = "town_city",
    area: Optional[str] = None,
    interval: Literal["year", "month"] = "year",
    db: Session = Depends(get_db),
):
    return crud.get_sales_volume_trend(
        db=db,
        area_type=area_type,
        area=area,
        interval=interval,
    )