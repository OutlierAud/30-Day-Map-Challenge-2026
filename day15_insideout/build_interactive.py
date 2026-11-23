"""Package the renderer's basemap and geometry in an offline HTML viewer."""
import base64
from io import BytesIO
import json

from render import ROOT, SCALE, SECONDS, THICK, Scene, pose


def main():
    scene = Scene()
    texture = BytesIO()
    scene.texture.save(texture, "PNG")
    areas = []
    for index, row in enumerate(scene.areas):
        areas.append({
            "name": row["name"],
            "before": row["before"],
            "after": row["after"],
            "change": row["population_change"],
            "land": row["land_price_survey"],
            "bars": [
                [bottom.tolist(), top.tolist(), color, loss]
                for bottom, top, color, loss in [scene.columns[1][index], scene.columns[-1][index]]
            ],
        })
    places = [
        [scene.world((lon, lat)).tolist(), name, dx, dy]
        for lon, lat, name, dx, dy in [
            (127.681, 26.213, "Naha", -20, 16), (127.804, 26.334, "Okinawa City", 22, -8),
            (127.978, 26.590, "Nago", -20, -12), (128.176, 26.749, "Kunigami", 20, 10),
        ]
    ]
    data = {
        "areas": areas,
        "places": places,
        "coast": [ring.tolist() for ring in scene.coast_rings],
        "scale": SCALE,
        "thickness": THICK,
        "textureBounds": scene.texture_bounds,
        "texture": "data:image/png;base64," + base64.b64encode(texture.getvalue()).decode("ascii"),
        "duration": SECONDS,
        "poses": [pose(i / (SECONDS * 30)) for i in range(SECONDS * 30 + 1)],
    }
    template = (ROOT / "interactive.template.html").read_text()
    encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    (ROOT / "interactive.html").write_text(template.replace("/* MAP_DATA */ null", encoded))


if __name__ == "__main__":
    main()
