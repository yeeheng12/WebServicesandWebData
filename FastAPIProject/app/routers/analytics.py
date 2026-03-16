from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.dependencies import get_db

router = APIRouter()


@router.get("/average-rent")
def average_rent(city: str = None, db: Session = Depends(get_db)):
    result = crud.get_average_rent(db=db, city=city)
    if result is None:
        raise HTTPException(status_code=404, detail="No listings found")
    return result


@router.get("/median-rent")
def median_rent(city: str = None, db: Session = Depends(get_db)):
    result = crud.get_median_rent(db=db, city=city)
    if result is None:
        raise HTTPException(status_code=404, detail="No listings found")
    return result


@router.get("/summary")
def summary(city: str = None, db: Session = Depends(get_db)):
    result = crud.get_summary_stats(db=db, city=city)
    if result is None:
        raise HTTPException(status_code=404, detail="No listings found")
    return result


@router.get("/area-comparison")
def area_comparison(city: str = None, db: Session = Depends(get_db)):
    result = crud.get_area_comparison(db=db, city=city)
    if result is None:
        raise HTTPException(status_code=404, detail="No listings found")
    return result


@router.get("/outliers")
def outliers(city: str = None, db: Session = Depends(get_db)):
    result = crud.get_outliers(db=db, city=city)
    if result is None:
        raise HTTPException(status_code=404, detail="No listings found")
    return result