# Day 13 data workflow

The workflow validates the raw NOAA IBTrACS and OISST files and generates two processed track CSVs. The published CSVs are located in `data/`.

## Source downloads

- [NOAA IBTrACS v04r01, last three years (CSV)](https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.last3years.list.v04r01.csv)
- [NOAA OISST v2.1, preliminary (ERDDAP)](https://coastwatch.pfeg.noaa.gov/erddap/griddap/ncdcOisst21NrtAgg.html)
- [NOAA OISST v2.1, final archive (ERDDAP)](https://coastwatch.pfeg.noaa.gov/erddap/griddap/ncdcOisst21Agg.html)

Download the IBTrACS CSV and the OISST subsets before running the workflow. In ERDDAP, select `sst`, a stride of 1 on each axis and NetCDF (`.nc`) output. Use latitude 19.875–45.125°N and longitude 119.875–150.125°E. The [source-file manifest](#original-oisst-files) lists the archive and UTC date range for each original subset. Preserve the filename prefixes and select non-overlapping subsets across the two archives.

The IBTrACS download is a rolling release, and preliminary OISST can be revised or superseded. Exact recreation of the historical outputs depends on the original source versions. Available versions can be processed using the same steps.

## Run the workflow

Requirements are Python 3, R with `readr` and `dplyr`, and the NetCDF command-line utility `ncdump`. The notebook also requires Jupyter with a Python 3 kernel.

Run from the project root with paths to the raw files. The example writes new CSVs to `generated/`. The notebook `04_day13_data_validation.ipynb` runs the same workflow and uses paths configured in its first code cell.

```sh
IBTRACS_CSV="/path/to/ibtracs.last3years.list.v04r01.csv"
OISST_DIR="/path/to/oisst-subsets"

python3 03_validate_typhoon_data.py \
  --ibtracs "$IBTRACS_CSV" \
  --oisst "$OISST_DIR"/ncdcOisst21NrtAgg_*.nc "$OISST_DIR"/ncdcOisst21Agg_*.nc \
  --output-dir generated
```

## Validation and processing

| Stage | Source checks and processing | Output |
| --- | --- | --- |
| IBTrACS | `01_prepare_tracks.R` checks columns and parsing, then checks storm IDs, UTC timestamps, coordinate ranges and non-negative winds for Western Pacific observations in 2024–2026. It reports missing coordinates or winds, filters to 20–45°N, 120–150°E and `USA_WIND` ≥ 64 knots, and checks that retained storm IDs and timestamps are unique in combination. Eligible track types are `main`, `PROVISIONAL` and `US-PROVISIONAL`. | `typhoon_tracks_2024_2026.csv` |
| OISST | `02_match_oisst.R` checks Celsius units, the grid axes and dimensions, valid and non-overlapping UTC dates, and unmasked temperatures in the range −3°C to 45°C. For each retained track point, it selects the nearest 0.25° grid centre on the UTC date and rounds SST to two decimal places. Exact ties use the lower coordinate. Masked cells and dates missing from the source grids are recorded separately. | `typhoon_tracks_oisst_2024_2026.csv` |

The SST export also records the selected grid coordinates and source archive. For the published map, the final archive supplied 15 values across three dates missing from the preliminary subsets: 16 August 2024 and 27–28 July 2025.

## Original OISST files

The dates below are the first and last UTC dates in each downloaded subset. Gaps can occur inside a subset.

| File | Archive | First UTC date | Last UTC date |
| --- | --- | --- | --- |
| `ncdcOisst21Agg_b01e_2b2e_9280_U1794663486031.nc` | Final | 2024-08-16 | 2024-08-16 |
| `ncdcOisst21Agg_fe41_c9c7_df65_U1794663486982.nc` | Final | 2025-07-27 | 2025-07-28 |
| `ncdcOisst21NrtAgg_6f0a_c34c_9dbe_U1794663358668.nc` | Near-real-time | 2025-07-06 | 2025-10-13 |
| `ncdcOisst21NrtAgg_7e2c_1c2b_0b64_U1794663335457.nc` | Near-real-time | 2024-05-28 | 2024-11-15 |
| `ncdcOisst21NrtAgg_88c1_8548_cc79_U1794663390139.nc` | Near-real-time | 2026-08-02 | 2026-10-31 |
| `ncdcOisst21NrtAgg_a42c_4bcf_2c59_U1794663400352.nc` | Near-real-time | 2026-04-17 | 2026-07-31 |
| `ncdcOisst21NrtAgg_e4f1_5c77_664a_U1794663316059.nc` | Near-real-time | 2026-11-01 | 2026-11-11 |
