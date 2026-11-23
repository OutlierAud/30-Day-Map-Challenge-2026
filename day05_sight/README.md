# 30 Day Map Challenge | Day 05

### 5 November 2026 | Senses: Sight

## 🎬 [Watch the animation](media/trading-starlight-for-streetlights.mp4)

## Jump To

- [Project](#trading-starlight-for-streetlights)
- [Dataset](#dataset)
- [Methodology & Tools](#methodology--tools)
- [Key Insights](#key-insights)
- [Reflection](#reflection)
- [File Structure](#file-structure)
- [References](#references)

## Trading Starlight for Streetlights

#### The Geography of Light Pollution

*As Earth gets brighter, skies get dimmer.*

How does artificial light reshape the night? This map and animation trace the global footprint of nighttime lighting, moving from regional views of illuminated cities and corridors to a wide view of Earth at night. The Day 05 theme, **Senses: Sight**, is an invitation to think about how the lights we see from orbit relate to the stars we can see from the ground.

## Dataset

### 1. NASA Black Marble nighttime imagery

The nighttime layer is the Generic Mapping Tools (GMT) version of NASA’s Black Marble mosaic. The mosaic draws on observations from the Day/Night Band of the Visible Infrared Imaging Radiometer Suite (VIIRS) aboard the NASA/NOAA Suomi NPP satellite. GMT distributed the downsampled image as `earth_night_02m_p.tif`, and the copy used here was downloaded from NOAA STAR. [NASA Earth Observatory](https://science.nasa.gov/earth/earth-observatory/earth-at-night/) · [GMT dataset documentation](https://www.generic-mapping-tools.org/remote-datasets/earth-daynight.html) · [NOAA STAR GeoTIFF download](https://www.star.nesdis.noaa.gov/data/socd3/lsa/gmtdata/server/earth/earth_night/earth_night_02m_p.tif)

| Property | Details |
| --- | --- |
| Local file | `media/night_lights.tif` |
| Coverage | Global, 180°W to 180°E and 90°S to 90°N |
| Grid spacing | 2 arcminutes, or 0.0333° per pixel |
| Image size | 10,800 × 5,400 pixels |
| Format | GeoTIFF with three 8-bit RGB bands |
| Observation period | The exact observation dates for this GMT copy are unverified. |

### 2. Natural Earth country boundaries

`worldmap.geojson` contains 177 features from Natural Earth’s **Admin 0 – Countries** dataset at 1:110 million scale. The layer provides country boundaries and names for geographic context. [Natural Earth dataset](https://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-admin-0-countries/)

### Data Considerations

The raster stores rendered RGB colours. Its brightness supports a qualitative reading of nighttime lights, while calibrated radiance, ground-level skyglow and star visibility require their own measurements. The animation moves across a single mosaic, so changes between frames reflect the map view.

## Methodology & Tools

1. **Build the map in QGIS.** Load the Black Marble GeoTIFF through QGIS’s GDAL raster provider and add Natural Earth country boundaries and labels for context.
2. **Animate the map with PyQGIS.** Move through keyframed views of North America, Europe, East Asia and Australia before pulling back to a wide world view. The script interpolates the map extent and rotation and gradually flattens the opening perspective tilt.
3. **Render the frames.** Open `day05_starrynight.qgz` in QGIS and run `pan_2D_light_pollution.py` from the QGIS Python Console. With its default settings, the script renders 361 PNGs at 3840 × 2160 and checks each image’s dimensions. It saves the sequence in `Final_Cinematic_Frames_4K_v3` on the desktop.
4. **Assemble the video.** The rendered PNG sequence is ready to import into QuickTime Player. The soundtrack credit is “Nightlight” by ViiCréateur.

## Key Insights

- The eastern United States, western Europe and coastal East Asia show dense clusters of nighttime lights.
- The Nile appears as a narrow ribbon of light against the darker surrounding desert. In Australia, lights cluster along parts of the coast, with fewer visible points across the interior.
- At regional scale, the lights suggest corridors between settlements. The wider view shows how unevenly visible illumination is distributed across the globe.

## Reflection

The regional views give the lights room to resolve into individual clusters and corridors. Pulling back makes their uneven distribution easier to see. The view from orbit also puts the theme of sight in perspective. It shows where lights are visible from space and leaves open the question of what people can see when they look up from those places.

## File Structure

```text
day05_sight/
├── README.md
├── day05_starrynight.qgz
├── pan_2D_light_pollution.py
├── worldmap.geojson
└── media/
    ├── trading-starlight-for-streetlights.mp4
    ├── night_lights.tif
    ├── title.png
    └── subtitle.png
```

## References

### Data Sources

- NASA Earth Observatory, *Earth at Night / Black Marble*. [NASA imagery and documentation](https://science.nasa.gov/earth/earth-observatory/earth-at-night/maps/)
- Generic Mapping Tools, *NASA Earth Day/Night Images*, 2-arcminute nighttime mosaic. [GMT documentation](https://www.generic-mapping-tools.org/remote-datasets/earth-daynight.html) · [NOAA STAR file listing](https://www.star.nesdis.noaa.gov/data/socd3/lsa/gmtdata/server/earth/earth_night/)
- Natural Earth, *Admin 0 – Countries*, 1:110 million. [Dataset](https://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-admin-0-countries/)

### Tools and Media

- [QGIS](https://qgis.org/) · [Python](https://www.python.org/) · [GDAL](https://gdal.org/)
- “Nightlight” by ViiCréateur. [Pixabay artist page](https://pixabay.com/vi/users/viicr%C3%A9ateur-36479483/)
- [30 Day Map Challenge](https://30daymapchallenge.com/)
