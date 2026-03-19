from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import pandas as pd


# =========================
# CONFIG
# =========================
PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

NSPL_FILE = RAW_DIR / "NSPL_FEB_2026_UK.csv"
EPC_ROOT = RAW_DIR / "all-domestic-certificates"
PRICE_PAID_FILE = RAW_DIR / "pp-complete.csv"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Keep recent years only
PRICE_PAID_START_DATE = "2020-01-01"

# Restrict to major cities only
TARGET_CITIES = {
    "LONDON",
    "MANCHESTER",
    "BIRMINGHAM",
    "LEEDS",
    "LIVERPOOL",
    "BRISTOL",
}

# Chunk sizes
PRICE_PAID_CHUNKSIZE = 200_000
MERGE_CHUNKSIZE = 200_000


# =========================
# HELPERS
# =========================
def print_step(message: str) -> None:
    print(f"\n=== {message} ===")


def read_csv_flexible(path: Path, **kwargs) -> pd.DataFrame:
    try:
        return pd.read_csv(path, low_memory=False, **kwargs)
    except UnicodeDecodeError:
        return pd.read_csv(path, low_memory=False, encoding="latin-1", **kwargs)


def normalise_postcode(value) -> Optional[str]:
    if pd.isna(value):
        return None
    text = str(value).strip().upper()
    if not text or text in {"NAN", "NONE", "NULL"}:
        return None
    text = re.sub(r"\s+", "", text)
    if len(text) >= 5:
        text = f"{text[:-3]} {text[-3:]}"
    return text


def normalise_text(value) -> Optional[str]:
    if pd.isna(value):
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.upper() in {"NODATA!", "NO DATA!", "NAN", "NULL", "NONE"}:
        return None
    return text


def normalise_lmk(value) -> Optional[str]:
    if pd.isna(value):
        return None
    text = str(value).strip()
    if not text or text.upper() in {"NAN", "NULL", "NONE"}:
        return None
    return text


def safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def safe_date(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")


def remove_if_exists(path: Path) -> None:
    if path.exists():
        path.unlink()


def append_df_to_csv(df: pd.DataFrame, output_path: Path, first_write: bool) -> bool:
    df.to_csv(output_path, mode="w" if first_write else "a", header=first_write, index=False)
    return False


def build_sales_postcode_set(price_paid_path: Path) -> set[str]:
    if not price_paid_path.exists():
        raise FileNotFoundError(f"Missing filtered price-paid file: {price_paid_path}")

    df = read_csv_flexible(price_paid_path, usecols=["postcode"])
    df["postcode"] = df["postcode"].map(normalise_postcode)
    return set(df["postcode"].dropna().unique())


def build_filtered_lmk_set(certificates_path: Path) -> set[str]:
    if not certificates_path.exists():
        raise FileNotFoundError(f"Missing filtered certificates file: {certificates_path}")

    df = read_csv_flexible(certificates_path, usecols=["lmk_key"])
    df["lmk_key"] = df["lmk_key"].map(normalise_lmk)
    return set(df["lmk_key"].dropna().unique())


# =========================
# NSPL CLEANING
# =========================
def clean_nspl() -> Path:
    print_step("Cleaning NSPL")

    if not NSPL_FILE.exists():
        raise FileNotFoundError(f"NSPL file not found: {NSPL_FILE}")

    header_df = read_csv_flexible(NSPL_FILE, nrows=0)
    original_cols = list(header_df.columns)
    lower_map = {c.lower(): c for c in original_cols}

    required_lower = ["pcds", "lat", "long", "lad25cd", "rgn25cd", "ctry25cd"]
    missing = [c for c in required_lower if c not in lower_map]
    if missing:
        raise ValueError(
            f"NSPL file is missing expected columns: {missing}\n"
            f"Actual columns found: {original_cols[:50]}"
        )

    usecols = [lower_map[c] for c in required_lower]
    df = read_csv_flexible(NSPL_FILE, usecols=usecols)

    df = df.rename(columns={
        lower_map["pcds"]: "postcode",
        lower_map["lat"]: "latitude",
        lower_map["long"]: "longitude",
        lower_map["lad25cd"]: "local_authority_code",
        lower_map["rgn25cd"]: "region_code",
        lower_map["ctry25cd"]: "country_code",
    })

    df["postcode"] = df["postcode"].map(normalise_postcode)
    df["latitude"] = safe_numeric(df["latitude"])
    df["longitude"] = safe_numeric(df["longitude"])

    for col in ["local_authority_code", "region_code", "country_code"]:
        df[col] = df[col].map(normalise_text)

    df = df.dropna(subset=["postcode"])
    df = df.drop_duplicates(subset=["postcode"], keep="first")

    output_path = PROCESSED_DIR / "nspl_clean.csv"
    remove_if_exists(output_path)
    df.to_csv(output_path, index=False)

    print(f"Saved NSPL cleaned file: {output_path}")
    print(f"Rows: {len(df):,}")
    return output_path


# =========================
# EPC FILE DISCOVERY
# =========================
def find_epc_csvs(epc_root: Path) -> tuple[list[Path], list[Path]]:
    cert_files: list[Path] = []
    rec_files: list[Path] = []

    for subdir in sorted(epc_root.iterdir()):
        if not subdir.is_dir():
            continue

        cert_path = subdir / "certificates.csv"
        rec_path = subdir / "recommendations.csv"

        if cert_path.exists():
            cert_files.append(cert_path)
        if rec_path.exists():
            rec_files.append(rec_path)

    return cert_files, rec_files


# =========================
# PRICE PAID CLEANING
# =========================
def clean_price_paid() -> Path | None:
    print_step(f"Cleaning Price Paid data (from {PRICE_PAID_START_DATE} onward, major cities only)")

    if not PRICE_PAID_FILE.exists():
        print(f"Price Paid file not found at {PRICE_PAID_FILE}, skipping.")
        return None

    col_names = [
        "transaction_unique_identifier",
        "price",
        "date_of_transfer",
        "postcode",
        "property_type",
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

    output_path = PROCESSED_DIR / "price_paid_clean.csv"
    remove_if_exists(output_path)

    first_write = True
    total_rows_written = 0
    start_date = pd.Timestamp(PRICE_PAID_START_DATE)

    for chunk_no, chunk in enumerate(
        pd.read_csv(
            PRICE_PAID_FILE,
            header=None,
            names=col_names,
            chunksize=PRICE_PAID_CHUNKSIZE,
            low_memory=False,
        ),
        start=1,
    ):
        print(f"Processing price-paid chunk {chunk_no}")

        chunk["postcode"] = chunk["postcode"].map(normalise_postcode)
        chunk["price"] = safe_numeric(chunk["price"])
        chunk["date_of_transfer"] = safe_date(chunk["date_of_transfer"])

        for col in [
            "transaction_unique_identifier", "property_type", "old_new", "duration",
            "paon", "saon", "street", "locality", "town_city", "district",
            "county", "ppd_category_type", "record_status"
        ]:
            chunk[col] = chunk[col].map(normalise_text)

        chunk = chunk.dropna(subset=["postcode", "price", "date_of_transfer", "town_city"])
        chunk = chunk[chunk["date_of_transfer"] >= start_date]

        chunk["town_city_upper"] = chunk["town_city"].str.upper()
        chunk = chunk[chunk["town_city_upper"].isin(TARGET_CITIES)]
        chunk = chunk.drop(columns=["town_city_upper"])

        chunk = chunk[[
            "transaction_unique_identifier",
            "price",
            "date_of_transfer",
            "postcode",
            "property_type",
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
        ]]

        first_write = append_df_to_csv(chunk, output_path, first_write)
        total_rows_written += len(chunk)

    print(f"Saved Price Paid cleaned file: {output_path}")
    print(f"Rows written: {total_rows_written:,}")
    return output_path


# =========================
# EPC CERTIFICATES CLEANING
# =========================
def clean_certificates(filtered_postcodes: set[str]) -> Path:
    print_step("Cleaning EPC certificates (major-city sales postcodes only)")

    if not EPC_ROOT.exists():
        raise FileNotFoundError(f"EPC root folder not found: {EPC_ROOT}")

    cert_files, _ = find_epc_csvs(EPC_ROOT)
    if not cert_files:
        raise FileNotFoundError(f"No certificates.csv files found in {EPC_ROOT}")

    keep_cols = [
        "LMK_KEY",
        "POSTCODE",
        "ADDRESS1",
        "ADDRESS2",
        "ADDRESS3",
        "ADDRESS",
        "LOCAL_AUTHORITY",
        "LOCAL_AUTHORITY_LABEL",
        "POSTTOWN",
        "COUNTY",
        "PROPERTY_TYPE",
        "BUILT_FORM",
        "TENURE",
        "CURRENT_ENERGY_RATING",
        "POTENTIAL_ENERGY_RATING",
        "CURRENT_ENERGY_EFFICIENCY",
        "POTENTIAL_ENERGY_EFFICIENCY",
        "TOTAL_FLOOR_AREA",
        "NUMBER_HABITABLE_ROOMS",
        "ENVIRONMENT_IMPACT_CURRENT",
        "ENVIRONMENT_IMPACT_POTENTIAL",
        "CO2_EMISSIONS_CURRENT",
        "ENERGY_CONSUMPTION_CURRENT",
        "ENERGY_CONSUMPTION_POTENTIAL",
        "MAINS_GAS_FLAG",
        "HOTWATER_DESCRIPTION",
        "HEATING_DESCRIPTION",
        "WINDOWS_DESCRIPTION",
        "WALLS_DESCRIPTION",
        "ROOF_DESCRIPTION",
        "LIGHTING_DESCRIPTION",
        "FLOOR_DESCRIPTION",
        "CONSTRUCTION_AGE_BAND",
        "LODGEMENT_DATE",
        "INSPECTION_DATE",
        "TRANSACTION_TYPE",
        "UPRN",
    ]

    output_path = PROCESSED_DIR / "certificates_clean.csv"
    remove_if_exists(output_path)

    first_write = True
    total_rows_written = 0

    for i, file_path in enumerate(cert_files, start=1):
        print(f"[{i}/{len(cert_files)}] Reading {file_path.name} from {file_path.parent.name}")

        df = read_csv_flexible(file_path, usecols=lambda c: c in keep_cols)

        for col in keep_cols:
            if col not in df.columns:
                df[col] = pd.NA

        df = df[keep_cols].copy()
        df.columns = [c.lower() for c in df.columns]

        df = df.rename(columns={
            "local_authority": "local_authority_code",
            "local_authority_label": "local_authority_label",
        })

        df["lmk_key"] = df["lmk_key"].map(normalise_lmk)
        df["postcode"] = df["postcode"].map(normalise_postcode)

        df = df[df["postcode"].isin(filtered_postcodes)]

        text_cols = [
            "address1", "address2", "address3", "address",
            "local_authority_code", "local_authority_label",
            "posttown", "county", "property_type", "built_form", "tenure",
            "current_energy_rating", "potential_energy_rating",
            "mains_gas_flag", "hotwater_description", "heating_description",
            "windows_description", "walls_description", "roof_description",
            "lighting_description", "floor_description",
            "construction_age_band", "transaction_type", "uprn",
        ]
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].map(normalise_text)

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
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = safe_numeric(df[col])

        if "lodgement_date" in df.columns:
            df["lodgement_date"] = safe_date(df["lodgement_date"])
        if "inspection_date" in df.columns:
            df["inspection_date"] = safe_date(df["inspection_date"])

        df = df.dropna(subset=["lmk_key", "postcode"])
        df = df.drop_duplicates(subset=["lmk_key"], keep="first")

        first_write = append_df_to_csv(df, output_path, first_write)
        total_rows_written += len(df)

    print(f"Saved certificates cleaned file: {output_path}")
    print(f"Rows written: {total_rows_written:,}")
    return output_path


# =========================
# EPC RECOMMENDATIONS CLEANING
# =========================
def clean_recommendations(filtered_lmk_keys: set[str]) -> Path:
    print_step("Cleaning EPC recommendations (filtered LMK keys only)")

    if not EPC_ROOT.exists():
        raise FileNotFoundError(f"EPC root folder not found: {EPC_ROOT}")

    _, rec_files = find_epc_csvs(EPC_ROOT)
    if not rec_files:
        raise FileNotFoundError(f"No recommendations.csv files found in {EPC_ROOT}")

    keep_cols = [
        "LMK_KEY",
        "IMPROVEMENT_ITEM",
        "IMPROVEMENT_SUMMARY_TEXT",
        "IMPROVEMENT_DESCR_TEXT",
        "IMPROVEMENT_ID_TEXT",
        "INDICATIVE_COST",
    ]

    output_path = PROCESSED_DIR / "recommendations_clean.csv"
    remove_if_exists(output_path)

    first_write = True
    total_rows_written = 0

    for i, file_path in enumerate(rec_files, start=1):
        print(f"[{i}/{len(rec_files)}] Reading {file_path.name} from {file_path.parent.name}")

        df = read_csv_flexible(file_path, usecols=lambda c: c in keep_cols)

        for col in keep_cols:
            if col not in df.columns:
                df[col] = pd.NA

        df = df[keep_cols].copy()
        df.columns = [c.lower() for c in df.columns]

        df["lmk_key"] = df["lmk_key"].map(normalise_lmk)
        df = df[df["lmk_key"].isin(filtered_lmk_keys)]

        df["improvement_item"] = safe_numeric(df["improvement_item"])

        for col in [
            "improvement_summary_text",
            "improvement_descr_text",
            "improvement_id_text",
            "indicative_cost",
        ]:
            if col in df.columns:
                df[col] = df[col].map(normalise_text)

        df = df.dropna(subset=["lmk_key"])

        first_write = append_df_to_csv(df, output_path, first_write)
        total_rows_written += len(df)

    print(f"Saved recommendations cleaned file: {output_path}")
    print(f"Rows written: {total_rows_written:,}")
    return output_path


# =========================
# MERGE CERTIFICATES + NSPL
# =========================
def build_certificates_with_location() -> Path:
    print_step("Building certificates + NSPL merged file")

    cert_path = PROCESSED_DIR / "certificates_clean.csv"
    nspl_path = PROCESSED_DIR / "nspl_clean.csv"

    if not cert_path.exists():
        raise FileNotFoundError(f"Certificates cleaned file not found: {cert_path}")
    if not nspl_path.exists():
        raise FileNotFoundError(f"NSPL cleaned file not found: {nspl_path}")

    nspl_df = read_csv_flexible(nspl_path)
    output_path = PROCESSED_DIR / "certificates_with_location.csv"
    remove_if_exists(output_path)

    first_write = True
    total_rows_written = 0

    for chunk_no, cert_chunk in enumerate(
        pd.read_csv(cert_path, chunksize=MERGE_CHUNKSIZE, low_memory=False),
        start=1
    ):
        print(f"Merging certificate chunk {chunk_no}")

        cert_chunk["postcode"] = cert_chunk["postcode"].map(normalise_postcode)
        merged = cert_chunk.merge(nspl_df, how="left", on="postcode")

        first_write = append_df_to_csv(merged, output_path, first_write)
        total_rows_written += len(merged)

    print(f"Saved merged file: {output_path}")
    print(f"Rows written: {total_rows_written:,}")
    return output_path


# =========================
# MAIN
# =========================
def main() -> None:
    print_step("START CLEANING PIPELINE")

    nspl_clean = clean_nspl()
    price_paid_clean = clean_price_paid()

    if not price_paid_clean:
        raise RuntimeError("price_paid_clean.csv was not generated.")

    filtered_postcodes = build_sales_postcode_set(price_paid_clean)
    print(f"Filtered sales postcodes: {len(filtered_postcodes):,}")

    certificates_clean = clean_certificates(filtered_postcodes=filtered_postcodes)

    filtered_lmk_keys = build_filtered_lmk_set(certificates_clean)
    print(f"Filtered LMK keys: {len(filtered_lmk_keys):,}")

    recommendations_clean = clean_recommendations(filtered_lmk_keys=filtered_lmk_keys)
    merged_file = build_certificates_with_location()

    print_step("DONE")
    print("Generated files:")
    print(f" - {nspl_clean}")
    print(f" - {price_paid_clean}")
    print(f" - {certificates_clean}")
    print(f" - {recommendations_clean}")
    print(f" - {merged_file}")


if __name__ == "__main__":
    main()