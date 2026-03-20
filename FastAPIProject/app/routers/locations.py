from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.dependencies import get_db

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.get(
    "/",
    response_model=List[str],
    summary="List available locations",
    description="Returns distinct location names available in the dataset.",
)
def read_locations(db: Session = Depends(get_db)):
    return crud.get_distinct_locations(db=db)

@router.get(
    "/{area_name}/summary",
    response_model=schemas.LocationSummaryWithLinksResponse,
    summary="Get location summary",
    description="Returns listing count, average price, median price, average efficiency, and floor area for a location.",
)
def read_location_summary(area_name: str, db: Session = Depends(get_db)):
    result = crud.get_location_summary(db=db, area=area_name)
    if result is None:
        raise HTTPException(status_code=404, detail="Location not found")

    payload = result.copy()
    payload["_links"] = {
        "self": f"/locations/{area_name}/summary",
        "related_area_properties": f"/properties/?town_city={area_name}",
        "price_trend": f"/analytics/price-trend?area_type=town_city&area={area_name}",
        "energy_price_impact": f"/analytics/energy-price-impact?area_type=town_city&area={area_name}",
    }
    return payload