from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PRICE_PAID_PATH = PROCESSED_DIR / "price_paid_clean.csv"
CERTS_LOC_PATH = PROCESSED_DIR / "certificates_with_location.csv"
OUTPUT_PATH = PROCESSED_DIR / "property_records.csv"


def load_csv(path: Path, **kwargs) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return pd.read_csv(path, low_memory=False, **kwargs)


def normalise_text_value(value) -> Optional[str]:
    if pd.isna(value):
        return None
    text = str(value).strip()
    if not text or text.upper() in {"NAN", "NONE", "NULL"}:
        return None
    return text


def normalise_postcode_value(value) -> Optional[str]:
    if pd.isna(value):
        return None
    text = str(value).strip().upper()
    if not text or text in {"NAN", "NONE", "NULL"}:
        return None
    return text


def safe_date(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")


def safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def normalise_dataframe(df: pd.DataFrame, postcode_col: str, property_type_col: str) -> pd.DataFrame:
    df = df.copy()

    if postcode_col in df.columns:
        df[postcode_col] = df[postcode_col].map(normalise_postcode_value)

    if property_type_col in df.columns:
        df[property_type_col] = (
            df[property_type_col]
            .map(normalise_text_value)
            .str.upper()
        )

    return df


def prepare_sales(df: pd.DataFrame) -> pd.DataFrame:
    df = normalise_dataframe(df, postcode_col="postcode", property_type_col="property_type")

    if "date_of_transfer" in df.columns:
        df["date_of_transfer"] = safe_date(df["date_of_transfer"])

    if "price" in df.columns:
        df["price"] = safe_numeric(df["price"])

    text_cols = [
        "transaction_unique_identifier",
        "old_new",
        "duration",
        "paon",
        "saon",
        "street",
        "locality",
        "town_city",
        "district",
        "county",
        "ppd_category_type",
        "record_status",
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].map(normalise_text_value)

    df = df.dropna(subset=["postcode", "property_type", "price"])
    return df


def prepare_epc(df: pd.DataFrame) -> pd.DataFrame:
    df = normalise_dataframe(df, postcode_col="postcode", property_type_col="property_type")

    date_cols = ["lodgement_date", "inspection_date"]
    for col in date_cols:
        if col in df.columns:
            df[col] = safe_date(df[col])

    numeric_cols = [
        "current_energy_efficiency",
        "potential_energy_efficiency",
        "total_floor_area",
        "number_habitable_rooms",
        "environment_impact_current",
        "environment_impact_potential",
        "co2_emissions_current",
        "energy_consumption_current",
        "energy_consumption_potential",
        "latitude",
        "longitude",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = safe_numeric(df[col])

    text_cols = [
        "lmk_key",
        "address1",
        "address2",
        "address3",
        "address",
        "local_authority_code",
        "local_authority_label",
        "posttown",
        "county",
        "built_form",
        "tenure",
        "current_energy_rating",
        "potential_energy_rating",
        "mains_gas_flag",
        "hotwater_description",
        "heating_description",
        "windows_description",
        "walls_description",
        "roof_description",
        "lighting_description",
        "floor_description",
        "construction_age_band",
        "transaction_type",
        "uprn",
        "region_code",
        "country_code",
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].map(normalise_text_value)

    df = df.dropna(subset=["postcode", "property_type"])

    # Keep the latest EPC per postcode
    sort_cols = ["postcode"]
    if "lodgement_date" in df.columns:
        df = df.sort_values(
            by=sort_cols + ["lodgement_date"],
            ascending=[True, False],
        )

    df = df.drop_duplicates(subset=["postcode"], keep="first")
    return df


def main() -> None:
    print("Loading cleaned datasets...")
    sales = load_csv(PRICE_PAID_PATH)
    epc = load_csv(CERTS_LOC_PATH)

    print("Preparing sales data...")
    sales = prepare_sales(sales)

    print("Preparing EPC/location data...")
    epc = prepare_epc(epc)

    print(f"Sales rows after cleaning: {len(sales):,}")
    print(f"EPC rows after reduction: {len(epc):,}")

    print("Merging sales with EPC/location data...")
    merged = sales.merge(
        epc,
        how="left",
        on=["postcode"],
        suffixes=("_sale", "_epc"),
    )

    # Track whether a match happened
    merged["merge_match_flag"] = merged["lmk_key"].notna()

    print("Renaming fields for API use...")
    rename_map = {
        "transaction_unique_identifier": "transaction_id",
        "date_of_transfer": "sale_date",
        "old_new": "old_new_flag",
        "duration": "tenure_duration",
    }
    merged = merged.rename(columns=rename_map)

    # Prefer sales-side county, but keep EPC county if useful
    if "county_sale" in merged.columns and "county" not in merged.columns:
        merged = merged.rename(columns={"county_sale": "county"})

    # Final selected columns for API/database
    keep_cols = [
        "transaction_id",
        "price",
        "sale_date",
        "postcode",
        "property_type_sale",
        "property_type_epc",
        "old_new_flag",
        "tenure_duration",
        "paon",
        "saon",
        "street",
        "locality",
        "town_city",
        "district",
        "county",
        "ppd_category_type",
        "record_status",
        "merge_match_flag",
        "lmk_key",
        "address1",
        "address2",
        "address3",
        "address",
        "local_authority_code",
        "local_authority_label",
        "posttown",
        "built_form",
        "tenure",
        "current_energy_rating",
        "potential_energy_rating",
        "current_energy_efficiency",
        "potential_energy_efficiency",
        "total_floor_area",
        "number_habitable_rooms",
        "environment_impact_current",
        "environment_impact_potential",
        "co2_emissions_current",
        "energy_consumption_current",
        "energy_consumption_potential",
        "mains_gas_flag",
        "hotwater_description",
        "heating_description",
        "windows_description",
        "walls_description",
        "roof_description",
        "lighting_description",
        "floor_description",
        "construction_age_band",
        "lodgement_date",
        "inspection_date",
        "transaction_type",
        "uprn",
        "latitude",
        "longitude",
        "region_code",
        "country_code",
    ]

    existing_cols = [c for c in keep_cols if c in merged.columns]
    merged = merged[existing_cols].copy()

    print("Cleaning null-like values...")
    merged = merged.replace(
        {
            "nan": pd.NA,
            "None": pd.NA,
            "": pd.NA,
        }
    )

    # Optional: sort final data for nicer inspection
    sort_output_cols = [c for c in ["town_city", "district", "postcode", "sale_date"] if c in merged.columns]
    if sort_output_cols:
        merged = merged.sort_values(by=sort_output_cols)

    print(f"Saving merged dataset to: {OUTPUT_PATH}")
    merged.to_csv(OUTPUT_PATH, index=False)

    total_rows = len(merged)
    matched_rows = int(merged["merge_match_flag"].sum()) if "merge_match_flag" in merged.columns else 0
    unmatched_rows = total_rows - matched_rows

    print("Done.")
    print(f"Rows: {total_rows:,}")
    print(f"Columns: {len(merged.columns)}")
    print(f"Matched EPC rows: {matched_rows:,}")
    print(f"Unmatched sales rows: {unmatched_rows:,}")


if __name__ == "__main__":
    main()