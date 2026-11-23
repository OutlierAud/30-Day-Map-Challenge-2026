# 30 Day Map Challenge | Day 15
### 15 November 2026 | Inside Out

## The Price of Space
#### Where did residential land prices rise as populations grew or shrank?

Flip the map to compare changes in population and assessed residential land prices across 26 municipalities on Okinawa’s main island. Open `interactive.html` in a browser and select a municipality to follow it across both faces.

## Dataset

- Population counts from the October 2020 and October 2025 censuses.
- Municipal mean assessed residential land prices in yen per m² from July 2020 and July 2025.
- Day 13 municipal boundaries and OpenStreetMap roads. The map shows main-island geometry and uses published totals for each municipality.

## Methodology & Tools

- Each bar shows the percentage change from its 2020 value. 
    - Cyan shows population gains, hatched purple shows losses 
    - Hot pink shows land price rises. 
- Each face has its own scale. 
- Select a municipality to see the original values and the change in residents or yen per m².

Python: To bbild the standalone HTML map and render the 28-second loop with FFmpeg.  

To rebuild the map, run:  
`../.venv/bin/python build_interactive.py` 
  
To rebuild the video, run:  
`../.venv/bin/python render.py`

## Key Insights

- Ginoza had the largest population gain (+7.6%) and Kunigami the largest loss (−8.5%).
- Assessed residential land prices rose in all 26 municipalities. Kitanakagusuku had the largest rise (+54.9%) and Kunigami the smallest (+2.7%).
- Naha lost 6,920 residents while its assessed residential land price rose 14.1%.

## References

- [Okinawa Prefecture census results](https://www.pref.okinawa.lg.jp/toukeika/pc/2025/R07kokutyou.html)
- [Residential land price survey, 2020](https://www.pref.okinawa.lg.jp/_res/projects/default_project/_page_/001/012/366/2020sityousonbetu.pdf) and [2025](https://www.pref.okinawa.lg.jp/_res/projects/default_project/_page_/001/012/366/2025sityousonbetu.pdf)
- [MLIT municipal boundaries](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html)
- Roads © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright) via [OpenFreeMap](https://openfreemap.org/)
