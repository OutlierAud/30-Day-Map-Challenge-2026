import argparse
import base64
import io
import json
from pathlib import Path
import re
import numpy as np
from PIL import Image

# Render the same ocean frames as the original map build using its palette.
parser = argparse.ArgumentParser(description="Render the daily ocean frames using the map palette.")
parser.add_argument("source", type=Path, metavar="MAP.html")
parser.add_argument("grids", type=Path, metavar="FLOAT_GRID_DIR")
parser.add_argument("target", type=Path, metavar="OUTPUT.json")
args = parser.parse_args()
source, grids, target = args.source, args.grids, args.target
page = source.read_text()
colours = re.findall(r'\{label: "[^"]+", colour: "#([a-f0-9]{6})"\}', page)
assert len(colours) == 7
palette = [0, 0, 0] + [int(c[i:i+2], 16) for c in colours for i in (0, 2, 4)]
size = (960, 800)
# The source has a one-cell buffer outside the visible map. Resample
# temperatures and valid-cell weights separately to avoid blending in land.
box = (1, 1, 121, 101)
def resize(a):
    return np.asarray(Image.fromarray(a.astype(np.float32)).resize(size, Image.Resampling.BILINEAR, box=box))

frames = {}
for path in sorted(grids.glob('*.bin')):
    values = np.fromfile(path, dtype='<f4').reshape(102, 122)
    valid = np.isfinite(values)
    weight = resize(valid)
    interpolated = resize(np.where(valid, values, 0))
    interpolated = np.divide(interpolated, weight, out=np.zeros_like(interpolated), where=weight > 0)
    mask = np.asarray(Image.fromarray(valid.astype(np.uint8)).resize(size, Image.Resampling.NEAREST, box=box))
    bands = (np.searchsorted([20, 22, 24, 26, 28, 30], interpolated, side='right') + 1).astype(np.uint8)
    bands[mask == 0] = 0
    frame = Image.frombytes('P', size, bands.tobytes())
    frame.putpalette(palette)
    data = io.BytesIO()
    frame.save(data, format='PNG', transparency=0, bits=4, compress_level=6)
    frames[path.stem] = base64.b64encode(data.getvalue()).decode()
target.write_text(json.dumps(frames, separators=(",", ":")))
print(f"Rendered {len(frames)} ocean frames at {size[0]} × {size[1]} pixels.")
