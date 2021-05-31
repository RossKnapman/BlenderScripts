import bpy
import numpy as np

x = np.linspace(-20, 20, 20)
y = np.linspace(-20, 20, 20)


def skyrmionFromSphere(R, h, x, y, m=1, eta=np.pi/2):

    for i in range(len(x)):
        print(i)

        for j in range(len(y)):

            # X, Y in the plane
            X =  x[i]
            Y = y[j]

            # Spherical polars in the plane
            phi = np.arctan2(Y, X)
            r = np.sqrt(X**2 + Y**2)

            # Angle between corresponding point on sphere and vertical
            alpha = np.arctan(r/(h+2*R))

            theta = np.pi - 2*alpha

            Phi = m * phi + eta
            Theta = theta


            bpy.ops.mesh.primitive_cone_add(location=(X, Y, 0))

            bpy.ops.transform.rotate(value=theta, orient_axis='Y')
            bpy.ops.transform.rotate(value=Phi, orient_axis='Z')

            bpy.ops.collection.objects_add_active(collection="Skyrmion")
            bpy.ops.transform.resize(value=(0.5, 0.5, 0.5))
            bpy.ops.object.shade_smooth()

            theMaterial = bpy.data.materials.new(name="theta"+str(i)+"phi"+str(j))
            bpy.context.active_object.data.materials.append(theMaterial)
            redValue = (np.cos(theta) + 1) / 2
            bpy.context.object.active_material.diffuse_color = (redValue, 0, 1 - redValue, 1)
