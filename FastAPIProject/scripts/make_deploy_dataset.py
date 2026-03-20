from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "property_records.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "property_records_deploy.csv"

TARGET_CITIES = {"LEEDS", "MANCHESTER", "BIRMINGHAM", "LONDON"}
START_DATE = "2022-01-01"
MAX_ROWS = 100_000
MAX_ROWS_PER_CITY = 30000

df = pd.read_csv(INPUT_PATH, low_memory=False)

df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
df["town_city_upper"] = df["town_city"].astype(str).str.upper().str.strip()

df = df[df["sale_date"] >= pd.Timestamp(START_DATE)]
df = df[df["town_city_upper"].isin(TARGET_CITIES)]
df = df.drop(columns=["town_city_upper"])

# Optional: keep newest rows first
df = df.sort_values(by="sale_date", ascending=False)

# Optional cap for deployment
if len(df) > MAX_ROWS:
    df = df.head(MAX_ROWS)

df.to_csv(OUTPUT_PATH, index=False)

print(f"Saved deploy dataset to: {OUTPUT_PATH}")
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")