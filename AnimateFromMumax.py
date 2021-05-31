import bpy
import os
import numpy as np
import discretisedfield as df
import matplotlib

##########################################
# Take MuMax Data and Animate in Blender #
##########################################

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

scaleFactor = 3    # Controls distance between arrows
frameDistance = 5  # Controls how far apart the frames are in time (higher = slower simulation)

directory = '/Users/rossknapman/Desktop/BlenderTest/'
initialFile = 'm000000.ovf'

m = df.Field.fromfile(directory + initialFile).array
m = m.reshape(m.shape[0], m.shape[1], 3)  # Loads as 3D array of vectors due to redundant z index; change to 2D array

# Distance between data points
step = 5
m = m[::step, ::step]


for i in range(m.shape[0]):
    for j in range(m.shape[1]):

        # Position based on array index; texture shifted to be centred at origin
        x = scaleFactor * (i - (m.shape[0] - 1)/2)
        y = scaleFactor * (j - (m.shape[1] - 1)/2)
        
        # Create a cone and place it at the required point
        # In a similar manner, you could also create a cylinder here, and join them to create an arrow
        # Note that the cone is pointing upwards, and the rotation is not updated until the second for loop with frameNo
        # I set a z-value of 2 as I orinally placed a cylinder below it to create an arrow
        bpy.ops.mesh.primitive_cone_add(vertices=100, location=(x, y, 2))
        
        # We rename the objects so that we can select them (this is especially useful if we deal with more complex objects, like a cylinder and cone joined together to make an arrow)
        theCone = bpy.data.objects.get('Cone')  # Select the newly-created cone, which Blender just calls 'Cone' by default
        theCone.name = f'Cone({i},{j})'         # Rename
        theCone.rotation_mode = 'AXIS_ANGLE'    # Imporant when we update the orientations

        # Create a new material to put on the cone, we just give it the same name as the cone (e.g. Cone(14,21))
        newMat = bpy.data.materials.new(name=f'Cone({i},{j})')
        newMat.use_nodes = True                # Allows programmatic updating of the shader
        theCone.data.materials.append(newMat)  # Attach the material to the cone

        # Set new cones to red (useful for debugging, to make sure the cones are actually being coloured)
        bpy.data.materials[f'Cone({i},{j})'].node_tree.nodes[0].inputs['Base Color'].default_value = [1, 0, 0, 1]
        
        # Line the cones to the scene
        bpy.context.scene.collection.objects.link(theCone)
            

files = sorted([''.join([i for i in f if i.isdigit()]) for f in os.listdir(directory) if f.startswith('m') and f.endswith('.ovf')])

# Loop through the files
for frameNo in range(int(files[0]), int(files[-1])):
    
    m = df.Field.fromfile(directory + 'm' + f'{frameNo:06d}' + '.ovf').array
    m = m.reshape(m.shape[0], m.shape[1], 3)  # We only image a 2D film, so we remove the redundant z-axis
            
    m = m[::step, ::step]

    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            
            # Select the required object
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
            
            # Update the material colour based on the z-value of the magnetization
            r, g, b, alpha = cmap(norm(mz))
            bpy.data.materials[f'Cone({i},{j})'].node_tree.nodes[0].inputs['Base Color'].default_value = [r, g, b, alpha]

            # Insert keyframes for the material colour and the orientation of the vector
            bpy.data.materials[f'Cone({i},{j})'].node_tree.nodes[0].inputs['Base Color'].keyframe_insert(data_path='default_value', frame=frameDistance*frameNo)
            object.keyframe_insert(data_path='rotation_axis_angle', frame=frameNo)

# Save the .blend file
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
