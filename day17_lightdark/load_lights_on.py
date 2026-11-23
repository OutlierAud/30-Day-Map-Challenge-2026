import bpy
from mathutils import Vector

scene = bpy.context.scene
earth = scene.objects["Earth"]
sun = scene.objects["Sun"]
dots = next(obj for obj in earth.children if obj.name.startswith("Lighthouse dots"))

tree = dots.data.materials[0].node_tree
nodes = tree.nodes
links = tree.links
emission = next(node for node in nodes if node.type == "EMISSION")
output = next(node for node in nodes if node.type == "OUTPUT_MATERIAL")

# A positive dot product means this point is on the sunlit side.
sun_direction = sun.matrix_world.to_quaternion() @ Vector((0, 0, 1))
position = nodes.new("ShaderNodeNewGeometry")
dot_product = nodes.new("ShaderNodeVectorMath")
dot_product.operation = "DOT_PRODUCT"
dot_product.inputs[1].default_value = sun_direction
links.new(position.outputs["Position"], dot_product.inputs[0])

daylight = nodes.new("ShaderNodeMath")
daylight.operation = "GREATER_THAN"
daylight.inputs[1].default_value = earth.matrix_world.translation.dot(sun_direction)
links.new(dot_product.outputs["Value"], daylight.inputs[0])

transparent = nodes.new("ShaderNodeBsdfTransparent")
mix = nodes.new("ShaderNodeMixShader")
links.new(daylight.outputs[0], mix.inputs[0])
links.new(emission.outputs[0], mix.inputs[1])
links.new(transparent.outputs[0], mix.inputs[2])
links.new(mix.outputs[0], output.inputs["Surface"])