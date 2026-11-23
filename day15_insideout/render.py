"""Render the two-sided map with an orthographic 3D camera and export via FFmpeg."""
import argparse
import json
from math import cos, sin, pi, radians
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import Polygon
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent
FONT = Path("/System/Library/Fonts/Supplemental")
W, H, FPS, SECONDS = 1080, 1350, 30, 28
SCALE, CENTER = 8.35, np.array([540, 648])
BACKGROUND = "#0a0c13"
INK, MUTED = "#eff3fd", "#98a9bd"
CYAN, LOSS, PINK = "#39f4ee", "#9639e6", "#ff439d"
POP_HEIGHT, PRICE_HEIGHT = 190, 33
THICK = 0.40
ROAD_COLORS = {
    "motorway": ("#ae9c89", 4), "trunk": ("#a69a8b", 4),
    "primary": ("#7f8d9f", 3), "secondary": ("#606e83", 2),
    "tertiary": ("#495769", 2),
}


def font(size, bold=False):
    return ImageFont.truetype(str(FONT / ("Arial Bold.ttf" if bold else "Arial.ttf")), size)


FONTS = {size: font(size, bold) for size, bold in [(18, False), (19, False), (22, False), (25, True), (37, True), (82, True)]}


def smooth(a, b, value):
    t = max(0, min(1, (value - a) / (b - a)))
    return t * t * (3 - 2 * t)


def shade(hex_color, factor):
    return tuple(min(255, round(int(hex_color[i:i + 2], 16) * factor)) for i in (1, 3, 5))


def pose(t):
    """Pitch, yaw and spin in degrees, with upright holds on both faces."""
    seconds = max(0, min(1, t)) * SECONDS
    first = smooth(.65, 13.4, seconds)
    second = smooth(14.6, 27.35, seconds)
    turn = first + second
    phase = pi * turn
    return (-43 - 180 * turn,
            18 * sin(phase) + 7 * sin(2 * phase),
            -10 + 12 * sin(phase) + 2 * (1 - cos(phase)))


def camera(t):
    pitch, yaw, spin = map(radians, pose(t))
    cz, sz, cx, sx, cy, sy = cos(spin), sin(spin), cos(pitch), sin(pitch), cos(yaw), sin(yaw)
    return (np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]]) @
            np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]) @
            np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]))


class Scene:
    def __init__(self):
        data = json.loads((ROOT / "data/main-island.json").read_text())
        self.areas, self.roads = data["areas"], data["roads"]
        all_xy = np.array([xy for row in self.areas for poly in row["polygons"] for xy in poly[0]])
        self.origin = (all_xy.min(0) + all_xy.max(0)) / 2
        self.geo_scale = np.array([111.32 * cos(radians(self.origin[1])), 110.8])
        self.polygons = [
            [self.world(ring) for ring in poly]
            for row in self.areas for poly in row["polygons"]
        ]
        self.coast = unary_union([Polygon(p[0], p[1:]) for p in self.polygons]).simplify(.035)
        self.coast_rings = [
            np.array(ring.coords)
            for polygon in getattr(self.coast, "geoms", [self.coast])
            for ring in [polygon.exterior, *polygon.interiors]
        ]
        self.texture_bounds = (-42, 42, 18)
        self.texture = self.basemap()
        self.columns = self.make_columns()

    def world(self, xy):
        return (np.asarray(xy) - self.origin) * self.geo_scale

    def texture_points(self, points):
        x0, y1, density = self.texture_bounds
        return [tuple(p) for p in ((points - [x0, y1]) * [density, -density])]

    def basemap(self):
        image = Image.new("RGBA", (1512, 1512))
        draw = ImageDraw.Draw(image)
        for index, poly in enumerate(self.polygons):
            fill = ["#242e3e", "#283448", "#29374a", "#253246"][index % 4]
            draw.polygon(self.texture_points(poly[0]), fill=fill)
            for hole in poly[1:]:
                draw.polygon(self.texture_points(hole), fill=(0, 0, 0, 0))
        mask = image.getchannel("A")
        for kind in ROAD_COLORS.keys().__reversed__():
            color, width = ROAD_COLORS[kind]
            for road_kind, line in self.roads:
                if road_kind == kind:
                    draw.line(self.texture_points(self.world(line)), fill=color, width=width, joint="curve")
        for poly in self.polygons:
            draw.line(self.texture_points(poly[0]), fill="#667991", width=2, joint="curve")
        for ring in self.coast_rings:
            draw.line(self.texture_points(ring), fill="#afc0d8", width=3, joint="curve")
        image.putalpha(mask)
        return image

    def make_columns(self):
        columns = {1: [], -1: []}
        for row in self.areas:
            x, y = self.world(row["anchor"])
            change = row["population_change"] / row["before"]
            (before_price, _), (after_price, _) = row["land_price_survey"]
            price_change = (after_price - before_price) / before_price
            for direction, height, width, color, loss in [
                (1, abs(change) * POP_HEIGHT, .75, CYAN if change >= 0 else LOSS, change < 0),
                (-1, abs(price_change) * PRICE_HEIGHT, .75, PINK, price_change < 0),
            ]:
                base = direction * THICK / 2
                bottom = np.array([[x - width, y - width, base], [x + width, y - width, base],
                                   [x + width, y + width, base], [x - width, y + width, base]])
                top = bottom + [0, 0, direction * height]
                columns[direction].append((bottom, top, color, loss))
        return columns

    @staticmethod
    def screen(view):
        return view[:, :2] * [SCALE, -SCALE] + CENTER

    def draw_map_texture(self, canvas, matrix, side):
        x0, y1, density = self.texture_bounds
        view = matrix @ np.array([x0, y1, side * THICK / 2])
        origin = self.screen(view[None])[0]
        forward = np.diag([SCALE, -SCALE]) @ matrix[:2, :2] @ np.diag([1 / density, -1 / density])
        if abs(np.linalg.det(forward)) < .001:
            return
        inverse = np.linalg.inv(forward)
        transform = np.column_stack([inverse, -inverse @ origin]).ravel()
        layer = self.texture.transform((W, H), Image.Transform.AFFINE, transform, Image.Resampling.BILINEAR)
        canvas.paste(layer, mask=layer.getchannel("A"))

    def draw_edge(self, draw, matrix):
        faces = []
        for ring in self.coast_rings:
            vertices = np.column_stack([ring, np.full(len(ring), THICK / 2)])
            a = vertices @ matrix.T
            b = a - matrix[:, 2] * THICK
            top, bottom = self.screen(a), self.screen(b)
            for i in range(len(ring) - 1):
                facing = (top[i + 1, 0] - top[i, 0]) * (bottom[i, 1] - top[i, 1]) - (top[i + 1, 1] - top[i, 1]) * (bottom[i, 0] - top[i, 0])
                if facing > 0:
                    continue
                faces.append((a[i, 2], [top[i], top[i + 1], bottom[i + 1], bottom[i]], "#46556c"))
        for _, vertices, color in sorted(faces, key=lambda face: face[0]):
            draw.polygon([tuple(p) for p in vertices], fill=color)

    def draw_columns(self, draw, matrix, side, near):
        faces = []
        for bottom, top, color, loss in self.columns[side]:
            vertices = np.concatenate([bottom, top]) @ matrix.T
            screen = self.screen(vertices)
            for indices, factor in [([4, 5, 6, 7], 1.10), ([0, 1, 5, 4], .65),
                                    ([1, 2, 6, 5], .81), ([2, 3, 7, 6], .55),
                                    ([3, 0, 4, 7], .92), ([3, 2, 1, 0], .53)]:
                xy = screen[indices]
                a, b = xy[1] - xy[0], xy[2] - xy[1]
                if (a[0] * b[1] - a[1] * b[0]) * side >= 0:
                    continue
                depth = vertices[indices, 2].mean()
                faces.append((depth, xy, shade(color, factor * (1 if near else .75)), loss, factor))
        for _, points, color, loss, factor in sorted(faces, key=lambda f: f[0]):
            draw.polygon([tuple(p) for p in points], fill=color)
            if loss and factor < 1 and near:
                for t in [.25, .5, .75]:
                    a = points[0] * (1 - t) + points[3] * t
                    b = points[1] * (1 - t) + points[2] * t
                    draw.line([tuple(a), tuple(b)], fill="#dcaaff", width=1)

    def draw_places(self, draw, matrix, side):
        if abs(matrix[2, 2]) < .48:
            return
        placed = []
        for lon, lat, name, dx, dy in [
            (127.681, 26.213, "NAHA", -20, 16),
            (127.804, 26.334, "OKINAWA CITY", 22, -8),
            (127.978, 26.590, "NAGO", -20, -12),
            (128.176, 26.749, "KUNIGAMI", 20, 10),
        ]:
            xy = self.world((lon, lat))
            x, y = self.screen(np.array([[*xy, side * THICK / 2]]) @ matrix.T)[0]
            dx *= side
            anchor = "lm" if dx > 0 else "rm"
            target = (x + dx, y + dy)
            box = draw.textbbox(target, name, font=FONTS[18], anchor=anchor, stroke_width=2)
            if any(box[0] < other[2] and box[2] > other[0] and box[1] < other[3] and box[3] > other[1] for other in placed):
                continue
            placed.append(box)
            draw.line([(x, y), target], fill="#72869f", width=1)
            draw.ellipse((x-2, y-2, x+2, y+2), fill="#d4e5f3")
            draw.text(target, name, font=FONTS[18], anchor=anchor, fill="#e0eaf8", stroke_width=2, stroke_fill=BACKGROUND)

    def frame(self, t):
        matrix = camera(t)
        side = 1 if matrix[2, 2] >= 0 else -1
        image = Image.new("RGB", (W, H), BACKGROUND)
        draw = ImageDraw.Draw(image)
        self.draw_columns(draw, matrix, -side, False)
        self.draw_edge(draw, matrix)
        self.draw_map_texture(image, matrix, side)
        self.draw_columns(draw, matrix, side, True)
        self.draw_places(draw, matrix, side)
        self.overlay(draw, matrix[2, 2])
        return image

    def overlay(self, draw, facing):
        draw.text((64, 63), "OKINAWA MAIN ISLAND", font=FONTS[25], fill=MUTED)
        draw.text((64, 108), "The Price of Space", font=FONTS[82], fill=INK)
        draw.line((64, 228, 1016, 228), fill="#334052", width=1)
        fraction = smooth(-.38, .38, facing)
        rgb = tuple(round(a * fraction + b * (1 - fraction)) for a, b in zip(shade(CYAN, 1), shade(PINK, 1)))
        draw.line((64, 228, 153, 228), fill=rgb, width=3)
        draw.text((1016, 71), "INSIDE OUT", font=FONTS[19], fill=MUTED, anchor="ra")
        draw.line((64, 1070, 1016, 1070), fill="#334052", width=1)
        self.legend(draw, 64, "Population change", "Oct 2020–Oct 2025  ·  % change", CYAN, facing >= 0)
        self.legend(draw, 570, "Land price change", "Jul 2020–Jul 2025  ·  % change", PINK, facing < 0)
        draw.rectangle((64, 1247, 76, 1259), fill=LOSS)
        draw.line((64, 1254, 76, 1254), fill="#dcaaff")
        draw.text((86, 1243), "Hatched bars show losses", font=FONTS[18], fill=MUTED)
        draw.text((64, 1300), "Okinawa Prefecture  /  MLIT boundaries", font=FONTS[18], fill=MUTED)
        if self.roads:
            draw.text((1016, 1300), "© OpenStreetMap contributors  /  OpenFreeMap", font=FONTS[18], fill=MUTED, anchor="ra")

    @staticmethod
    def legend(draw, x, title, units, color, active):
        draw.ellipse((x, 1096, x + 11, 1107), fill=color if active else shade(color, .48))
        draw.text((x + 21, 1085), title, font=FONTS[37], fill=INK if active else "#b0bccc")
        draw.text((x, 1136), units, font=FONTS[22], fill=MUTED)
        step = (.04 * POP_HEIGHT if color == CYAN else .25 * PRICE_HEIGHT) * SCALE
        for i, label in enumerate(Scene.scale_labels(color)):
            tick_x = x + i * step
            draw.line((tick_x, 1184, tick_x, 1193), fill=color)
            draw.text((tick_x, 1201), label, font=FONTS[18], fill=MUTED, anchor="ma" if i else "la")
        draw.line((x, 1187, x + 2 * step, 1187), fill=color, width=2)

    @staticmethod
    def scale_labels(color):
        return ["0%", "4%", "8%"] if color == CYAN else ["0%", "25%", "50%"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "the-price-of-space.mp4")
    parser.add_argument("--frame", type=float, help="Render one PNG at the given time in seconds.")
    args = parser.parse_args()
    scene = Scene()
    if args.frame is not None:
        scene.frame(args.frame / SECONDS).save(args.output.with_suffix(".png"))
        return
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16",
               "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(args.output)]
    with subprocess.Popen(command, stdin=subprocess.PIPE) as encoder:
        for frame in range(FPS * SECONDS):
            encoder.stdin.write(scene.frame(frame / (FPS * SECONDS)).tobytes())
        encoder.stdin.close()
        if encoder.wait():
            raise RuntimeError("FFmpeg could not encode the animation")


if __name__ == "__main__":
    main()
