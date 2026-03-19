from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class PropertyBase(BaseModel):
    price: float = Field(..., gt=0)
    sale_date: Optional[date] = None
    postcode: Optional[str] = None
    property_type: Optional[str] = None
    property_type_epc: Optional[str] = None
    town_city: Optional[str] = None
    district: Optional[str] = None
    county: Optional[str] = None

    current_energy_rating: Optional[str] = None
    potential_energy_rating: Optional[str] = None
    current_energy_efficiency: Optional[float] = None
    potential_energy_efficiency: Optional[float] = None

    total_floor_area: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class PropertyCreate(PropertyBase):
    transaction_id: Optional[str] = None
    old_new_flag: Optional[str] = None
    tenure_duration: Optional[str] = None
    paon: Optional[str] = None
    saon: Optional[str] = None
    street: Optional[str] = None
    locality: Optional[str] = None
    ppd_category_type: Optional[str] = None
    record_status: Optional[str] = None
    lmk_key: Optional[str] = None
    built_form: Optional[str] = None
    tenure: Optional[str] = None
    number_habitable_rooms: Optional[float] = None
    co2_emissions_current: Optional[float] = None
    local_authority_code: Optional[str] = None
    local_authority_label: Optional[str] = None
    region_code: Optional[str] = None
    country_code: Optional[str] = None

class PropertyUpdate(BaseModel):
    transaction_id: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    sale_date: Optional[date] = None
    postcode: Optional[str] = None
    property_type: Optional[str] = None
    property_type_epc: Optional[str] = None

    old_new_flag: Optional[str] = None
    tenure_duration: Optional[str] = None
    paon: Optional[str] = None
    saon: Optional[str] = None
    street: Optional[str] = None
    locality: Optional[str] = None
    town_city: Optional[str] = None
    district: Optional[str] = None
    county: Optional[str] = None

    ppd_category_type: Optional[str] = None
    record_status: Optional[str] = None

    lmk_key: Optional[str] = None
    built_form: Optional[str] = None
    tenure: Optional[str] = None

    current_energy_rating: Optional[str] = None
    potential_energy_rating: Optional[str] = None
    current_energy_efficiency: Optional[float] = None
    potential_energy_efficiency: Optional[float] = None

    total_floor_area: Optional[float] = None
    number_habitable_rooms: Optional[float] = None
    co2_emissions_current: Optional[float] = None

    local_authority_code: Optional[str] = None
    local_authority_label: Optional[str] = None
    region_code: Optional[str] = None
    country_code: Optional[str] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PropertyResponse(PropertyBase):
    id: int
    transaction_id: Optional[str] = None
    old_new_flag: Optional[str] = None
    tenure_duration: Optional[str] = None
    paon: Optional[str] = None
    saon: Optional[str] = None
    street: Optional[str] = None
    locality: Optional[str] = None
    ppd_category_type: Optional[str] = None
    record_status: Optional[str] = None
    lmk_key: Optional[str] = None
    built_form: Optional[str] = None
    tenure: Optional[str] = None
    number_habitable_rooms: Optional[float] = None
    co2_emissions_current: Optional[float] = None
    local_authority_code: Optional[str] = None
    local_authority_label: Optional[str] = None
    region_code: Optional[str] = None
    country_code: Optional[str] = None

    class Config:
        from_attributes = True

class PropertyListResponse(BaseModel):
    items: list[PropertyResponse]
    skip: int
    limit: int
    returned: int

class LocationSummaryResponse(BaseModel):
    location_name: str
    listing_count: int
    average_price: Optional[float]
    median_price: Optional[float]
    average_efficiency: Optional[float]
    average_floor_area: Optional[float]


class AveragePriceResponse(BaseModel):
    area: Optional[str]
    average_price: float
    count: int


class MedianPriceResponse(BaseModel):
    area: Optional[str]
    median_price: float
    count: int


class PriceByTypeItem(BaseModel):
    property_type: Optional[str]
    average_price: float
    count: int


class EpcDistributionItem(BaseModel):
    current_energy_rating: Optional[str]
    count: int


class EfficiencySummaryResponse(BaseModel):
    area: Optional[str]
    average_current_efficiency: Optional[float]
    average_potential_efficiency: Optional[float]
    count: int


class CompareLocationsResponse(BaseModel):
    area1: str
    area2: str
    area1_average_price: Optional[float]
    area2_average_price: Optional[float]
    area1_average_efficiency: Optional[float]
    area2_average_efficiency: Optional[float]
    area1_count: int
    area2_count: int


class PriceVsEfficiencyItem(BaseModel):
    current_energy_rating: Optional[str]
    average_price: float
    count: int

class PriceTrendItem(BaseModel):
    period: str
    average_price: Optional[float]
    median_price: Optional[float]
    sales_count: int


class EnergyPriceImpactResponse(BaseModel):
    area_type: Optional[str]
    area: Optional[str]
    property_type: Optional[str]
    high_efficiency_ratings: list[str]
    low_efficiency_ratings: list[str]
    high_efficiency_average_price: Optional[float]
    low_efficiency_average_price: Optional[float]
    price_difference: Optional[float]
    percentage_difference: Optional[float]
    high_efficiency_count: int
    low_efficiency_count: int


class TopAreasByPriceItem(BaseModel):
    area_type: str
    area_name: str
    average_price: Optional[float]
    median_price: Optional[float]
    sales_count: int


class SalesVolumeTrendItem(BaseModel):
    period: str
    sales_count: int