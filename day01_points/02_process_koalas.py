"""
Process Koala Sightings — Gold Coast, Queensland
------------------------------------------------
Prepares koala occurrence records from the Atlas of Living Australia
for Day 1: Points of the 2026 #30DayMapChallenge.

Processing:
1. Load the original occurrence records.
2. Convert coordinates into geographic points.
3. Retain records within the Gold Coast LGA boundary.
4. Select relevant columns.
5. Export the processed dataset.

Input:
    data/koala_sightings_raw.csv
    data/goldcoast_lga.gpkg

Output:
    data/koala_sightings_processed.csv

Note:
    Original data remains unchanged.
    Output coordinates are not yet generalized for public release.
"""

from pathlib import Path
import pandas as pd
import geopandas as gpd

DATA_DIR = Path(__file__).parent / "data"

# Load original data
df = pd.read_csv(DATA_DIR / "koala_sightings_raw.csv", low_memory=False)

# Load Gold Coast LGA boundary
lga = gpd.read_file(DATA_DIR / "goldcoast_lga.gpkg")

# Convert coordinates into geographic points
koalas = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(
        df["decimalLongitude"],
        df["decimalLatitude"]
    ),
    crs="EPSG:4326"
).to_crs(lga.crs)

# Retain records within or on the LGA boundary
inside = koalas.geometry.intersects(lga.geometry.union_all())
koalas = koalas.loc[inside].copy()

# Select relevant columns
cols = [
    "recordID",
    "decimalLatitude",
    "decimalLongitude",
    "eventDate",
    "coordinateUncertaintyInMeters",
    "dataResourceName",
    "dcterms:license"
]

processed = koalas[cols].copy()

# Export processed dataset
output_path = DATA_DIR / "koala_sightings_processed.csv"
processed.to_csv(output_path, index=False)

print(f"Original records: {len(df):,}")
print(f"Processed records: {len(processed):,}")
print(f"Columns retained: {len(processed.columns)}")
print(f"Saved to: {output_path}")