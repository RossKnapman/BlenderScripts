# Rescales the data from ParaView, moves it to the origin, and adds the colours from ParaView (so that I don't have to do it manually every time I change something in ParaView)

import bpy
import numpy as np

vectorField = bpy.data.objects['BW']

# Scale the vector field so that its size is not of ~nm
vectorField.scale[0] = 1e+08
vectorField.scale[1] = 1e+08
vectorField.scale[2] = 1e+08

# Translate the vector field back to the origin
vectorField.location.x -= 5
vectorField.location.y -= 5

# Allow colouring exported from ParaView
mat = bpy.data.materials.new(name="PVColouring")
mat.use_nodes = True

nodes = mat.node_tree.nodes
links = mat.node_tree.links

psNode = nodes.get('Principled BSDF')

attributeNode = nodes.new("ShaderNodeAttribute")
attributeNode.location.x -= 500
links.new(attributeNode.outputs['Color'], psNode.inputs['Base Color'])
attributeNode.attribute_name = 'Col'

bpy.context.active_object.data.materials.append(mat)
