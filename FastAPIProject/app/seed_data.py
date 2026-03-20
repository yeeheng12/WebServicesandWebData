from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.database import SessionLocal, engine
from app.models import Base, PropertyRecord

PROJECT_ROOT = Path(__file__).resolve().parents[1]
#local
#DATA_PATH = PROJECT_ROOT / "data" / "processed" / "property_records.csv"
#for deployment
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "property_records_deploy.csv"

def parse_date(value):
    if pd.isna(value):
        return None

    text = str(value).strip()
    if not text or text.upper() in {"NAN", "NONE", "NULL"}:
        return None

    # Fast path for values like 2024-05-17 or 2024-05-17 00:00:00
    try:
        return pd.Timestamp(text[:10]).date()
    except Exception:
        return None


def parse_float(value):
    if pd.isna(value):
        return None
    try:
        return float(value)
    except Exception:
        return None


def parse_str(value):
    if pd.isna(value):
        return None
    text = str(value).strip()
    return text if text else None


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing merged data file: {DATA_PATH}")

    Base.metadata.create_all(bind=engine)

    df = pd.read_csv(DATA_PATH, low_memory=False)

    for col in ["sale_date", "lodgement_date", "inspection_date"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str[:10]
            df.loc[df[col].isin(["nan", "None", "NULL", ""]), col] = None

    db = SessionLocal()
    try:
        db.query(PropertyRecord).delete()
        db.commit()

        records = []
        for _, row in df.iterrows():
            records.append(
                PropertyRecord(
                    transaction_id=parse_str(row.get("transaction_id")),
                    price=parse_float(row.get("price")) or 0.0,
                    sale_date=parse_date(row.get("sale_date")),
                    postcode=parse_str(row.get("postcode")),
                    property_type=(
                            parse_str(row.get("property_type"))
                            or parse_str(row.get("property_type_sale"))
                            or parse_str(row.get("property_type_epc"))
                    ),
                    property_type_epc=parse_str(row.get("property_type_epc")),
                    old_new_flag=parse_str(row.get("old_new_flag")),
                    tenure_duration=parse_str(row.get("tenure_duration")),
                    paon=parse_str(row.get("paon")),
                    saon=parse_str(row.get("saon")),
                    street=parse_str(row.get("street")),
                    locality=parse_str(row.get("locality")),
                    town_city=parse_str(row.get("town_city")),
                    district=parse_str(row.get("district")),
                    county=parse_str(row.get("county")),
                    ppd_category_type=parse_str(row.get("ppd_category_type")),
                    record_status=parse_str(row.get("record_status")),
                    lmk_key=parse_str(row.get("lmk_key")),
                    address1=parse_str(row.get("address1")),
                    address2=parse_str(row.get("address2")),
                    address3=parse_str(row.get("address3")),
                    address=parse_str(row.get("address")),
                    local_authority_code=parse_str(row.get("local_authority_code")),
                    local_authority_label=parse_str(row.get("local_authority_label")),
                    posttown=parse_str(row.get("posttown")),
                    built_form=parse_str(row.get("built_form")),
                    tenure=parse_str(row.get("tenure")),
                    current_energy_rating=parse_str(row.get("current_energy_rating")),
                    potential_energy_rating=parse_str(row.get("potential_energy_rating")),
                    current_energy_efficiency=parse_float(row.get("current_energy_efficiency")),
                    potential_energy_efficiency=parse_float(row.get("potential_energy_efficiency")),
                    total_floor_area=parse_float(row.get("total_floor_area")),
                    number_habitable_rooms=parse_float(row.get("number_habitable_rooms")),
                    environment_impact_current=parse_float(row.get("environment_impact_current")),
                    environment_impact_potential=parse_float(row.get("environment_impact_potential")),
                    co2_emissions_current=parse_float(row.get("co2_emissions_current")),
                    energy_consumption_current=parse_float(row.get("energy_consumption_current")),
                    energy_consumption_potential=parse_float(row.get("energy_consumption_potential")),
                    mains_gas_flag=parse_str(row.get("mains_gas_flag")),
                    hotwater_description=parse_str(row.get("hotwater_description")),
                    heating_description=parse_str(row.get("heating_description")),
                    windows_description=parse_str(row.get("windows_description")),
                    walls_description=parse_str(row.get("walls_description")),
                    roof_description=parse_str(row.get("roof_description")),
                    lighting_description=parse_str(row.get("lighting_description")),
                    floor_description=parse_str(row.get("floor_description")),
                    construction_age_band=parse_str(row.get("construction_age_band")),
                    lodgement_date=parse_date(row.get("lodgement_date")),
                    inspection_date=parse_date(row.get("inspection_date")),
                    transaction_type=parse_str(row.get("transaction_type")),
                    uprn=parse_str(row.get("uprn")),
                    latitude=parse_float(row.get("latitude")),
                    longitude=parse_float(row.get("longitude")),
                    region_code=parse_str(row.get("region_code")),
                    country_code=parse_str(row.get("country_code")),
                )
            )

        db.bulk_save_objects(records)
        db.commit()
        print(f"Seeded {len(records):,} records into property_records")
    finally:
        db.close()


if __name__ == "__main__":
    main()