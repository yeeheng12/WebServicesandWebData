from pydantic import BaseModel
from typing import Optional


class LocationBase(BaseModel):
    city: str
    district: str
    postcode_area: str
    region: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class LocationCreate(LocationBase):
    pass


class LocationResponse(LocationBase):
    id: int

    class Config:
        from_attributes = True


class ListingBase(BaseModel):
    title: str
    description: str
    monthly_rent: float
    deposit: float
    bedrooms: int
    bathrooms: int
    property_type: str
    furnished: bool
    bills_included: bool
    available_from: str
    is_active: bool = True
    location_id: int


class ListingCreate(ListingBase):
    pass


class ListingResponse(ListingBase):
    id: int

    class Config:
        from_attributes = True