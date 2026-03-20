from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Index, Integer, String, func, Boolean
from sqlalchemy.orm import relationship

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # viewer, editor, admin
    role = Column(String, nullable=False, default="viewer")
    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    created_properties = relationship(
        "PropertyRecord",
        foreign_keys="PropertyRecord.created_by_user_id",
        back_populates="created_by_user",
    )
    updated_properties = relationship(
        "PropertyRecord",
        foreign_keys="PropertyRecord.updated_by_user_id",
        back_populates="updated_by_user",
    )
    created_certificates = relationship(
        "EnergyCertificate",
        foreign_keys="EnergyCertificate.created_by_user_id",
        back_populates="created_by_user",
    )
    updated_certificates = relationship(
        "EnergyCertificate",
        foreign_keys="EnergyCertificate.updated_by_user_id",
        back_populates="updated_by_user",
    )

class PropertyRecord(Base):
    __tablename__ = "property_records"

    __table_args__ = (
        Index("ix_property_town_city_sale_date", "town_city", "sale_date"),
        Index("ix_property_district_sale_date", "district", "sale_date"),
        Index("ix_property_county_sale_date", "county", "sale_date"),
        Index("ix_property_town_city_price", "town_city", "price"),
        Index("ix_property_district_price", "district", "price"),
        Index("ix_property_county_price", "county", "price"),
        Index("ix_property_town_city_energy_rating", "town_city", "current_energy_rating"),
        Index("ix_property_district_energy_rating", "district", "current_energy_rating"),
        Index("ix_property_county_energy_rating", "county", "current_energy_rating"),
        Index("ix_property_property_type_sale_date", "property_type", "sale_date"),
    )

    id = Column(Integer, primary_key=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    updated_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    created_by_user = relationship(
        "User",
        foreign_keys=[created_by_user_id],
        back_populates="created_properties",
    )
    updated_by_user = relationship(
        "User",
        foreign_keys=[updated_by_user_id],
        back_populates="updated_properties",
    )

    transaction_id = Column(String, unique=True, index=True, nullable=True)
    price = Column(Float, index=True, nullable=False)
    sale_date = Column(Date, index=True, nullable=True)

    postcode = Column(String, index=True, nullable=True)

    # Main API-facing property type
    property_type = Column(String, index=True, nullable=True)

    # Raw source-specific property types kept for transparency/debugging
    property_type_epc = Column(String, nullable=True)

    old_new_flag = Column(String, nullable=True)
    tenure_duration = Column(String, nullable=True)

    paon = Column(String, nullable=True)
    saon = Column(String, nullable=True)
    street = Column(String, nullable=True)
    locality = Column(String, nullable=True)
    town_city = Column(String, index=True, nullable=True)
    district = Column(String, index=True, nullable=True)
    county = Column(String, index=True, nullable=True)

    ppd_category_type = Column(String, nullable=True)
    record_status = Column(String, nullable=True)

    lmk_key = Column(String, index=True, nullable=True)
    address1 = Column(String, nullable=True)
    address2 = Column(String, nullable=True)
    address3 = Column(String, nullable=True)
    address = Column(String, nullable=True)

    local_authority_code = Column(String, index=True, nullable=True)
    local_authority_label = Column(String, nullable=True)
    posttown = Column(String, nullable=True)

    built_form = Column(String, nullable=True)
    tenure = Column(String, nullable=True)

    current_energy_rating = Column(String, index=True, nullable=True)
    potential_energy_rating = Column(String, nullable=True)
    current_energy_efficiency = Column(Float, index=True, nullable=True)
    potential_energy_efficiency = Column(Float, nullable=True)

    total_floor_area = Column(Float, nullable=True)
    number_habitable_rooms = Column(Float, nullable=True)

    environment_impact_current = Column(Float, nullable=True)
    environment_impact_potential = Column(Float, nullable=True)
    co2_emissions_current = Column(Float, nullable=True)
    energy_consumption_current = Column(Float, nullable=True)
    energy_consumption_potential = Column(Float, nullable=True)

    mains_gas_flag = Column(String, nullable=True)
    hotwater_description = Column(String, nullable=True)
    heating_description = Column(String, nullable=True)
    windows_description = Column(String, nullable=True)
    walls_description = Column(String, nullable=True)
    roof_description = Column(String, nullable=True)
    lighting_description = Column(String, nullable=True)
    floor_description = Column(String, nullable=True)
    construction_age_band = Column(String, nullable=True)

    lodgement_date = Column(Date, nullable=True)
    inspection_date = Column(Date, nullable=True)
    transaction_type = Column(String, nullable=True)
    uprn = Column(String, nullable=True)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    region_code = Column(String, nullable=True)
    country_code = Column(String, nullable=True)

    energy_certificates = relationship(
        "EnergyCertificate",
        back_populates="property",
        cascade="all, delete-orphan",
    )

class EnergyCertificate(Base):
    __tablename__ = "energy_certificates"
    __table_args__ = (
        Index("ix_energy_property_lodgement_date", "property_id", "lodgement_date"),
        Index("ix_energy_property_inspection_date", "property_id", "inspection_date"),
        Index("ix_energy_property_current_rating", "property_id", "current_energy_rating"),
    )

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("property_records.id"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    updated_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    created_by_user = relationship(
        "User",
        foreign_keys=[created_by_user_id],
        back_populates="created_certificates",
    )
    updated_by_user = relationship(
        "User",
        foreign_keys=[updated_by_user_id],
        back_populates="updated_certificates",
    )

    lmk_key = Column(String, unique=True, index=True, nullable=True)

    current_energy_rating = Column(String, index=True, nullable=True)
    potential_energy_rating = Column(String, nullable=True)

    current_energy_efficiency = Column(Float, nullable=True)
    potential_energy_efficiency = Column(Float, nullable=True)

    total_floor_area = Column(Float, nullable=True)
    lodgement_date = Column(Date, nullable=True)
    inspection_date = Column(Date, nullable=True)

    tenure = Column(String, nullable=True)
    built_form = Column(String, nullable=True)
    mains_gas_flag = Column(String, nullable=True)

    windows_description = Column(String, nullable=True)
    walls_description = Column(String, nullable=True)
    roof_description = Column(String, nullable=True)
    floor_description = Column(String, nullable=True)
    heating_description = Column(String, nullable=True)
    hotwater_description = Column(String, nullable=True)

    property = relationship("PropertyRecord", back_populates="energy_certificates")