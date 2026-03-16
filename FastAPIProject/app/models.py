from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, nullable=False)
    district = Column(String, nullable=False)
    postcode_area = Column(String, nullable=False)
    region = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    listings = relationship("Listing", back_populates="location", cascade="all, delete")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    monthly_rent = Column(Float, nullable=False)
    deposit = Column(Float, nullable=False)
    bedrooms = Column(Integer, nullable=False)
    bathrooms = Column(Integer, nullable=False)
    property_type = Column(String, nullable=False)
    furnished = Column(Boolean, nullable=False, default=False)
    bills_included = Column(Boolean, nullable=False, default=False)
    available_from = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)

    location = relationship("Location", back_populates="listings")