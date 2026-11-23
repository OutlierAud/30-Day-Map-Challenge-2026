# 30 Day Map Challenge | Day 02
### 2 November 2026 | Lines: A Map Challenge Classic

## Jump To

- [Dataset](#dataset)
- [Methodology & Tools](#methodology--tools)
- [Key Insights](#key-insights)
- [Reflection](#reflection)
- [File Structure](#file-structure)
- [References](#references)

## Singapore, Connected
#### Picturing the city-state’s migrant origins and destinations

* Where do the largest migrant populations in Singapore come from?
* Where do the largest migrant populations originating from Singapore live?
* Which countries or areas appear among the top 10 in both directions?

This map will show Singapore’s top 10 migrant origins and top 10 migrant destinations using mid-2024 population estimates.

The lines represent relationships between origins and destinations, not actual travel routes. Where both directions involve the same country or area, separate curves will be used where possible to reduce overlap.

This project is an exploration of line mapping, spatial patterns, and cartographic design using Python and Kepler.gl.

## Dataset

### Data Sources

**1. United Nations — International Migrant Stock 2024**

Estimates of international migrant populations by origin and destination.

- Source: United Nations, Department of Economic and Social Affairs, Population Division
- Dataset: International Migrant Stock 2024, destination-and-origin workbook
- Worksheet: Table 1
- Local filename: `migrantstock_raw.xlsx`
- Geographic extent: Worldwide, with Singapore as the focal origin or destination
- Reference date: 1 July 2024
- Population measure: Estimated number of international migrants, both sexes combined
- Map selection: Top 10 origins of migrants living in Singapore and top 10 destinations of migrants originating from Singapore
- Dataset: https://www.un.org/development/desa/pd/content/international-migrant-stock

The original workbook is retained unchanged. Table 1 contains country/area pairs alongside regional and other aggregate records. The `Migrant notes` worksheet provides definitions and coverage notes.

**2. Natural Earth — Country Coordinates**

Representative locations were taken from the `LABEL_X` (longitude) and `LABEL_Y` (latitude) fields in Natural Earth’s 1:10m Admin 0 Countries dataset.

UN location codes were matched to Natural Earth’s `UN_A3` codes. Taiwan was explicitly matched to Natural Earth’s `TWN` record because its UN code was not available as a matching value in that source.

These coordinates anchor connections for display; they are not individual residential locations, movement endpoints, or calculated population centres. Natural Earth’s boundaries and names do not replace the UN dataset’s country/area definitions.

**3. World Basemap**

A muted world basemap will provide geographic context in Kepler.gl. The final basemap provider and required attribution will be recorded after selection.

### Data Considerations

**Migrant Populations, Not Annual Flows**

Migrant stock measures the number of migrants living in a destination at a particular date. It does not measure how many people arrived or departed during 2024.

Connections towards and away from Singapore will therefore be labelled as migrant origins and destinations rather than annual inflows and outflows. Changes in migrant stock between dates should not be interpreted directly as migration flows. The data do not establish migration motives or intermediate countries of residence.

**Origin and Citizenship**

Origin is generally based on country of birth; citizenship is used where birthplace data are unavailable. Singapore’s destination records have data type `B`, indicating estimates based on the foreign-born population. Other destinations may use different definitions, as documented in the workbook notes.

Migrants originating from Singapore are not necessarily Singapore citizens. Similarly, migrants living in Singapore are not necessarily foreign citizens. These figures are not presented as citizenship totals.

**Coverage and Comparability**

The top 10 lists were ranked independently. Both endpoint location codes were required to be below `900` to exclude World, regional aggregates, and development or income groups from country/area rankings.

World totals and six broad geographic regions were retained in the original `migration` DataFrame for summary analysis. These aggregates are excluded from the map connections.

Each connection’s percentage uses the corresponding World total as its denominator, not the combined top 10 population. Missing or suppressed values must not be treated as zero; none were found in the five selected analysis columns.

Asterisks were removed from processed display names, with the original names and notes retained in the raw workbook. Estimates may draw on different national sources and methods.

**Licensing and Attribution**

The workbook identifies its licence as Creative Commons Attribution 3.0 IGO (CC BY 3.0 IGO). Natural Earth data are in the public domain. The sources are credited below; basemap attribution will be added when selected.

## Methodology & Tools

**Data processing:** Python (pandas), Jupyter notebook, openpyxl for Excel reading  
**Coordinate preparation:** Python and Natural Earth country label coordinates  
**Planned mapping:** Kepler.gl

1. **Inspect the workbook:** List worksheets and identify Table 1 as the origin–destination table. Read the column headings from Excel row 11 using `header=10`.
2. **Select relevant columns:** Create a separate `migration` DataFrame containing destination, destination code, origin, origin code, and the both-sexes 2024 population estimate. Keep the original loaded DataFrame unchanged.
3. **Validate the data:** Check missing values, duplicate origin–destination pairs, numeric population values, and negative counts.
4. **Summarise the context:** Report Singapore’s World totals and broad regional breakdowns for both directions.
5. **Filter Singapore connections:** Keep records where Singapore is the origin or destination, then exclude aggregate codes from country/area rankings.
6. **Rank and calculate shares:** Select the 10 largest populations in each direction, add a direction field, and calculate each connection’s percentage of its corresponding World total.
7. **Prepare mapping data:** Remove asterisks from display names, export the processed CSV, and add origin and destination latitude/longitude columns using Natural Earth label points.
8. **Cartographic design — planned:** Use teal for origins connecting towards Singapore and orange for destinations connecting away from Singapore. Scale line width to population using one shared scale, reinforcing direction through the legend and arrowheads where supported.
9. **Final map — planned:** Refine labels, overlapping connections, visual hierarchy, and composition before exporting the completed visualization.

The notebook documents the inspection, validation, filtering, ranking, and summary calculations. Coordinate enrichment was performed separately; the map-ready CSV is retained alongside the notebook’s processed output.

### Data Validation Summary

The selected analysis table contains **28,030 origin–destination records**, including aggregate records.

Validation identified:

- No missing values in the five selected analysis columns.
- No duplicate origin–destination code pairs.
- No non-numeric 2024 population values.
- No negative 2024 population values.
- Exactly 10 selected connections in each direction.
- Coordinates available for all 20 selected connections, with latitude and longitude within valid ranges.

Population counts, direction labels, and percentages were preserved during coordinate enrichment.

**Final mapping dataset: 20 connections.**

## Key Insights

Preliminary findings from the processed data; the map is still in development.

| Measure | Migrants living in Singapore | Migrants originating from Singapore living abroad |
| --- | ---: | ---: |
| World total | 2,841,665 | 269,613 |
| Combined top 10 population | 2,709,692 | 256,315 |
| Top 10 share of corresponding World total | 95.36% | 95.07% |

- Malaysia is the largest recorded origin among migrants living in Singapore, with **1,553,249 people**.
- Malaysia is also the largest recorded destination among migrants originating from Singapore, with **79,926 people**.
- Seven countries or areas appear in both top 10 lists: **Malaysia, China, India, Australia, Hong Kong SAR, New Zealand, and Canada**.

These findings describe migrant populations at mid-2024, not moves made during that year.

## Reflection

*To be completed following map development.*

## File Structure

The notebook and data files are prepared. The saved map configuration and final image are planned outputs.

```text
 day02_lines/
 ├── README.md
 ├── 01_sg_migration_EDA.ipynb
 ├── data/
 │   ├── migrantstock_raw.xlsx
 │   ├── sg_migration_top10_2024.csv
 │   └── sg_migration_top10_2024_kepler.csv
 ├── maps/
 │   └── singapore_migration_kepler.json    # Planned
 └── outputs/
     └── sg_connected.png                 # Planned
```

The repository uses a shared uv environment. Dependencies are recorded in the root `pyproject.toml` and `uv.lock`.

## References

### Data Sources

- [UN DESA — International Migrant Stock](https://www.un.org/development/desa/pd/content/international-migrant-stock)
- [Natural Earth — Admin 0 Countries](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/)
- [Natural Earth — GeoJSON used for coordinate extraction](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_10m_admin_0_countries.geojson)

### Data Definitions and Attribution

- United Nations Department of Economic and Social Affairs, Population Division (2024). *International Migrant Stock 2024*. Destination and origin, Table 1 and Migrant notes.
- [Creative Commons Attribution 3.0 IGO](https://creativecommons.org/licenses/by/3.0/igo/)
- [Natural Earth — Public Domain Terms](https://www.naturalearthdata.com/about/terms-of-use/)
- Final basemap attribution to be added following map development.

### Tools and Challenge

- [30 Day Map Challenge](https://30daymapchallenge.com/)
- [Kepler.gl Documentation](https://docs.kepler.gl/)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [Jupyter Documentation](https://docs.jupyter.org/)
