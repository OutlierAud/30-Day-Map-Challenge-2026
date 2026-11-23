import bpy
import json
from math import cos, radians, sin
from pathlib import Path

earth = bpy.data.objects["Earth"]
path = Path(bpy.path.abspath("//data/ne_50m_coastline.geojson"))
features = json.loads(path.read_text(encoding="utf-8"))["features"]

curve = bpy.data.curves.new("Coastlines", type="CURVE")
curve.dimensions = "3D"
curve.bevel_depth = 0.0015  # Controls the thickness of the lines.
curve.bevel_resolution = 0
radius = 1.002  # Place the coastlines just above Earth's surface.

for feature in features:
    geometry = feature["geometry"]
    lines = geometry["coordinates"]
    if geometry["type"] == "LineString":
        lines = [lines]

    for line in lines:
        spline = curve.splines.new("POLY")
        spline.points.add(len(line) - 1)

        for point, coordinate in zip(spline.points, line):
            lon, lat = map(radians, coordinate[:2])
            point.co = (
                radius * cos(lat) * cos(lon),
                radius * cos(lat) * sin(lon),
                radius * sin(lat),
                1.0,
            )

coastlines = bpy.data.objects.new("Coastlines", curve)
bpy.context.collection.objects.link(coastlines)
coastlines.parent = earth

material = bpy.data.materials.new("Coastline gray")
material.diffuse_color = (0.14, 0.17, 0.22, 1.0)
curve.materials.append(material)