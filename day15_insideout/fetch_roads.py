"""Download the OpenFreeMap vector tiles covering Okinawa, then extract road lines."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import gzip
import json
from math import asinh, floor, pi, radians, tan
from pathlib import Path
import subprocess


def tile(lon, lat, zoom):
    width = 2 ** zoom
    return floor(width * (lon + 180) / 360), floor(width * (1 - asinh(tan(radians(lat))) / pi) / 2)


def download_url(url):
    return subprocess.check_output(["curl", "-fsSL", "--retry", "1", "--max-time", "25", url])


def fetch(directory):
    zoom = 11
    template = json.loads(download_url("https://tiles.openfreemap.org/planet"))["tiles"][0]
    west, north = tile(127.62, 26.89, zoom)
    east, south = tile(128.35, 26.06, zoom)
    tasks = [(x, y) for x in range(west, east + 1) for y in range(north, south + 1)]
    directory.mkdir(parents=True, exist_ok=True)

    def download(tile_coordinates):
        x, y = tile_coordinates
        path = directory / str(zoom) / str(x) / f"{y}.pbf"
        path.parent.mkdir(parents=True, exist_ok=True)
        data = download_url(template.format(z=zoom, x=x, y=y))
        path.write_bytes(gzip.decompress(data) if data.startswith(b"\x1f\x8b") else data)

    with ThreadPoolExecutor(max_workers=5) as workers:
        list(workers.map(download, tasks))
    print(f"Downloaded {len(tasks)} tiles from {template}")


def extract(directory, output):
    import pyogrio
    classes = {"motorway": "motorway", "trunk": "trunk", "primary": "primary",
               "secondary": "secondary", "tertiary": "tertiary", "minor": "tertiary"}
    elements = []
    for path in sorted(directory.glob("*/*/*.pbf")):
        if "transportation" not in pyogrio.list_layers(path)[:, 0]:
            continue
        roads = pyogrio.read_dataframe(path, layer="transportation").to_crs(4326)
        for kind, geom in zip(roads["class"], roads.geometry):
            if kind not in classes or geom is None:
                continue
            for line in getattr(geom, "geoms", [geom]):
                if line.geom_type == "LineString":
                    elements.append({
                        "tags": {"highway": classes[kind]},
                        "geometry": [{"lon": x, "lat": y} for x, y in line.coords],
                    })
    if not elements:
        raise RuntimeError("No road features were found in the source tiles")
    output.write_text(json.dumps({"elements": elements}, separators=(",", ":")))
    print(f"Extracted {len(elements)} road segments")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tiles", type=Path)
    parser.add_argument("--extract", type=Path)
    args = parser.parse_args()
    if args.extract:
        extract(args.tiles, args.extract)
    else:
        fetch(args.tiles)
