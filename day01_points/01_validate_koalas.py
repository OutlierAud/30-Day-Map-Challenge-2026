"""
Day 1 — Koala Sightings on the Gold Coast
validate_koalas.py

Data source: Atlas of Living Australia (ALA)
Study period: 1 November 2021 - 31 October 2026

Validate raw koala occurrence records before spatial analysis.

Note:
This script reports data quality issues but does not remove records.
"""

from pathlib import Path
import pandas as pd

DATA_PATH = Path(__file__).parent / "data" / "koala_sightings_raw.csv"

df = pd.read_csv(DATA_PATH, low_memory=False)

print(f"Records: {len(df):,}")
print(f"Columns: {len(df.columns)}")

print("\nColumn names:")
for col in df.columns:
    print(col)

# Check relevant columns
cols = [
    "occurrenceID",
    "decimalLatitude",
    "decimalLongitude",
    "eventDate",
    "scientificName",
    "coordinateUncertaintyInMeters",
]

# Check missing values
print("\nMissing values:")
print(df[cols].isna().sum())

# Check unique identifier
print("\nIdentifier completeness:")
print(df[["occurrenceID", "recordID", "catalogNumber"]].notna().sum())

# Check exact duplicate rows
print("\nExact duplicate rows:")
print(df.duplicated().sum())

# Check duplicate occurrence IDs
print("\nDuplicate occurrence IDs:")
print(df["occurrenceID"].dropna().duplicated().sum())
print("\nDuplicate record IDs:")
print(df["recordID"].dropna().duplicated().sum())

# Check invalid coordinates
invalid_coords = (
    ~df["decimalLatitude"].between(-90, 90)
    | ~df["decimalLongitude"].between(-180, 180)
)

# Check invalid coordinates
print("\nInvalid coordinates:")
print(invalid_coords.sum())

uncertainty = pd.to_numeric(
    df["coordinateUncertaintyInMeters"],
    errors="coerce"
)

print("\nCoordinate uncertainty (metres):")
print(uncertainty.describe())
print("\nRecords with uncertainty > 1,000 m:")
print((uncertainty > 1000).sum())
print("\nRecords with uncertainty > 10,000 m:")
print((uncertainty > 10000).sum())


# Convert observation dates to datetime
dates = pd.to_datetime(df["eventDate"], errors="coerce", utc=True)

print("\nInvalid dates:", dates.isna().sum())
print("Earliest observation:", dates.min())
print("Latest observation:", dates.max())

# Check dates outside our study period
outside_period = ~dates.between(
    "2021-11-01",
    "2026-10-31 23:59:59"
)

print("Records outside study period:", outside_period.sum())

# Check observation times
print("\nObservation time completeness:")
print("Available:", df["eventTime"].notna().sum())
print("Missing:", df["eventTime"].isna().sum())

print("\nSample observation times:")
print(df["eventTime"].dropna().head(10))

# Extract hour from observation time
df["hour"] = pd.to_numeric(
    df["eventTime"].str.slice(0, 2),
    errors="coerce"
)

print("\nSightings by hour:")
print(df["hour"].value_counts().sort_index())


import geopandas as gpd

# Load Gold Coast LGA boundary
boundary_path = Path(__file__).parent / "data" / "goldcoast_lga.gpkg"
lga = gpd.read_file(boundary_path)

# Convert koala coordinates into geographic points
koalas = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(
        df["decimalLongitude"],
        df["decimalLatitude"]
    ),
    crs="EPSG:4326"
)

# Match the boundary's coordinate reference system
koalas = koalas.to_crs(lga.crs)

# Check whether each point falls within the LGA
inside = koalas.geometry.intersects(lga.geometry.union_all())

print("\nSpatial validation:")
print("Inside Gold Coast LGA:", inside.sum())
print("Outside Gold Coast LGA:", (~inside).sum())

outside = koalas.loc[~inside].copy()

outside["distance_m"] = outside.geometry.distance(
    lga.geometry.union_all()
)

print("\nRecords outside Gold Coast LGA:")
print(outside[
    [
        "recordID",
        "decimalLatitude",
        "decimalLongitude",
        "coordinateUncertaintyInMeters",
        "distance_m"
    ]
].to_string(index=False))