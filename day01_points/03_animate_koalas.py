import numpy as np
import pandas as pd

# Load processed sightings
df = pd.read_csv(
    "day01_points/data/koala_sightings_processed.csv"
)

# Reproducible random order
rng = np.random.default_rng(42)
df["animation_order"] = rng.permutation(len(df))

# Assign artificial timestamps across 5 seconds
start = pd.Timestamp("2026-01-01 00:00:00")

df["animation_time"] = (
    start
    + pd.to_timedelta(
        df["animation_order"] / len(df) * 5,
        unit="s"
    )
)

# Save animation dataset
df.to_csv(
    "day01_points/data/koala_sightings_animation.csv",
    index=False
)

print(f"Prepared {len(df):,} sightings for animation.")