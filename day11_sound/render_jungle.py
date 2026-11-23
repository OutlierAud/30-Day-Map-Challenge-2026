"""Render the Jungle Beats sound map. Requires NumPy, Pillow 10.1+ and FFmpeg."""

import argparse
from pathlib import Path
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("audio", type=Path, help="Path to the Jungle Beats recording")
parser.add_argument("-o", "--output", type=Path, default=Path("jungle_beats_sound_map.mp4"))
args = parser.parse_args()

rate, hop, window = 24000, 120, 1024
pcm = subprocess.check_output([
    "ffmpeg", "-v", "error", "-i", str(args.audio), "-ac", "1",
    "-ar", str(rate), "-f", "f32le", "-",
])
samples = np.frombuffer(pcm, dtype="<f4")
frames = np.lib.stride_tricks.sliding_window_view(np.pad(samples, window // 2), window)[::hop]
db = 20 * np.log10(np.maximum(np.abs(np.fft.rfft(frames * np.hanning(window))), 1e-5))
flux = np.maximum(0, np.diff(np.maximum(db[:, :13], -12), axis=0)).mean(axis=1)
hits = []
for index in np.argsort(flux)[::-1]:
    if flux[index] < 3.8:
        break
    if all(abs(index - other) > 24 for other in hits):
        hits.append(index)
hit_times = sorted((index + 1) * hop / rate for index in hits)

width, height, fps = 1280, 720, 30
left, right, top, bottom, baseline = 137, 1195, 230, 485, 550
axis_duration = 20
background = (19, 26, 27)
cream, muted, grid = '#f2eee3', '#acbcb7', '#354440'
green, yellow, orange = '#00ce89', '#fafe00', '#FF5100E4'

def x_at(t):
    return round(left + (right - left) * t / axis_duration)

def y_at(hz):
    return round(bottom - (bottom - top) * np.log2(hz / 250) / 5)

def font(size):
    try:
        return ImageFont.truetype('DejaVuSans.ttf', size)
    except OSError:
        return ImageFont.load_default(size=size)

base = Image.new('RGB', (width, height), background)
draw = ImageDraw.Draw(base)
draw.text((63, 44), 'Theme Day 11  /  Senses: Sound', fill=muted, font=font(19))
draw.text((60, 71), 'Jungle Beats', fill=green, font=font(66))
draw.text((65, 154), 'A sound map in time', fill=muted, font=font(24))

for seconds in range(0, 21, 5):
    x = x_at(seconds)
    draw.line((x, top, x, baseline + 19), fill=grid)
    draw.text((x, 589), f'{seconds}s', font=font(19), fill=muted, anchor='mt')
for hz, label in [(250, '250 Hz'), (500, '500 Hz'), (1000, '1 kHz'),
                  (2000, '2 kHz'), (4000, '4 kHz'), (8000, '8 kHz')]:
    y = y_at(hz)
    draw.line((left, y, right, y), fill=grid)
    draw.text((left - 15, y), label, font=font(17), fill=muted, anchor='rm')
draw.line((left, baseline, right, baseline), fill='#735349')
draw.line((left, 648, left + 27, 648), fill=yellow, width=4)
draw.text((left + 39, 648), 'Tonal frequencies', fill=cream, font=font(18), anchor='lm')
draw.line((left + 251, 638, left + 251, 658), fill=orange, width=4)
draw.text((left + 268, 648), 'Estimated drum hits', fill=cream, font=font(18), anchor='lm')

# Emphasize sustained peaks over nearby frequencies and brief broadband hits.
bins = np.arange(11, 343)
nearby = np.lib.stride_tricks.sliding_window_view(db, 19, axis=1)[:, bins - 9]
contrast = db[:, bins] - np.median(nearby, axis=-1)
strength = np.clip((contrast - 7) / 24, 0, 1) * np.clip((db[:, bins] + 15) / 27, 0, 1)
strength = np.median(np.lib.stride_tricks.sliding_window_view(
    np.pad(strength, ((2, 2), (0, 0))), 5, axis=0), axis=-1)

rows = np.arange(top, bottom + 1)
hz_at_row = 250 * 2 ** (5 * (bottom - rows) / (bottom - top))
frequency_bins = hz_at_row * window / rate
spectral = np.stack([np.interp(frequency_bins, bins, spectrum, left=0, right=0)
                     for spectrum in strength], axis=1)
columns = np.arange(right - left + 1) * axis_duration / (right - left)
spectral = np.stack([np.interp(columns, np.arange(len(db)) * hop / rate, row, right=0)
                     for row in spectral])
plot = np.asarray(base.crop((left, top, right + 1, bottom + 1))).astype(float)
amount = np.clip(spectral * 1.4, 0, 1)[..., None]
tones = Image.fromarray(np.uint8(plot * (1 - amount) + np.array([255, 255, 0]) * amount))

command = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pixel_format', 'rgb24',
           '-video_size', f'{width}x{height}', '-framerate', str(fps), '-i', '-',
           '-i', str(args.audio), '-map', '0:v', '-map', '1:a:0', '-map', '1:a:0',
           '-c:a:0', 'aac', '-b:a:0', '192k', '-disposition:a:0', 'default',
           '-c:a:1', 'copy', '-disposition:a:1', '0', '-c:v',
           'libx264', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
           str(args.output)]
with subprocess.Popen(command, stdin=subprocess.PIPE) as encoder:
    for frame in range(22 * fps):
        t = frame / fps
        x = x_at(min(t, len(samples) / rate))
        image = base.copy()
        image.paste(tones.crop((0, 0, x - left + 1, tones.height)), (left, top))
        draw = ImageDraw.Draw(image)
        if t < len(samples) / rate:
            draw.line((x, top, x, baseline + 18), fill='#81998e')
        for hit in hit_times:
            if hit <= t:
                x = x_at(hit)
                draw.line((x, baseline - 32, x, baseline), fill=orange, width=4)
        encoder.stdin.write(image.tobytes())
    encoder.stdin.close()
    if encoder.wait():
        raise RuntimeError('Video export failed')
print(f'{len(hit_times)} estimated drum hits')
