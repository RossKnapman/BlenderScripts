import bpy

# For each object in the collection "Sphere", change metallicity value on
# principled BSDF shader to zer
for object in bpy.context.scene.collection.children['Sphere'].objects:
    object.material_slots[0].material.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value = 0.
