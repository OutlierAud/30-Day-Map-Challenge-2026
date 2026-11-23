# 30 Day Map Challenge | Day 13
### 13 November 2026 | Interactions

## Jump To

- [Dataset](#dataset)
- [Methodology & Tools](#methodology--tools)
- [Data validation and processed outputs](#data-validation-and-processed-outputs)
- [Key Insights](#key-insights)
- [Reflection](#reflection)
- [File Structure](#file-structure)
- [References](#references)

## Typhoon Tracks and Ocean Temperatures
#### How did typhoon paths and wind strength vary from 2024 to 2026?

Where did typhoons change direction or strengthen? What were the sea surface temperatures along their paths? How does the picture change when I look beyond June–September?

The interactive map displays typhoon tracks and daily sea surface temperature (SST) in the western North Pacific. Controls select the year and date window, play the animation, scrub through the timeline or toggle the SST layer. Track-point tooltips show the UTC timestamp, maximum sustained wind speed and matched SST.

[Open the interactive map](https://wnptyphoonsst.netlify.app/)

## Dataset

### Data Sources

**1. NOAA International Best Track Archive for Climate Stewardship (IBTrACS), v04r01**

- Map extent covers 120°–150°E and 20°–45°N in the western North Pacific.
- The map includes observations where the IBTrACS `USA_WIND` field reports maximum sustained winds of at least 64 knots.
- The three years are 2024, 2025 and 2026. The latest included 2026 track observation is 11 November 2026 at 03:00 UTC. Track records for 2025 and 2026 are provisional.

**2. NOAA Daily Optimum Interpolation Sea Surface Temperature (OISST), v2.1**

- Daily SST in °C on a 0.25° grid. Point matches use the near-real-time archive, with 15 values taken from the final archive across three dates.

**3. Natural Earth**

- Shaded relief and coastline boundaries provide geographic context.

### Data Considerations

“All available months” runs from the first to the last qualifying track date in each year. A storm is counted once per year if it has at least one qualifying observation in the selected window. Counts apply to the map extent and wind threshold, so basin-wide totals and comparisons based on equal observation periods require a different analysis. A track can first appear when the storm enters the map or reaches 64 knots, after it has already formed.

## Methodology & Tools

**Tools** · R for source validation, track preparation and SST matching. Python for running the workflow and rendering the background. D3.js for the interactive map.

1. Validate the raw IBTrACS track records and filter to the study area, years and wind threshold.
2. Validate the raw OISST grids and match each retained track point by UTC calendar date to the nearest grid cell. Keep track points with missing SST and record the match status.
3. Display the daily ocean layer in 2°C bands. Interpolation smooths the display of the original 0.25° grid.
4. Draw track width and point size by wind band (64–79, 80–99 and 100+ knots). Each segment uses the wind recorded at its endpoint. Leave gaps longer than six hours open.

### Data validation and processed outputs

The IBTrACS checks cover required fields, parsing, storm IDs, timestamps, coordinates and wind values for observations in the study years and basin. The OISST checks cover temperature units and range, grid coordinates and dimensions, and unique UTC dates. [Data workflow](DATA_WORKFLOW.md) lists the source files and commands.

The published processing run retained 520 track points. Of these, 511 matched an SST value from 19.42°C to 31.37°C, and nine fell in masked cells.

| Year | Storms, all available months | Track observations | Matched SST | Masked SST |
| --- | ---: | ---: | ---: | ---: |
| 2024 | 10 | 146 | 141 | 5 |
| 2025 | 5 | 59 | 57 | 2 |
| 2026 | 13 | 315 | 313 | 2 |
| **Total** | **28** | **520** | **511** | **9** |

## Key Insights

- The map shows 13 qualifying storms in 2026 through 11 November, compared with 10 in 2024 and five in 2025 across all available months. For June–September, the counts are seven, six and three respectively.
- The timeline and wind bands make it easier to follow changes in direction and strength as the tracks build. 
- The map provides a starting point for comparing paths and the ocean conditions storms travelled through.

## Reflection

Ocean colour represents temperature and line width represents wind strength. The map displays the portion of each track that falls within the location and wind criteria. Full track length requires the unfiltered observations.

## File Structure

- [`DATA_WORKFLOW.md`](DATA_WORKFLOW.md) — source files, processing steps and reproduction commands
- [`04_day13_data_validation.ipynb`](04_day13_data_validation.ipynb) and [`03_validate_typhoon_data.py`](03_validate_typhoon_data.py) — raw-data validation and processing entry points
- [`01_prepare_tracks.R`](01_prepare_tracks.R) and [`02_match_oisst.R`](02_match_oisst.R) — track preparation and SST matching
- [`05_extract_ocean_grids.R`](05_extract_ocean_grids.R) and [`06_render_ocean_frames.py`](06_render_ocean_frames.py) — daily ocean background preparation

- `README.md` — project notes and data validation summary
- [`typhoon_sst_animation.html`](typhoon_sst_animation.html) — interactive map with embedded data
- [`data/typhoon_tracks_2024_2026.csv`](data/typhoon_tracks_2024_2026.csv) — filtered track observations
- [`data/typhoon_tracks_oisst_2024_2026.csv`](data/typhoon_tracks_oisst_2024_2026.csv) — track observations with SST matches and match status

## References

- [NOAA IBTrACS](https://www.ncei.noaa.gov/products/international-best-track-archive)
- [NOAA OISST v2.1](https://www.ncei.noaa.gov/products/optimum-interpolation-sst)
- [NOAA ENSO advisories](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_advisory/)
- [Natural Earth shaded relief](https://www.naturalearthdata.com/downloads/50m-raster-data/50m-natural-earth-1/)
