import bpy
import time

for object in bpy.data.collections['Skyrmion'].all_objects:
    object.select_set(True)
#    bpy.ops.transform.resize(value=(2, 2, 2))
    object.select_set(False)
