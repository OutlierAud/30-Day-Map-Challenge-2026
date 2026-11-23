# 30 Day Map Challenge | Day 17
### 17 November 2026 | Light & Dark

## Jump To

- [Dataset](#dataset)
- [Methodology & Tools](#methodology--tools)
- [File Structure](#file-structure)
- [References](#references)

## Where the Land Ends
#### How much of the coastline can we see by lighthouse alone?

The idea is to map lighthouses around the world on a slowly rotating black globe. Warm-white points mark the lighthouses, with faint coastlines for context.

## Dataset

- **OpenStreetMap** — Worldwide features tagged `man_made=lighthouse`, exported from Overpass Turbo as GeoJSON. Coverage varies by region, and the tag does not confirm that a light is still operating.
- **Natural Earth** — World coastlines at 1:50m, downloaded as GeoJSON.

## Methodology & Tools

**Tools:** Blender, Python

1. Load the lighthouse and coastline GeoJSON files.
2. Use their geographic coordinates to place the lights and draw the coastlines on a sphere.
3. Style the lights with a soft glow and animate one full rotation.

## File Structure

```text
day17_lightdark/
├── README.md
└── data/
    ├── lighthouses.geojson
    └── ne_50m_coastline.geojson
```

## References

- [© OpenStreetMap contributors](https://www.openstreetmap.org/copyright)
- [Overpass Turbo lighthouse query](https://overpass-turbo.eu/?Q=%5Bout%3Ajson%5D%5Btimeout%3A90%5D%3B%0Anwr%5B%22man_made%22%3D%22lighthouse%22%5D%3B%0Aout%20center%3B)
- [Natural Earth coastline download](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_50m_coastline.geojson)
- [30 Day Map Challenge](https://30daymapchallenge.com/)
