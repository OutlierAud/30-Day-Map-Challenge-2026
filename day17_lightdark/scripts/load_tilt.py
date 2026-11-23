import bpy
from math import radians
from mathutils import Vector

scene = bpy.context.scene
earth = scene.objects["Earth"]

tilt = scene.objects.get("Globe Tilt")
if tilt is None:
    tilt = bpy.data.objects.new("Globe Tilt", None)
    scene.collection.objects.link(tilt)
    earth.parent = tilt

# Tilt around the horizontal axis of the camera view.
axis = scene.camera.matrix_world.to_quaternion() @ Vector((1, 0, 0))
tilt.rotation_mode = "AXIS_ANGLE"
tilt.rotation_axis_angle = (0, *axis)

for frame, degrees in [(1, 0), (63, 38), (125, 0), (187, -38), (250, 0)]:
    tilt.rotation_axis_angle[0] = radians(degrees)
    tilt.keyframe_insert(data_path="rotation_axis_angle", index=0, frame=frame)

scene.frame_set(1)