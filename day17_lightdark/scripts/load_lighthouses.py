import bpy
import json
from math import cos, radians, sin
from pathlib import Path

earth = bpy.data.objects["Earth"]
path = Path(bpy.path.abspath("//data/lighthouses.geojson"))
features = json.loads(path.read_text(encoding="utf-8"))["features"]

radius = 1.006  # Sit just above the surface of the default sphere.
size = 0.006    # Dot size. We can adjust this after seeing the result.

# Each dot is a tiny diamond made from six vertices and eight faces.
offsets = [(size, 0, 0), (-size, 0, 0), (0, size, 0),
           (0, -size, 0), (0, 0, size), (0, 0, -size)]
dot_faces = [(4, 0, 2), (4, 2, 1), (4, 1, 3), (4, 3, 0),
             (5, 2, 0), (5, 1, 2), (5, 3, 1), (5, 0, 3)]

vertices, faces = [], []
for feature in features:
    geometry = feature["geometry"]
    if geometry["type"] != "Point":
        continue

    lon, lat = map(radians, geometry["coordinates"][:2])
    x = radius * cos(lat) * cos(lon)
    y = radius * cos(lat) * sin(lon)
    z = radius * sin(lat)

    start = len(vertices)
    vertices.extend((x + dx, y + dy, z + dz) for dx, dy, dz in offsets)
    faces.extend(tuple(start + index for index in face) for face in dot_faces)

mesh = bpy.data.meshes.new("Lighthouse dots")
mesh.from_pydata(vertices, [], faces)
mesh.update()

dots = bpy.data.objects.new("Lighthouse dots", mesh)
bpy.context.collection.objects.link(dots)
dots.parent = earth  # The dots turn with the Earth.

material = bpy.data.materials.new("Warm lighthouse light")
material.use_nodes = True
nodes = material.node_tree.nodes
emission = nodes.new("ShaderNodeEmission")
emission.inputs["Color"].default_value = (1.0, 0.68, 0.32, 1.0)
emission.inputs["Strength"].default_value = 2.0
material.node_tree.links.new(
    emission.outputs["Emission"], nodes["Material Output"].inputs["Surface"]
)
mesh.materials.append(material)