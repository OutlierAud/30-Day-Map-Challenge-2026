import os
import math
import gc
import time
from qgis.core import (QgsRectangle, QgsProject, QgsMapRendererParallelJob,
                       QgsMapSettings)
from qgis.utils import iface
from qgis.PyQt.QtCore import QStandardPaths, QSize, QPointF, QEventLoop, Qt
from qgis.PyQt.QtGui import QImage, QPainter, QColor, QTransform, QPolygonF
from qgis.PyQt.QtWidgets import QApplication

# ---------------- SETTINGS ----------------
TOTAL_FRAMES    = 360
START_FRAME     = 0
SUPERSAMPLE     = 1          # 1 = native 4K (keeps lights bright)
OUT_W, OUT_H    = 3840, 2160
DST_FOLDER_NAME = "Final_Cinematic_Frames_4K_v3"
SKIP_EXISTING   = False

# Final framing (smaller final_width = tighter crop, fewer borders)
final_width     = 340
final_center_y  = 6

# Tilt strength at frame 0 (fades to 0 by the last frame). Lower = flatter.
TILT_START      = 0.25
# ------------------------------------------

desktop = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
dst_folder = os.path.join(desktop, DST_FOLDER_NAME)
os.makedirs(dst_folder, exist_ok=True)
print(f"==== SAVING 4K TO: {dst_folder} ====")

canvas = iface.mapCanvas()
ASPECT = OUT_W / OUT_H
render_w, render_h = OUT_W * SUPERSAMPLE, OUT_H * SUPERSAMPLE

def extent_16x9(cx, cy, width):
    h = width / ASPECT
    return QgsRectangle(cx - width / 2, cy - h / 2, cx + width / 2, cy + h / 2)

final_extent = extent_16x9(0, final_center_y, final_width)
keyframes = [
    [0,   QgsRectangle(-130, 20, -60, 60),  -65],
    [80,  QgsRectangle(-20, 20, 50, 60),    -35],
    [160, QgsRectangle(80, 0, 150, 40),     -45],
    [240, QgsRectangle(110, -45, 180, -5),  -30],
    [360, final_extent,                       0]
]

def lerp(a, b, t):
    return a + (b - a) * t

# ---- Map settings, built once ----
settings = QgsMapSettings(canvas.mapSettings())
layers = list(settings.layers())
anno = QgsProject.instance().mainAnnotationLayer()
if anno not in layers:
    layers = [anno] + layers
settings.setLayers(layers)
settings.setOutputSize(QSize(render_w, render_h))
settings.setDevicePixelRatio(1.0)      # force exactly render_w x render_h pixels
settings.setOutputDpi(canvas.mapSettings().outputDpi() * render_w / canvas.width())
settings.setBackgroundColor(QColor(0, 0, 0))
settings.setFlag(QgsMapSettings.Flag.Antialiasing, True)
settings.setFlag(QgsMapSettings.Flag.DrawLabeling, True)
settings.setFlag(QgsMapSettings.Flag.UseAdvancedEffects, True)
settings.setFlag(QgsMapSettings.Flag.UseRenderingOptimization, False)

def render_flat():
    job = QgsMapRendererParallelJob(settings)
    loop = QEventLoop()
    job.finished.connect(loop.quit)
    job.start()
    loop.exec()
    img = QImage(job.renderedImage())
    job.deleteLater()
    img.setDevicePixelRatio(1.0)
    return img

src_quad = QPolygonF([QPointF(0, 0), QPointF(render_w, 0),
                      QPointF(render_w, render_h), QPointF(0, render_h)])

def render_frame(i):
    global_t = i / TOTAL_FRAMES
    eased_t = 0.5 - 0.5 * math.cos(math.pi * global_t)
    virtual_frame = eased_t * TOTAL_FRAMES

    current_k = next_k = None
    for j in range(len(keyframes) - 1):
        if keyframes[j][0] <= virtual_frame <= keyframes[j + 1][0]:
            current_k, next_k = keyframes[j], keyframes[j + 1]
            break
    if not (current_k and next_k):
        return None

    start_f, end_f = current_k[0], next_k[0]
    local_t = (virtual_frame - start_f) / (end_f - start_f) if end_f > start_f else 1.0
    r1, r2 = current_k[1], next_k[1]
    rect = QgsRectangle(
        lerp(r1.xMinimum(), r2.xMinimum(), local_t),
        lerp(r1.yMinimum(), r2.yMinimum(), local_t),
        lerp(r1.xMaximum(), r2.xMaximum(), local_t),
        lerp(r1.yMaximum(), r2.yMaximum(), local_t))
    rot = lerp(current_k[2], next_k[2], local_t)

    settings.setRotation(rot)
    settings.setExtent(rect)
    base = render_flat()

    # Tilt: top edge stays on the frame edge, bottom corners pushed OUTSIDE the
    # frame, so the image always covers the whole canvas (no black wedges).
    p = lerp(TILT_START, 0.0, eased_t)
    if p > 1e-6:
        dest = QPolygonF([
            QPointF(0,                   0),
            QPointF(render_w,            0),
            QPointF(render_w * (1 + p),  render_h),
            QPointF(-render_w * p,       render_h)])
        tr = QTransform()
        QTransform.quadToQuad(src_quad, dest, tr)
        warped = QImage(QSize(render_w, render_h), QImage.Format.Format_RGB32)
        warped.fill(QColor(0, 0, 0))
        pw = QPainter(warped)
        pw.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        pw.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        pw.setTransform(tr)
        pw.drawImage(0, 0, base)
        pw.end()
        del pw
    else:
        warped = base          # identity: skip warp, no resampling loss

    if SUPERSAMPLE != 1:
        warped = warped.scaled(OUT_W, OUT_H, Qt.AspectRatioMode.IgnoreAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
    return warped

t_start = time.time()
for i in range(START_FRAME, TOTAL_FRAMES + 1):
    dst_path = os.path.join(dst_folder, f"cine_{i:03d}.png")
    if SKIP_EXISTING and os.path.exists(dst_path):
        continue

    t0 = time.time()
    img = render_frame(i)
    if img is None:
        print(f"  !! no keyframe segment for frame {i}")
        continue
    img.setDevicePixelRatio(1.0)
    ok = img.save(dst_path)
    del img
    gc.collect()

    if not ok:
        print(f"  !! FAILED TO SAVE frame {i}")
    else:
        print(f"Frame {i}/{TOTAL_FRAMES} in {time.time() - t0:.1f}s "
              f"(elapsed {time.time() - t_start:.0f}s)")
    QApplication.processEvents()

# ---- Verify every frame is exactly OUT_W x OUT_H ----
bad = []
for i in range(START_FRAME, TOTAL_FRAMES + 1):
    pth = os.path.join(dst_folder, f"cine_{i:03d}.png")
    if not os.path.exists(pth):
        bad.append((i, "missing")); continue
    im = QImage(pth)
    if im.width() != OUT_W or im.height() != OUT_H:
        bad.append((i, f"{im.width()}x{im.height()}"))
print("ALL FRAMES OK" if not bad else f"PROBLEM FRAMES: {bad}")
print(f"FINISHED! Open the image sequence from '{DST_FOLDER_NAME}' in QuickTime.")