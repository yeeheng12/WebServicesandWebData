from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str = "viewer"

    @field_validator("role")
    @classmethod
    def validate_role(cls, value):
        if value not in {"viewer", "editor", "admin"}:
            raise ValueError("role must be one of: viewer, editor, admin")
        return value


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserRoleUpdate(BaseModel):
    role: str = Field(..., pattern="^(viewer|editor|admin)$")

class UserStatusUpdate(BaseModel):
    is_active: bool

class UserListResponse(BaseModel):
    items: list["UserResponse"]
    total: int

class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class LoginResponse(TokenResponse):
    user: UserResponse

class AuditFieldsMixin(BaseModel):
    created_at: datetime
    updated_at: datetime
    created_by_user_id: Optional[int] = None
    updated_by_user_id: Optional[int] = None

class EnergyValidationMixin(BaseModel):
    @field_validator("current_energy_rating", "potential_energy_rating", check_fields=False)
    @classmethod
    def validate_energy_rating(cls, value):
        if value is None:
            return value
        value = value.upper()
        if value not in {"A", "B", "C", "D", "E", "F", "G"}:
            raise ValueError("energy rating must be one of: A, B, C, D, E, F, G")
        return value

    @field_validator("current_energy_efficiency", "potential_energy_efficiency", check_fields=False)
    @classmethod
    def validate_efficiency(cls, value):
        if value is None:
            return value
        if value < 0 or value > 100:
            raise ValueError("energy efficiency must be between 0 and 100")
        return value

    @field_validator("total_floor_area", check_fields=False)
    @classmethod
    def validate_floor_area(cls, value):
        if value is None:
            return value
        if value < 0:
            raise ValueError("total_floor_area must be non-negative")
        return value

class PropertyBase(EnergyValidationMixin):
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

class PropertyUpdate(EnergyValidationMixin):
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

class PropertyResponse(AuditFieldsMixin, PropertyBase):
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

    model_config = ConfigDict(from_attributes=True)


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

class LinksResponse(BaseModel):
    self: str
    related_area_properties: Optional[str] = None
    price_trend: Optional[str] = None
    energy_price_impact: Optional[str] = None
    energy_certificates: Optional[str] = None


class PropertyDetailResponse(PropertyResponse):
    links: LinksResponse = Field(alias="_links")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class LocationSummaryWithLinksResponse(LocationSummaryResponse):
    links: LinksResponse = Field(alias="_links")

    model_config = ConfigDict(populate_by_name=True)

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

class TopAreasByEnergyPremiumItem(BaseModel):
    area_type: str
    area_name: str
    high_efficiency_ratings: list[str]
    low_efficiency_ratings: list[str]
    high_efficiency_average_price: Optional[float]
    low_efficiency_average_price: Optional[float]
    price_difference: Optional[float]
    percentage_difference: Optional[float]
    high_efficiency_count: int
    low_efficiency_count: int

class EnergyCertificateBase(EnergyValidationMixin):
    property_id: int
    lmk_key: Optional[str] = None
    current_energy_rating: Optional[str] = None
    potential_energy_rating: Optional[str] = None
    current_energy_efficiency: Optional[float] = None
    potential_energy_efficiency: Optional[float] = None
    total_floor_area: Optional[float] = None
    lodgement_date: Optional[date] = None
    inspection_date: Optional[date] = None
    tenure: Optional[str] = None
    built_form: Optional[str] = None
    mains_gas_flag: Optional[str] = None
    windows_description: Optional[str] = None
    walls_description: Optional[str] = None
    roof_description: Optional[str] = None
    floor_description: Optional[str] = None
    heating_description: Optional[str] = None
    hotwater_description: Optional[str] = None

class EnergyCertificateCreate(EnergyCertificateBase):
    pass


class EnergyCertificateUpdate(EnergyValidationMixin):
    property_id: Optional[int] = None
    lmk_key: Optional[str] = None
    current_energy_rating: Optional[str] = None
    potential_energy_rating: Optional[str] = None
    current_energy_efficiency: Optional[float] = None
    potential_energy_efficiency: Optional[float] = None
    total_floor_area: Optional[float] = None
    lodgement_date: Optional[date] = None
    inspection_date: Optional[date] = None
    tenure: Optional[str] = None
    built_form: Optional[str] = None
    mains_gas_flag: Optional[str] = None
    windows_description: Optional[str] = None
    walls_description: Optional[str] = None
    roof_description: Optional[str] = None
    floor_description: Optional[str] = None
    heating_description: Optional[str] = None
    hotwater_description: Optional[str] = None

class EnergyCertificateResponse(AuditFieldsMixin, EnergyCertificateBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PaginationMeta(BaseModel):
    skip: int
    limit: int
    returned: int
    total: int
    has_next: bool
    has_previous: bool
    next_offset: Optional[int] = None
    previous_offset: Optional[int] = None


class PropertyListResponse(BaseModel):
    items: list[PropertyResponse]
    pagination: PaginationMeta


class EnergyCertificateListResponse(BaseModel):
    items: list[EnergyCertificateResponse]
    pagination: PaginationMeta