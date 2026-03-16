from sqlalchemy.orm import Session
from app import models, schemas


def create_location(db: Session, location: schemas.LocationCreate):
    db_location = models.Location(
        city=location.city,
        district=location.district,
        postcode_area=location.postcode_area,
        region=location.region,
        latitude=location.latitude,
        longitude=location.longitude
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def get_locations(db: Session):
    return db.query(models.Location).all()


def get_location(db: Session, location_id: int):
    return db.query(models.Location).filter(models.Location.id == location_id).first()


def update_location(db: Session, location_id: int, location: schemas.LocationCreate):
    db_location = get_location(db, location_id)

    if db_location is None:
        return None

    db_location.city = location.city
    db_location.district = location.district
    db_location.postcode_area = location.postcode_area
    db_location.region = location.region
    db_location.latitude = location.latitude
    db_location.longitude = location.longitude

    db.commit()
    db.refresh(db_location)
    return db_location


def delete_location(db: Session, location_id: int):
    db_location = get_location(db, location_id)

    if db_location is None:
        return None

    db.delete(db_location)
    db.commit()
    return db_location


def create_listing(db: Session, listing: schemas.ListingCreate):
    db_listing = models.Listing(
        title=listing.title,
        description=listing.description,
        monthly_rent=listing.monthly_rent,
        deposit=listing.deposit,
        bedrooms=listing.bedrooms,
        bathrooms=listing.bathrooms,
        property_type=listing.property_type,
        furnished=listing.furnished,
        bills_included=listing.bills_included,
        available_from=listing.available_from,
        is_active=listing.is_active,
        location_id=listing.location_id
    )
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing


def get_listings(
    db: Session,
    city: str = None,
    district: str = None,
    min_rent: float = None,
    max_rent: float = None,
    bedrooms: int = None,
    property_type: str = None,
    is_active: bool = None,
    sort_by: str = None,
    order: str = "asc"
):
    query = db.query(models.Listing).join(models.Location)

    if city:
        query = query.filter(models.Location.city.ilike(f"%{city}%"))

    if district:
        query = query.filter(models.Location.district.ilike(f"%{district}%"))

    if min_rent is not None:
        query = query.filter(models.Listing.monthly_rent >= min_rent)

    if max_rent is not None:
        query = query.filter(models.Listing.monthly_rent <= max_rent)

    if bedrooms is not None:
        query = query.filter(models.Listing.bedrooms == bedrooms)

    if property_type:
        query = query.filter(models.Listing.property_type.ilike(f"%{property_type}%"))

    if is_active is not None:
        query = query.filter(models.Listing.is_active == is_active)

    allowed_sort_fields = {
        "monthly_rent": models.Listing.monthly_rent,
        "bedrooms": models.Listing.bedrooms,
        "bathrooms": models.Listing.bathrooms,
        "available_from": models.Listing.available_from
    }

    if sort_by in allowed_sort_fields:
        sort_column = allowed_sort_fields[sort_by]
        if order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

    return query.all()


def get_listing(db: Session, listing_id: int):
    return db.query(models.Listing).filter(models.Listing.id == listing_id).first()


def update_listing(db: Session, listing_id: int, listing: schemas.ListingCreate):
    db_listing = get_listing(db, listing_id)

    if db_listing is None:
        return None

    db_listing.title = listing.title
    db_listing.description = listing.description
    db_listing.monthly_rent = listing.monthly_rent
    db_listing.deposit = listing.deposit
    db_listing.bedrooms = listing.bedrooms
    db_listing.bathrooms = listing.bathrooms
    db_listing.property_type = listing.property_type
    db_listing.furnished = listing.furnished
    db_listing.bills_included = listing.bills_included
    db_listing.available_from = listing.available_from
    db_listing.is_active = listing.is_active
    db_listing.location_id = listing.location_id

    db.commit()
    db.refresh(db_listing)
    return db_listing


def delete_listing(db: Session, listing_id: int):
    db_listing = get_listing(db, listing_id)

    if db_listing is None:
        return None

    db.delete(db_listing)
    db.commit()
    return db_listing

def get_average_rent(db: Session, city: str = None):
    query = db.query(models.Listing).join(models.Location)

    if city:
        query = query.filter(models.Location.city.ilike(f"%{city}%"))

    listings = query.all()

    if not listings:
        return None

    average_rent = sum(listing.monthly_rent for listing in listings) / len(listings)

    return {
        "city": city,
        "average_rent": round(average_rent, 2),
        "listing_count": len(listings)
    }


def get_median_rent(db: Session, city: str = None):
    query = db.query(models.Listing).join(models.Location)

    if city:
        query = query.filter(models.Location.city.ilike(f"%{city}%"))

    rents = sorted([listing.monthly_rent for listing in query.all()])

    if not rents:
        return None

    n = len(rents)
    mid = n // 2

    if n % 2 == 0:
        median = (rents[mid - 1] + rents[mid]) / 2
    else:
        median = rents[mid]

    return {
        "city": city,
        "median_rent": round(median, 2),
        "listing_count": n
    }


def get_summary_stats(db: Session, city: str = None):
    query = db.query(models.Listing).join(models.Location)

    if city:
        query = query.filter(models.Location.city.ilike(f"%{city}%"))

    listings = query.all()

    if not listings:
        return None

    rents = [listing.monthly_rent for listing in listings]
    average_rent = sum(rents) / len(rents)

    sorted_rents = sorted(rents)
    n = len(sorted_rents)
    mid = n // 2

    if n % 2 == 0:
        median_rent = (sorted_rents[mid - 1] + sorted_rents[mid]) / 2
    else:
        median_rent = sorted_rents[mid]

    cheapest_listing = min(listings, key=lambda x: x.monthly_rent)
    most_expensive_listing = max(listings, key=lambda x: x.monthly_rent)

    return {
        "city": city,
        "listing_count": len(listings),
        "average_rent": round(average_rent, 2),
        "median_rent": round(median_rent, 2),
        "cheapest_listing": {
            "id": cheapest_listing.id,
            "title": cheapest_listing.title,
            "monthly_rent": cheapest_listing.monthly_rent
        },
        "most_expensive_listing": {
            "id": most_expensive_listing.id,
            "title": most_expensive_listing.title,
            "monthly_rent": most_expensive_listing.monthly_rent
        }
    }

def get_area_comparison(db: Session, city: str = None):
    query = db.query(models.Listing).join(models.Location)

    if city:
        query = query.filter(models.Location.city.ilike(f"%{city}%"))

    listings = query.all()

    if not listings:
        return None

    district_data = {}

    for listing in listings:
        district = listing.location.district

        if district not in district_data:
            district_data[district] = []

        district_data[district].append(listing.monthly_rent)

    results = []

    for district, rents in district_data.items():
        rents_sorted = sorted(rents)
        n = len(rents_sorted)
        mid = n // 2

        if n % 2 == 0:
            median_rent = (rents_sorted[mid - 1] + rents_sorted[mid]) / 2
        else:
            median_rent = rents_sorted[mid]

        average_rent = sum(rents_sorted) / n

        results.append({
            "district": district,
            "listing_count": n,
            "average_rent": round(average_rent, 2),
            "median_rent": round(median_rent, 2)
        })

    results.sort(key=lambda x: x["average_rent"], reverse=True)

    return {
        "city": city,
        "areas": results
    }


def get_outliers(db: Session, city: str = None):
    query = db.query(models.Listing).join(models.Location)

    if city:
        query = query.filter(models.Location.city.ilike(f"%{city}%"))

    listings = query.all()

    if not listings:
        return None

    rents = [listing.monthly_rent for listing in listings]
    n = len(rents)

    if n < 2:
        return {
            "city": city,
            "mean_rent": round(rents[0], 2),
            "lower_threshold": round(rents[0], 2),
            "upper_threshold": round(rents[0], 2),
            "outliers": []
        }

    mean_rent = sum(rents) / n
    variance = sum((rent - mean_rent) ** 2 for rent in rents) / n
    std_dev = variance ** 0.5

    lower_threshold = mean_rent - 2 * std_dev
    upper_threshold = mean_rent + 2 * std_dev

    outliers = []

    for listing in listings:
        if listing.monthly_rent < lower_threshold or listing.monthly_rent > upper_threshold:
            outliers.append({
                "id": listing.id,
                "title": listing.title,
                "monthly_rent": listing.monthly_rent,
                "district": listing.location.district,
                "reason": "Below threshold" if listing.monthly_rent < lower_threshold else "Above threshold"
            })

    return {
        "city": city,
        "mean_rent": round(mean_rent, 2),
        "lower_threshold": round(lower_threshold, 2),
        "upper_threshold": round(upper_threshold, 2),
        "outliers": outliers
    }