# Adapted from my processing code from master's project
# Equidistance cones "glued" onto a 3D sphere, see https://www.cmu.edu/biolphys/deserno/pdf/sphere_equi.pdf for the algorithm

import bpy
import numpy as np

# Values which should be toggled
R = 4  # Sphere radius
h = 5  # Height of sphere above plane (0 corresponds to tangent with bottom)
m = 1

def drawSphere(R, h, m=1, eta=np.pi/2, N=5000):

    a = 4 * np.pi * R * R / (N)
    d = np.sqrt(a)
    M_theta = int(np.round(np.pi / d))
    d_theta = np.pi / M_theta
    d_phi = a / d_theta

    for i in range(M_theta):

        print(i, M_theta)

        theta = np.pi * (i + 0.5) / M_theta
        M_phi = int(np.round(2 * np.pi * np.sin(theta) / d_phi))

        for j in range(M_phi):

            phi = 2 * np.pi * j / M_phi
            Phi = m * phi + eta
            Theta = theta

            bpy.ops.mesh.primitive_cone_add(location=(R*np.cos(phi)*np.sin(theta), R*np.sin(phi)*np.sin(theta), R + h + R*np.cos(theta)))

            bpy.ops.transform.rotate(value=theta, orient_axis='Y')
            bpy.ops.transform.rotate(value=Phi, orient_axis='Z')

            bpy.ops.collection.objects_add_active(collection="Sphere")
            bpy.ops.transform.resize(value=(0.3, 0.3, 0.3))
            bpy.ops.object.shade_smooth()

            theMaterial = bpy.data.materials.new(name="theta"+str(i)+"phi"+str(j))
            bpy.context.active_object.data.materials.append(theMaterial)
            redValue = (np.cos(theta) + 1) / 2
            bpy.context.object.active_material.diffuse_color = (redValue, 0, 1 - redValue, 1)
            bpy.context.object.active_material.metallic = 0
