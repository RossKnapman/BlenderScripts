import bpy
import numpy as np
import discretisedfield as df
import time
import matplotlib

# To use discretisedfield with Blender's Python, you need to:
# - cd to the folder containing Blender's Python binary (find using, in Blender Python console, sys.exec_prefix)
# - ./python<...> -m ensurepip
# - ./python<...> -m pip install discretisedfield

# Inspiration came from https://peytondmurray.github.io/coding/blender-visualization/

# Deal with the colour map
cmap = matplotlib.cm.get_cmap('RdBu_r')
# To normalise m_z to be between 0 and 1, which is where the colour map is defined
norm = matplotlib.colors.Normalize(vmin=-1, vmax=1)

# Clear objects from previous runs
for obj in bpy.data.objects:
    bpy.data.objects.remove(obj)

# Clear materials from pervious runs
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat)

scaleFactor = 3  # Controls distance between arrows


#def createMaterial(theName):

#    mat = bpy.data.materials.new(name=theName)
#    mat.use_nodes = True

#    nodes = mat.node_tree.nodes
#    links = mat.node_tree.links

#    # Shader already has Principled BSDF and MaterialOutput nodes
#    psNode = nodes.get('Principled BSDF')
#    psNode.inputs['Metallic'].default_value = 0


#    # Add ramp node and colours
#    rampNode = nodes.new("ShaderNodeValToRGB")
#    rampNode.location.x -= 400  # Easier to see in shader editor when they're not stacked on top of each other

#    # Colour ramp values
#    rampNode.color_ramp.elements[0].color = (0, 0, 1, 1)
#    rampNode.color_ramp.elements[1].color = (1, 0, 0, 1)
#    
#    valueNode = nodes.new("ShaderNodeValue")
#    valueNode.location.x -= 600

#    # Link the nodes together
#    links.new(valueNode.outputs["Value"], rampNode.inputs["Fac"])
#    links.new(rampNode.outputs["Color"], psNode.inputs["Base Color"])

#    return mat


directory = '/home/rknapman/scratch/7.5.out/'
initialFile = 'm000000.ovf'

m = df.Field.fromfile(directory + initialFile).array
m = m.reshape(m.shape[0], m.shape[1], 3)  # Loads as 3D array of vectors due to redundant z index; change to 2D array

step = 2
m = m[::step, ::step]
m = m[:300, 50:200]

for i in range(m.shape[0]):
    
    print(i, 'of', m.shape[0])
    
    for j in range(m.shape[1]):
       
            # Position based on array index; texture shifted to be centred at origin
            x = scaleFactor * (i - (m.shape[0] - 1)/2)
            y = scaleFactor * (j - (m.shape[1] - 1)/2)
            
            bpy.ops.mesh.primitive_cone_add(vertices=100, location=(x, y, 2))
            
            # We rename the objects so that we can select them, then join them together into one object
            theCone = bpy.data.objects.get('Cone')
            theCone.name = f'Cone({i},{j})'
            theCone.rotation_mode = 'AXIS_ANGLE'
            
            newMat = bpy.data.materials.new(name=f'Cone({i},{j})')
            newMat.use_nodes = True
            theCone.data.materials.append(newMat)
            
            bpy.data.materials[f'Cone({i},{j})'].node_tree.nodes[0].inputs['Base Color'].default_value = [1, 0, 0, 1]
            
            bpy.context.scene.collection.objects.link(theCone)
            
            
pastTheta = 0
pastPhi = 0

selectingArray = []
anglesArray = []
findingArray = []
rotatingArray = []
keyframingArray = []

            
for frameNo in range(640, 760):
    
    print(frameNo)
    
    m = df.Field.fromfile(directory + 'm' + f'{frameNo:06d}' + '.ovf').array
    m = m.reshape(m.shape[0], m.shape[1], 3)
            
    m = m[::step, ::step]
    m = m[:300, 50:200]

    for i in range(m.shape[0]):
        
        for j in range(m.shape[1]):
            
            object = bpy.data.objects[f'Cone({i},{j})']

            mx = m[i, j, 0]
            my = m[i, j, 1]
            mz = m[i, j, 2]
            
            theta = np.arccos(mz / np.sqrt(mx**2 + my**2 + mz**2))
            phi = np.arctan2(my, mx)

            object = bpy.data.objects[f'Cone({i},{j})']
            
            theAxisAngle = phi + np.pi/2
            axisX = np.cos(theAxisAngle)
            axisY = np.sin(theAxisAngle)

            object.rotation_axis_angle = [theta, axisX, axisY, 0]
            
            r, g, b, alpha = cmap(norm(mz))
            
            bpy.data.materials[f'Cone({i},{j})'].node_tree.nodes[0].inputs['Base Color'].default_value = [r, g, b, alpha]
            bpy.data.materials[f'Cone({i},{j})'].node_tree.nodes[0].inputs['Base Color'].keyframe_insert(data_path='default_value', frame=5*(frameNo-640))
            object.keyframe_insert(data_path='rotation_axis_angle', frame=5*(frameNo-640))
            

# Save the .blend file
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
