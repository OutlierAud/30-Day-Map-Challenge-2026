"""Prepare the Day 13 measurements and exact main-island component."""
from collections import defaultdict, deque
import json
from pathlib import Path

from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"


def javascript_data(filename):
    return json.JSONDecoder().raw_decode((DATA / filename).read_text().split("=", 1)[1].lstrip())[0]


def main_island(features):
    polygons, by_vertex = [], defaultdict(list)
    for feature in features:
        geometry = feature["geometry"]
        parts = geometry["coordinates"]
        if geometry["type"] == "Polygon":
            parts = [parts]
        for rings in parts:
            index = len(polygons)
            polygons.append((feature["properties"], rings))
            for xy in rings[0]:
                by_vertex[tuple(xy)].append(index)
    seed = max(
        (i for i, (p, _) in enumerate(polygons) if p["code"] == "47201"),
        key=lambda i: Polygon(polygons[i][1][0]).area,
    )
    included = {seed}
    queue = deque([seed])
    while queue:
        for xy in polygons[queue.popleft()][1][0]:
            for index in by_vertex.pop(tuple(xy), []):
                if index not in included:
                    included.add(index)
                    queue.append(index)
    municipalities = {}
    for i in sorted(included):
        properties, rings = polygons[i]
        row = municipalities.setdefault(properties["code"], {**properties, "polygons": []})
        row["polygons"].append(Polygon(rings[0], rings[1:]))
    return municipalities


def build(roads_file=None):
    municipalities = main_island(javascript_data("okinawa.js")["features"])
    prices = javascript_data("land.js")
    coast = unary_union([polygon for row in municipalities.values() for polygon in row["polygons"]])
    roads = []
    if roads_file:
        elements = json.loads(Path(roads_file).read_text())["elements"]
        for way in elements:
            line = LineString([(p["lon"], p["lat"]) for p in way["geometry"]])
            segment = line.intersection(coast)
            for part in getattr(segment, "geoms", [segment]):
                if part.geom_type == "LineString" and not part.is_empty:
                    roads.append([way["tags"]["highway"], list(part.simplify(0.00006).coords)])
    rows = []
    for code, row in municipalities.items():
        polygons = row.pop("polygons")
        anchor = max(polygons, key=lambda polygon: polygon.area).representative_point()
        rows.append({
            **row,
            "polygons": [[list(p.exterior.coords), *[list(r.coords) for r in p.interiors]] for p in polygons],
            "anchor": list(anchor.coords)[0],
            "population_change": row["after"] - row["before"],
            "land_price_survey": prices.get(code),
        })
    assert len(rows) == 26, len(rows)
    assert all(r["land_price_survey"] for r in rows)
    (DATA / "main-island.json").write_text(json.dumps({"areas": rows, "roads": roads}, ensure_ascii=False, separators=(",", ":")))
    print(f"{len(rows)} municipalities, {len(roads)} road segments")


if __name__ == "__main__":
    import sys
    build(sys.argv[1] if len(sys.argv) > 1 else None)
