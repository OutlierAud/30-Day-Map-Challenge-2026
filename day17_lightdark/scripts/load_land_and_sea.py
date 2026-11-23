"""Paint the Earth object from the Natural Earth land polygons.

Run inside Blender with the .blend file saved beside the data folder.
The generated land mask is packed into the .blend when you save it.
"""

import json
from collections import defaultdict
from math import ceil, pi
from pathlib import Path

import bpy
import numpy as np


WIDTH = 2048
HEIGHT = 1024
MASK_NAME = "Natural Earth land mask"
NODE_PREFIX = "Land and sea | "
LAND_COLOR = (0.155, 0.205, 0.145, 1.0)
OCEAN_COLOR = (0.024, 0.071, 0.127, 1.0)


def rasterize_land(features):
    """Fill equirectangular pixel rows between polygon edges, including holes."""
    mask = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
    for feature in features:
        geometry = feature["geometry"]
        polygons = geometry["coordinates"]
        if geometry["type"] == "Polygon":
            polygons = [polygons]

        for polygon in polygons:
            intersections = defaultdict(list)
            for ring in polygon:
                points = [
                    ((lon + 180) * WIDTH / 360, (lat + 90) * HEIGHT / 180)
                    for lon, lat, *_ in ring
                ]
                for (x1, y1), (x2, y2) in zip(points, points[1:]):
                    if y1 == y2:
                        continue
                    first = max(0, ceil(min(y1, y2) - 0.5))
                    stop = min(HEIGHT, ceil(max(y1, y2) - 0.5))
                    slope = (x2 - x1) / (y2 - y1)
                    for row in range(first, stop):
                        intersections[row].append(x1 + (row + 0.5 - y1) * slope)

            for row, crossings in intersections.items():
                crossings.sort()
                for left, right in zip(crossings[::2], crossings[1::2]):
                    first = max(0, ceil(left - 0.5))
                    stop = min(WIDTH, ceil(right - 0.5))
                    mask[row, first:stop] = 1
    return mask


def make_mask_image(mask):
    image = bpy.data.images.get(MASK_NAME)
    if image is None:
        image = bpy.data.images.new(MASK_NAME, WIDTH, HEIGHT, alpha=False)
    if tuple(image.size) != (WIDTH, HEIGHT):
        image.scale(WIDTH, HEIGHT)
    image.colorspace_settings.name = "Non-Color"

    pixels = np.ones((HEIGHT, WIDTH, 4), dtype=np.float32)
    pixels[:, :, :3] = mask[:, :, None]
    image.pixels.foreach_set(pixels.ravel())
    image.update()
    image.pack()
    return image


def apply_colors(material, image):
    tree = material.node_tree
    nodes = tree.nodes
    links = tree.links
    surface = next(node for node in nodes if node.type == "BSDF_PRINCIPLED")
    for node in list(nodes):
        if node.name.startswith(NODE_PREFIX):
            nodes.remove(node)

    def add(node_type, name, position):
        node = nodes.new(node_type)
        node.name = NODE_PREFIX + name
        node.label = name
        node.location = position
        return node

    # Local coordinates rotate with Earth. Match the longitude/latitude
    # convention used to place the lighthouse dots and coastline curves.
    coordinates = add("ShaderNodeTexCoord", "Earth coordinates", (-1250, 0))
    direction = add("ShaderNodeVectorMath", "Unit direction", (-1050, 0))
    direction.operation = "NORMALIZE"
    links.new(coordinates.outputs["Object"], direction.inputs[0])

    axes = add("ShaderNodeSeparateXYZ", "Separate XYZ", (-850, 0))
    links.new(direction.outputs["Vector"], axes.inputs[0])

    longitude = add("ShaderNodeMath", "Longitude", (-650, 120))
    longitude.operation = "ARCTAN2"
    links.new(axes.outputs["Y"], longitude.inputs[0])
    links.new(axes.outputs["X"], longitude.inputs[1])

    latitude = add("ShaderNodeMath", "Latitude", (-650, -110))
    latitude.operation = "ARCSINE"
    links.new(axes.outputs["Z"], latitude.inputs[0])

    uv = add("ShaderNodeCombineXYZ", "Map coordinates", (-250, 0))
    for index, angle, scale in ((0, longitude, 1 / (2 * pi)), (1, latitude, 1 / pi)):
        convert = add("ShaderNodeMath", ("Longitude to U", "Latitude to V")[index],
                      (-450, 120 - index * 230))
        convert.operation = "MULTIPLY_ADD"
        convert.inputs[1].default_value = scale
        convert.inputs[2].default_value = 0.5
        links.new(angle.outputs[0], convert.inputs[0])
        links.new(convert.outputs[0], uv.inputs[index])

    texture = add("ShaderNodeTexImage", "Land mask", (-50, 0))
    texture.image = image
    links.new(uv.outputs[0], texture.inputs["Vector"])

    colors = add("ShaderNodeMixRGB", "Ocean and land colors", (250, 0))
    colors.inputs[1].default_value = OCEAN_COLOR
    colors.inputs[2].default_value = LAND_COLOR
    links.new(texture.outputs["Color"], colors.inputs[0])
    links.new(colors.outputs[0], surface.inputs["Base Color"])
    surface.inputs["Specular IOR Level"].default_value = 0


def main():
    earth = bpy.context.scene.objects["Earth"]
    path = Path(bpy.path.abspath("//data/ne_50m_land.geojson"))
    features = json.loads(path.read_text(encoding="utf-8"))["features"]
    mask = rasterize_land(features)
    image = make_mask_image(mask)
    apply_colors(earth.active_material, image)
    print("Applied and packed the Earth land mask. Save your Blender project.")


if __name__ == "__main__":
    main()
