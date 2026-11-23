# 30 Day Map Challenge | Day 01
### 1 November 2026 | Points: A Map Challenge Classic

## Jump To

- [Dataset](#dataset)
- [Methodology & Tools](#methodology--tools)
- [Key Insights](#key-insights)
- [Reflection](#reflection)
- [File Structure](#file-structure)
- [References](#references)

## Koala Sightings on the Gold Coast
#### Where are the koalas?

Are sightings clustered?  
Can we identify any spatial relationships?  
Do recorded sightings fall within the boundaries we've established to protect wildlife?

The idea is to map recorded koala sightings across the Gold Coast, Queensland, with parks and nature reserves providing geographic context.

This project is an exploration of point mapping, spatial patterns, and cartographic design using Python and QGIS.

## Dataset

### Data Sources

**1. Atlas of Living Australia (ALA)**

Koala (*Phascolarctos cinereus*) occurrence records, including geographic coordinates and observation dates.

- Source: Atlas of Living Australia
- Species: *Phascolarctos cinereus*
- Geographic extent: Gold Coast Local Government Area, Queensland, Australia
- Observation period: 1 November 2021 – 10 October 2026
- Original records: 3,152
- Records retained following spatial validation: 3,151
- Dataset DOI: https://doi.org/10.26197/ala.8df9a8c3-c658-4f62-9ca3-6afc27677887

The dataset includes observations contributed by multiple organizations, including the City of Gold Coast, Queensland WildNet, iNaturalist, and koala conservation groups.

**2. OpenStreetMap (OSM)**

Geographic reference data for the Gold Coast, including roads, land use, and other contextual features.

**3. Queensland Spatial Catalogue (QSpatial)**

Spatial boundaries for protected areas, parks, and nature reserves.

Relevant datasets will be selected based on geographic coverage and availability.

### Data Considerations

**Observation Bias and Spatial Accuracy**

Occurrence records represent documented observations, not necessarily individual koalas or population estimates.

The geographic distribution of sightings may be influenced by observation effort, accessibility, reporting practices, and positional accuracy.

Coordinate uncertainty is reported for only a subset of records. Missing uncertainty values do not necessarily indicate accurate locations.

Consequently, concentrations of recorded sightings should not be interpreted directly as concentrations of koala populations.

**Sensitive Species Locations**

The Atlas of Living Australia applies sensitivity-management procedures to biodiversity occurrence records. Depending on the applicable restrictions, location information may be generalized or withheld.

However, the accompanying download documentation does not explicitly confirm whether coordinates in this particular dataset have been generalized.

The following fields will be examined, where available, to identify documented coordinate modifications or restrictions:

- `dataGeneralizations`
- `generalisationInMetres`
- `informationWithheld`

Original downloaded coordinates are retained for local spatial analysis. Their suitability for public release will be assessed before publication.

The final visualization will emphasize broader spatial patterns rather than the identification of individual observation locations.

**Licensing and Attribution**

The ALA download contains records contributed by multiple data providers under different licensing conditions, including:

- Creative Commons Attribution (CC BY)
- Creative Commons Attribution–ShareAlike (CC BY-SA)
- Creative Commons Attribution–NonCommercial (CC BY-NC)

Some contributing datasets do not specify licensing conditions in the download documentation.

Source attribution and licensing information are retained during processing. Any public redistribution of occurrence records will require consideration of the applicable licenses.

## Methodology & Tools

**Tools:** Python (pandas, GeoPandas), QGIS

1. **Establish the geographic context:** Define the Gold Coast Local Government Area as the study boundary.
2. **Import spatial data:** Load koala occurrence records and geographic reference layers.
3. **Data validation:** Assess missing values, duplicate records, coordinate validity, observation dates, positional uncertainty, and geographic relevance.
4. **Data processing:** Retain records within the study boundary and select relevant attributes for mapping.
5. **Spatial analysis:** Explore the distribution of sightings and their relationship with parks and nature reserves.
6. **Cartographic design:** Experiment with point symbology, colour, visual hierarchy, and map composition.
7. **Final map:** Refine and export the completed visualization.

### Data Validation Summary

The original dataset contains 3,152 occurrence records.

Validation identified:

- No duplicate `recordID` values.
- No missing or invalid geographic coordinates.
- No invalid observation dates or dates outside the requested study period.
- Coordinate uncertainty reported for 592 records; unavailable for 2,560 records.
- One record located approximately 7.86 metres outside the Gold Coast LGA boundary.

The record outside the study boundary was excluded from the processed dataset.

**Final dataset: 3,151 occurrence records.**

## Key Insights

*To be completed following map development.*

## Reflection

*To be completed following map development.*

## File Structure

```text
day01_points/
├── README.md
├── validate_koalas.py
├── process_koalas.py
├── data/
│   ├── goldcoast_lga.gpkg
│   ├── koala_sightings_raw.csv
│   ├── koala_sightings_processed.csv
│   ├── headings.csv
│   ├── citation.csv
│   ├── doi.txt
│   └── README.html
└── day01_koala_sightings.qgz
```

## References

### Data Sources
- [Atlas of Living Australia (ALA)](https://www.ala.org.au/)
- [ALA Koala Occurrence Dataset — Download DOI](https://doi.org/10.26197/ala.8df9a8c3-c658-4f62-9ca3-6afc27677887)
- [OpenStreetMap](https://www.openstreetmap.org/)
- [Queensland Spatial Catalogue (QSpatial)](https://qldspatial.information.qld.gov.au/)

### Data Sensitivity and Licensing
- [ALA — Restricted Access Species Data](https://support.ala.org.au/support/solutions/articles/6000286893-restricted-access-species-sensitive-data-in-the-ala)
- [Queensland Government — Confidential Species](https://www.data.qld.gov.au/dataset/queensland-confidential-species)
- [ALA — Citing the Atlas of Living Australia](https://support.ala.org.au/support/solutions/articles/6000261662-citing-the-ala)

### Tools and Challenge
- [30 Day Map Challenge](https://30daymapchallenge.com/)
- [QGIS Documentation](https://docs.qgis.org/)
- [GeoPandas Documentation](https://geopandas.org/)
- [pandas Documentation](https://pandas.pydata.org/docs/)