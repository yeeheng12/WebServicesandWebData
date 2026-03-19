from __future__ import annotations

from statistics import median
from typing import Optional

from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Session

from app import models, schemas

from collections import defaultdict

def create_property(db: Session, property_data: schemas.PropertyCreate):
    db_property = models.PropertyRecord(**property_data.model_dump())
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property


def get_property(db: Session, property_id: int):
    return (
        db.query(models.PropertyRecord)
        .filter(models.PropertyRecord.id == property_id)
        .first()
    )

def update_property(
    db: Session,
    property_id: int,
    property_data: schemas.PropertyUpdate,
):
    db_property = get_property(db, property_id)
    if db_property is None:
        return None

    update_data = property_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_property, field, value)

    db.commit()
    db.refresh(db_property)
    return db_property


def get_properties(
    db: Session,
    postcode: str = None,
    town_city: str = None,
    district: str = None,
    county: str = None,
    property_type: str = None,
    min_price: float = None,
    max_price: float = None,
    date_from=None,
    date_to=None,
    epc_rating: str = None,
    min_efficiency: float = None,
    max_efficiency: float = None,
    sort_by: str = "sale_date",
    order: str = "desc",
    skip: int = 0,
    limit: int = 50,
):
    query = db.query(models.PropertyRecord)

    if postcode:
        query = query.filter(models.PropertyRecord.postcode.ilike(f"%{postcode}%"))
    if town_city:
        query = query.filter(models.PropertyRecord.town_city.ilike(f"%{town_city}%"))
    if district:
        query = query.filter(models.PropertyRecord.district.ilike(f"%{district}%"))
    if county:
        query = query.filter(models.PropertyRecord.county.ilike(f"%{county}%"))
    if property_type:
        query = query.filter(models.PropertyRecord.property_type.ilike(f"%{property_type}%"))
    if min_price is not None:
        query = query.filter(models.PropertyRecord.price >= min_price)
    if max_price is not None:
        query = query.filter(models.PropertyRecord.price <= max_price)
    if date_from is not None:
        query = query.filter(models.PropertyRecord.sale_date >= date_from)
    if date_to is not None:
        query = query.filter(models.PropertyRecord.sale_date <= date_to)
    if epc_rating:
        query = query.filter(models.PropertyRecord.current_energy_rating == epc_rating.upper())
    if min_efficiency is not None:
        query = query.filter(models.PropertyRecord.current_energy_efficiency >= min_efficiency)
    if max_efficiency is not None:
        query = query.filter(models.PropertyRecord.current_energy_efficiency <= max_efficiency)

    allowed_sort_fields = {
        "price": models.PropertyRecord.price,
        "sale_date": models.PropertyRecord.sale_date,
        "current_energy_efficiency": models.PropertyRecord.current_energy_efficiency,
        "total_floor_area": models.PropertyRecord.total_floor_area,
    }

    sort_col = allowed_sort_fields.get(sort_by, models.PropertyRecord.sale_date)
    query = query.order_by(desc(sort_col) if order == "desc" else asc(sort_col))

    return query.offset(skip).limit(limit).all()


def delete_property(db: Session, property_id: int):
    db_property = get_property(db, property_id)
    if db_property is None:
        return None
    db.delete(db_property)
    db.commit()
    return db_property


def get_distinct_locations(db: Session):
    rows = (
        db.query(models.PropertyRecord.town_city)
        .filter(models.PropertyRecord.town_city.isnot(None))
        .distinct()
        .order_by(models.PropertyRecord.town_city.asc())
        .all()
    )
    return [r[0] for r in rows if r[0]]


def _filter_area(query, area: Optional[str]):
    if area:
        query = query.filter(models.PropertyRecord.town_city.ilike(f"%{area}%"))
    return query

def _get_area_column(area_type: Optional[str]):
    allowed = {
        "town_city": models.PropertyRecord.town_city,
        "district": models.PropertyRecord.district,
        "county": models.PropertyRecord.county,
        "postcode": models.PropertyRecord.postcode,
    }
    return allowed.get(area_type or "town_city")


def _filter_area_by_type(query, area_type: Optional[str], area: Optional[str]):
    if area:
        col = _get_area_column(area_type)
        if col is not None:
            query = query.filter(col.ilike(f"%{area}%"))
    return query

def get_location_summary(db: Session, area: str):
    query = db.query(models.PropertyRecord)
    query = _filter_area(query, area)

    rows = query.all()
    if not rows:
        return None

    prices = [r.price for r in rows if r.price is not None]
    efficiencies = [r.current_energy_efficiency for r in rows if r.current_energy_efficiency is not None]
    floor_areas = [r.total_floor_area for r in rows if r.total_floor_area is not None]

    return {
        "location_name": area,
        "listing_count": len(rows),
        "average_price": round(sum(prices) / len(prices), 2) if prices else None,
        "median_price": round(median(prices), 2) if prices else None,
        "average_efficiency": round(sum(efficiencies) / len(efficiencies), 2) if efficiencies else None,
        "average_floor_area": round(sum(floor_areas) / len(floor_areas), 2) if floor_areas else None,
    }


def get_average_price(db: Session, area: str = None):
    query = db.query(
        func.avg(models.PropertyRecord.price),
        func.count(models.PropertyRecord.id),
    )
    query = _filter_area(query, area)

    avg_price, count = query.first()
    if not count:
        return None

    return {
        "area": area,
        "average_price": round(float(avg_price), 2),
        "count": count,
    }


def get_median_price(db: Session, area: str = None):
    query = db.query(models.PropertyRecord.price)
    query = _filter_area(query, area)
    prices = sorted([p[0] for p in query.all() if p[0] is not None])

    if not prices:
        return None

    return {
        "area": area,
        "median_price": round(float(median(prices)), 2),
        "count": len(prices),
    }


def get_price_by_property_type(db: Session, area: str = None):
    query = db.query(
        models.PropertyRecord.property_type,
        func.avg(models.PropertyRecord.price),
        func.count(models.PropertyRecord.id),
    )
    query = _filter_area(query, area)
    query = query.group_by(models.PropertyRecord.property_type)

    results = []
    for property_type, avg_price, count in query.all():
        results.append({
            "property_type": property_type,
            "average_price": round(float(avg_price), 2),
            "count": count,
        })
    return results


def get_epc_distribution(db: Session, area: str = None):
    query = db.query(
        models.PropertyRecord.current_energy_rating,
        func.count(models.PropertyRecord.id),
    )
    query = _filter_area(query, area)
    query = query.group_by(models.PropertyRecord.current_energy_rating)
    query = query.order_by(models.PropertyRecord.current_energy_rating.asc())

    return [
        {
            "current_energy_rating": rating,
            "count": count,
        }
        for rating, count in query.all()
    ]


def get_efficiency_summary(db: Session, area: str = None):
    query = db.query(
        func.avg(models.PropertyRecord.current_energy_efficiency),
        func.avg(models.PropertyRecord.potential_energy_efficiency),
        func.count(models.PropertyRecord.id),
    )
    query = _filter_area(query, area)

    avg_current, avg_potential, count = query.first()
    if not count:
        return None

    return {
        "area": area,
        "average_current_efficiency": round(float(avg_current), 2) if avg_current is not None else None,
        "average_potential_efficiency": round(float(avg_potential), 2) if avg_potential is not None else None,
        "count": count,
    }


def get_price_vs_efficiency(db: Session, area: str = None):
    query = db.query(
        models.PropertyRecord.current_energy_rating,
        func.avg(models.PropertyRecord.price),
        func.count(models.PropertyRecord.id),
    )
    query = _filter_area(query, area)
    query = query.group_by(models.PropertyRecord.current_energy_rating)
    query = query.order_by(models.PropertyRecord.current_energy_rating.asc())

    return [
        {
            "current_energy_rating": rating,
            "average_price": round(float(avg_price), 2),
            "count": count,
        }
        for rating, avg_price, count in query.all()
    ]


def get_compare_locations(db: Session, area1: str, area2: str):
    summary1 = get_location_summary(db, area1)
    summary2 = get_location_summary(db, area2)

    if summary1 is None or summary2 is None:
        return None

    return {
        "area1": area1,
        "area2": area2,
        "area1_average_price": summary1["average_price"],
        "area2_average_price": summary2["average_price"],
        "area1_average_efficiency": summary1["average_efficiency"],
        "area2_average_efficiency": summary2["average_efficiency"],
        "area1_count": summary1["listing_count"],
        "area2_count": summary2["listing_count"],
    }

def get_price_trend(
    db: Session,
    area_type: Optional[str] = "town_city",
    area: Optional[str] = None,
    property_type: Optional[str] = None,
    interval: str = "year",
    metric: str = "average",
):
    query = db.query(models.PropertyRecord).filter(models.PropertyRecord.sale_date.isnot(None))
    query = _filter_area_by_type(query, area_type, area)

    if property_type:
        query = query.filter(models.PropertyRecord.property_type.ilike(f"%{property_type}%"))

    rows = query.all()
    if not rows:
        return []

    grouped = defaultdict(list)

    for row in rows:
        if row.sale_date is None or row.price is None:
            continue

        if interval == "month":
            period = row.sale_date.strftime("%Y-%m")
        else:
            period = row.sale_date.strftime("%Y")

        grouped[period].append(row.price)

    results = []
    for period in sorted(grouped.keys()):
        prices = grouped[period]
        results.append(
            {
                "period": period,
                "average_price": round(sum(prices) / len(prices), 2) if prices else None,
                "median_price": round(float(median(prices)), 2) if prices else None,
                "sales_count": len(prices),
            }
        )

    return results


def get_energy_price_impact(
    db: Session,
    area_type: Optional[str] = "town_city",
    area: Optional[str] = None,
    property_type: Optional[str] = None,
):
    high_ratings = ["A", "B", "C"]
    low_ratings = ["E", "F", "G"]

    query = db.query(models.PropertyRecord)
    query = _filter_area_by_type(query, area_type, area)

    if property_type:
        query = query.filter(models.PropertyRecord.property_type.ilike(f"%{property_type}%"))

    rows = query.all()
    if not rows:
        return None

    high_prices = [
        row.price for row in rows
        if row.price is not None and row.current_energy_rating in high_ratings
    ]
    low_prices = [
        row.price for row in rows
        if row.price is not None and row.current_energy_rating in low_ratings
    ]

    high_avg = round(sum(high_prices) / len(high_prices), 2) if high_prices else None
    low_avg = round(sum(low_prices) / len(low_prices), 2) if low_prices else None

    price_difference = None
    percentage_difference = None
    if high_avg is not None and low_avg is not None:
        price_difference = round(high_avg - low_avg, 2)
        if low_avg != 0:
            percentage_difference = round(((high_avg - low_avg) / low_avg) * 100, 2)

    return {
        "area_type": area_type,
        "area": area,
        "property_type": property_type,
        "high_efficiency_ratings": high_ratings,
        "low_efficiency_ratings": low_ratings,
        "high_efficiency_average_price": high_avg,
        "low_efficiency_average_price": low_avg,
        "price_difference": price_difference,
        "percentage_difference": percentage_difference,
        "high_efficiency_count": len(high_prices),
        "low_efficiency_count": len(low_prices),
    }


def get_top_areas_by_price(
    db: Session,
    area_type: str = "town_city",
    limit: int = 10,
):
    col = _get_area_column(area_type)
    if col is None:
        return []

    query = db.query(col, models.PropertyRecord.price).filter(col.isnot(None))
    rows = query.all()

    grouped = defaultdict(list)
    for area_name, price in rows:
        if area_name and price is not None:
            grouped[area_name].append(price)

    results = []
    for area_name, prices in grouped.items():
        results.append(
            {
                "area_type": area_type,
                "area_name": area_name,
                "average_price": round(sum(prices) / len(prices), 2),
                "median_price": round(float(median(prices)), 2),
                "sales_count": len(prices),
            }
        )

    results.sort(key=lambda x: (x["average_price"] is None, -(x["average_price"] or 0)))
    return results[:limit]


def get_sales_volume_trend(
    db: Session,
    area_type: Optional[str] = "town_city",
    area: Optional[str] = None,
    interval: str = "year",
):
    query = db.query(models.PropertyRecord).filter(models.PropertyRecord.sale_date.isnot(None))
    query = _filter_area_by_type(query, area_type, area)

    rows = query.all()
    if not rows:
        return []

    grouped = defaultdict(int)

    for row in rows:
        if row.sale_date is None:
            continue

        if interval == "month":
            period = row.sale_date.strftime("%Y-%m")
        else:
            period = row.sale_date.strftime("%Y")

        grouped[period] += 1

    return [
        {"period": period, "sales_count": grouped[period]}
        for period in sorted(grouped.keys())
    ]