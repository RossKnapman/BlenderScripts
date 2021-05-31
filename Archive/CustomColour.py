import bpy

value = 0.2

def createMaterial(theName, theValue):

    mat = bpy.data.materials.new(name=theName)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Shader already has Principled BSDF and MaterialOutput nodes
    psNode = nodes.get('Principled BSDF')

    # Add ramp node and colours
    rampNode = nodes.new("ShaderNodeValToRGB")
    rampNode.location.x -= 400  # Easier to see in shader editor when they're not stacked on top of each other

    # Add middle colour value
    rampNode.color_ramp.elements.new(position=0.5)
    rampNode.color_ramp.elements[0].color = (0, 0, 1, 1)
    rampNode.color_ramp.elements[1].color = (1, 1, 1, 1)
    rampNode.color_ramp.elements[2].color = (1, 0, 0, 1)

    valueNode = nodes.new("ShaderNodeValue")
    valueNode.location.x -= 600

    # Set value node to our required value depending on e.g. angle
    valueNode.outputs["Value"].default_value = theValue

    # Link the nodes together
    links.new(valueNode.outputs["Value"], rampNode.inputs["Fac"])
    links.new(rampNode.outputs["Color"], psNode.inputs["Base Color"])
