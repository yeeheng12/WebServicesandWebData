from __future__ import annotations
from sqlalchemy.exc import IntegrityError
from app.security import get_password_hash

from statistics import median
from typing import Optional

from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Session

from app import models, schemas

from collections import defaultdict
from app.database import engine

def _get_period_expression(interval: str):
    dialect = engine.dialect.name

    if dialect == "sqlite":
        if interval == "month":
            return func.strftime("%Y-%m", models.PropertyRecord.sale_date)
        return func.strftime("%Y", models.PropertyRecord.sale_date)

    # Postgres
    if interval == "month":
        return func.to_char(models.PropertyRecord.sale_date, "YYYY-MM")
    return func.to_char(models.PropertyRecord.sale_date, "YYYY")

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db, skip: int = 0, limit: int = 50):
    items = db.query(models.User).offset(skip).limit(limit).all()
    total = db.query(models.User).count()
    return {"items": items, "total": total}

def get_user_by_id(db, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def update_user_role(db, user_id: int, role: str):
    user = get_user_by_id(db, user_id)
    if user is None:
        return None
    user.role = role
    db.commit()
    db.refresh(user)
    return user

def update_user_active_status(db, user_id: int, is_active: bool):
    user = get_user_by_id(db, user_id)
    if user is None:
        return None
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user

def create_user(db: Session, user_data: schemas.UserCreate):
    if get_user_by_username(db, user_data.username):
        return None, "duplicate_username"

    if get_user_by_email(db, user_data.email):
        return None, "duplicate_email"

    db_user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        is_active=True,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user, None

def create_property(db: Session, property_data: schemas.PropertyCreate, created_by_user_id: int | None = None):
    db_property = models.PropertyRecord(
        **property_data.model_dump(),
        created_by_user_id=created_by_user_id,
        updated_by_user_id=created_by_user_id,
    )
    db.add(db_property)

    try:
        db.commit()
        db.refresh(db_property)
        return db_property, None
    except IntegrityError:
        db.rollback()
        return None, "duplicate_transaction_id"


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
    updated_by_user_id: int | None = None,
):
    db_property = get_property(db, property_id)
    if db_property is None:
        return None, "not_found"

    update_data = property_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_property, field, value)

    db_property.updated_by_user_id = updated_by_user_id

    try:
        db.commit()
        db.refresh(db_property)
        return db_property, None
    except IntegrityError:
        db.rollback()
        return None, "duplicate_transaction_id"

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
        query = query.filter(func.lower(models.PropertyRecord.postcode) == postcode.lower())
    if town_city:
        query = query.filter(func.lower(models.PropertyRecord.town_city) == town_city.lower())
    if district:
        query = query.filter(func.lower(models.PropertyRecord.district) == district.lower())
    if county:
        query = query.filter(func.lower(models.PropertyRecord.county) == county.lower())
    if property_type:
        query = query.filter(func.lower(models.PropertyRecord.property_type) == property_type.lower())
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

    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total


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
        query = query.filter(func.lower(models.PropertyRecord.town_city) == area.lower())
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
            query = query.filter(func.lower(col) == area.lower())
    return query

def get_location_summary(db: Session, area: str):
    base_query = db.query(models.PropertyRecord)
    base_query = _filter_area(base_query, area)

    count_query = db.query(
        func.count(models.PropertyRecord.id),
        func.avg(models.PropertyRecord.price),
        func.avg(models.PropertyRecord.current_energy_efficiency),
        func.avg(models.PropertyRecord.total_floor_area),
    )
    count_query = _filter_area(count_query, area)

    listing_count, avg_price, avg_efficiency, avg_floor_area = count_query.first()

    if not listing_count:
        return None

    price_rows = (
        db.query(models.PropertyRecord.price)
        .filter(models.PropertyRecord.price.isnot(None))
    )
    price_rows = _filter_area(price_rows, area)
    prices = sorted([p[0] for p in price_rows.all() if p[0] is not None])

    median_price = round(float(median(prices)), 2) if prices else None

    return {
        "location_name": area,
        "listing_count": listing_count,
        "average_price": round(float(avg_price), 2) if avg_price is not None else None,
        "median_price": median_price,
        "average_efficiency": round(float(avg_efficiency), 2) if avg_efficiency is not None else None,
        "average_floor_area": round(float(avg_floor_area), 2) if avg_floor_area is not None else None,
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
):
    period_expr = _get_period_expression(interval)

    stats_query = db.query(
        period_expr.label("period"),
        func.avg(models.PropertyRecord.price).label("average_price"),
        func.count(models.PropertyRecord.id).label("sales_count"),
    ).filter(
        models.PropertyRecord.sale_date.isnot(None),
        models.PropertyRecord.price.isnot(None),
    )

    stats_query = _filter_area_by_type(stats_query, area_type, area)

    if property_type:
        stats_query = stats_query.filter(
            func.lower(models.PropertyRecord.property_type) == property_type.lower()
        )

    stats_query = stats_query.group_by("period").order_by("period")
    stats_rows = stats_query.all()

    if not stats_rows:
        return []

    price_query = db.query(
        period_expr.label("period"),
        models.PropertyRecord.price,
    ).filter(
        models.PropertyRecord.sale_date.isnot(None),
        models.PropertyRecord.price.isnot(None),
    )

    price_query = _filter_area_by_type(price_query, area_type, area)

    if property_type:
        price_query = price_query.filter(
            func.lower(models.PropertyRecord.property_type) == property_type.lower()
        )

    grouped_prices = defaultdict(list)
    for period, price in price_query.all():
        grouped_prices[period].append(price)

    results = []
    for period, avg_price, sales_count in stats_rows:
        prices = grouped_prices.get(period, [])
        results.append(
            {
                "period": period,
                "average_price": round(float(avg_price), 2) if avg_price is not None else None,
                "median_price": round(float(median(prices)), 2) if prices else None,
                "sales_count": sales_count,
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

    high_query = db.query(
        func.avg(models.PropertyRecord.price),
        func.count(models.PropertyRecord.id),
    ).filter(
        models.PropertyRecord.price.isnot(None),
        models.PropertyRecord.current_energy_rating.in_(high_ratings),
    )
    high_query = _filter_area_by_type(high_query, area_type, area)

    low_query = db.query(
        func.avg(models.PropertyRecord.price),
        func.count(models.PropertyRecord.id),
    ).filter(
        models.PropertyRecord.price.isnot(None),
        models.PropertyRecord.current_energy_rating.in_(low_ratings),
    )
    low_query = _filter_area_by_type(low_query, area_type, area)

    if property_type:
        high_query = high_query.filter(
            func.lower(models.PropertyRecord.property_type) == property_type.lower()
        )
        low_query = low_query.filter(
            func.lower(models.PropertyRecord.property_type) == property_type.lower()
        )

    high_avg_raw, high_count = high_query.first()
    low_avg_raw, low_count = low_query.first()

    if not high_count and not low_count:
        return None

    high_avg = round(float(high_avg_raw), 2) if high_avg_raw is not None else None
    low_avg = round(float(low_avg_raw), 2) if low_avg_raw is not None else None

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
        "high_efficiency_count": high_count or 0,
        "low_efficiency_count": low_count or 0,
    }

def get_top_areas_by_price(
    db: Session,
    area_type: str = "town_city",
    limit: int = 10,
):
    col = _get_area_column(area_type)
    if col is None:
        return []

    stats_query = db.query(
        col.label("area_name"),
        func.avg(models.PropertyRecord.price).label("average_price"),
        func.count(models.PropertyRecord.id).label("sales_count"),
    ).filter(
        col.isnot(None),
        models.PropertyRecord.price.isnot(None),
    ).group_by(col)

    stats_rows = stats_query.all()
    if not stats_rows:
        return []

    price_rows = (
        db.query(col.label("area_name"), models.PropertyRecord.price)
        .filter(col.isnot(None), models.PropertyRecord.price.isnot(None))
        .all()
    )

    grouped_prices = defaultdict(list)
    for area_name, price in price_rows:
        grouped_prices[area_name].append(price)

    results = []
    for area_name, avg_price, sales_count in stats_rows:
        prices = grouped_prices.get(area_name, [])
        results.append(
            {
                "area_type": area_type,
                "area_name": area_name,
                "average_price": round(float(avg_price), 2) if avg_price is not None else None,
                "median_price": round(float(median(prices)), 2) if prices else None,
                "sales_count": sales_count,
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
    period_expr = _get_period_expression(interval)

    query = db.query(
        period_expr.label("period"),
        func.count(models.PropertyRecord.id).label("sales_count"),
    ).filter(models.PropertyRecord.sale_date.isnot(None))

    query = _filter_area_by_type(query, area_type, area)
    query = query.group_by("period").order_by("period")

    return [
        {"period": period, "sales_count": sales_count}
        for period, sales_count in query.all()
    ]

def get_top_areas_by_energy_premium(
    db: Session,
    area_type: str = "town_city",
    limit: int = 10,
):
    col = _get_area_column(area_type)
    if col is None:
        return []

    high_ratings = ["A", "B", "C"]
    low_ratings = ["E", "F", "G"]

    high_query = db.query(
        col.label("area_name"),
        func.avg(models.PropertyRecord.price).label("high_avg"),
        func.count(models.PropertyRecord.id).label("high_count"),
    ).filter(
        col.isnot(None),
        models.PropertyRecord.price.isnot(None),
        models.PropertyRecord.current_energy_rating.in_(high_ratings),
    ).group_by(col)

    low_query = db.query(
        col.label("area_name"),
        func.avg(models.PropertyRecord.price).label("low_avg"),
        func.count(models.PropertyRecord.id).label("low_count"),
    ).filter(
        col.isnot(None),
        models.PropertyRecord.price.isnot(None),
        models.PropertyRecord.current_energy_rating.in_(low_ratings),
    ).group_by(col)

    high_rows = {
        area_name: (high_avg, high_count)
        for area_name, high_avg, high_count in high_query.all()
    }
    low_rows = {
        area_name: (low_avg, low_count)
        for area_name, low_avg, low_count in low_query.all()
    }

    common_areas = set(high_rows.keys()) & set(low_rows.keys())
    if not common_areas:
        return []

    results = []
    for area_name in common_areas:
        high_avg_raw, high_count = high_rows[area_name]
        low_avg_raw, low_count = low_rows[area_name]

        high_avg = round(float(high_avg_raw), 2) if high_avg_raw is not None else None
        low_avg = round(float(low_avg_raw), 2) if low_avg_raw is not None else None

        if high_avg is None or low_avg is None:
            continue

        price_difference = round(high_avg - low_avg, 2)
        percentage_difference = round(((high_avg - low_avg) / low_avg) * 100, 2) if low_avg != 0 else None

        results.append(
            {
                "area_type": area_type,
                "area_name": area_name,
                "high_efficiency_ratings": high_ratings,
                "low_efficiency_ratings": low_ratings,
                "high_efficiency_average_price": high_avg,
                "low_efficiency_average_price": low_avg,
                "price_difference": price_difference,
                "percentage_difference": percentage_difference,
                "high_efficiency_count": high_count,
                "low_efficiency_count": low_count,
            }
        )

    results.sort(
        key=lambda x: (
            x["price_difference"] is None,
            -(x["price_difference"] or 0),
        )
    )
    return results[:limit]

def build_pagination_meta(*, skip: int, limit: int, returned: int, total: int):
    next_offset = skip + limit if skip + limit < total else None
    previous_offset = max(skip - limit, 0) if skip > 0 else None

    return {
        "skip": skip,
        "limit": limit,
        "returned": returned,
        "total": total,
        "has_next": next_offset is not None,
        "has_previous": skip > 0,
        "next_offset": next_offset,
        "previous_offset": previous_offset,
    }

def create_energy_certificate(
    db: Session,
    certificate_data: schemas.EnergyCertificateCreate,
    created_by_user_id: int | None = None,
):
    property_exists = get_property(db, certificate_data.property_id)
    if property_exists is None:
        return None, "property_not_found"

    db_certificate = models.EnergyCertificate(
        **certificate_data.model_dump(),
        created_by_user_id=created_by_user_id,
        updated_by_user_id=created_by_user_id,
    )
    db.add(db_certificate)

    try:
        db.commit()
        db.refresh(db_certificate)
        return db_certificate, None
    except IntegrityError:
        db.rollback()
        return None, "duplicate_lmk_key"


def get_energy_certificate(db: Session, certificate_id: int):
    return (
        db.query(models.EnergyCertificate)
        .filter(models.EnergyCertificate.id == certificate_id)
        .first()
    )


def get_energy_certificates(
    db: Session,
    property_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
):
    query = db.query(models.EnergyCertificate)

    if property_id is not None:
        query = query.filter(models.EnergyCertificate.property_id == property_id)

    total = query.count()

    items = (
        query.order_by(models.EnergyCertificate.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return items, total

def update_energy_certificate(
    db: Session,
    certificate_id: int,
    certificate_data: schemas.EnergyCertificateUpdate,
    updated_by_user_id: int | None = None,
):
    db_certificate = get_energy_certificate(db, certificate_id)
    if db_certificate is None:
        return None, "certificate_not_found"

    update_data = certificate_data.model_dump(exclude_unset=True)

    if "property_id" in update_data:
        property_exists = get_property(db, update_data["property_id"])
        if property_exists is None:
            return None, "property_not_found"

    for field, value in update_data.items():
        setattr(db_certificate, field, value)

    db_certificate.updated_by_user_id = updated_by_user_id

    try:
        db.commit()
        db.refresh(db_certificate)
        return db_certificate, None
    except IntegrityError:
        db.rollback()
        return None, "duplicate_lmk_key"

def delete_energy_certificate(db: Session, certificate_id: int):
    db_certificate = get_energy_certificate(db, certificate_id)
    if db_certificate is None:
        return None

    db.delete(db_certificate)
    db.commit()
    return db_certificate


def get_property_energy_certificates(
    db: Session,
    property_id: int,
    skip: int = 0,
    limit: int = 50,
):
    property_exists = get_property(db, property_id)
    if property_exists is None:
        return None, None, "property_not_found"

    query = (
        db.query(models.EnergyCertificate)
        .filter(models.EnergyCertificate.property_id == property_id)
    )

    total = query.count()

    certificates = (
        query.order_by(models.EnergyCertificate.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return certificates, total, None